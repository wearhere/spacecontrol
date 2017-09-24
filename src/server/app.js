const express = require('express');

const app = express();

const http = require('http');
const path = require('path');
const PublicationServer = require('publication-server');

app.use('/public', express.static(path.join(__dirname, '../../public')));

app.get('/', function(req, res) {
  res.sendFile(path.join(__dirname, 'index.html'));
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
  let progress = 0;

  this.added('game', _id, { _id, progress });

  this.ready();

  setInterval(() => {
    this.changed('game', _id, { progress: progress += 10 });
  }, 1000);
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, function() {
  // eslint-disable-next-line no-console
  console.log(`Web server listening on port ${PORT}…`);
});
