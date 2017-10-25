"""Demonstration/debugging panel. Uses the shell for I/O."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import Queue
import select
import threading
from panel_client import PanelStateBase, MIN_LATENCY_MS

# A control is any object that the player can manipulate to put in one or more states. A control can
# be anything from a button to a switch to a dial to a pair of dolls that you touch against each
# other.
#
# It's ok to have multiple controls of the same form, i.e. multiple buttons, as long as they can
# be clearly identified. This may be a matter of just labeling them differently. See `actions` for
# tips on naming.
#
# This is a list of all controls monitored by this control panel. As controls
# connect/disconnect, add and remove from this list, then call `announce` again.
CONTROL_SCHEMES = [
    [
        {
            # An identifier for the control. Must be globally unique. This shouldn't be that hard in practice
            # because players will need to uniquely identify this control among all controls. Just give it a
            # weird name.
            'id': 'defenestrator',

            # The current state of the control. This should always be a string even if the state is numeric
            # (this is because the keys of `actions` won't be able to be JSON-serialized if numeric).
            #
            # The values of this will depend on the control. For a button or a switch, `state` might be one
            # of `['0', '1']` or `['off', 'on']`. For a multi-valued control like a dial or slider, `state`
            # might be one of `['0', '1', '2', '3']` or `['red', 'green', 'yellow'].
            'state': '0',

            # Possible things that the player might do to or with the control. This is a map where the keys
            # are the possible values of `state` (see above), and the values are how the player puts the
            # control in that state ("actions").
            #
            # You'll notice that the value of '0' here is the empty string. This represents the player not
            # having to do anything to put the control in this state, as would be the case for a button-like
            # control, where if the player stops touching the control it will automatically return to this
            # state.
            #
            # The game may ask the player to perform any non-empty action. The action will be displayed to the
            # player, so make it clear and exciting. Actions should be globally unique, since players will be
            # shouting these across the room. It's possible to unique actions by being creative about what
            # the control is called and does (and labeling the physical control accordingly). For instance,
            # notice how the action here is to "defenestrates the aristocracy", not merely "push the button".
            # Another button might "launch the missiles". Two dials might respectively be labeled
            # "Froomulator" and "Hypervisor", with actions "Set Froomulator to 1" vs. "Set Hypervisor to 1".
            #
            # See the third control below for a shorthand way to define `actions` for dial-like controls.
            'actions': {
                '0': '',
                '1': 'Defenestrate the aristocracy!'
            },

            # HACK(jeff): `'type': 'button'` is only present to be able to play the game via the CLI, see
            # where this is read at the bottom of this script.
            'type': 'button',
        },
        {
            'id': 'octo',
            'state': 'nothing',
            'actions': {
                'nothing': '',
                'nipple': 'Octo bite raven girl nipple!',
                'mouth': 'Octo kiss raven girl mouth!'
            },
            'type': 'button'
        }
    ],
    [{
        'id': 'Froomulator',
        'state': '0',

        # This is a shorthand form of `states`, where the first value (the array) contains the values for
        # `state`, and the second value (the string) is a "template action": the actual actions for each
        # state will be formed by replacing "%s" with the state.
        'actions': [['0', '1', '2'], 'Set Froomulator to %s!'],
        'type': 'switch'
    }]
]


def poll_keyboard(stop_event, input_queue, stdin):
  while True:
    if stop_event.is_set():
      return
    ready, _, __ = select.select([stdin], [], [], MIN_LATENCY_MS/1000)
    if ready:
      try:
        user_input = stdin.readline()[:-1]
        input_queue.put(user_input)
      except EOFError:
        pass


class KeyboardPanel(PanelStateBase):
  """Simulate a panel using the keyboard."""

  def __init__(self, stdin, player_number):
    self.input_queue = Queue.Queue()
    self.stop_event = threading.Event()
    self.stop_event.clear()

    self.kbd_thread = threading.Thread(
        target=poll_keyboard, args=(self.stop_event, self.input_queue, stdin))
    self.controls = CONTROL_SCHEMES[player_number - 1]
    self.display_message('Conrol scheme: {}'.format(self.controls))
    self.kbd_thread.start()

  def is_button(self, item):
    matching_actions = [
        action for action in self.controls
        if action['id'] == item and action.get('type', '') == 'button'
    ]
    if matching_actions:
      return True

  def get_state_updates(self):
    """Returns an iterable of control_id, state pairs for new user input."""
    try:
      item, action = self.input_queue.get(block=False).split(' ')
      if self.is_button(item):
        # hack to simulate the behavior of a real button. 
        self.input_queue.put((item + ' 0'))
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
    self.stop_event.set()
