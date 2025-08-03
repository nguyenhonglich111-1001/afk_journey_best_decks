# Standard library imports
import random
import sys
from collections import Counter
from itertools import combinations
from typing import List, Dict, Tuple, Set, Any, Optional

# Local application imports
from crafting.base_crafting import BaseCrafting, State

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

    def evaluate_deck(self, deck: Tuple[str, ...], simulations: int = 50000) -> Dict[str, float]:
        """
        Runs a Monte Carlo simulation for a given deck to find its average and max score.

        Args:
            deck: A tuple of card names representing the deck.
            simulations: The number of simulation runs to perform.

        Returns:
            A dictionary containing the 'average_score' and 'max_score'.
        """
        total_score = 0.0
        max_score = 0.0

        for _ in range(simulations):
            # Reset the state for each simulation run.
            state: State = {
                'yellow': 1,
                'blue': 1,
                'artisan_bonus': 0,
                'forge_expert_bonus': 0,
                'slow_cook_bonus_per_flip': 0,
                'charge_count': 0,
                'first_forge_played': False,
            }
            if self.active_buff_id:
                state[self.active_buff_id] = True

            shuffled_deck = random.sample(list(deck), len(deck))

            for card_name in shuffled_deck:
                func = self.card_functions.get(card_name)
                if func:
                    func(state)

            current_score = state['yellow'] * state['blue']
            total_score += current_score
            if current_score > max_score:
                max_score = current_score

        average_score = total_score / simulations if simulations > 0 else 0
        return {'average_score': average_score, 'max_score': float(max_score)}

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

            for i, deck in enumerate(unique_decks):
                scores = self.evaluate_deck(deck)
                deck_scores.append({
                    'deck': Counter(deck),
                    'average_score': scores['average_score'],
                    'max_score': scores['max_score']
                })

                progress = (i + 1) / num_decks
                sys.stdout.write(f"\r  Progress: [{'#' * int(20 * progress):<20}] {i+1}/{num_decks}")
                sys.stdout.flush()

            print("\nEvaluation complete.")

            deck_scores.sort(key=lambda x: x['average_score'], reverse=True)
            results[size] = deck_scores[:top_n]

        return results
