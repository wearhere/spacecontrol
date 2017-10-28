const { SUN_INITIAL_PROGRESS } = require('./GameConstants');

const defaults = {
  started: false,
  level: 1,
  progress: 0,
  sunProgress: SUN_INITIAL_PROGRESS
};

module.exports = defaults;
