import _ from 'underscore';
import React from 'react';
import Status from '/views/Status';

export default function TimeToStart(props) {
  if (!_.isNumber(props.time) || (props.time <= 0)) return null;

  return <Status>Game will start in {props.time / 1000}…</Status>;
}
