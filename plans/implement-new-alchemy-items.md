# Feature Implementation Plan: implement-new-alchemy-items

## 📋 Todo Checklist
- [x] ~~Implement `warmdust_deck_buff`~~ ✅ Implemented
- [x] ~~Implement `calming_warmdust_deck_buff`~~ ✅ Implemented
- [x] ~~Integrate new buffs into the `AlchemyCrafting` class~~ ✅ Implemented
- [x] ~~Final Review and Testing~~ ✅ Implemented and reviewed

## 🔍 Analysis & Investigation

### Codebase Structure
- `data/items.json`: This file contains the definitions of all items, including their names, crafting types, deck sizes, and special buffs. The two new items, "Warmdust-Deck" and "Calming Warmdust-deck", have been added here.
- `src/crafting/alchemy.py`: This file implements the logic for the 'Alchemy' crafting type. It contains the `AlchemyCrafting` class, which defines the specific functions for each alchemy card.
- `src/crafting/base_crafting.py`: This file provides the `BaseCrafting` abstract base class, which defines the common interface for all crafting types.

### Current Architecture
The current architecture uses a class-based approach for different crafting types, with each type inheriting from `BaseCrafting`. The `AlchemyCrafting` class in `src/crafting/alchemy.py` is responsible for managing the state and logic of alchemy crafting. Card effects are implemented as methods within this class, and a dictionary maps card names to these methods.

The new items introduce special buffs that need to be implemented. These buffs are triggered for each card played and modify the score of the lowest or highest color.

### Dependencies & Integration Points
The new logic will be integrated into the `AlchemyCrafting` class. The buffs will be implemented as new methods and will be called from the card functions.

### Considerations & Challenges
- The buffs need to be applied for each card triggered, so the logic should be called from within each card function in `AlchemyCrafting`.
- The `Warmdust-Deck` buff needs to identify the color with the lowest score, while the `Calming Warmdust-deck` buff needs to identify the color with the highest score. Helper methods for this already exist (`_get_lowest_color` and `_get_highest_color`).

## 📝 Implementation Plan

### Step-by-Step Implementation
1. **Step 1: Implement the `warmdust_deck_buff`**
   - **Files to modify**: `src/crafting/alchemy.py`
   - **Changes needed**:
     - Create a new method `_apply_warmdust_deck_buff(self, state: State)`.
     - This method will check if the `warmdust_deck_buff` is active in the current state.
     - If active, it will identify the color with the lowest score using `_get_lowest_color` and increment its value by 1.
   - **Implementation Notes**: Implemented the `_apply_warmdust_deck_buff` method in `src/crafting/alchemy.py`.
   - **Status**: ✅ Completed

2. **Step 2: Implement the `calming_warmdust_deck_buff`**
   - **Files to modify**: `src/crafting/alchemy.py`
   - **Changes needed**:
     - Create a new method `_apply_calming_warmdust_deck_buff(self, state: State)`.
     - This method will check if the `calming_warmdust_deck_buff` is active in the current state.
     - If active, it will identify the color with the highest score using `_get_highest_color` and increment its value by 3.
   - **Implementation Notes**: Implemented the `_apply_calming_warmdust_deck_buff` method in `src/crafting/alchemy.py`.
   - **Status**: ✅ Completed

3. **Step 3: Integrate the new buffs into the card functions**
   - **Files to modify**: `src/crafting/alchemy.py`
   - **Changes needed**:
     - In each card function (`ingredient`, `grind`, `enchant`, `distill`), add calls to `_apply_warmdust_deck_buff` and `_apply_calming_warmdust_deck_buff` at the beginning of the function. This ensures that the buffs are applied every time a card is played.
   - **Implementation Notes**: Added calls to the new buff methods in all card functions in `src/crafting/alchemy.py`.
   - **Status**: ✅ Completed

### Testing Strategy
- To test the implementation, you can add temporary print statements within the new buff methods to verify they are being called correctly.
- Run the simulator for the new items and check if the scores are calculated as expected.
- You can create a new scenario in the `scenarios` directory to test the new items specifically.

## 🎯 Success Criteria
- The `Warmdust-Deck` item should correctly apply its buff, increasing the lowest color's score by 1 for each card played.
- The `Calming Warmdust-deck` item should correctly apply its buff, increasing the highest color's score by 3 for each card played.
- The new buffs should not interfere with the existing logic of the alchemy cards.
- The simulation should run without errors and produce the correct results for the new items.
