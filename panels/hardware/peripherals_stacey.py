#!/usr/bin/env python2.7
""" Initializes and gives access to peripherals """

from blackpill import Blackpill
BLACKPILL = Blackpill('/dev/ttyAMA0')

ALL = [
  BLACKPILL,
]

def reset_all():
  for p in ALL:
    p.reset()
