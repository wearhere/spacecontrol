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
        this.listenTo(command, 'change:completed', () => {
          this.set('display', 'Nice job!');
        });
      }
    });
  },

  _setUpConnection(connection) {
    connection.setEncoding('utf8');

    // HACK(jeff): Here we're assuming that we'll receive the Python `sendall`, i.e. a single
    // JSON-encoded, carriage-return-delimited blob, in exactly one chunk. Not sure if that's
    // guaranteed.
    connection.on('data', (chunk) => {
      let event;
      try {
        event = JSON.parse(chunk);
      } catch (e) {
        console.error(`Invalid panel message received: ${chunk}`);
        return;
      }

      const { message, data } = event;
      switch (message) {
        case 'announce': {
          const { controls } = data;
          this.controls.reset(controls, {
            silent: false // Ensure an 'update' event is fired.
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

    this._connection.write(JSON.stringify({ message, data }) + '\r');
  }
});

module.exports = PanelModel;
