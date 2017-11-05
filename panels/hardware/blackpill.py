"""Handles a Black Pill Microcontroller"""
import serial
import time

class Blackpill(object):
  def __init__(self, port, num_pins=11):
    # may need this later? 
    self.samples_per_second = 100
    self.num_pins = num_pins
    self.port = port
 
    # store I/O config
    self.pins_enabled = [False] * num_pins
    self.pin_values = [None] * num_pins

    # (re)enable pins and (re)connect via serial
    self.reset()
  
  def stop(self):
    self.serial.close()

  def read_inputs(self):
    """reads all enabled pins and stores the values locally"""
    pin_state = self.serial.readline()
    if not pin_state:
      print "cannot read yet"
      return
    pin_vals = pin_state.split(",")
    for pin_id, pin_val in enumerate(pin_vals):
      control_id, val = pin_val.split(":")
      self.pin_values[pin_id] = float(val)
      # TODO: do we need this??
      # give the device time to read the given input
      #time.sleep(1.0 / self.samples_per_second)

  def read(self, pin):
    """ Update all pin values, return just the relevant one """
    # TODO is this a shameless hack? we may want to thread this
    self.read_inputs()
    value = self.pin_values[pin]

    # something went wrong!
    #if value is None:
    #  if self.pins_enabled[pin]:
    #    raise RuntimeError(
    #        "Tried to read pin %s, but it's state is not available!" % pin)
    #  else:
    #    raise RuntimeError(
    #        "Tried to read pin %s, but that pin is not enabled for reading!" % pin)
    #else:
    return value

  def enable_pin(self, pin):
    """enables reading a given pin whenever we read all the inputs"""
    if pin < 0 or pin > self.num_pins - 1:
      raise RuntimeError("Input pin must be between 0 and %s, not %s" % self.num_pins -1, pin)

    self.pins_enabled[pin] = True

  def reset(self):
    """Connect via Serial, enable all pins"""
    for i in range(self.num_pins):
      self.enable_pin(i)
    # Serial comms from Dawn
    # TODO: correct port??
    self.serial = serial.Serial(
      port=self.port, # '/dev/ttyACM0',
      baudrate = 9600,
      parity=serial.PARITY_NONE,
      stopbits=serial.STOPBITS_ONE,
      bytesize=serial.EIGHTBITS,
      timeout=1
    )
    if not self.serial.isOpen():
      raise ValueError("Couldn't open %s" % port)
      
 
