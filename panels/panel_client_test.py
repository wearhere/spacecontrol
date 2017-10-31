import json
import itertools as it
import unittest
import mock
from StringIO import StringIO
import sys

import panel_client


class TestSpaceTeamMessenger(unittest.TestCase):

  def setUp(self):
    self.mocked_socket = mock.Mock()
    socket = mock.Mock(side_effect=(lambda _, __: self.mocked_socket))
    self.messenger = panel_client.SpaceTeamMessenger(socket)

    self.message1 = ({'message': 1})
    self.message2 = ({'message': 2})

    split_idx = 4

  def test_get_messages_empty(self):
    self.mocked_socket.recv.side_effect = lambda _: ''
    self.assertEqual(self.messenger.peek_buffer(), '')
    self.assertEqual(len(list(self.messenger.get_messages())), 0)

  def test_get_messages_parsing(self):
    two_message_buffer = ''.join(
        [panel_client._encode(msg) for msg in [self.message1, self.message2]])
    self.mocked_socket.recv.side_effect = lambda _: two_message_buffer
    messages = list(self.messenger.get_messages())
    self.assertEqual(len(messages), 2)
    self.assertEqual(messages, [self.message1, self.message2])
    self.assertEqual(self.messenger.peek_buffer(), '')


class TestIOSubprocesses(unittest.TestCase):

  def setUp(self):
    self.action_queue = mock.Mock()
    self.message_queue = mock.Mock()
    self.panel_io_started = mock.Mock()

  def test_server_io(self):
    num_actions = 10
    num_messages = 6
    msg_template = 'Hi #{}'
    mock_messenger = mock.Mock()
    actions = it.chain([str(x) for x in range(num_actions)], [None])
    self.action_queue.get.side_effect = actions
    messages = it.chain(([{
        'message': 'display',
        'data': {
            'display': msg_template.format(x)
        }
    }] for x in range(num_messages)), [[] for x in range(num_actions)])
    mock_messenger.get_messages.side_effect = messages

    panel_client._server_io_subprocess_main(
        self.action_queue,
        self.message_queue,
        messenger_factory=lambda: mock_messenger)

    mock_messenger.send.assert_has_calls(
        mock.call(str(x)) for x in range(num_actions))

    self.message_queue.put.assert_has_calls(
        mock.call({
        'message': 'display',
        'data': {
            'display': msg_template.format(x)
        }
    }) for x in range(num_messages))


  # Disable control validation for the purposes of this test.
  @mock.patch('panel_client._validate_controls')
  def test_panel_io(self, mock_validate_controls):
    panel_state = mock.Mock()
    # Since this is a mock, it'll respond to the `getattr('panel_main')` call as if this actually
    # defined it, so we must explicitly suppress the check.
    panel_state.panel_main = False
    updates = [[update] for update in zip('abcedf', (x for x in range(6)))]
    panel_state.get_state_updates.side_effect = it.chain(updates, [[None]])

    msg = {'message':'display', 'data':{'display':'hi'}}
    self.message_queue.get.side_effect = lambda block: msg

    panel_client._panel_io_subprocess_main(
        lambda: panel_state, self.action_queue, self.message_queue, self.panel_io_started)

    panel_state.display_message.assert_called_with(msg['data']['display'])

    self.action_queue.put.assert_has_calls(
        mock.call(panel_client._make_update_message(update[0]))
        for update in updates)


