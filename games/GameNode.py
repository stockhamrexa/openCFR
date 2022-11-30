class GameNode:
    '''
    A class representing a single game node.
    '''

    def __init__(self, history, player, next_nodes=[], available_actions=None, is_chance_node=False, chance_outcomes=None, chance_probs=None, is_terminal_node=False, terminal_utility=None):
        '''
        Initializes the game node with the following variables:

        history: A list of actions taken in the game, where each element of history is a (player, action) tuple. How
                 player and action are represented are game specific.
        player: The player whose turn it is to act.
        next_nodes: An array of the same length as available_actions or chance_outcomes depending on whether or not
                    is_chance_node is True. Contains an array of GameNode objects representing the next action in the
                    game.
        available_actions: An array where each index contains a token representing an action in the game.
        is_chance_node: Whether or not the node is a chance node.
        chance_outcomes: An array where each index contains a token representing a chance_action in the game.
        chance_probs: An array of the same length as chance_outcomes, where each index contains the probability of the
                      chance outcome at the same index in chance_outcomes occuring.
        is_terminal_node: Whether or not the node is a terminal node.
        terminal_utility: The terminal utility for player given the game history.
        '''
        self.history = history
        self.player = player
        self.next_nodes = next_nodes
        self.available_actions = available_actions
        self.is_chance_node = is_chance_node
        self.chance_outcomes = chance_outcomes
        self.chance_probs = chance_probs
        self.is_terminal_node = is_terminal_node
        self.terminal_utility = terminal_utility