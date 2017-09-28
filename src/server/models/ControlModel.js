const _ = require('underscore');
const Backbone = require('backbone');
const CommandModel = require('./CommandModel');
const util = require('util');

const ControlModel = Backbone.Model.extend({
  defaults: {
    id: null,
    state: null,
    actions: null
  },

  parse(hash) {
    const attrs = _.clone(hash);

    if (_.isArray(attrs.actions)) {
      const states = attrs.actions[0];
      const templateAction = attrs.actions[1];
      attrs.actions = _.object(states, _.times(states.length, (i) => {
        // HACK(jeff): Pretty sure taking remote input and passing it through a formatter is a huge
        // security risk.
        return util.format(templateAction, states[i]);
      }));
    }

    return attrs;
  },

  // Returns something that the user might do with this control. If the user may perform multiple
  // actions to/with this control, this method will return one at random.
  getCommand() {
    let action, state;

    const actions = this.get('actions');
    const currentAction = actions[this.get('state')];
    const possibleActions = _.without(actions, currentAction).filter((action) => !!action);
    if (_.isEmpty(possibleActions)) {
      console.error('Action', currentAction, 'is stuck! Programming error or hardware error? ' +
        '(or temporary race condition see code)');

      // ???(jeff): What to do here? Just tell the player to do the same thing for now, hopefully
      // they can notify an attendant or we'll catch it in logs.
      //
      // But as long as there's no delay between commands I think this might just be a race
      // condition --`panel.py` can't necessarily reset the button fast enough.
      action = currentAction;
      state = this.get('state');
    } else {
      action = _.sample(possibleActions);
      state = _.findKey(actions, (val) => (val === action));
    }

    return new CommandModel({ control: this, action, state });
  }
});

module.exports = ControlModel;
