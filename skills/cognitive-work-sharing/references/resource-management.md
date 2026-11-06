# Cognitive Resource Management

Reference for [cognitive-work-sharing](../SKILL.md), for human understanding and agent guidance when this skill is explicitly invoked. [繁體中文](resource-management.zh-TW.md) provides the same guidance. This adds no role, mandatory gate, or execution authority.

## 1. From delegating work to managing cognitive resources

Once agents can advance substantive work, the operator's problem can shift from getting work done to absorbing its results. Faster production may concentrate interpretation, integration, judgment, and intervention at the human operator. Human attention becomes an asset of the collaboration system.

In the framework author's experience, insufficient focus or a sense of cognitive devastation often marks a transition beyond initial use: the operator can now drive work and must learn to manage the resulting demands. Treat this as an experiential description, not a qualification. Beginners can also overload, and experienced operators can overload because of work design. Do not encourage exhaustion as evidence of proficiency.

The central lesson: **manage which work enters human thought, when it arrives, and in what form, as well as how work gets completed.**

## 2. Human resources are not a fixed token counter

Magic or human tokens can illustrate limited attention, working memory, judgment effort, and recovery needs. They are not interchangeable units of fixed capacity. The same document can demand very different effort depending on fatigue, familiarity, and context.

Allow for deterioration that is not proportional to added work: context confusion, repeated reading, or missed conditions may sharply increase rework. This is a planning assumption that warrants margin, not a universal fatigue curve validated here. Agents should not diagnose physiological or psychological conditions from a short conversation.

Count establishing and recovering context, comparing alternatives, interpreting evidence, switching tasks, carrying unresolved matters, and repairing mistakes. Agent execution time and document length alone miss these costs.

## 3. Metadecision: choose what deserves thought

A decision asks which path to take. A metadecision also asks whether to decide now, what to investigate first, who prepares the material, and when enough is known. This addresses depth and stopping conditions beyond ordering a task list.

Use these perspectives when helpful, rather than as a mandatory form:

| Perspective | Judgment needed | Material an agent can prepare |
| --- | --- | --- |
| Goal and timing | What advances now? What happens if deferred? | Relationship to current goals, deadlines, and settled decisions. |
| Paths and dependencies | Which failed premise would waste the path? | Rough alternatives, critical premises, dependencies, and rework points. |
| Information value | Which unknown could change the choice? | A discriminating check or minimal experiment, rather than exhaustive collection. |
| Cognitive demand | What human judgment is needed, and is it ready to make? | Established facts, trade-offs, recommendation, and remaining human choice. |
| Stopping and intervention | What is enough to act? What warrants revisiting? | Stopping conditions, reversible next steps, and evidence that would change the conclusion. |

Sketch paths to expose conditions that could change direction, not to write the entire implementation plan early. Resolve a shared critical premise first. Defer detail that does not affect the next reversible step.

## 4. Order work and arrange when judgment arrives

Importance, urgency, readiness for judgment, and suitability for attention now are different considerations. A high-priority matter may first need agent investigation; a smaller prepared decision might be resolved earlier. Arrival order should not determine attention priority.

Delegation produces downstream human work. Consider what results will require understanding, whether several streams will await the same person's judgment together, and which conclusions depend on unsettled premises. This does not prescribe a fixed session limit. Manage the arrival of reports and decision demands.

Continue within existing authority without inventing gates. Before requesting a human decision, resolve established facts and already-delegated matters. Group reports by shared decision context while surfacing genuinely time-sensitive problems; quieter reporting must not conceal them.

## 5. Decide when research is enough

Continue when further evidence could change the choice, avoid material rework, or make unacceptable uncertainty manageable. Weigh that benefit against human interpretation effort, investigation cost, delay, and displaced work. Use qualitative judgment rather than invented precision.

Before investigating, identify the disagreement to resolve, what evidence would change direction, and when a reversible step is appropriate. Pause research that only enriches background without affecting the current choice. For consequential work still missing critical evidence, expose the gap; stopping research does not establish grounds for approval.

Metadecision itself consumes resources. Clear, low-consequence, reversible work often warrants direct action. Work with uncertain premises, many dependencies, or expensive rework more often warrants preparation.

## 6. When overload has already arrived

When the user reports exhaustion, difficulty understanding reports, or inability to decide, use existing context to reduce the immediate demands. Do not return a large menu asking them to design their own relief.

- Preserve the goal, confirmed decisions, open issues, and resumption point in existing records.
- Separate settled matters, discoverable facts, delegated choices, and genuine human decisions; avoid repeated adjudication.
- Present the conclusion, basis, recommendation, consequences, and remaining uncertainty needed now. Keep full evidence traceable.
- If understanding is missing, prepare examples, explanations, or checks. Shorter wording alone does not ensure easier understanding.
- If judgment is unavailable now, explain what can wait, the cost of waiting, and what authorized work can continue. Preserve necessary approvals; fatigue is not consent.

Rest or pausing is reasonable, but should not replace correcting repeated questions, poor allocation, and accumulated reports. Saving effort does not authorize expanding the agreed task.

## 7. Development example

An architectural choice has two paths. An agent proposes implementing both extensively while the operator is already absorbing many review reports.

Find the actual disagreement first. If the choice mainly depends on whether the existing engine exposes an interface, inspect it or run a small experiment before implementing both paths. Meanwhile, the agent can resolve review findings already answered by established rules and group genuine trade-offs by context, without asking the operator to reconstruct every task together.

When interface evidence arrives, explain how it changes the paths, which trade-off remains human-owned, and the next reversible step. If it does not distinguish the paths, identify the missing condition instead of repeating discussion without new evidence.

This changes the order and form of cognitive investment. It requires no new agent node, mandatory heavy process, or additional parallel work.

## 8. Assess usefulness

Look for fewer avoidable repeated decisions and context reconstructions, earlier discovery of path-invalidating premises, preserved human understanding and intervention, and resumable records. Fewer questions, faster approvals, or more output alone do not establish improvement.

## 9. Evidence and claim boundaries

[Griffiths, Lieder and Goodman, 2015](https://onlinelibrary.wiley.com/doi/10.1111/tops.12142) propose resource-rational analysis of cognitive strategies under resource constraints. [Callaway et al., 2018](https://arxiv.org/abs/1711.06892) study selecting computations, allocating effort, and stopping. The former offers a theoretical perspective; the latter investigates computational models. Neither validates this skill or measures operator fatigue curves.

For GenAI metacognitive demands and practitioner orchestration costs, see [evidence notes R1 and P1](evidence.md). These operating suggestions synthesize those perspectives with the author's practice. Overload as a transition beyond initial use is the author's observation, not a research-established developmental stage or diagnostic criterion.
