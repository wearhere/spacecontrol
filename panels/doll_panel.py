"""Demonstration/debugging panel. Uses the shell for I/O."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import Queue
from progress_lcd import ProgressLCD
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
    '11': 'blood_o'
}

# touch_def = ['rat_bite', 'rat_body', 'rat_tail', 'cat_bite', 'cat_claw', 'octo_bite', 'octo_tentacle',
#            'girl_bite', 'girl_nipple', 'girl_pussy', 'blood_a', 'blood_o', 'syringe', 'clown_leg',
#            'bird_bite']

CONTROL_SCHEMES = [
    {
        'id': 'rat_bite_rat_tail',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat bites its own tail'
        },
    },
    {
        'id': 'rat_bite_cat_bite',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty bites the Rat\'s mouth'
        }
    },
    {
        'id': 'rat_bite_cat_claw',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty claws the Rat\'s mouth'
        }
    },
    {
        'id': 'rat_bite_octo_bite',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat kisses the Octopus'
        }
    },
    {
        'id': 'rat_bite_octo_tentacle',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat bites the octopus\'s tentacle'
        }
    },
    {
        'id': 'rat_bite_girl_bite',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat kisses Madeline'
        }
    },
    {
        'id': 'rat_bite_girl_nipple',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat kisses Madeline\'s nipple'
        }
    },
    {
        'id': 'rat_bite_girl_pussy',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat tickles Madeline\'s lady bits'
        }
    },
    {
        'id': 'rat_body_octo_tentacle',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Octopus inserts tentacle into Rat\'s body'
        }
    },
    {
        'id': 'rat_body_blood_a',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Infuse A-type blood into Rat'
        }
    },
    {
        'id': 'rat_body_blood_o',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Infuse O-type blood into Rat'
        }
    },
    {
        'id': 'rat_tail_cat_bite',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty bites the Rat\'s tail'
        }
    },
    {
        'id': 'rat_tail_cat_claw',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty scratches the Rat\'s tail'
        }
    },
    {
        'id': 'rat_tail_octo_bite',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Octopus nibbles the Rat\'s tail'
        }
    },
    {
        'id': 'rat_tail_octo_tentacle',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Octopus brushes Rat\'s tail with tentacle'
        }
    },
    {
        'id': 'rat_tail_girl_bite',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Madeline bites the Rat\'s tail'
        }
    },
    {
        'id': 'rat_tail_girl_nipple',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat tickles Madeline\'s nipples with its tail'
        }
    },
    {
        'id': 'rat_tail_girl_pussy',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat tickles Madeline\'s lady bits with its tail'
        }
    },
    {
        'id': 'cat_bite_cat_claw',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty licks its own claws'
        }
    },
    {
        'id': 'cat_bite_octo_bite',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty kisses the octopus'
        }
    },
    {
        'id': 'cat_bite_octo_tentacle',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty bites the Octopus\'s tentacle'
        }
    },
    {
        'id': 'cat_bite_girl_bite',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Madeline kisses the cat\'s lips'
        }
    },
    {
        'id': 'cat_bite_girl_nipple',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty licks Madeline\'s nipples'
        }
    },
    {
        'id': 'cat_bite_girl_pussy',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty goes down on Madeline'
        }
    },
    {
        'id': 'cat_bite_blood_a',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Feed A-type blood to Cat'
        }
    },
    {
        'id': 'cat_bite_blood_o',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Feed O-type blood to Kitteh'
        }
    },
    {
        'id': 'cat_claw_octo_bite',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty scratches the Octopus\'s mouth'
        }
    },
    {
        'id': 'cat_claw_octo_tentacle',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty scratches the Octopus\'s tentacle'
        }
    },
    {
        'id': 'cat_claw_girl_bite',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty claws at Madeline\'s lips'
        }
    },
    {
        'id': 'cat_claw_girl_nipple',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty scratches Madeline\'s nipples'
        }
    },
    {
        'id': 'cat_claw_girl_pussy',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty scratches Madeline\'s muff'
        }
    },
    {
        'id': 'octo_bite_girl_bite',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Octopus and Madeline make out'
        }
    },
    {
        'id': 'octo_bite_girl_nipple',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Octopus plays with Madeline\'s nipples'
        }
    },
    {
        'id': 'octo_bite_girl_pussy',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Octopus eats Madeline out'
        }
    },
    {
        'id': 'octo_tentacle_girl_bite',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Madeline nibbles the octopus\'s tentacle'
        }
    },
    {
        'id': 'octo_tentacle_girl_nipple',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Octopus plays with Madeline\'s nipples with its tentacle'
        }
    },
    {
        'id': 'octo_tentacle_girl_pussy',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Hentai'
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

  def get_state_updates(self):
    """Returns an iterable of control_id, state pairs for new user input."""
    try:
        action, key = self.input_queue.get(block=False).rstrip().split(',')
        first, second = key.split(' ')
        id = '{0}_{1}'.format(touch_def[first], touch_def[second])

        print('Setting {0} to {1}'.format(id, action))
        control = [c.id for c in CONTROL_SCHEMES if c.id == id]
        if len(control) > 0:
            yield control[0], action
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

  def display_status(self, data):
    self.lcd.display_progress(data['progress'])
    print('Do {0}'.format(data))
