import os
import pandas as pd
import time

t0 = time.perf_counter()
K = 1                       # 惩罚因子，k >= 1，可自行调整
REMOVED = ["333ft", "magic", "mmagic", "333mbo"]

df = pd.read_csv(
    "./data/WCA_export_ranks_average.tsv",
    sep="\t",
    dtype={"person_id": str, "event_id": str},
)

df = df[~df["event_id"].isin(REMOVED)]          # 去掉已取消的项目

# 每个项目的参与人数 n，以及缺失时的惩罚排名
n = df.groupby("event_id").size()
penalty = n * K                                  # 当前是 n * K；想用 n + K 就改这一行

ranks = df.pivot(index="person_id", columns="event_id", values="world_rank")
ranks = ranks.fillna(penalty)

sor = (ranks.sum(axis=1)
            .astype(int)
            .rename("SOR")
            .reset_index()
            .sort_values(["SOR", "person_id"]))

# ---- 新增：SOR 排名 ----
# method="min"：并列时取最小名次（1, 2, 2, 4 这种写法）
sor["sor_rank"] = sor["SOR"].rank(method="min").astype(int)

# ---- 新增：姓名和国籍 ----
persons = pd.read_csv(
    "./data/WCA_export_persons.tsv",
    sep="\t",
    dtype=str,
    usecols=["wca_id", "sub_id", "name", "country_id"],
)
persons = persons[persons["sub_id"] == "1"]      # 只保留当前记录，避免一个人出现多行
persons = persons.rename(columns={"wca_id": "person_id", "country_id": "nationality"})

sor = sor.merge(persons[["person_id", "name", "nationality"]],
                on="person_id", how="left")

sor = sor[["sor_rank", "person_id", "name", "nationality", "SOR"]]

os.makedirs("./output", exist_ok=True)
sor.to_csv("./output/sor.csv", sep=",", index=False)
print(sor.head(10))

t1 = time.perf_counter()
print(f"Time taken: {t1 - t0:.2f} seconds")