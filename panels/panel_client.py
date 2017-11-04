from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import locale
import json
import multiprocessing
from Queue import Empty as EmptyQueueException
import os
import socket
import struct
import sys
import time

# Time to wait for panel IO to start
PANEL_IO_START_SECONDS = 2

# Polling interval of the IO process
MIN_LATENCY_MS = 10

#CONTROLLER_IP = "192.168.1.254"
LCD_WIDTH = 20 # Characters.

class PanelStateBase:

  def diff_states(self, old_state, new_state):
    return {
        k:v for k, v in new_state.iteritems()
        if (k not in old_state) or (v != old_state[k])
    }

  def get_state_updates(self):
    """Must implement this function for your panel.

    Should return an iterable of control_id, state pairs for anything that has
    changed since the last call.

    Alternatively, if you would like to manually handle messages, you can
    implement panel_main(action_queue, message_queue)
    """
    raise NotImplementedError()

  def get_controls(self):
    """Must implement this function for your panel.

    Should return the available controls.
    """
    raise NotImplementedError()

  def display_message(self, message):
    """Must implement this function for your panel.

    Display a message from the server for the user."""
    raise NotImplementedError()

  def display_status(self, message):
    """Must implement this function for your panel.

    Display a status message from the server for the user."""
    raise NotImplementedError()

  def display_progress(self, value):
    """Must implement this function for your panel.

    Display a progress bar."""
    raise NotImplementedError()

def _validate_controls(controls):
  assert isinstance(controls, list), 'Controls is not a list'

  for control in controls:
    try:
      for attr in ['id', 'state', 'actions']:
        assert attr in control, '`{}` is missing'.format(attr)

      assert isinstance(control['id'], str), '`id` is not a string'

      assert isinstance(control['state'], str), '`state` is not a string'

      if isinstance(control['actions'], dict):
        states = control['actions'].keys()
        assert all([isinstance(state, str) for state in states]), 'State in `actions` is not a string'

        actions = control['actions'].values()
        for action in actions:
          assert isinstance(action, str), 'Values of `actions` must be strings'
          assert '%s' not in action, 'Format strings are only supported in the shorthand form of `actions`'

        assert control['state'] in states, '`state` not present in `actions`'

      elif isinstance(control['actions'], list):
        assert len(control['actions']) == 2, 'Shorthand `actions` is malformed'

        states = control['actions'][0]
        assert isinstance(states, list), 'Shorthand `actions` is malformed'
        assert all([isinstance(state, str) for state in states]), 'State in `actions` is not a string'

        action = control['actions'][1]
        assert isinstance(action, str) and '%s' in action, 'Shorthand `actions` is malformed'

        assert control['state'] in states, '`state` not present in `actions`'

      else:
        raise TypeError('`actions` is malformed')

    except Exception as e:
      raise TypeError('{} failed validation: {}'.format(control, e))

  assert len(set([control['id'] for control in controls])) == len(controls), 'Control ids are not unique'


def _make_update_message(update):
  return {'message': 'set-state', 'data': {'id': str(update[0]), 'state': str(update[1])}}


def _make_announce_message(controls):
  return {'message': 'announce', 'data': {'controls':controls}}


def _panel_io_subprocess_main(panel_state_factory, action_queue, message_queue, panel_io_started):
  panel_state = panel_state_factory()
  controls = panel_state.get_controls()

  try:
    _validate_controls(controls)
  except Exception as e:
    print(e)
    return

  action_queue.put(_make_announce_message(controls))
  panel_io_started.set()

  try:
    if getattr(panel_state, 'panel_main', False):
      panel_state.panel_main(action_queue, message_queue)
      return

    while True:
      # TODO: add support for the panel to update available controls
      for update in panel_state.get_state_updates():
        if update is None:
          # received shutdown signal
          return
        action_queue.put(_make_update_message(update))
      try:
        message = message_queue.get(block=False)
        if message['message'] == 'set-display':
          panel_state.display_message(message['data']['message'])
        elif message['message'] == 'set-status':
          panel_state.display_status(message['data']['message'])
        elif message['message'] == 'set-progress':
          panel_state.display_progress(message['data']['value'])
      except EmptyQueueException:
        pass
      time.sleep(MIN_LATENCY_MS / 1000)
  except KeyboardInterrupt:
    # Ignore keyboard interrupts since `run_panel` will register a handler and stop the client.
    pass


