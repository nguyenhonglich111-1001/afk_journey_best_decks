# Feature Implementation Plan: refactor_fuse_card_solid

## 📋 Todo Checklist
- [x] ~~Update `data/cards.json` to include a `trigger` property for the "Fuse" card.~~ ✅ Implemented
- [x] ~~Add a new `apply_end_of_cycle_effects` method to the `BaseCrafting` class.~~ ✅ Implemented
- [x] ~~Move the "Fuse" logic from `src/simulator.py` to `src/crafting/alchemy.py`.~~ ✅ Implemented
- [x] ~~Refactor `src/simulator.py` to remove the hardcoded "Fuse" logic and call the new method.~~ ✅ Implemented
- [x] ~~Test the refactored implementation by running a simulation.~~ ✅ Implemented
- [x] ~~Final Review and Cleanup.~~ ✅ Implemented

## 🔍 Analysis & Investigation

### Codebase Structure
- **`data/cards.json`**: Defines card properties. This will be extended to include card trigger information.
- **`src/crafting/base_crafting.py`**: The abstract base class for all crafting types. It defines the interface that the simulator interacts with. This is the ideal place to introduce the concept of different effect timings.
- **`src/crafting/alchemy.py`**: The concrete implementation for Alchemy crafting. This class should contain all logic specific to alchemy cards, including "Fuse".
- **`src/simulator.py`**: The core simulation engine. Its responsibility should be to orchestrate the simulation steps (e.g., play cards, apply final effects, calculate score) rather than knowing the logic of any specific card.

### Current Architecture
The current implementation has a critical design flaw: the `CardSimulator` is hardcoded to know about the "Fuse" card. This violates two key SOLID principles:

1.  **Single Responsibility Principle (SRP)**: The simulator's responsibility has bled into handling specific card logic, when it should only be concerned with running the simulation process.
2.  **Open/Closed Principle (OCP)**: The simulator is not closed for modification. To add another card with a special end-of-cycle trigger, one would have to modify the simulator's core `evaluate_deck` method again.

The proposed refactoring will address this by creating a more robust, event-driven system where the simulator is decoupled from the specific card implementations.

### Dependencies & Integration Points
- The `CardSimulator` is tightly coupled with the crafting classes (`AlchemyCrafting`, etc.). The plan is to strengthen the contract between them through the `BaseCrafting` interface, making the coupling looser and more predictable.
- The card definitions in `cards.json` will be the single source of truth for how a card behaves, including its trigger timing.

### Considerations & Challenges
- **Backwards Compatibility**: The change must not break the functionality of existing cards. By making the new `trigger` property in `cards.json` optional and defaulting to the standard "on_play" behavior, we ensure existing cards work as before.
- **Extensibility**: The new design must be easily extensible for future cards with different trigger types (e.g., `on_shuffle`, `on_discard`). The proposed architecture provides a solid foundation for this.

## 📝 Implementation Plan

### Prerequisites
No new dependencies are required.

### Step-by-Step Implementation
1. **Step 1: Generalize Card Triggers in `cards.json`**
   - **Files to modify**: `data/cards.json`
   - **Changes needed**: Add a `"trigger": "end_of_cycle"` property to the "Fuse" card. This explicitly defines its unique timing. Other cards will be assumed to have a default "on_play" trigger.
   - **Implementation Notes**: Added the `"trigger": "end_of_cycle"` property to the "Fuse" card in `data/cards.json`.
   - **Status**: ✅ Completed

   ```json
   // In data/cards.json, inside the "alchemy" list
   {
       "card_name": "Fuse",
       "card_quantity": 1,
       "card_function": "Triggers if the color point gap is less than 10 when production ends. All colors +5.",
       "trigger": "end_of_cycle" // Add this line
   }
   ```

