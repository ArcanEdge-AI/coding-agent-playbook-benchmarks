> **2026-09-12 evidence correction:** The claim that this research excluded global instructions is withdrawn. Current prompt inspection found the installed global AGENTS.md in the harness context. Recorded outputs and executable checks remain available, but they do not prove a global-free baseline. See the [isolation correction](../history.md). Historical descriptions of isolation below are superseded by this notice.

# Prompting: what worked, what remains uncertain, and how to test it

Use this guide to give an AI model a clear task and judge whether a change to your instructions actually improves its work. The practical starting point is to describe the outcome, provide the information that changes the answer, identify the important boundaries, and define observable success. Add detail when it resolves a real ambiguity.

This guide draws on our four-model instruction research. We tested skill text and task requests in a controlled harness; we did not run a general experiment comparing everyday chat prompting techniques. The observations below are evidence from those tests. The example prompts are practical applications of those findings, not independently proven formulas.

**What the research actually taught us**

| Finding | Evidence | Practical implication |
|---|---|---|
| A model can follow an instruction correctly and still frustrate the user's task. | Several original skills explicitly required the unnecessary pause that appeared in the answer. | Inspect the instruction causing the behavior before assuming the model needs more emphasis or effort. |
| A general exception may fail to overcome a specific conflicting rule. | Broad qualifiers did not reliably resolve PDF endings, template intake, or the mandatory-bag reference. Direct revisions later passed the targeted final cases across all four models. | Replace the conflicting instruction where possible; keep examples and supporting material consistent with the desired behavior. |
| Specific scope and authority can support useful progress. | Corrected build, CI, simulator, and comment workflows passed cases requiring routine authorized work while preserving their boundaries. | Explain which work should be completed and what would require a new decision. |
| Choosing a correct answer is easier to test than producing a correct result. | The broad choice matrix was near its scoring ceiling. Open-ended probes exposed omitted source labels, invented assumptions, intake gates, and other failures. | Test with the actual task, not just “which approach is best?” |
| Plausible output can contain checkable errors. | A storyboard answer used valid dimensions but displayed an incorrect equation. Some generated code passed execution checks while its broader response still failed workflow review. | Verify calculations, artifacts, and task behavior separately. |
| One instruction version can work across different models. | Final revised text passed the selected cases on Astra, Sol, Terra, and Luna without separate model-specific patches. | Start with a shared clear prompt; specialize only when repeated evidence warrants it. |
| Passing after revision does not establish universal improvement. | Of 360 paired requests in the broad run, 12 improved, 348 passed both versions, and none regressed on the scored choices. Later revisions also reused observed failures. | Keep the improvement claim tied to the tested cases. Use new tasks to check whether it transfers. |

The broad comparison used single samples and reused some scenarios across related entries. The final correction run accepted 640 decision checks and 48 open-ended probes, with earlier failures retained. Neither result is a reliability percentage for future tasks. See the [broad comparison](../history.md), [targeted revisions](../history.md), and [final correction report](../history.md).

**A useful prompt contains the decisions the model needs**

Use only the parts that matter. A simple request may need one sentence; a substantial task may benefit from this structure:

```text
Produce [concrete result] for [purpose or audience].

Use [relevant facts, files, examples, and established choices].
Preserve [important constraints or existing decisions].

You may [work that is authorized].
If [specific boundary or material missing information], [ask or report it].
Otherwise, make reasonable minor choices and continue.

Check [observable success conditions].
Return [required output], including [evidence or limitations that matter].
```

“Concrete result” distinguishes a diagnosis, a plan, an implemented repair, and a verified deliverable. “Relevant context” means information that could change the answer. “Success conditions” describe something you can inspect, such as retained units, a passing test, an exact file format, or a working user flow.

An extensive role description, emphatic language, or a long list of generic standards is not a substitute for these details. Our study did not compare those techniques, so it cannot establish whether adding them helps your task.

