import random
import sys
from itertools import combinations
from collections import Counter

class CardSimulator:
    """
    Handles the simulation of card decks to find the ones with the highest
    expected score.
    """
    def __init__(self, crafting_instance):
        """
        Initializes the simulator with a specific crafting type instance.
        
        Args:
            crafting_instance: An object that inherits from BaseCrafting 
                               (e.g., KitchenCrafting).
        """
        self.crafting = crafting_instance
        self.card_functions = self.crafting.get_card_functions()

    def evaluate_deck(self, deck, simulations=50000):
        """
        Runs a Monte Carlo simulation for a given deck to find its average score.
        """
        total_score = 0
        
        for _ in range(simulations):
            # Reset the state for each simulation run.
            # These are the state variables that card functions can modify.
            state = {
                'yellow': 1,
                'blue': 1,
                'artisan_bonus': 0,
                'forge_expert_bonus': 0,
                'slow_cook_bonus_per_flip': 0
            }
            
            # The order of cards being pulled is random
            shuffled_deck = random.sample(list(deck), len(deck))
            
            for card_name in shuffled_deck:
                func = self.card_functions.get(card_name)
                if func:
                    # The function modifies the state dictionary
                    func(state)

            total_score += state['yellow'] * state['blue']
            
        return total_score / simulations

    def find_best_decks(self, deck_sizes, top_n=5):
        """
        Generates all possible decks, evaluates them, and returns the top N.
        """
        all_cards = self.crafting.get_all_cards()
        
        print(f"Total available cards: {len(all_cards)}")
        print(f"Card pool: {self.crafting.get_card_pool_info()}")

        results = {}
        for size in deck_sizes:
            print(f"\n--- Evaluating decks of size {size} ---")
            if size > len(all_cards):
                print(f"Cannot form a deck of size {size}, not enough cards available.")
                continue

            # Generate unique combinations of cards to avoid redundant simulations
            unique_decks = set(combinations(all_cards, size))
            
            deck_scores = []
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
