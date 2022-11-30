from abc import ABC, abstractmethod

class Game(ABC):
    '''
    An abstract base class that is used to define a game.
    '''

    def __init__(self, num_actions, num_players, action_map=None):
        self.num_actions = num_actions
        self.num_players = num_players

        if action_map != None:
            self.action_map = action_map

        else:
            self.action_map = ['Action ' + str(i) for i in self.num_actions]

        super().__init__()

    @abstractmethod
    def is_chance_node(self, history):
        '''
        Returns true iff chance defines the action at this game state, else false. For example: dealing cards.
        '''
        return None

    @abstractmethod
    def is_terminal_node(self, history):
        '''
        Returns true iff the state is terminal, else false. A state is terminal when there are no further actions to be
        taken.
        '''
        return None

    @abstractmethod
    def handle_chance(self, history, sample=False):
        '''
        A helper function that handles behavior at a given chance node. Returns a list of chance outcomes and a list of
        probabilities corresponding to each of those outcomes. If sample is false, all possible actions at that chance
        node are returned, otherwise a user-defined subset is returned.
        '''
        return None

    @abstractmethod
    def get_terminal_utility(self, history):
        '''
        Returns the utility at a terminal node for the player who just acted.
        '''
        return None

    @abstractmethod
    def get_available_actions(self, history):
        '''
        Returns the actions available to a given player at the current state. The actions should be represented as a
        NumPy array.
        '''
        return None

    @abstractmethod
    def get_player(self, history):
        '''
        Returns the identifier of the player who acts in this state.
        '''
        return None

    @abstractmethod
    def get_infoset_key(self, history):
        '''
        Returns a string representation of the game history to be used as a unique information set key.
        '''
        return None

    @abstractmethod
    def build_game_tree(self):
        '''
        Recursively builds a game tree consisting of GameNode objects.
        '''
        return None