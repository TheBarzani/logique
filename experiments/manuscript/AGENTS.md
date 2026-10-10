# Manuscript reproduction

`legacy/` is a narrowly scoped snapshot from the source commit recorded in
`provenance.json`. Preserve these files byte-for-byte, including their original
formatting. Do not run the hardware submission script; it is retained only to
document how historical measurements were collected.

Implement replay, validation, and compatibility handling in
`tools/reproduce_manuscript.py`. The maintained library must not import this
snapshot. Generated files belong in a new directory under `dump/`. Preserve all
reference data; track methodology changes separately from historical reproduction.
