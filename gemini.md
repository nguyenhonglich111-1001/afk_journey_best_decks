# AFK Journey Best Deck Finder

This project is a simulator designed to find the optimal deck of cards for different crafting types in a game.

## Core Components
- `main.py`: The main entry point to run the simulation.
- `simulator.py`: Contains the core Monte Carlo simulation logic to evaluate deck scores.
- `cards.json`: A JSON file that defines the cards, their effects, and quantities for each crafting type (e.g., "kitchen", "forging").
- `crafting/`: A directory containing the Python implementation for the logic of each card defined in `cards.json`.

## Instructions
* always follow the `PYTHON_RULES.md` for Python coding standards overall
* always check `PROJECT_OVERVIEW.md` before starting a new task
* always implement error catching handler
* always implement user-friendly flows
**Commit Workflow:**
    1.  **Write to File:** Always first write the complete, multi-line commit message to a temporary file named `.git_commit_message.txt` in the project root.
    2.  **Commit from File:** Always execute the commit using the command `git commit -F .git_commit_message.txt`.
    3.  **Do Not Delete:** The `.git_commit_message.txt` file should not be deleted after the commit to allow for reuse.
* always commit your code, but let the user (you) handle the `git push` operation manually
* always not change the value of `top_n_results` in `main.py`, the user can change it manually if needed.
* always append to the `.gitignore` file if you add new files that should not be tracked by Git. Don't delete existing entries.
