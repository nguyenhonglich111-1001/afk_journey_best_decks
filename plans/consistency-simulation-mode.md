# Feature Implementation Plan: Consistency Simulation Mode

## 📋 Todo Checklist
- [x] ~~Add a new `--target-score` command-line argument to `main.py`.~~ ✅ Implemented
- [x] ~~Update `simulator.py` to handle the new consistency calculation mode.~~ ✅ Implemented
- [x] ~~Modify `CardSimulator.evaluate_deck` to return both average score and consistency.~~ ✅ Implemented
- [x] ~~Adjust the multiprocessing wrapper to handle the new return format.~~ ✅ Implemented
- [x] ~~Update `main.py` to display the new metrics when in consistency mode.~~ ✅ Implemented
- [x] ~~Final Review and Testing.~~ ✅ Implemented

## 🔍 Analysis & Investigation

### Codebase Structure
- `main.py`: The entry point of the application. It handles parsing command-line arguments, loading data, initializing the simulator, and printing the final results. This is where the new CLI option will be added and where the output format will be adjusted.
- `simulator.py`: Contains the core logic for the Monte Carlo simulation. The `CardSimulator` class is responsible for evaluating decks. This file will be modified to calculate the new "consistency" metric.
- `crafting/`: This directory contains the logic for individual cards and will not require changes, as the core card effects are not being altered.

### Current Architecture
The application has a clean, decoupled architecture. `main.py` serves as the controller, while `simulator.py` is the engine. This separation makes it straightforward to add a new simulation mode without disrupting existing logic. The simulation is parallelized using the `multiprocessing` module, which is a key consideration for this feature. The `evaluate_deck_wrapper` function is used to allow the `multiprocessing.Pool` to call an instance method of `CardSimulator`, and it must be updated to handle the new data structure returned by the evaluation function.

### Dependencies & Integration Points
- **`argparse`**: The standard library module used in `main.py` to parse CLI arguments. A new argument, `--target-score`, will be added here.
- **`multiprocessing`**: The `evaluate_deck` method's return value will change from a single float to a dictionary. This requires updating the `evaluate_deck_wrapper` function and the loop that processes the results from the multiprocessing pool in `find_best_decks`.

### Considerations & Challenges
- **Data Flow**: The primary challenge is ensuring the new data (consistency score) flows correctly from the simulation engine back to the main display function. The `evaluate_deck` method will now return a dictionary (`{'score': float, 'consistency': float}`) instead of just a float. This change ripples through the `evaluate_deck_wrapper` and the result processing loop in `find_best_decks`.
- **User Experience**: The CLI output needs to be clear about which mode is active. When `--target-score` is used, the output should be explicitly sorted by "Consistency" and display that metric prominently, while still showing the average score for context.
- **Default Behavior**: The existing default behavior (finding the highest average score) must remain unchanged when the new flag is not used.

## 📝 Implementation Plan

### Prerequisites
- No new packages or external dependencies are required.

### Step-by-Step Implementation
1. **Step 1**: Add a `--target-score` argument in `main.py`.
   - **Files to modify**: `main.py`
   - **Changes needed**: In the `main` function, add a new argument to the `ArgumentParser`.
     ```python
     parser.add_argument(
         "--target-score",
         type=int,
         help="Find decks with the highest chance to meet this target score."
     )
     ```

2. **Step 2**: Update the `CardSimulator` to accept and store the target score.
   - **Files to modify**: `simulator.py`
   - **Changes needed**: Modify the `CardSimulator.__init__` method to accept and store `target_score`.
     ```python
     # In CardSimulator.__init__
     def __init__(
         self,
         crafting_instance: BaseCrafting,
         active_buff_id: Optional[str] = None,
         target_score: Optional[int] = None  # Add this
     ) -> None:
         # ... existing assignments
         self.target_score = target_score  # Add this
     ```

