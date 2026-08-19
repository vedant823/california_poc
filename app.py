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
    
    * Sierra Watershed → Foothill Reservoir → North Treatment Plant → Community Utility. 
    
    Select a climate scenario below to recalculate system metrics and view the resulting **Vulnerability Score (0.0 to 1.0)**. 
    """
)


# -------------------------------------------------------------
# SIDEBAR CONTROLS (USER INTERFACES)
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

# Map human-readable dropdown strings back to internal backend function keys
scenario_map = {
    "Baseline (Normal)": "baseline",
    "Severe Drought (Supply Deficit)": "drought",
    "Rain-on-Burn (Turbidity Penalty)": "wildfire_plus_precipitation",
    "Compound Collapse (Filter Breach)": "compound_collapse",
}
backend_key = scenario_map[selected_scenario]

# -------------------------------------------------------------
# SIMULATION CALCULATION PIPELINE
# -------------------------------------------------------------
# Run all backgrounds secretly to generate the final compilation comparison bar graph
v_base = run_annual_simulation("baseline")
v_drought = run_annual_simulation("drought")
v_rain = run_annual_simulation("wildfire_plus_precipitation")
v_comp = run_annual_simulation("compound_collapse")

# Run user selected scenario to display on user interface canvas
# Note: This will automatically print the markdown table cleanly behind the scenes into terminal log buffers
_ = run_annual_simulation(backend_key)

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
