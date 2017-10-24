import json
import itertools as it
import unittest
import mock

import panel_client


class TestSpaceTeamMessenger(unittest.TestCase):

  def setUp(self):
    self.mocked_socket = mock.Mock()
    socket = mock.Mock(side_effect=(lambda: self.mocked_socket))
    self.messenger = panel_client.SpaceTeamMessenger(socket)

    self.message1 = json.dumps({'message': 1})
    self.message2 = json.dumps({'message': 2})

    split_idx = 4
    self.msg1_1 = self.message1[:split_idx]
    self.msg1_2 = self.message1[split_idx:]

  def test_get_messages_empty(self):
    self.mocked_socket.recv.side_effect = lambda _: ''
    self.assertEqual(len(list(self.messenger.get_messages())), 0)
    self.assertEqual(len(self.messenger.peek_buffer()), 0)

  def test_get_messages_malformed(self):
    self.mocked_socket.recv.side_effect = (
        lambda _: self.msg1_1 + self.messenger.get_delimiter())
    self.assertEqual(len(list(self.messenger.get_messages())), 0)
    self.assertEqual(self.messenger.peek_buffer(), '')

  def test_get_messages_incomplete(self):
    self.mocked_socket.recv.side_effect = lambda _: self.msg1_1
    self.assertEqual(len(list(self.messenger.get_messages())), 0)
    self.assertEqual(self.messenger.peek_buffer(), self.msg1_1)

  def test_get_messages_parsing(self):
    two_message_buffer = self.messenger.get_delimiter().join(
        [self.message1, self.message2, ''])
    self.mocked_socket.recv.side_effect = lambda _: two_message_buffer
    messages = list(self.messenger.get_messages())
    self.assertEqual(len(messages), 2)
    self.assertEqual(messages, [json.loads(msg)
                                for msg in [self.message1, self.message2]])
    self.assertEqual(self.messenger.peek_buffer(), '')


class TestIOSubprocesses(unittest.TestCase):
  def setUp(self):
    self.action_queue = mock.Mock()
    self.message_queue = mock.Mock()


  def test_server_io(self):
    num_actions = 10
    num_messages = 6
    msg_template = 'Hi #{}'
    mock_messenger = mock.Mock()
    actions = it.chain([str(x) for x in range(num_actions)], [None])
    self.action_queue.get.side_effect = actions
    messages = it.chain(([{'message':'display', 'data':{'display':msg_template.format(x)}}]
                for x in range(num_messages)), [ [] for x in range(num_actions)])
    mock_messenger.get_messages.side_effect = messages

    panel_client._server_io_subprocess_main(self.action_queue,
                                            self.message_queue,
                                            messenger_factory = lambda: mock_messenger)

    mock_messenger.send.assert_has_calls(mock.call(str(x)) for x in range(num_actions))

    self.message_queue.put.assert_has_calls(mock.call(msg_template.format(x))
                                             for x in range(num_messages))

  def test_panel_io(self):
    panel_state = mock.Mock()
    updates = [[update] for update in zip('abcedf', (x for x in range(6)))]
    panel_state.get_state_updates.side_effect = it.chain(updates, [[None]])

    msg = 'hi'
    self.message_queue.get.side_effect = lambda: msg

    panel_client._panel_io_subprocess_main(lambda: panel_state, self.action_queue, self.message_queue)

    panel_state.display_message.assert_called_with(msg)

    self.action_queue.put.assert_has_calls(mock.call(panel_client._make_update_message(update[0]))
                                                    for update in updates)

if __name__ == '__main__':
  unittest.main()
