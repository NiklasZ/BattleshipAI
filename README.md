# BattleShipAI

This is my submission to battleship challenge by aigaming.com, submitted on the 08.01.2018. It composes 3 bots that can play the game [battleship](https://en.wikipedia.org/wiki/Battleship_(game)) in aigaming's [battleship competition](https://www.aigaming.com/GameInfo/GameTypes?type=51). Each bot is an incremental improvement and are called (from weakest, to strongest):

1. Bouillabaisse - bot that uses probabilistic targeting and completely randomised placement.
2. Gazpacho - bot that uses probabilistic targeting and well-spaced randomised placement.
3. Pho - bot that uses heuristic-driven targeting and well-spaced randomised placement.

The application also features additional functions:
* a GUI client provided by aigaming that connects to their server and visualises games in action.
* a training algorithm that adapts heuristics to opponent's playstyles.
* a logging function that stores games for training.
* an (optional) plotting function that allows displaying bot performance.

## Getting Started

The application is in source and not packaged. It can be run for testing purposes by following the below sections.

### Prerequisites

To run the application, you require Python 3.6 or newer and the following libraries (most easily installed via [PIP](https://pypi.python.org/pypi/pip)):

```
pip install numpy
pip install scipy
pip install requests
```

and optionally (if the plotting is of interest):

```
pip install pandas
pip install matplotlib
```

### Installing

The application does not have any installer that needs to be run. Simply navigate to `project` and run:

```
python src
```

This will load the basic client and should look like the following:

![alt text](https://github.com/NiklasZ/BattleshipAI/edit/master/readme_assets/blank_client.png)


## How does it work?

## Running the tests

Coming soon.

## Authors

* [NiklasZ](https://github.com/NiklasZ)

## Acknowledgments

* [https://www.aigaming.com/](aigaming.com) for providing the [client](https://www.aigaming.com/Help?url=downloads), composed of UI and request handling.
* [Paul Knysh](https://github.com/paulknysh), for their [black box function optimisation algorithm](https://github.com/paulknysh/blackbox).
