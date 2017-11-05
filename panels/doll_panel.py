"""Demonstration/debugging panel. Uses the shell for I/O."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import Queue
from progress_lcd import ProgressLCD
from sound_system import SoundSystem
import select
import serial
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

touch_def = {
    '0': 'rat_bite',
    '1': 'rat_body',
    '2': 'rat_tail',
    '3': 'cat_bite',
    '4': 'cat_claw',
    '5': 'octo_bite',
    '6': 'octo_tentacle',
    '7': 'girl_bite',
    '8': 'girl_nipple',
    '9': 'girl_pussy',
    '10': 'blood_a',
    '11': 'blood_o',
    '12': 'syringe',
    '13': 'clown_butt',
    '14': 'bird_bite',
    # '15': 'clown belly',
    # '16': 'clown_dick',
    # '17': 'bird_shake'
}

CONTROL_SCHEMES = [
    {
        'id': 'rat_bite_rat_tail',
        'sounds': ['squeaky kiss.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat bites its own tail'
        },
    },
    {
        'id': 'rat_bite_cat_bite',
        'sounds': ['cat bite.wav', 'squeaky rat.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty bites the Rat\'s mouth'
        }
    },
    {
        'id': 'rat_bite_cat_claw',
        'sounds': ['cat scratch.wav', 'rat squeak.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty claws the Rat\'s mouth'
        }
    },
    {
        'id': 'rat_bite_octo_bite',
        'sounds': ['water churn.wav', 'squeaky kiss.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat kisses the Octopus'
        }
    },
    {
        'id': 'rat_bite_octo_tentacle',
        'sounds': ['tent squish.wav', 'dog toy squish.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat bites the octopus\'s tentacle'
        }
    },
    {
        'id': 'rat_bite_girl_bite',
        'sounds': ['kiss.wav', 'girl kiss.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat kisses Madeline'
        }
    },
    {
        'id': 'rat_bite_girl_nipple',
        'sounds': ['nipple giggle.wav', 'squeaky kiss.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat kisses Madeline\'s nipple'
        }
    },
    {
        'id': 'rat_bite_girl_pussy',
        'sounds': ['girl resistant moan.wav', 'laughingmice.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat tickles Madeline\'s lady bits with its tongue'
        }
    },
    {
        'id': 'rat_bite_bird_bite',
        'sounds': ['chomp.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat kisses the Vampire Bird'
        }
    },
    {
        'id': 'rat_body_octo_tentacle',
        'sounds': ['water splash.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Octopus inserts tentacle into Rat\'s body'
        }
    },
    {
        'id': 'rat_body_blood_a',
        'sounds': ['water churn.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Infuse A-type blood into Rat'
        }
    },
    {
        'id': 'rat_body_blood_o',
        'sounds': ['water churn.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Infuse O-type blood into Rat'
        }
    },
    {
        'id': 'rat_body_syringe',
        'sounds': ['squeaky rat.wav'],
        'state': '-1',
        'actions': {
            '-1': '',
            '0': 'Inject Manganate into the Rat\'s body',
            '1': 'Inject L-Theanine into the Rat\'s body',
            '2': 'Inject Hemoglobin into the Rat\'s body',
        }
    },
    {
        'id': 'rat_body_bird_bite',
        'sounds': ['chomp.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Vampire Bird draws blood from Rat\'s body'
        }
    },
    {
        'id': 'rat_tail_cat_bite',
        'sounds': ['cat bite.wav', 'squeaky rat.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty bites the Rat\'s tail'
        }
    },
    {
        'id': 'rat_tail_cat_claw',
        'sounds': ['cat scratch.wav', 'rat squeak.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty scratches the Rat\'s tail'
        }
    },
    {
        'id': 'rat_tail_octo_bite',
        'sounds': ['octo whimper.wav', 'squeaky rat.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Octopus nibbles the Rat\'s tail'
        }
    },
    {
        'id': 'rat_tail_octo_tentacle',
        'sounds': ['clown-teehee.wav', 'dog toy squish.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Octopus brushes Rat\'s tail with tentacle'
        }
    },
    {
        'id': 'rat_tail_girl_bite',
        'sounds': ['chomp.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Madeline bites the Rat\'s tail'
        }
    },
    {
        'id': 'rat_tail_girl_nipple',
        'sounds': ['girl gasp.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat tickles Madeline\'s nipples with its tail'
        }
    },
    {
        'id': 'rat_tail_girl_pussy',
        'sounds': ['girl scream rat tail.wav', 'rat squeak.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat tickles Madeline\'s lady bits with its tail'
        }
    },
    {
        'id': 'cat_bite_cat_claw',
        'sounds': ['long purr.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty licks its own claws'
        }
    },
    {
        'id': 'cat_bite_octo_bite',
        'sounds': ['cat slurp.wav', 'water churn.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty kisses the octopus'
        }
    },
    {
        'id': 'cat_bite_octo_tentacle',
        'sounds': ['cat bite.wav', 'octo whimper.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty bites the Octopus\'s tentacle'
        }
    },
    {
        'id': 'cat_bite_girl_bite',
        'sounds': ['kiss breath.wav', 'light purr.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Madeline kisses the cat\'s lips'
        }
    },
    {
        'id': 'cat_bite_girl_nipple',
        'sounds': ['nipple giggle.wav', 'kitten meow.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty licks Madeline\'s nipples'
        }
    },
    {
        'id': 'cat_bite_girl_pussy',
        'sounds': ['meow commercial.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty goes down on Madeline'
        }
    },
    {
        'id': 'cat_bite_blood_a',
        'sounds': ['cat slurp.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Feed A-type blood to Cat'
        }
    },
    {
        'id': 'cat_bite_blood_o',
        'sounds': ['cat slurp.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Feed O-type blood to Kitteh'
        }
    },
    {
        'id': 'cat_bite_syringe',
        'sounds': ['cat slurp.wav'],
        'state': '-1',
        'actions': {
            '-1': '',
            '0': 'Feed Kitty some Manganate',
            '1': 'Force feed the Cat L-Theanine',
            '2': 'Inject Hemoglobin into the Cat\'s mouth',
        }
    },
    {
        'id': 'cat_bite_bird_bite',
        'sounds': ['chomp.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty kisses the Vampire Bird'
        }
    },
    {
        'id': 'cat_claw_octo_bite',
        'sounds': ['tom cat.wav', 'octo roar.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty scratches the Octopus\'s mouth'
        }
    },
    {
        'id': 'cat_claw_octo_tentacle',
        'sounds': ['puking or fighting.wav', 'cat scream.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty scratches the Octopus\'s tentacle'
        }
    },
    {
        'id': 'cat_claw_girl_bite',
        'sounds': ['throat clearing.wav', 'kitten meow.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty claws at Madeline\'s lips'
        }
    },
    {
        'id': 'cat_claw_girl_nipple',
        'sounds': ['girl ouch.wav', 'cat meow.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty scratches Madeline\'s nipples'
        }
    },
    {
        'id': 'cat_claw_girl_pussy',
        'sounds': ['girl gasp.wav', 'tom cat.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty scratches Madeline\'s muff'
        }
    },
    {
        'id': 'cat_claw_bird_bite',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty claws the Vampire Bird\'s beak'
        }
    },
    {
        'id': 'octo_bite_girl_bite',
        'sounds': ['kiss.wav', 'girl kiss.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Octopus and Madeline make out'
        }
    },
    {
        'id': 'octo_bite_girl_nipple',
        'sounds': ['girl resistant moan.wav', 'cat slurp.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Octopus nibbles Madeline\'s nipples'
        }
    },
    {
        'id': 'octo_bite_girl_pussy',
        'sounds': ['song easter egg.wav', 'water churn.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Octopus eats Madeline out'
        }
    },
    {
        'id': 'octo_bite_bird_bite',
        'sounds': ['kiss.wav', 'bird-call.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Vampire Bird kisses the Octopus'
        }
    },
    {
        'id': 'octo_tentacle_girl_bite',
        'sounds': ['girl gasp.wav', 'cat_licking.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Madeline nibbles the octopus\'s tentacle'
        }
    },
    {
        'id': 'octo_tentacle_girl_nipple',
        'sounds': ['surprise moan girl.wav', 'water splash.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Octopus plays with Madeline\'s nipples with its tentacle'
        }
    },
    {
        'id': 'octo_tentacle_girl_pussy',
        'sounds': ['dubstep porn loop.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Hentai'
        }
    },
    {
        'id': 'girl_bite_bird_bite',
        'sounds': ['kiss.wav', 'girl kiss.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Vampire Bird kisses Madeline'
        }
    },
    {
        'id': 'girl_nipple_bird_bite',
        'sounds': ['nipple giggle.wav', 'bird-call.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Vampire Bird nuzzles Madeline\'s nipple'
        }
    },
    {
        'id': 'girl_pussy_bird_bite',
        'sounds': ['girl gasp.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Vampire Bird teethes Madeline\'s down low'
        }
    },
    {
        'id': 'blood_a_bird_bite',
        'sounds': ['cat slurp.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Feed A-type Blood to Vampire Bird'
        }
    },
    {
        'id': 'blood_o_bird_bite',
        'sounds': ['cat slurp.wav'],
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Feed O-type Blood to Vampire Bird'
        }
    },
    {
        'id': 'syringe_bird_bite',
        'sounds': ['cat slurp.wav'],
        'state': '0',
        'actions': {
            '-1': '',
            '0': '',
            '1': '',
            '2': 'Feed some Hemoglobin to the Vampire Bird',
        }
    },
]

def poll_doll_input(input_queue):
  ser = serial.Serial(
      port='/dev/ttyACM0',
      baudrate=9600,
      parity=serial.PARITY_NONE,
      stopbits=serial.STOPBITS_ONE,
      bytesize=serial.EIGHTBITS,
      timeout=1
  )

  while True:
    state = ser.readline()
    if state:
        input_queue.put(state)

class DollPanel(PanelStateBase):
  """Simulate a panel using the keyboard."""

  def __init__(self):
    self.input_queue = Queue.Queue()
    self.input_thread = threading.Thread(
        target=poll_doll_input, args=(self.input_queue,))
    self.input_thread.start()
    self.lcd = ProgressLCD(rs_pin=25, en_pin=24, d4_pin=23, d5_pin=17,
      d6_pin=21, d7_pin=22)
    self.sound_system = SoundSystem()

  def get_state_updates(self):
    """Returns an iterable of control_id, state pairs for new user input."""
    try:
        action, key = self.input_queue.get(block=False).rstrip().split(',')
        first, second = key.split(' ')
        id = '{0}_{1}'.format(touch_def[first], touch_def[second])

        print('Setting {0} to {1}'.format(id, action))
        control = [c for c in CONTROL_SCHEMES if c['id'] == id]
        if len(control) > 0:
            print('Sending: {0} to {1}'.format(id, action))
            if control[0].get('sounds') and control[0]['actions'].get(action) and len(control[0]['actions'].get(action)) > 0:
                self.sound_system.play_sounds(control[0]['sounds'])
            yield control[0]['id'], action
        return
    except ValueError:
      self.display_message(
          'Invalid format. Must be of the form "control_id state"')
    except Queue.Empty:
      return

  def get_controls(self):
    """Must implement this function for your panel.

    Should return the available controls.
    """
    return CONTROL_SCHEMES

  def display_message(self, message):
    """Prints the message with a prefix (to differentiate it from what the user types)."""
    self.lcd.display_message(message)
    print('> {0}'.format(message))

  def display_status(self, message):
    self.lcd.display_status(message)
    print('Status {0}'.format(message))

  def display_progress(self, value):
    self.lcd.display_progress(value)
    print('Prog {0}'.format(value))
