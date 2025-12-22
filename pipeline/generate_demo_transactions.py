import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_high_volume_transactions(scenario_type="transient"):
    print(f"Generating high-volume demo transactions ({scenario_type})...")
    
    start_time = pd.Timestamp("2025-12-18 15:00:00")
    data = []
    
    # Configuration
    WINDOWS = 12
    ROWS_PER_WINDOW = 10000
    
    # Store IDs
    store_ids = [f"S{i:03d}" for i in range(1, 21)]
    
    transaction_counter = 0

    for i in range(WINDOWS):
        window_start = start_time + timedelta(minutes=5 * i)
        
        # Determine scenario based on window index
        # 0-4: Normal
        # 5-9: Late Data Incident
        # 10-11: Recovery (ONLY IF transient)
        
        if scenario_type == "transient":
            is_late_incident = (5 <= i <= 9)
        else: # persistent
            is_late_incident = (i >= 5)

        for _ in range(ROWS_PER_WINDOW):
            transaction_counter += 1
            tx_id = f"tx_{transaction_counter:06d}"
            store_id = np.random.choice(store_ids)
            amount = int(np.random.normal(100, 20))
            
            # Event Time (randomly distributed within the 5 min window)
            offset_seconds = np.random.randint(0, 300)
            event_time = window_start + timedelta(seconds=offset_seconds)
            
            # Ingestion Time
            if is_late_incident and np.random.random() > 0.1: # 90% late during incident
                # Late by 20 minutes
                ingestion_delay = 20 * 60 + np.random.randint(0, 60)
            else:
                # Normal delay (1-5 seconds)
                ingestion_delay = np.random.randint(1, 5)
                
            ingestion_time = event_time + timedelta(seconds=ingestion_delay)
            
            data.append([
                tx_id,
                event_time,
                ingestion_time,
                store_id,
                amount,
                "SUCCESS"
            ])
            
    columns = ["transaction_id", "event_time", "ingestion_time", "store_id", "amount", "payment_status"]
    df = pd.DataFrame(data, columns=columns)
    
    output_filename = f"data/raw/supermarket_transactions_{scenario_type}.csv"
    df.to_csv(output_filename, index=False)
    print(f"Generated {len(df)} transactions to {output_filename}")

if __name__ == "__main__":
    generate_high_volume_transactions(scenario_type="transient")
    generate_high_volume_transactions(scenario_type="persistent")
