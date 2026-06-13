"""EgoMem CLI.

  egomem demo                      # fast end-to-end demo (small synthetic run)
  egomem sim --seed 0              # full out-of-view recall benchmark (reproduces RESULTS.md)
  egomem sim --seed 0 --pose-drift 0.15
"""
from __future__ import annotations

import argparse
import sys


def _print_results(results):
    cfg = results["_config"]; h1 = results["_h1"]
    print(f"  config: seed={cfg['seed']} n_train={cfg['n_train']} n_test={cfg['n_test']} "
          f"pose_drift={cfg['pose_drift']}")
    print(f"  {'arm':10s} {'WM pos succ@0.5m':>17s} {'WM err(m)':>10s} {'VLA dir succ@30d':>17s} {'VLA err(deg)':>13s}")
    for arm in ("no-memory", "naive", "egomem"):
        r = results[arm]
        print(f"  {arm:10s} {r['wm_success']:17.3f} {r['wm_mean_err_m']:10.3f} "
              f"{r['vla_success']:17.3f} {r['vla_mean_err_deg']:13.1f}")
    print(f"  H1 (egomem >= no-memory+20pp AND >= naive, both consumers): "
          f"{h1['H1']}  [WM {'PASS' if h1['wm_pass'] else 'FAIL'} | VLA {'PASS' if h1['vla_pass'] else 'FAIL'}]")


def cmd_demo(_args):
    from .sim import run
    print("EgoMem demo - small synthetic out-of-view recall run (fast).")
    res = run(seed=0, n_train=40, n_test=20, pose_drift=0.0, epochs=200)
    _print_results(res)
    print("\nThis is a reduced run for speed; `egomem sim --seed 0` reproduces the full result.")
    return 0


def cmd_sim(args):
    from .sim import run
    res = run(seed=args.seed, n_train=args.n_train, n_test=args.n_test,
              pose_drift=args.pose_drift, epochs=args.epochs)
    print("EgoMem out-of-view recall benchmark")
    _print_results(res)
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="egomem", description="Model-agnostic memory layer for robotics from egocentric video.")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("demo", help="fast end-to-end demo").set_defaults(func=cmd_demo)

    s = sub.add_parser("sim", help="full out-of-view recall benchmark")
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--n-train", type=int, default=200)
    s.add_argument("--n-test", type=int, default=100)
    s.add_argument("--pose-drift", type=float, default=0.0)
    s.add_argument("--epochs", type=int, default=400)
    s.set_defaults(func=cmd_sim)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
