import networkx as nx
import pandas as pd


def run_annual_simulation(scenario="baseline", w1=0.6, w2=0.4):
    """Reads data arrays, executes NetworkX pipelines, and generates scenario indexes.

    Tracks monthly metrics, prints an operational summary table, and computes annual means
    using user-defined weights passed from the web app interface.
    """
    df_water = pd.read_csv("data/watershed_historical.csv")
    df_res = pd.read_csv("data/reservoir_historical.csv")
    df_util = pd.read_csv("data/utility_demand_historical.csv")

    total_annual_vulnerability = 0.0

    # Lists to store metrics for mean calculations
    metrics_log = {
        "flow": [],
        "w_ntu": [],
        "r_ntu": [],
        "d_ntu": [],
        "demand": [],
        "delivered": [],
        "target": [],
    }

    # Disaster Threshold Ceiling Constant
    MAX_DISASTER_NTU = 25.0  # Turbidity ceiling where water is 100% unusable

    print(
        f"\n=========================================================================================================================="
    )
    print(
        f" SCENARIO DETAILS: {scenario.upper().replace('_', ' ')} (w1={w1:.2f}, w2={w2:.2f})"
    )
    print(
        f"=========================================================================================================================="
    )
    print(
        f"{'Month':<6} | {'Watershed Flow':<14} | {'Watershed Turb':<14} | {'Reservoir Turb':<14} | {'Delivered Turb':<14} | {'Comm Demand':<12} | {'Delivered MGD':<13} | {'Target NTU':<10}"
    )
    print("-" * 122)

    for i in range(12):
        G = nx.DiGraph()
        month = df_water.loc[i, "Month"]

        pop = df_util.loc[i, "Target_Population"]
        gpcd = df_util.loc[i, "Avg_GPCD_Demand"]
        comm_demand = (pop * gpcd) / 1000000.0  # Gallons to MGD conversion
        target_ntu = df_util.loc[i, "Safe_Quality_Threshold_NTU"]

        if scenario == "baseline":
            inflow = df_water.loc[i, "Baseline_Flow_MGD"]
            source_ntu = df_water.loc[i, "Baseline_NTU"]
            settling = df_res.loc[i, "Baseline_Settling_Efficiency"]
            plant_bypass_ntu = 0.5
        elif scenario == "drought":
            inflow = df_water.loc[i, "Drought_Flow_MGD"]
            source_ntu = df_water.loc[i, "Baseline_NTU"] * 1.5
            settling = df_res.loc[i, "Baseline_Settling_Efficiency"]
            plant_bypass_ntu = 0.5
        elif scenario == "wildfire_plus_precipitation":
            inflow = df_water.loc[i, "Baseline_Flow_MGD"]
            source_ntu = df_water.loc[i, "RainOnBurn_NTU"]
            settling = df_res.loc[i, "RainOnBurn_Settling_Efficiency"]
            plant_bypass_ntu = 4.0
        elif scenario == "compound_collapse":
            inflow = df_water.loc[i, "Drought_Flow_MGD"]
            source_ntu = df_water.loc[i, "RainOnBurn_NTU"]
            settling = df_res.loc[i, "RainOnBurn_Settling_Efficiency"]
            plant_bypass_ntu = 25.0 if month in ["Dec", "Jan", "Feb"] else 2.0

        # Graph Formulation
        G.add_edge(
            "Sierra Watershed", "Foothill Reservoir", flow=inflow, ntu=source_ntu
        )

        reservoir_out_ntu = source_ntu * (1.0 - settling)
        G.add_edge(
            "Foothill Reservoir",
            "North Treatment Plant",
            flow=min(150.0, inflow),
            ntu=reservoir_out_ntu,
        )

        incoming_ntu = G["Foothill Reservoir"]["North Treatment Plant"]["ntu"]
        incoming_flow = G["Foothill Reservoir"]["North Treatment Plant"]["flow"]

        if incoming_ntu <= 50.0:
            max_plant_capacity = 150.0
        else:
            max_plant_capacity = 150.0 * (50.0 / incoming_ntu)

        supplied_volume = min(max_plant_capacity, incoming_flow, comm_demand)
        G.add_edge(
            "North Treatment Plant",
            "Community Utility",
            flow=supplied_volume,
            ntu=plant_bypass_ntu,
        )

        # Print current month metrics
        print(
            f"{month:<6} | {inflow:<14.1f} | {source_ntu:<14.1f} | {reservoir_out_ntu:<14.1f} | {plant_bypass_ntu:<14.1f} | {comm_demand:<12.1f} | {supplied_volume:<13.1f} | {target_ntu:<10.1f}"
        )

        # Log current month values for mean tracking
        metrics_log["flow"].append(inflow)
        metrics_log["w_ntu"].append(source_ntu)
        metrics_log["r_ntu"].append(reservoir_out_ntu)
        metrics_log["d_ntu"].append(plant_bypass_ntu)
        metrics_log["demand"].append(comm_demand)
        metrics_log["delivered"].append(supplied_volume)
        metrics_log["target"].append(target_ntu)

        # SCORING ENGINE (Using dynamic function arguments w1 and w2)
        supply_deficit = max(0.0, (comm_demand - supplied_volume) / comm_demand)
        supply_deficit = min(1.0, supply_deficit)

        if plant_bypass_ntu <= target_ntu:
            quality_failure = 0.0
        else:
            raw_quality_error = (plant_bypass_ntu - target_ntu) / (
                MAX_DISASTER_NTU - target_ntu
            )
            quality_failure = min(1.0, max(0.0, raw_quality_error))

        month_vulnerability = (w1 * supply_deficit) + (w2 * quality_failure)
        total_annual_vulnerability += month_vulnerability

    # Calculate final means
    mean_flow = sum(metrics_log["flow"]) / 12.0
    mean_w_ntu = sum(metrics_log["w_ntu"]) / 12.0
    mean_r_ntu = sum(metrics_log["r_ntu"]) / 12.0
    mean_d_ntu = sum(metrics_log["d_ntu"]) / 12.0
    mean_demand = sum(metrics_log["demand"]) / 12.0
    mean_delivered = sum(metrics_log["delivered"]) / 12.0
    mean_target = sum(metrics_log["target"]) / 12.0

    print("-" * 122)
    print(
        f"{'MEAN':<6} | {mean_flow:<14.1f} | {mean_w_ntu:<14.1f} | {mean_r_ntu:<14.1f} | {mean_d_ntu:<14.1f} | {mean_demand:<12.1f} | {mean_delivered:<13.1f} | {mean_target:<10.1f}"
    )
    print(
        f"=========================================================================================================================="
    )

    return total_annual_vulnerability / 12.0
