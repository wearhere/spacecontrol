const _ = require('underscore');
const bodyParser = require('body-parser');
const express = require('express');
const fs = require('fs');
const GameModel = require('./models/GameModel');
const path = require('path');

const app = express();

app.use(bodyParser.json());

app.use('/public', express.static(path.join(__dirname, '../../public')));

if (process.env.NODE_ENV !== 'production') {
  app.use(require('connect-livereload')({
    port: 22222,
    plugins: [
      '/public/lib/livereload-require-js-includes/index.js'
    ]
  }));
}

app.use('/api', require('./api'));

const indexTemplate = _.template(fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8'));
app.get('/', function(req, res) {
  res.send(indexTemplate({
    game: JSON.stringify(GameModel.default())
  }));
});

module.exports = app;