3. **Step 3**: Modify the deck evaluation logic to calculate consistency.
   - **Files to modify**: `simulator.py`
   - **Changes needed**: Update the `evaluate_deck` method to count how many simulation runs meet the `target_score` and return a dictionary containing both the average score and the consistency percentage.
     ```python
     # In CardSimulator.evaluate_deck
     def evaluate_deck(self, deck: Tuple[str, ...], simulations: int = 50000) -> Dict[str, float]:
         total_score = 0.0
         successful_runs = 0

         for _ in range(simulations):
             # ... existing state setup ...
             final_score = state['yellow'] * state['blue']
             total_score += final_score

             if self.target_score and final_score >= self.target_score:
                 successful_runs += 1

         results = {'score': total_score / simulations}
         if self.target_score:
             results['consistency'] = (successful_runs / simulations) * 100
         
         return results
     ```

4. **Step 4**: Update the multiprocessing wrapper and the main simulation loop.
   - **Files to modify**: `simulator.py`
   - **Changes needed**: 
     - The `evaluate_deck_wrapper` needs to be updated to handle the new dictionary return type.
     - The `find_best_decks` method needs to be updated to process the new results format and sort based on the correct metric (`consistency` or `score`).
     ```python
     # Top-level function
     def evaluate_deck_wrapper(args):
         simulator_instance, deck = args
         eval_results = simulator_instance.evaluate_deck(deck) # Returns a dict now
         return deck, eval_results

     # In CardSimulator.find_best_decks
     # ...
     for deck, eval_results in results_from_pool:
         deck_info = {
             'deck': Counter(deck),
             'score': eval_results.get('score', 0),
             'consistency': eval_results.get('consistency', 0)
         }
         deck_scores.append(deck_info)
     
     # Sort based on the simulation mode
     sort_key = 'consistency' if self.target_score else 'score'
     deck_scores.sort(key=lambda x: x[sort_key], reverse=True)
     results[size] = deck_scores[:top_n]
     ```

5. **Step 5**: Update `main.py` to control the simulator and display the results.
   - **Files to modify**: `main.py`
   - **Changes needed**: 
     - Pass the `target_score` from `args` when initializing `CardSimulator`.
     - Add logic to detect which mode is active and print the appropriate headers and result metrics.
     ```python
     # In main function
     simulator = CardSimulator(
         crafting_instance,
         active_buff_id=active_buff_id, # This will be None in the normal case
         target_score=args.target_score
     )
     
     # ... later in the results printing section ...
     if args.target_score:
         print(f"\n\n--- Top {top_n_results} Most Consistent Decks (Target: {args.target_score}) ---")
         metric_key = 'consistency'
         metric_label = 'Consistency'
         metric_unit = '%'
     else:
         # ... existing code ...

     # ... inside the loop ...
     main_metric_val = result[metric_key]
     avg_score = result['score']
     print(f"  #{i+1}: {metric_label}: {main_metric_val:.2f}{metric_unit}")
     print(f"     Avg Score: {avg_score:.2f}") # Always show avg score
     print(f"     Deck: {deck_str}")
     ```

### Testing Strategy
1.  **Default Mode Test**: Run the script without the `--target-score` flag (e.g., `python main.py forging`). The output should be identical to the current behavior, showing the top decks sorted by "Expected Score".
2.  **Consistency Mode Test**: Run the script with the new flag (e.g., `python main.py kitchen --target-score 100`). The output should be titled "Most Consistent Decks" and show results sorted by the "Consistency" percentage. It should also display the "Avg Score" for context.
3.  **Special Item Test**: Combine the flags to ensure they work together (e.g., `python main.py forging --item "Carve Box" --target-score 200`). The simulation should run for the correct deck size and use the consistency metric.

## 🎯 Success Criteria
- The application runs without errors in both default and target-score modes.
- When run with `--target-score`, the results are correctly sorted by the consistency percentage.
- The command-line output is clear and accurately reflects the active simulation mode and the resulting metrics.
- The existing functionality remains unaffected when the new flag is not used.
