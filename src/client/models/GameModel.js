import _ from 'underscore';
import { PublicationModel } from 'backbone-publication';
import defaults from '/GameModelDefaults';

const GameModel = PublicationModel.extend({
  defaults,

  urlRoot: '/api/games',

  reset() {
    this.save(_.result(this, 'defaults'));
  }
});

export default GameModel;
