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
    
    print("Usage:")
    print("  python main.py --item <item_name>      (for item-specific analysis)")
    print("  python main.py <crafting_type>         (for general analysis)")

    # Print available crafting types
    print("\nAvailable Crafting Types (for general analysis):")
    for type_name in CRAFTING_TYPE_CLASSES.keys():
        print(f"  - {type_name}")
        
    # Print available special items
    try:
        with open('items.json', 'r') as f:
            items_data = json.load(f)
        if items_data:
            print("\nAvailable Special Items:")
            for name, data in items_data.items():
                crafting_type = data.get('crafting_type', 'N/A')
                print(f'  - "{name}" (Type: {crafting_type}, Deck Size: {data["deck_size"]})')
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    print("\nExample (Item-specific): python main.py --item \"Carve Box\"")
    print("Example (General): python main.py forging")

def main() -> None:
    """
    Main function to run the crafting simulation.
    """
    parser = argparse.ArgumentParser(description="AFK Journey Crafting Simulator")
    parser.add_argument(
        "crafting_type",
        nargs='?',
        default=None,
        choices=CRAFTING_TYPE_CLASSES.keys(),
        help="The crafting type to analyze (optional if --item is used)."
    )
    parser.add_argument(
        "--item",
        type=str,
        help="The name of a special item to use for the simulation."
    )
    args = parser.parse_args()

    # --- Data Loading ---
    items_data = {}
    try:
        with open('cards.json', 'r') as f:
            cards_data = json.load(f)
        # Always load items_data to check for item-specific crafting_type
        with open('items.json', 'r') as f:
            items_data = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: Data file not found - {e.filename}")
        return
    except json.JSONDecodeError:
        print("Error: A data file is not a valid JSON file.")
        return

    # --- Workflow Selection & Setup ---
    chosen_type_name = None
    active_buff_id = None
    star_thresholds = None
    top_n_results = 2
    deck_sizes_to_check = [3, 4, 5, 6]
    item_name_for_display = None

    if args.item:
        item = items_data.get(args.item)
        if not item:
            print(f"Error: Special item '{args.item}' not found in items.json.")
            return
        
        chosen_type_name = item.get('crafting_type')
        if not chosen_type_name:
            print(f"Error: Item '{args.item}' is missing the 'crafting_type' attribute in items.json.")
            return

        active_buff_id = item.get('buff_id')
        star_thresholds = item.get('star_thresholds')
        deck_sizes_to_check = [item['deck_size']]
        item_name_for_display = args.item
        
        print(f"\n--- Analyzing for Item: {item_name_for_display} ---")
        if star_thresholds:
            print(f"    Crafting Type: {chosen_type_name}")
            print("    Mode: Star-Optimization Analysis")
        else:
            print("    Mode: Highest Average Score (Item-specific)")

    elif args.crafting_type:
        chosen_type_name = args.crafting_type
        print(f"\n--- Analyzing Crafting Type: {chosen_type_name} ---")
        print("    Mode: Finding highest average score decks.")
    
    else:
        # If neither is provided, print usage and exit.
        print_usage_guide()
        return

    # --- Simulation Setup ---
    crafting_data = cards_data.get(chosen_type_name)
    CraftingClass = CRAFTING_TYPE_CLASSES.get(chosen_type_name)
    
    if not crafting_data or not CraftingClass:
        print(f"Error: No data or implementation for '{chosen_type_name}' found.")
        return

    crafting_instance = CraftingClass(crafting_data)
    
    simulator = CardSimulator(
        crafting_instance,
        active_buff_id=active_buff_id,
        star_thresholds=star_thresholds
    )

    # --- Simulation Execution ---
    best_decks = simulator.find_best_decks(deck_sizes_to_check, top_n=top_n_results)

    # --- Results ---
    if best_decks:
        # Determine the output format based on the simulation mode
        if star_thresholds:
            print(f"\n\n--- Best Deck Per Star Level for: {item_name_for_display} ---")
        else:
            print(f"\n\n--- Top {top_n_results} Highest-Score Decks for: {chosen_type_name} ---")

        for size, decks in best_decks.items():
            print(f"\n--- Deck Size: {size} ---")
            if not decks:
                print("  No results.")
                continue

            if star_thresholds:
                for star_num in range(1, len(star_thresholds) + 1):
                    star_key = f"{star_num}_star"
                    result = decks.get(star_key)
                    if not result:
                        continue

                    threshold = star_thresholds[star_num - 1]
                    print(f"\n--- Best Deck for {star_num}-Star ({threshold} pts) ---")
                    
                    deck_str = ", ".join([f"{count}x {name}" for name, count in result['deck'].items()])
                    avg_score = result.get('score', 0)
                    chance = result.get('star_chances', {}).get(star_key, 0)

                    print(f"  Chance to reach {star_num}-Star: {chance:.2f}%")
                    print(f"  Avg Score: {avg_score:.2f}")
                    print(f"  Deck: {deck_str}")
            else:
                # This is now the fallback for the default mode
                for i, result in enumerate(decks):
                    deck_str = ", ".join([f"{count}x {name}" for name, count in result['deck'].items()])
                    avg_score = result.get('score', 0)
                    print(f"  #{i+1}: Expected Score: {avg_score:.2f}")
                    print(f"     Deck: {deck_str}")


if __name__ == "__main__":
    main()
