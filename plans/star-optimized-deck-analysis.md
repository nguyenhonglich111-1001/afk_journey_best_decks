# Feature Implementation Plan: Star-Optimized Deck Analysis

## 📋 Todo Checklist
- [x] ~~Update `items.json` to include the new `star_thresholds` attribute.~~ ✅ Implemented
- [x] ~~Modify `simulator.py` to handle multi-target star analysis.~~ ✅ Implemented
- [x] ~~Update `CardSimulator.evaluate_deck` to calculate probabilities for each star threshold.~~ ✅ Implemented
- [x] ~~Refactor the sorting logic in `find_best_decks` to prioritize the highest achievable star.~~ ✅ Implemented
- [x] ~~Update `main.py` to trigger the new analysis mode and display the detailed star-level results.~~ ✅ Implemented
- [x] ~~Final Review and Testing.~~ ✅ Implemented

## 🔍 Analysis & Investigation

### Codebase Structure
- `items.json`: This file will be updated to include a new `star_thresholds` array (e.g., `[200, 400, 600]`) for each item. This will be the data source for the new analysis mode.
- `main.py`: The application's entry point. It will be modified to detect when an item-based analysis is requested, pass the `star_thresholds` to the simulator, and format the new, detailed output.
- `simulator.py`: The core simulation engine. The `CardSimulator` class will be significantly updated to perform the new analysis. It will calculate the probability of reaching each score threshold and return a more complex data structure.

### Current Architecture
The current architecture supports different simulation modes (`--target-score` vs. default highest score). This new feature will extend this concept. Instead of a single target, the simulator will now handle multiple targets (the star thresholds). The logic for triggering this new mode will be tied to the existing `--item` flag, making the user experience intuitive. When an item is specified, the simulation will automatically switch to the star-optimization analysis.

### Dependencies & Integration Points
- **`items.json`**: The new `star_thresholds` attribute is the primary new data dependency.
- **`main.py` / `simulator.py` Interface**: The data passed to the `CardSimulator` constructor will now include the `star_thresholds` list. The data returned from `find_best_decks` will also be more complex, containing the probabilities for each star level.
- **Sorting Logic**: The most complex part of the implementation will be the new sorting algorithm. It needs to find decks that provide the highest chance of reaching the highest possible star level, while also considering the average score as a tie-breaker. This means a deck with a 60% chance of 3 stars is better than a deck with a 99% chance of 2 stars, even if the latter has a higher average score.

### Considerations & Challenges
- **Complex Sorting**: The sorting logic is non-trivial. It must iterate through the star levels from highest to lowest, comparing decks based on their probability of achieving that star. If probabilities are equal, it should fall back to comparing the probability of the next-lower star, and so on. The average score should be the final tie-breaker.
- **Data Structure**: The data structure returned from `evaluate_deck` will change from a simple dictionary to one containing a nested dictionary for star probabilities (e.g., `{'score': 123.4, 'star_chances': {'1_star': 95.0, '2_star': 60.0, '3_star': 15.0}}`). This change needs to be handled correctly throughout the data processing pipeline.
- **Clear Output**: The final output in the console must be very clear, presenting the probability for each star level in an easy-to-read format so the user can make an informed decision.

## 📝 Implementation Plan

### Prerequisites
- The `items.json` file must be manually updated with the `star_thresholds` for the items that should be analyzed with this new mode.

### Step-by-Step Implementation
1. **Step 1**: Update `items.json` with the new `star_thresholds` data.
   - **Files to modify**: `items.json`
   - **Changes needed**: Add the `star_thresholds` array to the relevant items. (User has confirmed this is complete).
     ```json
     "Carve Box": {
         "deck_size": 4,
         "buff_id": "carve_box_buff",
         "description": "The first Forge card affects all colors.",
         "star_thresholds": [200, 400, 600]
     }
     ```

