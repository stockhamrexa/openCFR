import numpy as np
import random

from .. import Game
from .. import GameNode
from .. import UtilityNode

NUM_ACTIONS = 6 # Check, Bet 3 x Big Blind, Bet 6 x Big Blind, Bet 9 x Big Blind, Call, Fold
NUM_PLAYERS = 2
ACTION_MAP = ['Check', 'Bet_3BB', 'Bet_6BB', 'Bet_9BB', 'Call', 'Fold']

SMALL_BLIND = 1
BIG_BLIND = 2
STARTING_STACK = 36

PREFLOP_BUCKETS = ['Pair', 'Suited_Or_Connector', 'Other']
POSTFLOP_BUCKETS = ['Very_Weak', 'Weak', 'Average', 'Strong']

random.seed(42)

class StaticUtility(UtilityNode):
    '''
    Define utility at each terminal node where each call to get_utility returns the same value.
    '''

    def __init__(self, utility):
        self.utility = utility
        super().__init__()

    def get_utility(self):
        return self.utility

class DynamicUtility(UtilityNode):
    '''
    Define utility at each terminal node where each call to get_utility returns a different value.
    '''

    def __init__(self, pot_size, pot_contribution, bucket):
        self.pot_size = pot_size
        self.pot_contribution = pot_contribution
        self.bucket = bucket
        super().__init__()

    def get_utility(self):
        if self.bucket == 'Strong':
            hand = random.randint(1, 323)
            opp_hand = random.randint(1, 323)

        elif self.bucket == 'Average':
            hand = random.randint(1, 1288)
            opp_hand = random.randint(1, 1288)

        elif self.bucket == 'Weak':
            hand = random.randint(1, 1717)
            opp_hand = random.randint(1, 1717)

        else:
            hand = random.randint(1, 4138)
            opp_hand = random.randint(1, 4138)

        if hand > opp_hand:
            return self.pot_size - self.pot_contribution

        if hand < opp_hand:
            return -self.pot_contribution

        if hand == opp_hand:
            return 0

