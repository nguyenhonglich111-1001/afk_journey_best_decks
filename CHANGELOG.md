# Changelog

All notable changes to this project will be documented in this file.

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