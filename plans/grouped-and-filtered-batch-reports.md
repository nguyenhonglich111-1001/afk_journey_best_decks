# Feature Implementation Plan: Grouped and Filtered Batch Reports

## 📋 Todo Checklist
- [x] ~~Add a `--crafting_type` filter to the `--item all` batch mode.~~ ✅ Implemented
- [x] ~~Group the collected simulation results by `crafting_type`.~~ ✅ Implemented
- [x] ~~Update the output formatter to display the grouped results.~~ ✅ Implemented
- [x] ~~Unify the single-item analysis to use the new grouped report format.~~ ✅ Implemented
- [x] ~~Final Review and Testing.~~ ✅ Implemented

## 🔍 Analysis & Investigation

### Codebase Structure
- `main.py`: This is the only file requiring modification. The changes will be focused on the `main` function and the `format_results_for_discord` helper function.
- `collections.defaultdict`: This will be imported to simplify the process of grouping the results.

### Current Architecture
The current `--item all` workflow executes as follows:
1.  Loop through all items in `items.json`.
2.  Run a simulation for each.
3.  Append each result to a flat list (`all_results`).
4.  Pass the flat list to `format_results_for_discord` for formatting.

The proposed architecture introduces two key changes to this flow:
1.  **Filtering**: An initial check will be added inside the main loop to see if a `crafting_type` filter was provided. If so, it will skip any items that do not match the filter.
2.  **Grouping**: After the simulations are complete, the flat `all_results` list will be transformed into a `grouped_results` dictionary. This dictionary will use the `crafting_type` as the key and a list of that type's item results as the value. This grouped structure will then be passed to the formatter, enabling grouped output.

This approach is efficient because it adds the new logic without altering the core simulation or result-generating code, focusing only on the pre- and post-processing of the batch run.

### Dependencies & Integration Points
- **Argument Parsing**: The user request can be fulfilled without changing the `argparse` setup. The existing optional positional argument `crafting_type` can be used as the filter when `item` is "all". The logic `if args.item == "all":` will have a check for `args.crafting_type`.
- **Data Structure**: The most significant change is the transformation of the `all_results` list into a `grouped_results` dictionary before formatting. The `format_results_for_discord` function's signature and internal logic must be updated to handle this new `Dict[str, List[dict]]` structure.

### Considerations & Challenges
- **Code Duplication**: The current `main` function has separate logic paths for single-item analysis and general analysis. To ensure a consistent look and feel, the plan includes refactoring the single-item analysis to also use the new grouped reporting format. This promotes code reuse and a more unified user experience.
- **Clarity of Output**: The new grouped format must be clear. The plan specifies adding a prominent header for each `crafting_type` (e.g., `## 👑 Crafting Type: Forging`) to visually separate the sections in the final report.

## 📝 Implementation Plan

### Prerequisites
- `from collections import defaultdict` should be added to `main.py`.

### Step-by-Step Implementation
1. **Step 1**: Implement the `crafting_type` filter for batch mode.
   - **Files to modify**: `main.py`
   - **Changes needed**:
     - In the `if args.item == "all":` block, before calling `run_simulation_for_item`, add a filtering condition.
     ```python
     # Inside the `for item_name, item_data in items_data.items():` loop
     if args.crafting_type and item_data.get('crafting_type') != args.crafting_type:
         continue
     ```

2. **Step 2**: Group the results by `crafting_type`.
   - **Files to modify**: `main.py`
   - **Changes needed**:
     - After the batch simulation loop finishes and `all_results` is populated, create a `defaultdict(list)`.
     - Iterate through `all_results` and populate the `defaultdict`, using the `crafting_type` from each item's data as the key.
     ```python
     grouped_results = defaultdict(list)
     for result in all_results:
         # We need to fetch the crafting_type again for grouping
         item_name = result.get('item_name')
         crafting_type = items_data.get(item_name, {}).get('crafting_type')
         if crafting_type:
             grouped_results[crafting_type].append(result)
     ```

3. **Step 3**: Update the output formatter to handle grouped data.
   - **Files to modify**: `main.py`
   - **Changes needed**:
     - Change the signature of `format_results_for_discord` to `format_results_for_discord(grouped_results: Dict[str, List[dict]]) -> str`.
     - Rewrite the function's loops to first iterate over the `crafting_type` and then over the items within that type.
     - Add a prominent markdown header for each `crafting_type`.
     ```python
     # Inside format_results_for_discord
     for crafting_type, results_list in grouped_results.items():
         report_parts.append(f"## 👑 Crafting Type: {crafting_type.title()}")
         for result_data in results_list:
             # ... existing item formatting logic ...
     ```

4. **Step 4**: Unify the single-item analysis output.
   - **Files to modify**: `main.py`
   - **Changes needed**:
     - In the `if args.item:` block (for single items), instead of having a separate print block, reuse the new grouped formatting logic.
     - After the single simulation is run, create a `grouped_results` dictionary containing just that one item's results, and call `format_results_for_discord`.
     - This ensures that whether the user runs a batch analysis or a single item analysis, the output format is consistent.

### Testing Strategy
1.  **Filtered Batch Test**: Run `python main.py --item all kitchen`.
    - **Expected Outcome**: The script should only run simulations for "Salted Raisin" and any other kitchen items. The final report should only contain the "Kitchen" group.
2.  **Full Batch Test**: Run `python main.py --item all`.
    - **Expected Outcome**: The script should run simulations for all items. The final report should have a "Kitchen" group and a "Forging" group, with the respective items listed under each.
3.  **Single Item Test**: Run `python main.py --item "Carve Box"`.
    - **Expected Outcome**: The output should be a grouped report containing only the "Forging" group, which in turn contains only the "Carve Box" results. This confirms the output is now consistent across modes.
4.  **General Analysis Regression Test**: Run `python main.py forging`.
    - **Expected Outcome**: This mode's output should remain completely unchanged, as it does not involve star-based analysis and does not use the Discord formatter.

## 🎯 Success Criteria
- When a `crafting_type` is provided with `--item all`, the simulation is correctly filtered.
- The final report for batch mode is cleanly grouped by `crafting_type`.
- The output for a single-item simulation is now consistent with the new grouped report format.
- The general, non-item-based analysis mode is unaffected.
