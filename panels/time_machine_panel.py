"""Doll Panel."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from panel_client import PanelStateBase, _validate_controls
import control_manager 

import progress_lcd
import RPi.GPIO as GPIO
from Adafruit_GPIO import MCP230xx


class TimeMachinePanel(PanelStateBase):
  """Simulate a panel using the keyboard."""

  def __init__(self):
    self.lcd = progress_lcd.ProgressLCD(rs_pin=17, en_pin=27, d4_pin=9, d5_pin=11, d6_pin=5, d7_pin=6)
    self.lcd.display_message('Welcome, Time-Traveller!')
    GPIO.setmode(GPIO.BCM)


    self.aux_systems_to_pins = {'Forward Deflector':4, 'Morlock Suppressor':0, 'Turbo Encabulator':5, 'Spline Reticulator':1, 'Flux Capacitor':2, 'Stallyn\'s Amps':6, 'Eye of Harmony':3, 'Improbability Drive':7}
    self.inverter_pins = [12, 8, 13, 9, 11, 15, 10, 14]
    self.shunt_pins = [15, 14, 13, 12, 11, 10, 9, 8]
    self.reactor_pin = 4
    self.tachyon_pins = [22, 10]


    self.tachyon_pins = [22, 10]
    self.reactor_pin = 4
    self.grav_pins = [8, 25, 24, 23, 18, 21, 20, 16, 12, 7]
    for pin in [self.reactor_pin]+self.tachyon_pins+self.grav_pins:
      GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    self.MCP0 = MCP230xx.MCP23017(0x20)
    self.MCP7 = MCP230xx.MCP23017(0x27)
    for pin in range(16):
      for MCP in [self.MCP0, self.MCP7]:
        MCP.setup(pin, GPIO.IN)
        MCP.pullup(pin, True)


    self.controls = control_manager.SpaceTeamControls()


    # MCP0 controls
    self.controls.make_button_array('inverters{}', self.MCP0.input, self.inverter_pins, 
                                    button_text = "Invert residuum {}!")
    for name, pin in self.aux_systems_to_pins.iteritems():
      self.controls.make_toggle(name, control_manager.toggle_reader(pin, self.MCP0.input), 
                                toggle_texts=['Route auxilliary power to the {}'.format(name),
                                              'Cut auxilliary power to the {}'.format(name)])

    #MCP7 controls
    self.controls.make_toggle_array('shunt{}', self.MCP7.input, self.shunt_pins, 
                                    toggle_texts=['Enable cyclotron shunt {}', 
                                                  'Disable cyclotron shunt {}'])

    #GPIO controls
    self.controls.make_toggle('reactor', control_manager.toggle_reader(self.reactor_pin, GPIO.input),
                              toggle_texts=['Engage the chronotonic reactor!',
                                            'DISENGAGE CHRONOTONIC REACTOR'])
    self.controls.make_button_array('tachyon{}', GPIO.input, self.tachyon_pins,
                                    button_text='Bleed tachyoners from valve {}')
    self.controls.make_toggle_array('graviton{}', GPIO.input, self.grav_pins,
                                    toggle_texts=['Disengage graviton flux restrictor {}!',
                                                  'Engage graviton flux restrictor {}!'])

    self._state = self.controls.read_state()


  def get_state_updates(self):
    """Returns an iterable of control_id, state pairs for new user input."""
    old_state = self._state
    self._state = self.controls.read_state()
    for item, val in self.diff_states(old_state, self._state).iteritems():
      print(item, val)
      yield item, val

  def get_controls(self):
    """Must implement this function for your panel.

    Should return the available controls.
    """
    return self.controls.get_controls_data()

  def display_message(self, message):
    """Prints the message with a prefix (to differentiate it from what the user types)."""
    self.lcd.display_message(message)

  def display_status(self, message):
    self.lcd.display_status(message)

  def display_progress(self, data):
    self.lcd.display_progress(data)

