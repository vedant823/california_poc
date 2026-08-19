import matplotlib.pyplot as plt
import streamlit as st
from src.data_prep import generate_mock_historical_data
from src.simulation import run_annual_simulation

# Initialize background data structures
generate_mock_historical_data()

# -------------------------------------------------------------
# WEBSITE PAGE LAYOUT & TEXT CONFIGURATION
# -------------------------------------------------------------
st.set_page_config(page_title="CA Water Grid Vulnerability", layout="wide")

st.title("💧 California Water Grid Vulnerability Dashboard")
st.markdown(
    """
This proof-of-concept web application models a high-level **Directed Acyclic Graph (DAG)** water grid system:
* Sierra Watershed $\rightarrow$ Foothill Reservoir $\rightarrow$ North Treatment Plant $\rightarrow$ Community Utility.

Adjust the weights below to see how prioritizing **Water Quantity vs. Water Quality** changes the overall vulnerability across different scenarios.
"""
)

# -------------------------------------------------------------
# SIDEBAR CONTROLS (USER INTERFACES & DYNAMIC SLIDERS)
# -------------------------------------------------------------
st.sidebar.header("🕹️ Simulation Controls")

selected_scenario = st.sidebar.selectbox(
    "Choose Climate Scenario Profile:",
    options=[
        "Baseline (Normal)",
        "Severe Drought (Supply Deficit)",
        "Rain-on-Burn (Turbidity Penalty)",
        "Compound Collapse (Filter Breach)",
    ],
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚖️ Vulnerability Weighting Factors")
st.sidebar.markdown(
    "Define the importance of supply vs quality. The values are locked to add up to exactly **1.0**."
)

# Interactive slider for w1 (Supply Deficit Weight)
w1_input = st.sidebar.slider(
    "Quantity Weight ($w_1$ - Supply Deficit)",
    min_value=0.0,
    max_value=1.0,
    value=0.6,
    step=0.05,
    help="Higher values penalize the system more when it fails to meet the required MGD volume demand.",
)

# Automatically calculate w2 so they always sum to 1.0
w2_input = 1.0 - w1_input

# Visual confirmation indicator text in sidebar
st.sidebar.info(f"**Calculated Quality Weight ($w_2$):** {w2_input:.2f}")

# Map human-readable dropdown strings back to internal backend function keys
scenario_map = {
    "Baseline (Normal)": "baseline",
    "Severe Drought (Supply Deficit)": "drought",
    "Rain-on-Burn (Turbidity Penalty)": "wildfire_plus_precipitation",
    "Compound Collapse (Filter Breach)": "compound_collapse",
}
backend_key = scenario_map[selected_scenario]

# -------------------------------------------------------------
# SIMULATION CALCULATION PIPELINE (WITH CUSTOM WEIGHTS)
# -------------------------------------------------------------
# Pass the slider values down into the NetworkX logic engines
v_base = run_annual_simulation("baseline", w1=w1_input, w2=w2_input)
v_drought = run_annual_simulation("drought", w1=w1_input, w2=w2_input)
v_rain = run_annual_simulation("wildfire_plus_precipitation", w1=w1_input, w2=w2_input)
v_comp = run_annual_simulation("compound_collapse", w1=w1_input, w2=w2_input)

# -------------------------------------------------------------
# LAYOUT DISPLAY SPLIT: VISUAL GRAPH VS METRICS SUMMARY
# -------------------------------------------------------------
col1, col2 = st.columns([1.2, 1.0])

with col1:
    st.subheader("📊 Cross-Scenario System Performance Index")

    scenarios = [
        "Baseline\n(Normal)",
        "Severe Drought\n(Supply Deficit)",
        "Rain-on-Burn\n(Turbidity Penalty)",
        "Compound Collapse\n(Filter Breach)",
    ]
    scores = [v_base, v_drought, v_rain, v_comp]
    colors = ["#2ecc71", "#f1c40f", "#e67e22", "#c0392b"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(scenarios, scores, color=colors, edgecolor="black", width=0.45)

    ax.set_ylabel("Annual System Vulnerability Index (V)", fontweight="bold")
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

    # Pass the Matplotlib canvas asset object straight to Streamlit to render on screen
    st.pyplot(fig)

with col2:
    st.subheader("📝 Selected Profile Metric Analysis")

    current_score = {
        "baseline": v_base,
        "drought": v_drought,
        "wildfire_plus_precipitation": v_rain,
        "compound_collapse": v_comp,
    }[backend_key]

    # Create distinct visual badge container panels mapping metrics
    st.metric(
        label="Computed System Vulnerability Index Score (V)",
        value=f"{current_score:.2f}",
        delta="Total Safe Status (0.0)" if current_score == 0 else "System Failure Alert",
        delta_color="off" if current_score == 0 else "inverse",
    )

    st.info(
        f"**Active Environment Context:** You are currently previewing system behavior mapping a continuous **{selected_scenario}** event footprint tracking real California baseline hydro-geological records across a 12-month timeline profile."
    )
    
    st.markdown(
        f"""
        ### Current Weight Allocation Analysis:
        * **Supply Protection Severity Penalty:** your system scaling currently weights a missing unit of water volume at **{w1_input * 100:.0f}%**.
        * **Safety Standards Non-Compliance Penalty:** your system currently weights delivery of polluted water above your target threshold at **{w2_input * 100:.0f}%**.
        """
    )
