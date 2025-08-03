import random
from .base_crafting import BaseCrafting

class ForgingCrafting(BaseCrafting):
    """
    Implements the logic for the 'forging' crafting type.
    """
    def get_card_functions(self):
        """Maps forging card names to their specific functions."""
        return {
            "Forge Expert": self.forge_expert,
            "Forge": self.forge,
            "Ignite": self.ignite,
            "Heat Up": self.heat_up,
        }

    # --- Card Function Implementations ---

    def forge_expert(self, state):
        """Random color +3. All future Forge Expert cards gain +3."""
        artisan_bonus = state.get('artisan_bonus', 0)
        forge_expert_bonus = state.get('forge_expert_bonus', 0)
        
        color = self._get_random_color()
        state[color] += (3 + artisan_bonus + forge_expert_bonus)
        
        # The bonus for the *next* Forge Expert is increased.
        state['forge_expert_bonus'] = forge_expert_bonus + 3
        return state

    def forge(self, state):
        """Random color +3. (Affected by Artisan bonus)."""
        artisan_bonus = state.get('artisan_bonus', 0)
        color = self._get_random_color()
        state[color] += (3 + artisan_bonus)
        return state

    def ignite(self, state):
        """Random color x2."""
        color = self._get_random_color()
        state[color] *= 2
        return state

    def heat_up(self, state):
        """All future cards attribute Artisan gain +3."""
        state['artisan_bonus'] = state.get('artisan_bonus', 0) + 3
        return state
