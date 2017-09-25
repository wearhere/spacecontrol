import json
import os
import socket

# As controls connect/disconnect, add and remove from this list, then call `announce` again.
controls = [
  { 'id': 0, 'type': 'button', 'state': 0, 'action': 'Defenestrate', 'item': 'aristocracy' }
]

sock = socket.socket()
sock.connect(('localhost', os.getenv('CONTROLLER_PORT', 8000)))

def send(message, data):
  sock.sendall(json.dumps({ "message": message, "data": data }) + '\r')

# TODO: Make this repeatable so that we can receive additional messages even if we read past a single
# message (currently we drop `following_text`), and non-blocking so that it can be interspersed with
# messages from the controls and consequent announcements to the main controller. Not sure how to do
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

event = receive()
if event['message'] == 'display':
  print event['data']['display']

# Since there's only a single command at present, and that command is a button i.e. just needs its
# state to be set to 1, this is guaranteed to satisfy the controller and cause the game to progress.
send('set-state', { 'id': 0, 'state': 1 })

# `sock` will automatically close here.
