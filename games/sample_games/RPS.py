import numpy as np

from .. import Game
from .. import GameNode
from .. import UtilityNode

NUM_ACTIONS = 3 # Rock, Paper, Scissors
NUM_PLAYERS = 1
ACTION_MAP = ['Rock', 'Paper', 'Scissors']

class Utility(UtilityNode):
    '''
    Define utility at each terminal node.
    '''

    def __init__(self, utility):
        self.utility = utility
        super().__init__()

    def get_utility(self):
        return self.utility

class RPS(Game):
    '''
    Rock-Paper-Scissors
    '''

    def __init__(self, opp_strategy = np.repeat(1 / 3, 3)):
        super().__init__(NUM_ACTIONS, NUM_PLAYERS, ACTION_MAP)
        self.opp_strategy = opp_strategy

    def is_chance_node(self, history):
        '''
        Returns true iff chance defines the action at this game state, else false. For example: dealing cards.
        '''
        if len(history) == 1:
            return True

        return False

    def is_terminal_node(self, history):
        '''
        Returns true iff the state is terminal, else false. A state is terminal when there are no further actions to be
        taken.
        '''
        return len(history) == 2

    def handle_chance(self, history, sample=False):
        '''
        A helper function that handles behavior at a given chance node. Returns a list of chance outcomes and a list of
        probabilities corresponding to each of those outcomes. If sample is false, all possible actions at that chance
        node are returned, otherwise a user-defined subset is returned.
        '''
        chance_outcomes = np.arange(self.num_actions)
        chance_probs = self.opp_strategy

        return chance_outcomes, chance_probs

    def get_terminal_utility(self, history):
        '''
        Returns the utility at a terminal node for the player who just acted.
        '''
        action = history[-2][1]
        opp_action = history[-1][1]
        utility = np.zeros(self.num_actions)
        utility[opp_action] = 0
        utility[(opp_action + 1) % self.num_actions] = 1
        utility[(opp_action + 2) % self.num_actions] = -1

        return utility[action]

    def get_available_actions(self, history):
        '''
        Returns the actions available to a given player at the current state. The actions should be represented as a
        NumPy array.
        '''
        return np.arange(self.num_actions)

    def get_player(self, history):
        '''
        Returns the identifier of the player who acts in this state.
        '''
        return 0

    def get_infoset_key(self, history):
        '''
        Returns a string representation of the game history to be used as a unique information set key.
        '''
        return 'Shoot'

    def build_game_tree(self, history=[]):
        '''
        Recursively builds a game tree consisting of GameNode objects.
        '''
        player = self.get_player(history)
        is_chance_node = self.is_chance_node(history)
        is_terminal_node = self.is_terminal_node(history)

        if is_terminal_node:
            terminal_utility = self.get_terminal_utility(history)
            utility_node = Utility(terminal_utility)

            return GameNode(history, player, is_terminal_node=True, terminal_utility=utility_node)

        elif is_chance_node:
            chance_outcomes, chance_probs = self.handle_chance(history)
            next_nodes = []

            for outcome in chance_outcomes:
                next_history = history + [('r', outcome)]
                next_nodes.append(self.build_game_tree(history=next_history))

            return GameNode(history, player, next_nodes, is_chance_node=True, chance_outcomes=chance_outcomes, chance_probs=chance_probs)

        else:
            available_actions = self.get_available_actions(history)
            next_nodes = []

            for action in available_actions:
                next_history = history + [(player, action)]
                next_nodes.append(self.build_game_tree(history=next_history))

            return GameNode(history, player, next_nodes, available_actions)