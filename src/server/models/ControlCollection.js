const Backbone = require('backbone');
const ControlModel = require('./ControlModel');

const ControlCollection = Backbone.Collection.extend({
  model: ControlModel
});

module.exports = ControlCollection;
