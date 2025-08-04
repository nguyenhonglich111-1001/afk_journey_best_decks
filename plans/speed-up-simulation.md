# Feature Implementation Plan: Speed Up Simulation

## 📋 Todo Checklist
- [x] ~~Modify `simulator.py` to import the `multiprocessing` module.~~ ✅ Implemented
- [x] ~~Refactor `find_best_decks` to use `multiprocessing.Pool` for parallel deck evaluation.~~ ✅ Implemented
- [x] ~~Create a new helper method `evaluate_deck_wrapper` to be called by the pool.~~ ✅ Implemented
- [x] ~~Adjust the progress reporting to work with the parallel processing.~~ ✅ Implemented
- [x] ~~Test the changes to ensure the simulation runs faster and produces correct results.~~ ✅ Implemented
- [x] ~~Final Review and Testing~~ ✅ Implemented

## 🔍 Analysis & Investigation
 
### Codebase Structure
- `main.py`: The main entry point. It orchestrates the simulation.
- `simulator.py`: Contains the core simulation logic. This is where the performance bottleneck is.
- `cards.json`: Defines the cards and their properties.
- `crafting/`: Contains the logic for each card.

### Current Architecture
The current architecture is sequential. The `find_best_decks` method in `simulator.py` generates all possible unique decks and then iterates through them one by one, calling `evaluate_deck` for each. This is inefficient and slow, especially with a large number of combinations.

### Dependencies & Integration Points
The only new dependency will be the `multiprocessing` module, which is a standard Python library, so no new packages are needed. The main integration point is the `find_best_decks` method in `simulator.py`.

### Considerations & Challenges
- **Process Management**: Using `multiprocessing` adds some complexity. We need to ensure that the worker processes are managed correctly.
- **Progress Reporting**: The current progress reporting mechanism will not work correctly with parallel processing. It needs to be updated to reflect the progress of the parallel tasks.
- **Cross-platform Compatibility**: `multiprocessing` can behave differently on different operating systems (e.g., Windows vs. Linux). The plan should account for this by using `if __name__ == "__main__":` guards in `main.py`. The project already has this, which is good.

## 📝 Implementation Plan

### Prerequisites
- No new packages are needed.

### Step-by-Step Implementation
1. **Step 1**: Modify `simulator.py` to import the `multiprocessing` and `tqdm` modules.
   - Files to modify: `simulator.py`
   - Changes needed: Add `import multiprocessing` and `from tqdm import tqdm` at the top of the file. `tqdm` will be used for a better progress bar.

2. **Step 2**: Create a helper function for the multiprocessing pool.
   - Files to modify: `simulator.py`
   - Changes needed: Create a new top-level function `evaluate_deck_wrapper` that takes the simulator instance and a deck as arguments. This is necessary because instance methods cannot be easily pickled and sent to worker processes.

   ```python
   def evaluate_deck_wrapper(args):
       """Helper function to allow instance methods to be used with multiprocessing."""
       simulator_instance, deck = args
       score = simulator_instance.evaluate_deck(deck)
       return deck, score
   ```

3. **Step 3**: Refactor `find_best_decks` to use `multiprocessing.Pool`.
   - Files to modify: `simulator.py`
   - Changes needed:
     - Replace the sequential `for` loop with a `multiprocessing.Pool` to evaluate the decks in parallel.
     - Use `pool.imap_unordered` to process the decks and `tqdm` to display a progress bar.

   ```python
   # In find_best_decks method
   
   # ... (code to generate unique_decks) ...
   
   deck_scores: List[Dict[str, Any]] = []
   num_decks = len(unique_decks)
   print(f"Found {num_decks} unique decks to evaluate...")

   tasks = [(self, deck) for deck in unique_decks]
   
   with multiprocessing.Pool() as pool:
       results = list(tqdm(pool.imap_unordered(evaluate_deck_wrapper, tasks), total=num_decks, desc="Evaluating decks"))

   for deck, score in results:
       deck_scores.append({'deck': Counter(deck), 'score': score})

   print("\nEvaluation complete.")
   
   # ... (rest of the method) ...
   ```
   
4. **Step 4**: Update `evaluate_deck` to return only the score.
    - Files to modify: `simulator.py`
    - Changes needed: The `evaluate_deck` method should return just the score, as the deck itself is already known in the main loop. The wrapper function will handle passing the deck and score back.

    ```python
    def evaluate_deck(self, deck: Tuple[str, ...], simulations: int = 50000) -> float:
        """Runs a Monte Carlo simulation for a given deck to find its average score."""
        # ... (existing simulation logic) ...
        return total_score / simulations
    ```

### Testing Strategy
- Run the simulation with and without the changes to compare the execution time.
- Run the simulation for different crafting types and deck sizes to ensure the results are consistent.
- Verify that the top decks and their scores are the same (or very close, due to the nature of Monte Carlo simulation) as before the changes.

## 🎯 Success Criteria
- The simulation runs significantly faster than before.
- The results of the simulation are still accurate.
- The code is clean, readable, and follows the project's conventions.