**Patterns worth using**

**Describe completion.** “Help with the report” leaves several possible outcomes. “Write the finished one-page report from these notes for the project sponsor” makes the deliverable concrete. In the tested creative workflows, the complete brief needed to carry through to delivery without an unnecessary new intake sequence.

**Give bounded freedom.** Replace “ask me before every step” with the actual decision boundary when independent progress is wanted. For example: “Choose routine implementation details within this change. Ask if the repair changes the public API or requires a new dependency.” This preserves useful autonomy without making the task open-ended.

**State established choices once, clearly.** Include the chosen model, service, audience, format, approved content, or design reference when it matters. A request to add a timeout should not become an opportunity to change the model. A completed brief should not trigger questions it has already answered.

**Pair restrictions with the desired behavior.** Instead of only “do not overcomplicate this,” say “use the existing module and implement the smallest change that satisfies these two cases.” Instead of only “do not ask questions,” say “use the supplied choices and reasonable defaults; ask only if missing information prevents a correct result.” Necessary questions can still be the right behavior.

**Preserve facts explicitly when fidelity matters.** For a summary, identify which figures, units, source labels, qualifications, and distinctions must survive compression. The PDF tests showed that a generally sensible summary could still omit these details or invent a comparison option.

**Request evidence suited to the task.** For code, ask for the relevant test result and remaining failures. For research, ask for support for consequential claims and a distinction between evidence and inference. For a calculation, require a check against the stated quantities. A confident explanation alone cannot establish correctness.

**Resolve contradictions rather than piling on reminders.** If one instruction asks for a finished artifact and another requires a template interview every time, decide when the interview is needed. If you control the reusable instruction, correct it there. If you control only the task prompt, make the intended choice explicit within your authority and recognize that other instruction layers still apply.

**Stop when the requested result meets its criteria.** Specify the checks that matter instead of asking for unlimited polish or mandatory extra suggestions. In the research, fixed follow-up rules repeatedly produced output the task did not need.

**Four everyday examples**

These examples apply the observed principles. They have not themselves been run as a new benchmark.

| Task | Prompt |
|---|---|
| Repair a bug | “Fix the failing import in the checkout module using the existing API. You may edit the affected code and its focused test. Reproduce the failure, make the repair, and run the relevant checks. Ask if it requires a public API change. Report the change, test result, and any remaining blocker.” |
| Assess a proposal | “Evaluate this proposal against the stated budget, delivery date, and requirements. Identify supported strengths, risks, and missing evidence. Give a recommendation with its assumptions. Return the assessment here.” |
| Summarize research | “Summarize the attached findings for a decision maker in about 400 words. Preserve sample sizes, units, table/figure attribution for key claims, and limitations that affect the conclusion. Distinguish observations from inference. End with a recommendation only if the evidence supports one.” |
| Finish a creative brief | “Create the finished 15-second vertical video described below. The audience, narrator, references, and style are supplied; reasonable visual defaults are fine. Deliver one MP4 with no subtitles or cover image. Use only the approved generation allowance. Verify exact-duration support before spending; if unsupported, explain the available options. Do not publish it.” |

You should not need to anticipate every defect in every request. Add a constraint because it matters to the task or addresses a recurring failure. If the same reminder is necessary repeatedly, inspect the reusable instructions and workflow that cause the problem.

**How to know whether a prompt is better**

Treat a proposed improvement as a small experiment. Start with a specific failure: “It asks for approval again,” “It loses the units,” or “It reports a fix without running the available test.” “The answer feels smarter” is too vague to diagnose on its own.

