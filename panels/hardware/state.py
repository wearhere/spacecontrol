#!/usr/bin/env python2.7
"""
Contains and manages the current state of the game
"""

from peripherals_stacey import *
from controls import *

MERINGUE_INPUTS = {
    # ROTARY SWITCHES
    "rs_1_rainbow": Slider(
      device=BLACKPILL,
      pin=0,
      num_bins=6,
      max_val=3950,
      ),
    "rs_2_dark_sky": Slider(
      device=BLACKPILL,
      pin=1,
      num_bins=9,
      max_val=3950,
      ),
    "rs_3_kardashev": Slider(
      device=BLACKPILL,
      pin=2,
      num_bins=5,
      max_val=3950,
      ),
    # TOP LIGHT-UP BUTTONS
    "b_top_blue": Switch(
      device=BLACKPILL,
      pin=3,
      ),
    "b_top_white": Switch(
      device=BLACKPILL,
      pin=4,
      ),
    "b_top_green": Switch(
      device=BLACKPILL,
      pin=5,
      ),   
    "b_top_yellow": Switch(
      device=BLACKPILL,
      pin=6,
      ),
    # LEFT SMALL BUTTONS
    "b_left_blue": Switch(
      device=BLACKPILL,
      pin=7,
      ),
    "b_left_green": Switch(
      device=BLACKPILL,
      pin=8,
      ),
    "b_left_black": Switch(
      device=BLACKPILL,
      pin=9,
      ),
    # SLIDERS
    "slide_1_temp": Slider(
      device=BLACKPILL,
      pin=10,
      num_bins=5,
      max_val=4095,
      ),
    "slide_2_encounters": Slider(
      device=BLACKPILL,
      pin=11,
      num_bins=7,
      max_val=4095,
      ),
    # TRIPLE SWITCHES
    "ts_tongue" : TripleSwitch(
      device=BLACKPILL,
      up_pin=12,
      down_pin=13,
      ),
    "ts_light_blue_dick" : TripleSwitch(
      device=BLACKPILL,
      up_pin=14,
      down_pin=15,
      ),
    "ts_big_balls_dick_1" : TripleSwitch(
      device=BLACKPILL,
      up_pin = 17,
      down_pin=16,
      ),
    }

def generate(inputs=MERINGUE_INPUTS):
  state = {}
  for tag, control in inputs.items():
    control.read()
    state[tag] = str(control.value)
  print "statei in generate: ", state
  return state
