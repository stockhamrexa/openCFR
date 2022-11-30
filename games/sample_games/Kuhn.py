import numpy as np
import random

from .. import Game
from .. import GameNode
from .. import UtilityNode

NUM_ACTIONS = 4 # Check, Bet, Call, Fold
NUM_PLAYERS = 2
ACTION_MAP = ['Check', 'Bet', 'Call', 'Fold']

random.seed(42)

class Utility(UtilityNode):
    '''
    Define utility at each terminal node.
    '''

    def __init__(self, utility):
        self.utility = utility
        super().__init__()

    def get_utility(self):
        return self.utility

class Kuhn(Game):
    '''
    An implementation of Kuhn poker: https://en.wikipedia.org/wiki/Kuhn_poker
    '''

    def __init__(self):
       super().__init__(NUM_ACTIONS, NUM_PLAYERS, ACTION_MAP)

    def is_chance_node(self, history):
        '''
        Returns true iff chance defines the action at this game state, else false. For example: dealing cards.
        '''
        return len(history) <= 1

    def is_terminal_node(self, history):
        '''
        Returns true iff the state is terminal, else false. A state is terminal when there are no further actions to be
        taken.
        '''
        if len(history) <= 2:
            return False

        if len(history) == 5:
            return True

        if history[-2][1] == 1: # The second to last move was a bet
            return True

        if history[-2][1] == 0 and history[-1][1] == 0: # Two checks in a row
            return True

        return False

    def handle_chance(self, history, sample=False):
        '''
        A helper function that handles behavior at a given chance node. Returns a list of chance outcomes and a list of
        probabilities corresponding to each of those outcomes. If sample is false, all possible actions at that chance
        node are returned, otherwise a user-defined subset is returned.
        '''
        cards = ['J', 'Q', 'K']
        chance_outcomes = []
        chance_probs = []

        if len(history) == 0:
            for card in cards:
                chance_outcomes.append(card)
                chance_probs.append(1 / 3)

        else:
            player1_card = history[0][1]

            for card in cards:
                if card != player1_card:
                    chance_outcomes.append(card)
                    chance_probs.append(1 / 2)

        return chance_outcomes, chance_probs

    def get_terminal_utility(self, history):
        '''
        Returns the utility at a terminal node for the player who just acted.
        '''
        cards = ['J', 'Q', 'K']
        player = self.get_player(history)
        opp_player = (player + 1) % 2

        player_card = history[0 + player][1]
        opp_player_card = history[0 + opp_player][1]

        if history[-1][1] == 3: # The last player folded
            if history[-1][0] == player:
                return -1

            return 1

        else:
            multiplier = 1 if cards.index(player_card) > cards.index(opp_player_card) else -1

            if history[-1][1] == 2 and history[-2][1] == 1: # The last player called after a bet
                return 2 * multiplier

            return multiplier

    def get_available_actions(self, history):
        '''
        Returns the actions available to a given player at the current state. The actions should be represented as a
        NumPy array.
        '''
        if len(history) == 2: # Cards have been dealt
            actions = np.array([0, 1])

        elif len(history) == 3:
            if history[-1][1] == 0:
                actions = np.array([0, 1])

            else:
                actions = np.array([2, 3])

        else:
            actions = np.array([2, 3])

        return actions

    def get_player(self, history):
        '''
        Returns the identifier of the player who acts in this state.
        '''
        if len(history) == 0:
            return 0

        last_turn = history[-1]

        if last_turn[0] == 0:
            return 1

        return 0

    def get_infoset_key(self, history):
        '''
        Returns a string representation of the game history to be used as a unique information set key.
        '''
        player = self.get_player(history)
        card = history[player][1]
        infoset = card

        for action in history:
            if action[0] != 'r':
                infoset += '-' + str(action[1])

        return infoset

    def build_game_tree(self, history=[]):
        '''
        Recursively builds a game tree consisting of GameNode objects.
        '''
        player = self.get_player(history)
        is_chance_node = self.is_chance_node(history)
        is_terminal_node = self.is_terminal_node(history)

        if is_terminal_node:
            print(history)
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