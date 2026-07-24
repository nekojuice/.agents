# Draft schema, rubric, color, and tool model

This file defines everything needed to author a correct `draft.json` and understand what the assembler produces.

## 1. Flat draft format (`draft.json`)

Author this. It is intentionally shallow (2 levels) so cross-references cannot drift — the assembler wires the deep structure.

```jsonc
{
  "library": "once-espejo project analysis",   // storage_name; keep stable to allow later merge
  "elements": [
    {
      "id": "ux-onboarding",                    // stable latin slug, unique, [a-z0-9-]; becomes ele_id
      "text": "First-run guide to create a library from the explorer",
      "storage_cat": "frontend"                 // NEUTRAL filing by source/subsystem, not by dimension
    }
  ],
  "palettes": [
    {
      "name": "Core value",                     // pal_name; keep stable to allow later merge
      "kind": "value",                          // value | health | mixed | custom (stored in metadata)
      "metadata": {},                           // optional; free-form, merged with kind
      "cats": [
        {
          "name": "User experience",            // cat_name; merging key
          "base": 0,                            // cat_base, default 0
          "factor": 1,                          // cat_factor, default 1
          "color": "#4F86C6",                   // cat_color, #RRGGBB; see color guidance
          "group": "experience",               // optional semantic-group hint, stored in metadata for future mixing
          "elements": [
            { "ele": "ux-onboarding", "val": 3 }  // ele = element id above; val in -5..+5
          ]
        }
      ]
    }
  ]
}
```

Rules the assembler enforces (see report):

- Every `elements[].id` is unique and non-empty. An element referenced by a palette but absent from `elements` is an **ERROR** (orphan reference).
- An element may appear in **multiple palettes**, but **at most once per palette** (duplicate within one palette is an ERROR — the tool would reject the second add).
- Named cats per palette (excluding protected cats) must be **≤ 21** (ERROR if over). **> 11** is a WARNING.
- `val` outside −5..+5, negative `base`, or an element that no palette references are **WARNINGs**.
- `color` must be `#RRGGBB` if present; anything else is an ERROR. Omit `color` to leave a cat neutral.
- The assembler always injects the protected cats `未分類` and `通用` into every palette. To place elements into them, name a cat `未分類` or `通用` in the draft — its `base`/`factor`/elements merge into the injected protected cat. Each palette **should normally include a `通用` cat** populated with cross-cutting elements (see section 4); an empty `通用` triggers a WARNING. Only use `未分類` deliberately (parked / undecided elements).

## 2. Scoring rubric

Score consistently; the tool computes `cat total = cat_base + cat_factor × Σ(ele.val)`.

| Field | Meaning | Default | Guidance |
|---|---|---|---|
| `ele.val` | An element's benefit (+) or harm (−) | — | +1 basic feature / −1 minor flaw; +3 core selling point / −3 serious perf issue; +5 epic idea / −5 appalling design; **comment-type element = 0** (use comments sparingly). Stay within −5..+5. |
| `cat.factor` | How much this cat contributes to the whole | 1 | 0.x only if the cat's impact is negligible; > 1 only for outsized impact. |
| `cat.base` | Immediate effect of the cat existing at all | 0 | Keep 0 unless the cat is inherently very valuable or very bad. **Avoid negative `base`** — let `ele.val` carry the negative sign; the cat itself should not go negative unless the user specifically designs it that way. |

Negative-score column (tool-side): for each element `term = base + factor × val`; only `term < 0` terms sum into the cat's negative score. This is why a negative `base` double-counts across every element — another reason to avoid it.

## 3. Color guidance (per cat `color`)

Each cat gets one original `#RRGGBB` color. Future versions will do further score math and color mixing on the relation chart, so pick colors that carry meaning now.

