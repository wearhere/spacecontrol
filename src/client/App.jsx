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

const SPACESHIP_UPDATE_INTERVAL_MS = 300;

function App(props) {
  // Speedily update when transitioning back to the initial state.
  const sunUpdateIntervalMs = (props.sunProgress === SUN_INITIAL_PROGRESS) ?
    SPACESHIP_UPDATE_INTERVAL_MS : SUN_UPDATE_INTERVAL_MS;

  return (
    <div>
      <HUD level={props.level} />
      {/* HACK(jeff): Hardcode some numbers here to sync the position of the sun and the spaceship
        * given the same values of `sunProgress` and `progress`. */}
      <Sun style={{
        marginLeft: `calc(-2110px + ${props.sunProgress}vw + 20vw)`,
        // Immediately transition back to the initial state, otherwise animate.
        transition: `all ${sunUpdateIntervalMs / 1000}s linear`}} />
      <Spaceship style={{
        marginLeft: `${props.progress}vw`,
        transition: `all ${SPACESHIP_UPDATE_INTERVAL_MS / 1000}s ease` }}/>
    </div>
  );
}

function mapModelsToProps({ model }) {
  return _.pick(model.attributes, 'level', 'progress', 'sunProgress');
}

export default connectBackboneToReact(mapModelsToProps)(App);
