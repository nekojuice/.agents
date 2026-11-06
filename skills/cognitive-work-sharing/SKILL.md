---
name: cognitive-work-sharing
description: >-
  Provides explicitly requested guidance on allocating reasoning, evidence
  gathering, decisions, and cognitive resources in agent-assisted engineering.
  Covers understanding the collaboration model, steering and evaluating agent
  work, and handling accumulated questions or cognitive overload. Explicit
  invocation only; do not activate automatically.
disable-model-invocation: true
metadata:
  author: Codex GPT-6
  version: "1.4"
  last_updated: "2026-11-06T17:58:19"
---

# Sharing Cognitive Work with Agents

A human-facing and agent-readable guide to the philosophy of cognitive work sharing, complemented by references on resource management. Invoke explicitly with `$cognitive-work-sharing` in Codex, `/cognitive-work-sharing` in Claude Code, or a direct request to use this skill. Agents must not activate it automatically. This is not a complete framework operation manual.

Human readers: use this to decide what thinking to retain, delegate, and ask to have explained. Agents: use it to help the operator form a workable allocation of that thinking.

[繁體中文](references/zh-TW.md) contains the same guidance. Read [research and experience notes](references/evidence.md) when explaining the evidence, its limits, or the status of a claim. Do not load every reference for a simple guidance request.

When attention, fatigue, accumulated decisions, or preparation costs become the bottleneck, read [cognitive resource management](references/resource-management.md) ([繁體中文](references/resource-management.zh-TW.md)). It addresses the earlier question of which work deserves cognitive investment, before dividing that work between people and agents.

## 1. The object being operated

An agent-assisted engineering system includes people, agents, instructions, tools, records, and artifacts. Natural-language rules gain concrete meaning through interpretation in a particular situation. People and agents turn them into work, inspect the results, and maintain the rules.

Treat the ability to work at this level as understanding how to organize reasoning and action. Usage count alone does not establish that understanding. Nor does knowing the philosophy establish domain competence or successful delivery. The relative importance of philosophy and experience is not an experimentally established ranking.

This level can organize different artifacts: code, images, models, animation, or engine-produced media. Each medium still needs its own methods and evidence. Cross-medium transfer is a working proposition from the author's practice, not a result demonstrated by the cited coding studies.

## 2. Recognize the load before allocating it

Using an agent can move effort from producing an artifact to specifying intent, tracking context, assessing evidence, resolving ambiguity, and revising the work. More generated output or more agent sessions does not establish more usable delivery.

Do not diagnose an overwhelmed operator as lacking intelligence, diligence, or an innate capacity for abstraction. Examine the work presented to them: repeated questions, missing evidence, stale context, unnecessary interruptions, conflicting reports, or an unresolved substantive decision.

## 3. Separate authority from preparatory thinking

A human decision point reserves authority. It does not require the human to perform every investigation, comparison, or check leading to the decision.

Before returning a question to the operator, determine its kind using available context:

| Kind of work | Appropriate handling |
| --- | --- |
| Already settled in instructions or confirmed decisions | Apply the recorded answer and identify the basis when consequential. |
| A fact that can be established | Inspect the authorized source or arrange the appropriate investigation; report remaining uncertainty. |
| Alternatives whose consequences need understanding | Compare or test them within the task's permissions; bring back evidence and material trade-offs. |
| A decision already delegated within stated bounds | Decide within those bounds and disclose consequential assumptions. |
| Missing human intent, a new value trade-off, or a required approval | Present the unresolved choice with its consequences and an evidence-backed recommendation where possible. |

Do not label every unknown a human decision. Do not infer authorization because a course of action looks technically preferable. If a preference is already stated, apply it rather than asking the person to rediscover it.

## 4. Use agents to work on agent-generated problems

When an agent produces a difficult report, a long question list, or an unfamiliar result, the operator may delegate work on that material: recover its sources, distinguish facts from proposals, find contradictions, test a claim, explain a mechanism, or produce a more decision-ready presentation.

Choose the existing agent, a worker, or an authorized helper according to the work. A new agent and an additional handoff are not inherently improvements. Preserve the original question, relevant constraints, source pointers, evidence, and unresolved uncertainty when work moves.

Agreement between agents is not independent evidence. A second agent may repeat the same assumption or inherit the first agent's framing. Use original sources, observable outcomes, or meaningful tests where available. Stop repeating reviews when they add no new evidence; state what remains unresolved.

## 5. Preserve an actionable understanding

Externalize decisions and context so the operator does not have to keep every detail in working memory. Reuse the project's existing records; do not create a parallel source of truth by default.

Distinguish offloading effort from losing the ability to assess the result. The operator need not personally reconstruct every implementation detail. They need an understanding appropriate to their task, responsibility, and the consequences of being wrong.

If a consequential result is opaque, help build that understanding. Useful forms include a source-grounded walkthrough, an example with counterexamples, a diagram, or a demonstrable explanation of behavior. An agent's explanation is itself a claim to check, not proof merely because it is fluent.

The useful question is: can the operator explain the intended result, the basis for accepting it, the important remaining uncertainty, and how to intervene? Speed alone does not answer that question.

## 6. Guide at the point of difficulty

For conceptual discussion, explain the relevant principles without starting an execution process. For a user who is stuck, identify the immediate obstacle and suggest a proportionate next move.

- Use accessible task context first; ask only for missing information that materially changes the next action.
- Resolve or prepare what is already authorized before presenting the remaining decision.
- Explain why the decision matters now, what the options change, and what evidence supports the recommendation.
- Present enough context to judge the choice without flooding the person with every internal finding.
- If the material remains too hard to assess, help explain or test it rather than repeatedly restating the same question.

Example: a review produces many findings. Before asking for a verdict on every row, check them against the agreed intent, exclude supported false positives, group related causes, and distinguish in-scope corrections from genuine decisions. Retain the complete findings and reasoning where appropriate; a shorter presentation must not hide unresolved problems.

Example: the operator asks only for an independent review of someone else's merge request. Support that review and its interpretation. Do not silently turn it into implementation or a full project-management pipeline.

## 7. Fit the work and respect the existing contract

Understanding the whole system does not require using its heaviest process for every task. Debugging, a standalone review, an experiment, and a substantial delivery can require different arrangements. Explain the arrangement through the outcome, consequences, verification needs, and existing instructions.

This skill adds guidance, not another orchestrator, approval authority, or mandatory stage. It does not grant permission to edit, delegate, contact others, install tools, or widen scope. Existing authorizations and project rules continue to apply. Using it does not by itself start Manager, Factory, Helper, or a teaching workspace.

## 8. Learn principles that transfer

The intended learning is a usable model of the collaboration: what needs to be decided, what can establish the answer, who has authority, what can be delegated, and how the result can be checked.

Use explanations and grounded examples to make these relationships visible. Do not prescribe repeated use, memorizing commands, or adopting fewer skills as a sufficient answer to cognitive overload.

Treat these principles as revisable engineering guidance. Separate research observations, practitioner experience, and local hypotheses. Research supports changes in the distribution of cognitive work; it does not prove this particular framework reduces load, that all newcomers fail for the same reason, or that more delegation always helps.
