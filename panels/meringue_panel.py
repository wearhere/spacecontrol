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
    'id': 'slide_1_temp',
    'state': '0',
    'actions': {
      '4': 'It\'s fucking freezing',
      '3': 'Kinda chilly in here',
      '2': 'The weather is mild and pleasant',
      '1': 'It\'s getting warm in here',
      '0': 'OMG SO FUCKING HOT IN HERE'
    },
  },
  {
    # hynek: [1, 2, 3, 4, 5, 6, 7] [0-4095 % 5] 
    'id': 'slide_2_encounters',
    'state': '0',
    'actions': {
      '0': 'First kind: UFO on the horizon!',
      '1': 'Second kind: in a crop circle',
      '2': 'Third kind: aliens waving to you',
      '3': 'Fourth kind: alien abduction',
      '4': 'Fifth kind: Pinging the aliens',
      '5': 'Sixth kind: Extraterrestrial invasion',
      '6': 'Seventh kind: Extraterrestrial lovemaking'
    },
  },
  {
    # rainbow wheel: [red, orange, yellow, green, blue, purple]
    # at higher levels, show various fruit?
    # at higher levels, show R G B pixel values :P
    # TODO: multiple levels of difficulty?
    'id': 'rs_1_rainbow',
    'state': '0',
    'actions': {
      '5': 'Strawberries',
      '4': 'Orange',
      '3': 'Banana',
      '2': 'Cucumber',
      '1': 'Blueberries',
      '0': 'Eggplant'
    },
  },
  {
    # Bortle dark sky scale: [1-9] [0-3950] % 8
    'id': 'rs_2_dark_sky',
    'state': '0',
    'actions': {
      '0': 'Remote wilderness sky',
      '1': 'Countryside sky',
      '2': 'Small subub sky',
      '3': 'Big suburb sky',
      '4': 'San Francisco sky',
      '5': 'Manhattan sky'
    },
  },
  #{
    # Kardashev scale of civilization [1-5] [3950] % 5
   # 'id': 'rs_3_kardashev',
   # 'state': '0',
   # 'actions': {
   #   '0': 'Type I: planetary civilization with a parent star',
   #   '1': 'Type II: planet harvests full energy of parent star',
   #   '2': 'Type III: civilization controls entire galaxy',
   #   '3': 'Type IV: civilization controls entire universe',
   #   '4': 'Type V: civilization controls collections of universes!',
   # },
  #},
  # LIGHT UP BUTTONS
  {
    # top button blue
    'id': 'b_top_blue',
    'state': '0',
    'actions': {
      '0': '',
      '1': 'Launch Infinite Improbability Drive!',
    },
  },
  {
    # top button white
    'id': 'b_top_white',
    'state': '0',
    'actions': {
      '0': '',
      '1': 'Say thanks for all the fish',
    },
  },
  {
    # top button green
    'id': 'b_top_green',
    'state': '0',
    'actions': {
      '0': '',
      '1': 'Subvert the dominant paradigm',
    },
  },
  {
    # top button yellow
    'id': 'b_top_yellow',
    'state': '0',
    'actions': {
      '0': '',
      '1': 'Shuffle off this mortal coil',
    },
  },
  # SMALL LEFT BUTTONS
  {
    'id': 'b_left_blue',
    'state': '0',
    'actions': {
      '0': '',
      '1': 'Soar angelic',
    },
  },
  {
    'id': 'b_left_green',
    'state': '0',
    'actions': {
      '0': '',
      '1': 'Make this trivial world sublime',
    },
  },
  {
    'id': 'b_left_black',
    'state': '0',
    'actions': {
      '0': '',
      '1': 'Fathom hell',
    },
  },
  # TRIPLE SWITCHES
  #{
  #  'id': 'tongue_tsw',
  #  'state': 'neutral',
  #  'actions': {
  #    'neutral': 'Tongue sticks straight out',
  #    'up': 'Tongue licks all the way up',
  #    'down': 'Tongue licks all the way down',
  #    },
  #},
  #{
  #  'id': 'light_blue_sw',
  #  'state': 'neutral',
  #  'actions': {
  #    'neutral': 'Periwinkle dick is chilling',
  #    'up': 'Periwinkle dick is hard',
  #    'down': 'Periwinkle dick is flaccid',
  #    },
  #},
  #{
  #  'id': 'big_balls_sw',
  #  'state': 'neutral',
  #  'actions': {
  #    'neutral': 'Big balls dick is chilling',
  #    'up': 'Big ball dick is hard',
  #    'down': 'Big ball dick is flaccid',
  #  },
  #},
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

  def display_status(self, message):
    """Prints the message with a prefix (to differentiate it from what the user types)."""
    # when received, put on fourth
    print('> ' + message)

  def display_progress(self, value):
    # when recieved, put on fourth
    pass
