const _ = require('underscore');
const Backbone = require('backbone');

const GameModel = Backbone.Model.extend({
  defaults: {
    started: false,
    progress: 0
  },

  // A requirement of `backbone-publication`.
  idAttribute: '_id',

  initialize() {
    this._publications = [];

    // Listen to events that cause game state to mutate.
    this._setUpListeners();

    // Whenever game state mutates, publish it to the `GameModel` client-side.
    this.on('change', () => {
      _.each(this._publications, (publication) => {
        publication.changed('game', this.id, this.changedAttributes());
      });
    });
  },

  addPublication(publication) {
    this._publications.push(publication);

    publication.added('game', this.id, this.attributes);
  },

  removePublication(publication) {
    // Not clear that we should call `publication.removed` here, so we don't.
    this._publications = _.without(this._publications, publication);
  },

  _setUpListeners() {
    this.listenTo(GameModel, {
      'button-pressed': () => {
        this.set('progress', this.get('progress') + 10);
      },

      // 'other-event': () => {...}, etc.
    });
  }
}, {
  _instances: new Map(),

  // Factory method.
  withId(id) {
    let instance = this._instances.get(id);
    if (!instance) {
      // Required that we pass `id` as `_id` for the benefit of `backbone-publication`.
      instance = new GameModel({ _id: id });
      this._instances.set(id, instance);
    }
    return instance;
  }
});

// Use the model class itself as a message bus with which to communicate with instances.
_.extend(GameModel, Backbone.Events);

module.exports = GameModel;
