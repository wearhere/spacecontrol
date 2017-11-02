import _ from 'underscore';
import Backbone from 'backbone';
import { MAX_SCOREBOARD_LENGTH } from '../../common/GameConstants';

const ScoreModel = Backbone.Model.extend({
  defaults: {
    name: null,
    score: 0
  }
});

const ScoreCollection = Backbone.Collection.extend({
  model: ScoreModel,
  url: '/api/scores',

  initialize(models, { maxLength = MAX_SCOREBOARD_LENGTH }) {
    this._maxLength = maxLength;
  },

  isHighScore(score) {
    if (this.isEmpty()) return true;

    // TODO(jeff): Accept scores that are >= the min once we can truncate the list:
    // https://github.com/wearhere/spacecontrol/issues/61
    return (this.length < this._maxLength) || (score > _.min(this.pluck('score')));
  }
});

export default ScoreCollection;
