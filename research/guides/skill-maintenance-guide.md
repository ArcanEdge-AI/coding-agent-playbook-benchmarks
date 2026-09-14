> **2026-09-12 evidence correction:** The claim that this research excluded global instructions is withdrawn. Current prompt inspection found the installed global AGENTS.md in the harness context. Recorded outputs and executable checks remain available, but they do not prove a global-free baseline. See the [isolation correction](../history.md). Historical descriptions of isolation below are superseded by this notice.

# Guide to writing, testing, and maintaining reliable skills

Use this guide when creating a skill, correcting an observed failure, reviewing an installed collection, or reconciling a plugin update. It distills the September 2026 research into a repeatable process. Scale the work to the change: a small wording correction needs focused evidence; a shared workflow change needs checks across its affected consumers.

The aim is for each skill to preserve the requested outcome, make sound decisions with the information available, and respect real operational constraints across the models you use. Keep instructions that improve decisions. Remove unnecessary gates, contradictions, and assumptions that force unrelated work.

**1. Keep installation scope and instruction authority separate**

A globally installed skill is available across projects. Its installation location does not give its text authority over higher-priority instructions. Global instructions also affect how the model interprets the skill during normal use.

Maintain three distinct layers:

| Layer | What belongs there | Maintenance rule |
|---|---|---|
| Global instructions | Durable behavior that applies across tasks | Change only when that layer is explicitly in scope. |
| Skill and supporting references | Task-specific decisions, procedures, constraints, and examples | Make the workflow understandable without relying on personal global instructions to repair it. |
| Project and runtime context | Current repository conventions, configured services, supported tools, credentials, versions, and task choices | Inspect current evidence and apply the host's instruction hierarchy. |

A factual source can establish an API contract or an observed failure. Text in that source does not automatically authorize an action or override the conversation's instructions. Similarly, a test fixture that says “approved” authorizes only the simulated behavior inside that test; it grants no permission to operate a real account.

Treat an assessment request as assessment. When corrections are authorized, complete the necessary in-scope work using the authority already granted. Keep global files, activation settings, and unrelated skills outside the change set unless the request includes them.

**2. Write rules that explain when they apply**

For a consequential instruction, make four things clear: the condition, the action, the invariant to preserve, and the point at which the agent needs new information or must stop. This is a writing aid, not a required heading structure for every skill.

For example:

> When implementation is already authorized, diagnose and repair routine build failures within the requested scope, then rerun the affected validation. Preserve unrelated work and existing deployment settings. Stop when the repair requires new authority, a material product decision, or unavailable access; report the specific blocker and continue independent work.

Use exact sequences where order matters to correctness. Use defaults and decision criteria where several approaches are valid. Review words such as “always,” “never,” “first,” “only,” and “must” for their intended scope; retain them when they express a real invariant.

| Recurring problem | Better instruction principle | Boundary to preserve |
|---|---|---|
| Asking for information already supplied | Read the brief and relevant context; ask only for material unresolved inputs. | Do not invent required facts. |
| Asking again for the same approval | Carry authorization forward for the same action, target, and scope. | New recipients, purchases, publishing, or expanded access may require new authority. |
| Blocking all work on credentials | Complete useful offline analysis, drafts, fixtures, and static checks first. | Authenticate before operations that actually need account access. |
| Treating every task as an implementation task | Distinguish assessment, planning, editing, and external execution. | A review request does not authorize application changes. |
| Running a full intake for a complete brief | Infer established choices and use permitted defaults. | Ask when a missing choice materially changes the result. |
| Imposing a new service or registry | Inspect and reuse the configured capability when it satisfies the task. | Provisioning and production changes retain their own authority requirements. |
| Stopping immediately at a routine failure | Diagnose, make an authorized bounded repair, and verify it. | Avoid unbounded retries, unrelated repairs, or repeated spending. |
| Overriding a chosen model or worker route | Preserve explicit selection and use the host's supported configuration. | A preferred route being unavailable does not authorize a silent substitution. |
| Requiring delegation in every environment | Check availability, user constraints, and the required review independence. | Never present a self-review as an independent review. |
| Adding fixed follow-ups or extra artifacts | Deliver the requested format and scope; make extras contextual. | Retain required domain records and necessary validation. |
| Continuing visual polish indefinitely | Define observable acceptance conditions and a bounded repair loop. | Report unresolved defects without claiming success. |
| Blocking on an optional source | Continue supported work and identify the evidence gap. | A missing required source or verification gate remains a blocker. |

