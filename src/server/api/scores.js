const _ = require('underscore');
const express = require('express');
const fs = require('fs');
const path = require('path');
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
  readScores((err, scores) => {
    if (err) return res.status(500).end();

    const score = _.defaults({}, req.body, { id: uuidv4() });
    scores.push(score);

    writeScores(scores, (err2) => {
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
