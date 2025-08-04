# Feature Implementation Plan: Post-Merge Project Health Check

## 📋 Todo Checklist
- [x] Review Git history and status
- [x] Set up the Python environment
- [x] Perform static code analysis
- [x] Execute the application in all modes
- [x] Validate outputs and new features
- [x] Document findings and recommend next steps

## 🔍 Analysis & Investigation

### Codebase Structure
The project is a Python-based Monte Carlo simulator. The main components are:
- `main.py`: The command-line entry point.
- `simulator.py`: The core simulation engine, which uses `multiprocessing` for performance.
- `cards.json` & `items.json`: Data files defining the simulation parameters.
- `crafting/`: A package containing the implementation of different crafting logics.
- `PYTHON_RULES.MD` & `gemini.md`: Documents outlining project standards and guidelines.

### Git History
The `git log` confirms the user's report. A `company` branch was merged into `main`. Prior to the merge, several significant features were added on the `company` branch, including a batch simulation mode (`--item all`), a feature to save reports (`--save-report`), and several refactors. The working directory is currently clean.

### Dependencies & Integration Points
The project has a dependency on the `tqdm` library, as seen in `simulator.py`. There is no `requirements.txt` file to manage dependencies formally.

### Considerations & Challenges
The most significant challenge is the **complete absence of an automated test suite**. The search for test files (e.g., `test_*.py`) or a `tests/` directory came up empty. This means verification must be done manually by running the application and observing its behavior. This process is more time-consuming and error-prone than running a test suite.

## 📝 Implementation Plan

### Prerequisites
A Python environment is required. The plan assumes Python 3 is installed and accessible via the `python` command.

### Step-by-Step Implementation

1.  **Step 1: Verify Git Status**
    - Files to modify: None
    - Action: Run `git status` to ensure the working directory is clean and there are no lingering merge conflicts. The previous analysis showed it was clean, but it's good practice to re-verify.

2.  **Step 2: Install Dependencies**
    - Files to modify: None (though creating `requirements.txt` is recommended)
    - Action: Install the `tqdm` library.
    - Command: `pip install tqdm`
    - Recommendation: After confirming all dependencies, create a `requirements.txt` file for future use with the command `pip freeze > requirements.txt`.

2.5. **Step 2.5: Fix Syntax Error in `crafting/kitchen.py`**
    - Files to modify: `crafting/kitchen.py`
    - Action: Update the `heat_control` function to merge the upgraded logic (applying a bonus to both colors) with the PRD re-trigger mechanism. This resolves the syntax error caused by conflicting implementations.
    - **Implementation Notes**: The function was updated to correctly reflect the card's new, upgraded behavior.
    - **Status**: ✅ Completed

3.  **Step 3: Perform Static Analysis (Linting)**
    - Files to modify: None
    - Action: Run a linter like `flake8` or `pylint` over the codebase to check for syntax errors, style violations (according to `PYTHON_RULES.MD`), and simple logical errors.
    - Command: `flake8 .` or `pylint *.py crafting/*.py`

4.  **Step 4: Execute General Analysis Mode**
    - Files to modify: None
    - Action: Run the simulator for a general `crafting_type`. This will test the core simulation logic without any special item-specific features.
    - Command: `python main.py forging`
    - Verification: Check that the script runs to completion without any tracebacks and prints the top decks for each deck size.

5.  **Step 5: Execute Single Item Analysis Mode**
    - Files to modify: None
    - Action: Run the simulator for a specific item that uses the star-optimization analysis. This tests the more complex analysis path.
    - Command: `python main.py --item "Carve Box"` (or another item from `items.json` with `star_thresholds`).
    - Verification: Check that the script runs to completion and prints the best deck for each star level.

6.  **Step 6: Execute and Validate Batch Analysis Mode**
    - Files to modify: None
    - Action: Run the new batch analysis mode for all items.
    - Command: `python main.py --item all`
    - Verification:
        - The script should run without errors.
        - It should print a consolidated markdown report for all items with `star_thresholds`.
        - The output should be well-formatted and readable.

7.  **Step 7: Validate Saved Report Feature**
    - Files to modify: None (a new file will be created by the script)
    - Action: Run the batch analysis with the `--save-report` flag.
    - Command: `python main.py --item all --save-report`
    - Verification:
        - A new directory named `output/` should be created.
        - A markdown file with a timestamped name (e.g., `report_2025-08-04_19-21-31.md`) should be present in the `output/` directory.
        - The content of the file should be identical to the report printed to the console in the previous step.
        - Check that `output/` is correctly listed in `.gitignore`.

### Testing Strategy
As there are no automated tests, the strategy is based on manual, end-to-end execution of the application's main workflows. Each step in the implementation plan is a test case that verifies a specific part of the application's functionality. The key is to look for runtime errors (exceptions) and to manually inspect the output to ensure it is logical and well-formatted.

## 🎯 Success Criteria
The project is considered "healthy" if:
- All shell commands in the implementation plan execute without raising Python exceptions.
- The output for each command is present, correctly formatted, and appears logical (e.g., decks are composed of valid cards, percentages are calculated).
- The `--save-report` flag successfully creates a non-empty report file in the correct directory.
- Static analysis tools do not report any critical errors.
- **Recommendation:** The immediate next step after verification should be to create a basic test suite (using `pytest`) to prevent similar situations in the future. At a minimum, there should be tests for `evaluate_deck` and the main workflows in `main.py`.
