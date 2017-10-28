const _ = require('underscore');
const Backbone = require('backbone');
const defaults = require('../../common/GameModelDefaults');
const {
  SUN_PROGRESS_INCREMENT,
  SUN_UPDATE_INTERVAL_MS
} = require('../../common/GameConstants');

const GameModel = Backbone.Model.extend({
  defaults,

  // A requirement of `backbone-publication`.
  idAttribute: '_id',

  initialize() {
    this.panels = new Backbone.Collection();

    this.listenTo(this.panels, {
      add: (panel) => {
        this._assignCommands();

        this.listenTo(panel.controls, {
          update: (_, { changes: { added, removed } }) => {
            this._controlsRemoved(removed);
            if (!_.isEmpty(added)) this._assignCommands();
          },

          'change:state': (control, state) => {
            const command = this._commands.findWhere({ control });
            if (command && (state === command.get('state'))) {
              command.set('completed', true);
            }
          }
        });
      },

      remove: (panel) => {
        this._controlsRemoved(panel.controls.models);
        this.stopListening(panel.controls);
      },

      'change:command': (panel, command) => {
        if (!command) this._assignCommands();
      }
    });

    this._commands = new Backbone.Collection();
    this.listenTo(this._commands, {
      'change:completed': (command) => {
        this._commands.remove(command);
        this.panels.findWhere({ command }).unset('command');
        this.set('progress', this.get('progress') + 10);
      }
    });

    this.on('change:progress', (model, progress) => {
      if (progress >= 100) { // >= vs. === for safety belts.
        // Level up!
        this.set({
          level: this.get('level') + 1,
          progress: 0,
          sunProgress: _.result(this, 'defaults').sunProgress
        });
      }
    });

    setInterval(() => {
      this.set('sunProgress', this.get('sunProgress') + SUN_PROGRESS_INCREMENT);
    }, SUN_UPDATE_INTERVAL_MS);

    this.on('change:sunProgress', (model, sunProgress) => {
      if (sunProgress >= this.get('progress')) {
        // Sun has caught the player--game over! Reset to the initial state.
        this.set(_.result(this, 'defaults'));
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

  _controlsRemoved(controls) {
    controls.forEach((control) => {
      const command = this._commands.findWhere({ control });
      if (command) {
        this._commands.remove(command);
        const panel = this.panels.findWhere({ command });
        // Note that the panel might not exist if the controls were removed because the entire panel
        // disconnected.
        if (panel) panel.unset('command');
      }
    });
  },

  // Assigns commands to panels needing commands, which happens when:
  //
  //  1. New panels and/or controls have joined
  //  2. A control described by a current command has been lost (possibly because the panel has
  //     disconnected)
  //  3. One or more existing panels have finished their commands
  _assignCommands() {
    // Choose as many controls to manipulate as there are panels needing commands.
    const panelsNeedingCommands = this.panels.filter((panel) => !panel.has('command'));
    if (_.isEmpty(panelsNeedingCommands)) return;

    const allControls = this.panels.reduce((controls, panel) => {
      controls.push(...panel.controls.models);
      return controls;
    }, []);

    const inactiveControls = _.difference(allControls, this._commands.pluck('control'));

    const controlsToAssign = _.sample(inactiveControls, panelsNeedingCommands.length);

    // Now assign these to panels.
    panelsNeedingCommands.forEach((panel) => {
      const control = controlsToAssign.pop();
      if (control) { // There could theoretically be fewer inactive controls than panels.
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
