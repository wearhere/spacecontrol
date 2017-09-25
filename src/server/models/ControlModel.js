const Backbone = require('backbone');

const ControlModel = Backbone.Model.extend({
  defaults: {
    id: null,
    type: null,
    state: null,
    action: null,
    item: null
  },

  // Returns something that the user might do with this control.
  // Should be random for controls with multi-valued states.
  getCommand() {
    switch (this.get('type')) {
      case 'button':
        return {
          display: `${this.get('action')} the ${this.get('item')}!`,
          state: 1
        };
    }
  }
});

module.exports = ControlModel;
