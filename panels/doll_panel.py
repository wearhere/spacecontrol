"""Demonstration/debugging panel. Uses the shell for I/O."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import Queue
import select
import serial
import threading
from panel_client import PanelStateBase, MIN_LATENCY_MS

ser = serial.Serial(
    port='/dev/ttyACM0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

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
    {
        'id': 'rat_bite_rat_tail',
        'key': '0 1',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat bites its own tail'
        },
    },
    {
        'id': 'rat_bite_cat_bite',
        'key': '0 2',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty bites the Rat\'s mouth'
        }
    },
    {
        'id': 'rat_bite_cat_claw',
        'key': '0 3',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty claws the Rat\'s mouth'
        }
    },
    {
        'id': 'rat_bite_octo_bite',
        'key': '0 4',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat kisses the Octopus'
        }
    },
    {
        'id': 'rat_bite_octo_tentacle',
        'key': '0 5',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat bites the octopus\'s tentacle'
        }
    },
    {
        'id': 'rat_bite_girl_bite',
        'key': '0 6',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat kisses Madeline'
        }
    },
    {
        'id': 'rat_bite_girl_nipple',
        'key': '0 7',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat kisses Madeline\s nipple'
        }
    },
    {
        'id': 'rat_bite_girl_pussy',
        'key': '0 8',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat tickles Madeline\s lady bits'
        }
    },
    {
        'id': 'rat_tail_cat_bite',
        'key': '1 2',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty bites the Rat\'s tail'
        }
    },
    {
        'id': 'rat_tail_cat_claw',
        'key': '1 3',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty scratches the Rat\'s tail'
        }
    },
    {
        'id': 'rat_tail_octo_bite',
        'key': '1 4',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Octopus touches the Rat\'s mouth'
        }
    },
    {
        'id': 'rat_tail_octo_tentacle',
        'key': '1 5',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Octopus tickles the Rat\'s tail'
        }
    },
    {
        'id': 'rat_tail_girl_bite',
        'key': '1 6',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Madeline bites the Rat\'s tail'
        }
    },
    {
        'id': 'rat_tail_girl_nipple',
        'key': '1 7',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat tickles Madeline\s nipples with its tail'
        }
    },
    {
        'id': 'rat_tail_girl_pussy',
        'key': '1 8',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Rat tickles Madeline\s lady bits with its tail'
        }
    },
    {
        'id': 'cat_bite_cat_claw',
        'key': '2 3',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty licks its own claws'
        }
    },
    {
        'id': 'cat_bite_octo_bite',
        'key': '2 4',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty kisses the octopus'
        }
    },
    {
        'id': 'cat_bite_octo_tentacle',
        'key': '2 5',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty bites the Octopus\'s tentacle'
        }
    },
    {
        'id': 'cat_bite_girl_bite',
        'key': '2 6',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Madeline kisses the cat\'s lips'
        }
    },
    {
        'id': 'cat_bite_girl_nipple',
        'key': '2 7',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty licks Madeline\'s nipples'
        }
    },
    {
        'id': 'cat_bite_girl_pussy',
        'key': '2 8',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty goes down on Madeline'
        }
    },
    {
        'id': 'cat_claw_octo_bite',
        'key': '3 4',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty scratches the Octopus\'s mouth'
        }
    },
    {
        'id': 'cat_claw_octo_tentacle',
        'key': '3 5',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty scratches the Octopus\'s tentacle'
        }
    },
    {
        'id': 'cat_claw_girl_bite',
        'key': '3 6',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty claws at Madeline\'s lips'
        }
    },
    {
        'id': 'cat_claw_girl_nipple',
        'key': '3 7',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty scratches Madeline\'s nipples'
        }
    },
    {
        'id': 'cat_claw_girl_pussy',
        'key': '3 8',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Kitty scratches Madeline\'s muff'
        }
    },
    {
        'id': 'octo_bite_girl_bite',
        'key': '4 6',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Octopus and Madeline make out'
        }
    },
    {
        'id': 'octo_bite_girl_nipple',
        'key': '4 7',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Octopus plays with Madeline\'s nipples'
        }
    },
    {
        'id': 'octo_bite_girl_pussy',
        'key': '4 8',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Octopus eats Madeline out'
        }
    },
    {
        'id': 'octo_tentacle_girl_bite',
        'key': '5 6',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Madeline nibbles the octopus\'s tentacle'
        }
    },
    {
        'id': 'octo_tentacle_girl_nipple',
        'key': '5 7',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Octopus plays with Madeline\'s nipples'
        }
    },
    {
        'id': 'octo_tentacle_girl_pussy',
        'key': '5 8',
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Hentai'
        }
    },
]

def poll_doll_input(input_queue):
  while True:
    state = ser.readline()
    if state:
        input_queue.put(state)

class DollPanel(PanelStateBase):
  """Simulate a panel using the keyboard."""

  def __init__(self, stdin, player_number):
    self.input_queue = Queue.Queue()

    self.kbd_thread = threading.Thread(
        target=poll_doll_input, args=(self.input_queue))
    self.kbd_thread.start()

  def get_state_updates(self):
    """Returns an iterable of control_id, state pairs for new user input."""
    try:
        action, key = self.input_queue.get(block=False).split(',')
        control = filter(lambda x: x.key == key, CONTROL_SCHEMES)[0]
        yield control.id, action
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
    print('> ' + message)
