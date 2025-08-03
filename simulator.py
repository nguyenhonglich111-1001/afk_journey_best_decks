# Standard library imports
import random
import sys
from collections import Counter
from itertools import combinations
from typing import List, Dict, Tuple, Set, Any

# Local application imports
from crafting.base_crafting import BaseCrafting, State

class CardSimulator:
    """
    Handles the simulation of card decks to find the ones with the highest
    expected score using Monte Carlo methods.
    """
    def __init__(self, crafting_instance: BaseCrafting) -> None:
        """
        Initializes the simulator with a specific crafting type instance.

        Args:
            crafting_instance: An object that inherits from BaseCrafting
                               (e.g., KitchenCrafting or ForgingCrafting).
        """
        self.crafting = crafting_instance
        self.card_functions = self.crafting.get_card_functions()

    def evaluate_deck(self, deck: Tuple[str, ...], simulations: int = 50000) -> float:
        """
        Runs a Monte Carlo simulation for a given deck to find its average score.

        Args:
            deck (Tuple[str, ...]): A tuple of card names representing the deck.
            simulations (int): The number of simulation runs to perform.
                               Defaults to 50000.

        Returns:
            float: The average score of the deck over all simulations.
        """
        total_score = 0.0

        for _ in range(simulations):
            # Reset the state for each simulation run.
            # These are the state variables that card functions can modify.
            state: State = {
                'yellow': 1,
                'blue': 1,
                'artisan_bonus': 0,
                'forge_expert_bonus': 0,
                'slow_cook_bonus_per_flip': 0,
                'charge_count': 0
            }

            # The order of cards being pulled is random
            shuffled_deck = random.sample(list(deck), len(deck))

            for card_name in shuffled_deck:
                func = self.card_functions.get(card_name)
                if func:
                    # The function modifies the state dictionary in place
                    func(state)

            total_score += state['yellow'] * state['blue']

        return total_score / simulations

    def find_best_decks(self, deck_sizes: List[int], top_n: int = 5) -> Dict[int, List[Dict[str, Any]]]:
        """
        Generates all possible unique decks, evaluates them, and returns the top N.

        Args:
            deck_sizes (List[int]): A list of deck sizes to evaluate.
            top_n (int): The number of top-scoring decks to return for each size.
                         Defaults to 5.

        Returns:
            A dictionary where keys are deck sizes and values are a list
            of the top N scoring decks for that size. Each deck is represented
            as a dictionary containing its score and card composition.
        """
        all_cards: List[str] = self.crafting.get_all_cards()

        print(f"Total available cards: {len(all_cards)}")
        print(f"Card pool: {self.crafting.get_card_pool_info()}")

        results: Dict[int, List[Dict[str, Any]]] = {}
        for size in deck_sizes:
            print(f"\n--- Evaluating decks of size {size} ---")
            if size > len(all_cards):
                print(f"Cannot form a deck of size {size}, not enough cards available.")
                continue

            # Generate unique combinations of cards to avoid redundant simulations
            unique_decks: Set[Tuple[str, ...]] = set(combinations(all_cards, size))

            deck_scores: List[Dict[str, Any]] = []
            num_decks = len(unique_decks)
            print(f"Found {num_decks} unique decks to evaluate...")

            for i, deck in enumerate(unique_decks):
                score = self.evaluate_deck(deck)
                # Store deck as a Counter for readable output
                deck_scores.append({'deck': Counter(deck), 'score': score})

                # Progress indicator
                progress = (i + 1) / num_decks
                sys.stdout.write(f"\r  Progress: [{'#' * int(20 * progress):<20}] {i+1}/{num_decks}")
                sys.stdout.flush()

            print("\nEvaluation complete.")

            # Sort the decks by score in descending order
            deck_scores.sort(key=lambda x: x['score'], reverse=True)
            results[size] = deck_scores[:top_n]

        return results
