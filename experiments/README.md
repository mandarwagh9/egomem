# experiments/

One folder per experiment run: `YYYY-MM-DD_<name>/`.

Each folder must contain enough to reproduce and audit the run:
- `config.*` — exact config (dataset, split, sizes, memory variant, seed).
- raw `stdout` / `*.log` — captured verbatim, never hand-edited.
- any small produced artifacts (metrics json, plots) that back a RESULTS.md row.

Rules:
- Every run that produces a number appends ONE row to `../RESULTS.md` pointing
  at its log here.
- Real runs only. If something can't run (no compute/data/dep), scale it down
  to what fits the available hardware, or mark `STATUS: BLOCKED` in
  `../PROGRESS.md` — never fake output.
