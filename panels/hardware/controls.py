#!/usr/bin/env python2.7
"""
The collection of our various types of controls
"""

from __future__ import division
import peripherals_stacey
from colour import Color

class Switch(object):
  def __init__(self, device, pin):
    self.device = device
    self.pin = pin

    self.prev_value = None
    self.value = None

  def read(self):
    self.prev_value = self.value
    self.value = self.device.read(self.pin)
    self.after_read()

  def after_read(self):
    pass

class SwitchWithLight(Switch):
  ACTIVE_COLOR = Color("green")
  INACTIVE_COLOR = Color("orange")

  def __init__(self, device, pin, led_id):
    Switch.__init__(self, device, pin)

    self.led_id = led_id
    self.last_color = None

  def after_read(self):
    self.set_color()

  def set_color(self):
    color = self.ACTIVE_COLOR if self.value else self.INACTIVE_COLOR
    if self.prev_color != color:
      peripherals.MAPLE.set_led(self.led_id, new_color)
      self.prev_color = color

class SwitchWithTwoLights(Switch):
  UP_ON_COLOR = Color("green")
  UP_OFF_COLOR = Color("red")

  DOWN_ON_COLOR = Color("green")
  DOWN_OFF_COLOR = Color("blue")

  def __init__(self, device, pin, led_up_id, led_down_id):
    Switch.__init__(self, device, pin)
    self.led_up_id = led_up_id
    self.led_down_id = led_down_id

  def after_read(self):
    if self.prev_value == self.value:
      return

    up_color = UP_ON_COLOR if self.value else UP_OFF_COLOR
    down_color = DOWN_OFF_COLOR if self.value else DOWN_ON_COLOR

    peripherals.MAPLE.set_led(self.led_up_id, up_color)
    peripherals.MAPLE.set_led(self.led_down_id, down_color)

class KeypadButton(SwitchWithLight):
  """Just like a switch with a light, but calls a callback on press"""

  def __init__(self, device, pin, led_id):
    SwitchWithLight.__init__(self, device, pin, led_id)
    self.callback = lambda: None

  def after_read(self):
    SwitchWithLight.after_read(self)
    if self.prev_value != self.value:
      self.callback()

class Keypad(object):
  """A keypad; this is pretty specific to my board"""
  REQUIRED_KEYS = set([0,1,2,3,4,5,6,7,8,9,'input','ok'])

  ACTIVE_COLOR = Color("green")
  INACTIVE_COLOR = Color("lime")

  DISABLED_COLOR = Color("orange")
  DISABLED_ACTIVE_COLOR = Color("orange")

  BLINK_COLOR = Color("blue")
  BLINK_INTERVAL_SEC = 0.5

  def __init__(self, buttons):
    # did we get the buttons we require?
    provided = set(buttons.keys)
    if provided != self.REQUIRED_KEYS:
      raise RuntimeError(
          "Keypad requires a dictionary of buttons with exactly keys %s, but %s was provided" % (
            self.REQUIRED_KEYS, provided))

    # save and initialize callbacks on key press
    self.buttons = buttons
    for label in self.buttons:
      self.buttons[label].callback = self.callback_for(btn)

    # internal state
    self.next_blink = 0
    self.input_mode = False
    self.blink_on_mode = False

    # set colors on the buttons
    self.set_button_colors()

    # what should we be displaying right now?
    self.display = ['H', 'E', 'H']
    self.value = list(self.display)

  def callback_for(self, label):
    return lambda: self.key_pressed(label)

  def key_pressed(self, label):
    if label == 'input':
      if not self.input_mode:
        self.input_mode = True

    elif label == 'ok':
      if self.input_mode:
        self.input_mode = False
        self.value = list(self.display)

    else:
      if self.input_mode:
        self.display = self.display[1:] + [label]

  def set_button_colors(self):
    """sets the colors for all the keys based on the current mode"""
    # in input mode, the number keys and the ok key are active
    if self.input_mode:
      # numbers are active (aka green)
      number_active_color = self.ACTIVE_COLOR
      number_inactive_color = self.INACTIVE_COLOR

      # input button is inactive
      self.buttons['input'].ACTIVE_COLOR = self.DISABLED_ACTIVE_COLOR
      self.buttons['input'].INACTIVE_COLOR = self.DISABLED_COLOR

      # the ok button is active and blinking
      self.buttons['ok'].ACTIVE_COLOR = self.ACTIVE_COLOR
      if self.blink_on_mode:
        self.buttons['ok'].INACTIVE_COLOR = self.BLINK_COLOR
      else:
        self.buttons['ok'].INACTIVE_COLOR = self.INACTIVE_COLOR

    # otherwise, only the input key is active (and is blinking)
    else:
      # numbers are inactive
      number_active_color = self.DISABLED_ACTIVE_COLOR
      number_inactive_color = self.DISABLED_COLOR

      # ok button is inactive too
      self.buttons['ok'].ACTIVE_COLOR = self.DISABLED_ACTIVE_COLOR
      self.buttons['ok'].INACTIVE_COLOR = self.DISABLED_COLOR

      # the input button is active and blinking
      self.buttons['input'].ACTIVE_COLOR = self.ACTIVE_COLOR
      if self.blink_on_mode:
        self.buttons['input'].INACTIVE_COLOR = self.BLINK_COLOR
      else:
        self.buttons['input'].INACTIVE_COLOR = self.INACTIVE_COLOR

    # now we need to iterate through the number keys and set them
    for key in xrange(0, 9):
      btn = self.buttons[key]
      btn.ACTIVE_COLOR = number_active_color
      btn.INACTIVE_COLOR = number_inactive_color

  def read(self):
    # handle blinking
    now = time.time()
    if now > next_blink:
      next_blink = now + self.BLINK_INTERVAL
      self.blink_on_mode = not self.blink_on_mode

    # set the button colors based on the current mode
    self.set_button_colors()

    # now lets read the inputs; that will set colors if necessary
    for btn in self.buttons:
      btn.read()