2. **Step 2**: Update the `CardSimulator` to handle star threshold analysis.
   - **Files to modify**: `simulator.py`
   - **Changes needed**:
     - Modify `CardSimulator.__init__` to accept `star_thresholds: Optional[List[int]] = None`.
     - Update `evaluate_deck` to calculate the success rate for each threshold, prioritizing star analysis over single-target analysis.
     ```python
     # In CardSimulator.__init__
     def __init__(
         self,
         crafting_instance: BaseCrafting,
         active_buff_id: Optional[str] = None,
         target_score: Optional[int] = None,
         star_thresholds: Optional[List[int]] = None
     ) -> None:
         self.crafting = crafting_instance
         self.card_functions = self.crafting.get_card_functions()
         self.active_buff_id = active_buff_id
         self.target_score = target_score
         self.star_thresholds = star_thresholds

     # In CardSimulator.evaluate_deck
     def evaluate_deck(self, deck: Tuple[str, ...], simulations: int = 50000) -> Dict[str, Any]:
         total_score = 0.0
         successful_runs_target = 0
         successful_runs_stars = [0] * len(self.star_thresholds) if self.star_thresholds else []

         for _ in range(simulations):
             # ... (simulation logic) ...
             final_score = state['yellow'] * state['blue']
             total_score += final_score

             if self.star_thresholds:
                 for i, threshold in enumerate(self.star_thresholds):
                     if final_score >= threshold:
                         successful_runs_stars[i] += 1
             elif self.target_score and final_score >= self.target_score:
                 successful_runs_target += 1

         results = {'score': total_score / simulations}
         if self.star_thresholds:
             results['star_chances'] = {
                 f"{i+1}_star": (count / simulations) * 100
                 for i, count in enumerate(successful_runs_stars)
             }
         elif self.target_score:
             results['consistency'] = (successful_runs_target / simulations) * 100
         
         return results
     ```

3. **Step 3**: Implement the advanced sorting logic.
   - **Files to modify**: `simulator.py`
   - **Changes needed**: In `find_best_decks`, add a new sorting path for star analysis. The sort key should be a tuple of the star-level probabilities (from highest to lowest), followed by the average score.
     ```python
     # In CardSimulator.find_best_decks
     # ... (after processing pool results) ...
     if self.star_thresholds:
         num_stars = len(self.star_thresholds)
         deck_scores.sort(
             key=lambda x: tuple(x.get('star_chances', {}).get(f"{i}_star", 0) for i in range(num_stars, 0, -1)) + (x.get('score', 0),),
             reverse=True
         )
     else:
         sort_key = 'consistency' if self.target_score else 'score'
         deck_scores.sort(key=lambda x: x.get(sort_key, 0), reverse=True)
     
     results[size] = deck_scores[:top_n]
     ```

4. **Step 4**: Update `main.py` to trigger the new mode and display the results.
   - **Files to modify**: `main.py`
   - **Changes needed**:
     - When an item is loaded, check if it has `star_thresholds` and pass them to the `CardSimulator`.
     - Create a new display format for the results that shows the probability for each star level.
     ```python
     # In main function's item workflow
     star_thresholds = item.get("star_thresholds")
     simulator = CardSimulator(
         crafting_instance,
         active_buff_id=active_buff_id,
         target_score=args.target_score,
         star_thresholds=star_thresholds
     )

     # In the results printing section
     item_data = items_data.get(args.item, {}) if args.item else {}
     star_thresholds = item_data.get("star_thresholds")

     if star_thresholds:
         print(f"\n\n--- Top {top_n_results} Star-Optimized Decks for: {args.item} ---")
         for size, decks in best_decks.items():
             print(f"\n--- Deck Size: {size} ---")
             if not decks:
                 print("  No results.")
                 continue
             for i, result in enumerate(decks):
                 deck_str = ", ".join([f"{count}x {name}" for name, count in result['deck'].items()])
                 print(f"  #{i+1}: Avg Score: {result.get('score', 0):.2f}")
                 star_chances = result.get('star_chances', {})
                 for star_num in range(1, len(star_thresholds) + 1):
                     star_key = f"{star_num}_star"
                     chance = star_chances.get(star_key, 0)
                     threshold = star_thresholds[star_num - 1]
                     print(f"     {star_num}-Star ({threshold} pts): {chance:.2f}%")
                 print(f"     Deck: {deck_str}")
     else:
         # ... existing result printing logic for target_score and default modes ...
     ```

### Testing Strategy
1.  **Run Star-Optimization Test**: Run the script with an item that has `star_thresholds` (e.g., `python main.py forging --item "Carve Box"`). Verify that the output is formatted correctly, showing the chances for 1-star, 2-star, and 3-star.
2.  **Verify Sorting**: Manually inspect the sorted results to ensure the logic is correct. A deck with a higher chance at a higher star level should always be ranked first. For example, a deck with a 10% chance at 3-stars should be ranked above a deck with a 0% chance at 3-stars but a 99% chance at 2-stars.
3.  **Regression Test**: Run the script in the other modes.
    - With `--target-score` (e.g., `python main.py kitchen --target-score 100`).
    - In default highest-score mode (e.g., `python main.py kitchen`).
    - Verify that the output for these modes has not been affected by the changes.

## 🎯 Success Criteria
- When running a simulation for an item with `star_thresholds`, the output correctly displays the probability of achieving each star level, sorted from lowest to highest star.
- The list of decks is sorted correctly, prioritizing the highest achievable star level, then the next highest, and finally by average score as a tie-breaker.
- The existing `--target-score` and default simulation modes continue to function as expected.
- The application runs without errors in all modes.
