# openCFR
A Python implementation of a variety of Counterfactual Regret Minimization (CFR) variants for finding the Nash
equilibrium of zero-sum imperfect information games. 

## Installation
To get started with **openCFR**, it is recommended that you use ```pip```:

```python
pip install openCFR
```

Alternatively, you can clone this repository and install it from source by running ```python setup.py install```.

### Requirements
This library uses:
 ```
 numpy>=1.23.2
 tqdm>=4.57.0
 ```

## Implementation Notes
This library is written in pure Python and is not yet optimized for speed or memory usage. Small games such as 
rock-paper-scissors, liars dice, and Kuhn poker perform well, but more extensive games such as heads-up no-limit 
Texas Hold-Em may be too large without bucketing game states.

## Usage

### Defining A Game
All user-generated games should inherit from the ```Game``` abstract base class, which provides a framework for defining
the rules of a game. Each ```Game``` object is initialized with three values: ```num_actions```, ```num_players```, and 
```action_map```. ```num_actions``` is the total number of unique actions available in the game. In rock-paper-scissors,
this would be three. ```num_players``` is the number of players in the game. **Note**: The behavior of each CFR variant
is currently untested for greater than two players. ```action_map``` is a list of strings with a length equal to
```num_actions```. Each action ```i``` is mapped to the string at ```action_map[i]```. In rock-paper-scissors, 
```action_map=['Rock', 'Paper', 'Scissors']```.

The ```Game``` abstract base class requires the implementation of the following functions:
- ```is_chance_node(history)```: Returns true iff chance defines the action at this game state, else false. For example,
dealing cards.
- ```is_terminal_node(history)```: Returns true iff the state is terminal, else false.
- ```handle_chance(history)```: Defines behavior at chance nodes. Returns a list of possible outcomes and a list of the
probability of those outcomes
- ```get_terminal_utility(history)```: Returns the utility at a terminal node for the player who just acted.
- ```get_available_actions(history)```: Returns the actions available to a given player at the current state.
- ```get_player(history)```: Returns the identifier of the player who acts in this state.
- ```get_infoset_key(history)```: Converts the game history to a string containing only events in the history seen by
the player whose turn it is to act.
- ```build_game_tree()```: Recursively builds a game tree consisting of GameNode objects. Starts with an empty history
and utilizes the above functions to iterate through the full game.

There are many ways to structure your games ```history```. However, in the sample games provided by this library, it is
structured as a list of tuples. Below are all of the possible histories at terminal game states for Kuhn poker:

```python
[('r', 'J'), ('r', 'Q'), (0, 0), (1, 0)]
[('r', 'J'), ('r', 'Q'), (0, 0), (1, 1), (0, 2)]
[('r', 'J'), ('r', 'Q'), (0, 0), (1, 1), (0, 3)]
[('r', 'J'), ('r', 'Q'), (0, 1), (1, 2)]
[('r', 'J'), ('r', 'Q'), (0, 1), (1, 3)]
[('r', 'J'), ('r', 'K'), (0, 0), (1, 0)]
[('r', 'J'), ('r', 'K'), (0, 0), (1, 1), (0, 2)]
[('r', 'J'), ('r', 'K'), (0, 0), (1, 1), (0, 3)]
[('r', 'J'), ('r', 'K'), (0, 1), (1, 2)]
[('r', 'J'), ('r', 'K'), (0, 1), (1, 3)]
[('r', 'Q'), ('r', 'J'), (0, 0), (1, 0)]
[('r', 'Q'), ('r', 'J'), (0, 0), (1, 1), (0, 2)]
[('r', 'Q'), ('r', 'J'), (0, 0), (1, 1), (0, 3)]
[('r', 'Q'), ('r', 'J'), (0, 1), (1, 2)]
[('r', 'Q'), ('r', 'J'), (0, 1), (1, 3)]
[('r', 'Q'), ('r', 'K'), (0, 0), (1, 0)]
[('r', 'Q'), ('r', 'K'), (0, 0), (1, 1), (0, 2)]
[('r', 'Q'), ('r', 'K'), (0, 0), (1, 1), (0, 3)]
[('r', 'Q'), ('r', 'K'), (0, 1), (1, 2)]
[('r', 'Q'), ('r', 'K'), (0, 1), (1, 3)]
[('r', 'K'), ('r', 'J'), (0, 0), (1, 0)]
[('r', 'K'), ('r', 'J'), (0, 0), (1, 1), (0, 2)]
[('r', 'K'), ('r', 'J'), (0, 0), (1, 1), (0, 3)]
[('r', 'K'), ('r', 'J'), (0, 1), (1, 2)]
[('r', 'K'), ('r', 'J'), (0, 1), (1, 3)]
[('r', 'K'), ('r', 'Q'), (0, 0), (1, 0)]
[('r', 'K'), ('r', 'Q'), (0, 0), (1, 1), (0, 2)]
[('r', 'K'), ('r', 'Q'), (0, 0), (1, 1), (0, 3)]
[('r', 'K'), ('r', 'Q'), (0, 1), (1, 2)]
[('r', 'K'), ('r', 'Q'), (0, 1), (1, 3)]
```

