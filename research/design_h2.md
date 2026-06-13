# EgoMem — Cycle 2 Design (real-data validation, tests H2)

**Date:** 2026-06-13. Reuses the **unchanged `egomem` library** (3 memory arms +
read-heads) from Cycle 1; only the data loader is new. This also validates the
packaged library on real data.

## Dataset — ARKitScenes 3dod (VERIFIED reachable & ungated this run)

- **CDN base:** `https://docs-assets.developer.apple.com/ml-research/datasets/arkitscenes/v1`
- **Metadata:** `…/threedod/metadata.csv` — downloaded OK (HTTP 200, 154 KB);
  **5047 scenes** (4498 Training, 549 Validation).
- **Per-scene zip:** `…/threedod/Validation/{video_id}.zip` — HTTP 200,
  **≈187 MB/scene**. Contents (verified on scene `41069021`):
  - `…/{vid}_frames/lowres_wide.traj` — **1878 poses**, 7 cols per line:
    `timestamp r0 r1 r2 t0 t1 t2`.
  - `…/{vid}_frames/lowres_wide/*.png` — 1878 RGB frames; `lowres_depth/*.png` —
    1878 depth maps; `lowres_wide_intrinsics/*.pincam` — per-frame intrinsics.
  - `{vid}_3dod_annotation.json` — **18 objects** (this scene); each
    `data[i]` has `label` (e.g. "sofa","table","chair","tv_monitor","cabinet",
    "oven") and `segments.obb = {centroid[3], axesLengths[3], normalizedAxes[9]}`.
- **Local cache:** one scene already downloaded+unzipped at
  `/tmp/41069021.zip` and `/tmp/arkit_inspect/41069021/` (reuse; avoid re-download).
- **Download tool:** `/tmp/arkit_dl.py` (Apple's `download_data.py`) or direct curl
  of the per-scene zip URL above.

## CRITICAL open format detail (loader MUST resolve + validate, not guess)

- **Trajectory convention:** use Apple's official `TrajStringToMatrix`:
  `tokens[1:4]` = angle-axis rotation (world→camera), `tokens[4:7]` = translation;
  build world→camera 4×4, then **invert** → camera→world = our `cam_pose`
  (world←camera). Implement Rodrigues→matrix in numpy (no cv2 dep).
- **OBB units/frame mismatch (UNRESOLVED — do not assume):** obb centroid for
  scene 41069021 obj0 = `[155.8, 110.1, 76.7]` and axesLengths `[166, 83, 91]`
  — consistent with **centimetres** (a 1.66 m sofa), while traj translations are
  in **metres** (camera ≈2.1 m). The box and trajectory frames/units must be
  reconciled against the official ARKitScenes `threedod` box utilities before any
  recall number is produced.
- **Validation gate (HARD):** before computing ANY recall metric, the loader must
  pass a sanity check — project several box centroids into frames where that
  object is plausibly visible and confirm they land within the image and at
  positive depth roughly matching the depth map. If alignment can't be verified,
  STATUS: BLOCKED with the exact mismatch — **never** report recall numbers off an
  unvalidated transform.

## Protocol (mirrors Cycle 1 on real geometry)

Per scene (subsample the 1878-frame trajectory to ~every Kth frame, K≈20, →
~90 frames, to match Cycle-1 horizon scale and keep CPU cost low):
1. Parse poses (official convention) and object centroids (resolved to metres,
   common frame). Objects = the 3D-box set; positions = centroids.
2. Per frame: object "visible" iff its centroid projects within the image via
   per-frame intrinsics + pose and is in front within range. Detection `pos_cam`
   = centroid transformed into that frame's camera coords (REAL pose).
3. Drive the **unchanged** `egomem` arms (`NoMemory`/`NaiveBuffer`/`EgoMem`) via
   `Observation`/`QueryState`; query at the final subsampled frame.
4. Recall targets = objects out of view at the final frame but seen earlier.
   GT = centroid in final-frame camera coords (real final pose).

**Pooling/splits:** evaluate on **N≈12–16 Validation scenes** (download ≈2–3 GB;
CPU; GCP available if bulk is wanted). Pool recall queries across scenes; split by
**scene** into train/test for the read-heads (no scene leakage). Heads, tolerances
(0.5 m / 30°), arms, and the H1 threshold check are reused verbatim from
`lib/egomem` + the Cycle-1 protocol. Seeds ≥2 for the head training.

**Logging:** `experiments/2026-06-13_arkit-oov/` with `config.json`, full
`stdout.log`, `metrics.json`, the validation-gate output, and the list of
scene ids used. Append rows to RESULTS.md (real numbers only; note dataset =
ARKitScenes-3dod + scene count).

## Baselines

Identical 3 arms (no-memory / naive / EgoMem) from the library — mandatory.

## Why this is the right next experiment

It swaps the synthetic substrate for **real egocentric RGB-D with real VIO poses
and real object layouts**, directly testing whether Cycle-1's confirmed mechanism
survives real sensing — and whether the real-pose case lands on the "good
localization" side of the Cycle-1 drift boundary. It reuses the shipped library
unchanged, so a positive H2 also demonstrates the library works on real data.