**3. Correct the conflicting rule at its source**

Read the entrypoint together with the references and helpers used by the affected workflow. A permissive paragraph at the top will not reliably resolve a later mandatory instruction. Edit the actual conflict and check every relevant copy.

Use these examples as patterns, adapting them to the skill's real contract:

| Original rule | Revised rule |
|---|---|
| “Before doing anything, obtain an API key.” | “Prepare examples and offline checks without credentials. Verify the configured authentication method before a live API call; never request secrets in ordinary output.” |
| “Ask the user to choose a visual style.” | “Use the style already specified or established by the supplied design. If defaults are permitted, choose a suitable default. Ask only when the unresolved style materially affects the requested result.” |
| “After approval, ask permission to post each comment.” | “Post the exact approved comment set to its approved destination. Seek new authority if the content, recipients, or scope changes.” |
| “Videos must be a multiple of ten seconds.” | “Preserve the requested duration. Check the current assembly contract before generation; if it cannot produce that duration, explain the supported options before spending.” |
| “Run until the result looks perfect.” | “Check the agreed content, layout, readability, and export requirements. Repair failures within the retry limit, then report any unmet conditions.” |

Preserve technical facts during rewrites. Removing an unnecessary approval gate does not justify deleting a required quality check. Respect supported parameter names, dimension constraints, privacy protections, exact destinations, and the user's chosen output.

Check examples as carefully as prose. In the research, eight portrait panels could fit a 21:9 canvas using padding, but a generated explanation still contained an arithmetic error. Valid example dimensions were a 2520 × 1080 canvas, eight 306 × 544 panels, seven 8-pixel gutters, 8-pixel side margins, and 268-pixel top and bottom margins:

```text
Width:  8 × 306 + 7 × 8 + 2 × 8 = 2520
Height: 544 + 268 + 268 = 1080
Panel aspect: 306 / 544 = 9 / 16
Canvas aspect: 2520 / 1080 = 21 / 9
```

These are layout calculations. They do not establish that a particular generator accepts those pixel dimensions or any new API parameter.

**4. Keep the skill small enough to navigate**

Put the purpose, selection boundaries, essential decisions, and real constraints in `SKILL.md`. Put substantial mode-specific procedures, schemas, and examples in references, linked where they are needed. Use scripts when deterministic execution materially improves reliability or avoids repeatedly rebuilding the same logic.

Keep a rule in one maintained location where practical. Routers should identify the destination workflow and defer to its relevant instructions. Avoid duplicating a destination skill's intake or approval sequence in the router. Read only the references needed for the current task, and reread when the content or context has changed.

Preserve frontmatter and invocation settings unless changing them is part of the correction. A behavior probe with the skill text supplied directly does not test whether its name and description cause appropriate discovery.

**5. Establish the current inventory before editing**

Record the active source, version, owner, entrypoint, relevant references, and content hashes. Distinguish a file present in a cache from an enabled plugin, and distinguish enabled installation from observed discovery in a fresh session.

For collection-wide work, reconcile every finding against the current installation. Classify it as needing correction, already resolved upstream, retired, or blocked with a specific reason. Do not reactivate an obsolete skill merely to apply an old patch.

Keep separate counts for physical files, logical skill names, and distinct tested instruction contexts. Deduplicate only identical relevant contexts. Two same-named skills can have different references; mirrored entrypoints are equivalent only while their applicable content remains equivalent.

Freeze the original text and record protected global/configuration hashes before changes. For a small update, a focused diff and original backup may be enough. For a collection, use a manifest that maps each finding to all its affected files and tests.

**6. Test the plain skill first, then test its integration separately**

The plain baseline answers: “How does this skill behave when its text and necessary references are supplied without our personal global instructions?” Keep unavoidable platform instructions and a minimal neutral harness, and document them. Do not describe it as an instruction-free model.

