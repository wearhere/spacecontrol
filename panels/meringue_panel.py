"""Demonstration/debugging panel. Uses the shell for I/O."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import Queue
import select
import threading
from panel_client import PanelStateBase, MIN_LATENCY_MS

import hardware

# load and initialize peripherals
from hardware import peripherals_stacey
peripherals_stacey.reset_all()

# initialize local state
# TODO: separate config for different panels?
from hardware import state

CONTROL_SCHEMES = [
  {
    # weather: [frosty, chill, meh, hot in here, wtf] [0-4095 % 5]
    'id': 'slide_1',
    'state': 'frosty',
    'actions': {
      'frosty': 'Forecast says frosty',
      'chill': 'Forecast says chill',
      'meh': 'The weather is meh',
      'hot': 'It\'s getting hot in here',
      'wtf': 'This weather is wtf'
    },
  },
  {
    # hynek: [1, 2, 3, 4, 5, 6, 7] [0-4095 % 5] 
    'id': 'slide_2',
    'state': '1',
    'actions': {
      '1': 'UFO on the horizon!',
      '2': 'Walking in a crop circle',
      '3': 'The aliens are waving to you',
      '4': 'Alien abduction',
      '5': 'Pinging the aliens',
      '6': 'Extraterrestrial invasion',
      '7': 'Extraterrestrial lovemaking'
    },
  },
  {
    # rainbow wheel: [red, orange, yellow, green, blue, purple]
    # at higher levels, show various fruit?
    # at higher levels, show R G B pixel values :P
    # TODO: multiple levels of difficulty?
    'id': 'rs_1',
    'state': 'red',
    'action': {
      'red': 'Strawberries!',
      'orange': 'Orange',
      'yellow': 'Banana',
      'green' : 'Cucumber',
      'blue': 'Blueberries',
      'purple': 'Eggplant'
    },
  },
  {
    # Bortle dark sky scale: [1-9] [0-3950] % 8
    'id': 'rs_2',
    'state': '1',
    'action': {
      '1': 'North Pole sky',
      '2': 'Australian outback sky',
      '3': 'Remote countryside sky',
      '4': 'Small suburb sky',
      '5': 'Large suburb sky',
      '6': 'Small city sky',
      '7': 'Bay Area sky',
      '8': 'Big city sky',
      '9': 'Times Square sky'
    },
  }
]
        #'actions': [['0', '1', '2'], 'Set Froomulator to %s!'],
        # TODO: do we care about the type of controller?
        #'type': 'switch'

class MeringuePanel(PanelStateBase):
  """Meringue panel prototype situation"""

  def __init__(self):
    # poll peripherals here before returning
    self.controls = CONTROL_SCHEMES
    self.display_message('Conrol scheme: {}'.format(self.controls))
    self.prev_state = state.generate()
    print(self.prev_state)

  def get_state_updates(self):
    """Returns an iterable of control_id, state pairs for new user input."""
    try:
      # get new state from all peripherals
      new_state = state.generate()
      state_changes = self.diff_states(self.prev_state, new_state)
      self.prev_state = new_state
      for control_id, state_value in state_changes.items():
        yield control_id, state_value
    except ValueError:
      self.display_message(
          'Invalid format. Must be of the form "control_id state"')

  def get_controls(self):
    """Must implement this function for your panel.

    Should return the available controls.
    """
    return self.controls

  def display_message(self, message):
    """Prints the message."""
    print(message)

