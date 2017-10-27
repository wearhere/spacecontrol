import { PublicationModel } from 'backbone-publication';
import { SUN_INITIAL_PROGRESS } from '/GameConstants';

const GameModel = PublicationModel.extend({
  defaults: {
    progress: 0,
    // Start the sun off _behind_ the spaceship, since when they catch each other that's it for the
    // player.
    sunProgress: SUN_INITIAL_PROGRESS
  }
});

export default GameModel;
