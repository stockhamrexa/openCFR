import numpy as np

from ..InfoSet import InformationSet

ALTERNATING = True # Whether player regrets are updated successively or alternatingly

def update(infosets):
    '''
    Update the strategy sum, strategy, and reach probability sum, and reset the reach probability for each
    InformationSet following a traversal of the game tree.
    '''
    for _, infoset in infosets.items():
        infoset.update()
        infoset.reset_regret()

    return infosets

def cfr(game, game_node, infosets, reach_probs, chance_prob, iteration, traverser):
    '''
    The CFR+ counterfactual regret minimization algorithm.

    :param game: An implementation of the Game abstract base class.
    :param game_node: A GameNode object representing the current state of the game.
    :param infosets: A dictionary mapping information set keys to an InformationSet object. The key has the same values
                     as InformationSet.key.
    :param reach_probs: The probability contribution of each player to reaching the current game state, indexed by
                        player.
    :param chance_prob: The probability contribution of chance events to reaching the current game state.
    :param iteration: How many iterations of CFR have been run.
    :param traverser: The player who is traversing the game tree. Regret is only updated for information states this player visits.
    :return: The utility of the first player for the single traversal of the game tree.
    '''
    if game_node.is_chance_node: # If the game is at a chance node
        expected_value = 0

        for i in range(len(game_node.next_nodes)): # Sample every possible chance outcome
            next_node = game_node.next_nodes[i]
            chance = game_node.chance_probs[i]

            expected_value += chance * cfr(game, next_node, infosets, reach_probs, chance_prob * chance, iteration, traverser)

        return expected_value

    if game_node.is_terminal_node: # If the game is at a terminal node
        return game_node.terminal_utility.get_utility()

    infoset_key = game.get_infoset_key(game_node.history)
    available_actions = game_node.available_actions

    if infoset_key not in infosets: # Create a new InformationSet object if this is a new game state
        infoset = InformationSet(infoset_key, available_actions)
        infosets[infoset_key] = infoset

    else:
        infoset = infosets[infoset_key]

    player = game_node.player

    if player == traverser:
        infoset.reach_prob += reach_probs[player]

    action_utils = np.zeros(len(available_actions))
    strategy = infoset.strategy

    for i in range(len(game_node.next_nodes)): # Sample every possible action
        next_node = game_node.next_nodes[i]
        next_reach_probs = reach_probs.copy()
        next_reach_probs[player] *= strategy[i]
        utility_multiplier = 1 if game.num_players == 1 or player == next_node.player else -1
        action_utils[i] = utility_multiplier * cfr(game, next_node, infosets, next_reach_probs, chance_prob, iteration, traverser)

    util = np.sum(action_utils * strategy)
    regrets = action_utils - util
    opp_contribution = np.prod(reach_probs) / (reach_probs[player] if reach_probs[player] != 0 else 1)

    if player == traverser:
        infoset.regret_sum += opp_contribution * chance_prob * regrets  # Update the regret sum

    return util