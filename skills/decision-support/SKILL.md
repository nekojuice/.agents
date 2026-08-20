---
name: decision-support
description: >-
  Factor a tangled decision into independent decision nodes, weigh each
  option against the stated goals, and recommend per node without bundling a
  package. Use when a choice mixes several entangled factors, when options have
  been packaged into all-or-nothing bundles, or when the user wants a complex
  decision — in code or in life — laid out as separate choice-axes with
  trade-offs and consequences. Skip for a single, clear, easily reversible
  small decision.
disable-model-invocation: false
metadata:
  author: Claude Code Opus 4.8
  version: "1.0"
  last_updated: "2026-08-20T16:01:21"
---

# decision-support

Turn one tangled decision into a set of independent choice-axes, weigh each on the same fulcrum, and guide axis by axis. This applies anywhere a decision has moving parts — software design, a career move, a purchase, a life choice.

## Factor, don't bundle

A complex decision is a product of independent axes, not a menu of pre-assembled packages. The core move is to expose the axes and let each choice be made on its own.

The anti-pattern is bundling several independent decisions into one option. If auth involves *token vs. session for the API*, *where the frontend keeps credentials*, and *whether passwords are encrypted at rest*, those are **three separate nodes** — not "Plan A / Plan B / Plan C". Bundling explodes the option count, hides the real structure, and forces the user to accept an unwanted half to get a wanted half.

So: decompose into axes, choose per axis, recombine at the end.

## The method

**1. Set the fulcrum.** Before decomposing, establish with the user what the decision is being weighed *for*: the goals and their relative weight (cost, speed, security, reversibility, maintenance effort, whatever applies). Weighing without a fulcrum is just a pros-and-cons list. Everything downstream is measured against this.

**2. Decompose into orthogonal nodes.** Split the problem into decision nodes that are as independent as possible. A node is atomic when swapping its chosen option does **not** force a change in another node. Stop there: splitting past that point adds noise; stopping short of it hides an axis.

**3. Enumerate options per node.** For each node, list its own concrete options — only the ones for that axis.

**4. Weigh, explain, and recommend — per node.** For each option, put it on the fulcrum (what it gains, what it costs, against the stated goals) and state its consequence or its reason (what follows from choosing it, or why it exists). Then give **one recommendation for that node**, with its reason and its consequence.

**5. Recombine — conflicts are first-class.** Assemble the nodes back into a whole and check cross-node relationships:
- Mark dependencies and mutual exclusions between nodes.
- Detect combinations that are invalid (choosing X at one node kills an option at another).
- Turn the per-node recommendations against each other: if node 1 recommends X and node 2 recommends Y but X and Y cannot coexist, name that tension explicitly.

## Output shape

Deliver a structured list or table (table when nodes share uniform attributes; list otherwise). Give each node:

- **Node** — what it is deciding.
- **Options** — the choices on this axis.
- **Per option** — the weighing (gains / costs against the fulcrum) and the consequence or reason.
- **Recommendation** — which option, why, and what choosing it entails.
- **Coupling** — which nodes it depends on or excludes.

Close with a **recombine view**: the cross-node dependencies and conflicts, and any place where the independent recommendations collide.

## Guardrails

- **Recommend per node, never a package.** Give guidance on each axis; do not re-bundle the axes into a single "recommended solution". The user assembles the whole.
- **Surface conflicts; do not resolve them.** When recommendations or choices collide, name the trade-off and hand it back — the user decides which side wins. Do not pick for them.
- **Do not over-decompose.** Respect the atomicity heuristic in step 2. More nodes is not better structure.
