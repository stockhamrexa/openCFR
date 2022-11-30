from abc import ABC, abstractmethod

class UtilityNode(ABC):
    '''
    An abstract base class used to define a terminal utility node.
    '''

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_utility(self):
        '''
        The function that will be called when determining the utility at a terminal node. Can be defined to return the
        same value every time or sample values.

        :return: An int defining utility.
        '''
        return 0