# QPY serialization representation ledger

This is a representation change, not a performance improvement or a corrected
historical comparison table. The exact-byte serialization correctness fix is
committed separately as `2792427` after the stage-provenance foundation `b6743cb`.

The final worker ledger contains 240 logical/common-basis component rows over
24 tiny R1/R2/R3, j=0/1 cases. Against original emitted circuits, root reference
and unsafe legacy readback, 48 rows change gate-type maps: 16 preparation,
16 diffusion and 16 search rows. 36 change total gate count and depth; zero
change width. All 120 common-basis rows and raw/oracle rows stay identical in
this fixture set. Open-control constructions can additionally emit X gates.
The artifact representation is explicitly `resolved_standard_gates`, with mixed
logical granularity. Do not aggregate it with historical opaque-operation counts.

Full row-by-row ledger, including before/after maps and expansion provenance:
`dump/1025125442-qpy-coordinator-triage/representation-differences.json`, SHA-256
`b4a499bb3de7fb6488cb5abc3bf9fee807c18966111958e843962ba6300a419d`.
Candidate and integrated coordinator semantic replays independently recount all
240 saved rows each. Saved operator semantics, rather than reproduced counts,
are admitted only under [the independent review](qpy_semantic_review.md).

Earlier unsafe QPY, 720-row pilot, comparison summaries and archived research
outputs remain untouched and are not retroactively admitted. Their affected
serialization evidence needs separate correction/review before paper use. No
new nine-graph study, research table, advantage, protocol freeze or paper claim
is supplied by this ledger.
