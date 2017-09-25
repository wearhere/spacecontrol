const http = require('http');

// Need to wrap the Express server in a real HTTP server for the benefit of the publication server.
let server = http.createServer(require('./webServer'));

require('./publicationServer')(server);

const PORT = process.env.PORT || 3000;
server.listen(PORT, function() {
  // eslint-disable-next-line no-console
  console.log(`Web server listening on port ${PORT}…`);
});