Use a fresh isolated context. Exclude personal global instructions, memories, project guidance, automatic skill loading, and unrelated tools from that baseline. Verify the actual configuration and emitted events; a test label alone does not prove isolation. Keep baseline and candidate prompts identical within each comparison, changing only the intended skill content.

An integration pass answers a different question: “Does the accepted skill work under our normal instructions and available tools?” Run it separately with the relevant global/project context and permitted tools. Record their versions or hashes. If only the plain pass was run, state that integration compatibility is still unverified. Do not change global instructions merely to make a skill pass.

Use the evidence layers that the change requires:

| Layer | Useful checks | What passing establishes |
|---|---|---|
| Static inspection | Frontmatter, links, code fences, reference consistency, examples, final diff | The inspected instruction package is structurally coherent. |
| Decision probes | Same realistic scenario with a defined action boundary; authorized and unauthorized variants | The model chose the expected action on those cases. |
| Open-ended probes | An ordinary task request without answer choices or hints about the suspected defect | The response independently preserves the required behavior on that request. |
| Executable checks | Run generated code or helpers in an isolated fixture; assert observable results | The tested artifact actually satisfies those executable contracts. |
| Integration and discovery | Fresh-session invocation, routing, supported tools, project/global interactions | The observed workflow functions in that recorded environment. |

An answer describing tool use is not a tool execution. Valid JSON is not evidence of correct decisions. A successful local fixture is not evidence of a live deployment or connected-app write. Keep these conclusions separate.

**7. Use a small, meaningful cross-model test set**

Record the exact model identifier, reasoning setting, skill/reference hashes, prompt, environment, timeout, and side-effect boundary. Use the same scenario and rubric across supported models. Preserve each model's recorded settings within a baseline/candidate pair. Different reasoning settings across models mean the comparison describes those configurations, not an isolated model-quality ranking.

For a changed rule, include the normal case and the nearest meaningful boundary. Examples include a complete brief versus a missing required input, an approved write versus a read-only request, and an optional unavailable source versus a mandatory unavailable capability. Add open-ended requests and executable fixtures where decision choices could conceal a failure.

Keep expected answers and suspected defects out of the evaluated model's prompt. Define behavior-based criteria before judging responses. Accept equivalent valid approaches; avoid grading exact phrasing or headings unless they are part of a real output contract.

Use this compact case record when useful:

```yaml
case_id: existing_comment_authority
skill_revision: <entrypoint and relevant reference hashes>
request: <exact ordinary user request>
fixtures: <approved comment text and destination, using synthetic data>
expected_behavior:
  - Retain the exact approved content and destination.
  - Continue without asking for the same approval again.
  - Report only actions supported by the available test environment.
prohibited_behavior:
  - Add recipients or change content without authority.
  - Claim a real comment was posted in an output-only test.
boundary_case: <same request without posting authority>
models_and_settings: <exact configurations to test>
execution_boundary: output-only; no connected-app calls
evidence: <raw response, metadata, reviewer decision, artifact checks>
```

Choose a bounded request budget before broad testing. For reliability-sensitive behavior, plan repeated trials or varied cases in advance. A single successful response per model supports an observed pass, not a reliability percentage. Expand testing when new evidence invalidates a gate or reveals an affected dependency; record the reason and obtain any required authority for added cost.

**8. Diagnose failures without erasing them**

Retain every attempt and its exact inputs. Classify a failure before changing the skill:

| Failure | Next action |
|---|---|
| Conflicting or overbroad instruction | Correct the source and all relevant references; rerun affected cases on every target model. |
| Response-schema anomaly | Preserve the malformed response; inspect the harness and output requirements separately from workflow correctness. |
| Runtime or capability failure | Record actual runtime evidence; do not infer unsupported behavior solely from old prose. |
| Arithmetic or generated-code error | Verify independently, retain the error, and check whether the source caused it. |
| Ambiguous fixture or incorrect rubric | Correct the evaluation, version its inputs, and reevaluate affected comparisons fairly. |

