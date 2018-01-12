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

![alt text](https://github.com/NiklasZ/BattleshipAI/blob/master/readme_assets/blank_client.png)

If this works, then try to run the following configuration against the master-bot:

```
python src --botid pho --password a_password --gamestyle 103 --dontplaysameuserbot --trainbot  --heuristics ship_adjacency
```

This should initialise the bot Pho to play a game of style 103 (land-based) against whichever opponent offers on the aigaming server.

If you want to use the bot without the server and GUI you can also just create a script like the following:
 
 ```python
 
 # Project imports
import src.ai.ai as ai
import src.utils.game_recorder as record
import src.utils.config_manager
 
# To initialise the bot
recorder = record.GameRecorder(game_state, bot_name)
bot = ai.AI(game_state)
bot.load_bot(bot_name, heuristic_choices=heuristic_names)
won = None
final_state = None
...

# In a game round:
for turn in game:
  move = bot.make_decision(game_state)
  # update the game_state with the move
  ...
  recorder.record_turn(game_state)
  # opponent moves
  ...
  recorder.record_turn(game_state)

# If bot wins
won = True
# If it loses
won = False

# Finally store results of match and optionally train bot.
recorder.record_end()
bot.finish_game(final_game_state, won, train_bot=train_bot)
```
## How does it work?

Details on how the bots work can be seen [here](https://github.com/NiklasZ/BattleshipAI/blob/master/AI_DOCS.md).

## Running the tests

This project does include feature tests for the AI-related components of the bots. They cover all functions in `project/src/ai/` save for those related to training (as those would be very expensive to test and not really meaningful either). The tests for each module are named `test_MODULE_NAME.py` for simplicity.

To run *all* the project tests make sure to be in the `project` directory and run `python -m unittest discover`.

Otherwise, to run a *single* test module use `python -m unittest tests.TEST_NAME`.

## Authors

* [NiklasZ](https://github.com/NiklasZ)

## Acknowledgments

* [https://www.aigaming.com/](aigaming.com) for providing the [client](https://www.aigaming.com/Help?url=downloads), composed of UI and request handling.
* [Paul Knysh](https://github.com/paulknysh), for their [black box function optimisation algorithm](https://github.com/paulknysh/blackbox).
