# EgoMem — Cycle 10 (H10): downstream TASK SUCCESS (not a recall proxy)

**Date:** 2026-06-14. H1–H9 measured out-of-view *recall*. H10 tests the thing that
actually matters: does the neutral memory let a controller **complete a long-horizon
task** it otherwise fails?

## Hypothesis H10

> In a closed-loop long-horizon **scan-then-fetch** task (map a room, then navigate to
> K=4 target objects in order under FOV+range-limited sensing), a controller equipped
> with EgoMem completes the task far more often than the same controller with no memory
> — by ≥ 20 points task-success in a regime where targets cannot be trivially
> re-observed.

The *same* rule-based controller drives all arms (steer toward whatever world position
`query` returns for the current target); they differ only in what memory supplies for an
out-of-view target: nothing (no-memory → must re-search), a stale wrong bearing (naive),
or the correct recalled bearing (egomem). Metric = **task success rate** (all K reached
within budget), 3 seeds × 200 episodes.

## Result (CONFIRMED) — and the value scales with partial observability

Difficulty sweep (room size / sensing range); `stdout_fetch.log`, RESULTS `fetch-task *`:

| difficulty | no-memory | naive | egomem | gain | verdict |
|---|---|---|---|---|---|
| easy (8 m / 6 m) | 0.975 | 0.658 | 1.000 | +2.5 pts | REJECTED |
| medium (11 m / 5 m) | 0.205 | 0.195 | 1.000 | +79.5 pts | CONFIRMED |
| hard (14 m / 4 m) | 0.010 | 0.013 | 1.000 | **+99.0 pts** | CONFIRMED |

**Finding:** when re-observation is cheap (small room, long range) memory barely helps
(+2.5). In the realistic regime (large space, limited sensing) memory is **decisive:
~1 % → 100 %** task completion. naive ≈ no-memory or worse (stale bearing misdirects).
This connects the recall results to task value: the same neutral memory that improves
out-of-view recall converts long-horizon partially-observed tasks from near-impossible
to solved.

## Honest caveats

- Rule-based controller (isolates the memory's *information* value; not a learned VLA).
- Clean synthetic perception (the real-perception cost is H8/H9's ~1 m noise).
- egomem = 1.000 throughout = perfect synthetic memory; the *baseline collapse* with
  difficulty is the real signal, and the easy-regime +2.5 shows where memory is NOT the
  bottleneck.

**VERDICT: H10 CONFIRMED** (in the partial-observability regime). The buyer-side neutral
memory delivers task-level value, not just a recall proxy.