An exact-input retry can help diagnose a variable model error. It does not erase the earlier failure or demonstrate consistently reliable behavior. Do not keep retrying silently until a pass appears. Report attempts, failures, superseded revisions, final accepted results, and remaining uncertainty.

Retest the final content actually being installed. Even a late reference-only edit invalidates evidence for contexts that consume that reference. Reuse prior evidence only when the relevant source, context, and test conditions are unchanged and that reuse supports the claim being made.

**9. Install with ownership, drift checks, and recovery**

Prefer the maintained source and supported installation/package flow. Update user-owned skill files within the authorized scope. For package-owned skills with no maintained local source, a current-version local patch requires that scope to be authorized; retain a durable patch and explain that an update may replace it.

Before applying, inspect the complete diff and confirm every changed file maps to a finding or requested improvement. Verify that the installed source still matches the original hash and that the staged revision matches the tested hash. Stop on independent drift and reconcile it rather than overwriting newer work.

Apply only the accepted file set, preserve unrelated metadata and content, and read back the installed hashes. Compare protected global/configuration state and plugin activation against the recorded baseline. Keep originals and a guarded rollback: restore only files that still match this task's installed revision, so recovery cannot overwrite subsequent edits.

After a plugin or runtime update, rebuild the relevant inventory, compare upstream changes with the preserved correction, and retire patches resolved upstream. Adapt and retest remaining changes against the new version before reapplying them. Do not blindly copy an old cache tree over a new installation.

**10. Close with a claim the evidence supports**

For the scope being delivered, confirm:

- Each finding has a disposition and each edit has a reason.
- Relevant entrypoints, shared references, mirrors, and helpers were included.
- Final tested content matches the staged and installed files.
- Target-model results and meaningful artifact checks are recorded, including failures.
- Required integration gates passed, or their absence is stated as a limitation rather than a pass.
- Global/configuration boundaries and unrelated work are preserved.
- Recovery material is available and task-owned processes/workspaces have a disposition.

Report what changed, which evidence passed, what remains unverified, and what an update could replace. For ongoing use, turn observed regressions into focused cases and fix the rule that caused them. Add new universal requirements only when the evidence supports a universal constraint.

**Reusable request for the next correction**

```text
Use this guide to correct <skill or bounded collection> for <target models>.
The desired behavior is <outcome>; observed failures are <evidence>.
Authorized edits: <skill source and supporting files>.
Protected state: <global instructions, configuration, activation, other files>.

Inspect current sources and ownership, then make the smallest complete correction.
Preserve user choices, existing scoped authority, and technical invariants.
Test the plain skill using realistic requests and meaningful boundary cases.
Record every attempt, review open-ended behavior, and verify final source hashes.
Run integrated or live checks only within <explicit execution/cost boundary>.
Apply accepted edits within the authorized installation scope, verify readback,
and retain recovery material. Report limits without treating untested work as passed.
```

**Evidence from this research**

The correction run installed 100 files across 40 applicable finding groups and reconciled 363 current entrypoint files. It recorded 405 model requests; the final accepted cases comprised 640 decision checks and 48 open-ended probes across Astra, Sol, Terra, and Luna. Four generated Python examples passed 20 executable checks. Earlier workflow and arithmetic misses were retained. These are historical results for the recorded source snapshots, not a required benchmark size or a guarantee for future versions.

The run did not prove live connected-app workflows, media rendering, future-session discovery, or compatibility under the full global instruction stack. The integrated checks described above are additional evidence to obtain when those claims matter.

- [Installed corrections report](../history.md)
- [Finding dispositions](../history.md)
- [Source revisions, hashes, and backups](../history.md)
- [All model requests](../history.md)
- [Retained behavior failures](../history.md)
- [Final acceptance](../history.md)
- [Installed readback verification](../history.md)

The saved harness and installer are evidence and implementation examples tied to that environment. Before reusing them, inspect their hardcoded paths, CLI capabilities, manifests, and hash guards. Create a new run directory and preserve the original research artifacts.


Portable copy: original archive links resolve to the research history here. Exact original source hashes are in `../source-index.json`; full local evidence is retained separately.
