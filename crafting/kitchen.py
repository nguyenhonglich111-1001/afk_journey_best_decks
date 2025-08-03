import random
from typing import Dict, Callable
from .base_crafting import BaseCrafting, State

class KitchenCrafting(BaseCrafting):
    """
    Implements the logic for the 'Kitchen' crafting type.
    """
    def get_card_functions(self) -> Dict[str, Callable[[State], State]]:
        """
        Maps Kitchen card names to their specific functions.

        Returns:
            A dictionary mapping card names to their callable functions.
        """
        return {
            "Heat Control": self.heat_control,
            "Cut": self.cut,
            "Season": self.season,
            "Slow Cook": self.slow_cook,
        }

    # --- Card Function Implementations ---

    def heat_control(self, state: State) -> State:
        """
        Random color +3. Each flip also gets a bonus from any previously
        played Slow Cook cards. Has a 50% chance to trigger again.

        Args:
            state: The current simulation state.

        Returns:
            The modified simulation state.
        """
        # Check for a bonus from previously played Slow Cook cards
        bonus_per_flip = state.get('slow_cook_bonus_per_flip', 0)

        # Initial trigger
        color = self._get_random_color()
        state[color] += (3 + bonus_per_flip)

        # Chance to re-trigger
        while random.random() < 0.5:
            color = self._get_random_color()
            state[color] += (3 + bonus_per_flip)
        return state

    def cut(self, state: State) -> State:
        """
        Adds a bonus to a random color based on the 'Cut' card's defined
        value_range in cards.json.
        - If the 'Salted Raisin' buff is active, this will always be the
          maximum value from the range.
        """
        # Find the card's definition to get its value_range
        card_def = next(
            (card for card in self._card_definitions if card['card_name'] == 'Cut'),
            None
        )
        
        # Default to a safe range if the card isn't defined for some reason
        min_val, max_val = (4, 8)
        if card_def and 'value_range' in card_def:
            min_val, max_val = card_def['value_range']

        color = self._get_random_color()
        
        if state.get('salted_raisin_buff', False):
            bonus = max_val
        else:
            bonus = random.randint(min_val, max_val)
            
        state[color] += bonus
        return state

    def season(self, state: State) -> State:
        """
        Multiplies a random color by 2.

        Args:
            state: The current simulation state.

        Returns:
            The modified simulation state.
        """
        color = self._get_random_color()
        state[color] *= 2
        return state

    def slow_cook(self, state: State) -> State:
        """
        Adds +4 to the bonus that all future Heat Control flips will receive.

        Args:
            state: The current simulation state.

        Returns:
            The modified simulation state.
        """
        state['slow_cook_bonus_per_flip'] = state.get(
            'slow_cook_bonus_per_flip', 0
        ) + 4
        return state
