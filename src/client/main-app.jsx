import $ from 'jquery';
import App from '/App';
import GameModel from '/GameModel';
import React from 'react';
import ReactDOM from 'react-dom';

const model = new GameModel();

ReactDOM.render(<App models={{ model }}/>, $('#app')[0]);
