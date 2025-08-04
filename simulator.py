# Standard library imports
import random
import sys
from collections import Counter
from itertools import combinations
from typing import List, Dict, Tuple, Set, Any, Optional
import multiprocessing
from tqdm import tqdm

# Local application imports
from crafting.base_crafting import BaseCrafting, State


def evaluate_deck_wrapper(args):
    """Helper function to allow instance methods to be used with multiprocessing."""
    simulator_instance, deck = args
    score = simulator_instance.evaluate_deck(deck)
    return deck, score


class CardSimulator:
    """
    Handles the simulation of card decks to find the ones with the highest
    expected score using Monte Carlo methods.
    """
    def __init__(
        self,
        crafting_instance: BaseCrafting,
        active_buff_id: Optional[str] = None
    ) -> None:
        """
        Initializes the simulator.

        Args:
            crafting_instance: An object that inherits from BaseCrafting.
            active_buff_id: The unique identifier for a special item buff
                            to activate for the simulation run.
        """
        self.crafting = crafting_instance
        self.card_functions = self.crafting.get_card_functions()
        self.active_buff_id = active_buff_id

    def evaluate_deck(self, deck: Tuple[str, ...], simulations: int = 50000) -> float:
        """Runs a Monte Carlo simulation for a given deck to find its average score."""
        total_score = 0.0

        for _ in range(simulations):
            # Reset the state for each simulation run.
            state: State = {
                'yellow': 1,
                'blue': 1,
                'artisan_bonus': 0,
                'forge_expert_bonus': 0,
                'slow_cook_bonus_per_flip': 0,
                'slow_cook_all_color_bonus': 0,
                'charge_count': 0,
                # State for special item buffs
                'first_forge_played': False,
            }
            # If a special item buff is active, add its flag to the state
            if self.active_buff_id:
                state[self.active_buff_id] = True

            shuffled_deck = random.sample(list(deck), len(deck))

            for card_name in shuffled_deck:
                func = self.card_functions.get(card_name)
                if func:
                    func(state)

            total_score += state['yellow'] * state['blue']

        return total_score / simulations

    def find_best_decks(self, deck_sizes: List[int], top_n: int = 5) -> Dict[int, List[Dict[str, Any]]]:
        """Generates all possible unique decks, evaluates them, and returns the top N."""
        all_cards: List[str] = self.crafting.get_all_cards()

        print(f"Total available cards: {len(all_cards)}")
        print(f"Card pool: {self.crafting.get_card_pool_info()}")

        results: Dict[int, List[Dict[str, Any]]] = {}
        for size in deck_sizes:
            print(f"\n--- Evaluating decks of size {size} ---")
            if size > len(all_cards):
                print(f"Cannot form a deck of size {size}, not enough cards available.")
                continue

            unique_decks: Set[Tuple[str, ...]] = set(combinations(all_cards, size))

            deck_scores: List[Dict[str, Any]] = []
            num_decks = len(unique_decks)
            print(f"Found {num_decks} unique decks to evaluate...")

            tasks = [(self, deck) for deck in unique_decks]

            with multiprocessing.Pool() as pool:
                results_from_pool = list(tqdm(pool.imap_unordered(evaluate_deck_wrapper, tasks), total=num_decks, desc="Evaluating decks"))

            for deck, score in results_from_pool:
                deck_scores.append({'deck': Counter(deck), 'score': score})

            print("\nEvaluation complete.")

            deck_scores.sort(key=lambda x: x['score'], reverse=True)
            results[size] = deck_scores[:top_n]

        return results
