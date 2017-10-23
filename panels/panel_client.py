from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import locale
import json
import multiprocessing
from Queue import Empty as EmptyQueueException
import os
import socket
import sys
import time

# Polling interval of the IO process
MIN_LATENCY_MS = 10


class PanelStateBase:

  def get_state_updates(self):
    """Must implement this function for your panel.

    Should return an iterable of key, value pairs for anything that has changed
    since the last call, or of the complete state.
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


def _make_update_message(update):
  return {'message': 'set-state', 'data': {'id': update[0], 'state': update[1]}}

def _make_announce_message(controls):
  return {'message': 'announce', 'data': controls}


def _panel_io_subprocess_main(panel_state_class, action_queue, message_queue):
  panel_state = panel_state_class()
  action_queue.put(_make_announce_message(panel_state.get_controls()))

  while True:
    for update in panel_state.get_state_updates():
      if update is None:
        # received shutdown signal
        break
      action_queue.put(_make_update_message(update))
    try:
      panel_state.display_message(message_queue.get())
    except EmptyQueueException:
      pass
    time.sleep(MIN_LATENCY_MS / 1000)


def _server_io_subprocess_main(action_queue, message_queue, socket=socket):
  messenger = SpaceTeamMessenger(socket)
  while True:
    try:
      action = action_queue.get()
      if action is None:
        # received shutdown signal
        break
      messenger.send(action)
    except EmptyQueueException:
      pass
    for message in messenger.get_messages():
      if message['message'] == 'display':
        message_queue.put(message['data']['display'])
    time.sleep(MIN_LATENCY_MS / 1000)


class PanelClient:
  """Handles communication with the server and polling state updates."""

  def __init__(self, PanelStateClass):
    self._action_queue = multiprocessing.Queue()
    self._message_queue = multiprocessing.Queue()
    self._panel_state_class = PanelStateClass

  def start(self):
    """Start I/O subprocess and begin communicating with server."""
    self._panel_io_subprocess = multiprocessing.Process(
        target=_panel_io_subprocess_main,
        args=(seld._panel_state_class, self._action_queue, self._message_queue))
    self._panel_io_subprocess.start()

    self._server_io_subprocess = multiprocessing.Process(
        target=_server_io_subprocess_main,
        args=(self._action_queue, self._message_queue))
    self._server_io_subprocess.start()

  def stop(self):
    self._action_queue.put(None)
    self._message_queue.put(None)


class SpaceTeamMessenger:
  """Handles reading and deserializing messages from the server"""

  def __init___(self, socket):
    # Connect to controller and appraise it of our controls.
    # Make the connection non-blocking _after_ connecting to avoid this nonsense:
    # https://stackoverflow.com/a/6206705/495611
    self._socket = socket.socket()
    self._socket.connect(('localhost', os.getenv('CONTROLLER_PORT', 8000)))
    self._socket.setblocking(0)
    self._msg_buffer = ''

  def get_messages(self):
    """Yields all available messages."""
    try:
      self._msg_buffer += self._socket.recv(4096)
      while msg_buffer:
        msg, delimiter, self._msg_buffer = self._msg_buffer.partition('\r')
        if not delimiter:
          # message is incomplete
          self._msg_buffer = msg
          break
        try:
          yield json.loads(msg)
        except ValueError:
          # malformed message
          continue
    except socket.error:
      return []

  def send(self, message):
    self.socket.sendall(json.dumps(message))
