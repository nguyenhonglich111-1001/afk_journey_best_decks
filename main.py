# Standard library imports
import json
import sys
from typing import Dict, Type

# Local application imports
from crafting.base_crafting import BaseCrafting
from crafting.forging import ForgingCrafting
from crafting.kitchen import KitchenCrafting
from simulator import CardSimulator

# This dictionary maps the string name of a crafting type to its class.
# To add a new crafting type, import its class and add it here.
CRAFTING_TYPE_CLASSES: Dict[str, Type[BaseCrafting]] = {
    "kitchen": KitchenCrafting,
    "forging": ForgingCrafting,
}

def main() -> None:
    """
    Main function to run the crafting simulation.

    It loads card data, lets the user choose a crafting type,
    and runs the simulation to find the best decks.
    """
    try:
        with open('cards.json', 'r') as f:
            cards_data = json.load(f)
    except FileNotFoundError:
        print("Error: cards.json not found. Please make sure the file is in the same directory.")
        return
    except json.JSONDecodeError:
        print("Error: cards.json is not a valid JSON file.")
        return

    available_types = list(CRAFTING_TYPE_CLASSES.keys())

    print("Welcome to the AFK Journey Crafting Simulator!")

    chosen_type_name = ""
    # Check for command-line argument for non-interactive use
    if len(sys.argv) > 1 and sys.argv[1] in available_types:
        chosen_type_name = sys.argv[1]
        print(f"\nRunning analysis for command-line argument: '{chosen_type_name}'")
    # Automatically select if there's only one type
    elif len(available_types) == 1:
        chosen_type_name = available_types[0]
        print(f"Automatically selected the only available crafting type: {chosen_type_name}")
    # Fallback to interactive prompt
    else:
        while chosen_type_name not in available_types:
            print("Available crafting types:", available_types)
            choice = input(f"Enter the crafting type to analyze (e.g., {available_types[0]}): ")
            if choice in available_types:
                chosen_type_name = choice
            else:
                print("Invalid type. Please choose from the list.")

    # --- Simulation ---

    # Get the specific card data and the correct class for the chosen type
    crafting_data = cards_data.get(chosen_type_name)
    CraftingClass = CRAFTING_TYPE_CLASSES.get(chosen_type_name)

    if not crafting_data or not CraftingClass:
        print(f"Error: No data or implementation for '{chosen_type_name}' found.")
        return

    # Create an instance of the chosen crafting class (e.g., KitchenCrafting)
    crafting_instance = CraftingClass(crafting_data)

    # Create a simulator instance with the chosen crafting logic
    simulator = CardSimulator(crafting_instance)

    print(f"\n--- Analyzing Crafting Type: {chosen_type_name} ---")

    deck_sizes_to_check = [3, 4, 5, 6]
    top_n_results = 1

    best_decks = simulator.find_best_decks(deck_sizes_to_check, top_n=top_n_results)

    # --- Results ---
    if best_decks:
        print(f"\n\n--- Top {top_n_results} Highest-Score Decks for '{chosen_type_name}' ---")
        for size, decks in best_decks.items():
            print(f"\n--- Deck Size: {size} ---")
            if not decks:
                print("  No results.")
                continue
            for i, result in enumerate(decks):
                # Format the deck for printing, e.g., "2x Card A, 1x Card B"
                deck_str = ", ".join([f"{count}x {name}" for name, count in result['deck'].items()])
                print(f"  #{i+1}: Expected Score: {result['score']:.2f}")
                print(f"     Deck: {deck_str}")


if __name__ == "__main__":
    main()
