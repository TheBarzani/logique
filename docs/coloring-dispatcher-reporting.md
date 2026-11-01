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
