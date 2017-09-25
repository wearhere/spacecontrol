const GameModel = require('./GameModel');
const PublicationServer = require('publication-server');

let publicationServer = null;
module.exports = function(server) {
  if (publicationServer) throw new Error('Publication server has already been initialized!');

  publicationServer = new PublicationServer({
    authFn: function(req, done) {
      process.nextTick(done);
    },
    mountPath: '/ws',
    server,
    errHandler: (err) => {
      // eslint-disable-next-line no-console
      console.error(`Websocket error: ${err}`);
    }
  });

  publicationServer.publish('game', function({ _id }) {
    // Create a game or retrieve the existing game.
    let game = GameModel.withId(_id);

    // Publish the current game state.
    game.addPublication(this);

    // Tell the client that all data has been published.
    this.ready();

    // Cleanup if the client disconnects.
    this.onStop(() => game.removePublication(this));
  });
};
