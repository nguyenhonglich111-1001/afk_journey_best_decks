# Feature Implementation Plan: correct-alchemy-buff-logic

## 📋 Todo Checklist
- [x] ~~Correct the buff checking logic in `src/crafting/alchemy.py`~~ ✅ Implemented
- [x] ~~Final Review and Testing~~ ✅ Implemented and reviewed

## 🔍 Analysis & Investigation

### Codebase Structure
- `data/items.json`: This file is correctly configured. The `buff_id` fields for "Warmdust-Deck" and "Calming Warmdust-deck" are present.
- `src/crafting/forging.py`: This file serves as the correct reference implementation. It checks for buffs using `state.get('buff_name', False)`.
- `src/crafting/alchemy.py`: This file contains the incorrect implementation. It checks for buff names in a non-existent `state.get("buffs", [])` list instead of checking for a boolean flag directly on the `state` object.
- `src/simulator.py`: The simulator correctly sets a boolean flag on the `state` object (e.g., `state['warmdust_deck_buff'] = True`) based on the `active_buff_id` from `items.json`.

### Current Architecture
The architecture relies on the `CardSimulator` to inject a boolean flag into the `state` dictionary, and the specific crafting class (`AlchemyCrafting` in this case) is responsible for checking for that flag to apply its logic. The previous implementation broke this pattern by checking for the buff in a list that is never created.

### Dependencies & Integration Points
The only dependency is between the `CardSimulator` and the `AlchemyCrafting` class. The simulator sets the state, and the crafting class reads it. This plan will fix the reading part.

### Considerations & Challenges
The change is straightforward and low-risk. It aligns the alchemy buff implementation with the established pattern used in the forging module, improving consistency and fixing the bug.

## 📝 Implementation Plan

### Step-by-Step Implementation
1. **Step 1: Correct the buff checking logic in `src/crafting/alchemy.py`**
   - **Files to modify**: `src/crafting/alchemy.py`
   - **Changes needed**:
     - In the `_apply_warmdust_deck_buff` method, change the conditional from `if "warmdust_deck_buff" in state.get("buffs", []):` to `if state.get("warmdust_deck_buff", False):`.
     - In the `_apply_calming_warmdust_deck_buff` method, change the conditional from `if "calming_warmdust_deck_buff" in state.get("buffs", []):` to `if state.get("calming_warmdust_deck_buff", False):`.
   - **Implementation Notes**: Corrected the buff checking logic in `_apply_warmdust_deck_buff` and `_apply_calming_warmdust_deck_buff` to use `state.get("buff_name", False)`.
   - **Status**: ✅ Completed

### Testing Strategy
- Run the simulator for the "Warmdust-Deck" and "Calming Warmdust-deck" items.
- Verify that the buffs are now correctly applied by observing the simulation results. The scores should be different from a run without the buff.
- Add temporary print statements in the buff methods in `src/crafting/alchemy.py` to get direct confirmation that the logic is being triggered during a simulation run.

## 🎯 Success Criteria
- The logic in `src/crafting/alchemy.py` is updated to correctly check for the buff flags in the `state` object.
- When the simulator is run with the "Warmdust-Deck" or "Calming Warmdust-deck" items, their respective buffs are applied on every card play.
- The fix is verified through simulation results or debug printing.
