# Feature Implementation Plan: State and Card Logic Verification

## 📋 Todo Checklist
- [x] Analyze initial simulation state
- [x] Create a comprehensive state variable map
- [x] Document Forging card and item logic
- [x] Document Kitchen card and item logic
- [x] Final review of the complete analysis

## 🔍 Analysis & Investigation

### Files Inspected
- `simulator.py`: To understand how the simulation state is initialized and managed.
- `crafting/forging.py`: To analyze the logic of all Forging cards.
- `crafting/kitchen.py`: To analyze the logic of all Kitchen cards.
- `items.json`: To identify all special items and their corresponding state buffs.

### Current Architecture
The simulation architecture is sound. A `state` dictionary is initialized for each simulation run in `simulator.py`. This `state` is then passed sequentially to each card function in a shuffled deck. Each function reads from and writes to this single `state` object, ensuring that effects correctly persist and stack within a single run. Item-specific buffs are added to the state at the beginning of the simulation, allowing card functions to conditionally alter their behavior.

### Considerations & Challenges
The primary challenge is the complexity of the interactions, especially in the `forging` crafting type, where multiple state variables and item buffs can influence a single card's outcome. The analysis requires careful tracing of each variable. The `heat_control` card in `kitchen` also has complex logic with its persistent PRD (Pseudo-Random Distribution) history.

## 📝 Implementation Plan (Analysis and Documentation)

This plan outlines the steps to produce a definitive guide to the simulation's logic, verifying its correctness in the process.

### Step 1: Analyze Initial State
- **Action**: Document the initial state dictionary created in `simulator.py:evaluate_deck`.
- **Result**:
    - `yellow`, `blue`: The base scores, always start at `1`.
    - `artisan_bonus`: Starts at `0`. Used by Forging.
    - `forge_expert_bonus`: Starts at `0`. Used by Forging.
    - `slow_cook_all_color_bonus`: Starts at `0`. Used by Kitchen.
    - `charge_count`: Starts at `0`. Used by Forging.
    - `first_forge_played`: Starts at `False`. Used by Forging.
    - `fe_played_count`: Starts at `0`. Used by Forging.
    - `prd_history`: A dictionary `{ 'hc_plays': 0, 'hc_successes': 0 }` that is passed by reference and persists across all simulations for a single deck evaluation. Used by Kitchen.
    - `[item.buff_id]`: A boolean flag (e.g., `carve_box_buff: True`) is added if an item is active for the simulation.

### Step 2: State Variable Mapping
- **Action**: Create a table that maps every state variable to its purpose and the components that interact with it.

| State Variable                | Crafting Type | Purpose                                                                        | Reads From                               | Writes To                                |
| ----------------------------- | ------------- | ------------------------------------------------------------------------------ | ---------------------------------------- | ---------------------------------------- |
| `yellow`, `blue`              | Both          | The two primary scores that are multiplied for the final result.               | All cards that add points.               | All cards that add points.               |
| `artisan_bonus`               | Forging       | A bonus added to all "Artisan" cards (`Forge`, `Forge Expert`).                | `Forge`, `Forge Expert`                  | `Heat Up`                                |
| `charge_count`                | Forging       | A counter for charges that allow Artisan cards to affect both colors.          | `Forge`, `Forge Expert`                  | `Charge`                                 |
| `first_forge_played`          | Forging       | A flag to ensure the "Carve Box" item buff only applies to the first Forge card. | `Forge`                                  | `Forge`                                  |
| `fe_played_count`             | Forging       | Tracks how many `Forge Expert` cards have been played for its compounding bonus. | `Forge Expert`                           | `Forge Expert`                           |
| `forge_expert_bonus`          | Forging       | A compounding bonus pool for the `Forge Expert` card.                          | `Forge Expert`                           | `Forge Expert`                           |
| `slow_cook_all_color_bonus`   | Kitchen       | A bonus added to every `Heat Control` flip.                                    | `Heat Control`                           | `Slow Cook`                              |
| `prd_history`                 | Kitchen       | A persistent dictionary to manage the self-correcting re-trigger for `Heat Control`. | `Heat Control`                           | `Heat Control`                           |
| `carve_box_buff`              | Forging       | Item Buff: Makes the first `Forge` card affect both colors.                    | `Forge`                                  | `simulator.py`                           |
| `copper_stewpot_buff`         | Forging       | Item Buff: Gives `Forge Expert` a 30% chance to trigger a second time.         | `Forge Expert`                           | `simulator.py`                           |
| `salted_raisin_buff`          | Kitchen       | Item Buff: Makes the `Cut` card always yield its maximum value.                | `Cut`                                    | `simulator.py`                           |

