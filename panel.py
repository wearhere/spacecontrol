import locale
import json
import os
import socket
import sys
import threading
import time

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

# HACK(jeff): Multiple panels can't have the same controls. So when playing via the CLI, we divvy
# up the controls between players.
if len(sys.argv) < 2:
  print 'Enter player number (1 or 2).'
  exit(1)

player_number = int(sys.argv[1])
if player_number is 1:
  controls = controls[:2]
elif player_number is 2:
  controls = controls[2:]
else:
  # To add more players, just add some more controls to the list above so that we have more to divvy up.
  print 'Game only supports two players atm.'
  exit(1)

print 'Your controls are: ', json.dumps(controls, indent=2)


# Connect to controller and apprise it of our controls.
# Make the connection non-blocking _after_ connecting to avoid this nonsense:
# https://stackoverflow.com/a/6206705/495611
sock = socket.socket()
sock.connect(('localhost', os.getenv('CONTROLLER_PORT', 8000)))
sock.setblocking(0)

def send(message, data):
  sock.sendall(json.dumps({ "message": message, "data": data }) + '\r')

def announce():
  send("announce", { "controls": controls })

announce()


# Handle events from controls and the controller.

# Mimic controls changing by the player entering keyboard input.
# Use a thread to allow blocking reads thereof.

control_queue = []
def readKeyboard():
  while (True):
    control_id, space, state = raw_input().partition(' ')
    if control_id and state:
      control_queue.append((control_id, state))
threading.Thread(target=readKeyboard).start()

def receiveControl():
  try:
    state_change = control_queue.pop(0) # Pops from start of list.
  except:
    # Ignore the queue being empty.
    return False

  control_id, state = state_change

  try:
    control = filter(lambda c: c['id'] == control_id, controls)[0]
  except:
    # The player entered invalid input like trying to manipulate a control that wasn't on their board.
    return False

  send('set-state', { 'id': control_id, 'state': state })

  # HACK(jeff): We need to explicitly reset buttons' state while playing from the CLI, whereas a
  # physical button's state would automatically reset when the player lifted their finger off.
  if ('type' in control) and (control['type'] == 'button'):
    send('set-state', { 'id': control_id, 'state': '0' })

  return True

buffer = ''
def receiveController():
  global buffer

  while True:
    try:
      data = sock.recv(4096) # Arbitrary / maximum length.
    except:
      # If the buffer is empty, we return as not having handled an event.
      # Otherwise we wait for the rest of the data corresponding to this event.
      if not buffer:
        return False
      else:
        continue

    buffer += data

    # Note that we may receive multiple events at once.
    while buffer:
      raw_event, carriage_return, following_text = buffer.partition('\r')
      try:
        event = json.loads(raw_event)
      except:
        # We didn't receive a complet message.
        buffer = raw_event
        break

      if event['message'] == 'display':
        display = event['data']['display']
        print '> ' + display

      # Resume processing the text after the message--possibly another event.
      buffer = following_text

  return True


# Play the game.
try:
  while (True):
    for receiver in [receiveControl, receiveController]:
      if receiver():
        continue

    # Wait for an event to occur.
    time.sleep(0.1)
except KeyboardInterrupt:
  # Kill all threads: https://stackoverflow.com/a/1635089/495611
  os._exit(0)

# `sock` will automatically close when the script finishes or is terminated.
