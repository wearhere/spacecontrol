# spacecontrol

This is a command-and-control server for [spaceship control panels], actually three servers
in one:

* a web server, to display the game's central UI to players
* a websocket server, to update that UI in realtime
* a socket server, to message the control panels

It also includes a simulation of a panel to guide the development of the
[actual panel software][spaceship control panels].

## Installation

Install the [latest Node] (v8.5.0 at the time of this writing).

Then run `npm install` in this directory.

The panel simulation has been tested using Python 2.7.13 i.e. the default version of Python
built into OS X 10.12.6. I dunno if it works with Python 3&mdash;hopefully yes!

## Usage

Run `npm start`. This will:

* start the web and websocket servers on port 3000 (port can be changed via the `WEB_PORT` environment variable)
* start the socket server on port 8000 (port can be changed via the `PANEL_PORT` environment variable)

These servers will live-reload if you make changes to any relevant files whether client or
server. Press Ctrl-C to kill all the servers.

Visit `http://localhost:3000` in your browser. You will see a glorious "spaceship".

Now, run `python panels/run_panel.py` in a separate terminal. It will print the list of controls that are
available, followed by a message. Let's say the message is "Defenestrate the aristocracy!" Go find
this message within the controls that printed at the top. Type the `id` of the top-level dict
containing it, a space, and its key within the `actions` dict. In this case you would type
"defenestrator 1". Then press enter.

You'll see "Nice job", the spaceship will move a little bit across the screen, and you'll get a new
command to perform as above.

You just acted… as a spaceteam!

More precisely:

1. The Python script opened a connection to the socket server as if a panel had suddenly
joined the local network.
2. When the "panel" joined, it announced what controls it had attached, including a button that can
be pressed (state "1") to "Defenestrate the aristocracy!"
3. The server told the panel to display to the player that they should "Defenestrate the aristocracy!"
4. You told the panel to tell the server that the button was pressed (as if you had actually pressed
a physical button).
5. Since you performed the command, you caused the spaceship to travel a little bit across the field.

Bonus: try running `python panels/run_panel.py --player_number 2` in _another_ terminal. Now you can play as two players! This
means that you may need to switch between the terminals to perform the commands! If one terminal
prints "Defenestrate the aristocracy!" but the list of controls at the top of the terminal didn't
contain that message, you'll need to enter "defenestrate 1" at the _other_ terminal.

In the real game, this part will involve the first player shouting to the other players to figure
out who can perform the command.

## So what's expected of the panels?

Panel code can be found in the panels/ directory

### Simple panel setup:

The quickest way to get started is to extend PanelStateBase. Refer to keyboard_panel.py for an example.
There are several functions you must implement:

1. `get_state_updates` - should return any changes to panel state since the last call to this function. (hint: consider using PanelStateBase.diff_states).
2. `get_controls` - should return the panel's available controls.
3. `display_message` - show a message to the user.
4. `display_status` - show a secondary, "status" message to the user. This message takes multiple
forms--see the notes on the `'set_status`' message below.

You can instead define a `panel_main` method if you prefer to run arbitrary code (see next section).

### In-depth/roll your own

Panels should open socket connections to `localhost:8000` and communicate with the server by sending
JSON-encoding data. The beginning of a message should contain a 32-bit unsigned integer: this is the length
of the message.

```
{ "message": "a string", "data": <any JSON-serializable data> }
```

See `panel_client._encode()` for an example.

They should maintain a list of the controls attached to the panel, in the format shown
at the top of `keyboard_panel.py`. If your panel can detect controls going up/down, then it should
call `announce` each time available controls change. This will cause the server to recalculate
what commands are available to it.

(This means that we won't have to babysit this setup, it can cope with controls or even
entire panels dropping out.)

When an event with `message: 'set-display'` is received, the panel should display the value of
`data.message` on its attached display&mdash;this is the command for the player to perform.

When an event with `message: 'set-status'` is received:

* if `data` contains the key `message`, the panel should display `data['message']` at the bottom of
its attached display.
* otherwise, if `data` contains the key `progress`, the panel should display a progress bar at the
bottom of its display, of width `floor(data['progress'] * LCD_WIDTH)`.

When a control is manipulated, the panel should send an event like

```
{ "message": "set-state", "data": { "id": <the ID of the control that changed>, "state": <the control's new state> } }
```

See `panel_client._make_update_message()`

## Questions or concerns?

_The C&C server is in Node?_ It's an extremely good fit due to the highly event-driven
nature of this application, reading and writing to the panels and to the web UI. I can
say from experience that this will be able to handle many many socket connections without
falling over or even slowing. It also simplifies the development environment since the
frontend is in JavaScript too.

The panels, separated as they are by the sockets, can easily be in a different language.
Python has been chosen for familiarity / availability of Raspberry Pi code snippets.

## Running in production

Both the Node server and the Python panel code will be run on Raspberry Pis, the Python code
since the control panels need to interface with the controls over serial pins, the Node server
so that we don't have to leave a laptop lying out to play the game.

The Raspberry Pis will be wired together over local Ethernet to avoid assuming that the game
venue will have reliable WiFi. The panel scripts (`panel.py`) will be launched with the
`CONTROLLER_IP` environment variable set to the static IP of the control Pi.

[spaceship control panels]: https://github.com/igor47/spaceboard
[latest Node]: https://nodejs.org/en/
