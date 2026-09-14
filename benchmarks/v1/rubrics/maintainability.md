# Maintainability review rubric — v1 proposal

**Status:** Proposed anchors for calibration, not a scored study or approved promotion threshold. Freeze a version before confirmation; do not revise it after seeing condition labels or comparative outcomes.

## What is being judged

Review the submitted patch against the task specification, starting repository, applicable conventions, and independently observed validation evidence. Evaluate a complete solution that fits the demonstrated problem, not the shortest patch or the implementation closest to a reference answer.

The proposed acceptance gate is **at least 2 in every dimension, with no disqualifying blocker**. Do not let a high score in one dimension compensate for a serious defect in another. Functional correctness and valid delivery are separate required gates; this rubric cannot turn failing code into an acceptable solution.

| Dimension | 0 — Serious defect | 1 — Meaningful cleanup required | 2 — Acceptable to merge | 3 — Particularly clear and appropriate |
|---|---|---|---|---|
| Architectural fit | Breaks a required boundary or creates a material integration/policy risk | Introduces avoidable coupling, inconsistent responsibilities, or unnecessary parallel patterns | Fits the existing system with appropriate boundaries and justified departures | Makes responsibilities especially clear and resolves demonstrated structural friction without expanding scope |
| Appropriate complexity | Speculative infrastructure or unrelated rewriting makes the required change unsafe to maintain | Avoidable abstractions, dependencies, duplication, or churn require cleanup | Smallest complete design suited to the real requirements; necessary complexity retained | A demonstrably simpler complete solution removes existing friction without hiding behavior or sacrificing safeguards |
| Clarity and changeability | Behavior is misleading or tightly tangled enough to make ordinary maintenance hazardous | Naming, control flow, responsibilities, or failure handling need material clarification | Behavior and interfaces are understandable; changes and failures are handled explicitly | A future maintainer can make the foreseeable next change especially cleanly, supported by evidence rather than speculation |
| Validation and delivery quality | Material false validation claims, weakened required checks, or hidden unfinished work | Missing meaningful coverage, cleanup, or accurate handoff needs repair | Relevant defect-sensitive checks, appropriate cleanup, and an accurate bounded handoff | Particularly useful focused tests and evidence clarify tricky behavior without redundant validation or unnecessary reporting |

Necessary security, data integrity, accessibility, validation, and error handling are not over-engineering. Do not reward low line counts, comment counts, helper counts, or compliance with instruction wording for its own sake. A score of 3 is not permission for extra unrequested work.

## Review procedure

For the first study, review every functionally passing submission. Assign a neutral review ID and hide condition, model, usage, cost, and helper history. Reviewers receive the requirements and relevant repository context, patch, independently produced test results, and a de-identified handoff. Log any accidental unblinding. Functional failures remain rejected and visible in outcomes; their missing quality review is not a zero or a fabricated score.

Choose a double-scored subset before reviewing outcomes. Two reviewers score independently, then adjudicate disagreement using patch-level evidence. Record both original scores, the final adjudication, and its rationale. Human review is the initial acceptance authority; automated review may assist evidence collection but requires calibration before replacing that authority.

Calibrate on development examples, including a small complete fix and a legitimately complex change. Do not reveal protected confirmation solutions to the instruction-tuning process. Freeze rubric bytes, reviewer instructions, coverage policy, and thresholds before confirmation.

## Required review record

Record the neutral review ID, task/rubric versions, reviewer identifier, blinding status, four dimension scores, blockers, evidence for each score, and adjudication when applicable. Evidence should identify the relevant file/symbol or independently observed behavior. Retain review minutes separately from agent credits.

A blocker needs a concrete requirement, risk, or misleading claim and supporting evidence. Do not use personal stylistic preference as a blocker. Independently verified integrity/security failures are disqualifying even when functional checks pass.

Keep initial quality review separate from the optional fresh-agent maintenance follow-up. The original solution is never graded against an unstated future feature. See the [full protocol](../../../research/evaluation-v1/PLAN.md) for pipeline accounting and confirmation rules.