def _server_io_subprocess_main(
    action_queue,
    message_queue,
    messenger_factory=lambda: SpaceTeamMessenger(socket.socket)):
  messenger = messenger_factory()

  try:
    while True:
      try:
        action = action_queue.get(block=False)
        if action is None:
          # received shutdown signal
          return
        messenger.send(action)
      except EmptyQueueException:
        pass
      for message in messenger.get_messages():
        message_queue.put(message)
      #time.sleep(MIN_LATENCY_MS / 1000)
  except KeyboardInterrupt:
    # Ignore keyboard interrupts since `run_panel` will register a handler and stop the client.
    pass


class PanelClient:
  """Handles communication with the server and polling state updates."""

  def __init__(self, panel_state_factory):
    self._action_queue = multiprocessing.Queue()
    self._message_queue = multiprocessing.Queue()
    self._panel_io_started = multiprocessing.Event()
    self._panel_state_factory = panel_state_factory

  def start(self):
    """Start I/O subprocess and begin communicating with server."""
    self._panel_io_subprocess = multiprocessing.Process(
        target=_panel_io_subprocess_main,
        args=(self._panel_state_factory, self._action_queue, self._message_queue,
              self._panel_io_started))
    self._panel_io_subprocess.start()

    # Wait for panel IO to start.
    panel_io_start_time = time.time()
    while not self._panel_io_started.is_set():
      if not self._panel_io_subprocess.is_alive() or \
        (time.time() - panel_io_start_time) > PANEL_IO_START_SECONDS:
        print('Could not start panel IO; aborting.')
        sys.exit(1)
        return # For the purposes of unit tests.
      time.sleep(0.025)

    self._server_io_subprocess = multiprocessing.Process(
        target=_server_io_subprocess_main,
        args=(self._action_queue, self._message_queue))
    self._server_io_subprocess.start()

  def stop(self):
    self._action_queue.put(None)
    self._message_queue.put(None)

    self._panel_io_subprocess.join()
    self._server_io_subprocess.join()


class SpaceTeamMessenger:
  """Handles reading and deserializing messages from the server"""

  def __init__(self, socket_class,
               controller_port=80):
    # Connect to controller and appraise it of our controls.
    # Make the connection non-blocking _after_ connecting to avoid this nonsense:
    # https://stackoverflow.com/a/6206705/495611
    self._socket = socket_class(socket.AF_INET, socket.SOCK_STREAM)
    self._socket.connect((
      os.getenv('CONTROLLER_IP', 'localhost'),
      os.getenv('CONTROLLER_PORT', 8000)
    ))
    self._socket.setblocking(0)
    self._msg_buffer = ''

  def peek_buffer(self):
    return self._msg_buffer

  def get_messages(self):
    """Yields all available messages."""
    try:
      self._msg_buffer += self._socket.recv(4096)
      while len(self._msg_buffer) >= 4:
        message = self._pop_from_buffer()
        if message:
          yield message
        else:
          return

    except socket.error:
      return

  def _pop_from_buffer(self):
    msg_length = struct.unpack('>I', self._msg_buffer[:4])[0]
    if len(self._msg_buffer) < (4 + msg_length):
      return None

    # okay, we have a complete message! lets return it!
    msg_ends_at = 4 + msg_length
    msg = self._msg_buffer[4:msg_ends_at]
    self._msg_buffer = self._msg_buffer[msg_ends_at:]

    return json.loads(msg)

  def send(self, message):
    self._socket.sendall(_encode(message))

def _encode(message):
  jstr = json.dumps(message)
  return struct.pack('>I%ds' % len(jstr), len(jstr), jstr)
