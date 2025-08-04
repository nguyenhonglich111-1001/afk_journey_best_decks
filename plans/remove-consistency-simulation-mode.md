# Feature Implementation Plan: Remove Consistency Simulation Mode

## 📋 Todo Checklist
- [x] ~~Remove `--target-score` argument from `main.py`~~ ✅ Implemented
- [x] ~~Revert `simulator.py` to only calculate and return the average score.~~ ✅ Implemented
- [x] ~~Update `main.py` to remove all consistency-related logic and display formatting.~~ ✅ Implemented
- [x] ~~Final Review and Testing.~~ ✅ Implemented

## 🔍 Analysis & Investigation

### Codebase Structure
- `main.py`: This file currently contains the `--target-score` command-line argument, logic for selecting the simulation mode based on this argument, and conditional formatting for printing consistency results. All of this logic needs to be removed.
- `simulator.py`: The `CardSimulator` class holds the `target_score` state and its evaluation methods (`evaluate_deck`, `find_best_decks`) contain logic to calculate, return, and sort by a `consistency` metric. This logic will be reverted to only handle the average score.
- `plans/consistency-simulation-mode.md`: This file serves as a reference for all the code locations that were touched when the feature was originally added, providing a clear guide for its removal.

### Current Architecture
The architecture separates the CLI/controller (`main.py`) from the simulation engine (`simulator.py`). The removal process will involve simplifying both components. The data flow between the multiprocessing wrapper (`evaluate_deck_wrapper`) and the main loop in `find_best_decks` will be reverted to pass a simple float (the score) instead of a dictionary, which will simplify the data handling.

### Dependencies & Integration Points
- **`argparse`**: The `--target-score` argument will be removed from the parser in `main.py`.
- **`multiprocessing`**: The wrapper function and the result processing loop in `simulator.py` will be simplified, as they will no longer need to handle a dictionary payload.

### Considerations & Challenges
- **Clean Removal**: The main goal is to remove the feature cleanly, ensuring no dead code or vestigial logic remains.
- **Restoring Default Behavior**: It is critical to ensure that the default behavior—finding the deck with the highest average score—is perfectly preserved and functions as the one and only simulation mode.
- **Reverting Data Structures**: The return type of `CardSimulator.evaluate_deck` must be changed back from a dictionary to a float, and all calling functions must be updated to reflect this change.

## 📝 Implementation Plan

### Prerequisites
- No new packages or external dependencies are required.

### Step-by-Step Implementation
1. **Step 1**: Remove the `--target-score` argument and related logic from `main.py`.
   - **Files to modify**: `main.py`
   - **Changes needed**:
     - Delete the `parser.add_argument` call for `"--target-score"`.
     - Remove the `target_score` parameter from the `CardSimulator` instantiation.
     - Delete the entire `elif args.target_score:` block that defines the "consistency" mode. The logic should fall through to the final `else` block which handles the standard high-score analysis.
     - Simplify the results printing loop to remove any conditional formatting for consistency, leaving only the logic that prints the "Expected Score".

2. **Step 2**: Revert `CardSimulator` to remove `target_score` logic.
   - **Files to modify**: `simulator.py`
   - **Changes needed**:
     - In `CardSimulator.__init__`, remove the `target_score` parameter and the `self.target_score` assignment.
     - The `star_thresholds` logic is related to a different feature (`--item`) and should be kept, but the `target_score` path should be removed.

3. **Step 3**: Simplify the deck evaluation and result processing logic.
   - **Files to modify**: `simulator.py`
   - **Changes needed**:
     - In `CardSimulator.evaluate_deck`, remove the calculation for `successful_runs_target`. The function should only calculate and return the average score. The return type hint should be changed from `Dict[str, Any]` back to what it was previously or simply `float` if that was the case. The logic for `star_chances` should remain, but the `elif self.target_score:` block must be removed. The final return value under the default path should just be the score.
     - **Crucially**, the `evaluate_deck` method's return value needs to be consistent. It now returns a dictionary in all cases. To simplify, we will make it return *only* the score float when no special mode is active.
     - Update `evaluate_deck_wrapper` to reflect this. It will now receive a dictionary from `evaluate_deck` and should be simplified or checked to ensure it passes the payload correctly.
     - In `find_best_decks`, simplify the result processing loop. It should no longer look for a 'consistency' key.
     - In `find_best_decks`, remove the conditional sorting logic. The decks should now only be sorted by `score` in all cases, except for the star-optimization mode which has its own sorting key.

4. **Step 4**: Finalize `main.py` to handle the simplified data structure.
   - **Files to modify**: `main.py`
   - **Changes needed**:
     - The loop that prints results in `main` must be simplified. It will no longer receive 'consistency' in its results dictionary. Remove the `elif args.target_score:` block entirely and adjust the final `else` block to be the only path for non-item-based analysis.

### Testing Strategy
1.  **Default Mode Test**: Run the script with a standard crafting type (e.g., `python main.py forging`). The script should execute successfully and display results sorted by "Expected Score".
2.  **Item Mode Test**: Run the script with a special item (e.g., `python main.py forging --item "Carve Box"`). This functionality should remain unaffected, with the simulation running for the specified deck size.
3.  **Argument Removal Test**: Attempt to run the script with the now-removed flag (e.g., `python main.py kitchen --target-score 100`). The script should exit with an "unrecognized arguments" error, confirming the flag has been successfully removed.

## 🎯 Success Criteria
- The application runs without errors.
- The `--target-score` command-line argument is no longer available and attempting to use it causes an error.
- All code related to the "consistency" metric and `target_score` has been cleanly removed from the codebase.
- The application correctly finds and displays the top decks sorted by the highest average score as its default and only behavior (besides the special item modes).
