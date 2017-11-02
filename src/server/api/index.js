const express = require('express');
const router = express.Router();

router.use('/games', require('./games'));
router.use('/scores', require('./scores'));

module.exports = router;
