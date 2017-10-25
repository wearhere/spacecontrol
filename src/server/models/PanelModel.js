const Backbone = require('backbone');
const ControlCollection = require('./ControlCollection');

const PanelModel = Backbone.Model.extend({
  defaults: {
    display: null,
    command: null
  },

  initialize(attrs, { connection }) {
    this.controls = new ControlCollection();

    this._setUpConnection(connection);

    this.on('change:display', (_, display) => {
      this._send('display', { display });
    });

    this.on('change:command', (_, command) => {
      const previousCommand = this.previous('command');
      if (previousCommand) this.stopListening(previousCommand);
      if (command) {
        this.set('display', command.get('action'));
        this.listenToOnce(command, 'change:completed', () => {
          this.set('display', 'Nice job!');
        });
      }
    });
  },

  _setUpConnection(connection) {
    connection.setEncoding('utf8');

    // It's not guaranteed that we'll receive the Python `sendall`, i.e. a
    // single JSON-encoded message. we need to expect we might receive more or
    // less data than that and so buffer the data. we expect the first 4 bytes
    // of data to include the amount of data which will be recieved
    let buffer = Buffer.alloc(0);

    connection.on('data', (chunk) => {
      buffer = Buffer.concat([buffer, Buffer.from(chunk)]);

      // Parse the data in a loop in case we got multiple messages at once.
      // We need at least 4 bytes for a message.
      while (buffer.length >= 4) {
        const msgLength = buffer.readUInt32BE();
        const msgEnd = 4 + msgLength;

        // not enough data for a complete message
        if (buffer.length < msgEnd) break;

        // extract a message from the buffer
        const msg = buffer.slice(4, msgEnd);
        buffer = buffer.slice(msgEnd);

        // parse the message json
        let event;
        try {
          event = JSON.parse(msg);
        } catch (e) {
          console.error(`Invalid panel message received: ${chunk}: ${e}`);
          continue;
        }

        // act on the message
        const { message, data } = event;
        switch (message) {
          case 'announce': {
            const { controls } = data;
            this.controls.reset(controls, {
              silent: false, // Ensure an 'update' event is fired.
              parse: true
            });
            break;
          }
          case 'set-state': {
            const { id, state } = data;
            const control = this.controls.get(id);
            if (!control) {
              // TODO(jeff): The panels should probably also have IDs to make best sense of this.
              console.error('Received state change event for unknown control:', id);
              return;
            }
            control.set('state', state);
            break;
          }
        }
      }
    });

    connection.on('error', (err) => {
      if (err.code === 'ECONNRESET') {
        // This happens when the connection closes before the other end has read everything that
        // we've written to it. We assume that the panel connection could drop at any time so don't
        // bother logging this.
      } else {
        console.error('Panel connection errored:', err);
      }
    });

    connection.on('close', () => {
      this.trigger('destroy', this, this.collection);
      this._connection = null;
    });

    this._connection = connection;
  },

  _send(message, data) {
    if (!this._connection) return; // Connection might have closed.
    const str = JSON.stringify({ message, data });

    const buffer = Buffer.alloc(4 + str.length);
    buffer.writeUInt32BE(str.length, 0);
    buffer.write(str, 4);

    this._connection.write(buffer);
  }
});

module.exports = PanelModel;
