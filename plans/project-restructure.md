# Feature Implementation Plan: Project Restructure

## 📋 Todo Checklist
- [x] ~~Create the new directory structure (`src`, `data`).~~ ✅ Implemented
- [x] ~~Move source code files and directories into `src`.~~ ✅ Implemented
- [x] ~~Move data files into `data`.~~ ✅ Implemented
- [x] ~~Update file paths in the source code to reflect the new structure.~~ ✅ Implemented
- [x] ~~Update `.gitignore` to include the `data/` directory.~~ ✅ Implemented
- [x] ~~Final Review and Testing.~~ ✅ Implemented

## 🔍 Analysis & Investigation

### Codebase Structure
The current project structure keeps all files in the root directory, including source code (`main.py`, `simulator.py`), data files (`cards.json`, `items.json`), and module directories (`crafting/`). This leads to a cluttered root and mixes different types of project assets.

**Files Inspected:**
- `main.py`: To identify data file access and module imports.
- `.gitignore`: To check existing rules.
- `crafting/`: To confirm it's a self-contained module.

### Current Architecture
The architecture is a simple script-based simulator. `main.py` serves as the entry point, orchestrating the simulation defined in `simulator.py` and using crafting logic from the `crafting/` modules. Data is loaded directly from JSON files in the root. This direct file access is the main part that will be impacted by the restructure.

### Dependencies & Integration Points
- The core dependency is on the file system structure. `main.py` uses `open('cards.json')` and `open('items.json')`, assuming they are in the same directory as the script.
- Python's import system currently works because all modules (`simulator`, `crafting`) are in the same root directory, which is implicitly on the `PYTHONPATH`.

### Considerations & Challenges
- **Path Management**: The biggest challenge is ensuring all file paths are correctly updated. Moving the scripts and data will break the current relative path assumptions. The plan addresses this by using paths relative to the script's new location.
- **Running the Script**: Users will need to know the new way to run the application (`python src/main.py`). The testing plan will verify this.
- **Imports**: Moving all source files together into `src` should not break Python's import system, as the relative locations of `main.py`, `simulator.py`, and `crafting/` to each other remain the same.

## 📝 Implementation Plan

### Prerequisites
- No new packages are required. This is a file-system-only change.

### Step-by-Step Implementation
1. **Step 1**: Create the new `src` and `data` directories.
   - **Action**: Create two new folders in the project root: `src` and `data`.

2. **Step 2**: Move all source code into the `src` directory.
   - **Files to move**:
     - `main.py` → `src/main.py`
     - `simulator.py` → `src/simulator.py`
     - `crafting/` → `src/crafting/`

3. **Step 3**: Move all data files into the `data` directory.
   - **Files to move**:
     - `cards.json` → `data/cards.json`
     - `items.json` → `data/items.json`

4. **Step 4**: Update the file paths in `src/main.py` to be location-independent.
   - **Files to modify**: `src/main.py`
   - **Changes needed**: Modify the script to build absolute paths to the data files based on the script's own location. This ensures the script can be run from any directory.
   ```python
   # At the top of main.py, after imports
   SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
   DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
   CARDS_PATH = os.path.join(DATA_DIR, 'cards.json')
   ITEMS_PATH = os.path.join(DATA_DIR, 'items.json')

   # In print_usage_guide()
   # old
   with open('items.json', 'r') as f:
   # new
   with open(ITEMS_PATH, 'r') as f:

   # In main()
   # old
   with open('cards.json', 'r') as f:
       cards_data = json.load(f)
   with open('items.json', 'r') as f:
       items_data = json.load(f)
   # new
   with open(CARDS_PATH, 'r') as f:
       cards_data = json.load(f)
   with open(ITEMS_PATH, 'r') as f:
       items_data = json.load(f)
   ```

5. **Step 5**: Update `.gitignore` to allow the `data` directory.
   - **Files to modify**: `.gitignore`
   - **Changes needed**: The current `.gitignore` does not explicitly ignore the `data` directory, but it's good practice to ensure it's not accidentally ignored by a broad rule. Add a line to explicitly un-ignore it if needed, or simply verify no existing rule blocks it. A simple safeguard is to add `!data/` if a rule like `*` or `data/` were present. Given the current state, no change is likely needed, but this step ensures verification. For the purpose of this plan, we will assume no change is needed unless a conflicting rule is found.

### Testing Strategy
1.  **Run a single item simulation**:
    - **Command**: `python src/main.py --item "Carve Box"`
    - **Expected Outcome**: The script should run without any `FileNotFoundError` and produce the same output as before the restructure.
2.  **Run a batch simulation**:
    - **Command**: `python src/main.py --item all`
    - **Expected Outcome**: The script should run successfully and produce the same grouped report as before.
3.  **Run a general analysis**:
    - **Command**: `python src/main.py forging`
    - **Expected Outcome**: The script should run successfully and produce the same output as before.

## 🎯 Success Criteria
- The project root directory is cleaner, with code and data separated into `src` and `data` directories.
- All simulation modes (`single item`, `batch`, `general`) run correctly from the new `src` directory.
- There are no path-related errors after the restructuring.
