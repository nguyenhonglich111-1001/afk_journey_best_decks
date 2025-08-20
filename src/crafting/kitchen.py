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
            "Ferment": self.ferment,
        }

    # --- Card Function Implementations ---

    def ferment(self, state: State) -> State:
        """
        Activates the permanent Ferment buff, which guarantees an additional
        flip for all future Heat Control cards. Does not stack.
        """
        state['ferment_buff_active'] = True
        return state

    def heat_control(self, state: State) -> State:
        """
        Triggers a number of guaranteed flips based on the `hc_guaranteed_flips_level`
        set by Ferment cards. Each flip adds +3 to a random color and gets a
        bonus from Slow Cook.
        
        After guaranteed flips, it may re-trigger additional random flips based
        on a self-correcting PRD system.
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
            adjusted_chance = base_chance
            
        adjusted_chance = max(0.05, min(0.95, adjusted_chance))

        # --- 3. Execute the Card's Core Logic ---
        all_color_bonus = state.get('slow_cook_all_color_bonus', 0)
        successes_this_card = 0

        def _trigger_flip():
            """Applies the bonus to both colors and the base effect to one."""
            state['yellow'] += all_color_bonus
            state['blue'] += all_color_bonus
            color = self._get_random_color()
            state[color] += 10  # Base effect of +8 to a random color

        # --- 4. Perform Base and Guaranteed Flips ---
        # Heat Control always gets one base flip.
        _trigger_flip()
        successes_this_card += 1

        # It gets a second, guaranteed flip if the Ferment buff is active.
        if state.get('ferment_buff_active', False):
            _trigger_flip()

        # --- 5. Perform Additional Random Flips via PRD ---
        for _ in range(max_attempts):
            if random.random() < 0.45:
                successes_this_card += 1
                _trigger_flip()
            else:
                break
        
        # --- 6. Update the Persistent History ---
        prd_history['hc_plays'] = current_plays + 1
        prd_history['hc_successes'] = current_successes + successes_this_card
        state['heat_control_trigger_count'] += successes_this_card
        
        return state

    def cut(self, state: State) -> State:
        """
        Adds a bonus to a random color based on the 'Cut' card's defined
        value_range in cards.json.
        """
        card_def = next(
            (card for card in self._card_definitions if card['card_name'] == 'Cut'),
            None
        )
        
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
        """
        color = self._get_random_color()
        state[color] *= 2
        return state

    def slow_cook(self, state: State) -> State:
        """
        Adds +2 to the bonus that all future Heat Control flips will receive
        for both colors. This effect stacks.
        """
        state['slow_cook_all_color_bonus'] = state.get('slow_cook_all_color_bonus', 0) + 4
        return state

    def apply_end_of_cycle_effects(self, state: State, deck: tuple[str, ...]) -> State:
        """
        Applies end-of-cycle effects for the Kitchen crafting type.
        """
        if "Bake" in deck:
            yellow_score = state['yellow']
            blue_score = state['blue']
            
            difference = abs(yellow_score - blue_score)
            adjustment = difference / 2
            
            if yellow_score > blue_score:
                state['yellow'] -= adjustment
                state['blue'] += adjustment
            else:
                state['yellow'] += adjustment
                state['blue'] -= adjustment

        if state.get('dried_mushroom_buff') and state.get('heat_control_trigger_count', 0) >= 7:
            state['yellow'] += 3
            state['blue'] += 3
        return state