# Standard library imports
import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from typing import Dict, Type

# Local application imports
from crafting.base_crafting import BaseCrafting
from crafting.forging import ForgingCrafting
from crafting.kitchen import KitchenCrafting
from crafting.alchemy import AlchemyCrafting
from simulator import CardSimulator

# --- Path Setup ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
CARDS_PATH = os.path.join(DATA_DIR, 'cards.json')
ITEMS_PATH = os.path.join(DATA_DIR, 'items.json')

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
        with open(ITEMS_PATH, 'r') as f:
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


def run_simulation_for_item(item_name: str, item_data: dict, cards_data: dict, report_type: str = "stars") -> dict:
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
        star_thresholds=item_data.get('star_thresholds'),
        wish_points=item_data.get('wish_points'),
        stamina_cost=item_data.get('stamina_cost')
    )
    
    deck_sizes_to_check = [item_data['deck_size']]
    simulation_results = simulator.find_best_decks(deck_sizes_to_check, report_type=report_type)
    
    # Create a new dictionary to hold metadata and results separately
    return {
        'item_name': item_name,
        'star_thresholds': item_data.get('star_thresholds'),
        'stamina_cost': item_data.get('stamina_cost'),
        'results': simulation_results,
        'deck_size': item_data['deck_size']
    }


def format_stars_report(grouped_results: Dict[str, list]) -> str:
    """Formats a dictionary of grouped simulation results into a single Discord-friendly string."""
    report_parts = []
    for crafting_type, results_list in grouped_results.items():
        report_parts.append(f"## [+] Crafting Type: {crafting_type.title()}")
        for result_data in results_list:
            item_name = result_data.get('item_name', 'Unknown Item')
            stamina_cost = result_data.get('stamina_cost')
            simulation_results = result_data.get('results', {})
            
            report_parts.append(f"**Item: {item_name}** (Stamina: {stamina_cost})")
            
            if not simulation_results:
                report_parts.append("- No results found.")
                continue

            deck_size = list(simulation_results.keys())[0]
            deck_results = simulation_results[deck_size]

            # --- Existing Per-Star Analysis Section ---
            if deck_results:
                report_parts.append(f"**Best Deck per Star Level**")
                star_thresholds = result_data.get('star_thresholds', [])
                for i, star_key in enumerate(deck_results):
                    result = deck_results[star_key]
                    threshold = star_thresholds[i]
                    chance = result.get('star_chances', {}).get(star_key, 0)
                    deck_str = ", ".join([f"{count}x {name}" for name, count in result['deck'].items()])
                    report_parts.append(
                        f"- **Best for {i+1}-Star ({threshold} pts):** {chance:.2f}% | Deck: {deck_str}"
                    )
            
            report_parts.append("---")

    return "\n".join(report_parts)

