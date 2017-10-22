import locale
import json
import os
import socket

# A control is any object that the player can manipulate to put in one or more states. A control can
# be anything from a button to a switch to a dial to a pair of dolls that you touch against each
# other.
#
# It's ok to have multiple controls of the same form, i.e. multiple buttons, as long as they can
# be clearly identified. This may be a matter of just labeling them differently. See `actions` for
# tips on naming.
#
# This is a list of all controls monitored by this control panel. As controls
# connect/disconnect, add and remove from this list, then call `announce` again.
controls = [{
  # An identifier for the control. Must be globally unique. This shouldn't be that hard in practice
  # because players will need to uniquely identify this control among all controls. Just give it a
  # weird name.
  'id': 'defenestrator',

  # The current state of the control. This should always be a string even if the state is numeric
  # (this is because the keys of `actions` won't be able to be JSON-serialized if numeric).
  #
  # The values of this will depend on the control. For a button or a switch, `state` might be one
  # of `['0', '1']` or `['off', 'on']`. For a multi-valued control like a dial or slider, `state`
  # might be one of `['0', '1', '2', '3']` or `['red', 'green', 'yellow'].
  'state': '0',

  # Possible things that the player might do to or with the control. This is a map where the keys
  # are the possible values of `state` (see above), and the values are how the player puts the
  # control in that state ("actions").
  #
  # You'll notice that the value of '0' here is the empty string. This represents the player not
  # having to do anything to put the control in this state, as would be the case for a button-like
  # control, where if the player stops touching the control it will automatically return to this
  # state.
  #
  # The game may ask the player to perform any non-empty action. The action will be displayed to the
  # player, so make it clear and exciting. Actions should be globally unique, since players will be
  # shouting these across the room. It's possible to unique actions by being creative about what
  # the control is called and does (and labeling the physical control accordingly). For instance,
  # notice how the action here is to "defenestrates the aristocracy", not merely "push the button".
  # Another button might "launch the missiles". Two dials might respectively be labeled
  # "Froomulator" and "Hypervisor", with actions "Set Froomulator to 1" vs. "Set Hypervisor to 1".
  #
  # See the third control below for a shorthand way to define `actions` for dial-like controls.
  'actions': {
    '0': '',
    '1': 'Defenestrate the aristocracy!'
  },

    # HACK(jeff): `'type': 'button'` is only present to be able to play the game via the CLI, see
    # where this is read at the bottom of this script.
  'type': 'button',
}, {
  'id': 'octo',

  'state': 'nothing',

  'actions': {
    'nothing': '',
    'nipple': 'Octo bite raven girl nipple!',
    'mouth': 'Octo kiss raven girl mouth!'
  },

  'type': 'button'
}, {
  'id': 'Froomulator',

  'state': '0',

  # This is a shorthand form of `states`, where the first value (the array) contains the values for
  # `state`, and the second value (the string) is a "template action": the actual actions for each
  # state will be formed by replacing "%s" with the state.
  'actions': [
    ['0', '1', '2'],
    'Set Froomulator to %s!'
  ]
}]

sock = socket.socket()
sock.connect(('localhost', os.getenv('CONTROLLER_PORT', 8000)))

def send(message, data):
  sock.sendall(json.dumps({ "message": message, "data": data }) + '\r')

# TODO: Make this repeatable so that we can receive additional messages even if we read past a single
# message (currently we drop `following_text`), and non-blocking so that it can be interspersed with
# messages from the controls and consequent announcements to the controller. Not sure how to do
# those things!
def receive():
  buffer = ''
  while True:
    data = sock.recv(4096) # Arbitrary / maximum length.
    buffer += data
    raw_event, carriage_return, following_text = buffer.partition('\r')
    if raw_event:
      return json.loads(raw_event)

def announce():
  send("announce", { "controls": controls })

announce()

# Play the game.
while (True):
  event = receive()
  if event['message'] == 'display':
    display = event['data']['display']
    print display

    # HACK(jeff): This script shouldn't have to know what's displayed, this is just for purposes of
    # playing the game via the CLI.
    if display == 'Nice job!':
      continue

  control_id, space, state = raw_input('Set state: ').partition(' ')

  send('set-state', { 'id': control_id, 'state': state })

  # HACK(jeff): We need to explicitly reset buttons' state while playing from the CLI, whereas a
  # physical button's state would automatically reset when the player lifted their finger off.
  control = filter(lambda c: c['id'] == control_id, controls)[0]
  if ('type' in control) and (control['type'] == 'button'):
    send('set-state', { 'id': control_id, 'state': '0' })

# `sock` will automatically close when the script finishes or is terminated.
