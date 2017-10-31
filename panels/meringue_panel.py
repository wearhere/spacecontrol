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
    'state': '0',
    'actions': {
      '0': 'Forecast says frosty',
      '1': 'Forecast says chill',
      '2': 'The weather is meh',
      '3': 'It\'s getting hot in here',
      '4': 'This weather is wtf'
    },
  },
  {
    # hynek: [1, 2, 3, 4, 5, 6, 7] [0-4095 % 5] 
    'id': 'slide_2',
    'state': '0',
    'actions': {
      '0': 'UFO on the horizon!',
      '1': 'Walking in a crop circle',
      '2': 'The aliens are waving to you',
      '3': 'Alien abduction',
      '4': 'Pinging the aliens',
      '5': 'Extraterrestrial invasion',
      '6': 'Extraterrestrial lovemaking'
    },
  },
  {
    # rainbow wheel: [red, orange, yellow, green, blue, purple]
    # at higher levels, show various fruit?
    # at higher levels, show R G B pixel values :P
    # TODO: multiple levels of difficulty?
    'id': 'rs_1',
    'state': '0',
    'actions': {
      '0': 'Strawberries!',
      '1': 'Orange',
      '2': 'Banana',
      '3' : 'Cucumber',
      '4': 'Blueberries',
      '5': 'Eggplant'
    },
  },
  {
    # Bortle dark sky scale: [1-9] [0-3950] % 8
    'id': 'rs_2',
    'state': '0',
    'actions': {
      '0': 'North Pole sky',
      '1': 'Australian outback sky',
      '2': 'Remote countryside sky',
      '3': 'Small suburb sky',
      '4': 'Large suburb sky',
      '5': 'Small city sky',
      '6': 'Bay Area sky',
      '7': 'Big city sky',
      '8': 'Times Square sky'
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
    """Prints the message with a prefix (to differentiate it from what the user types)."""
    print('> ' + message)

  def display_status(self, data):
    """Prints the message with a prefix (to differentiate it from what the user types)."""
    if 'message' in data:
      # Ignore empty messages i.e. clearing the status.
      if data['message']:
        print('> ' + data['message'])
    #elif 'progress' in data:
    #  print('> ' + (' ' * int(math.floor(data['progress'] * LCD_WIDTH))))

