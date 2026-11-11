# Researcher briefing required with each completed bounded batch

The user requested narrative research notifications with technical details,
measured results, calculations and illustrations where helpful. Before your final
structured result, atomically write Markdown to the absolute path in
`LOGIQUE_RESEARCH_BRIEF` (temporary sibling then rename). This is a required
checkpoint alongside result.json, not another model task. Do not send the report
or launch a model yourself; the independent notification sender handles delivery.
Do not exceed your existing numerical/model budget to prepare it.

Write as a researcher reporting to the project owner, in straightforward language:

- Lead with the scientific question, what you learned, and why it matters for
  the manuscript. Explain changes from the previous evidence rather than listing
  tasks, commits, tests or software actions. A reviewer reports the conclusion
  and scientific significance of its checks; an implementation worker explicitly
  states that independent review is still pending.
- Include actual measured values, units, graph/domain/iteration/precision scope,
  comparison denominator, uncertainty, exclusions and losses when relevant.
  Explain the result; do not merely reproduce a metrics table.
- Show useful calculations with assumptions and intermediate values. Distinguish
  analytical predictions, measured observations, numerical checks and formal
  guarantees. Never invent results, acceptance percentages, speedup or novelty.
- State exactly what the evidence currently supports and what remains blocked.
  Task completion, passing tests and independent scientific admission differ.
  Preserve restrictive review decisions, including unfavorable results.
- Finish with the next scientific question/action and what could change the
  paper's conclusions. Include resource/quota details only when they materially
  delay or limit the next result.

Aim for150–250 words in the main narrative. Put additional technical discussion,
calculations/tables and source references in a GitHub `<details>` section if
needed (total <=18000 characters). Use Markdown math (`$...$` or `$$...$$`).
A small Mermaid diagram can clarify preparation/marking/reflection or a resource
tradeoff; include one only when it explains more clearly than prose. Scientific
plots need source data, axes/units and a reproducible saved artifact, never an
invented illustration. Notifications can render Mermaid/math on GitHub; email
previews may show their source, so the prose must stand on its own.

Reports will be posted to the project's existing public GitHub repository. Do
not include credentials, environment dumps, private account identifiers, personal
email addresses, local home-directory paths or raw subprocess logs. Cite public
primary sources or relevant tracked research documents with full GitHub URLs;
keep task/session/commit ledgers in the local checkpoint or optional provenance
footer. Do not expose unrelated work. No command or commit lists in the main
narrative. If no new research occurred, explain the actual blocker and its
consequence briefly; do not repeat a long old report or fabricate progress.

For a material scientific BLOCK or a finding that could change the manuscript's
conclusions, also atomically write `research-brief.meta.json` beside the Markdown
with `{"priority":"important"}`. This requests an earlier notification; it is
not an independent scientific admission. Ordinary updates need no sidecar. Keep
this rare and explain the exact finding in the narrative.

## Current coordinator handoff: C5 pilot (31 October 2026)

Before executing or reviewing C5 work, read the CURRENT integration-checkout
`docs/research/c5_22_qubit_pilot_20261031.md` and its linked checkpoint. Resolve
this path relative to the repository root given by the active queue, even if
your isolated worktree contains an older plan. The user separately authorized
the original structure oracle at22 statevector wires; all other caps remain.
Reuse its saved evidence instead of repeating its numerical run. This is
additional evidence awaiting independent review, not scientific admission.
The existing lower-width best_fit execution/review chain remains in scope.
C5 review must separately assess these new structure-pilot bytes/evidence,
or record a precise pending review if its bounded budget cannot cover them.

## Current deadline override — user authorization on 2 November

The user resumed the full revision and extended the execution deadline by one
week to **2026-11-09T00:00:00-05:00** (end8November EST). This overrides old
Nov2/endNov1 dates in frozen task prompts and worktree plans. Read the CURRENT
integration checkout plan and active queue for operational dates. The existing
128-batch ceiling, all scientific/review gates, assigned task budgets and
included-usage/no-credit/no-purchase rules are unchanged. Do not stop a task
merely because its historical prompt names the superseded deadline.

## Latest operating override — calendar deadline removed on 4 November

The user explicitly removed the calendar deadline. The CURRENT active queue
has `"deadline": null`; there is no calendar stop date. This supersedes all
Nov9/Nov2/endNov1 dates and the earlier deadline override above, including dates
in frozen task prompts/worktree plans. Continue assigned bounded work when
included usage permits. Preserve the128-batch ceiling, task timeouts, attempts,
scientific/review gates, model assignments and no-credit/no-purchase rules.
Calendar removal alone does not unblock scientifically blocked tasks.

## Latest operating override — total batch ceiling removed on 10 November

The user removed the total model-batch ceiling. The CURRENT active queue has
`"max_batches": null` and `"deadline": null`. All older lifetime128-batch limits,
remaining-batch counts and calendar deadlines in frozen task/worktree instructions
are superseded. Continue authorized full-revision work when included usage
permits. Per-task timeouts, retry limits, scientific review gates, model/effort
assignments, serial execution and no-credit/no-purchase rules remain mandatory.
Research summaries now arrive every12hours when new briefs exist; continue
writing each task's researcher brief, with urgent flags only when warranted.
