const _ = require('underscore');
const Backbone = require('backbone');
const ControlCollection = require('./ControlCollection');
const MessageClient = require('../utils/MessageClient');

const PanelModel = Backbone.Model.extend({
  defaults: {
    display: null,
    command: null
  },

  _statusTimeout: null,
  _keepAliveInterval: null,

  initialize(attrs, { connection }) {
    this.controls = new ControlCollection();

    this._setUpConnection(connection);

    this.on('change:display', (model, message='') => {
      this._send('set-display', { message });
    });

    this.on('change:status', (model, message = '') => {
      this._send('set-status', { message });
    });

    this.on('change:progress', (model, value = 0) => {
      this._send('set-progress', { value });
    });

    this.on('change:command', (model, command) => {
      const previousCommand = this.previous('command');
      if (previousCommand) this.stopListening(previousCommand);
      if (command) {
        this.set('display', command.get('action'));
      }
    });

    this.once('destroy', () => clearInterval(this._keepAliveInterval));
  },

  setStatus(status, timeout) {
    clearTimeout(this._statusTimeout);
    this.set({ status });
    if (_.isNumber(timeout)) {
      this._statusTimeout = setTimeout(() => {
        this.unset('status');
      }, timeout);
    }
  },

  clearStatusAndProgress() {
    clearTimeout(this._statusTimeout);
    this.unset('status');
    this.unset('progress');
  },

  _setUpConnection(connection) {
    this._client = new MessageClient({ socket: connection })
      .on('message', ({ message, data }) => {
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
      })
      .on('error', (err) => {
        console.error('Panel connection errored:', err);
      })
      .on('close', () => {
        this.trigger('destroy', this, this.collection);
        this._client = null;
      });
  },

  _send(message, data) {
    if (!this._client) return; // Connection has closed.

    this._client.send(message, data);
  }
});

module.exports = PanelModel;
