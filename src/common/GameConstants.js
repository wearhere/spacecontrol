// The various states of the game.
const GAME_STATE = {
  WAITING_FOR_PLAYERS: 0,
  WAITING_TO_START: 1,
  STARTED: 2
};

// How long before the sun appears on the starfield.
const SUN_DELAY_MS = 30 * 1000;

// How much to advance the sun across the starfield when the timer fires. This doesn't affect the
// appearance of the sun's advance assuming that we linearly animate increments using a duration of
// `SUN_UPDATE_INTERVAL_MS`. *However*, the greater this increment is, the less time the player has
// before the sun catches up to the spaceship, because on the last increment, the sun's position
// will immediately catch up to the spaceship (before it animates to that position), and with larger
// increments there will be fewer increments.
const SUN_PROGRESS_INCREMENT = 5;

// How often to update the sun's progress across the starfield.
const SUN_UPDATE_INTERVAL_MS = 5000;

// Start the sun off _behind_ the spaceship, since when they catch each other that's it for the
// player.
const SUN_INITIAL_PROGRESS = -((SUN_DELAY_MS / SUN_UPDATE_INTERVAL_MS) * SUN_PROGRESS_INCREMENT);

// The time additional players are given to join the game after the first player has joined
// before the game starts.
const TIME_TO_START_MS = 10 * 1000;

// The time players are given to perform commands before the command is replaced and the ship slides
// backwards. During the game this is done for time pressure. Before the game this is done so that
// if a player can't figure out how to perform a command, they're not prevented from joining the
// game, they can just wait for the next command. To give them time to figure out how the game
// works, they get double the time to perform before the game starts.
function timeToPerformMs(state = GAME_STATE.STARTED) {
  let baseTime = 5 * 1000;
  if (state !== GAME_STATE.STARTED) {
    baseTime *= 2;
  }
  return baseTime;
}

module.exports = {
  GAME_STATE,
  SUN_INITIAL_PROGRESS,
  SUN_PROGRESS_INCREMENT,
  SUN_UPDATE_INTERVAL_MS,
  TIME_TO_START_MS,
  timeToPerformMs
};
