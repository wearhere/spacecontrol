const Backbone = require('backbone');

const ControlModel = Backbone.Model.extend({
  defaults: {
    id: null,
    type: null,
    state: null,
    possibleStates: null,
    action: null,
    item: null
  },

  // Returns something that the user might do with this control.
  // Should be random for controls with multi-valued states.
  getCommand() {
    switch (this.get('type')) {
      case 'button':
        return {
          // TODO(jeff): Make this more flexible to handle commands like "octo bite raven girl nipple".
          display: `${titlecase(this.get('action'))} the ${this.get('item')}!`,
          state: 1
        };
    }
  }
});

function titlecase(str) {
  if (!str) return str;
  return str[0].toUpperCase() + str.slice(1);
}

module.exports = ControlModel;
