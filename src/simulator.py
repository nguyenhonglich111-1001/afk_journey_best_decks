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
    eval_results = simulator_instance.evaluate_deck(deck)
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
        star_thresholds: Optional[List[int]] = None
    ) -> None:
        """
        Initializes the simulator.

        Args:
            crafting_instance: An object that inherits from BaseCrafting.
            active_buff_id: The unique identifier for a special item buff.
            star_thresholds: A list of scores to check for star-level consistency.
        """
        self.crafting = crafting_instance
        self.card_functions = self.crafting.get_card_functions()
        self.active_buff_id = active_buff_id
        self.star_thresholds = star_thresholds

    def evaluate_deck(self, deck: Tuple[str, ...], simulations: int = 50000) -> Dict[str, Any]:
        """
        Runs a Monte Carlo simulation for a given deck.

        Returns a dictionary containing the average score and other metrics based
        on the simulation mode (star chances or single-target consistency).
        """
        total_score = 0.0
        max_score = 0.0

        # This history object is persistent across all simulations for this one deck.
        # This allows the self-correcting PRD to work over a large sample size.
        prd_history = {
            'hc_plays': 0,
            'hc_successes': 0,
        }
        successful_runs_stars = [0] * len(self.star_thresholds) if self.star_thresholds else []

        for _ in range(simulations):
            # Reset the state for each simulation run
            state: State = {
                'yellow': 1, 'blue': 1, 'artisan_bonus': 0,
                'forge_expert_bonus': 0, 'slow_cook_all_color_bonus': 0,
                'charge_count': 0, 'first_forge_played': False,
                'fe_played_count': 0, 'enchant_debuff': 0,
                'ferment_buff_active': False,
                # Pass a reference to the persistent history into each run.
                'prd_history': prd_history,
            }
            if self.active_buff_id:
                state[self.active_buff_id] = True

            shuffled_deck = random.sample(list(deck), len(deck))

            for card_name in shuffled_deck:
                func = self.card_functions.get(card_name)
                if func:
                    func(state)

            final_score = state['yellow'] * state['blue']
            total_score += final_score

            # Check against star thresholds
            if self.star_thresholds:
                for i, threshold in enumerate(self.star_thresholds):
                    if final_score >= threshold:
                        successful_runs_stars[i] += 1

        # Prepare results
        results = {'score': total_score / simulations}
        if self.star_thresholds:
            results['star_chances'] = {
                f"{i+1}_star": (count / simulations) * 100
                for i, count in enumerate(successful_runs_stars)
            }
        
        return results

    def find_best_decks(self, deck_sizes: List[int], top_n: int = 5) -> Dict[int, Any]:
        """
        Generates all possible unique decks, evaluates them, and returns the top
        results based on the simulation mode.
        """
        all_cards: List[str] = self.crafting.get_all_cards()

        print(f"Total available cards: {len(all_cards)}")
        print(f"Card pool: {self.crafting.get_card_pool_info()}")

        results: Dict[int, Any] = {}
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
                    'star_chances': eval_results.get('star_chances', {})
                }
                deck_scores.append(deck_info)

            print("\nEvaluation complete.")

            # --- Analysis based on simulation mode ---
            if self.star_thresholds:
                best_decks_for_stars: Dict[str, Dict[str, Any]] = {}
                for i in range(1, len(self.star_thresholds) + 1):
                    star_key = f"{i}_star"
                    # Find the deck with the highest chance for this specific star
                    best_deck = max(
                        deck_scores,
                        key=lambda x: x.get('star_chances', {}).get(star_key, 0)
                    )
                    best_decks_for_stars[star_key] = best_deck
                results[size] = best_decks_for_stars
            else:
                # Default behavior: sort by highest average score
                deck_scores.sort(key=lambda x: x.get('score', 0), reverse=True)
                results[size] = deck_scores[:top_n]

        return results


