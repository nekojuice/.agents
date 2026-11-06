# Evidence and experience / 研究與心得

Checked: 2026-11-06. This is a curated reading record, not a systematic literature review. Sources support particular observations or perspectives, not validation of this skill. Read the original before making a stronger claim.

查閱日期：2026-11-06。本索引是選讀紀錄，並非系統性文獻回顧。來源支持特定觀察或觀點，不等於本 skill 已經獲得實證驗證；要作更強的主張，需重新查閱原文。

## R1. Metacognitive demands / 後設認知需求

[Tankelevitch et al., CHI 2024: The Metacognitive Demands and Opportunities of Generative AI](https://www.microsoft.com/en-us/research/publication/the-metacognitive-demands-and-opportunities-of-generative-ai/)

Conceptual synthesis drawing on cognitive research and GenAI user studies. It connects prompting, evaluation, reliance, and workflow choices to monitoring and regulating one's thinking. Useful for framing operator demands; not a controlled test establishing this framework's effectiveness.

這是結合認知研究與生成式 AI 使用研究的概念論述，將提示、評估、信任與工作策略連到對自身思考的監控和調節。可用來理解操作負荷，不能當作本框架有效性的受控實驗證據。

## R2. Supervisory engineering / 監督型工程工作

[Vella and Blincoe, 2026, version 2 revised 2026-11-03: The Impact of AI Coding Assistants on Software Engineering](https://arxiv.org/abs/2605.23135v2)

Two questionnaires six months apart: 158 first-wave participants, 101 second-wave participants, 95 matched. The authors describe direction, evaluation, and correction as supervisory engineering work. Findings concern perceived experience and productivity; they do not establish objective causal productivity gains or universally increased cognitive load.

半年間隔的兩次問卷，首輪 158 人、次輪 101 人、配對 95 人。作者以監督型工程工作描述引導、評估與修正。這是感受與自陳生產力資料，不證明客觀因果收益或所有人的認知負荷都增加。

## R3. Layered supervision / 分層監督

[Stolze and Strässle, ESEM 2026: When Review Alone No Longer Scales](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ESEM.2026.90)

A qualitative interview study of five practitioners, within a broader survey context. It describes supervision distributed across explicit architectural conventions, executable checks, and human interpretation. This informs the distinction between retaining authority and personally doing every check. The small qualitative sample does not prove a universal prescription.

五名實務者的質性訪談，置於較廣泛問卷脈絡。研究描述監督分布於外顯架構規範、可執行檢查與人類判讀。可啟發「保留權力不等於親做全部檢查」；小樣本不能證明通用處方。

## R4. Skill formation / 能力形成

[Shen and Tamkin, 2026: How AI assistance impacts the formation of coding skills](https://www.anthropic.com/research/AI-assistance-coding-skills)

A randomized study of 52 mostly junior engineers learning an unfamiliar Python library. The AI group averaged 50% on the quiz versus 67% without AI; the completion-time difference was not significant. Interaction-style comparisons were qualitative, not separately randomized causal tests. The setting was a short learning task with a sidebar assistant, not this multi-agent framework.

52 名多為初階工程師學習陌生 Python 函式庫的隨機研究。AI 組測驗平均 50%，對照組 67%；完成時間差異未達顯著。不同互動風格的比較是質性分析，不是另行隨機測試的因果結論。情境為短期學習與側欄助理，不是本多 agent 框架。

## R5. Distributed cognition / 分散式認知

[Hollan, Hutchins and Kirsh, 2000: Distributed Cognition](https://doi.org/10.1145/353485.353487)

An HCI theoretical perspective examining cognition across people, tools, representations, and environments. It motivates considering records and artifacts as part of the working system. It predates generative AI and does not validate LLM-based delegation. This reading used the authors' available abstract and bibliographic record, not a full-paper review.

這個人機互動理論從人、工具、表徵與環境共同理解認知，可啟發將文件與產物納入工作系統。它早於生成式 AI，不驗證 LLM 委派。本輪依作者可取得的摘要與書目理解，未完成全文審讀。

## P1. Practitioner experience / 實務心得：編排成本

[Addy Osmani, 2026-05-24: The Orchestration Tax](https://addyosmani.com/blog/orchestration-tax/)

The author describes the mismatch between cheap agent spawning and expensive human review, context recovery, and integration. Useful for questioning output volume as a success metric. Treat personal workload accounts and suggested agent counts as experience, not universal limits or experimentally established scaling laws for people.

作者描述啟動 agent 的低成本，與人類審查、恢復脈絡及整合的高成本之間的落差。可用來質疑只看產出量的衡量方式。個人負荷、建議 agent 數量屬心得，不是通用門檻，也不是已實驗確立的人類擴展定律。

## P2. Practitioner experience / 實務心得：用 agent 協助理解

[Simon Willison: Interactive explanations](https://simonwillison.net/guides/agentic-engineering-patterns/interactive-explanations/)

The author describes using a code walkthrough and an agent-generated interactive visualization to understand an algorithm. It is a concrete example of using agents to help understand agent-produced work. It does not show that every generated explanation is correct or that every user will learn effectively from one.

作者以程式解說與 agent 製作的互動視覺化理解演算法，是用 agent 協助理解其產物的具體案例。它不證明所有生成解釋都正確，也不保證所有人都能有效學會。

## Local propositions awaiting validation / 待驗證的本地工作主張

- Agent-assisted preparation can reduce the human's decision burden while preserving meaningful control, if the resulting evidence and choices remain assessable.
- This framework's principles can transfer across software, images, modeling, and other engineering media.
- A bilingual, human-facing skill can help unfamiliar operators form that collaboration model.

- 由 agent 準備判斷材料，可能在保留有意義控制的同時減少人的決策負荷，前提是證據與選擇仍可判讀。
- 此框架的原則可以遷移到程式、圖像、建模等工程媒介。
- 雙語的人類操作 skill 能協助陌生操作者形成這種協作模型。

These are propositions for evaluation. The sources above do not directly test them in this repository.

這些是待評估的主張；上述來源沒有直接在本 repo 中測試它們。
