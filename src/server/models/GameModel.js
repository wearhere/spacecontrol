const _ = require('underscore');
const Backbone = require('backbone');
const defaults = require('../../common/GameModelDefaults');
const {
  GAME_STATE: { WAITING_FOR_PLAYERS, WAITING_TO_START, IN_LEVEL, BETWEEN_LEVELS, DEAD, SCOREBOARD },
  gameHasStarted,
  SUN_PROGRESS_INCREMENT,
  SUN_UPDATE_INTERVAL_MS,
  TIME_TO_START_MS,
  timeToPerformMs,
  TIME_BETWEEN_LEVELS_MS,
  TIME_TO_DIE_MS
} = require('../../common/GameConstants');

const GameModel = Backbone.Model.extend({
  defaults,

  // A requirement of `backbone-publication`.
  idAttribute: '_id',

  _timeToStartInterval: null,
  _sunInterval: null,
  _nextLevelTimeout: null,
  _endGameTimeout: null,

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
        if (!command) this._assignCommands();
      }
    });

    this._playingPanels = new Backbone.Collection();
    this.listenTo(this._playingPanels, {
      add: () => {
        if (this.get('state') === WAITING_FOR_PLAYERS) {
          this.set('state', WAITING_TO_START);
        } else if (this.get('state') === WAITING_TO_START) {
          const allPlayersJoined = this._playingPanels.length === this.panels.length;
          const timeToStart = this.get('timeToStart');
          if (allPlayersJoined && _.isNumber(timeToStart) && (timeToStart > 5 * 1000)) {
            // Skip to 5 seconds to start if there are no more players to join.
            this.set('timeToStart', 5 * 1000);
          }
        }
      },

      remove: () => {
        if (this._playingPanels.isEmpty()) {
          if (gameHasStarted(this.get('state'))) {
            this._resetGame();
          } else {
            this.set({
              timeToStart: null,
              state: WAITING_FOR_PLAYERS
            });
          }
        }
      }
    });

    this._commands = new Backbone.Collection();
    this.listenTo(this._commands, {
      'change:timeToPerform': (command, timeToPerform) => {
        const gameStarted = gameHasStarted(this.get('state'));
        const panels = gameStarted ? this._playingPanels : this.panels;
        const assignedPanel = panels.findWhere({ command });

        if (timeToPerform > 0) {
          assignedPanel.set('progress', timeToPerform / timeToPerformMs(this.get('state')));
        } else {
          if (gameStarted) {
            assignedPanel.setStatus('Too late!', 500);
            this.set('progress', Math.max(this.get('progress') - 10, 0));
          }

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
        assignedPanel.setStatus('Nice job!', 500);

        if (!gameHasStarted(this.get('state'))) {
          this._playingPanels.add(assignedPanel);
        } else {
          this.set('progress', this.get('progress') + 10);
        }

        // HACK(jeff): Unset the command after potentially adding the panel to `this._playingPanels`
        // to prevent a panel waiting to start from getting a new command.
        assignedPanel.unset('command');
      }
    });


    this._publications = [];

    this.on({
      'change:state': (model, state) => {
        clearInterval(this._timeToStartInterval);
        clearInterval(this._sunInterval);
        clearTimeout(this._nextLevelTimeout);
        clearTimeout(this._endGameTimeout);

        switch (state) {
          case WAITING_FOR_PLAYERS:
            // Reset the panels so that players may signal they're ready.
            this.panels.invoke('clearStatusAndProgress');
            this._playingPanels.reset();
            this._assignCommands();

            break;

          case WAITING_TO_START:
            this.set('timeToStart', TIME_TO_START_MS);

            this._timeToStartInterval = setInterval(() => {
              this.set('timeToStart', Math.max(this.get('timeToStart') - 1000, 0));
            }, 1000);

            break;

          case IN_LEVEL: {
            if (this.previous('state') === WAITING_TO_START) {
              // Discard any commands on which we are waiting (from panels that didn't report during
              // the WAITING_TO_START phase).
              this._resetCommands();

              // Notify any panels that didn't report that they'll have to wait.
              const nonPlayingPanels = this.panels.difference(this._playingPanels.models);

              // TODO(jeff): Fix https://github.com/wearhere/spacecontrol/issues/27 so we can use …
              nonPlayingPanels.forEach((panel) => panel.set('display', 'Waiting for next game...'));
            }

            // Give all the player panels commands.
            this._assignCommands();

            this._sunInterval = setInterval(() => {
              this.set('sunProgress', this.get('sunProgress') + SUN_PROGRESS_INCREMENT);
            }, SUN_UPDATE_INTERVAL_MS);

            break;
          }

          case BETWEEN_LEVELS:
            // Discard any commands from the panels other than the one that finished the level.
            this._resetCommands();

            this._playingPanels.forEach((panel) => {
              panel.clearStatusAndProgress();
              // TODO(jeff): Fix https://github.com/wearhere/spacecontrol/issues/27 so we can use …
              panel.set('display', 'Get ready...');
            });

            this._nextLevelTimeout = setTimeout(() => {
              this.set({
                state: IN_LEVEL,
                level: this.get('level') + 1,
                progress: 0,
                sunProgress: _.result(this, 'defaults').sunProgress
              });
            }, TIME_BETWEEN_LEVELS_MS);

            break;

          case DEAD:
            // Discard all commands.
            this._resetCommands();

            this._playingPanels.forEach((panel) => {
              panel.clearStatusAndProgress();
              panel.set('display', 'Too late!!!');
            });

            this._endGameTimeout = setTimeout(() => this.set('state', SCOREBOARD), TIME_TO_DIE_MS);

            break;

          case SCOREBOARD:
            // Clear the 'Too late' message.
            this._playingPanels.forEach((panel) => panel.unset('display'));

            // We don't put any sort of timer in here for resetting the game--the user can hit space.

            break;

          default:
            throw new Error(`Unknown state: ${state}`);
        }
      },

      'change:timeToStart': (model, timeToStart) => {
        if (_.isNumber(timeToStart)) {
          if (timeToStart <= 0) { // <= vs. === for safety belts.
            this.set('state', IN_LEVEL);
          } else if (this.get('state') === WAITING_TO_START) { // Safety belts to avoid wiping out commands.
            this._playingPanels.forEach((panel) => {
              panel.clearStatusAndProgress();

              // TODO(jeff): Fix https://github.com/wearhere/spacecontrol/issues/27 so we can use …
              panel.set('display', `Game will start in ${timeToStart / 1000}...`);
            });
          }
        }
      },

      'change:progress': (model, progress) => {
        if (progress >= 100) { // >= vs. === for safety belts.
          // Level up!
          this.set('state', BETWEEN_LEVELS);
        }
      },

      // Check whether the sun has caught the player when both the sun progress _and_ the progress
      // change since the player might slide backward if they miss a command.
      'change:sunProgress change:progress': () => {
        if (this.get('sunProgress') >= this.get('progress')) {
          // Sun has caught the player--game over!
          this.set('state', DEAD);
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

  _resetCommands() {
    this._commands.forEach((command) => this.panels.findWhere({ command }).unset('command'));
    this._commands.reset();
  },

  // Assigns commands to panels needing commands, which happens when:
  //
  //  1. New panels and/or controls have joined
  //  2. A control described by a current command has been lost (possibly because the panel has
  //     disconnected)
  //  3. One or more existing panels have finished their commands
  _assignCommands() {
    const gameStarted = gameHasStarted(this.get('state'));
    const panels = gameStarted ? this._playingPanels : this.panels;

    // Choose as many controls to manipulate as there are panels needing commands.
    // Panels waiting to start will get commands when we start.
    // Also don't assign when we're between levels or dead.
    const panelsNeedingCommands = panels.filter((panel) => {
      return !panel.has('command') &&
        !((this.get('state') === WAITING_TO_START) && this._playingPanels.contains(panel)) &&
        !_.contains([BETWEEN_LEVELS, DEAD], this.get('state'));
    });
    if (_.isEmpty(panelsNeedingCommands)) return;

    const activeControls = this._commands.pluck('control');
    const inactiveControlsByPanel = new Map();
    panels.each((panel) => {
      const inactiveControls = panel.controls.difference(activeControls);
      if (!_.isEmpty(inactiveControls)) {
        inactiveControlsByPanel.set(panel, inactiveControls);
      }
    });

    panelsNeedingCommands.forEach((panel) => {
      let panelToAssign, controlsToAssign;

      // If we're waiting to start, we assign only same-panel commands, so that we may detect if
      // a player is actually at the panel. Otherwise we assign cross-panel commands too, for most
      // shouting.
      //
      // When we choose cross-panel commands, we choose a panel first, _then_ a control from that
      // panel, rather than sampling from _all_ panels, in order to try to more evenly distribute
      // commands between panels i.e. players (even if one panel has a ton of controls).
      if (gameStarted) {
        panelToAssign = _.sample([...inactiveControlsByPanel.keys()]);
      } else {
        panelToAssign = panel;
      }

      controlsToAssign = inactiveControlsByPanel.get(panelToAssign);

      const control = _.sample(controlsToAssign);

      // We might have run out of controls.
      if (!control) return;

      // Remove this control (and potentially panel) from the set to assign.
      controlsToAssign = _.without(controlsToAssign, control);
      if (_.isEmpty(controlsToAssign)) {
        inactiveControlsByPanel.delete(panelToAssign);
      } else {
        inactiveControlsByPanel.set(panel, controlsToAssign);
      }

      const command = control.getCommand();
      panel.set({ command });
      this._commands.add(command);

      // Give the player a limited time to perform commands.
      command.start(timeToPerformMs(this.get('state')));
    });
  },

  _resetGame() {
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
