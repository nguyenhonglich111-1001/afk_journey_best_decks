import random
from typing import Dict, Callable
from .base_crafting import BaseCrafting, State

class ForgingCrafting(BaseCrafting):
    """
    Implements the logic for the 'forging' crafting type.
    """
    def get_card_functions(self) -> Dict[str, Callable[[State], State]]:
        """
        Maps forging card names to their specific functions.
        """
        return {
            "Forge Expert": self.forge_expert,
            "Forge": self.forge,
            "Ignite": self.ignite,
            "Heat Up": self.heat_up,
            "Charge": self.charge,
        }

    # --- Card Function Implementations ---

    def forge_expert(self, state: State) -> State:
        """
        Random color +3. All future Forge Expert cards gain +3.
        - Consumes a 'Charge' to affect both colors.
        - Can be triggered extra times by the 'Copper Stewpot' buff.
        """
        # Define the core action of this card as a local function
        # to make it easy to re-trigger for the Copper Stewpot buff.
        def _trigger_effect():
            artisan_bonus = state.get('artisan_bonus', 0)
            forge_expert_bonus = state.get('forge_expert_bonus', 0)
            bonus = 3 + artisan_bonus + forge_expert_bonus

            if state.get('charge_count', 0) > 0:
                state['yellow'] += bonus
                state['blue'] += bonus
                state['charge_count'] -= 1
            else:
                color = self._get_random_color()
                state[color] += bonus
            
            # The self-buff applies regardless of how it was triggered
            state['forge_expert_bonus'] = forge_expert_bonus + 3

        # --- Main Execution ---
        _trigger_effect()

        # Check for the Copper Stewpot buff for a chance to trigger again
        if state.get('copper_stewpot_buff', False):
            if random.random() < 0.50:
                _trigger_effect()
        
        return state

    def forge(self, state: State) -> State:
        """
        Random color +3. (Affected by Artisan bonus).
        - Consumes a 'Charge' to affect both colors.
        - The first Forge card played is affected by the 'Carve Box' buff.
        """
        artisan_bonus = state.get('artisan_bonus', 0)
        bonus = 3 + artisan_bonus

        # Check for the Carve Box buff, which affects the first Forge card
        is_first_forge = not state.get('first_forge_played', False)
        if state.get('carve_box_buff', False) and is_first_forge:
            state['yellow'] += bonus
            state['blue'] += bonus
        # Check for a standard charge
        elif state.get('charge_count', 0) > 0:
            state['yellow'] += bonus
            state['blue'] += bonus
            state['charge_count'] -= 1
        # Default action
        else:
            color = self._get_random_color()
            state[color] += bonus
        
        # Mark that a forge card has now been played
        state['first_forge_played'] = True
        return state

    def ignite(self, state: State) -> State:
        """
        Random color x2.
        """
        color = self._get_random_color()
        state[color] *= 2
        return state

    def heat_up(self, state: State) -> State:
        """
        All future cards with attribute Artisan gain +3.
        """
        state['artisan_bonus'] = state.get('artisan_bonus', 0) + 3
        return state

    def charge(self, state: State) -> State:
        """
        Increments the charge counter for future Artisan cards.
        """
        state['charge_count'] = state.get('charge_count', 0) + 1
        return state
