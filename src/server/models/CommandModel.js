const Backbone = require('backbone');
const { timeToPerformMs } = require('../../common/GameConstants');

const CommandModel = Backbone.Model.extend({
  defaults: {
    control: null,
    action: null,
    state: null,
    completed: false
  },

  _timeToPerformInterval: null,

  start(timeToPerform = timeToPerformMs()) {
    if (this._timeToPerformInterval) {
      throw new Error('Command has already been started');
    }

    // Set the starting time-to-perform.
    this.set({ timeToPerform });

    this._timeToPerformInterval = setInterval(() => {
      const timeToPerform = this.get('timeToPerform') - 1000;
      this.set({ timeToPerform });

      if (timeToPerform <= 0) { // <= vs. === for safety belts.
        clearInterval(this._timeToPerformInterval);
      }
    }, 1000);
  }
});

module.exports = CommandModel;
