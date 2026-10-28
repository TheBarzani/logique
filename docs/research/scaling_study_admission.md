# Scaling study admission gate — 28 October 2026

**Decision: BLOCK. No scaling implementation or pilot is admitted.**
This integration triage is COMPLETE. Subsequent scaling jobs must inspect this
gate before executing; task completion does not authorize compiler experiments.
Input, witness, provenance and protocol preparation may proceed independently.

Independent decision: [verbatim re-review](scaling_contract_rereview.md), committed
by the reviewer as `5411998f31cc3ae46e88c841a7b748734889260b`, report SHA256
`da9a3ac97a5f1aa1918cc4c213a1fa333421aeec7e9c435fc9f581faa38c12ca`.
Reviewed candidate HEAD `01935f432fca9c10a5451e5711c3716607998d71`, correction
`4bd9a16`, remains outside integration along with original implementation
`5da2e1e`, `fd62200`, `36e730e` and original checkpoint `f095a5c`.
No worker checkpoint-only files have been cherry-picked into the root.

The decision binds these actual candidate bytes:

| Path | SHA256 |
| --- | --- |
| `src/logique/synthesis/process.py` | `9c94548e725684a3eeef1eaf85eca16672e87ee438a69f48d42e9d52942491e4` |
| `tests/test_native_process.py` | `a70f419dad10d8221b11b4e4da431814309bf534b02a892ed285ada105ebb2c5` |
| `docs/scaling-harness.md` | `ab36adee787c310b483ce5d4ad54b1b79f5cc8d1a8e6a2e6d32d625479e1aa08` |
| `src/logique/benchmarks/scaling.py` | `43070e357be798003868db28585e648b8ba6158703eabe2f4b11cc8fe8454d1d` |

The original B1 deadline and B2 RSS regressions now pass, but the leader can exit
between the final nonblocking reap and group kill. Real Darwin `killpg` then
raises EPERM, skipping reap, timeout accounting and the intended limit exception.
The scaling harness catches the OSError as an ordinary failure and charges zero
native wall time. Five attempted calls can therefore each receive the original
cumulative budget. This is a resource-contract blocker, not a scalability result.

Required correction: make owned-group cleanup resilient across leader exit;
guarantee reap and accounting through cleanup failures; preserve timeout and
interruption semantics and surviving-descendant cleanup. Genuine permission
failures must stay explicit. Failed launched work must consume the cumulative
budget, or the study must stop conservatively when accounting is unavailable.
Retain the exact race and cumulative-ledger regressions plus success, timeout,
interruption and descendant tests. Obtain a fresh independent exact-hash decision
before integration or selected scaling execution. Do not simply swallow EPERM.

Fresh coordinator reproduction and next ownership are recorded in
[triage](scaling_contract_triage.md). Full Task8, FT/RUS, ideal-amplitude,
comparison and manuscript scope remain open. No quantum or paper approval follows.
