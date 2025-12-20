import pandas as pd
from agent.guardian_agent import run_guardian_agent

df = pd.read_csv("data/processed/anomaly_results.csv")

sample = df[df["is_anomaly"] == 1].iloc[0]

result = run_guardian_agent(sample)

print(result)
