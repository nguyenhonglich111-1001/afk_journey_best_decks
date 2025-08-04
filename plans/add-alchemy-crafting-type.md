# Feature Implementation Plan: Add Alchemy Crafting Type

## 📋 Todo Checklist
- [x] Create `crafting/alchemy.py` with card logic
- [x] Update `simulator.py` with the new state variable
- [x] Update `cards.json` with alchemy card definitions
- [x] Update `items.json` with the new Growth Serum item
- [x] Update `main.py` to register the new crafting type
- [x] Test the new implementation

## 🔍 Analysis & Investigation

### Codebase Structure
The project is well-structured for extension. Adding a new crafting type involves creating a new class in the `crafting/` directory, defining its data in `cards.json`, and registering the new class in `main.py`.

### New Mechanic: Future-Card Debuff
The `Enchant` card introduces a new mechanic: a debuff that applies to all subsequent cards played in the same run.
- **Logic**: `Enchant` will add `+1` to a new state variable, `enchant_debuff`.
- **Implementation**:
    1. A new state variable, `enchant_debuff`, must be added to the initial state in `simulator.py`, initialized to `0`.
    2. The `Enchant` card function will increment this state variable.
    3. All other card functions in `alchemy.py` (`Ingredient`, `Grind`, `Distill`) must first read `enchant_debuff` and apply a `-1` penalty to a random color for each stack of the debuff before executing their primary effect.

### New Mechanic: Highest/Lowest Color
The cards `Ingredient`, `Grind`, and `Distill` require identifying the color with the highest or lowest score. This will require helper methods within the `AlchemyCrafting` class to compare `state['yellow']` and `state['blue']` and return the name of the target color.

## 📝 Implementation Plan

### Step 1: Create `crafting/alchemy.py`
- **Action**: Create a new file `crafting/alchemy.py` that defines the `AlchemyCrafting` class, inheriting from `BaseCrafting`.
- **Changes needed**:
    1.  Implement the helper methods `_get_highest_color()` and `_get_lowest_color()`.
    2.  Implement the `enchant()` method. It should add `+8` to the lowest color and then increment `state['enchant_debuff']` by `1`.
    3.  Implement the `_apply_enchant_debuff()` helper method. This method will read `state['enchant_debuff']` and, for each stack, subtract `1` from a random color.
    4.  Implement the `ingredient()`, `grind()`, and `distill()` methods. Each of these methods **must call `_apply_enchant_debuff()` first**, before executing their respective core logic (+6 to highest, +3 to lowest, x2 to highest).
    5.  Create the `get_card_functions()` dictionary to map the card names to these methods.

### Step 2: Update `simulator.py`
- **Files to modify**: `simulator.py`
- **Action**: Add the new `enchant_debuff` state variable to the simulation's initial state.
- **Changes needed**: In the `evaluate_deck` method, add `'enchant_debuff': 0` to the `state` dictionary.

### Step 3: Update `cards.json`
- **Files to modify**: `cards.json`
- **Action**: Add a new top-level key `"alchemy"` with an array of card definitions.
- **Changes needed**:
    ```json
    "alchemy": [
        {
            "card_name": "Ingredient",
            "card_quantity": 2,
            "card_function": "Highest color +6."
        },
        {
            "card_name": "Grind",
            "card_quantity": 2,
            "card_function": "Lowest color +3."
        },
        {
            "card_name": "Enchant",
            "card_quantity": 2,
            "card_function": "Lowest color +8; random color -1 for each future card trigger."
        },
        {
            "card_name": "Distill",
            "card_quantity": 2,
            "card_function": "Highest color x2."
        }
    ]
    ```

### Step 4: Update `items.json`
- **Files to modify**: `items.json`
- **Action**: Add the new "Growth Serum" item to the JSON file.
- **Changes needed**:
    ```json
    "Growth Serum": {
        "crafting_type": "alchemy",
        "deck_size": 3,
        "description": "A basic alchemy item.",
        "star_thresholds": [12, 27]
    }
    ```

### Step 5: Update `main.py`
- **Files to modify**: `main.py`
- **Action**: Import the new `AlchemyCrafting` class and add it to the `CRAFTING_TYPE_CLASSES` dictionary to make it available to the simulator.
- **Changes needed**:
    1.  Add the import: `from crafting.alchemy import AlchemyCrafting`
    2.  Add the new entry to the dictionary: `"alchemy": AlchemyCrafting,`

### Testing Strategy
1.  **Run Single Item Analysis**: Execute the simulation for the new item to verify the entire workflow.
    - **Command**: `python main.py --item "Growth Serum"`
    - **Expected Outcome**: The script should run without errors and produce a star-optimization analysis for a 3-card deck, showing the best decks to reach 12 and 27 points.
2.  **Run General Analysis**: Execute the simulation for the general `alchemy` type to test various deck sizes.
    - **Command**: `python main.py alchemy`
    - **Expected Outcome**: The script should run without errors and find the top-scoring decks for sizes 3, 4, 5, and 6.

## 🎯 Success Criteria
- The new `alchemy` crafting type is fully integrated and selectable via the command line.
- The "Growth Serum" item can be successfully simulated.
- The `Enchant` card's debuff correctly affects subsequent cards in a run.
- The highest/lowest color logic works as intended.
- All tests run without raising exceptions.
