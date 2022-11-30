import numpy as np
import os
import pickle
from tqdm import tqdm

_ROOT_DIR = os.getcwd()

class Trainer:
    '''
    A class that runs a specified CFR variant on a game.
    '''

    def __init__(self, game, minimizer):
        '''
        Initializes the Trainer object.

        :param game: An implementation of the Game abstract base class.
        :param minimizer: The CFR variant to use, selected from the minimizers directory.
        '''
        self.game = game
        self.minimizer = minimizer

    def train(self, iterations=1000, display_results=True, display_freq=100, save_results=False, save_freq=100, save_dir=_ROOT_DIR):
        '''
        Runs the specified CFR minimizer on the game and attempts to solve for the games Nash equilibrium.

        :param iterations: How many iterations to run the algorithm for.
        :param display_results: If player expected values and information state average strategies should be printed before
                                the end of training.
        :param display_freq: How frequently results should be displayed.
        :param save_results: If information set objects should be saved.
        :param save_freq: How many iterations between each save.
        :param save_dir: The directory to which results should be saved.
        :return: The dictionary of all InformationSet objects and the expected game value for the first player.
        '''
        infosets = {}
        expected_game_value = 0  # The expected value the player will win following the nash equilibrium (average strategy)
        traverser = 0
        starting_node = self.game.build_game_tree()  # The GameNode object representing the root of the game tree

        for i in tqdm(range(iterations)):
            reach_probs = np.ones(self.game.num_players)
            chance_prob = 1

            if self.minimizer.ALTERNATING == True:
                expected_game_value += self.minimizer.cfr(self.game, starting_node, infosets, reach_probs, chance_prob, i + 1, traverser)

            else:
                expected_game_value += self.minimizer.cfr(self.game, starting_node, infosets, reach_probs, chance_prob, i + 1)

            self.minimizer.update(infosets)
            traverser = (traverser + 1) % 2

            if i > 0 and display_results and i % display_freq == 0:
                self._print_results(infosets, expected_game_value, (i + 1))

            if i > 0 and save_results and i % save_freq == 0:
                name = 'results_' + str(i) + '.pickle'
                path = os.path.join(save_dir, name)

                with open(path, 'wb') as file:
                    pickle.dump(infosets, file, protocol=pickle.HIGHEST_PROTOCOL)

        if save_results:
            name = 'results_final.pickle'
            path = os.path.join(save_dir, name)

            with open(path, 'wb') as file:
                pickle.dump(infosets, file, protocol=pickle.HIGHEST_PROTOCOL)

        if display_results:
            self._print_results(infosets, expected_game_value, iterations)

        return infosets, expected_game_value

    def _print_results(self, infosets, expected_game_value, num_iterations):
        '''
        Prints the expected game value for each player and the average strategy for each information set.

        :param infosets: A dictionary containing all of the InformationSet objects traversed by the Trainer.
        :param expected_game_value: The expected value of the first player.
        :param num_iterations: What iteration of training the algorithm is on.
        '''
        utility = expected_game_value / num_iterations

        print('Iteration: ', num_iterations)
        print('Player 1 Expected Value: ', utility)
        print('Player 2 Expected Value: ', -utility)
        print()

        action_map = self.game.action_map

        for _, infoset in infosets.items():
            strategy = infoset.get_average_strategy()
            print(infoset.key, [action_map[i] + ': ' + str(strategy[np.where(infoset.available_actions == i)][0]) for i in infoset.available_actions])

        print()