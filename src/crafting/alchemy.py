import random
from typing import Dict, Callable, Tuple
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

    def _apply_overload_debuff(self, state: State):
        """Applies the debuff from previously played Overload cards."""
        debuff_stacks = state.get('overload_debuff', 0)
        for _ in range(debuff_stacks):
            color = self._get_random_color()
            state[color] = max(1, state[color] - 3) # Ensure score doesn't go below 1

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

    def _apply_soothing_buff(self, state: State):
        """Applies the buff for the Soothing item."""
        if state.get("soothing_buff", False):
            highest_color = self._get_highest_color(state)
            state[highest_color] += 3

    def _apply_illusion_buff(self, state: State):
        """Applies the buff for the Illusion item."""
        if state.get("illusion_buff", False):
            lowest_color = self._get_lowest_color(state)
            state[lowest_color] += 1

    def apply_pre_card_effects(self, state: State) -> State:
        """Applies all effects that should trigger before a card's main logic."""
        self._apply_enchant_debuff(state)
        self._apply_overload_debuff(state)
        self._apply_warmdust_deck_buff(state)
        self._apply_calming_warmdust_deck_buff(state)
        self._apply_soothing_buff(state)
        self._apply_illusion_buff(state)
        return state

    def get_card_functions(self) -> Dict[str, Callable[[State], State]]:
        """Maps alchemy card names to their specific functions."""
        return {
            "Ingredient": self.ingredient,
            "Grind": self.grind,
            "Enchant": self.enchant,
            "Distill": self.distill,
            "Overload": self.overload,
        }

    # --- Card Function Implementations ---
    def overload(self, state: State) -> State:
        """Highest color +40; increments future card debuff."""
        highest_color = self._get_highest_color(state)
        state[highest_color] += 40
        state['overload_debuff'] = state.get('overload_debuff', 0) + 1
        return state

    def ingredient(self, state: State) -> State:
        """Highest color +10. Lowest color -2."""
        highest_color = self._get_highest_color(state)
        lowest_color = self._get_lowest_color(state)
        state[highest_color] += 15
        state[lowest_color] = max(1, state[lowest_color] - 3)
        return state

    def grind(self, state: State) -> State:
        """Lowest color +4. Highest color -2"""
        highest_color = self._get_highest_color(state)
        lowest_color = self._get_lowest_color(state)
        state[lowest_color] += 8
        state[highest_color] = max(1, state[highest_color] - 4)

        return state

    def enchant(self, state: State) -> State:
        """Lowest color +8; increments future card debuff."""
        lowest_color = self._get_lowest_color(state)
        state[lowest_color] += 20
        state['enchant_debuff'] = state.get('enchant_debuff', 0) + 1
        return state

    def distill(self, state: State) -> State:
        """Highest color x2."""
        highest_color = self._get_highest_color(state)
        state[highest_color] *= 2
        return state

    def apply_end_of_cycle_effects(self, state: State, deck: Tuple[str, ...]) -> State:
        """Applies the logic for the Fuse card if it's in the deck."""
        if "Fuse" in deck:
            # Check the condition: color point gap is less than 10.
            if abs(state['yellow'] - state['blue']) < 20:
                state['yellow'] += 10
                state['blue'] += 10
        return state
    
    def apply_start_of_cycle_effects(self, state: State, deck: Tuple[str, ...]) -> State:
        if state.get("fireward_ring_buff", False):
            # Apply +15 to a random color at the start of production
            color = self._get_random_color()
            state[color] += 15

        return state

    def play_card(self, card_name: str, state: State) -> State:
        """
        Overrides the base play_card to handle special buffs for alchemy cards.
        """
        func = self.get_card_functions().get(card_name)
        if not func:
            return state

        # Original card play
        state = func(state)

        # Handle Warming Incense buff for Ingredient card
        if card_name == "Ingredient" and state.get("warming_incense_buff"):
            state = func(state)  # Trigger again

        # Handle Calmwind Incense buff for Grind card
        if card_name == "Grind" and state.get("calmwind_incense_buff"):
            state = func(state)  # Trigger again

        return state
