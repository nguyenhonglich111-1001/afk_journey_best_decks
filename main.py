# Standard library imports
import argparse
import json
import sys
from typing import Dict, Type

# Local application imports
from crafting.base_crafting import BaseCrafting
from crafting.forging import ForgingCrafting
from crafting.kitchen import KitchenCrafting
from simulator import CardSimulator

# This dictionary maps the string name of a crafting type to its class.
CRAFTING_TYPE_CLASSES: Dict[str, Type[BaseCrafting]] = {
    "kitchen": KitchenCrafting,
    "forging": ForgingCrafting,
}

def print_usage_guide():
    """Prints a helpful guide on how to run the script."""
    print("Welcome to the AFK Journey Crafting Simulator!")
    
    print("\nUsage: python main.py <crafting_type> [--item <item_name>]")
    
    # Print available crafting types
    print("\nAvailable Crafting Types:")
    for type_name in CRAFTING_TYPE_CLASSES.keys():
        print(f"  - {type_name}")
        
    # Print available special items
    try:
        with open('items.json', 'r') as f:
            items_data = json.load(f)
        if items_data:
            print("\nAvailable Special Items (use with --item flag):")
            for name, data in items_data.items():
                print(f'  - "{name}" (for deck size {data["deck_size"]})')
    except (FileNotFoundError, json.JSONDecodeError):
        # It's okay if items.json doesn't exist or is invalid, just don't show them.
        pass
    
    print("\nExample (Normal): python main.py forging")
    print('Example (Special): python main.py forging --item "Carve Box"')

def main() -> None:
    """
    Main function to run the crafting simulation.
    """
    # If run without arguments, print the usage guide and exit.
    if len(sys.argv) == 1:
        print_usage_guide()
        return

    parser = argparse.ArgumentParser(description="AFK Journey Crafting Simulator")
    parser.add_argument(
        "crafting_type",
        choices=CRAFTING_TYPE_CLASSES.keys(),
        help="The crafting type to analyze."
    )
    parser.add_argument(
        "--item",
        type=str,
        help="The name of a special item to use for the simulation."
    )
    parser.add_argument(
        "--target-score",
        type=int,
        help="Find decks with the highest chance to meet this target score."
    )
    args = parser.parse_args()

    # --- Data Loading ---
    items_data = {}
    try:
        with open('cards.json', 'r') as f:
            cards_data = json.load(f)
        if args.item:
            with open('items.json', 'r') as f:
                items_data = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: Data file not found - {e.filename}")
        return
    except json.JSONDecodeError:
        print("Error: A data file is not a valid JSON file.")
        return

    # --- Simulation Setup ---
    chosen_type_name = args.crafting_type
    crafting_data = cards_data.get(chosen_type_name)
    CraftingClass = CRAFTING_TYPE_CLASSES.get(chosen_type_name)
    
    if not crafting_data or not CraftingClass:
        print(f"Error: No data or implementation for '{chosen_type_name}' found.")
        return

    crafting_instance = CraftingClass(crafting_data)
    
    # --- Workflow Selection (Normal vs. Special Item vs. Target Score) ---
    active_buff_id = None
    top_n_results = 1 # Show more results by default
    deck_sizes_to_check = [3, 4, 5, 6]

    # Initialize the simulator with the target score if provided
    simulator = CardSimulator(
        crafting_instance,
        target_score=args.target_score
    )

    if args.item:
        # Special Item Workflow
        item = items_data.get(args.item)
        if not item:
            print(f"Error: Special item '{args.item}' not found in items.json.")
            return
        
        print(f"\n--- Analyzing with Special Item: {args.item} ---")
        print(f"    Buff: {item['description']}")
        
        deck_sizes_to_check = [item['deck_size']]
        active_buff_id = item['buff_id']
        # Re-initialize the simulator with the buff
        simulator = CardSimulator(
            crafting_instance,
            active_buff_id=active_buff_id,
            target_score=args.target_score
        )
    elif args.target_score:
        # Target Score Workflow
        print(f"\n--- Analyzing for Target Score: {args.target_score} ---")
        print("    Mode: Finding most consistent decks.")
    else:
        # Normal Workflow (Highest Average Score)
        print(f"\n--- Analyzing Crafting Type: {chosen_type_name} ---")
        print("    Mode: Finding highest average score decks.")

    # --- Simulation Execution ---
    best_decks = simulator.find_best_decks(deck_sizes_to_check, top_n=top_n_results)

    # --- Results ---
    if best_decks:
        # Determine the metric to display based on the simulation mode
        if args.target_score:
            print(f"\n\n--- Top {top_n_results} Most Consistent Decks (Target: {args.target_score}) ---")
            metric_key = 'consistency'
            metric_label = 'Consistency'
            metric_unit = '%'
        else:
            print(f"\n\n--- Top {top_n_results} Highest-Score Decks ---")
            metric_key = 'score'
            metric_label = 'Expected Score'
            metric_unit = ''

        for size, decks in best_decks.items():
            print(f"\n--- Deck Size: {size} ---")
            if not decks:
                print("  No results.")
                continue
            for i, result in enumerate(decks):
                deck_str = ", ".join([f"{count}x {name}" for name, count in result['deck'].items()])
                main_metric_val = result[metric_key]
                avg_score = result['score']
                
                # Format the output string
                if args.target_score:
                    print(f"  #{i+1}: {metric_label}: {main_metric_val:.2f}{metric_unit}")
                    print(f"     Avg Score: {avg_score:.2f}")
                else:
                    print(f"  #{i+1}: {metric_label}: {avg_score:.2f}")

                print(f"     Deck: {deck_str}")

if __name__ == "__main__":
    main()
