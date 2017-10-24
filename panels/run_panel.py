#!/usr/bin/python
"""Run a panel!"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import keyboard_panel
from panel_client import PanelClient

PANELS = [keyboard_panel.KeyboardPanel]


def main():
  parser = argparse.ArgumentParser(
      'Launch the controller for a Space Team panel!')
  parser.add_argument(
      '--panel_type',
      default='KeyboardPanel',
      choices=[panel.__name__ for panel in PANELS])
  args = parser.parse_args()

  panel_class = [
      panel for panel in PANELS if panel.__name__ == args.panel_type
  ][0]

  client = PanelClient(panel_class)

  client.start()

if __name__ == '__main__':
  main()
