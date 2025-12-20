from pipeline.aggregate_transactions import aggregate_transactions
from pipeline.stream_simulator import stream_simulation

RAW_DATA_PATH = "data/raw/supermarket_transactions.csv"
METRICS_PATH = "data/scenarios/single_late_data_incident.csv"

def run_demo():
    print("\nDEMO MODE STARTED\n")

    # Step 1: Aggregate raw transactions
    print("Aggregating raw supermarket transactions...")
    aggregate_transactions(
        input_path=RAW_DATA_PATH,
        output_path=METRICS_PATH
    )

    # Step 2: Stream simulation on aggregated metrics
    print("\nStarting stream simulation...\n")
    stream_simulation(input_path=METRICS_PATH)

    print("\nDEMO MODE COMPLETE")

if __name__ == "__main__":
    run_demo()
