# Standard library imports
import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, Type

# Local application imports
from crafting.base_crafting import BaseCrafting
from crafting.forging import ForgingCrafting
from crafting.kitchen import KitchenCrafting
from crafting.alchemy import AlchemyCrafting
from simulator import CardSimulator

# This dictionary maps the string name of a crafting type to its class.
CRAFTING_TYPE_CLASSES: Dict[str, Type[BaseCrafting]] = {
    "kitchen": KitchenCrafting,
    "forging": ForgingCrafting,
    "alchemy": AlchemyCrafting,
}

def print_usage_guide():
    """Prints a helpful guide on how to run the script."""
    print("Welcome to the AFK Journey Crafting Simulator!")
    
    print("\nUsage:")
    print("  python main.py --item <item_name>      (for a single item analysis)")
    print("  python main.py --item all              (for a batch analysis of all items)")
    print("  python main.py <crafting_type>         (for a general analysis)")

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
    
    print("\nExample (Single Item): python main.py --item \"Carve Box\"")
    print("Example (Batch): python main.py --item all")
    print("Example (General): python main.py forging")


def run_simulation_for_item(item_name: str, item_data: dict, cards_data: dict) -> dict:
    """Runs a full simulation for a single item and returns a structured result."""
    chosen_type_name = item_data.get('crafting_type')
    if not chosen_type_name:
        print(f"Warning: Item '{item_name}' is missing 'crafting_type'. Skipping.")
        return {}

    print(f"\n--- Analyzing for Item: {item_name} ---")
    
    crafting_data = cards_data.get(chosen_type_name)
    CraftingClass = CRAFTING_TYPE_CLASSES.get(chosen_type_name)
    
    if not crafting_data or not CraftingClass:
        print(f"Warning: No data or implementation for '{chosen_type_name}'. Skipping.")
        return {}

    crafting_instance = CraftingClass(crafting_data)
    
    simulator = CardSimulator(
        crafting_instance,
        active_buff_id=item_data.get('buff_id'),
        star_thresholds=item_data.get('star_thresholds')
    )
    
    deck_sizes_to_check = [item_data['deck_size']]
    simulation_results = simulator.find_best_decks(deck_sizes_to_check)
    
    # Create a new dictionary to hold metadata and results separately
    return {
        'item_name': item_name,
        'star_thresholds': item_data.get('star_thresholds'),
        'results': simulation_results
    }


def format_results_for_discord(all_results: list) -> str:
    """Formats a list of simulation results into a single Discord-friendly string."""
    report_parts = []
    for result_data in all_results:
        item_name = result_data.get('item_name', 'Unknown Item')
        star_thresholds = result_data.get('star_thresholds')
        simulation_results = result_data.get('results', {})
        
        report_parts.append(f"**Item: {item_name}**")
        
        if not star_thresholds:
            report_parts.append("- No star thresholds defined.")
            continue

        # The results are nested under the deck size key
        deck_size = list(simulation_results.keys())[0]
        decks = simulation_results[deck_size]

        for star_num in range(1, len(star_thresholds) + 1):
            star_key = f"{star_num}_star"
            result = decks.get(star_key)
            if not result:
                continue

            threshold = star_thresholds[star_num - 1]
            chance = result.get('star_chances', {}).get(star_key, 0)
            deck_str = ", ".join([f"{count}x {name}" for name, count in result['deck'].items()])
            
            report_parts.append(
                f"- **Best for {star_num}-Star ({threshold} pts):** {chance:.2f}% | Deck: {deck_str}"
            )
        report_parts.append("---")

    return "\n".join(report_parts)


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
        help="The name of a special item to use for the simulation, or 'all' for batch mode."
    )
    parser.add_argument(
        "--save-report",
        action="store_true",
        help="Save the batch simulation report to a markdown file."
    )
    args = parser.parse_args()

    # --- Data Loading ---
    try:
        with open('cards.json', 'r') as f:
            cards_data = json.load(f)
        with open('items.json', 'r') as f:
            items_data = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: Data file not found - {e.filename}")
        return
    except json.JSONDecodeError:
        print("Error: A data file is not a valid JSON file.")
        return

    # --- Workflow Selection ---
    if args.item == "all":
        print("--- Running simulations for all items. This may take a while... ---")
        all_results = []
        for item_name, item_data in items_data.items():
            # Only run for items that have star thresholds
            if 'star_thresholds' in item_data:
                result = run_simulation_for_item(item_name, item_data, cards_data)
                if result:
                    all_results.append(result)
        
        discord_report = format_results_for_discord(all_results)
        print("\n\n--- Batch Simulation Report ---")
        print(discord_report)

        if args.save_report:
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filepath = os.path.join(output_dir, f"report_{timestamp}.md")
            with open(filepath, "w") as f:
                f.write(discord_report)
            print(f"\nReport saved to: {filepath}")
        return

    # --- Single Run Logic (Item or General) ---
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
        print_usage_guide()
        return

    # --- Simulation Setup & Execution for Single Run ---
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
    
    best_decks = simulator.find_best_decks(deck_sizes_to_check, top_n=top_n_results)

    # --- Results for Single Run ---
    if best_decks:
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
                for i, result in enumerate(decks):
                    deck_str = ", ".join([f"{count}x {name}" for name, count in result['deck'].items()])
                    avg_score = result.get('score', 0)
                    print(f"  #{i+1}: Expected Score: {avg_score:.2f}")
                    print(f"     Deck: {deck_str}")



if __name__ == "__main__":
    main()
