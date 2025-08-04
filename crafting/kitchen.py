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
        Random color +3. Each flip also gets a bonus to both colors from any
        previously played Slow Cook cards. Has a 50% chance to trigger again.
        """
        all_color_bonus = state.get('slow_cook_all_color_bonus', 0)

        def _trigger_flip():
            # Apply the bonus to both colors
            state['yellow'] += all_color_bonus
            state['blue'] += all_color_bonus
            # Apply the base card effect to a random color
            color = self._get_random_color()
            state[color] += 3

        # Initial trigger
        _trigger_flip()

        # Chance to re-trigger
        while random.random() < 0.5:
            _trigger_flip()
            
        Random color +3. Re-triggers based on a self-correcting PRD system
        defined in cards.json that persists across a deck's evaluation.
        """
        # --- 1. Get PRD Parameters and Persistent History ---
        card_def = next((c for c in self._card_definitions if c['card_name'] == 'Heat Control'), {})
        prd_config = card_def.get('prd_config', {})
        
        base_chance = prd_config.get('base_chance', 0.5)
        target_average = prd_config.get('target_average', 1.0)
        correction_factor = prd_config.get('correction_factor', 1.0)
        max_attempts = prd_config.get('max_attempts', 10)

        prd_history = state.get('prd_history', {'hc_plays': 0, 'hc_successes': 0})
        
        # --- 2. Calculate the Adjusted Chance for this Card Play ---
        current_plays = prd_history.get('hc_plays', 0)
        current_successes = prd_history.get('hc_successes', 0)

        if current_plays > 0:
            current_average = current_successes / current_plays
            deviation = current_average - target_average
            adjusted_chance = base_chance - (deviation * correction_factor)
        else:
            # For the very first play, use the base chance.
            adjusted_chance = base_chance
            
        # Clamp the chance to a reasonable range (e.g., 5% to 95%)
        adjusted_chance = max(0.05, min(0.95, adjusted_chance))

        # --- 3. Execute the Card's Core Logic ---
        bonus_per_flip = state.get('slow_cook_bonus_per_flip', 0)
        
        # Initial trigger always happens
        color = self._get_random_color()
        state[color] += (3 + bonus_per_flip)
        
        # Re-trigger loop using the adjusted chance
        successes_this_card = 0
        for _ in range(max_attempts):
            if random.random() < adjusted_chance:
                successes_this_card += 1
                color = self._get_random_color()
                state[color] += (3 + bonus_per_flip)
            else:
                # The chain is broken on the first failure.
                break
        
        # --- 4. Update the Persistent History ---
        prd_history['hc_plays'] = current_plays + 1
        prd_history['hc_successes'] = current_successes + successes_this_card
        
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
        Adds +2 to the bonus that all future Heat Control flips will receive
        for both colors. This effect stacks.
        """
        state['slow_cook_all_color_bonus'] = state.get('slow_cook_all_color_bonus', 0) + 2
        return state
