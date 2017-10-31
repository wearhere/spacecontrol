#!/usr/bin/env python2.7
"""
Contains and manages the current state of the game
"""

from peripherals_stacey import *
from controls import *

MERINGUE_INPUTS = {
    "rs_1": Slider(
      device=BLACKPILL,
      pin=0,
      num_bins=6,
      max_val=3950,
      ),
    "rs_2": Slider(
      device=BLACKPILL,
      pin=1,
      num_bins=9,
      max_val=3950,
      ),
    "slide_1": Slider(
      device=BLACKPILL,
      pin=2,
      num_bins=5,
      max_val=4095,
      ),
    "slide_2": Slider(
      device=BLACKPILL,
      pin=3,
      num_bins=7,
      max_val=4095,
      ),
    }

def generate(inputs=MERINGUE_INPUTS):
  state = {}
  for tag, control in inputs.items():
    control.read()
    state[tag] = control.value
  #print "state: ", state
  return state