class TestControlValidation(unittest.TestCase):

  @mock.patch('sys.stdout', new_callable=StringIO) # https://stackoverflow.com/a/31171719/495611
  @mock.patch('sys.exit')
  def testPanelExitsIfValidationFails(self, mock_exit, mock_stdout):
    panel_state = mock.Mock()

    client = panel_client.PanelClient(lambda: panel_state)
    client.start()

    self.assertEqual(mock_stdout.getvalue(), 'Could not start panel IO; aborting.\n')
    sys.exit.assert_called_with(1)

  def testLonghandForm(self):
    panel_client._validate_controls([{
      'id': 'defenestrator',
      'state': '0',
      'actions': {
          '0': '',
          '1': 'Defenestrate the aristocracy!'
      }
    }])

  def testShorthandForm(self):
    panel_client._validate_controls([{
      'id': 'Froomulator',
      'state': '0',
      'actions': [['0', '1', '2'], 'Set Froomulator to %s!']
    }])

  def formatStringsOnlySupportedInShorthandForm(self):
    with self.assertRaisesRegexp(Exception, 'Format strings are only supported in the shorthand form of `actions`'):
      panel_client._validate_controls([{
        'id': 'defenestrator',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Defenestrate %s!'
        }
      }])

  def formatStringRequiredInShorthandForm(self):
    with self.assertRaisesRegexp(Exception, 'Shorthand `actions` is malformed'):
      panel_client._validate_controls([{
        'id': 'Froomulator',
        'state': '0',
        'actions': [['0', '1', '2'], 'Set Froomulator!']
      }])

  def testRequireControlKeys(self):
    with self.assertRaisesRegexp(Exception, '`state` is missing'):
      panel_client._validate_controls([{
        'id': 'defenestrator',
        'actions': {
          '0': '',
          '1': 'Defenestrate the aristocracy!'
        }
      }])

  # Useful for playing the game via the CLI, see where `type: 'button` is read by
  # `keyboard_panel.py`. Might also be used by other panel subclasses.
  def testIgnoreUnknownControlKeys(self):
    panel_client._validate_controls([{
      'id': 'defenestrator',
      'state': '0',
      'actions': {
          '0': '',
          '1': 'Defenestrate the aristocracy!'
      },
      'type': 'button'
    }])

  def testStateMustBeString(self):
    with self.assertRaisesRegexp(Exception, '`state` is not a string'):
      panel_client._validate_controls([{
        'id': 'defenestrator',
        'state': 0,
        'actions': {
            0: '',
            1: 'Defenestrate the aristocracy!'
        }
      }])

    with self.assertRaisesRegexp(Exception, 'State in `actions` is not a string'):
      panel_client._validate_controls([{
        'id': 'defenestrator',
        'state': '0',
        'actions': {
            '0': '',
            1: 'Defenestrate the aristocracy!'
        }
      }])

    with self.assertRaisesRegexp(Exception, 'State in `actions` is not a string'):
      panel_client._validate_controls([{
        'id': 'Froomulator',
        'state': '0',
        'actions': [['0', 1], 'Set Froomulator to %s!']
      }])

  def testStateMustBeInActions(self):
    with self.assertRaisesRegexp(Exception, '`state` not present in `actions`'):
      panel_client._validate_controls([{
        'id': 'defenestrator',
        'state': '2',
        'actions': {
            '0': '',
            '1': 'Defenestrate the aristocracy!'
        },
        'type': 'button'
      }])

    with self.assertRaisesRegexp(Exception, '`state` not present in `actions`'):
      panel_client._validate_controls([{
        'id': 'Froomulator',
        'state': '3',
        'actions': [['0', '1', '2'], 'Set Froomulator to %s!']
      }])

  def testStatesDontHaveToBeNumeric(self):
    panel_client._validate_controls([{
      'id': 'octo',
      'state': 'nothing',
      'actions': {
          'nothing': '',
          'nipple': 'Octo bite raven girl nipple!',
          'mouth': 'Octo kiss raven girl mouth!'
      }
    }])

  def testIdsMustBeUnique(self):
    with self.assertRaisesRegexp(Exception, 'Control ids are not unique'):
      panel_client._validate_controls([{
        'id': 'defenestrator',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Defenestrate the aristocracy!'
        }
      }, {
        'id': 'defenestrator',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Defenestrate the aristocracy!'
        }
      }])


if __name__ == '__main__':
  unittest.main()
