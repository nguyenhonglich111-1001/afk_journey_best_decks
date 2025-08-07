import random
from typing import Dict, Callable
from .base_crafting import BaseCrafting, State

class AlchemyCrafting(BaseCrafting):
    """
    Implements the logic for the 'Alchemy' crafting type.
    """
    def _get_highest_color(self, state: State) -> str:
        """Returns the name of the color with the highest score."""
        return 'yellow' if state['yellow'] >= state['blue'] else 'blue'

    def _get_lowest_color(self, state: State) -> str:
        """Returns the name of the color with the lowest score."""
        return 'yellow' if state['yellow'] <= state['blue'] else 'blue'

    def _apply_enchant_debuff(self, state: State):
        """Applies the debuff from previously played Enchant cards."""
        debuff_stacks = state.get('enchant_debuff', 0)
        for _ in range(debuff_stacks):
            color = self._get_random_color()
            state[color] = max(1, state[color] - 1) # Ensure score doesn't go below 1

    def _apply_warmdust_deck_buff(self, state: State):
        """Applies the buff for the Warmdust-Deck item."""
        if state.get("warmdust_deck_buff", False):
            lowest_color = self._get_lowest_color(state)
            state[lowest_color] += 1

    def _apply_calming_warmdust_deck_buff(self, state: State):
        """Applies the buff for the Calming Warmdust-deck item."""
        if state.get("calming_warmdust_deck_buff", False):
            highest_color = self._get_highest_color(state)
            state[highest_color] += 3

    def get_card_functions(self) -> Dict[str, Callable[[State], State]]:
        """Maps alchemy card names to their specific functions."""
        return {
            "Ingredient": self.ingredient,
            "Grind": self.grind,
            "Enchant": self.enchant,
            "Distill": self.distill,
        }

    # --- Card Function Implementations ---

    def ingredient(self, state: State) -> State:
        """Highest color +10. Lowest color -2."""
        self._apply_enchant_debuff(state)
        self._apply_warmdust_deck_buff(state)
        self._apply_calming_warmdust_deck_buff(state)
        highest_color = self._get_highest_color(state)
        lowest_color = self._get_lowest_color(state)
        state[highest_color] += 10
        state[lowest_color] = max(1, state[lowest_color] - 2)
        return state

    def grind(self, state: State) -> State:
        """Lowest color +4. Highest color -2"""
        self._apply_enchant_debuff(state)
        self._apply_warmdust_deck_buff(state)
        self._apply_calming_warmdust_deck_buff(state)
        highest_color = self._get_highest_color(state)
        lowest_color = self._get_lowest_color(state)
        state[lowest_color] += 4
        state[highest_color] = max(1, state[highest_color] - 2)

        return state

    def enchant(self, state: State) -> State:
        """Lowest color +8; increments future card debuff."""
        # Apply debuff from any previously played Enchant cards first.
        self._apply_enchant_debuff(state)
        self._apply_warmdust_deck_buff(state)
        self._apply_calming_warmdust_deck_buff(state)
        # Now, apply this card's effect.
        lowest_color = self._get_lowest_color(state)
        state[lowest_color] += 8
        state['enchant_debuff'] = state.get('enchant_debuff', 0) + 1
        return state

    def distill(self, state: State) -> State:
        """Highest color x2."""
        self._apply_enchant_debuff(state)
        self._apply_warmdust_deck_buff(state)
        self._apply_calming_warmdust_deck_buff(state)
        highest_color = self._get_highest_color(state)
        state[highest_color] *= 2
        return state
