"""Headline figure: EgoMem augments a frozen VLM on episodic-spatial QA.
Numbers are the logged results in ../../RESULTS.md (exp_id = spatial-qa H11b / H11c).
Run: python make_figure.py  ->  ../../paper/figures/qa_results.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# real logged accuracies (RESULTS.md): conditions x model
conds = ["no-memory", "VLM sees\n5 photos", "current-view\ntext", "+ EgoMem\nmemory"]
flash = [0.273, 0.491, 0.727, 0.927]   # H11b, 6 scenes / 55 Qs, gemini-2.5-flash
pro   = [0.194, 0.452, 0.613, 0.968]   # H11c, 3 scenes / 31 Qs, gemini-2.5-pro

x = np.arange(len(conds)); w = 0.38
fig, ax = plt.subplots(figsize=(8.2, 4.6))
colors = ["#bbbbbb", "#bbbbbb", "#bbbbbb", "#2a7de1"]
b1 = ax.bar(x - w / 2, flash, w, label="Gemini 2.5-flash", color=colors, edgecolor="white")
b2 = ax.bar(x + w / 2, pro, w, label="Gemini 2.5-pro", color=colors, alpha=0.55, hatch="//", edgecolor="white")
for bars, vals in [(b1, flash), (b2, pro)]:
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.015, f"{v:.2f}", ha="center", va="bottom", fontsize=8)

ax.set_ylabel("Episodic-spatial QA accuracy")
ax.set_ylim(0, 1.05)
ax.set_xticks(x); ax.set_xticklabels(conds, fontsize=9)
ax.set_title("A frozen VLM gains spatial competence by reading EgoMem\n"
             "(real ARKitScenes; EgoMem beats the VLM that *sees* the room by +44/+52 pts)",
             fontsize=10.5)
# legend: solid=flash, hatched=pro; color encodes EgoMem
from matplotlib.patches import Patch
ax.legend(handles=[Patch(facecolor="#888", label="Gemini 2.5-flash"),
                   Patch(facecolor="#888", alpha=0.55, hatch="//", label="Gemini 2.5-pro"),
                   Patch(facecolor="#2a7de1", label="EgoMem condition")],
          loc="upper left", fontsize=8.5, framealpha=0.9)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()

out = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "paper", "figures"))
os.makedirs(out, exist_ok=True)
path = os.path.join(out, "qa_results.png")
fig.savefig(path, dpi=150)
print("wrote", path)
