import $ from 'jquery';
import App from '/App';
import GameModel from '/GameModel';
import PublicationClient from 'publication-client';
import React from 'react';
import ReactDOM from 'react-dom';

// Retrieve the game data that was bootstrapped into `index.html`.
const game = window['initialPayload']['game'];

// Open the websocket.
let Publications = new PublicationClient('/');

// Subscribe to updates to our game.
Publications.subscribe('game', { _id: game._id });

// Hydrate a `GameModel` from the game data and wire it to updates from the websocket.
const model = new GameModel(game, {
  reactiveQuery: Publications.getCollection('game').find({ _id: game._id })
});

ReactDOM.render(<App models={{ model }}/>, $('#app')[0]);
