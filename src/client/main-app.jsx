import $ from 'jquery';
import App from '/App';
import GameModel from '/GameModel';
import PublicationClient from 'publication-client';
import React from 'react';
import ReactDOM from 'react-dom';

let Publications = new PublicationClient('/');

const GAME_QUERY = { _id: 'THE_GAME' };
Publications.subscribe('game', GAME_QUERY);

const model = new GameModel({ _id: GAME_QUERY._id }, {
  reactiveQuery: Publications.getCollection('game').find(GAME_QUERY)
});

ReactDOM.render(<App models={{ model }}/>, $('#app')[0]);
