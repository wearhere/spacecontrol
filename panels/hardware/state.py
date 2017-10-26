#!/usr/bin/env python2.7
"""
Contains and manages the current state of the game
"""

from peripherals_stacey import *
from controls import *

MERINGUE_INPUTS = {
    "rs_1": RotaryMeter(
      device=BLACKPILL,
      pin=0,
      num_bins=6,
      ),
    "rs_2": RotaryMeter(
      device=BLACKPILL,
      pin=1,
      num_bins=9
      ),
    "slide_1": Slider(
      device=BLACKPILL,
      pin=2,
      num_bins=5
      ),
    "slide_2": Slider(
      device=BLACKPILL,
      pin=3,
      num_bins=7
      ),
    }

def generate(inputs=MERINGUE_INPUTS):
  state = {}
  for tag, control in inputs.items():
    control.read()
    state[tag] = control.value

  return state
