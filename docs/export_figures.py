"""
Generates high-resolution figures of membership functions and FCM convergence for the PDF report.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import matplotlib.pyplot as plt
import numpy as np

from core.recommender import HybridTourismRecommender

FIG_DIR = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(FIG_DIR, exist_ok=True)

rec = HybridTourismRecommender()
engine = rec.fuzzy_engine

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

def export_mf(var, filename, title, xlabel):
    fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=300)
    x = np.linspace(var.universe[0], var.universe[1], 400)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for idx, (term, fset) in enumerate(var.sets.items()):
        y = fset.membership(x)
        c = colors[idx % len(colors)]
        ax.plot(x, y, label=term, color=c, lw=2.2)
        ax.fill_between(x, 0, y, color=c, alpha=0.15)
        
    ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel("Degree of Membership μ(x)", fontsize=10)
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc='upper right', frameon=True)
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, filename))
    plt.close(fig)

print("Exporting Membership Functions figures...")
export_mf(engine.var_budget, "mf_budget.png", "Membership Functions: Budget (€)", "Total Trip Budget (€)")
export_mf(engine.var_climate, "mf_climate.png", "Membership Functions: Climate (°C)", "Temperature (°C)")
export_mf(engine.var_duration, "mf_duration.png", "Membership Functions: Duration (Days)", "Trip Duration (Days)")
export_mf(engine.var_suitability, "mf_suitability.png", "Membership Functions: Output Suitability (%)", "Suitability Score (%)")

# FCM Convergence Figure
fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=300)
iters = list(range(1, len(rec.fcm_model.cost_history) + 1))
ax.plot(iters, rec.fcm_model.cost_history, marker='o', color='#2b5797', lw=2)
ax.set_title("Fuzzy C-Means Convergence: Bezdek Objective Function J_m", fontsize=12, fontweight='bold', pad=10)
ax.set_xlabel("Iteration", fontsize=10)
ax.set_ylabel("Cost Value J_m", fontsize=10)
plt.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "fcm_convergence.png"))
plt.close(fig)

print("All figures exported successfully to", FIG_DIR)
