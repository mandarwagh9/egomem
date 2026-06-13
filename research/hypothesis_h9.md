# EgoMem — Cycle 9 (H9): GT-free instance tracking (fully real association)

**Date:** 2026-06-14. H8 used a real detector + real depth but assigned detections to
objects by GT proximity (evaluation-side). H9 removes that last bit of GT from the
pipeline: form object tracks from the **detection stream alone**.

## Hypothesis H9

> With a real detector + real LiDAR depth AND **GT-free online spatial instance
> tracking** (each detection associated to the nearest existing track in world space,
> else spawns one — no GT, no ids from the detector), EgoMem still enables out-of-view
> recall that a no-memory baseline cannot, at the ~1 m real-perception tolerance.

GT is now used **only for scoring** (to assign a ground-truth position to a track via
its *early* observations — never to form tracks). This is standard MOT-style
evaluation; spurious tracks (detector false positives with no GT match) are excluded
from scoring, not from formation.

## Metric / threshold

Out-of-view recall success at 0.5 m and 1.0 m. A track is a target if it was observed
earlier but not at the final frame (out of view now) and matches a GT object (≤1.5 m
on early observations). egomem = track median → final camera frame; no-memory = only
final-frame detections (no track persistence → miss); naive = last detection,
un-transformed. Verdict per tolerance: egomem ≥ no-memory + 0.20 AND ≥ naive.

## Falsifier

egomem within 20 pp of no-memory, or below naive, at the realistic (1.0 m) tolerance —
i.e. GT-free tracking destroys the recall advantage.

## Plan

Add an online spatial tracker to `arkit_detector.py` (`--tracker`); reuse the 6
downloaded scenes (gate filters to the aligned ones); report at both tolerances.
This closes the H8 caveat and makes the real-perception pipeline fully GT-free except
for scoring.