1. **Save the original.** Keep the prompt, relevant context, output, model/settings, and any artifact or tool evidence.
2. **Define success before revising.** For example: all three approved comments retained, no additional recipient, no duplicate approval question, and no claim of posting in an output-only environment.
3. **Change one meaningful cause.** Replace the repeated-approval instruction, clarify an output requirement, or fix a contradiction. If multiple coordinated rules must change, treat them as a bundle; the test will not identify which individual sentence caused the improvement.
4. **Compare on the same tasks.** Give both versions the same inputs and available capabilities in separate fresh sessions. Keep model and reasoning settings fixed within each comparison. Prevent tool side effects from changing the starting state.
5. **Check an ordinary case and a boundary.** A prompt that proceeds after approval should also stop when the required approval is absent. A prompt that preserves numbers should also acknowledge when the source does not supply them.
6. **Try new examples.** Reserve some tasks that you do not use while editing. These held-out tasks help distinguish a reusable improvement from a fix tuned to one known answer.
7. **Repeat where variability matters.** Preselect the number of attempts you can afford. Keep all failures and report pass counts with their denominator. Do not stop recording once a retry succeeds.
8. **Inspect the real outcome.** Read the answer against the criteria, run relevant artifact checks, and record regressions. Adopt the change when the evidence supports its benefit without an unacceptable tradeoff.

For a lightweight start, choose a few representative tasks, include a meaningful boundary, and keep at least one new example out of the editing loop. This is a practical starting point, not a statistically validated sample size. Consequential or variable workflows need more evidence than occasional drafting tasks.

Keep a small comparison table:

| Task and version | Meets requirements? | Facts/artifact correct? | Unnecessary stops or extras? | Evidence and failure |
|---|---|---|---|---|
| Task 1, original | Record result | Record check | Record observation | Link original output |
| Task 1, revised | Record result | Record check | Record observation | Link revised output |
| New task, revised | Record result | Record check | Record observation | Note that it was held out |

If possible, review outputs without knowing which version produced them. Judge observable behavior and task quality; accept different valid wording. Keep the scoring criteria out of the subject's view when revealing them would give away the answer being tested.

**Separate prompt effects from the rest of the system**

An everyday result reflects the task prompt, conversation history, system/global instructions, loaded skills, model/settings, tools, and supplied evidence. Changing several of these at once makes the cause of improvement harder to identify.

Our isolated baseline excluded personal global instructions and injected selected skill text through a custom instruction file. That was useful for testing the supplied instructions, but it differs from ordinary skill discovery and ordinary user-message placement. It does not prove that the same sentence has the same effect in every layer.

For your own prompting, begin by testing in the environment where you intend to use the prompt. Keep the other layers stable and record the relevant ones. Use an isolated comparison when you need to investigate a particular source of behavior, then verify the improvement in normal use. A task prompt cannot create missing tools or override higher-priority instructions.

**What we should not claim yet**

This research does not show that longer prompts are better, shorter prompts are better, a particular persona improves accuracy, or a phrase such as “think harder” produces a reliable gain. It did not isolate the effect of asking for plans or explanations, compare reasoning levels, establish a best model overall, or validate all live workflows.

Most broad paired cases passed before and after the rewrite. That is evidence that those cases did not distinguish the versions. It is not evidence that every added instruction improved the result. The observed wins support specific changes to task alignment and conflicting workflow rules.

When judging your own prompts, distinguish four claims: “It sounds good,” “It passed this task,” “It passed repeated and unseen tasks,” and “It worked with the real tools and artifacts.” Each requires different evidence. Choose the level that matches how much you will rely on the result.

**A useful follow-up when an answer misses**

```text
The result missed [specific requirement]. Here is the evidence: [example].
Correct that part while preserving [what was already right].
Check the revised result against [observable criterion].
If conflicting instructions or missing information caused the problem,
identify the conflict or gap rather than inventing an answer.
```

Use that correction to finish the current task. If the failure recurs, revise the reusable prompt and compare it on fresh tasks using the process above. Keep only the instructions whose value you can explain through the decisions they improve or the constraints they preserve.


Portable copy: original archive links resolve to the research history here. Exact original source hashes are in `../source-index.json`; full local evidence is retained separately.
