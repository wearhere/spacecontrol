import { PublicationModel } from 'backbone-publication';

const GameModel = PublicationModel.extend({
  defaults: {
    progress: 0
  }
});

export default GameModel;
