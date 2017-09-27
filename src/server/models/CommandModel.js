const Backbone = require('backbone');

const CommandModel = Backbone.Model.extend({
  defaults: {
    control: null,
    action: null,
    state: null,
    completed: false
  }
});

module.exports = CommandModel;
