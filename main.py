import matplotlib.pyplot as plt
from src.data_prep import generate_mock_historical_data
from src.simulation import run_annual_simulation

# Step 1: Initialize data structure pipelines
print("Initializing PoC Framework...")
generate_mock_historical_data()

# Step 2: Compute core multi-scenario graph models (and trigger terminal printing)
print("\nRunning network simulation algorithms...")
v_base = run_annual_simulation("baseline")
v_drought = run_annual_simulation("drought")
v_rain = run_annual_simulation("wildfire_plus_precipitation")
v_comp = run_annual_simulation("compound_collapse")

print(
    f"\n=========================================================================================================================="
)
print("FINAL SCORES SUMMARY")
print(
    f"=========================================================================================================================="
)
print(f"-> Baseline Annual Vulnerability Index: {v_base:.2f}")
print(f"-> Severe Drought Annual Vulnerability Index: {v_drought:.2f}")
print(f"-> Rain-on-Burn Annual Vulnerability Index: {v_rain:.2f}")
print(f"-> Compound Collapse Annual Vulnerability Index: {v_comp:.2f}")

# Step 3: Map outputs to matplotlib canvas
print("\nPlotting visual metrics for meeting presentation...")
scenarios = [
    "Baseline\n(Normal)",
    "Severe Drought\n(Supply Deficit)",
    "Rain-on-Burn\n(Turbidity Penalty)",
    "Compound Collapse\n(Filter Breach)",
]
scores = [v_base, v_drought, v_rain, v_comp]
colors = ["#2ecc71", "#f1c40f", "#e67e22", "#c0392b"]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(scenarios, scores, color=colors, edgecolor="black", width=0.45)

ax.set_ylabel(
    "Annual System Vulnerability Index (V)", fontsize=12, fontweight="bold"
)
ax.set_title(
    "PoC Verification: Water Grid Network Vulnerability Metrics Across Annual Timeframes",
    fontsize=13,
    fontweight="bold",
    pad=20,
)
ax.set_ylim(0, 1.1)
ax.grid(axis="y", linestyle="--", alpha=0.4)
ax.set_axisbelow(True)

for bar in bars:
    height = bar.get_height()
    ax.annotate(
        f"{height:.2f}",
        xy=(bar.get_x() + bar.get_width() / 2, height),
        xytext=(0, 5),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontweight="bold",
    )

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.show()
