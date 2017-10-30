const EventEmitter = require('events');
const { Socket } = require('net');

class MessageClient extends EventEmitter {
  static encode(message) {
    const messageStr = JSON.stringify(message);

    const buffer = Buffer.alloc(
      4 /* length of message (unsigned int) */ +
      // TODO(jeff): Support Unicode: https://github.com/wearhere/spacecontrol/issues/27
      messageStr.length
    );
    buffer.writeUInt32BE(messageStr.length);
    buffer.write(messageStr, 4);

    return buffer;
  }

  constructor({ socket, host, port }) {
    super();

    if (socket) {
      this._socket = socket;
    } else {
      this._socket = new Socket();
      this._socket.connect(port, host);
    }

    this._buffer = Buffer.alloc(0);
    this._socket
      .on('data', this._onData.bind(this))
      .on('error', this._onError.bind(this))
      .on('close', this._onClose.bind(this));
  }

  send(message, data) {
    if (!this._socket) throw new Error('Connection has closed');

    const encodedMessage = MessageClient.encode({ message, data });
    this._socket.write(encodedMessage);
  }

  _onData(data) {
    this._buffer = Buffer.concat([this._buffer, data]);

    // Parse the data in a loop in case we got multiple messages at once.
    // We need at least 4 bytes for a message.
    while (this._buffer.length >= 4) {
      const msgLength = this._buffer.readUInt32BE();
      const msgEnd = 4 + msgLength;

      // Not enough data for a complete message.
      if (this._buffer.length < msgEnd) break;

      const msg = this._buffer.slice(4, msgEnd).toString();
      this._buffer = this._buffer.slice(msgEnd);

      let decodedMsg;
      try {
        decodedMsg = JSON.parse(msg);
      } catch (e) {
        console.error(`Invalid server message received: ${data}: ${e}`);
      }

      // This isn't in the `try` block since we don't want to catch errors in the event handlers.
      if (decodedMsg) this.emit('message', decodedMsg);
    }
  }

  _onError(error) {
    if (error.code === 'ECONNRESET') {
      // This happens when the connection closes before the other end has read everything that
      // we've written to it. We assume that the other end could drop at any time so don't
      // bother logging this.
    } else {
      this.emit('error', error);
    }
  }

  _onClose() {
    this._socket = null;
    this.emit('close');
  }
}

module.exports = MessageClient;
