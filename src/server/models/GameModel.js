const _ = require('underscore');
const Backbone = require('backbone');
const defaults = require('../../common/GameModelDefaults');
const {
  SUN_PROGRESS_INCREMENT,
  SUN_UPDATE_INTERVAL_MS,
  TIME_TO_START_MS,
  TIME_TO_PERFORM_MS
} = require('../../common/GameConstants');

const GameModel = Backbone.Model.extend({
  defaults,

  // A requirement of `backbone-publication`.
  idAttribute: '_id',

  _timeToStartInterval: null,
  _sunInterval: null,

  initialize() {
    this.panels = new Backbone.Collection();
    this.listenTo(this.panels, {
      add: (panel) => {
        this._assignCommands();

        this.listenTo(panel.controls, {
          update: (controls, { changes: { added, removed } }) => {
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

        if (this._playingPanels.contains(panel)) this._playingPanels.remove(panel);
      },

      'change:command': (panel, command) => {
        if (!command) {
          // Assign another command when one finishes if this panel is in play.
          // If we're waiting to start, wait to give the panel that completed the command
          // another one until we start.
          if ((this.get('state') === 'started') && this._playingPanels.contains(panel)) {
            this._assignCommands();
          }
        }
      }
    });

    this._playingPanels = new Backbone.Collection();
    this.listenTo(this._playingPanels, {
      add: () => {
        if (this.get('state') === 'waiting for players') {
          this.set('state', 'waiting to start');
        }
      },

      remove: () => {
        if (this._playingPanels.isEmpty()) {
          if (this.get('state') === 'started') {
            this._endGame();
          } else {
            this.set({
              timeToStart: null,
              state: 'waiting for players'
            });
          }
        }
      }
    });

    this._commands = new Backbone.Collection();
    this.listenTo(this._commands, {
      'change:timeToPerform': (command, timeToPerform) => {
        const assignedPanel = this._playingPanels.findWhere({ command });

        if (timeToPerform > 0) {
          assignedPanel.set('status', { progress: timeToPerform / TIME_TO_PERFORM_MS });
        } else {
          // No need to clear this status after display since it will shortly be replaced by the
          // new timer.
          assignedPanel.set('status', { message: 'Too late!' });
          this.set('progress', Math.max(this.get('progress') - 10, 0));

          this._commands.remove(command);
          assignedPanel.unset('command');
        }
      },

      'change:completed': (command) => {
        this._commands.remove(command);

        // Search _all_ panels for the one reporting the command not just playing panels,
        // since this may be before the game starts.
        const assignedPanel = this.panels.findWhere({ command });

        // Push the status before unsetting the command, as that will cause a new command to be
        // assigned and sent.
        assignedPanel.set('status', { message: 'Nice job!' });
        setTimeout(() => {
          if (_.isEqual(assignedPanel.get('status'), { message: 'Nice job!' })) {
            assignedPanel.unset('status');
          }
        }, 500);

        assignedPanel.unset('command');

        if (this.get('state') !== 'started') {
          this._playingPanels.add(assignedPanel);
        } else {
          this.set('progress', this.get('progress') + 10);
        }
      }
    });


    this._publications = [];

    this.on({
      'change:state': (model, state) => {
        clearInterval(this._timeToStartInterval);
        clearInterval(this._sunInterval);

        switch (state) {
          case 'started': {
            // Discard any commands on which we are waiting (from panels that didn't report during
            // the 'waiting to start' phase).
            this._commands.forEach((command) => this.panels.findWhere({ command }).unset('command'));
            this._commands.reset();

            // Notify any panels that didn't report that they'll have to wait.
            const nonPlayingPanels = this.panels.difference(this._playingPanels.models);

            // TODO(jeff): Fix https://github.com/wearhere/spacecontrol/issues/27 so we can use …
            nonPlayingPanels.forEach((panel) => panel.set('display', 'Waiting for next game...'));

            // Now give all the player panels commands.
            this._assignCommands();

            this._sunInterval = setInterval(() => {
              this.set('sunProgress', this.get('sunProgress') + SUN_PROGRESS_INCREMENT);
            }, SUN_UPDATE_INTERVAL_MS);

            break;
          }
          case 'waiting to start':
            this.set('timeToStart', TIME_TO_START_MS);

            this._timeToStartInterval = setInterval(() => {
              this.set('timeToStart', Math.max(this.get('timeToStart') - 1000, 0));
            }, 1000);

            break;

          case 'waiting for players':
            // Reset the panels so that players may signal they're ready.
            this.panels.forEach((panel) => panel.unset('status'));
            this._assignCommands();

            break;

          default:
            throw new Error(`Unknown state: ${state}`);
        }
      },

      'change:timeToStart': (model, timeToStart) => {
        if (_.isNumber(timeToStart)) {
          if (timeToStart <= 0) { // <= vs. === for safety belts.
            this.set('state', 'started');
          } else if (this.get('state') === 'waiting to start') { // Safety belts to avoid wiping out commands.
            this._playingPanels.forEach((panel) => {
              // TODO(jeff): Fix https://github.com/wearhere/spacecontrol/issues/27 so we can use …
              panel.set('display', `Game will start in ${timeToStart / 1000}...`);
            });
          }
        }
      },

      'change:progress': (model, progress) => {
        if (progress >= 100) { // >= vs. === for safety belts.
          // Level up!
          this.set({
            level: this.get('level') + 1,
            progress: 0,
            sunProgress: _.result(this, 'defaults').sunProgress
          });
        }
      },

      // Check whether the sun has caught the player when both the sun progress _and_ the progress
      // change since the player might slide backward if they miss a command.
      'change:sunProgress change:progress': () => {
        if (this.get('sunProgress') >= this.get('progress')) {
          // Sun has caught the player--game over! Reset to the initial state.
          this._endGame();
        }
      },

      // Whenever game state mutates, publish it to the `GameModel` client-side.
      'change': () => {
        _.each(this._publications, (publication) => {
          publication.changed('game', this.id, this.changedAttributes());
        });
      }
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
    const panels = (this.get('state') === 'started') ? this._playingPanels : this.panels;

    // Choose as many controls to manipulate as there are panels needing commands.
    const panelsNeedingCommands = panels.filter((panel) => !panel.has('command'));
    if (_.isEmpty(panelsNeedingCommands)) return;

    const controlsToPanels = new WeakMap();
    const allControls = panels.reduce((controls, panel) => {
      panel.controls.forEach((control) => {
        controlsToPanels.set(control, panel);
        controls.push(control);
      });
      return controls;
    }, []);

    const inactiveControls = _.difference(allControls, this._commands.pluck('control'));

    let controlsToAssign;

    const assignControl = (panel, control) => {
      const command = control.getCommand();
      panel.set({ command });
      this._commands.add(command);

      // Give the player a limited time to perform commands once the game starts.
      if (this.get('state') === 'started') {
        command.start();
      }
    };

    // If we're waiting to start, we assign only same-panel commands, so that we may detect if
    // a player is actually at the panel. Otherwise we assign cross-panel commands too, for most
    // shouting.
    if (this.get('state') === 'started') {
      controlsToAssign = _.sample(inactiveControls, panelsNeedingCommands.length);

      panelsNeedingCommands.forEach((panel) => {
        const control = controlsToAssign.pop();

        // There could theoretically be fewer inactive controls than panels.
        if (control) assignControl(panel, control);
      });
    } else {
      panelsNeedingCommands.forEach((panel) => {
        controlsToAssign = _.filter(inactiveControls, (control) => {
          const pnl = controlsToPanels.get(control);
          return pnl === panel;
        });

        const control = _.sample(controlsToAssign);

        // This panel might have zero controls, either because it hasn't announced yet or because
        // it's not configured right.
        if (control) assignControl(panel, control);
      });
    }
  },

  _endGame() {
    this.set(_.result(this, 'defaults'));
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
