const Backbone = require('backbone');
const CommandModel = require('./CommandModel');

const ControlModel = Backbone.Model.extend({
  defaults: {
    id: null,
    type: null,
    state: null,
    possibleStates: null,
    action: null
  },

  // Returns something that the user might do with this control.
  // Should be random for controls with multi-valued states.
  getCommand() {
    let action, state;

    switch (this.get('type')) {
      case 'button':
        // TODO(jeff): Make this more flexible to handle commands like "octo bite raven girl nipple".
        action = this.get('action');
        state = 1;
        break;
    }

    return new CommandModel({ control: this, action, state });
  }
});

module.exports = ControlModel;
