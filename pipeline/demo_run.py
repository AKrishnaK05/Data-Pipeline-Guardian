from dotenv import load_dotenv
load_dotenv()

from pipeline.aggregate_transactions import aggregate_transactions
from pipeline.stream_simulator import stream_simulation

import sys

from dotenv import load_dotenv
load_dotenv()

from pipeline.aggregate_transactions import aggregate_transactions
from pipeline.stream_simulator import stream_simulation

def run_demo(scenario="transient"):
    print(f"\nDEMO MODE STARTED (Scenario: {scenario})\n")

    raw_data_path = f"data/raw/supermarket_transactions_{scenario}.csv"
    metrics_path = f"data/scenarios/{scenario}_incident.csv"

    # Step 1: Aggregate raw transactions
    aggregate_transactions(
        input_path=raw_data_path,
        output_path=metrics_path
    )

    # Step 2: Stream simulation on aggregated metrics
    print("\nStarting stream simulation...\n")
    stream_simulation(input_path=metrics_path)

    print("\nDEMO MODE COMPLETE")

if __name__ == "__main__":
    scenario_arg = "transient"
    if len(sys.argv) > 1:
        scenario_arg = sys.argv[1]
    
    run_demo(scenario=scenario_arg)