def format_wishpoints_report(grouped_results: Dict[str, list]) -> str:
    """Formats the new report, sorted by Expected Wish Points."""
    report_parts = []
    for crafting_type, results_list in grouped_results.items():
        report_parts.append(f"## [+] Crafting Type: {crafting_type.title()}")
        # Sort items by the top deck's expected wish points
        results_list.sort(
            key=lambda x: (
                x['results'][x['deck_size']][0].get('expected_wish_points', 0) / x.get('stamina_cost', 1)
            ) if x.get('stamina_cost') else 0,
            reverse=True
        )
        for result_data in results_list:
            item_name = result_data.get('item_name', 'Unknown Item')
            stamina_cost = result_data.get('stamina_cost')
            deck_size = result_data.get('deck_size')
            top_deck = result_data['results'][deck_size][0]
            expected_wp = top_deck.get('expected_wish_points', 0)
            wp_per_stamina = expected_wp / stamina_cost if stamina_cost else 0
            deck_str = ", ".join([f"{count}x {name}" for name, count in top_deck['deck'].items()])

            report_parts.append(
                f"**Item: {item_name}** (Stamina: {stamina_cost})")
            report_parts.append(f"  - **Expected Wish Points**: {expected_wp:.2f} (Efficiency: {wp_per_stamina:.2f} WP/Stamina)")
            report_parts.append(f"  - **Deck**: {deck_str}")
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
    parser.add_argument(
        "--report-type",
        type=str,
        default="stars",
        choices=["stars", "wishpoints"],
        help="The type of report to generate: 'stars' for per-star optimization, 'wishpoints' for wish point efficiency."
    )
    args = parser.parse_args()

    # --- Data Loading ---
    try:
        with open(CARDS_PATH, 'r') as f:
            cards_data = json.load(f)
        with open(ITEMS_PATH, 'r') as f:
            items_data = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: Data file not found - {e.filename}")
        return
    except json.JSONDecodeError:
        print("Error: A data file is not a valid JSON file.")
        return

    # --- Workflow Selection ---
    if args.item == "all" or args.crafting_type:
        if args.crafting_type:
            print(f"--- Running simulations for all items of type: {args.crafting_type}. This may take a while... ---")
        else:
            print("--- Running simulations for all items. This may take a while... ---")

        all_results = []
        for item_name, item_data in items_data.items():
            # If a crafting_type is specified, filter by it. Otherwise, run for all.
            if args.crafting_type and item_data.get('crafting_type') != args.crafting_type:
                continue
            
            if 'star_thresholds' in item_data:
                result = run_simulation_for_item(item_name, item_data, cards_data, report_type=args.report_type)
                if result:
                    all_results.append(result)
        
        grouped_results = defaultdict(list)
        for result in all_results:
            # We need to fetch the crafting_type again for grouping
            item_name = result.get('item_name')
            crafting_type = items_data.get(item_name, {}).get('crafting_type')
            if crafting_type:
                grouped_results[crafting_type].append(result)
        
        if args.report_type == "wishpoints":
            discord_report = format_wishpoints_report(grouped_results)
            print("\n\n--- Wish Point Efficiency Report ---")
        else: # "stars"
            discord_report = format_stars_report(grouped_results)
            print("\n\n--- Star-Optimized Analysis Report ---")
        
        print(discord_report)

        if args.save_report:
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"report_{args.report_type}_{timestamp}.md"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w") as f:
                f.write(discord_report)
            print(f"\nReport saved to: {filepath}")
        return

    # --- Single Run Logic (Item) ---
    elif args.item:
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
        top_n_results = 2
        
        print(f"\n--- Analyzing for Item: {item_name_for_display} ---")
        if star_thresholds:
            print(f"    Crafting Type: {chosen_type_name}")
            print(f"    Mode: {args.report_type.title()} Analysis")
        else:
            print("    Mode: Highest Average Score (Item-specific)")
    
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
    
    # Get item data for the simulator
    item_data_for_sim = items_data.get(args.item) if args.item else {}

    simulator = CardSimulator(
        crafting_instance,
        active_buff_id=active_buff_id,
        star_thresholds=star_thresholds,
        wish_points=item_data_for_sim.get('wish_points'),
        stamina_cost=item_data_for_sim.get('stamina_cost')
    )
    
    simulation_results = simulator.find_best_decks(deck_sizes_to_check, report_type=args.report_type)

    # --- Results for Single Run ---
    if simulation_results:
        if star_thresholds:
            # Create a structured result similar to the batch mode
            item_data_for_report = items_data.get(args.item) if args.item else {}
            single_item_result = {
                'item_name': item_name_for_display,
                'star_thresholds': star_thresholds,
                'stamina_cost': item_data_for_report.get('stamina_cost'),
                'results': simulation_results,
                'deck_size': item_data_for_report.get('deck_size')
            }
            
            # Group it for the formatter
            grouped_results = defaultdict(list)
            grouped_results[chosen_type_name].append(single_item_result)
            
            # Format and print
            if args.report_type == "wishpoints":
                discord_report = format_wishpoints_report(grouped_results)
                print(f"\n\n--- Wish Point Efficiency Report for: {item_name_for_display} ---")
            else: # "stars"
                discord_report = format_stars_report(grouped_results)
                print(f"\n\n--- Star-Optimized Analysis Report for: {item_name_for_display} ---")

            print(discord_report)
        else:
            print(f"\n\n--- Top {top_n_results} Highest-Score Decks for: {chosen_type_name} ---")
            for size, decks in simulation_results.items():
                print(f"\n--- Deck Size: {size} ---")
                if not decks:
                    print("  No results.")
                    continue
                
                for i, result in enumerate(decks):
                    deck_str = ", ".join([f"{count}x {name}" for name, count in result['deck'].items()])
                    avg_score = result.get('score', 0)
                    print(f"  #{i+1}: Expected Score: {avg_score:.2f}")
                    print(f"     Deck: {deck_str}")



if __name__ == "__main__":
    main()
