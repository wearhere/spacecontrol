import _ from 'underscore';
import CBR from 'connect-backbone-to-react';
const { connectBackboneToReact } = CBR;
import React from 'react';
import Spaceship from '/Spaceship';
import Sun from '/Sun';
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
      {/* HACK(jeff): Hardcode some numbers here to sync the position of the sun and the spaceship
        * given the same values of `sunProgress` and `progress`. */}
      <div style={{
        marginLeft: `calc(-2110px + ${props.sunProgress}vw + 20vw)`,
        // Immediately transition back to the initial state, otherwise animate.
        transition: `all ${sunUpdateIntervalMs / 1000}s linear`
      }}>
        <Sun/>
      </div>
      <div style={{
        marginLeft: `${props.progress}vw`,
        transition: `all ${SPACESHIP_UPDATE_INTERVAL_MS / 1000}s ease`
      }}>
        <Spaceship/>
      </div>
    </div>
  );
}

function mapModelsToProps({ model }) {
  return _.pick(model.attributes, 'progress', 'sunProgress');
}

export default connectBackboneToReact(mapModelsToProps)(App);
