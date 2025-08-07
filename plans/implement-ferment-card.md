# Feature Implementation Plan: Add Ferment Card

## 📋 Todo Checklist
- [ ] Add new state variable to the simulator
- [ ] Add `Ferment` card definition to `data/cards.json`
- [ ] Implement `Ferment` card logic in `crafting/kitchen.py`
- [ ] Update `Heat Control` logic to consume `Ferment` charges
- [ ] Test the new card's functionality

## 🔍 Analysis & Investigation

### New Card Logic: Ferment
- **Effect**: For each `Ferment` card played, it "charges" one guaranteed successful flip for all future `Heat Control` cards.
- **Stacking**: The effect is cumulative. Playing two `Ferment` cards means the next `Heat Control` will have its first two flips guaranteed to succeed, followed by any flips from its normal PRD chance.
- **State Management**: This requires a new state variable, `guaranteed_hc_flips`, initialized to `0` at the start of each simulation run. `Ferment` will increment this variable, and `Heat Control` will decrement it.

### Files to be Modified
1.  **`simulator.py`**: To add the new `guaranteed_hc_flips` variable to the initial state dictionary in the `evaluate_deck` function.
2.  **`data/cards.json`**: To add the definition for the new `Ferment` card to the "kitchen" crafting type, including its name and quantity.
3.  **`crafting/kitchen.py`**: To add the new `ferment` function and update the `heat_control` function to incorporate the new logic.

### Existing Architecture
The plan follows the existing architecture perfectly. A new state variable is added, a new card function is created to modify that state, and an existing card function is updated to read that state. This maintains the project's data flow and design patterns.

## 📝 Implementation Plan

### Step 1: Add State Variable to Simulator
- **File to modify**: `simulator.py`
- **Changes needed**: In the `evaluate_deck` function, add `hc_guaranteed_flips_level` to the initial `state` dictionary with a value of `0`. This represents the permanent buff level.

### Step 2: Define the Ferment Card
- **File to modify**: `data/cards.json`
- **Changes needed**: Add a new object for the `Ferment` card to the `kitchen` array. Based on the user's notes, there are 2 copies of this card.

```json
{
    "card_name": "Ferment",
    "card_function": "Guarantees the first flip of all future Heat Control cards will succeed. Stacks.",
    "card_quantity": 2
}
```

### Step 3: Implement the Ferment Card Logic
- **File to modify**: `crafting/kitchen.py`
- **Changes needed**:
    1.  Create a new function `ferment(self, state: State) -> State`.
    2.  This function should increment the `hc_guaranteed_flips_level` state variable by 1.

### Step 4: Update Heat Control to Use Ferment Buff
- **File to modify**: `crafting/kitchen.py`
- **Changes needed**: Modify the `heat_control` function to be driven by the `hc_guaranteed_flips_level` buff.
- **Detailed Logic**:
    1.  Remove the single, unconditional flip from the start of the function.
    2.  Read the `hc_guaranteed_flips_level` from the state.
    3.  Loop `hc_guaranteed_flips_level` times, triggering a flip (`_trigger_flip()`) for each level of the buff.
    4.  **Do NOT** reset the `hc_guaranteed_flips_level` variable. It is a persistent buff.
    5.  The existing PRD re-trigger loop should execute *after* these guaranteed flips to potentially add more, random flips.

### Testing Strategy
- **Manual Verification**: After implementation, run a simulation for the `kitchen` crafting type.
- **Command**: `python main.py kitchen`
- **Expected Outcome**:
    1.  The simulation should run without errors.
    2.  The `Card pool` printed for the kitchen evaluation should now include `Ferment: 2`.
    3.  The top decks should logically include `Ferment` in combination with `Heat Control`, especially for higher deck sizes, indicating the synergy is correctly evaluated.

## 🎯 Success Criteria
- The `Ferment` card is successfully integrated into the simulation.
- The `Heat Control` card correctly utilizes the charges from `Ferment`.
- The simulation runs correctly and produces logical results that reflect the new card's synergy.