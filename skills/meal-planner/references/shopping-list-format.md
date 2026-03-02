# Shopping List Format

## Template

```markdown
# Shopping List

**[Date range]**

---

## Meat & Fish

- Item name in English (item name in local language) — quantity

## Dairy

- Item name in English (item name in local language) — quantity

## Produce

- Item name in English (item name in local language) — quantity

## Pantry & Condiments

- Item name in English (item name in local language) — quantity
```

For vegetarian plans, replace "Meat & Fish" with "Proteins" (tofu, tempeh, etc.) or skip the category if no dedicated protein items are needed.

## Rules

1. Simple bullet list per category. No tables, no extra columns, no "Used in" notes.
2. Each item on its own line: `- English name (local language name) — quantity`
3. Categories always in this order: Meat & Fish (or Proteins), Dairy, Produce, Pantry & Condiments.
4. Exclude items the user confirmed are already at home.
5. Consolidate quantities across recipes. If feta is used in two recipes (120 g + 120 g), list once as 240 g.
6. Group by category, not by recipe. The list is a single unified shopping list.
7. For pantry staples where the user likely needs a whole jar/bottle (e.g. fish sauce, sesame oil), use "small bottle" or "1 jar" instead of exact ml.
8. For spices the user may already have, add "(if not at home)" after the quantity.
