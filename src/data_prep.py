import os
import pandas as pd


def generate_mock_historical_data():
    """Generates realistic California baseline water matrices and saves them to CSV.

    Ensures baseline flows are high enough to completely prevent structural deficits.
    """
    os.makedirs("data", exist_ok=True)

    # Sierra Watershed Inflow (Raised Baseline flows to handle late-summer demands)
    watershed_data = {
        "Month": [
            "Oct",
            "Nov",
            "Dec",
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
        ],
        "Baseline_Flow_MGD": [
            120.0,
            110.0,
            120.0,
            130.0,
            140.0,
            150.0,
            220.0,
            250.0,
            190.0,
            150.0,
            140.0,
            130.0,
        ],  # Kept safely above max demand
        "Drought_Flow_MGD": [
            15.0,
            18.0,
            22.0,
            25.0,
            30.0,
            35.0,
            50.0,
            55.0,
            42.0,
            25.0,
            16.0,
            12.0,
        ],
        "Baseline_NTU": [
            8.0,
            10.0,
            12.0,
            15.0,
            15.0,
            12.0,
            10.0,
            8.0,
            7.0,
            8.0,
            9.0,
            8.0,
        ],
        "RainOnBurn_NTU": [
            12.0,
            15.0,
            650.0,
            700.0,
            550.0,
            200.0,
            45.0,
            20.0,
            15.0,
            12.0,
            11.0,
            12.0,
        ],
    }
    pd.DataFrame(watershed_data).to_csv("data/watershed_historical.csv", index=False)

    # Foothill Reservoir Storage Tracking (Syntax Fixed Here)
    reservoir_data = {
        "Month": [
            "Oct",
            "Nov",
            "Dec",
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
        ],
        "Max_Capacity_AF": [1000000.0] * 12,
        "Target_Storage_AF": [600000.0] * 12,
        "Baseline_Settling_Efficiency": [0.50] * 12,
        "RainOnBurn_Settling_Efficiency": [
            0.50,
            0.50,
            0.40,
            0.40,
            0.45,
            0.50,
            0.50,
            0.50,
            0.50,
            0.50,
            0.50,
            0.50,
        ],
    }
    pd.DataFrame(reservoir_data).to_csv("data/reservoir_historical.csv", index=False)

    # Community Utility Demand Data (Syntax Fixed Here)
    demand_data = {
        "Month": [
            "Oct",
            "Nov",
            "Dec",
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
        ],
        "Target_Population": [1000000.0] * 12,
        "Avg_GPCD_Demand": [
            95.0,
            80.0,
            70.0,
            68.0,
            70.0,
            75.0,
            88.0,
            105.0,
            115.0,
            120.0,
            118.0,
            108.0,
        ],
        "Safe_Quality_Threshold_NTU": [5.0] * 12,
    }
    pd.DataFrame(demand_data).to_csv(
        "data/utility_demand_historical.csv", index=False
    )
    print("-> System CSV files prepared inside /data directory.")
