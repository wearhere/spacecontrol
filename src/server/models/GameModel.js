const _ = require('underscore');
const Backbone = require('backbone');

const GameModel = Backbone.Model.extend({
  defaults: {
    // This is state shared with the client.
    started: false,
    progress: 0
  },

  // A requirement of `backbone-publication`.
  idAttribute: '_id',

  initialize() {
    this.panels = new Backbone.Collection();

    this._publications = [];

    this.listenTo(this.panels, {
      add: (panel) => {
        this._controlsChanged();

        this.listenTo(panel.controls, {
          update: () => this._controlsChanged()
        });
      },

      remove: (panel) => {
        panel.controls.forEach((control) => this.stopListening(control));
        this.stopListening(panel.controls);

        this._controlsChanged();
      }
    });

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

  _controlsChanged() {
    // TODO(jeff): If we lost a control we were telling users to manipulate, need to tell users
    // to do something else--and we should only be setting a new command if this has happened.

    const allControls = this.panels.reduce((controls, panel) => {
      controls.push(...panel.controls.models);
      return controls;
    }, []);

    // Choose as many controls to manipulate as there are panels.
    const controls = _.sample(allControls, this.panels.length);

    // Now assign these to panels.
    this.panels.forEach((panel) => {
      const control = controls.pop();
      if (control) { // There could theoretically be fewer controls than panels.
        const command = control.getCommand();
        panel.set('display', command.display);

        // TODO(jeff): It would be nice to register the listener only once, perhaps on the controls
        // collections since those will proxy through the control events.
        this.listenTo(control, 'change:state', (_, state) => {
          if (state === command.state) {
            this.stopListening(control, 'change:state');
            this.set('progress', this.get('progress') + 10);

            // TODO(jeff): Give this panel another command now.
          }
        });
      }
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
  },

  default() {
    const DEFAULT_GAME_ID = 'THE_GAME';
    return this.withId(DEFAULT_GAME_ID);
  }
});

module.exports = GameModel;
