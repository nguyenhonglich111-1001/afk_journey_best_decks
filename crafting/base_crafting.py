from abc import ABC, abstractmethod
from collections import Counter

class BaseCrafting(ABC):
    """
    Abstract base class for a crafting type.
    It defines the interface for managing cards and their functions.
    """
    def __init__(self, card_definitions):
        """
        Initializes the crafting type with its specific card data.
        
        Args:
            card_definitions (list): A list of dictionaries, where each dictionary
                                     describes a card, its quantity, and other attributes.
        """
        self._card_definitions = card_definitions
        self._all_cards = self._flatten_card_list()

    def _flatten_card_list(self):
        """Creates a flat list of all available card names based on their quantity."""
        cards = []
        for card in self._card_definitions:
            cards.extend([card['card_name']] * card['card_quantity'])
        return cards

    def get_all_cards(self):
        """Returns the complete list of available card names for this crafting type."""
        return self._all_cards
        
    def get_card_pool_info(self):
        """Returns a readable summary of the available cards."""
        return Counter(self._all_cards)

    @abstractmethod
    def get_card_functions(self):
        """
        Returns a dictionary mapping card names to their executable functions.
        This must be implemented by each subclass.
        """
        pass

    @staticmethod
    def _get_random_color():
        """Helper function to pick 'yellow' or 'blue' randomly."""
        import random
        return random.choice(['yellow', 'blue'])
