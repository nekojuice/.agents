# Deliverable skeleton — how to instantiate

This folder is the starting shape of the brand skill that the extraction produces. Copy it into the run's staging area, rename the folder to `<brand>`, then fill each file. Do not copy this `SKELETON.md` into the produced skill.

## Rules for filling

- Every `<…>` is a placeholder. Replace all of them; a produced file must not contain `<brand>`, `<prefix>`, `<role>`, `<component>` or any other angle-bracket placeholder outside code examples that explain notation.
- Sample values in templates (`#000000`, `0px`, `0`, `0ms`) are placeholders, not defaults. Replace them with values taken from the run's research or rebuild data. Never keep a placeholder value because it "looks reasonable".
- Template prose is English. The produced documents follow the project's language: rewrite headings and prose in that language, keep token names, file names, keys and anchors unchanged.
- The produced skill holds no source-project names, paths or research narrative. Traceability (source lines, `used_by`, confidence, lineage, old names) stays in the run in every phase, including P1.
- Lines starting with `> TEMPLATE:` are instructions to the author. Delete them when the section is filled.

## Files

| Skeleton file | Produced file | Written by | Generated or hand-written |
| --- | --- | --- | --- |
| `SKILL.md` | `<brand>/SKILL.md` | packaging worker (authoring) | hand-written; sizes in the reading order measured by command after all files exist |
| `agents/openai.yaml` | `<brand>/agents/openai.yaml` | packaging worker (authoring) | hand-written; policy inverse of `SKILL.md` |
| `DESIGN.md` | `<brand>/DESIGN.md` | packaging worker (authoring) | hand-written rules; every value copied from `tokens.json` |
| `tokens.json` | `<brand>/tokens.json` | packaging worker (data) | single source of every value |
| `components/README.md` | `<brand>/components/README.md` | packaging worker (specs) | catalog rows generated from `components/component-tokens.json`; reading notes hand-written |
| `components/component.template.md` | `<brand>/components/<component>.md` (one per component) | packaging worker (specs) | mechanical sections generated; purpose, accessibility, Do/Don't hand-written |
| `tailwind/index.css` | `<brand>/tailwind/index.css` | packaging worker (migration) | hand-written entry |

Files the scripts generate (not in this skeleton): `tokens.css`, `tokens.dtcg.json`, `tailwind/theme.css`, `data/contrast.json` results, `preview.html`, `preview/tailwind.css`. Files the data worker authors without a template: `components/component-tokens.json`, `data/gaps.json`, `data/contrast.json` definitions, `assets/README.md`, `base.css`, `preview/` fragments, optional `patterns/<pattern>.md` (same section order as the component template).

`scripts/`: copy the extraction skill's `scripts/package/` set into `<brand>/scripts/` unchanged. The produced skill's `SKILL.md` lists them as maintenance-only. A run never edits the copies; a needed change is made in the extraction skill's `scripts/package/` and copied again.

## Produced skill defaults

- Invocation: explicit only. Claude `disable-model-invocation: true`; Codex `policy.allow_implicit_invocation: false`. Change only on the user's decision, and keep the two values inverse.
- `metadata.version`: `"1.0"` on first delivery. Later phases bump the minor segment; bump the major segment only when the user orders it.
- `metadata.last_updated`: current OS local time to the second, obtained by command at the time of writing.
- All links relative to the skill root; the folder must work after being copied to another project.

## Phase usage

| Phase | What the skeleton becomes |
| --- | --- |
| P1 extract | Raw snapshot skill in the same layered schema: tiers `primitive`, `semantic`, `component` as the extraction skill's phase-1 reference assigns them, every entry `origin: source`, no research fields. `tailwind/theme.css` is generated; `tailwind/index.css` comes from this skeleton. `check_package.py --stage data --allow-orphans`. |
| P2 rebuild | Layered skill: tiers `primitive`, `semantic`, `component`; `origin` `source` or `added`; traceability kept in the run's lineage. `check_package.py --stage data`, then `--stage full`, without `--allow-orphans`. |
| P3 migrate | Same values; the web layer expressed in utility CSS. `tailwind/index.css` and the DESIGN.md Tailwind section become mandatory. |
