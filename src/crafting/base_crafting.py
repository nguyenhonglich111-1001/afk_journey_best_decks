import random
from abc import ABC, abstractmethod
from collections import Counter
from typing import List, Dict, Callable, Any, Tuple

# A type alias for the state dictionary used throughout the simulation.
# This makes it clear what kind of data the card functions operate on.
State = Dict[str, Any]

class BaseCrafting(ABC):
    """
    Abstract base class for a crafting type.

    It defines the interface for managing a collection of cards and their
    corresponding functions that modify a game state.
    """
    def __init__(self, card_definitions: List[Dict[str, Any]]) -> None:
        """
        Initializes the crafting type with its specific card data.

        Args:
            card_definitions (List[Dict[str, Any]]): A list of dictionaries,
                where each dictionary describes a card, its quantity, and
                other attributes.
        """
        self._card_definitions = card_definitions
        self._all_cards: List[str] = self._flatten_card_list()

    def _flatten_card_list(self) -> List[str]:
        """
        Creates a flat list of all available card names based on their quantity.

        Returns:
            List[str]: A list of card names, repeated by their quantity.
        """
        cards: List[str] = []
        for card in self._card_definitions:
            cards.extend([card['card_name']] * card['card_quantity'])
        return cards

    def get_all_cards(self) -> List[str]:
        """
        Returns the complete list of available card names for this crafting type.

        Returns:
            List[str]: The list of all cards.
        """
        return self._all_cards

    def get_card_pool_info(self) -> Counter:
        """
        Returns a readable summary of the available cards.

        Returns:
            Counter: A Counter object with card names as keys and their
                     quantities as values.
        """
        return Counter(self._all_cards)

    @abstractmethod
    def get_card_functions(self) -> Dict[str, Callable[[State], State]]:
        """
        Returns a dictionary mapping card names to their executable functions.

        This must be implemented by each subclass.

        Returns:
            Dict[str, Callable[[State], State]]: A dictionary where keys are
                card names and values are the functions that implement the
                card's logic.
        """
        pass

    def apply_end_of_cycle_effects(self, state: State, deck: Tuple[str, ...]) -> State:
        """
        Applies effects for cards that trigger at the end of the crafting process.
        Base implementation does nothing, to be overridden by subclasses.
        """
        return state

    def apply_pre_card_effects(self, state: State) -> State:
        """
        Applies any effects that should trigger before a card's main logic.
        Base implementation does nothing; to be overridden by subclasses if needed.
        """
        return state

    @staticmethod
    def _get_random_color() -> str:
        """
        Helper function to pick 'yellow' or 'blue' randomly.

        Returns:
            str: Either "yellow" or "blue".
        """
        return random.choice(['yellow', 'blue'])
