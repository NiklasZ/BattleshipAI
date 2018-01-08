# BattleShipAI

This is my submission to battleship challenge by aigaming.com, submitted on the 08.01.2018. It composes 3 bots that can play the game [battleship](https://en.wikipedia.org/wiki/Battleship_(game)) in aigaming's [battleship competition](https://www.aigaming.com/GameInfo/GameTypes?type=51). Each bot is an incremental improvement and are called (from weakest, to strongest):

1. Bouillabaisse - bot that uses probabilistic targeting and completely randomised placement.
2. Gazpacho - bot that uses probabilistic targeting and well-spaced randomised placement.
3. Pho - bot that uses heuristic-driven targeting and well-spaced randomised placement.

The application also features additional functions:
* a GUI client provided by aigaming that connects to their server and visualises games in action.
* a training algorithm that adapts heuristics to opponent's playstyles.
* a logging function that stores games for training.

## Getting Started

To run the bot

### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Installing

A step by step series of examples that tell you have to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## How does it work?

## Running the tests

Coming soon.

## Authors

* [NiklasZ](https://github.com/NiklasZ)

## Acknowledgments

* aigaming.com for providing the [client](https://www.aigaming.com/Help?url=downloads), composed of UI and request handling.
* [Paul Knysh](https://github.com/paulknysh/blackbox), for their a black box function optimisation algorithm.
