#!/usr/bin/python
"""Read state from the port expander and report changes."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse

from Adafruit.Adafruit_MCP230xx import MCP230XX_GPIO


def main():
  parser = argparse.ArgumentParser(
      'Launch MCP230xx debugger')
  parser.add_argument(
      '--num_ports',
      default=16,
      choices=[8, 16],
      type=int)
  parser.add_argument(
      '--address',
      default=0,
      choices=list(range(8)),
      type=int)
  args = parser.parse_args()

  mcp = MCP230XX_GPIO(args.address, args.num_ports)
  for port in range(args.num_ports):
    mcp.config(pin, mcp.INPUT)
    mcp.pullup(pin, True)

  def read():
    return {port:mcp.input(port) for port in range(args.num_ports)}

  state = read()

  while True:
    new_state = read()
    diff = {port:state for port in new_state
            if new_state[port] != state[port]}
    if not diff:
      continue

    print('*'*20+ 'State update!' + '*'*20)
    for port, state in new_state.iteritems():
      print('Port {}: {}'.format(port, state))
      print('\n')
    state = new_state

if __name__ == '__main__':
  main()
