# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Features

-   **Reworked Kitchen Crafting Logic:** Overhauled the interaction between `Slow Cook` and `Heat Control` cards to match complex, order-dependent game mechanics.
    -   `Slow Cook` now functions as an "activator." When played, it sets a bonus value that applies to future `Heat Control` cards.
    -   `Heat Control` now acts as a "trigger." When played, it checks for a pre-existing bonus from `Slow Cook` and applies that bonus value to each of its own trigger events (flips).
    -   This change makes the order of play critical to achieving the maximum score, as `Slow Cook` must be played *before* `Heat Control` to have an effect.

### Fixes

-   **Corrected `Slow Cook` Triggering (Intermediate fix):** Addressed an issue where `Slow Cook` would only trigger once per turn, even if `Heat Control` had multiple successful flips. The logic was temporarily updated to count the number of flips from `Heat Control` and apply the `Slow Cook` bonus for each one. (This logic was later superseded by the feature rework above).

### Chore

-   **Added Project Configuration Files:**
    -   Created a `.gitignore` file to exclude common Python artifacts, environment files (`.env`), and IDE-specific folders from version control.
    -   Created a `gemini.md` file to provide project context, a component overview, and usage instructions for AI-based tools.
