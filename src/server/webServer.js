const _ = require('underscore');
const express = require('express');
const fs = require('fs');
const GameModel = require('./models/GameModel');
const path = require('path');

const app = express();

app.use('/public', express.static(path.join(__dirname, '../../public')));

app.use(require('connect-livereload')({
  port: 22222,
  plugins: [
    '/public/lib/livereload-require-js-includes/index.js'
  ]
}));

const indexTemplate = _.template(fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8'));
app.get('/', function(req, res) {
  res.send(indexTemplate({
    game: JSON.stringify(GameModel.default())
  }));
});

module.exports = app;
