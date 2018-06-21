#!/usr/bin/python
"""Run a panel!"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import doll_panel
import keyboard_panel

from panel_client import PanelClient as PanelClientAsync
from panel_client_synchronous import PanelClient

import os
import signal
import sys


PANELS = [doll_panel.DollPanel, keyboard_panel.KeyboardPanel]

def main():
  parser = argparse.ArgumentParser(
      'Launch the controller for a Space Team panel!')
  parser.add_argument(
      '--panel_type',
      default='KeyboardPanel',
      choices=[panel.__name__ for panel in PANELS])
  parser.add_argument(
      '--player_number',
      default='1',
      choices=[1, 2],
      type=int)
  parser.add_argument(
      '--run_synchronous',
      default=True,
      type=bool)
  args = parser.parse_args()

  panel_class = [
      panel for panel in PANELS if panel.__name__ == args.panel_type
  ][0]

  if panel_class.__name__ == "KeyboardPanel":
    new_stdin = os.fdopen(os.dup(sys.stdin.fileno()))
    panel_class = lambda: keyboard_panel.KeyboardPanel(new_stdin, args.player_number)

  if args.run_synchronous:
    client = PanelClient(panel_class)
    client.start()
    print("Client exited normally")
    return

  else:
    client = PanelClientAsync(panel_class)
    client.start()

    def signal_handler(signal, frame):
      client.stop()
      sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
  main()
