# AFK Journey Best Deck Finder

This project is a simulator designed to find the optimal deck of cards for different crafting types in a game.

## Core Components
- `main.py`: The main entry point to run the simulation.
- `simulator.py`: Contains the core Monte Carlo simulation logic to evaluate deck scores.
- `cards.json`: A JSON file that defines the cards, their effects, and quantities for each crafting type (e.g., "kitchen", "forging").
- `crafting/`: A directory containing the Python implementation for the logic of each card defined in `cards.json`.

## How to Run
The simulation is run from the command line. You can specify which crafting type to analyze.

### Syntax
```bash
python main.py [crafting_type]
```

### Examples
To analyze the "kitchen" crafting type:
```bash
python main.py kitchen
```

To analyze the "forging" crafting type:
```bash
python main.py forging
```

If no crafting type is provided, the script will prompt the user to choose from the available types defined in `cards.json`.
