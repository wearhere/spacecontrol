import _ from 'underscore';
import CBR from 'connect-backbone-to-react';
const { connectBackboneToReact } = CBR;
import HUD from '/views/HUD';
import React from 'react';
import Spaceship from '/views/Spaceship';
import Sun from '/views/Sun';
import {
  SUN_INITIAL_PROGRESS,
  SUN_UPDATE_INTERVAL_MS
} from '/GameConstants';
import TimeToStart from '/views/TimeToStart';
import Title from '/views/Title';

const SPACESHIP_UPDATE_INTERVAL_MS = 300;

function App(props) {
  // Speedily update when transitioning back to the initial state.
  const sunUpdateIntervalMs = (props.sunProgress === SUN_INITIAL_PROGRESS) ?
    SPACESHIP_UPDATE_INTERVAL_MS : SUN_UPDATE_INTERVAL_MS;

  const spaceshipMargin = (props.state === 'started') ?
    // If the game is in progress move the spaceship along accordingly.
    { marginLeft: `${props.progress}vw` } :
    // Otherwise center it under the title.
    { marginLeft: 'auto', left: 0, right: 0 };

  return (
    <div>
      {(props.state === 'started') && <HUD level={props.level} />}

      {(props.state !== 'started') && <Title/>}

      {/* HACK(jeff): Hardcode some numbers here to sync the position of the sun and the spaceship
        * given the same values of `sunProgress` and `progress`. */}
      <Sun style={{
        marginLeft: `calc(-2110px + ${props.sunProgress}vw + 20vw)`,
        // Immediately transition back to the initial state, otherwise animate.
        transition: `all ${sunUpdateIntervalMs / 1000}s linear`}} />

      <Spaceship style={{
        ...spaceshipMargin,
        transition: `all ${SPACESHIP_UPDATE_INTERVAL_MS / 1000}s ease` }}/>

      <TimeToStart time={props.timeToStart}/>
    </div>
  );
}

function mapModelsToProps({ model }) {
  return _.pick(model.attributes, [
    'state', 'timeToStart', 'level', 'progress', 'sunProgress'
  ]);
}

export default connectBackboneToReact(mapModelsToProps)(App);
