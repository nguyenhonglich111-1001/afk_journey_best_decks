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
        }

    # --- Card Function Implementations ---

    def forge_expert(self, state: State) -> State:
        """
        Random color +3. All future Forge Expert cards gain +3.

        Args:
            state: The current simulation state.

        Returns:
            The modified simulation state.
        """
        artisan_bonus = state.get('artisan_bonus', 0)
        forge_expert_bonus = state.get('forge_expert_bonus', 0)

        color = self._get_random_color()
        state[color] += (3 + artisan_bonus + forge_expert_bonus)

        # The bonus for the *next* Forge Expert is increased.
        state['forge_expert_bonus'] = forge_expert_bonus + 3
        return state

    def forge(self, state: State) -> State:
        """
        Random color +3. (Affected by Artisan bonus).

        Args:
            state: The current simulation state.

        Returns:
            The modified simulation state.
        """
        artisan_bonus = state.get('artisan_bonus', 0)
        color = self._get_random_color()
        state[color] += (3 + artisan_bonus)
        return state

    def ignite(self, state: State) -> State:
        """
        Random color x2.

        Args:
            state: The current simulation state.

        Returns:
            The modified simulation state.
        """
        color = self._get_random_color()
        state[color] *= 2
        return state

    def heat_up(self, state: State) -> State:
        """
        All future cards with attribute Artisan gain +3.

        Args:
            state: The current simulation state.

        Returns:
            The modified simulation state.
        """
        state['artisan_bonus'] = state.get('artisan_bonus', 0) + 3
        return state
