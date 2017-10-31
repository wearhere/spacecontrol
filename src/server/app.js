const http = require('http');

// Create the web server.
// Need to wrap the Express server in a real HTTP server for the benefit of the publication server.
const webServer = http.createServer(require('./webServer'));

// Create the websocket server and mount it on the web server.
require('./websocketServer')(webServer);

// Create the panel (socket) server.
const panelServer = require('./panelServer');

const WEB_PORT = process.env.WEB_PORT || 3000;
webServer.listen(WEB_PORT, function() {
  console.log(`Web server listening on port ${WEB_PORT}…`);
});

const PANEL_PORT = process.env.PANEL_PORT || 8000;
panelServer.listen(PANEL_PORT, () => {
//panelServer.listen(80,'192.168.1.254', () => {
  console.log(`Panel server listening on port ${PANEL_PORT}…`);
});
