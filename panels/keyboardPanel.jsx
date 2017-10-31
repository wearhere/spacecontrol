/** @jsx h */
const _ = require('underscore');
const { h, render, Text } = require('ink');
const TextInput = require('ink-text-input');
const ProgressBar = require('ink-progress-bar');
const Panel = require('./Panel');
const { LCD_WIDTH } = Panel;

const argv = require('yargs')
  .usage('Usage: $0 <options>')
  .options({
    playerNumber: {
      type: 'number',
      choices: [1, 2],
      required: true
    }
  })
  .alias('h', 'help')
  .argv;

const CONTROL_SCHEMES = [
  [{
    'id': 'defenestrator',
    'state': '0',
    'actions': {
      '0': '',
      '1': 'Defenestrate the aristocracy!'
    },
    'type': 'button',
  }, {
    'id': 'octo',
    'state': 'nothing',
    'actions': {
      'nothing': '',
      'nipple': 'Octo bite raven girl nipple!',
      'mouth': 'Octo kiss raven girl mouth!'
    },
    'type': 'button'
  }], [{
    'id': 'Froomulator',
    'state': '0',
    'actions': [['0', '1', '2'], 'Set Froomulator to %s!']
  }]
];

function Cursor() {
  return <Text dim>█</Text>;
}

class KeyboardPanel extends Panel {
  constructor() {
    super();

    this._controls = CONTROL_SCHEMES[argv.playerNumber - 1];

    this.state = {
      display: '',
      status: null,
      input: ''
    };
  }

  get controls() {
    return this._controls;
  }

  set display(message) {
    this.setState({ display: message });
  }

  set status(data) {
    this.setState({ status: data });
  }

  render(props, state) {
    let status;
    if (state.status) {
      const { message, progress } = state.status;
      if (message) {
        status = message;
      } else if (progress) {
        status = <ProgressBar columns={LCD_WIDTH} percent={progress} />;
      }
    }

    return (
      <div>
        <div>
          Your controls:<br/>
          {JSON.stringify(this.controls, null, 2)}
        </div>
        <br/>

        <div>
          <Text red>{state.display}</Text><br/>
          {status}
        </div>
        <br/>

        <div>
          <span>Set state: </span>

          <TextInput
            value={state.input}
            onChange={::this.handleChange}
            onSubmit={::this.handleSubmit}
          />
          {/* Put a cursor afterward since `TextInput` will not do this. */}
          <Cursor/>
        </div>
      </div>
    );
  }

  handleChange(value) {
    this.setState({ input: value });
  }

  handleSubmit(value) {
    this.setState({ input: '' });

    const [id, state] = value.split(' ');
    this.setControlState(id, state);

    // HACK(jeff): Simulator the behavior of a real button in that it would automatically depress.
    const control = _.findWhere(this.controls, { id });
    if (control && (control.type === 'button')) {
      const nullState = _.findKey(control.actions, (val) => !val);
      this.setControlState(id, nullState);
    }
  }
}

render(<KeyboardPanel/>);