2. **Step 2: Update the `BaseCrafting` Interface**
   - **Files to modify**: `src/crafting/base_crafting.py`
   - **Changes needed**: Add a new method to the `BaseCrafting` class to handle end-of-cycle effects. This establishes a formal contract for all crafting types.
   - **Implementation Notes**: Added the `apply_end_of_cycle_effects` method to the `BaseCrafting` class.
   - **Status**: ✅ Completed

   ```python
   # In BaseCrafting class
   @abstractmethod
   def get_card_functions(self) -> Dict[str, Callable[[State], State]]:
       """Maps card names to their standard 'on play' functions."""
       pass

   def apply_end_of_cycle_effects(self, state: State, deck: Tuple[str, ...]) -> State:
       """
       Applies effects for cards that trigger at the end of the crafting process.
       Base implementation does nothing, to be overridden by subclasses.
       """
       return state
   ```

3. **Step 3: Relocate "Fuse" Logic to `alchemy.py`**
   - **Files to modify**: `src/crafting/alchemy.py`
   - **Changes needed**: Implement the `apply_end_of_cycle_effects` method and move the "Fuse" logic into it. The placeholder `fuse` function can now be removed.
   - **Implementation Notes**: Moved the "Fuse" logic to the `apply_end_of_cycle_effects` method in `src/crafting/alchemy.py` and removed the placeholder `fuse` method.
   - **Status**: ✅ Completed

   ```python
   # In AlchemyCrafting class

   # Remove the "Fuse" entry from the get_card_functions dictionary
   def get_card_functions(self) -> Dict[str, Callable[[State], State]]:
       return {
           "Ingredient": self.ingredient,
           "Grind": self.grind,
           "Enchant": self.enchant,
           "Distill": self.distill,
       }

   # Remove the placeholder fuse method entirely.

   # Add the new implementation for end-of-cycle effects
   def apply_end_of_cycle_effects(self, state: State, deck: Tuple[str, ...]) -> State:
       """Applies the logic for the Fuse card if it's in the deck."""
       if "Fuse" in deck:
           # Check the condition: color point gap is less than 10.
           if abs(state['yellow'] - state['blue']) < 10:
               state['yellow'] += 5
               state['blue'] += 5
       return state
   ```

4. **Step 4: Refactor the `CardSimulator`**
   - **Files to modify**: `src/simulator.py`
   - **Changes needed**: Remove the hardcoded "Fuse" logic from `evaluate_deck` and replace it with a generic call to the new `apply_end_of_cycle_effects` method.
   - **Implementation Notes**: Refactored the `evaluate_deck` method in `src/simulator.py` to remove the hardcoded "Fuse" logic and call the new `apply_end_of_cycle_effects` method.
   - **Status**: ✅ Completed

   ```python
   # In CardSimulator.evaluate_deck method
   # ... inside the for _ in range(simulations): loop ...

   shuffled_deck = random.sample(list(deck), len(deck))

   # --- START REFACTOR ---

   # On-play effects loop
   for card_name in shuffled_deck:
       func = self.card_functions.get(card_name)
       if func:
           func(state)

   # End-of-cycle effects
   state = self.crafting.apply_end_of_cycle_effects(state, deck)

   # --- END REFACTOR ---

   final_score = state['yellow'] * state['blue']
   total_score += final_score
   ```

### Testing Strategy
1.  **Execute Simulation**: Run the simulator for the "alchemy" crafting type.
    - Command: `python src/main.py alchemy`
2.  **Verify Output**:
    - The simulation should run without errors.
    - The results should be functionally identical to the previous implementation. The top-performing decks and their scores should match, proving the refactoring was successful.
3.  **Code Review**: Manually inspect the changed files (`simulator.py`, `alchemy.py`, `base_crafting.py`) to confirm that the responsibilities are now correctly separated and the hardcoded logic is gone.
   - **Implementation Notes**: The simulation ran successfully, and the output is identical to the pre-refactor run, confirming the logic is still correct.
   - **Status**: ✅ Completed

## 🎯 Success Criteria
- The `CardSimulator` class no longer contains any logic specific to the "Fuse" card or any other card.
- The "Fuse" card's logic is entirely contained within the `AlchemyCrafting` class.
- The simulation results for the alchemy craft type are identical to the results before the refactor, confirming no change in functionality.
- The new architecture is demonstrably more extensible, allowing for new end-of-cycle cards to be added by only modifying the relevant crafting module.