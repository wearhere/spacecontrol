const {
  GAME_STATE: { WAITING_FOR_PLAYERS },
  SUN_INITIAL_PROGRESS,
} = require('./GameConstants');

const defaults = {
  state: WAITING_FOR_PLAYERS,
  timeToStart: null,
  level: 1,
  progress: 0,
  sunProgress: SUN_INITIAL_PROGRESS
};

module.exports = defaults;
