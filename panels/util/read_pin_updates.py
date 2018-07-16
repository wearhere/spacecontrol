from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
from RPi import GPIO
from Adafruit_GPIO import MCP230xx
GPIO.setmode(GPIO.BCM)

def parse_MCP_config_string(config_str):
  if not config_str:
    return []
  configs = config_str.split(';')
  configs = [c.split(',') for c in configs]
  return [MCPReader(config[0], config[1:]) for config in configs]

def test_parse_MCP_config_string(config_str):
  if not config_str:
    return []
  configs = config_str.split(';')
  configs = [c.split(',') for c in configs]
  return [(config[0], config[1:]) for config in configs]


class StateReader(object):
  def get_updates(self):
    old_state = {pin:val for pin, val in self.state.iteritems()}
    self.state = self.read_state()
    return {pin:val for pin, val in self.state.iteritems()
            if self.state[pin] != old_state[pin]}
    
  def read_state(self):
    raise NotImplementedError('must implement reader in subclass!')


class MCPReader(StateReader):
  def __init__(self, address, pins=None):
    if not pins:
        pins = range(16)
    self._pins = [int(pin) for pin in pins]
    self._address = int(address)+0x20
    self._mcp = MCP230xx.MCP23017(self._address)
    for pin in self._pins:
      self._mcp.setup(pin, GPIO.IN)
      self._mcp.pullup(pin, True)
    self.state = self.read_state()

  def read_state(self):
    return {'MCP {}.{}'.format(self._address, pin):self._mcp.input(pin) for pin in self._pins}


class GPIOReader(StateReader):
  def __init__(self, pins):
    self._pins = [int(pin) for pin in pins]
    for pin in self._pins:
      GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    self.state = self.read_state()

  def read_state(self):
    return {'GPIO {}'.format(pin):GPIO.input(pin) for pin in self._pins}


def main():
  parser = argparse.ArgumentParser(
      'Print when a pin updates state')
  parser.add_argument(
      '--gpio_pins',
      default='',
      type=str)
  parser.add_argument(
      '--mcp_configs',
      default='',
      type=str,
      help='address1,pin,pin,pin,pin;addres2,pin,pin,pin'
  )  
  args = parser.parse_args()

  mcps = parse_MCP_config_string(args.mcp_configs)
  readers = mcps

  if args.gpio_pins:
    gpio = GPIOReader(args.gpio_pins.split(','))
    readers = [gpio] + readers

  while True:
    for reader in readers:
      for name, value in reader.get_updates().iteritems():
        print('"{}" is now {}'.format(name, value))


if __name__ == '__main__':
  main()

