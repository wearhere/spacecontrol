"""Doll Panel."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from collections import namedtuple

class Control(object):
  def __init__(self, ID, actions, read):
    self.ID = ID
    self.actions={str(state):cmd for state, cmd in actions.iteritems()}
    self.read=read

  def get_control_info(self):
    return {
        'id': self.ID,
        'state': str(self.read()),
        'actions': self.actions
        }

def button_reader(pin, interface, quiescent):
  def read():
    return int(interface(pin) != quiescent)
  return read

def toggle_reader(pin, interface):
  def read():
    return int(interface(pin))
  return read

class SpaceTeamControls(object):
  def __init__(self):
    self.controls = {}

  def get_controls_data(self):
    """Gets controls as formatted by the spaceteam controller."""
    return [control.get_control_info() for control in self.controls.values()]

  def read_state(self):
    """Returns a complete mapping of control, state pairs."""
    return {ID:control.read() for ID, control in self.controls.iteritems()}


  def make_button_array(self, name, pin_interface, pin_list, button_text=None,
                        quiescent_state=1):
    """Creates an array of buttons all attached to the same device.

    Args:
      name: formattable string, e.g. "Button {}"
      pin_interface: Calling pin_interface(pin) should return current pin state.
      pin_list: Ordered list that maps buttons to pins. b0 maps to pin_list[0].
      button_text: Displayed to the user when the button should be pressed.
      quiescent_state: value the button returns when unpressed.
    """
    if not button_text:
      button_text = 'Press {}!'.format(name)
    for button, pin in enumerate(pin_list):
      button = button+1
      ID = name.format(button)
      actions = {'0':'', '1':button_text.format(button)}
      self.controls[ID] = Control(ID, actions,
                                  button_reader(pin, pin_interface, quiescent_state))

  def make_toggle_array(self, name, pin_interface, pin_list, toggle_text=None,
                        toggle_texts=None):
    """Creates an array of toggles all attached to the same device.

    Args:
      name: formattable string, e.g. "toggle %s"
      pin_interface: Calling pin_interface(pin) should return current pin state.
      pin_list: Ordered list that maps buttons to pins. b0 maps to pin_list[0].
      toggle_text: Displayed to the user when the toggle should be changed.
                   Should be formatable with toggle number, value
      toggle_texts: Separate toggle texts for 0 and 1 states.
    """
    if toggle_text:
      if toggle_texts:
        raise ValueError('Can only specify one of toggle_text and toggle_texts')
      toggle_texts = [toggle_text, toggle_text]
    if not toggle_text and not toggle_texts:
      toggle_text = 'Set {}!'.format(name) + 'to {}'
    for toggle, pin in enumerate(pin_list):
      toggle = toggle + 1
      ID = name.format(toggle)
      actions = {str(val):toggle_text.format(toggle, val)
                 for val, toggle_text in enumerate(toggle_texts)}
      self.controls[ID] = Control(ID, actions, toggle_reader(pin, pin_interface))

  def make_toggle(self, name, reader, toggle_text=None, toggle_texts=None):
    """Creates a toggle control

    Args:
      name: name of the toggle, e.g. "Enfrapulator." Must be unique.
      pin_interface: Calling pin_interface(pin) should return current pin state.
      pin_list: Ordered list that maps buttons to pins. b0 maps to pin_list[0].
      toggle_text: Displayed to the user when the toggle should be changed.
                   Should be formatable with toggle number, value
      toggle_texts: Separate toggle texts for 0 and 1 states.
    """
    if toggle_text:
      if toggle_texts:
        raise ValueError('Can only specify one of toggle_text and toggle_texts')
      toggle_texts = [toggle_text, toggle_text]
    if not toggle_text and not toggle_texts:
      toggle_text = 'Set {}!'.format(name) + 'to {}'
    actions = {'0': toggle_texts[0], '1': toggle_texts[1]}
    self.controls[name] = Control(name, actions, lambda: reader())
