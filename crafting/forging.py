from typing import Dict, Callable
from .base_crafting import BaseCrafting, State

class ForgingCrafting(BaseCrafting):
    """
    Implements the logic for the 'forging' crafting type.
    """
    def get_card_functions(self) -> Dict[str, Callable[[State], State]]:
        """
        Maps forging card names to their specific functions.

        Returns:
            A dictionary mapping card names to their callable functions.
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
        Consumes a 'Charge' to affect both colors, if a charge is available.
        """
        artisan_bonus = state.get('artisan_bonus', 0)
        forge_expert_bonus = state.get('forge_expert_bonus', 0)
        bonus = 3 + artisan_bonus + forge_expert_bonus

        if state.get('charge_count', 0) > 0:
            state['yellow'] += bonus
            state['blue'] += bonus
            state['charge_count'] -= 1  # Consume one charge
        else:
            color = self._get_random_color()
            state[color] += bonus

        # The bonus for the *next* Forge Expert is increased.
        state['forge_expert_bonus'] = forge_expert_bonus + 3
        return state

    def forge(self, state: State) -> State:
        """
        Random color +3. (Affected by Artisan bonus).
        Consumes a 'Charge' to affect both colors, if a charge is available.
        """
        artisan_bonus = state.get('artisan_bonus', 0)
        bonus = 3 + artisan_bonus

        if state.get('charge_count', 0) > 0:
            state['yellow'] += bonus
            state['blue'] += bonus
            state['charge_count'] -= 1  # Consume one charge
        else:
            color = self._get_random_color()
            state[color] += bonus
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
        Increments the charge counter, causing future Artisan cards to affect all colors.
        """
        state['charge_count'] = state.get('charge_count', 0) + 1
        return state
