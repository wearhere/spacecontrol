"""Doll Panel."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from panel_client import PanelStateBase, _validate_controls
import scrolling_lcd
import RPi.GPIO as GPIO

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
tachyon_string = 'tachyon_bleed_valve_{}'

CONTROL_SCHEMES = [
    {
        'id': tachyon_string.format(1),
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Release tachyon pressure from valve 1!'
        },
    },
    {
        'id': tachyon_string.format(2),
        'state': '0',
        'actions': {
            '0': '',
            '1': 'Release tachyon pressure from valve 2!'
        },
    },
]

_validate_controls(CONTROL_SCHEMES)

class TimeMachinePanel(PanelStateBase):
  """Simulate a panel using the keyboard."""

  def __init__(self):
    self.lcd = scrolling_lcd.ScrollingLCD()
    self.lcd.display('Welcome, Time-Traveller!')
    GPIO.setmode(GPIO.BCM)
    self.t1_pin = 5
    self.t2_pin = 6
    self.pins = [self.t1_pin, self.t2_pin]
    self.pins_to_buttons = {pin:button+1 for button, pin in enumerate(self.pins)}

    for pin in self.pins:
      GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

  def get_state_updates(self):
    """Returns an iterable of control_id, state pairs for new user input."""
    for pin in self.pins:
      yield tachyon_string.format(self.pins_to_buttons[pin]), GPIO.input(pin)

  def get_controls(self):
    """Must implement this function for your panel.

    Should return the available controls.
    """
    return CONTROL_SCHEMES

  def display_message(self, message):
    """Prints the message with a prefix (to differentiate it from what the user types)."""
    print(message)
    self.lcd.display(str(message))

  def display_status(self, data):
    print(data)
    #self.lcd.display(str(data))
    pass
