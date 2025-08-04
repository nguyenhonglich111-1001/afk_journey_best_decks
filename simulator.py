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
    eval_results = simulator_instance.evaluate_deck(deck) # Returns a dict now
    return deck, eval_results


class CardSimulator:
    """
    Handles the simulation of card decks to find the ones with the highest
    expected score or highest consistency using Monte Carlo methods.
    """
    def __init__(
        self,
        crafting_instance: BaseCrafting,
        active_buff_id: Optional[str] = None,
        target_score: Optional[int] = None
    ) -> None:
        """
        Initializes the simulator.

        Args:
            crafting_instance: An object that inherits from BaseCrafting.
            active_buff_id: The unique identifier for a special item buff.
            target_score: The score to check for consistency.
        """
        self.crafting = crafting_instance
        self.card_functions = self.crafting.get_card_functions()
        self.active_buff_id = active_buff_id
        self.target_score = target_score

    def evaluate_deck(self, deck: Tuple[str, ...], simulations: int = 50000) -> Dict[str, float]:
        """
        Runs a Monte Carlo simulation for a given deck.

        Returns a dictionary containing the average score and, if a target_score
        is set, the consistency percentage.
        """
        total_score = 0.0
        successful_runs = 0

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

            final_score = state['yellow'] * state['blue']
            total_score += final_score

            if self.target_score and final_score >= self.target_score:
                successful_runs += 1

        # Prepare results
        results = {'score': total_score / simulations}
        if self.target_score:
            results['consistency'] = (successful_runs / simulations) * 100
        
        return results

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

            for deck, eval_results in results_from_pool:
                deck_info = {
                    'deck': Counter(deck),
                    'score': eval_results.get('score', 0),
                    'consistency': eval_results.get('consistency', 0)
                }
                deck_scores.append(deck_info)

            print("\nEvaluation complete.")

            # Sort based on the simulation mode
            sort_key = 'consistency' if self.target_score else 'score'
            deck_scores.sort(key=lambda x: x[sort_key], reverse=True)
            results[size] = deck_scores[:top_n]

        return results

