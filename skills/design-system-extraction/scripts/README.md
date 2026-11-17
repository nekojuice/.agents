# scripts

Python 3 standard library only, no network, every input and output path passed as an argument. Run each script with `python -I <script> --help` for the full usage. Self-tests: `extract/selftest.py`, `package/selftest.py`, `rebuild/selftest.py`, `rebuild/colormetrics.py selftest`, and `--selftest` on the other scripts that have one.

| Folder | Script | Purpose | Phase | Key args |
| --- | --- | --- | --- | --- |
| extract | `stack_scan.py` | Group views by their ordered stylesheet stack; engine syntax comes from a preset file (built-in: `plain-html` only; invented example in `assets/stack-preset.example.json`) | 1 extract | `--root` `--webroot` `--ext` `--preset` `--preset-file` `--out` |
| extract | `framework_structure.py` | Structural evidence for a vendored framework stylesheet (comments, non-ASCII, `:root` variables, class tokens absent from a reference copy, probes) | 1 extract | `--css` `--reference` `--probe` `--out` |
| extract | `markup_scan.py` | Class usage (`class`, `className`), conditional classes, inline styles, `<style>` blocks and script-driven class writes | 1 extract | `--root` `--views` `--scripts` `--view-ext` `--exclude` `--out` |
| extract | `asset_scan.py` | Asset inventory: format, pixel size, hash duplicates, references, `url()` and data URIs, SVG and small-PNG colours | 1 extract | `--root` `--assets` `--refs` `--css` `--ref-ext` `--out` |
| extract | `css_index.py` | CSS rule index with specificity and stack-profile ordering; `index` and `query` subcommands | 1 extract | `index --root --include --template-ext --template-comment --template-expr --fallback-encoding --profiles --out`; `query --index --class --page` |
| extract | `batch_query.py` | Run many `css_index.py query` lines against one loaded index | 1 extract | `--index` `--queries` `--out` |
| extract | `profile_diff.py` | Same-selector winners that differ between two stack profiles | 1 extract | `--index` `--a` `--b` `--class` `--selector` |
| extract | `sheet_residue.py` | Declarations of a first-loaded stylesheet that a later copy does not override | 1 extract | `--index` `--first` `--second` `--grep` |
| extract | `contrast.py` | WCAG 2.x contrast, single pair or batch file | 1 extract | `FG BG` `--base`; `--batch` `--out` |
| extract | `selftest.py` | Fixture test of `css_index`, `contrast`, `profile_diff`, `sheet_residue`, `batch_query` | 1 extract | `--tmp` |
| rebuild | `colormetrics.py` | CIELAB, CIEDE2000, colour family and step, contrast; importable module | 2 rebuild | `lab` `de` `contrast` `selftest`; `--family-rules` |
| rebuild | `rationalize.py` | Phase 1 package (read as it stands) to layered primitive / semantic / component draft with lineage and H1-H5 / added-state checks; human judgements only from the decision file; exit 1 on a failed check | 2 rebuild | `--tokens` `--component-map` `--contrast` `--usage` `--decisions` `--out-consolidation` `--out-lineage` `--check` |
| rebuild | `selftest.py` | Runs `rationalize.py` on neutral fixtures: passing run, `--check`, part keys only, failing check exit, required `note_syntax`, `used_by` from research data, and end to end from a Phase 1 package built with the package scripts to a layered package that passes the package check | 2 rebuild | `--keep` |
| package | `build_tokens.py` | `tokens.json` to `tokens.css` and DTCG JSON; prefix from `css.prefix` | 1 extract / 2 rebuild | `--tokens` `--css` `--dtcg` `--check` |
| package | `build_contrast.py` | Recompute `data/contrast.json` from tokens | 1 extract / 2 rebuild | `--tokens` `--contrast` `--check` |
| package | `build_tailwind.py` | `tokens.json` to Tailwind v4 `@theme inline`; breakpoint variants from `breakpoint-<step>` names; other brand naming from `tokens.json` `tailwind` | 1 extract / 2 rebuild / 3 migrate | `--tokens` `--out` `--check` |
| package | `build_preview.py` | Offline `preview.html` from fragments and data files; optional Tailwind CLI compile | 1 extract / 2 rebuild / 3 migrate | `--package` `--tailwind-cli` `--check` |
| package | `check_package.py` | Package gate: schema, tier direction, orphans, literal policy, anchors, Tailwind notation, rebuild equality, DTCG, assets, offline paths, forbid list, invocation policy | 1 extract / 2 rebuild / 3 migrate | `--stage data\|full` `--package` `--forbid-list` `--tailwind-cli` `--expect-version` `--invocation` `--allow-orphans` (Phase 1 only) |
| package | `selftest.py` | Builds neutral fixture packages (a layered one and a Phase 1 snapshot) and runs every package script, including both check stages | 1 extract / 2 rebuild | `--keep` |
| migrate | `residue_scan.py` | Count legacy mechanism residue (block-element-modifier names, forced-state classes, map mechanism keys) | 3 migrate | `--package` `--prefix` `--framework-words` `--json` |
| migrate | `residue_ledger_check.py` | Row-by-row check of the residue ledger (category, disposition, location after disposition, deleted files) | 3 migrate | `<ledger.md>` `--package` `--section` `--categories` `--delete-disposition` |
| migrate | `theme_name_diff.py` | Same-named variables of the brand theme and the framework default theme, equal or different | 3 migrate | `--theme` `--framework-theme` `--tokens-css` |
| verify | `boxdiff.py` | Element-by-element box sizes of old and new previews; `jobs`, `measure` (local headless browser over 127.0.0.1, proxy settings ignored), `diff` | 3 migrate / verify | `jobs --old --new --prefix --widths`; `measure --browser --user-data-dir`; `diff --jobs --raw --tol` |

The `package/` scripts are also copied into a deliverable package's `scripts/` folder. Those copies are not edited inside a run: a needed change is made here and copied again. `check_package.py` loads the generators from `<package>/scripts/` when present, otherwise from its own folder.
