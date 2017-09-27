import locale
import json
import os
import socket

# As controls connect/disconnect, add and remove from this list, then call `announce` again.
controls = [{
  # Anything descriptive and unique.
  'id': 'foo',

  # One of 'button', TBD.
  'type': 'button',

  # Anything JSON-serializable and descriptive when displayed to the player, see `possibleStates`
  # and `action`.
  'state': 0,

  # This is `[0, 1]` since a button can just be pressed or not. We might also do `['off', 'on']`
  # or, for a multi-valued control like a dial or slider, `[0, 1, 2, 3]` or `['red',
  # 'green', 'yellow'].
  #
  # If this control has *persistent state* or *greater than 2 states* i.e. is
  # a switch or dial or slider where the player needs to put the control into that state and then
  # explicitly put it into a different state (without it automatically resetting), you should tell
  # the player which state to put it into by interpolating it into `action` as described below.
  #
  # If these states will be interpolated into `action`, they should be intelligible, i.e. if your
  # switch has labels like "foo", "bar", "baz", those should be the values of `possibleStates` not
  # `[0, 1, 2]` since the player won't know how those map onto the physical control.
  'possibleStates': [0, 1],

  # The thing that the player might do with the control when the game selects it.
  #
  # If `action` contains `%s` then the game will tell the player to manipulate this control by
  # interpolating one of `possibleStates` into `action` at that position.
  'action': 'Defenestrate the aristocracy!'
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

  try:
    # HACK(jeff): Support numeric states by trying to parse as an int.
    # ???(jeff): Is this the simplest way of parsing an int in Python?
    state = locale.atoi(state)
  except Exception:
    # Guess it was a string.
    pass

  send('set-state', { 'id': control_id, 'state': state })

  # HACK(jeff): We need to explicitly reset buttons' state while playing from the CLI, whereas a
  # physical button's state would automatically reset when the player lifted their finger off.
  control = filter(lambda c: c['id'] == control_id, controls)[0]
  if control['type'] == 'button':
    send('set-state', { 'id': control_id, 'state': 0 })

# `sock` will automatically close when the script finishes or is terminated.