### Step 3: Card and Item Logic Guide
- **Action**: Document the precise logic for every card and item.

---
### **Forging** Card Logic
---
-   **`Heat Up`**
    -   **Effect**: Adds `+3` to the `artisan_bonus` state variable.
    -   **Interaction**: This bonus is read by `Forge` and `Forge Expert`. The effect is permanent for the rest of the run and stacks if multiple `Heat Up` cards are played.

-   **`Charge`**
    -   **Effect**: Increments the `charge_count` state variable by `1`.
    -   **Interaction**: This charge is consumed by the next `Forge` or `Forge Expert` card played, causing that card to apply its points to *both* `yellow` and `blue` scores instead of a random one.

-   **`Ignite`**
    -   **Effect**: Multiplies a random color (`yellow` or `blue`) by `2`.
    -   **Interaction**: This card is self-contained and does not interact with any other state variables.

-   **`Forge`**
    -   **Effect**: Adds `5 + artisan_bonus` to a color.
    -   **Interaction**:
        1.  **Item Buff (`Carve Box`)**: If `carve_box_buff` is `True` AND `first_forge_played` is `False`, this card applies its bonus to *both* colors. It then sets `first_forge_played` to `True`.
        2.  **Charge Consumption**: If the `Carve Box` condition is not met, it checks if `charge_count > 0`. If so, it applies its bonus to *both* colors and decrements `charge_count` by `1`.
        3.  **Default**: If neither of the above is true, it applies its bonus to a single random color.
        4.  Always sets `first_forge_played` to `True` after executing.

-   **`Forge Expert`**
    -   **Effect**: Adds `3 + artisan_bonus + forge_expert_bonus` to a color. It also has a complex self-compounding effect.
    -   **Interaction**:
        1.  Increments `fe_played_count` by `1` for the current run.
        2.  **Base Trigger**: The card always triggers once. The bonus applied is `3 + artisan_bonus + forge_expert_bonus`. After applying the points, it **updates** the `forge_expert_bonus` pool by adding `3 * fe_played_count`.
        3.  **Charge Consumption**: Like `Forge`, this trigger will consume a `charge_count` to apply its bonus to both colors.
        4.  **Item Buff (`Copper Stewpot`)**: If `copper_stewpot_buff` is `True`, there is a 30% chance to trigger the effect a second time. This second trigger reads all the same bonuses, but **does not** update the `forge_expert_bonus` pool.

---
### **Kitchen** Card Logic
---
-   **`Season`**
    -   **Effect**: Multiplies a random color (`yellow` or `blue`) by `2`.
    -   **Interaction**: This card is self-contained.

-   **`Slow Cook`**
    -   **Effect**: Adds `+2` to the `slow_cook_all_color_bonus` state variable.
    -   **Interaction**: This bonus is read by the `Heat Control` card. The effect stacks.

-   **`Cut`**
    -   **Effect**: Adds a random integer between a `min` and `max` value to a random color. The range is defined in `cards.json`.
    -   **Interaction**:
        1.  **Item Buff (`Salted Raisin`)**: If `salted_raisin_buff` is `True`, the bonus is always the `max` value of the range, not a random one.
        2.  **Default**: If the buff is not active, the bonus is a random integer within the defined range.

-   **`Heat Control`**
    -   **Effect**: Triggers a "flip" that adds `3` points to a random color and also adds the current `slow_cook_all_color_bonus` to *both* colors. This card has a chance to re-trigger multiple times.
    -   **Interaction**:
        1.  **Slow Cook Synergy**: Reads the `slow_cook_all_color_bonus` and applies it on every flip.
        2.  **PRD Re-trigger**: The re-trigger chance is not a simple flat percentage. It's a self-correcting system designed to average out to a target number of re-triggers over many simulations. It does this by:
            - Reading the persistent `prd_history` for the deck.
            - Calculating the historical average of re-triggers vs. the target average.
            - Adjusting the chance for the *current* set of flips to be higher if the historical average is too low, and lower if it's too high.
            - Updating the `prd_history` with the results of the current card's flips.

## 🎯 Success Criteria
- The plan is considered complete when this document is generated.
- The analysis accurately reflects the logic within the Python files.
- The card and state descriptions are clear, correct, and provide a definitive guide to the simulation's mechanics.
