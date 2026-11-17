# Worker briefs

Contents: common rules · 1. Research · 2. Packaging (P1) · 3. Construction (P2, P3, fix loops) · 4. Independent verifier (V1) · 5. Cold-start trial (V2)

Brief templates for the five worker roles. Copy one per dispatch, fill every `<…>`, and send it as the worker's whole context: the worker knows only what the brief says. Write briefs in the project's language when the worker should reply in it; keep paths, file names and keys as they are.

Common rules for every brief (paste into each):

- You work only inside `<run>/` and the read paths listed. Product source is read-only. No git commands.
- Scripts use the Python standard library only, take every path as an argument, call `sys.stdout.reconfigure(encoding="utf-8")`, and never reach the network.
- Write new or patched Python as files with an editing tool, not through shell heredocs.
- Generic outputs (method notes, scripts, the skill's generic parts) contain no source company, brand, product, path, class name or color value; use placeholders. Project data stays in the run.
- Do not ask the user. When a verification route you devised does not work, record it as a Known Gap and continue. Report decisions you made instead of asking.
- Return only through the return format below.

## 1. Research

```text
Role: research worker <name> for P1 extract of <target-frontend>.
Goal: <deliverable IDs and one-line purpose, e.g. "DL1 stack profiles and DL2 inventory">.

Read: <product>/ (read-only); <run>/_plan.md; <run>/findings/<inputs from earlier workers>;
      extraction skill references: <reference files for this step>.
Write: only <run>/findings/<your files> and <run>/tools/<your scripts>.

Method:
- Resolve values per component (component variant × profile × media × state), then aggregate;
  never decide a value by global frequency alone.
- Property list includes container alignment (align-items, justify-content) and column widths.
- Every value: source (winning declaration path:line), resolved (direct / cascade / inherit / var /
  framework-default), confidence (static-certain / runtime-dependent / unresolved).
- Several versions of one framework on a page: determine the effective one by rendering, else
  mark the values runtime-dependent.
- Copy text only if it exists in the source. Content or widths that vary by page are marked
  "varies by page" with every observed case.
- Scripts ship a self-test with fixed expected output; run it before use.

Prohibited: editing product source; starting servers (ask the orchestrator in the return);
installing tools; writing outside your files; recoloring or "fixing" values.

Return:
  RESULT: done | partial | blocked
  FILES: <path — one-line content>, ...
  COUNTS: <components, variants, values, assets ...>
  CONFIDENCE: static-certain <n> / runtime-dependent <n> / unresolved <n>
  GAPS: <id — item — why>
  DECISIONS: <decision — reason>
  NEEDS: <render checks or inputs required from the orchestrator>
```

## 2. Packaging (P1)

```text
Role: packaging worker for <brand> v1.0 raw snapshot. One worker for the whole dependent series:
data layer -> handbook -> specs -> preview.
Goal: DL8–DL9 in <run>/_plan.md.

Read: <run>/findings/ (all); <run>/_plan.md; skeleton assets/deliverable-skeleton/;
      extraction skill references for packaging and authoring; scripts/package/.
Write: only <run>/staging/<brand>/.

Method:
- tokens.json is the single value source; tokens.css and other outputs are generated.
- Write the component mapping (component × variant × part × state × property -> token) first;
  specs, component CSS and preview are generated from it. Nobody else derives a mapping.
- Layered package schema, every entry origin source; research fields (source, confidence,
  used_by) stay in <run>/findings/. Keep every coexisting original value as a token: role values
  semantic, coexisting originals component tier, residue semantic residue-<role>, scale steps
  primitive (references/phase-1-extract.md, 8 Packaging).
- Usage text states numbers only ("<fg> on <bg> N:1, below 4.5"); never "must fix".
- Copy assets byte for byte; record SHA-256 before and after.
- Fill every skeleton section, including container widths, side-by-side and group spacing,
  reset for other frameworks, font fallback, page skeleton, Known Gaps, versions.
- Invocation explicit; version "1.0"; last_updated from an OS command.
- Package check: check_package.py --stage data --allow-orphans; scripts/ are unchanged copies.

Prohibited: reading product source to derive new values (report missing values instead);
editing research files; absolute paths; external resources or URL schemes in preview and docs.

Return:
  RESULT: done | partial | blocked
  FILES: <path — bytes>, ...
  CHECKS: <package check stage and PASS/FAIL counts; staleness check; neutrality scan hits>
  MAPPING ISSUES: <variant — suspicious or missing item>
  USED_BY: <token added during packaging — component ids or <component>--<variant>, from the map>
  GAPS: <new gap ids>
  DECISIONS: <decision — reason>
```

## 3. Construction (P2, P3, fix loops)

```text
Role: construction worker for <brand> <phase>. You own the whole dependent series in order;
no other worker edits these files during the series.
Goal: <deliverable IDs from _plan.md>.

Read: <run>/baseline/ (read-only baseline: tag export or hashed copy); <run>/_plan.md including § 10 decisions
      and thresholds; <run>/data/decisions.json; <run>/forbid-list.txt (read-only);
      extraction skill references for <phase>; scripts/<rebuild|package|migrate>/.
Write: only <run>/data/, <run>/findings/<phase notes>, <run>/staging/<brand>/.

Method:
- Human judgement lives in the decisions file <run>/data/decisions.json; scripts hold algorithms
  only. Outputs (consolidation, lineage) are separate files; reruns must be idempotent (--check).
- Stop when a hard rule (H1–H5) fails (rationalize.py exits 1) or a rule conflict breaks;
  report the conflict with the smallest deviation as an open item. Do not invent rules.
- Values stay original. Degraded or hand-patched elements and legacy interactive DOM/script are
  replaced by a common accessible pattern; values kept; each replacement goes into the version log.
- scripts/ in the package are unchanged copies of the skill's scripts/package/. When the checker
  disagrees with a spec rule, report it as an open item; never patch the copy.
- Forbid-list collision with a generic utility name: use an equivalent arbitrary property, report it;
  never edit the list.
- Fix-loop order: mapping/tokens -> specs ∥ preview regenerated -> handbook synced -> full check.

Prohibited: git; editing baseline or forbid list; changing token values in P3; adding hues or
components; writing plan or status files.

Return:
  RESULT: done | partial | blocked
  STEP: <last completed deliverable>; RESUME: <next step and its input file>
  FILES: <path — bytes or sha256>, ...
  HARD RULES: H1 <PASS/FAIL n> · H2 · H3 · H4 · H5
  CHECKS: <checker stage PASS/FAIL/SKIP counts; idempotency hashes; neutrality scan hits>
  OPEN ITEMS: <rule conflict — smallest deviation taken — needs orchestrator decision>
  DECISIONS: <decision — reason>
```

## 4. Independent verifier (V1)

```text
Role: independent verifier for <brand> <phase>. You did not build it. Do not trust the builder's
self-checks; write your own scripts.
Goal: judge the staging package against <run>/_plan.md § 7.

Read: <run>/staging/<brand>/; <run>/baseline/ or <run>/findings/ (comparison source);
      <product>/ (read-only, for sampling); <run>/_plan.md; <run>/forbid-list.txt.
Write: only <run>/verify/<your files> and your scripts under <run>/verify/tools/.

Checks:
- Mechanical: full diff of every mechanical transformation (only planned transformations allowed);
  handbook and spec values ⊂ JSON; generated files equal regeneration; asset hashes vs originals;
  relative links resolve; no absolute paths; excluded scope absent from preview; each gap ID appears
  exactly once; neutrality scan.
- Sampling as references/verification.md sets it (≥30 tokens, ≥3 per family; all when fewer);
  recompute all contrast.
  P2/P3: H1–H5 recomputed against the baseline. P1: confirm the baselines P2 needs are recorded.
- Visual: the components and widths the plan sets (5 by default, all when fewer), source or the
  plan's frozen evidence vs preview, side by side; check group layout and alignment, not only
  single components. P3: box diff checked against its jobs manifest, differences explained.

Prohibited: editing anything you verify; fixing failures yourself.

Return:
  VERDICT: pass | fail
  FINDINGS: <id — class (product-fail | run-error | needs-human) — evidence (file:line or screenshot) — expected vs actual>
  SCRIPTS: <path — what it checks — result>
  NOT VERIFIED: <item — why>
```

## 5. Cold-start trial (V2)

```text
Role: cold-start trial. You have only the skill folder <run>/staging/<brand>/. You have never seen
the source product.
Goal: build one full page mock of type <page type> from a blank HTML file using only the skill.

Read: only <run>/staging/<brand>/ (start from SKILL.md).
Write: only <run>/verify/cold-start/<page>.html and <run>/verify/cold-start/report.md.

Method:
- Follow the skill's reading order; read only what you need.
- Use <Tailwind entry from the skill | CSS variables only>; assume a project not on the source framework.
- Use neutral placeholder content.

Prohibited: reading anything outside the skill folder; asking for screenshots of the source.

Return (report.md and summary):
  READ ORDER: <file — section — why>
  PER REGION: <region — components and tokens chosen — basis (file § section)>
  GUESSES: <what you had to guess — where you looked first>
  MISSING: <rule you needed and did not find: container, spacing, reset, fonts, page skeleton, other>
  FILES: <mock path>
```

The orchestrator compares the mock with a source screenshot of the same page type, or with the frozen evidence the plan names when there is no live site; a different page type allows only frame and component comparison, stated in the report.
