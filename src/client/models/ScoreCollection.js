import _ from 'underscore';
import Backbone from 'backbone';
import { MAX_SCOREBOARD_LENGTH } from '../../common/GameConstants';

const ScoreModel = Backbone.Model.extend({
  defaults: {
    name: null,
    score: 0
  },

  parse(resp) {
    const attrs = _.clone(resp);
    attrs.createdAt = new Date(attrs.createdAt);
    return attrs;
  }
});

const ScoreCollection = Backbone.Collection.extend({
  model: ScoreModel,
  url: '/api/scores',

  initialize(models, { maxLength = MAX_SCOREBOARD_LENGTH } = {}) {
    this._maxLength = maxLength;
  },

  // Sort first by score, then by createdAt, both descending.
  // Implementation modeled after https://stackoverflow.com/a/9201348/495611.
  comparator: (s1, s2) => {
    function sortBy(p1, p2, desc=true) {
      let comparison;

      if (p1 < p2) comparison = -1;
      else if (p1 > p2) comparison = 1;
      else comparison = 0;

      return comparison * (desc ? -1 : 1);
    }

    return _.reduce(['score', 'createdAt'], function(comparison, attr) {
      return comparison !== 0 ? comparison : sortBy(s1.get(attr), s2.get(attr));
    }, 0);
  },

  isHighScore(score) {
    if (this.isEmpty()) return true;

    // TODO(jeff): Accept scores that are >= the min once we can truncate the list:
    // https://github.com/wearhere/spacecontrol/issues/61
    return (this.length < this._maxLength) || (score > _.min(this.pluck('score')));
  }
});

export default ScoreCollection;