In the above histories, chance events are formatted as ```('r', chance_outcome)```, and all other events are formatted
as ```(player, action_taken)```, where the ```action_map``` in Kuhn poker is ```['Check', 'Bet', 'Call', 'Fold']```.


### Defining Utility
In order for the provided implementations of CFR to work correctly, the utility at a terminal node in the game tree 
should be represented by an object with a ```get_utility()``` function. This library provides the ```UtilityNode```
abstract base class to inherit. The two primary use cases for a utility node are static utility and dynamic utility:

- Static Utility: The returned utility will be the same for every traversal through the game tree. For example, in
rock-paper-scissors if player 1 throws rock and player 2 throws scissors, player 1's utility will always be 1 and
player 2's utility will always be -1.

```python
from games import UtilityNode


class StaticUtility(UtilityNode):
  '''
  Define utility at each terminal node where each call to get_utility returns the same value.
  '''

  def __init__(self, utility):
    self.utility = utility
    super().__init__()

  def get_utility(self):
    return self.utility
```

- Dynamic Utility: The returned utility will be different for every traversal through the game tree as the result of a
random outcome. For example, in a Texas Hold-em game tree which utilizes bucketing for hand strength, if player 1 and
player 2 both have a hand strength that is in the same bucket, the ```get_utility()``` function will randomly select
which of the two players won that hand.

```python
from games import UtilityNode


class DynamicUtility(UtilityNode):
  '''
  Define utility at each terminal node where each call to get_utility returns a different value.
  '''

  def __init__(self, player, utility):
    self.player = player
    self.utility = utility
    super().__init__()

  def get_utility(self):
    wins = some_random_event

    if self.player == wins:
      return self.utility

    return -self.utility
```

### Building A Game Tree
Once the rules of your game have been defined, to build the game tree call ```game.build_game_tree()```. The return
value of this function will be a ```GameNode``` object representing the root of your game tree.

### Sample Games
This library comes with three pre-defined sample games:
- Rock-Paper-Scissors
    ```python
    from games.sample_games import RPS
    game = RPS()
    game_tree = game.build_game_tree()
    ```
- Kuhn Poker
    ```python
    from games.sample_games import Kuhn
    game = Kuhn()
    game_tree = game.build_game_tree()
    ```
- Heads-Up No-Limit Texas Hold-Em
    ```python
    from games.sample_games import TexasHoldEm
    game = TexasHoldEm(small_blind, big_blind, starting_stack)
    game_tree = game.build_game_tree()
    ```
  
The Nash Equilibrium for each of these sample games has been computed using the CFR+ algorithm for 100,000 iterations
and are avilable for use in the *OpenCFR/pretrained/* directory.

### Selecting A Minimizer
This library has implemented five variants of the Counterfactual Regret Minimization algorithm:
- Vanilla CFR
    ```python

from src.minimizers import VanillaCFR
    ```
- CFR+
    ```python

from minimizers import CFRPlus
    ```
- CFR with regret based pruning
    ```python
    from minimizers import RBP_CFR
    ```
- Monte-Carlo CFR with external sampling
    ```python

from minimizers import MCCFR_External
    ```
- Monte-Carlo CFR with outcome sampling
    ```python

from src.minimizers import MCCFR_Outcome
    ```

### Finding A Nash Equilibrium
Once you have defined a game and selected a minimizer, you can begin training:

```python
from games import *
from minimizers import *
from Trainer import Trainer

game = TexasHoldEm(small_blind=2, big_blind=4, starting_stack=50)
minimizer = CFRPlus
trainer = Trainer(game=game, minimizer=minimizer)

infosets, expected_utility = trainer.train(iterations=10000, display_results=False, save_results=True, save_freq=10)
```

When traversing the game tree, the minimzer builds a dictionary of ```InfoSet``` objects, whose key is generated
by calling ```game.get_infoset_key(history)```. Each information set represents a set of nodes in the game tree
which are indistinguishable for a given player. To get the Nash equilibrium for an information set ```i```, call
```i.get_average_strategy()```. This dictionary of InfoSet objects is what is saved while training.

## Performance
The table below shows the performance of each algorithm as evaluated on Kuhn poker, where one iteration is a full
traversal of the game tree.

| CFR Variant                            | Iterations/Second |
|----------------------------------------|-------------------|
| Vanilla CFR                            | ~1100 it/s        |
| CFR+                                   | ~1100 it/s        |
| CFR with regret based pruning          | ~850 it/s         |
| Monte Carlo CFR with external sampling | ~2100 it/s        |
| Monte Carlo CFR with outcome sampling  | ~2300 it/s        |

## License
Copyright (c) 2022, Rex Stockham

Distributed under the [MIT License](https://mit-license.org/)

See the accompanying LICENSE.txt file for licensing, copyright, and warranty terms. All files in this repo are subject
to those terms and by using this software you are agreeing to those terms.