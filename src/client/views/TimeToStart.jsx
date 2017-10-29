import _ from 'underscore';
import React from 'react';

export default function TimeToStart(props) {
  if (!_.isNumber(props.time) || (props.time <= 0)) return null;

  return <h3 className='timeToStart'>Game will start in {props.time / 1000}…</h3>;
}
