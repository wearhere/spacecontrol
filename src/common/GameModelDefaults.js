const { SUN_INITIAL_PROGRESS } = require('./GameConstants');

const defaults = {
  // 'waiting for players', 'waiting to start', 'started'
  state: 'waiting for players',
  timeToStart: null,
  level: 1,
  progress: 0,
  sunProgress: SUN_INITIAL_PROGRESS
};

module.exports = defaults;
