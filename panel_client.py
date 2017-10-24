#!/usr/bin/env python2.7
"""
Acts as a client to a central control server
"""

import json
import socket
import struct

DEFAULT_PORT = 8000

class Client:
  """Handles communication with the server and polling state updates."""

  def __init__(self):
    """initialize comms"""
    self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.read_buffer = ""

  def connect(self, host, port = DEFAULT_PORT):
    self._socket.connect((host, port))
    self._socket.setblocking(0)

  def stop(self):
    self._socket.close()

  def send(self, message, data):
    """encodes and sends a message to the server"""
    msg = self.encode({
      'message': message,
      'data': data,
      })
    self._socket.sendall(msg)

  def read(self):
    """returns a message from server, or None"""
    no_data = False
    while True:
      try:
        self.read_buffer += self._socket.recv(4096)
      except socket.error:
        no_data = True

      msg = self.pop_from_buffer()
      if msg:
        return msg
      elif no_data:
        break

  def encode(self, msg):
    """encodes a message to send to the server"""
    jstr = json.dumps(msg)
    return struct.pack('>I%ds' % len(jstr), len(jstr), jstr)

  def pop_from_buffer(self):
    """parses a message read from the buffer"""
    # do we even know the length of the next message?
    if len(self.read_buffer) < 4:
      return None

    # have we received the entire next message?
    msg_length = struct.unpack('>I', self.read_buffer[:4])[0]
    if len(self.read_buffer) < (4 + msg_length):
      return None

    # okay, we have a complete message! lets return it!
    msg_ends_at = 4 + msg_length
    msg = self.read_buffer[4:msg_ends_at]
    self.read_buffer = self.read_buffer[msg_ends_at:]

    return json.loads(msg)
