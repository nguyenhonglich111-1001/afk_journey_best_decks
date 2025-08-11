# Feature Implementation Plan: implement_fuse_card

## 📋 Todo Checklist
- [x] ~~Add "Fuse" card definition to `data/cards.json`.~~ ✅ Implemented
- [x] ~~Implement the core "Fuse" logic in `src/simulator.py`.~~ ✅ Implemented
- [x] ~~Add a placeholder function for "Fuse" in `src/crafting/alchemy.py`.~~ ✅ Implemented
- [x] ~~Test the implementation by running a simulation for the "alchemy" type.~~ ✅ Implemented
- [x] ~~Final Review and Testing.~~ ✅ Implemented

## 🔍 Analysis & Investigation

### Codebase Structure
- **`data/cards.json`**: The central data file defining all cards, their quantities, and descriptions. This is the first place a new card must be added.
- **`src/crafting/`**: This directory contains the Python logic for each crafting type. The `alchemy.py` file implements the specific effects of each alchemy card.
- **`src/simulator.py`**: This is the core of the application. The `CardSimulator` class, specifically its `evaluate_deck` method, runs the Monte Carlo simulation for a given deck. It iterates through the cards in a shuffled deck and applies their effects to a `state` dictionary.
- **`src/main.py`**: The entry point that parses arguments and orchestrates the simulation.

### Current Architecture
The architecture is event-driven and state-based. For each simulation run, a `state` dictionary holds the current scores (`yellow`, `blue`) and any active buffs. The `evaluate_deck` method in `CardSimulator` shuffles the deck and iterates through the cards, calling the corresponding function from the appropriate crafting module (e.g., `AlchemyCrafting`) to modify the state.

The "Fuse" card presents a unique challenge because its effect is conditional and triggers *after* all other cards have been played. The current simulation loop is not designed for post-processing effects. The most direct and least disruptive way to implement this is to modify the `evaluate_deck` method to handle "Fuse" as a special case after the main card loop.

### Dependencies & Integration Points
The implementation is self-contained and has no new external dependencies. The key integration points are:
1.  The `cards.json` file, which the simulator reads to get the card pool.
2.  The `AlchemyCrafting` class, which provides the card functions.
3.  The `CardSimulator.evaluate_deck` method, which needs to be modified to handle the special trigger timing of "Fuse".

### Considerations & Challenges
- **Trigger Timing**: The main challenge is that "Fuse" breaks the existing pattern of cards being played sequentially. The logic must be applied after the main simulation loop but before the final score is calculated.
- **State Management**: The implementation must correctly check the `state` for the color gap (`abs(state['yellow'] - state['blue'])`) and apply the bonus if the condition is met.
- **Code Clarity**: The special handling for "Fuse" should be clearly commented in `simulator.py` to explain why it deviates from the standard card evaluation loop.

## 📝 Implementation Plan

### Prerequisites
No new dependencies are required. Ensure the project is in a clean state before starting.

### Step-by-Step Implementation
1. **Step 1: Define the "Fuse" Card in `cards.json`**
   - Files to modify: `data/cards.json`
   - Changes needed: Add a new entry to the "alchemy" card list.
   - **Implementation Notes**: Added the "Fuse" card to the `alchemy` section of `data/cards.json`.
   - **Status**: ✅ Completed

   ```json
   {
       "card_name": "Fuse",
       "card_quantity": 1,
       "card_function": "Triggers if the color point gap is less than 10 when production ends. All colors +5."
   }
   ```

2. **Step 2: Implement the Core "Fuse" Logic in the Simulator**
   - Files to modify: `src/simulator.py`
   - Changes needed: Modify the `evaluate_deck` method to handle "Fuse" as a special case after the main card loop.
   - **Implementation Notes**: Modified the `evaluate_deck` method in `src/simulator.py` to include the special post-loop logic for the "Fuse" card.
   - **Status**: ✅ Completed

   ```python
   # In CardSimulator.evaluate_deck method

   # ... inside the for _ in range(simulations): loop ...

   shuffled_deck = random.sample(list(deck), len(deck))
   
   # --- START MODIFICATION ---
   
   # Handle regular cards first
   for card_name in shuffled_deck:
       if card_name == "Fuse":
           continue  # Skip Fuse in the main loop
       func = self.card_functions.get(card_name)
       if func:
           func(state)

   # After all other cards are played, check for Fuse's effect
   if "Fuse" in deck:
       if abs(state['yellow'] - state['blue']) < 10:
           state['yellow'] += 5
           state['blue'] += 5
           
   # --- END MODIFICATION ---

   final_score = state['yellow'] * state['blue']
   total_score += final_score
   ```

3. **Step 3: Add Placeholder Function in `alchemy.py`**
   - Files to modify: `src/crafting/alchemy.py`
   - Changes needed: Add a "Fuse" function to the `get_card_functions` dictionary and create a placeholder method. This maintains consistency, even though the core logic resides in the simulator.
   - **Implementation Notes**: Added the placeholder `fuse` method to `src/crafting/alchemy.py` and included it in the `get_card_functions` dictionary.
   - **Status**: ✅ Completed

   ```python
   # In AlchemyCrafting class

   def get_card_functions(self) -> Dict[str, Callable[[State], State]]:
       """Maps alchemy card names to their specific functions."""
       return {
           "Ingredient": self.ingredient,
           "Grind": self.grind,
           "Enchant": self.enchant,
           "Distill": self.distill,
           "Fuse": self.fuse, # Add this line
       }

   # Add the new method
   def fuse(self, state: State) -> State:
       """
       This card's logic is handled in the simulator due to its special
       end-of-production trigger. This function is a placeholder.
       """
       # Intentionally does nothing, as logic is in simulator.py
       return state
   ```

### Testing Strategy
1.  **Unit Test**: While the project lacks a formal testing suite, the primary verification will be through a targeted simulation run.
2.  **Manual Verification**: Execute the simulator specifically for the "alchemy" crafting type with a deck of size 4.
    - Command: `python src/main.py alchemy`
3.  **Observe Output**:
    - Check if the simulation runs without errors.
    - Analyze the top-performing decks. Decks containing "Fuse" should appear in the results.
    - Manually calculate the expected score for a simple deck (e.g., 3x Grind, 1x Fuse) to ensure the logic is being applied correctly. The score should reflect the `+5` bonus being added when the color gap is small.
   - **Implementation Notes**: The simulation ran successfully. The output shows decks with the "Fuse" card, and the scores are consistent with the implemented logic.
   - **Status**: ✅ Completed

## 🎯 Success Criteria
The feature is complete and working when:
- The "Fuse" card is available for selection in the "alchemy" crafting type.
- Simulations including the "Fuse" card complete successfully.
- The final scores of simulation runs correctly reflect the "Fuse" card's conditional logic: the `+5` bonus to both colors is applied only when the point gap between them is less than 10 at the end of the production cycle.
- The top-ranked decks for alchemy now include combinations that strategically leverage the "Fuse" card's unique balancing requirement.