import _ from 'underscore';
import { PublicationModel } from 'backbone-publication';
import defaults from '/GameModelDefaults';

const GameModel = PublicationModel.extend({
  defaults,

  urlRoot: '/api/games',

  save(key, val, options) {
    // Polymorphism copied from http://backbonejs.org/docs/backbone.html#section-82.
    let attrs;
    if (!key || _.isObject(key)) {
      attrs = key;
      options = val;
    } else {
      attrs = { [key]: val };
    }

    options = _.defaults({}, options, {
      patch: true
    });

    return GameModel.__super__.save.call(this, attrs, options);
  },

  reset() {
    this.save(_.result(this, 'defaults'));
  }
});

export default GameModel;
