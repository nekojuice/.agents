# Channel: AHP or a compatible host tool set

Use this when the recipient is on a different platform and both sides support
AHP, the host's live agent-to-agent protocol, or any host tool set with the
same capabilities.

| Capability | Purpose |
| --- | --- |
| Wake / deliver | Starts a new turn in the recipient's session. |
| Discover peers | Maps a roster `canonical_id` to a live session. |
| Read peer context | Gathers context before, or instead of, asking. |
| Create a peer | Adds a peer when the run needs one. |

1. Append the full message to `_inbox.md` (SKILL.md section 4).
2. Resolve the recipient through the discover capability.
3. Wake it once with a short pointer: the message `id` and the record path.
4. Before going idle, keep your background listener running as SKILL.md
   section 5 requires.

If the capabilities are missing on either side, use the next channel in
SKILL.md section 7.
