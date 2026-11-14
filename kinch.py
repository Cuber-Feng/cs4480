import os
import time
import pandas as pd

t0 = time.perf_counter()

REMOVED = ["333ft", "magic", "mmagic", "333mbo"]

df = pd.read_csv(
    "./data/WCA_export_ranks_average.tsv",
    # "./data/big.tsv",
    sep="\t",
    dtype={"person_id": str, "event_id": str},
)
df = df[~df["event_id"].isin(REMOVED)]          # 去掉已取消的项目

# 每个项目的世界纪录（成绩越小越好，所以取最小值）
wr = df.groupby("event_id")["best"].min()

# 单项得分 = WR / 选手成绩 * 100，范围 (0, 100]，世界纪录保持者是 100
df["score"] = df["event_id"].map(wr) / df["best"] * 100

# 选手 x 项目 的得分矩阵，没参加的项目记 0 分
scores = df.pivot(index="person_id", columns="event_id", values="score").fillna(0)

# 综合成绩 = 所有项目得分的平均值（分母是项目总数，不是该选手参加的项目数）
kinch = (scores.mean(axis=1)
               .rename("kinch")
               .reset_index()
               .sort_values(["kinch", "person_id"], ascending=[False, True]))

# Kinch 越高越好，所以降序排名；并列取最小名次
kinch["kinch_rank"] = kinch["kinch"].rank(method="min", ascending=False).astype(int)

# 姓名和国籍
persons = pd.read_csv(
    "./data/WCA_export_persons.tsv",
    sep="\t",
    dtype=str,
    usecols=["wca_id", "sub_id", "name", "country_id"],
)
persons = persons[persons["sub_id"] == "1"]
persons = persons.rename(columns={"wca_id": "person_id", "country_id": "nationality"})

kinch = kinch.merge(persons[["person_id", "name", "nationality"]],
                    on="person_id", how="left")
kinch["kinch"] = kinch["kinch"].round(2)
kinch = kinch[["kinch_rank", "person_id", "name", "nationality", "kinch"]]

os.makedirs("./output", exist_ok=True)
kinch.to_csv("./output/kinch.csv", index=False, encoding="utf-8-sig")
print(kinch.head(10))
print(f"events counted: {scores.shape[1]}")

t1 = time.perf_counter()
print(f"Time taken: {t1 - t0:.2f} seconds")