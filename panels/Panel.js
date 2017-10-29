const { Component } = require('ink');
const MessageClient = require('../src/server/utils/MessageClient');

class Panel extends Component {
  componentDidMount() {
    const host = process.env.CONTROLLER_IP || 'localhost';
    const port = parseInt(process.env.CONTROLLER_PORT || '8000', 10);

    this._client = new MessageClient({ host, port })
      .on('message', ({ message, data }) =>{
        switch (message) {
          case 'set-display':
            this.display = data.message;
            break;
          case 'set-status':
            this.status = data.message;
            break;
        }
      })
      .on('error', (error) => {
        console.error('Error communicating with server:', error);
      })
      .on('close', () => {
        // TODO(jeff): Handle this.
      });

    this._client.send('announce', { controls: this.controls });
  }

  get controls() {
    throw new Error('Subclass must override');
  }

  set display(message) {
    throw new Error('Subclass must override');
  }

  set status(message) {
    throw new Error('Subclass must override');
  }

  setControlState(id, state) {
    this._client.send('set-state', { id, state });
  }
}

module.exports = Panel;
