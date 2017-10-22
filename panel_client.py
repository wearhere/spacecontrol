#!/usr/bin/env python2.7
"""
Acts as a client to a central control server
"""

from cobs import cobs
import json
import socket

DEFAULT_PORT = 8000

class Client:
  """Handles communication with the server and polling state updates."""

  def __init__(self):
    """initialize comms"""
    self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.read_buffer = []

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

    self._socket.sendall(msg + '\x00')

  def read(self):
    """returns a message from server, or None"""
    while True:
      new_data = self._socket.recv(4096)

      # stop trying to read if we're not getting anything
      if len(new_data) == 0:
        return None

      # save what we just got
      self.read_buffer.append(new_data)

      # do we have a full command? lets return it
      if '\x00' in new_data:
        all_read = ''.join(self.read_buffer)
        msg, remainder = all_read.split('\x00')
        self.read_buffer = [remainder]

        return decode(msg)

    def encode(self, msg):
      """encodes a message to send to the server"""
      return cobs.encode(json.dumps(msg))

    def decode(self, msg):
      """parses a message read from the socket"""
      return json.loads(cobs.decode(msg))
