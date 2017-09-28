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

Now, run `python panel.py` in a separate terminal. It will print a message to the console. Let's say
it says "Defenestrate the aristocracy!" Go find this message within the `controls` list in
`panel.py`. Type the `id` of the top-level dict containing it, a space, and its key within the
`actions` dict. In this case you would type "foo 1". Then press enter.

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

## So what's expected of the panels?

They should open socket connections to `localhost:8000` and communicate with the server by sending
JSON-encoding data of the below format, plus a carriage return:

```
{ "message": "a string", "data": <any JSON-serializable data> } + "\r"
```

They should maintain a list of the controls attached to the panel, in the format shown
at the top of `panel.py`. They should update this list as controls connect/disconnect, and
call `announce` each time after updating the list. This will cause the server to recalculate
what commands are available to it.

(This means that we won't have to babysit this setup, it can cope with controls or even
entire panels dropping out.)

When an event with `message: 'display'` is received, the panel should display the value of
`data.display` on its attached display&mdash;this is the command for the player to perform.

When a control is manipulated, the panel should send an event like

```
{ "message": "set-state", "data": { "id": <the ID of the control that changed>, "state": <the control's new state> } }
```

## Questions or concerns?

_The C&C server is in Node?_ It's an extremely good fit due to the highly event-driven
nature of this application, reading and writing to the panels and to the web UI. I can
say from experience that this will be able to handle many many socket connections without
falling over or even slowing. It also simplifies the development environment since the
frontend is in JavaScript too.

The panels, separated as they are by the sockets, can easily be in a different language
(though I suspect that Node would simplify writing them too 🙈, see next topic).

---

_It seems that by default, reading from a socket in Python is blocking!_ This will not do:
while panels wait to receive new commands, they must also be sending updates regarding the
state of controls. I couldn't find out how to do this at least not without some extremely
verbose code, perhaps you Python folks know!

[spaceship control panels]: https://github.com/igor47/spaceboard
[latest Node]: https://nodejs.org/en/

## TODO

- Control sends timeout along with message
- Panel tells control if timeout elapses before new message
