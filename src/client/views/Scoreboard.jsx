import $ from 'jquery';
import _ from 'underscore';
import KeyHint from '/views/KeyHint';
import React from 'react';
import ScoreCollection from '/models/ScoreCollection';
import { TIME_TO_STEP_SCOREBOARD_MS } from '/GameConstants';

export default class ScoreboardContainer extends React.Component {
  constructor() {
    super();

    this.scores = new ScoreCollection([]);

    this.state = {
      highScore: null,
      isLoaded: false,
      saveInProgress: false,
      hasSkippedHighScore: false
    };
  }

  componentDidMount() {
    // Don't bother handling any errors, the players can just reset the game.
    this.scores.fetch().done(() => this.setState({ isLoaded: true }));

    this.scheduleKeyHintTrigger();
  }

  componentWillUpdate() {
    // Remove the animation listener before our reference to the scoreboard container changes.
    $(this._scoreboardContainer).off('animationend');
  }

  componentDidUpdate() {
    this.scheduleKeyHintTrigger();
  }

  componentWillUnmount() {
    this.clearKeyHintTrigger();
  }

  clearKeyHintTrigger() {
    $(this._scoreboardContainer).off('animationend');
    clearTimeout(this._triggerKeyHintTimeout);
  }

  scheduleKeyHintTrigger() {
    // Component hasn't rendered yet.
    if (!this._scoreboardContainer) return;

    this.clearKeyHintTrigger();

    Promise.resolve().then(() => {
      const $scoreboardContainer = $(this._scoreboardContainer);
      if ($scoreboardContainer.css('animation') &&
          !$scoreboardContainer.css('animation').startsWith('none')
          && !$scoreboardContainer.data('animation-ended')) {
        return new Promise((resolve) => {
          $scoreboardContainer.on('animationend', () => {
            $scoreboardContainer.data('animation-ended', true);
            resolve();
          });
        });
      }
    }).then(() => {
      // TODO(jeff): Show this interval on-screen: https://github.com/wearhere/spacecontrol/issues/71
      this._triggerKeyHintTimeout = setTimeout(::this.onTriggerKeyHint, TIME_TO_STEP_SCOREBOARD_MS);
    });
  }

  onTriggerKeyHint() {
    this._keyHint.trigger();
  }

  onScoreKeyPress() {
    this.clearKeyHintTrigger();
  }

  onSubmitScore(e) {
    e.preventDefault();

    const nameInput = _.findWhere($(e.target).serializeArray(), { name: 'name' });
    const name = nameInput.value;

    // User must fill out a name.
    if (!name) return;

    this.setState({ saveInProgress: true });

    const highScore = this.scores.create({
      name,
      score: this.props.level
    }, { wait: true });

    // Don't handle errors--the players can just reset.
    highScore.once('sync', () => this.setState({
      highScore,
      saveInProgress: false
    }));
  }

  onSkipScore() {
    this.setState({ hasSkippedHighScore: true });
  }

  render() {
    const level = this.props.level;
    const { highScore, isLoaded, saveInProgress, hasSkippedHighScore } = this.state;

    // Don't show anything until the scoreboard loads.
    if (!isLoaded) return null;

    const hasSavedScore = !!highScore;
    const isHighScore = highScore || this.scores.isHighScore(level);

    const scores = this.scores.toJSON();

    const RefedScoreboardContainer = (props) => {
      return (
        <div className='scoreboard' ref={(el) => this._scoreboardContainer = el} {..._.omit(props, 'children')}>
          {props.children}
        </div>
      );
    };

    const RefedKeyHint = (props) => {
      return (
        <KeyHint ref={(el) => this._keyHint = el} {..._.omit(props, 'children')}>
          {props.children}
        </KeyHint>
      );
    };

    if (hasSavedScore || hasSkippedHighScore) {
      // Immediately transition to the scoreboard.
      return (
        <RefedScoreboardContainer data-end-scroll='other-scores-including-player'>
          <Scoreboard scores={scores}/>

          <RefedKeyHint triggerKey=' '>Hit space bar to reset</RefedKeyHint>
        </RefedScoreboardContainer>
      );
    } else {
      return (
        <RefedScoreboardContainer data-end-scroll={isHighScore ? 'player-score' : 'other-scores'}>
          {isHighScore ? (
            <div>
              <h2 className='player-score'>You made it to level {level}</h2>

              <NewHighScoreForm disabled={saveInProgress}
                onKeyPress={::this.onScoreKeyPress}
                onSubmit={::this.onSubmitScore}
                onEscape={::this.onSkipScore}/>

              <RefedKeyHint triggerKey='Escape'>Hit escape key to skip</RefedKeyHint>
            </div>
          ) : (
            <div>
              <h2 className='player-score'>You made it to level {level}</h2>

              <Scoreboard scores={scores}/>

              <RefedKeyHint triggerKey=' '>Hit space bar to reset</RefedKeyHint>
            </div>
          )}
        </RefedScoreboardContainer>
      );
    }
  }
}

class NewHighScoreForm extends React.Component {
  onKeyDown(e) {
    if ((e.key === 'Escape') && this.props.onEscape) {
      e.stopPropagation();

      this.props.onEscape();
    }
  }

  render() {
    return (
      <div className='new-high-score'>
        <h3>New high score!</h3>

        <form onKeyDown={::this.onKeyDown} onKeyPress={this.props.onKeyPress} onSubmit={this.props.onSubmit}>
          <NameInput disabled={this.props.disabled} name='name' focus/>
        </form>
      </div>
    );
  }
}

class NameInput extends React.Component {
  componentDidMount() {
    if (this.props.focus) this.input.focus();

    this._flashPlaceholderInterval = setInterval(() => $(this.input).toggleClass('flash-white'), 650);
  }

  componentWillUnmount() {
    clearInterval(this._flashPlaceholderInterval);
  }

  render() {
    return (
      <input
        disabled={this.props.disabled}
        ref={(input) => this.input = input}
        name={this.props.name}
        type="text"
        placeholder='Enter your name'
      />
    );
  }
}

function Scoreboard(props) {
  return (
    <div>
      <h3>All-time spaceteams:</h3>

      <table>
        <tbody>
          {props.scores.map(({ id, name, score }) => {
            return (
              <tr key={id}>
                <td>{name}</td>
                <td>{score}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
