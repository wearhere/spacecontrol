const GameModel = require('./models/GameModel');
const PanelModel = require('./models/PanelModel');
const net = require('net');

const server = net.createServer((connection) => {
  const panel = new PanelModel({}, { connection });

  // TODO(jeff): If we really wanted to support multiple games, we'd have to decide
  // which game to attach this one to.
  GameModel.default().panels.add(panel);
});

server.on('error', (err) => {
  console.error(`Panel server error: ${err}`);
});

module.exports = server;
