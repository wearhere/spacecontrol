const express = require('express');

const app = express();
const path = require('path');

app.use('/public', express.static(path.join(__dirname, '../../public')));

app.get('/', function(req, res) {
  res.sendFile(path.join(__dirname, 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, function() {
  // eslint-disable-next-line no-console
  console.log(`Listening on port ${PORT}…`);
});
