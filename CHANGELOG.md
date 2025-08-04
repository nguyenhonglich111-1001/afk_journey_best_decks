# Changelog

All notable changes to this project will be documented in this file.

## [2025-08-04]

### Features
- **Add Alchemy Crafting Type**: Introduced the new "alchemy" crafting type with four unique cards: `Ingredient`, `Grind`, `Enchant`, and `Distill`.
- **Implement New Game Mechanics**: Added logic for highest/lowest color targeting and a future-card debuff system for the `Enchant` card.
- **Add New Alchemy Item**: Added the "Growth Serum" item to `items.json`.

### Fixes
- **Correct Enchant Card Logic**: Updated the `Enchant` card to be affected by its own debuff, ensuring simulation accuracy based on in-game scenarios.
- **Fix Critical Syntax Error**: Resolved a syntax error in `crafting/kitchen.py` that was preventing the application from running.
- **Correct Simulation State**: Removed an unused state variable (`slow_cook_bonus_per_flip`) and restored a missing one (`forge_expert_bonus`) in `simulator.py`.

### Chore
- **Project Health Check**: Performed a full, end-to-end verification of the project's stability and functionality after a major branch merge.
- **Add Dependency Management**: Created a `requirements.txt` file to formalize project dependencies.
- **Add Analysis Documentation**: Created comprehensive plans documenting the post-merge health check and the complete state/card logic.

## [2025-08-03]

### Features

-   **Persistent Self-Correcting PRD System:** Implemented a sophisticated, persistent Pseudo-Random Distribution (PRD) system for the `Heat Control` card. This ensures its re-trigger average matches a specific target over a large number of trials, providing more realistic simulation results that adhere to the law of large numbers.
-   **Special Item Simulation Workflow:** Introduced a new, separate simulation flow for special items that provide unique, persistent buffs. This is triggered by a new `--item` command-line argument, which allows for targeted analysis of specific item/deck combinations.
-   **New Forging Items:** Added the "Carve Box" and "Copper Stewpot" special items, implementing their unique buff logic in the forging card functions.
-   **New Kitchen Item:** Added the "Salted Raisin" special item and its corresponding logic to the `cut` function.
-   **Stacking Charge Mechanic:** Upgraded the "Charge" card from a boolean flag to a stacking counter, allowing multiple charges to be stored and consumed correctly.
-   **Display Max Score:** Enhanced the simulation results to show both the "Expected Score" (average) and the "Max Score" (highest observed outcome), providing a more complete view of a deck's potential.
-   **Interactive Usage Guide:** Improved the main script to provide a helpful usage guide when run without arguments, listing available crafting types and special items.

### Refactor

-   **Apply Python Standards:** Refactored the entire codebase to align with the standards defined in `PYTHOH_RULES.MD`, including adding comprehensive type hinting, standardizing docstrings, and organizing imports.
-   **Data-Driven 'Cut' Card:** Refactored the 'Cut' card to be data-driven, with its min/max values defined in `cards.json` to allow for easier scaling and balance changes.

### Fixes

-   **Prevent UnboundLocalError:** Fixed a bug where `items_data` could be unbound if `items.json` was missing, preventing a potential crash.
-   **Restore Project File:** Restored the `PYTHOH_RULES.MD` file after it was accidentally deleted.

### Documentation

-   **Add Data Standard Rule:** Added a new rule to `PYTHOH_RULES.MD` requiring all cards to have a human-readable description, and updated the "Slow Cook" card's description to be compliant.

## [Unreleased] - Initial Development

### Features

-   **Reworked Kitchen Crafting Logic:** Overhauled the interaction between `Slow Cook` and `Heat Control` cards to match complex, order-dependent game mechanics.
-   **Initial Forging & Kitchen Logic:** Implemented the core simulation logic for all cards.

### Chore

-   **Added Project Configuration Files:** Created `.gitignore` and `gemini.md`.