import $ from 'jquery';
import _ from 'underscore';
import React from 'react';
import ScoreCollection from '/models/ScoreCollection';

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

    if (hasSavedScore || hasSkippedHighScore) {
      // Immediately transition to the scoreboard.
      return (
        <div className='scoreboard' data-end-scroll='other-scores-including-player'>
          <Scoreboard scores={scores}/>
        </div>
      );
    } else {
      return (
        <div className='scoreboard' data-end-scroll={isHighScore ? 'player-score' : 'other-scores'}>
          {isHighScore ? (
            <div>
              <h2 className='player-score'>You made it to level {level}</h2>

              <NewHighScoreForm disabled={saveInProgress} onSubmit={::this.onSubmitScore}
                onEscape={::this.onSkipScore}/>
            </div>
          ) : (
            <div>
              <h2 className='player-score'>You made it to level {level}</h2>

              <Scoreboard scores={scores}/>
            </div>
          )}
        </div>
      );
    }
  }
}

function NewHighScoreForm(props) {
  return (
    <div className='new-high-score'>
      <h3>New high score!</h3>

      <form onSubmit={props.onSubmit}>
        <NameInput disabled={props.disabled} name='name' onEscape={props.onEscape} focus/>
      </form>
    </div>
  );
}

class NameInput extends React.Component {
  componentDidMount() {
    if (this.props.focus) this.input.focus();

    this._flashPlaceholderInterval = setInterval(() => $(this.input).toggleClass('flash-white'), 650);
  }

  componentWillUnmount() {
    clearInterval(this._flashPlaceholderInterval);
  }

  onKeyDown(e) {
    e.stopPropagation();

    if ((e.key === 'Escape') && this.props.onEscape) {
      this.props.onEscape();
    }
  }

  render() {
    return (
      <input
        disabled={this.props.disabled}
        ref={(input) => this.input = input}
        name={this.props.name}
        type="text"
        placeholder='Enter your name'
        onKeyDown={::this.onKeyDown}
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
