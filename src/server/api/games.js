const express = require('express');
const GameModel = require('../models/GameModel');

const router = express.Router();

router.param('id', function(req, res, next, id) {
  // Create a game or retrieve the existing game.
  req.game = GameModel.withId(id);
  next();
});

router.put('/:id', function(req, res) {
  req.game.set(req.body);
  res.status(204).end();
});

module.exports = router;