class Analog(object):
  CHANGE_THRESHOLD = 0.05

  """An analog input (potentiometer)"""
  def __init__(self, device, pin, scaled=True):
    self.device = device
    self.pin = pin

    # initialize hysterisis
    self.prev_value = 0
    self.value = 0

    # enable reading that pin
    self.device.enable_pin(pin)
    self.scaled = scaled

  def read(self):
    cur_value = self.device.read(self.pin)

    # we only save the new value if it's changed more than threshold
    # this prevents oscillating due to analog jitter
    change = abs(1 - self.value/cur_value)
    if change > self.CHANGE_THRESHOLD:
      self.prev_value = self.value
      self.value = cur_value

    self.after_read()

  def after_read(self):
    pass

class Slider(Analog):
  """ Linear potentiometer """
  def __init__(self, device, pin, num_bins):
    Analog.__init__(self, device, pin, scaled=False)
    self.max_val = 4095
    self.num_bins = num_bins
    self.bin_size = self.max_val / num_bins

  def read_sector(self):
    """ Return the sector/bin into which the value falls"""
    try:
      bin_id = self.read() / self.bin_size
      return bin_id
    except:
      print "Slider value too big: ", self.read()
      return num_bins

class RotaryMeter(Slider):
  """Rotating potentiometer! How is this different? Unclear"""
  def __init__(self, device, pin, num_bins):
    Slider.__init__(self, device, pin, num_bins)
    self.max_val = 3950

class Accelerator(Analog):
  """A potentiometer with LEDs indicating the position"""
  def __init__(self, device, pin, first_led_id, led_count):
    Analog.__init__(self, device, pin)
    self.first_led_id = first_led_id
    self.led_count = led_count

    # configure the colors
    starting_color = Color("blue")
    starting_color.set_luminance(0.1)
    ending_color = Color("orange")
    ending_color.set_luminance(0.8)
    self.color_range = list(starting_color.range_to(ending_color, 41))

  def after_read(self):
    self.set_leds()

  def set_leds(self):
    """loads the attached led string with the correct colors"""
    # no nothing if the position hasn't changed
    if self.value == self.prev_value:
      pass

    pct = float(self.value) / 100
    last_led_on = int(pct * self.led_count)

    color_range_idx = int(pct * len(self.color_range))
    on_color = self.color_range[color_range_idx]

    # the leds that are on
    new_colors = \
      [on_color] * last_led_on + [Color("black")] * (self.led_count - last_led_on) # leds that are off

    peripherals.MAPLE.set_led_batch(self.first_led_id, new_colors)

class RotaryEncoder(object):
  """A rotary encoder!"""
  pass

class HandScanner(object):
  """Pretends to be a hand scanner, but really just temperature"""
  pass
