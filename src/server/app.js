const express = require('express');
const GameModel = require('./GameModel');
const http = require('http');
const path = require('path');
const PublicationServer = require('publication-server');

const app = express();

app.use('/public', express.static(path.join(__dirname, '../../public')));

app.use(require('connect-livereload')({
  port: 22222,
  plugins: [
    '/public/lib/livereload-require-js-includes/index.js'
  ]
}));

app.get('/', function(req, res) {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/press-button', function(req, res) {
  GameModel.trigger('button-pressed');
  res.status(204).end();
});

let server = http.createServer(app);
const publications = new PublicationServer({
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

publications.publish('game', function({ _id }) {
  // Create a game or retrieve the existing game.
  let game = GameModel.withId(_id);

  // Publish the current game state.
  game.addPublication(this);

  // Tell the client that all data has been published.
  this.ready();

  // Cleanup if the client disconnects.
  this.onStop(() => game.removePublication(this));
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, function() {
  // eslint-disable-next-line no-console
  console.log(`Web server listening on port ${PORT}…`);
});
