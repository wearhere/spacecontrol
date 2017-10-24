"""Demonstration/debugging panel. Uses the shell for I/O."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import Queue
import threading
from panel_client import PanelStateBase

CONTROL_SCHEMES = [
    [
        {
            'id': 'defenestrator',
            'state': '0',
            'actions': {
                '0': '',
                '1': 'Defenestrate the aristocracy!'
            },
            # HACK(jeff): `'type': 'button'` is only present to be able to play
            # the game via the CLI, see where this is read at the bottom of
            # this script.
            'type': 'switch',
        },
        {
            'id': 'octo',
            'state': 'nothing',
            'actions': {
                'nothing': '',
                'nipple': 'Octo bite raven girl nipple!',
                'mouth': 'Octo kiss raven girl mouth!'
            },
            'type': 'switch'
        },
    ],
    [{
        'id': 'Froomulator',
        'state': '0',
        'actions': [['0', '1', '2'], 'Set Froomulator to %s!']
    }]
]


def poll_keyboard(stop_queue, input_queue, stdin):
  while True:

    try:
      _ = stop_queue.get(block=False)
      return
    except Queue.Empty:
      pass
    try:
      user_input = stdin.readline()[:-1]
      input_queue.put(user_input)
    except EOFError:
      pass

    
class KeyboardPanel(PanelStateBase):
  """Simulate a panel using the keyboard."""

  def __init__(self, stdin, player_number):
    self.controls = {}
    self.input_queue = Queue.Queue()
    self.stop_queue = Queue.Queue()
    self.kbd_thread = threading.Thread(
        target=poll_keyboard,
        args=(self.stop_queue, self.input_queue, stdin))
    self.controls = CONTROL_SCHEMES[player_number - 1]
    self.display_message('Conrol scheme: {}'.format(self.controls))
    self.kbd_thread.start()
    
  def get_state_updates(self):
    """Returns an iterable of control_id, state pairs for new user input."""
    try:
      item, action = self.input_queue.get(block=False).split(' ')
      yield item, action
    except ValueError:
      self.display_message(
          'Invalid format. Must be of the form "control_id state"')
    except Queue.Empty:
      return

  def get_controls(self):
    """Must implement this function for your panel.

    Should return the available controls.
    """
    return self.controls

  def display_message(self, message):
    """Prints the message."""
    print(message)

  def __del__(self):
    self.stop_queue.put(None)
