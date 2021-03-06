import _ from 'underscore';
import classNames from 'classnames';
import CBR from 'connect-backbone-to-react';
const { connectBackboneToReact } = CBR;
import DangerMask from '/views/DangerMask';
import HUD from '/views/HUD';
import React from 'react';
import Scoreboard from '/views/Scoreboard';
import Spaceship from '/views/Spaceship';
import Status from '/views/Status';
import Sun from '/views/Sun';
import {
  GAME_STATE,
  SUN_UPDATE_INTERVAL_MS,
  DANGER_DISTANCE,
  TIME_BETWEEN_LEVELS_MS
} from '/GameConstants';
const {
  WAITING_FOR_PLAYERS,
  WAITING_TO_START,
  IN_LEVEL,
  BETWEEN_LEVELS,
  DEAD,
  SCOREBOARD
} = GAME_STATE;
import TimeToStart from '/views/TimeToStart';
import Title from '/views/Title';

const SPACESHIP_UPDATE_INTERVAL_MS = 300;

function GameContainer(props) {
  const classes = classNames('game', {
    'horizontal-scroll-background': props.scrollStars
  });

  return <div className={classes}>{props.children}</div>;
}

class App extends React.Component {
  constructor() {
    super();

    this.onKeyDown = ::this.onKeyDown;
  }

  componentDidMount() {
    $(document.body).on('keydown', this.onKeyDown);
  }

  componentWillUnmount() {
    $(document.body).off('keydown', this.onKeyDown);
  }

  onKeyDown(e) {
    if (e.key === ' ') {
      // By default the webpage scrolls a little bit--looks weird / introduces bottom margin.
      e.preventDefault();

      if (this.props.state === WAITING_TO_START) {
        const timeToStart = this.props.timeToStart;
        if (_.isNumber(timeToStart) && (timeToStart > 5 * 1000)) {
          // Skip to 5 seconds to start.
          this.props.set('timeToStart', 5 * 1000);
        }
      } else {
        this.props.reset();
      }
    }
  }

  render() {
    const props = this.props;

    switch (props.state) {
      case WAITING_FOR_PLAYERS:
      case WAITING_TO_START:
        return (
          <GameContainer>
            <Title/>

            {/* Center the ship under the title */}
            <Spaceship style={{ left: 0, right: 0 }}/>

            {props.timeToStart ?
              <TimeToStart time={props.timeToStart}/> :
              <Status>Players, to your panels!</Status>}
          </GameContainer>
        );

      case IN_LEVEL:
      case DEAD:
        return (
          <GameContainer>
            <HUD level={props.level}/>

            {/* HACK(jeff): Hardcode some numbers here to sync the position of the sun and the spaceship
              * given the same values of `sunProgress` and `progress`. */}
            <Sun style={{
              marginLeft: `calc(-2110px + ${props.sunProgress}vw + 20vw)`,
              transition: `all ${SUN_UPDATE_INTERVAL_MS / 1000}s linear`}}/>

            <Spaceship style={{
              marginLeft: `${props.progress}vw`,
              transition: `all ${SPACESHIP_UPDATE_INTERVAL_MS / 1000}s ease` }}/>

            <Status>Hit space bar to reset</Status>

            {((props.progress - props.sunProgress) <= DANGER_DISTANCE) &&
              <DangerMask fatal={props.state === DEAD}/>
            }
          </GameContainer>
        );

      case BETWEEN_LEVELS:
        return (
          <GameContainer scrollStars>
            <Spaceship style={{ animation: `${TIME_BETWEEN_LEVELS_MS / 1000}s ease-in 0s zoomlefttoright` }}/>
          </GameContainer>
        );

      case SCOREBOARD:
        return (
          <GameContainer>
            <Scoreboard level={props.level}/>
          </GameContainer>
        );

      default:
        throw new Error(`Unknown state: ${props.state}`);
    }
  }
}

function mapModelsToProps({ model }) {
  return _.extend(_.pick(model.attributes, [
    'state', 'timeToStart', 'level', 'progress', 'sunProgress'
  ]), {
    set: (...args) => model.save(...args),
    reset: ::model.reset
  });
}

export default connectBackboneToReact(mapModelsToProps)(App);