- **Hue = semantic proximity.** Semantically close cats take **nearby hues** on the color wheel; distant concepts take distant hues. (E.g. "merchant operation UX" and "in-app store features" are close → similar hue; "user point accumulation" is farther → different hue.)
- **Spread evenly.** Across a palette's cats, distribute hues around the wheel so they stay visually distinguishable — avoid clustering everything into one region.
- **Lightness/saturation = importance.** The more vivid / important the cat, the brighter and more saturated its color. **Avoid near-white and near-black** (roughly keep L ≈ 35–70%, moderate-to-high saturation).
- **`通用` (common)** is fixed **pure white `#FFFFFF`** by the assembler — don't color it yourself.
- **`未分類` (uncategorized)** has **no** color (neutral theme). It is not scored, not charted.

Practical method: cluster cats into semantic groups, allocate each group a hue band around the wheel, then set lightness/saturation by importance within the allowed range.

## 4. The `通用` (common) cat — cross-cutting elements

`通用` is the hub node pinned at 12 o'clock on the relation chart, present in every palette. It holds **cross-cutting** elements: ones that evaluate the target *as a whole*, horizontally, rather than any single functional area. Do not leave it empty by default — most targets have whole-project properties worth scoring.

**Decision test** — put an element in `通用` when any of these holds:

- (a) it describes the project/design *overall*, not one functional block;
- (b) it would remain true even if any single named cat were removed;
- (c) you would otherwise be tempted to duplicate it into 3+ named cats.

**Primary content: documentation health.** Create **one element per document type that exists** — README, user manual / operation guide, architecture docs (arch/ADR), deployment SOP, project plan / proposal, design mocks, etc. Score each on completeness **and fit** (does it match the actual implementation?):

- Well-written, up-to-date doc → positive `val`.
- Doc exists but is poor or drifted from reality → negative `val`.
- Doc missing → **no element at all** (do not add a 0-score placeholder). Presence/absence then reads at a glance: what exists and is good, what exists and is bad, and what simply isn't there.

**Other candidates by palette kind:**

| Kind | Cross-cutting candidates |
|---|---|
| `value` | overall vision coherence (do all features serve one goal? any "why does this exist" features?), brand / experience consistency (UI style, copy tone, interaction logic across screens) |
| `health` | convention consistency (naming, error-handling patterns, directory structure, terminology aligned across code/docs/UI), developer experience (one-command build/lint/test, environment setup, CI, git hygiene), observability / logging, license & governance (LICENSE, contribution guide, roadmap) |
| any | security / privacy baseline (secret management, input-validation conventions) |

**Promotion rule:** if a cross-cutting concern is the *main axis* of the palette or the project (e.g. documentation health for a documentation tool), promote it to a named cat instead — `通用` holds what is important overall but not any palette's headline.

**Scoring:** keep `通用`'s `factor` at 1 (and `base` at 0) unless the user asks otherwise. Its color is fixed pure white by the assembler.

## 5. Tool data model (what the assembler outputs; for reference)

The importable file is a `Library[]` (usually length 1). You never write this by hand.

```
Library      { storage_id, storage_name, storage_element: StorageCat[], paletas: Palette[] }
StorageCat   { cat_id, cat_name, cat_ele: StorageElement[] }        // element source of truth
StorageElement { ele_id, text }                                     // no score here
Palette      { pal_id, pal_name, metadata: {}, cats: PaletteCat[] }
PaletteCat   { cat_id, cat_name, cat_base, cat_factor, cat_color?, cat_ele: PaletteRef[] }
PaletteRef   { ele_id, val, index }                                 // references StorageElement.ele_id
```

Hidden constraints the assembler handles for you:

- **ids may be any string** — UUIDs are just the app default. The assembler uses stable slugs/indices (`ele_id` = your element `id`; `cat_id`/`pal_id`/`storage_id` = generated indices). Names carry meaning; ids only need to be strings.
- **Protected cats must exist.** The app's delete/uncategorize logic requires a `未分類` cat; the assembler always injects `未分類` and `通用` into storage and every palette.
- `未分類` is never scored/charted. `通用` is pinned to 12 o'clock on the relation chart; other cats follow the palette's array order clockwise (so cat order in the draft matters for chart layout).
- **Merge keys on names** (`storage_name`, `pal_name`, `cat_name`, and `ele_id`). Stable names → clean incremental merges on re-run.
