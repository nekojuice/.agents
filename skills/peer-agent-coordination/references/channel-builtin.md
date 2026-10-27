# Channel: same-platform built-in messaging

Use this when you and the recipient run on the same platform and that platform
offers built-in messaging between its sessions (send to another session, list
sessions).

1. Append the full message to `_inbox.md` (SKILL.md section 4).
2. Find the recipient's session by its `canonical_id` with the platform's
   session listing.
3. Send it a short pointer only: the message `id` and the record path.
4. Before going idle, keep your background listener running as SKILL.md
   section 5 requires.

The platform's own permission rules still apply on both sides. A message the
platform holds or refuses is not delivered; if it cannot reach the recipient,
use the next channel in SKILL.md section 7.
