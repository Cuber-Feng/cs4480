import pandas as pd
import time

df = pd.read_csv(
    "./data/WCA_export_ranks_average.tsv",
    sep="\t",
    dtype={"person_id": str, "event_id": str},
)

t0 = time.perf_counter()

removed_events = ["333ft", "magic", "mmagic", "333mbo"]
df = df[~df["event_id"].isin(removed_events)]
qs = [i / 10 for i in range(1, 11)]          # 0.1, 0.2, ..., 1.0

g = df.groupby("event_id")["best"]

stats = g.agg(participants="count", world_record="min")

pct = g.quantile(qs, interpolation="lower").unstack()
pct.columns = [f"p{int(q * 100)}" for q in qs]
pct = pct.astype(int)

out = stats.join(pct).sort_values("participants", ascending=False).round(2)
out.to_csv("./output/event_stats.csv", sep=",")
t1 = time.perf_counter()
print(f"Time taken: {t1 - t0:.2f} seconds")
print(out)