import random
from .base_crafting import BaseCrafting

class KitchenCrafting(BaseCrafting):
    """
    Implements the logic for the 'Kitchen' crafting type.
    """
    def get_card_functions(self):
        """Maps Kitchen card names to their specific functions."""
        return {
            "Heat Control": self.heat_control,
            "Cut": self.cut,
            "Season": self.season,
            "Slow Cook": self.slow_cook,
        }

    # --- Card Function Implementations ---

    def heat_control(self, state):
        """
        Random color +3. Each flip also gets a bonus from any previously
        played Slow Cook cards. Has a 50% chance to trigger again.
        """
        # Check for a bonus from previously played Slow Cook cards
        bonus_per_flip = state.get('slow_cook_bonus_per_flip', 0)
        
        # Initial trigger
        color = self._get_random_color()
        state[color] += (3 + bonus_per_flip)
        
        # Chance to re-trigger
        while random.random() < 0.4:
            color = self._get_random_color()
            state[color] += (3 + bonus_per_flip)
        return state

    def cut(self, state):
        """Adds a random number from 4 to 8 to a random color."""
        color = self._get_random_color()
        state[color] += random.randint(4, 8)
        # state[color] += 8
        return state

    def season(self, state):
        """Multiplies a random color by 2."""
        color = self._get_random_color()
        state[color] *= 2
        return state

    def slow_cook(self, state):
        """Adds +4 to the bonus that all future Heat Control flips will receive."""
        state['slow_cook_bonus_per_flip'] = state.get('slow_cook_bonus_per_flip', 0) + 4
        return state
