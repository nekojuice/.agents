# Run Operations

Mechanics that keep a run reproducible and safe: frozen baselines, staging and swap, the forbid list, tool installs, platform traps, and pause and resume. Gate order is in SKILL.md, Gates; this file covers how each mechanical step is done.

## Contents

- [Frozen baseline](#frozen-baseline)
- [Staging and swap](#staging-and-swap)
- [Forbid list](#forbid-list)
- [Tool downloads](#tool-downloads)
- [Scripts and encoding](#scripts-and-encoding)
- [Browsers](#browsers)
- [Pause and resume](#pause-and-resume)

## Frozen baseline

Before Phase 2 and before Phase 3, after the phase plan is confirmed and before construction starts, freeze the previous deliverable.

1. Commit and tag only when the user asks: under a factory, `orchestrator-factory` hard rule 6 and `commit-message-suggestion` `## Committing on request` decide; without a factory, the same request from the user is required. The tag is annotated (`git tag -a <tag> -m "<phase> baseline"`). Workers never run git. Without that request there is no tag: use the hashed copy (step 4) and never create a commit or tag to get one.
2. With a tag: export a read-only copy for workers with line-ending conversion off, then unpack it into the run's `baseline/` folder, which is what workers read:

   ```text
   git -c core.autocrlf=false archive --format=zip -o <run>/baseline.zip <tag> <deliverable-path>
   python -I -m zipfile -e <run>/baseline.zip <run>/baseline/
   ```

   With `core.autocrlf=true`, a plain export converts text files to CRLF and hashes stop matching.
3. Verify the unpacked files one by one against the tag's blobs, then delete the zip file:

   ```text
   git ls-tree -r -z <tag> <deliverable-path>
   ```

   A blob SHA is `sha1("blob <byte length>\0" + data)`; compute it for each file in `<run>/baseline/` and compare. Use `-z` so non-ASCII file names are not quoted and escaped.
4. Without a tag: copy the current deliverable folder byte for byte into `<run>/baseline/`, and write `<run>/baseline.sha1` with one line per file: the blob SHA (same formula as step 3) of the original file and its relative path. Then verify every file in `<run>/baseline/` against that list with the same SHA check. Workers read the copy exactly as they read an export.

## Staging and swap

Build the new version in the run's staging folder; it replaces the original location only after verification passes. The swap comes first, then the user's acceptance: the user reviews the swapped-in version, and the rollback restores the previous one when the user rejects it.

Preconditions for the swap:

| Precondition | Evidence |
| --- | --- |
| Package check passes (the phase's stage) | Check output saved in the run |
| Independent verification passes | Verifier report, no open `product-fail` |
| Cold-start trial reviewed | Reading log and guess list handled |
| Rollback copy | `<run>/pre-swap/` and `<run>/pre-swap.sha1`, verified (below) |

Rollback copy, made just before the swap and written into the plan's rollback step:

1. Copy the current contents of `<skill-location>/<brand>/` byte for byte into `<run>/pre-swap/`, and write `<run>/pre-swap.sha1`: one line per file, the blob SHA (Frozen baseline, step 3) and the relative path. For a first P1 build the folder does not exist yet: the list is empty.
2. Verify `<run>/pre-swap/` against the list with the same SHA check. A tag is only ever a source for making a copy; the rollback never reads git.

Rollback, when the user rejects the swapped-in version or the in-place check fails:

1. Empty only the contents of `<skill-location>/<brand>/`.
2. Copy `<run>/pre-swap/` back into it (nothing for a first P1 build).
3. Verify the result: the set of relative paths equals the list's path set, and every file's blob SHA matches the list.

Never run git commands that change the index, HEAD or other working-tree paths (`checkout`, `rm`, `reset`, `restore`, `clean`) for a rollback; `git status` may be read to report. Never delete recursively outside the swap target.

Swap: once the preconditions pass, empty only the contents of the skill's target folder (`<skill-location>/<brand>/`), then copy staging in; never delete any path outside that folder. Run the phase's package check again in place, then stop for the user's acceptance (SKILL.md, Gates, step 9).

## Forbid list

A mechanically generated list of words that must not appear in the package. It lives only in the run and is never copied into any deliverable. Format: `assets/forbid-list.template.txt`.

Generate it before work starts, from: site and product names in the previous manuals, project-specific words in old component ids, class names of the source project's stylesheets, structural regexes of the source framework and template engine.

| Section | Matching |
| --- | --- |
| `[allow]` | Brand-layer words always allowed; masked before matching, case-sensitive |
| `[substring]` | Case-insensitive substring in every text file, file names included |
| `[class]` | Only in CSS selectors and HTML class attribute tokens; boundaries may not be `[\w-]` |
| `[regex]` | Python regular expressions over every text file |
| `[section-allow]` | Named sections where framework items of `[class]` and `[regex]` pass (`[substring]` still applies) |

Traps:

- Mask `[allow]` case-sensitively. Case-insensitive masking hides forbidden words that contain an allowed word.
- A check script that contains a forbidden word will hit itself; split such strings in the script source.
- Remove SVG `xmlns` namespace URIs before external-URL and substring checks; they are not external resources.
- Unescape CSS selectors before `[class]` matching (`.<state>\:bg-<name>` otherwise yields a forbidden-looking class).
- A source class can equal a utility name of the new framework. Workers do not edit the list: they use an equivalent arbitrary property and report; the orchestrator decides on `[allow]`.
- Keep `file:` and `http(s):` strings out of docstrings and manuals; the external-resource check cannot tell them from links.
- Notes written for a reusable skill are scanned too, not only the package.

## Tool downloads

Scripts in this skill never reach the network. When a phase needs an outside tool (for example the utility framework's CLI):

1. Ask the user first: name the package, version, source and approximate size.
2. Install inside the run, at a fixed path excluded from version control, never in a system temp folder or globally.
3. Pin an exact version published at least two weeks earlier.
4. Point every cache at the run folder and skip install scripts:

   ```text
   npm install <package>@<version> --prefix <run>/tools/<name> --cache <run>/tools/.npm-cache --ignore-scripts --no-audit --no-fund
   ```

5. Delete the cache after install; keep only what the run uses. Record the tool, version and path in the run state.

## Scripts and encoding

| Trap | Handling |
| --- | --- |
| Console code page is not UTF-8 | Scripts call `sys.stdout.reconfigure(encoding="utf-8")`; `PYTHONIOENCODING` is ignored under `-I` |
| `grep -P` on non-ASCII text in Git Bash | `export LC_ALL=C.UTF-8` first |
| Heredoc-written Python | `\b` can become a backspace and silently produce a regex that never matches. Edit code with a file-editing tool or as a standalone script file |
| Line endings | Export and compare with conversion off; generators write LF |
| Python environment | Use the run's or project's virtual environment, run with `-I`, keep scripts outside folders that hold downloaded material |
| Paths | Every input and output is an argument; no defaults; no absolute paths in deliverables |

## Browsers

| Limit | Workaround |
| --- | --- |
| Built-in browser cannot open local files | Serve the folder on loopback: `python -m http.server <port> --bind 127.0.0.1 --directory <dir>`; stop it when done |
| Built-in browser cannot save screenshots to disk | Use a local headless browser for evidence files |
| Hidden pane loads at width 0 | Set the viewport width, then reload before measuring |
| `focus()` without system focus | Accept a focus measurement only when `:focus` matches |
| Reduced-motion preference | Record `matchMedia('(prefers-reduced-motion: reduce)')`; transitions measured under it are not design values |
| Overflow | Measure `document.documentElement.scrollWidth` against the viewport, not by eye |

After every browser session: close servers, reset emulation, delete temporary storage keys, confirm the product repo is unchanged.

## Pause and resume

- Every stop writes the resume point into the run state file's Stage line (`_status.md` under a factory): phase, step, last finished output, next action. Resuming must not require rereading the conversation.
- Mid-plan rulings go into the plan's revision notes the moment they are made.
- When the user delegates design decisions, keep each decision and its reason in the plan's decision table; decisions stay reversible.
- A worker that stops early returns what it finished, what it did not, and where to restart.
