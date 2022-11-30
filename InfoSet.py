import numpy as np

class InformationSet:
    '''
    A class representing an information set, where an information set is the set of nodes in the game-tree that are
    indistinguishable for a given player.
    '''

    def __init__(self, key, available_actions, to_string=None):
        '''
        Initializes the information set with the following variables:

            key: The unique string identifying each information set. Defined by each game.
            available_actions: An array where each index contains a token representing an action in the game.
            num_actions: The number of actions available at this information set. Equal to the length of the available
                         actions parameter.
            regret_sum: The sum of counterfactual regrets for each available action over all visits. Used to calculate
                        the next strategy. Initially zero for each action.
            strategy: The probability distribution over available actions for the current iteration. Initially equally
                      distributed probabilities for each action.
            strategy_sum: The sum of each visit’s strategy multiplied by the information set player’s reach probability.
                      Initially zero for each action.
            reach_prob: The probability of the player reaching this information set on the current iteration. Does not
                        take into account chance probabilities or the probability of opponent actions. Initially zero.
            reach_prob_sum: Accumulated probability of reaching the information set. Initially zero.
            to_string: A function used to print the information set.
        '''
        self.key = key
        self.available_actions = available_actions
        self.num_actions = len(available_actions)
        self.regret_sum = np.zeros(self.num_actions)
        self.strategy = np.repeat(1 / self.num_actions, self.num_actions)
        self.strategy_sum = np.zeros(self.num_actions)
        self.reach_prob = 0
        self.reach_prob_sum = 0
        self.to_string = to_string

    def get_strategy(self):
        '''
        Get the current strategy for the information set.
        '''
        strategy = np.where(self.regret_sum > 0, self.regret_sum, 0)
        normalizing_sum = np.sum(strategy)

        if normalizing_sum > 0:
            strategy = strategy / normalizing_sum

        else:
            strategy = np.repeat(1 / self.num_actions, self.num_actions)

        return strategy

    def get_average_strategy(self):
        '''
        Compute the average strategy of this information set. This is the computed Nash Equilibrium.
        '''
        avg_strategy = self.strategy_sum / self.reach_prob_sum if self.reach_prob_sum != 0 else self.strategy_sum
        normalizing_sum = np.sum(avg_strategy)

        if normalizing_sum > 0:
            return avg_strategy / normalizing_sum

        return np.repeat(1 / self.num_actions, self.num_actions)

    def update(self):
        '''
        Update the strategy sum, strategy, and reach probability sum, and reset the reach probability following a
        traversal of the game tree.
        '''
        self.strategy_sum += self.reach_prob * self.strategy
        self.strategy = self.get_strategy()
        self.reach_prob_sum += self.reach_prob
        self.reach_prob = 0

    def reset_regret(self):
        '''
        Zero out all negative regret values. Used by the CFR+ algorithm.
        '''
        self.regret_sum = np.where(self.regret_sum > 0, self.regret_sum, 0)

    def __str__(self):
        '''
        Print the information set.
        '''
        if self.to_string != None:
            return self.to_string(self.key)

        else:
           return self.key + ': ' + str(self.available_actions) + ': ' + str(self.get_average_strategy())