class TexasHoldEm(Game):
    '''
    An implementation of Heads Up No Limit Texas Hold-Em.
    '''

    def __init__(self, small_blind=SMALL_BLIND, big_blind=BIG_BLIND, starting_stack=STARTING_STACK):
        super().__init__(NUM_ACTIONS, NUM_PLAYERS, ACTION_MAP)
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.starting_stack = starting_stack

    def is_chance_node(self, history):
        '''
        Returns true iff chance defines the action at this game state, else false. For example: dealing cards.
        '''
        player = self.get_player(history)
        action_nodes = [i for i in history if i[0] != 'r'] # A list of all actions taken by players

        player_0_last_state, player_1_last_state = self.get_last_state(action_nodes)
        last_state, opp_last_state = (player_0_last_state, player_1_last_state) if player == 0 else (player_1_last_state, player_0_last_state)

        if len(history) <= 1: # If both players have not been dealt cards
            return True

        elif history[-1][0] == 'r' and history[-2][0] != 'r': # If only one player has had their hand strength evaluated
            return True

        elif history[-1][1] == 0 and history[-2][1] == 0: # If both players checked
            return True

        elif history[-2][1] == 4 and history[-1][1] == 0: # If the small blind opened with a call and the big blind checked
            return True

        elif history[-2][1] in [1, 2, 3] and history[-1][1] == 4: # If a player bet and the next player called
            return True

        elif last_state and opp_last_state and last_state[3] == 0 and opp_last_state[3] == 0: # If both players have bet all of their stack
            return True

        else:
            return False

    def is_terminal_node(self, history):
        '''
        Returns true iff the state is terminal, else false. A state is terminal when there are no further actions to be
        taken.
        '''
        player = self.get_player(history)
        chance_nodes = [i for i in history if i[0] == 'r']  # A list of all previously visited chance nodes
        action_nodes = [i for i in history if i[0] != 'r']  # A list of all actions taken by players

        player_0_last_state, player_1_last_state = self.get_last_state(action_nodes)
        last_state, opp_last_state = (player_0_last_state, player_1_last_state) if player == 0 else (player_1_last_state, player_0_last_state)

        if len(history) <= 2:
            return False

        elif history[-1][1] == 5: # If a player just folded
            return True

        elif 'river' in chance_nodes[-2] and 'river' in chance_nodes[-1]: # If the river has been dealt
            if history[-1][1] == 4: # If a player called
                return True

            elif history[-2][1] == 0 and history[-1][1] == 0: # If both players checked
                return True

            elif last_state[3] == 0 and opp_last_state[3] == 0: # If both players have bet their entire stack
                return True

            else:
                return False

        else:
            return False

    def handle_chance(self, history, sample=False):
        '''
        A helper function that handles behavior at a given chance node. Returns a list of chance outcomes and a list of
        probabilities corresponding to each of those outcomes. If sample is false, all possible actions at that chance
        node are returned, otherwise a user-defined subset is returned.
        '''
        chance_nodes = [i for i in history if i[0] == 'r']  # A list of all previously visited chance nodes

        if len(chance_nodes) == 0 or len(chance_nodes) == 1: # If cards are being dealt to player 0 or player 1
            return PREFLOP_BUCKETS, [156 / 2652, 912 / 2652, 1584 / 2652]

        elif len(chance_nodes) == 2 or len(chance_nodes) == 3: # If the flop is being dealt (one deal but must determine hand strength for both players)
            return POSTFLOP_BUCKETS, [.5544090056285178, .22996515679442509, .17247386759581881, .043151969981238276]

        else: # The turn or the river is being dealt
            last_bucket = chance_nodes[-2][2]

            # Hand strength bucket can never go down, only stay the same or go up
            if last_bucket == 'Very_Weak':
                return POSTFLOP_BUCKETS, [.5544090056285178, .22996515679442509, .17247386759581881, .043151969981238276]

            elif last_bucket == 'Weak':
                return ['Weak', 'Average', 'Strong'], [0.5160902255639097, 0.38706766917293234, 0.0968421052631579]

            elif last_bucket == 'Average':
                return ['Average', 'Strong'], [0.7998756991920448, 0.2001243008079553]

            else:
                return ['Strong'], [1]

    def get_terminal_utility(self, history):
        '''
        Returns the utility at a terminal node for the player who just acted.
        '''
        player = self.get_player(history)
        opp_player = (player + 1) % 2

        chance_nodes = [i for i in history if i[0] == 'r']  # A list of all previously visited chance nodes
        action_nodes = [i for i in history if i[0] != 'r']  # A list of all actions taken by players

        pot_size = action_nodes[-1][2] # The pot size after the last action was taken
        strength_bucket = chance_nodes[-2 + player][2]
        opp_strength_bucket = chance_nodes[-2 + opp_player][2]

        blind = self.small_blind if player == 0 else self.big_blind

        player_0_last_state, player_1_last_state = self.get_last_state(action_nodes)
        last_state = player_0_last_state if player == 0 else player_1_last_state

        stack_size = self.starting_stack - blind if not last_state else last_state[3]

        if action_nodes[-1][1] == 5: # If the last move was folding
            if action_nodes[-1][0] == player:
                utility = -(self.starting_stack - stack_size) # You lose what you put into the pot
                return StaticUtility(utility)

            else:
                utility =  pot_size - (self.starting_stack - stack_size) # You win what you didnt put into the pot
                return StaticUtility(utility)

        else: # If the game went to a showdown
            if POSTFLOP_BUCKETS.index(strength_bucket) > POSTFLOP_BUCKETS.index(opp_strength_bucket): # If the player had a definitively stronger hand than the opponent
                utility = pot_size - (self.starting_stack - stack_size)
                return StaticUtility(utility)

            elif POSTFLOP_BUCKETS.index(strength_bucket) < POSTFLOP_BUCKETS.index(opp_strength_bucket): # If the player had a definitively weaker hand than the opponent
                utility = -(self.starting_stack - stack_size)
                return StaticUtility(utility)

            else: # If the players hand strengths were in the same bucket
                return DynamicUtility(pot_size, self.starting_stack - stack_size, strength_bucket)

    def get_available_actions(self, history):
        '''
        Returns the actions available to a given player at the current state. The actions should be represented as a
        NumPy array.
        '''
        action_nodes = [i for i in history if i[0] != 'r']  # A list of all actions taken by players

        def get_bet_sizes(stack, opp_stack, last_opp_action):
            '''
            Determines which bet sizing buckets can be utilized on a given turn.

            :param stack: The amount of money you have available to bet
            :param opp_stack: The amount of money your opponent has available to bet
            :param last_action: The last action taken by the opponent
            :return: A list containing some subset of 1 (Bet_3BB), 2 (Bet_6BB), and 3 (Bet_9BB)
            '''
            last_bet_size = abs(stack - opp_stack) # The difference between the two stacks is the amount the player has to contribute to the pot in order to call

            if last_bet_size != 0: # Re-raise options that are available after an opponent has bet
                if last_bet_size < 3 * self.big_blind:
                    actions = [1, 2, 3]

                elif last_bet_size < 6 * self.big_blind:
                    actions = [2, 3]

                elif last_bet_size < 9 * self.big_blind:
                    actions = [3]

                else:
                    actions = []

            else: # If the player is the first one to bet in this round
                actions = [1, 2, 3]

            valid_actions = []

            for action in actions:
                stack_after_action = stack - action * 3 * self.big_blind # How large your stack will be if you take this action
                cost_to_call = opp_stack - (action * 3 * self.big_blind - last_bet_size) # The amount it will cost your opponent to call if you take this action

                if action * 3 * self.big_blind >= 2 * last_bet_size: # All raises must be twice the size of the previous raise
                    if stack_after_action >= 0 and cost_to_call >= 0: # You have enough money to take this action and your opponent has enough money to call
                        valid_actions.append(action)

                    elif action == 1 and stack > 0 and opp_stack > 0: # If you and your opponent have less than 3BB but still have money to bet
                        valid_actions.append(action)

            return valid_actions

        player = self.get_player(history)
        opp_player = (player + 1) % 2

        player_0_last_state, player_1_last_state = self.get_last_state(action_nodes)
        last_state, opp_last_state = (player_0_last_state, player_1_last_state) if player == 0 else (player_1_last_state, player_0_last_state)

        blind = self.small_blind if player == 0 else self.big_blind
        opp_blind = self.small_blind if opp_player == 0 else self.big_blind

        stack = self.starting_stack - blind if not last_state else last_state[3]
        opp_stack = self.starting_stack - opp_blind if not opp_last_state else opp_last_state[3]
        last_opp_action = None if not opp_last_state else opp_last_state[1]

        if history[-1][0] == 'r': # If the last action was dealing cards
            if history[-1][1] == 'preflop':
                actions = [5]
                actions += get_bet_sizes(stack, opp_stack, last_opp_action)

                return np.array(sorted(actions))

            else:
                actions = [0, 5]
                actions += get_bet_sizes(stack, opp_stack, last_opp_action)

                return np.array(sorted(actions))

        elif history[-1][1] == 0 or (history[-1][1] == 4 and history[-2][1] == 'preflop'): # If the last action was a check or the small blind opened with a call
            actions = [0, 5]
            actions += get_bet_sizes(stack, opp_stack, last_opp_action)

            return np.array(sorted(actions))

        else: # If the last action was a bet
            actions = [4, 5]
            actions += get_bet_sizes(stack, opp_stack, last_opp_action)

            return np.array(sorted(actions))

    def get_player(self, history):
        '''
        Returns the identifier of the player who acts in this state. Player 0 is the small blind, Player 1 is the big
        blind.
        '''
        chance_nodes = [i for i in history if i[0] == 'r']  # A list of all previously visited chance nodes
        action_nodes = [i for i in history if i[0] != 'r']  # A list of all actions taken by players

        if len(history) == 0:
            return 0

        elif history[-1][0] == 'r':
            if len(history) == 1 or history[-2][0] != 'r': # If hand strength has been computed after a deal for player 0
                return 1

            elif len(history) >= 3 and history[-1][0] == 'r' and history[-2][0] == 'r' and history[-3] == 'r': # If a showdown was reached before the river was dealt
                return action_nodes[-1][0]

            else:
                if 'preflop' in chance_nodes[-1]: # Player 0 is small blind and acts first preflop
                    return 0

                else: # Player 1 is big blind and acts first postflop
                    return 1

        else:
            if history[-1][0] == 0:
                return 1

            return 0

    def get_infoset_key(self, history):
        '''
        Returns a string representation of the game history to be used as a unique information set key.
        '''
        player = self.get_player(history)
        infoset = ''

        for i in range(len(history)):
            action = history[i]

            if len(infoset) != 0:
                prefix = '-'

            else:
                prefix = ''

            if action[0] == 'r':
                if player == 0 and (i == 0 or (history[i-1][0] != 'r' and i != 0)):
                    infoset += prefix + str(action[2])

                elif player == 1 and (i == 1 or (history[i-1][0] == 'r' and i != 0)):
                    infoset += prefix + str(action[2])

                else:
                    pass

            else:
                infoset += prefix + str(action[1])

        return infoset

    def get_last_state(self, action_nodes):
        '''
        Get the last game state of each player if one exists, else return None.
        '''
        player_0_action = None
        player_1_action = None

        for action in action_nodes:
            if action[0] == 0:
                player_0_action = action

            elif action[0] == 1:
                player_1_action = action

        return player_0_action, player_1_action

    def build_game_tree(self, history=[]):
        '''
        Recursively builds a game tree consisting of GameNode objects.
        '''
        player = self.get_player(history)
        is_chance_node = self.is_chance_node(history)
        is_terminal_node = self.is_terminal_node(history)

        chance_nodes = [i for i in history if i[0] == 'r']  # A list of all previously visited chance nodes
        action_nodes = [i for i in history if i[0] != 'r']  # A list of all actions taken by players

        player_0_last_state, player_1_last_state = self.get_last_state(action_nodes)
        last_state, opp_last_state = (player_0_last_state, player_1_last_state) if player == 0 else (player_1_last_state, player_0_last_state)

        if is_terminal_node:
            terminal_utility = self.get_terminal_utility(history)

            return GameNode(history, player, is_terminal_node=True, terminal_utility=terminal_utility)

        elif is_chance_node:
            chance_outcomes, chance_probs = self.handle_chance(history)
            next_nodes = []

            if len(chance_nodes) in [0, 1]:
                stage = 'preflop'

            elif len(chance_nodes) in [2, 3]:
                stage = 'flop'

            elif len(chance_nodes) in [4, 5]:
                stage = 'turn'

            else:
                stage = 'river'

            for outcome in chance_outcomes:
                next_history = history + [('r', stage, outcome)]
                next_nodes.append(self.build_game_tree(history=next_history))

            return GameNode(history, player, next_nodes, is_chance_node=True, chance_outcomes=chance_outcomes, chance_probs=chance_probs)

        else:
            available_actions = self.get_available_actions(history)
            next_nodes = []

            last_pot_size = self.big_blind + self.small_blind if len(action_nodes) == 0 else action_nodes[-1][2]

            if len(action_nodes) == 0:
                last_stack_size = self.starting_stack - self.small_blind
                last_opp_stack_size = self.starting_stack - self.small_blind

            elif len(action_nodes) == 1:
                last_stack_size = self.starting_stack - self.big_blind
                last_opp_stack_size = opp_last_state[3]

            else:
                last_stack_size = last_state[3]
                last_opp_stack_size = opp_last_state[3]

            for action in available_actions:
                if action == 0 or action == 5: # If the player checked or folded
                    next_history = history + [(player, action, last_pot_size, last_stack_size)]
                    next_nodes.append(self.build_game_tree(history=next_history))

                elif action == 1:
                    if last_opp_stack_size >= 3 * self.big_blind: # If the opponent has enough money to call a full bet
                        next_history = history + [(player, action, last_pot_size + 3 * self.big_blind, last_stack_size - 3 * self.big_blind)]
                        next_nodes.append(self.build_game_tree(history=next_history))

                    else: # If the opponent does not have enough to bet 3BB but has money remaining
                        next_history = history + [(player, action, last_pot_size + last_opp_stack_size, last_stack_size - last_opp_stack_size)]
                        next_nodes.append(self.build_game_tree(history=next_history))

                elif action == 2:
                    if history[-1][0] == 'r' and history[-1][1] == 'preflop': # If the small blind is opening with a bet
                        next_history = history + [(player, action, last_pot_size + (6 * self.big_blind) - self.small_blind, last_stack_size - (6 * self.big_blind) + self.small_blind)]
                        next_nodes.append(self.build_game_tree(history=next_history))

                    else:
                        next_history = history + [(player, action, last_pot_size + 6 * self.big_blind, last_stack_size - 6 * self.big_blind)]
                        next_nodes.append(self.build_game_tree(history=next_history))

                elif action == 3:
                    if history[-1][0] == 'r' and history[-1][1] == 'preflop': # If the small blind is opening with a bet
                        next_history = history + [(player, action, last_pot_size + (9 * self.big_blind) - self.small_blind, last_stack_size - (9 * self.big_blind) + self.small_blind)]
                        next_nodes.append(self.build_game_tree(history=next_history))

                    else:
                        next_history = history + [(player, action, last_pot_size + 9 * self.big_blind, last_stack_size - 9 * self.big_blind)]
                        next_nodes.append(self.build_game_tree(history=next_history))

                elif action == 4:
                    last_bet_size = abs(last_stack_size - last_opp_stack_size)

                    next_history = history + [(player, action, last_pot_size + last_bet_size, last_stack_size - last_bet_size)]
                    next_nodes.append(self.build_game_tree(history=next_history))

            return GameNode(history, player, next_nodes, available_actions)