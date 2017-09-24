import Backbone from 'backbone';

const GameModel = Backbone.Model.extend({
  defaults: {
    progress: 0
  },

  initialize() {
    setInterval(() => {
      this.set('progress', this.get('progress') + 20);
    }, 1000);
  }
});

export default GameModel;
