# Forming Requirements with Non-Specialists

Reference for [cognitive-work-sharing](../SKILL.md), for engineers, requirement participants, and agents. [繁體中文](requirements-discovery.zh-TW.md) provides the same guidance. This skill still requires explicit invocation. This reference grants no authority to implement, dispatch, or decide on a participant's behalf.

## 1. What collaboration must achieve before requirements exist

Non-specialists may not know what technology can do or what they actually want. Inviting requirements does not mean they can already describe outcomes, boundaries, exceptions, or acceptance criteria.

Help participants establish a problem and intended result they can examine together. Do not treat unexplored ideas as engineering assignments, silently making the engineer responsible for guessing preferences, filling in circumstances, choosing purposes, and defining scope.

This guidance draws on the framework user's experience; it is not an empirically validated universal requirements method. Describe requirements as unformed rather than treating non-specialists as a fixed personality category. Anyone can struggle to express intent in an unfamiliar domain.

## 2. Identify the maturity of a statement

Meeting statements can be different kinds of material. Confidence of delivery does not establish agreement.

| Material | Meaning | What to clarify next |
| --- | --- | --- |
| Problem | Something is causing difficulty. | Circumstances, impact, and current handling. |
| Wish | Work should become better. | What improvement would be useful, and to whom. |
| Idea | A possibility worth exploring. | The problem or opportunity it addresses. |
| Proposed solution | An initial picture of a solution. | Why this approach, and what must hold for it to work. |
| Confirmed requirement | An agreed expected behavior or outcome. | Scope, verification, and remaining decisions. |

For example, “AI should handle all customer complaints” does not establish a choice of automatic replies, refund decisions, or case assignment. Engineers and agents may propose interpretations, but must identify them as assumptions and preserve their source and confirmation status. Silence, enthusiasm, and an existing prototype do not establish confirmation.

## 3. Build shared material from concrete situations

Do not merely ask people to make their requirements clear. Start with experience they can recognize, asking as needed:

- Who was doing what the last time this happened?
- Where did work get stuck, and with what consequences?
- How was it handled, and under what constraints?
- Which part most needs changing, and what would make the change useful?

Reuse supplied material rather than asking again. Do not present every question at once; establish a concrete event that changes understanding. For new products or opportunities without a past event, jointly construct a clearly labeled hypothetical use situation and check it against potential users or other evidence.

Engineers help abstract from this material; non-specialists need not write specifications first. If there is no concrete event, hypothetical situation, or desired improvement, acknowledge that the problem is still being sought and implementation cannot yet be promised.

## 4. Distinguish kinds of uncertainty

| What is unknown | Suitable exploration |
| --- | --- |
| Where the problem lies | Observe actual work, events, and difficulties. |
| What the improved outcome should be | Compare whose work would change and with what consequences. |
| How to achieve an understood outcome | Have engineers investigate feasible paths, prerequisites, and limits. |
| Preferences that emerge through seeing | Use sketches, samples, or prototypes with a specific comparison purpose. |
| Conflicting desired outcomes | Expose the conflict and its consequences for the responsible decision-makers. |

Several uncertainties may coexist. A technical experiment cannot settle a value trade-off, and additional versions should not conceal unresolved disagreement.

## 5. Explain capabilities, completion levels, and boundaries

Show how work happens now and how it could change, including inputs, outputs, and human participation. Explain why the example is feasible. Examples should enable useful analogies rather than merely list technical terms or appealing features.

Explain what completion means. A concept demonstration, an interactive prototype, a usable result under agreed conditions, and an ongoing system with maintenance and exception handling represent different commitments. Prototype appearance must not imply reliability that has not been established.

Express boundaries through understandable conditions and consequences:

- **Capability:** What is demonstrated, and what still needs an experiment?
- **Prerequisites:** What data, access, tools, and domain knowledge are needed?
- **Reliability:** What can be checked, what errors remain possible, and what would they affect?
- **Delivery responsibility:** What is included, who accepts the result, and who maintains it?

Non-specialists need not invent these boundaries. Engineers explain them concretely; participants help confirm working facts, expectations, and acceptable consequences. Technical composability does not establish the resulting quality, cost, or schedule.

## 6. Give each exploration an identifiable question

Before making a sketch or prototype, state what it should distinguish and how different answers affect the next step. Eliminating an option, confirming a premise, or identifying a preference can be a valid exploration outcome; more features are not required.

For example, two sketches can distinguish whether work is primarily organized by case or by customer. If that changes information organization, comparison is useful. Two complete implementations are unnecessary for that question.

If demonstrations only generate more ideas without eliminating options, confirming conditions, or establishing criteria, identify the lack of convergence. Relate new ideas to the current problem rather than adding them all to delivery commitments. Existing authority and authorization govern expansion of exploration.

## 7. Leave progress that can be resumed

Every meeting need not reach a final decision, but it should clarify:

1. The problem or opportunity and whom it affects.
2. Confirmed understanding, provisional assumptions, and unresolved trade-offs.
3. Whether remaining uncertainty requires observation, investigation, demonstration, or an authorized decision.
4. Which decision the next exploration should enable and what will be sufficient.

Use existing project records rather than creating a parallel requirements authority. If agreement is insufficient, say no decision was reached. Do not invent consensus to produce a polished conclusion. New ideas need not all enter the next step.

## 8. How agents contribute without deciding for people

Within authorization, agents can organize statements, recover existing decisions, identify contradictions, draft hypothetical situations, investigate feasibility, and suggest the next exploration most likely to resolve uncertainty. Establish discoverable material before presenting questions that genuinely require human intent or trade-offs.

Preserve the distinction between original statements and their interpretation. Do not present inference as a user quotation, promote an exploration direction into a delivery requirement, or substitute technical feasibility for a business choice. When confirmation is needed, present a concrete interpretation and its consequences for correction rather than asking someone to write a complete specification from nothing.

Assess whether participants can better identify the problem, confirmed understanding, remaining unknowns, and what the next step will answer. Longer feature lists, more prototypes, or livelier meetings do not establish clearer requirements.
