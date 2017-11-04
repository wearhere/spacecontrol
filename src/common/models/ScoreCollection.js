const _ = require('underscore');
const Backbone = require('backbone');
const { MAX_SCOREBOARD_LENGTH } = require('../GameConstants');

const ScoreModel = Backbone.Model.extend({
  defaults: {
    name: null,
    score: 0,
    createdAt: null
  },

  parse(resp) {
    const attrs = _.clone(resp);
    attrs.createdAt = new Date(attrs.createdAt);
    return attrs;
  },

  toJSON() {
    const attrs = _.clone(this.attributes);
    if (attrs.createdAt) attrs.createdAt = attrs.createdAt.toISOString();
    return attrs;
  }
});

const ScoreCollection = Backbone.Collection.extend({
  model: ScoreModel,
  url: '/api/scores',

  initialize(models, { maxLength = MAX_SCOREBOARD_LENGTH } = {}) {
    this._maxLength = maxLength;
  },

  add(...args) {
    let models = ScoreCollection.__super__.add.call(this, ...args);

    const modelsToRemove = _.difference(this.models, this.slice(0, this._maxLength));
    if (!_.isEmpty(modelsToRemove)) {
      this.remove(modelsToRemove);
      models = _.difference(models, modelsToRemove);
    }

    return models;
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

    return (this.length < this._maxLength) || (score >= _.min(this.pluck('score')));
  }
});

module.exports = ScoreCollection;
