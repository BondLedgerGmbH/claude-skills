# Meal Planner - Implementation Guide

Step-by-step instructions for Claude to follow when executing this skill. This guide covers the exact tool calls, file operations, and conversation flow needed to produce the two output documents.

## Prerequisites

Before starting, read these files in order:

1. `SKILL.md` - the workflow and rules.
2. `references/user-preferences.md` - the user's personal context (shopping location, equipment, taste preferences).
3. `references/recipe-format.md` - the exact template for the recipes document.
4. `references/shopping-list-format.md` - the exact template for the shopping list document.

Do this at the start of every planning session. Do not skip or rely on memory of previous reads.

---

## Phase 1 - Conversation (Steps 1-3 of SKILL.md)

This phase is conversational. No files are created yet.

### 1.1 - Confirm diet type

Check Claude's auto-memory files for a stored diet preference.

- If found: confirm with the user. E.g. "Planning keto as usual, or switching this week?"
- If not found: ask the user to pick from: Keto, Low-carb high-protein, Vegetarian, Custom.
- If the user changes diet type: use the Edit tool to update the diet preference in `/Users/karolj/.claude/projects/-Users-karolj-Desktop-Claude/memory/MEMORY.md`.

### 1.2 - Gather inputs

Collect all inputs in a single turn if possible. Use the AskUserQuestion tool for structured choices where it makes sense (e.g. cuisine mode, portion confirmation). Use open-ended questions for things like existing ingredients.

Inputs to collect (see SKILL.md Step 2 for full details):

1. Time frame - which days, how many dinners.
2. Portions - confirm defaults (2 adults, 1.1x, 4 portions/dinner) or adjust.
3. Proteins - include/exclude/prioritise. Skip for vegetarian.
4. Allergies/intolerances - ask once, remember for the session.
5. Existing ingredients - ask explicitly: "Do you have any ingredients at home you want to use up? Meats, fish, fresh produce, cheeses, anything perishable especially."
6. Cuisine preferences - mix it up (default), include specific, or full theme.
7. Previous week's plan - ask if they have last week's recipes to avoid repeats. If a file is provided (MD or PDF), read it using the Read tool. Extract only recipe names and ingredient lists. Ignore all other content in the file.

### 1.3 - Present the weekly overview

Build the overview table in the conversation (not as a file). Include:

- The day/dinner/next-day-lunch table.
- A short note on ingredient usage logic.
- A note on cooking style variety.

Wait for explicit confirmation before proceeding. The user may:

- Confirm: proceed to Phase 2.
- Request swaps: adjust the overview and re-present.
- Reject entirely: ask what direction they prefer, regenerate.

Do NOT generate documents until the user confirms the overview.

---

## Phase 2 - Document Generation (Step 5 of SKILL.md)

Once the overview is confirmed, create two MD files.

### 2.1 - Create recipes.md

**Location:** `/Users/karolj/Desktop/Claude/output/meal-plans/recipes.md`

**Structure:** Follow the template in `references/recipe-format.md` exactly. For each dinner in the confirmed overview:

1. Check if the recipe needs advance prep (marinating, brining, etc.). If yes, place the warning block FIRST, before the ingredient table:

> ⚠️ **ADVANCE PREP - START [TIMEFRAME] BEFORE COOKING**
> [What needs to happen and why.]

2. Write the ingredient table for each component (main protein, sides, salad, sauce). Include:
   - Exact quantities scaled to the agreed multiplier.
   - Local language names in parentheses (per user-preferences.md).
   - "ON HAND" suffix for ingredients the user already has.
3. Write numbered instructions. For each step:
   - State the action explicitly (how to cut, what size, what thickness).
   - Include temperature in degrees C with fan equivalent.
   - Include timing.
   - Use culinary terms with inline explanations in parentheses.
4. Write reheating instructions for the next-day lunch.

**Quality checks before presenting:**

- Every ingredient has an explicit quantity (no "some" or "to taste" except salt/pepper).
- All proteins have internal target temperatures.
- All oven steps have fan equivalents.
- Advance prep warnings are at the TOP of the recipe, not buried in steps.
- Portion scale and per-day overrides are correctly applied.
- No ingredients flagged by the diet type rules appear without a note or swap.

### 2.2 - Create shopping-list.md

**Location:** `/Users/karolj/Desktop/Claude/output/meal-plans/shopping-list.md`

**Structure:** Follow the template in `references/shopping-list-format.md` exactly.

**Building the list:**

1. Go through every ingredient in every recipe.
2. Remove any ingredient marked "ON HAND".
3. Group remaining ingredients by category: Meat and Fish (or Proteins for vegetarian), Dairy, Produce, Pantry and Condiments.
4. Consolidate duplicates: if feta appears in two recipes (120 g + 120 g), list once as 240 g.
5. Format each line as: `- English name (local language name) - quantity`
6. For pantry items where a whole bottle/jar is needed, use "small bottle" or "1 jar".
7. For spices that might already be at home, append "(if not at home)".

**Quality checks before presenting:**

- No ON HAND items appear on the list.
- All quantities are consolidated (no ingredient listed twice).
- Categories are in the correct order.
- No tables, no "Used in" columns - bullet list only.

### 2.3 - Present to user

After both files are written, tell the user the files are ready and where they are:

- `/Users/karolj/Desktop/Claude/output/meal-plans/recipes.md`
- `/Users/karolj/Desktop/Claude/output/meal-plans/shopping-list.md`

Keep the response short. The user can open and read the documents themselves.

---

## Phase 3 - Iteration (Step 6 of SKILL.md)

The user will review and request changes. Common patterns:

### Ingredient or protein swap

1. Identify which recipe(s) and ingredient(s) are affected.
2. Use the Edit tool on `recipes.md` to update:
   - The ingredient table (name and quantity).
   - Any instruction steps that reference the old ingredient.
   - Reheating instructions if affected.
3. Use the Edit tool on `shopping-list.md` to update:
   - Remove the old ingredient (if no other recipe uses it).
   - Add the new ingredient (or adjust quantity if it already appears).

### Cooking method change

1. Use the Edit tool on `recipes.md` to rewrite the instructions section.
2. Adjust temperatures, timing, and any equipment references.
3. Shopping list usually unaffected.

### Diet safety question

1. Answer the question directly with specific carb/macro data.
2. If the ingredient is not diet-safe, suggest a swap.
3. If the user confirms the swap, follow the ingredient swap flow above.

### Portion adjustment mid-session

1. Recalculate all quantities in the affected recipe(s).
2. Use the Edit tool to update ingredient quantities in recipes.md.
3. Update the shopping list quantities accordingly in shopping-list.md.

---

## Error Handling

### User uploads a file that is not a meal plan

If the user provides an MD/PDF for "last week's plan" but the content is not a meal plan, inform the user and ask for the correct file. Do not attempt to extract recipe data from non-recipe content.

### Ingredient not available in the user's region

Check `references/user-preferences.md` for the shopping location. If an ingredient is likely hard to find (e.g. Thai basil at a standard European supermarket), flag it proactively and suggest where to find it or offer an alternative.

### Conflicting preferences

If the user's request conflicts with their stored preferences (e.g. requests goat cheese despite a noted dislike), mention the conflict and ask which to follow. The current conversation always takes priority over stored preferences.

---

## File Locations

```
Output files:
  /Users/karolj/Desktop/Claude/output/meal-plans/recipes.md
  /Users/karolj/Desktop/Claude/output/meal-plans/shopping-list.md
```
