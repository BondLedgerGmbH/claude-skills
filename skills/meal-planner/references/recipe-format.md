# Recipe Document Format

## Template

```markdown
# Recipes

**[Date range] · All recipes scaled to [scale]× · [portions] portions each**

---

## [Day] — [Full Dish Name with Side Description]

> ⚠️ **ADVANCE PREP — START [TIMEFRAME] BEFORE COOKING**
> [What needs to happen and why. Only include this block if advance prep is needed.]

### [Component Name]

| Ingredient | Quantity |
|---|---|
| Ingredient name (local language name) | Amount with unit |
| Ingredient name (local language name) — ON HAND | Amount with unit |

**Instructions**

1. Numbered step with explicit detail.
2. Include temperatures in °C (fan equivalent).
3. Include internal temperatures for proteins.
4. Include timing for each step.
5. Describe physical actions explicitly: how to cut, what size, what shape.

### [Next Component]

(repeat ingredient table + instructions pattern)

### Reheating ([Next Day] Lunch)

Specific reheating method, temperature, and timing. Note which components are good cold vs need reheating.

---

(repeat for each day)

## Notes

- All portions scaled to [scale]× standard servings
- Each recipe produces [portions] portions
- Reheating tips included for each next-day lunch
```

## Rules

1. Every ingredient must have an explicit quantity. No "some", "a bit of", or "to taste" except for salt/pepper.
2. Mark ingredients the user already has with `— ON HAND` after the ingredient name.
3. Include local language names in parentheses for meats, fish, cheeses, and key produce items (as specified in user-preferences.md).
4. Oven temperatures: always include fan equivalent, e.g. "200 °C (fan 180 °C)".
5. Internal temperatures for proteins: cod 63 °C, chicken thigh 75 °C, chicken/turkey breast 72 °C (let carry-over finish), salmon 52 °C for medium, pork 63 °C, beef mince 74 °C.
6. Use proper culinary terms but always explain them inline in parentheses. Examples:
   - "julienne the carrots (cut into thin matchstick-sized strips, ~3 mm wide)"
   - "deglaze the pan (pour in the wine and scrape up the browned bits from the bottom)"
   - "chiffonade the basil (stack leaves, roll tightly, slice into thin ribbons)"
   - "brunoise the shallot (dice into ~3 mm cubes)"
   - "sear the meat (cook undisturbed on high heat until a deep brown crust forms)"
7. Be explicit about every physical action: how to cut, what size, what shape, what thickness. Never assume the user knows.
8. If any step must happen well before cooking (marinating, brining, resting, rising, defrosting), place the advance prep warning block at the very TOP of that recipe, before the ingredient table. Use the format:
   ```
   > ⚠️ **ADVANCE PREP — START [TIMEFRAME] BEFORE COOKING**
   > [Clear description of what to do and why.]
   ```
9. Scale all quantities according to the agreed portion scale and number of people. Apply per-day overrides if the user specified them.
10. Each recipe must include reheating instructions for the next-day lunch.
