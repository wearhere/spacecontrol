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

    this.listenTo(this.panels, {
      add: (panel) => {
        this._controlsChanged();

        this.listenTo(panel.controls, {
          update: () => this._controlsChanged(),

          'change:state': (control, state) => {
            const command = this._commands.findWhere({ control });
            if (command && (state === command.get('state'))) {
              command.set('completed', true);
            }
          }
        });
      },

      remove: (panel) => {
        panel.controls.forEach((control) => this.stopListening(control));
        this.stopListening(panel.controls);

        this._controlsChanged();
      }
    });

    this._commands = new Backbone.Collection();
    this.listenTo(this._commands, {
      'change:completed': (command) => {
        this._commands.remove(command);
        // TODO(jeff): Assign a new command to the panel.
        this.panels.findWhere({ command }).unset('command');
        this.set('progress', this.get('progress') + 10);
      }
    });

    // Whenever game state mutates, publish it to the `GameModel` client-side.
    this._publications = [];
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
    // TODO(jeff): We should only be setting new commands if
    //
    //  1. New panels have joined
    //  2. A control described by a current command has been lost
    //  3. One or more existing panels have finished their commands
    //
    // Whereas currently we blow away existing panels' commands always.

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
        panel.set('command', command);
        this._commands.add(command);
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
