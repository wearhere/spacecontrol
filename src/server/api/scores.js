const _ = require('underscore');
const express = require('express');
const fs = require('fs');
const path = require('path');
const ScoreCollection = require('../../common/models/ScoreCollection');
const uuidv4 = require('uuid/v4');

const router = express.Router();

const SCORE_PATH = path.resolve(__dirname, '../scores.json');

// HACK(jeff): These APIs are not atomic!! Luckily we only have a single client
// at a time.

// TODO(jeff): Instate promise support for Express to clean up these nested callbacks.

router.get('/', function(req, res) {
  readScores((err, scores) => {
    if (err) return res.status(500).end();

    res.json(scores);
  });
});

router.post('/', function(req, res) {
  const score = _.extend({}, req.body, {
    id: uuidv4(),
    createdAt: new Date().toISOString()
  });

  readScores((err, scores) => {
    if (err) return res.status(500).end();

    const scoreColl = new ScoreCollection(scores, { parse: true });
    if (!scoreColl.isHighScore(score.score)) {
      return res.status(403).json({ message: 'Not a high score!' });
    }
    // Will automatically truncate the collection if necessary.
    scoreColl.add(score, { parse: true });

    writeScores(scoreColl.toJSON(), (err2) => {
      if (err2) return res.status(500).end();

      res.json(score);
    });
  });
});

function readScores(done) {
  fs.readFile(SCORE_PATH, { encoding: 'utf8'}, (err, str) => {
    // Ignore error--file might not exist.

    let scores = [];
    try {
      scores = JSON.parse(str);
    } catch (e) {
      // File didn't exist or JSON was malformed.
    }

    done(null, scores);
  });
}

function writeScores(scores, done) {
  let str;

  try {
    str = JSON.stringify(scores);
  } catch (e) {
    return done(e);
  }

  fs.writeFile(SCORE_PATH, str, done);
}

module.exports = router;
