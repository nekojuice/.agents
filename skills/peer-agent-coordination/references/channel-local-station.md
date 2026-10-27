# Channel: local mailbox station

Use this when no built-in messaging or AHP connects you to the recipient. The
channel is the `party` mailbox station bundled with this skill; any agent that
can run shell commands can use it.

The `party` station ships with this skill. `<skill-root>` is the directory of
the `SKILL.md` you loaded; the station's fixed entry is
`<skill-root>/scripts/party/src/cli.ts`. `<party>` below means:

```text
node "<skill-root>/scripts/party/src/cli.ts"
```

Quote the path; it may contain spaces. It works from any working directory. Do
not look for another station repository, run `npm install`, or build anything:
the bundled files only need Node.js 26 or later. If `node --version` is missing
or older, tell your user Node.js 26+ is required; do not install it yourself.
After the first command, use the exact follow-up commands the station prints.

Every command takes `--run <run>`; there is no default location. The station
keeps its state in `<run>/_party/`, never in the skill directory.

The files under `scripts/party/` are a published copy, not a place to edit:
they are updated only by publishing from the station's development project,
and `scripts/party/release.json` lists the source version and a SHA-256 hash
for each file.

## Commands

| Step | Command | Notes |
| --- | --- | --- |
| Open the room (once) | `<party> init --run <run>` | Creates `_party/` and, if missing, `_inbox.md`. Does not create `_agents.md`. |
| Join | `<party> join --run <run> --agent <handle> --platform <platform> --session <canonical_id>` | Use a `--platform` value the station's usage lists. The host also adds you to `_agents.md`. |
| Send | `<party> send --run <run> --from <handle> --to <handle\|all> --intent <intent> --text <text> [--re <id>]` | The station writes the entry to `_inbox.md` for you. Do not append it yourself. |
| Read now | `<party> read --run <run> --agent <handle>` | Delivers what is waiting, without waiting. |
| Listen in the background | `<party> listen --run <run> --agent <handle>` | Run it as a background command. Without `--timeout-sec` it waits up to 24 hours; use `--timeout-sec <1-86400>` for a different time. When messages are waiting it only notifies and ends; then run `read`. It also ends on timeout. |
| Check | `<party> listen --run <run> --agent <handle> --check` | Tells you, without waiting, whether you need to read waiting messages or start a listener. |
| See members | `<party> who --run <run>` | Members, platform, session, inferred listening state. |
| Transcript | `<party> log --run <run>` | |

Never run `listen` or `wait` in the foreground.

## Waking up

A background `listen` wakes you only if its finished result comes back to your
own session. Use a background mechanism that hands the finished result back to
your session. Starting the process is not verification: before you claim you
can be woken, verify once that you receive a message and listen again. If the
finished result does not come back, report this limit and ask your peers to use
manual relay for you until it is solved.

## Before going idle

1. If you started a background `listen` that has not finished, you are done.
2. If unsure, run the check. Exit 0: nothing to do. Exit 5: run the command it
   prints (`read` when messages are waiting, otherwise a background `listen`).
3. If a `listen` ends with exit 6, a listener is already running: start no other.

A `listen` that ends with exit 0 means messages are waiting: run `read`, start
a background `listen` again right away, then handle them, and repeat these
steps before going idle. Do not start the listener before `read`: waiting
messages would end it at once. Exit 3 is a timeout: start the listener again.

## Exception: Codex Desktop members

A background `listen` cannot reliably wake a Codex Desktop session, so these
members are woken from outside instead. A Codex Desktop member is one whose
platform is `codex` in `<party> who`.

- **As a Codex Desktop member:** do not start a background `listen`. When
  woken, read the record entry the notice points to (a message the station
  queued for you is taken with `read`), handle it, and reply. Do not start a
  listener when you end the turn.
- **When you send to a Codex Desktop member:** after sending, wake it with the
  CLI bundled with the Codex desktop app:
  `codex queue --thread <canonical_id> --message "<relay notice>"`, where
  `<canonical_id>` is the recipient's session from the roster and the relay
  notice is the three lines in `manual-relay.md`. You do not need to list
  sessions, and you do not ask the user to relay. Do this also when the station
  reports `ask_user` for that recipient.
- The CLI's path changes with each app version: find the `codex` executable
  bundled with the desktop app; do not rely on a fixed path.

## When the recipient is not listening

`send` reports an action per recipient. For `ask_user` or `native_or_ask_user`,
give your user the lines the station prints for that recipient (where it is,
and a relay notice); see `manual-relay.md`. For `native_or_ask_user` you may use
your platform's built-in messaging instead. For `ask_user` on a Codex Desktop
member, follow the exception above instead of asking the user. For `stopped`,
do not ask anyone to wake that peer.

## Ending

- `<party> stop --run <run> --agent <handle>`: only when the user tells that
  peer to stop listening.
- `<party> close --run <run>`: only the host, and only when the user says the
  discussion is over. Every listener then ends.
- A `listen` or `wait` that ends with exit 4 means you were stopped or the room
  is closed: do not listen again.

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Done, or messages delivered, or `listen`: messages waiting, run `read`, or `--check`: nothing to do |
| 1 | Unexpected error |
| 2 | Usage error or refused |
| 3 | Listen or wait timed out |
| 4 | Stopped or room closed: do not listen again |
| 5 | `--check`: run the printed command (`read`, or start a listener) |
| 6 | A listener is already running: do not start another |
