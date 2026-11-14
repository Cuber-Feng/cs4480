import os
import time
import numpy as np
import pandas as pd

t0 = time.perf_counter()

REMOVED = ["333ft", "magic", "mmagic", "333mbo"]
MISSING_SCORE = 0           # 没参加的项目记多少分（和 Kinch 一致，记 0）

# 副分表：边界成绩从快到慢，对应的分数
FP = np.array([100, 95, 90, 80, 70, 60, 50, 40], dtype=float)
BOUNDARY_NAMES = ["WR", "p95", "p90", "p80", "p70", "p60", "p50", "slowest"]


def boundaries(a):
    """a: 该项目所有选手的成绩（已升序）。返回 8 个边界成绩，保证非递减。"""
    n = len(a)

    def at_rank(r):                         # 第 r 名的成绩（1-based），超出范围时截断
        return a[min(max(r, 1), n) - 1]

    def top_permille(k):                    # 前 k‰ 对应的名次，向上取整（整数运算，避免浮点误差）
        return at_rank(-(-n * k // 1000))

    b = [
        a[0],                                           # 100: WR
        max(top_permille(1),  at_rank(3)),              # 95 : 前 0.1% 与 WR3 中较慢者
        max(top_permille(10), at_rank(10)),             # 90 : 前 1%   与 WR10 中较慢者
        max(top_permille(50), at_rank(50)),             # 80 : 前 5%   与 WR50 中较慢者
        top_permille(100),                              # 70 : 前 10%
        top_permille(200),                              # 60 : 前 20%
        top_permille(500),                              # 50 : 前 50%
        a[-1],                                          # 40 : 最慢
    ]
    return np.maximum.accumulate(np.array(b, dtype=float))


def piecewise_score(x, xp):
    """对成绩 x 在相邻边界之间做线性插值，返回 40~100 的分数（越快分越高）。"""
    x = x.astype(float)
    j = np.searchsorted(xp, x, side="left")         # 第一个 >= x 的边界
    j = np.clip(j, 0, len(xp) - 1)
    lo = np.clip(j - 1, 0, None)
    denom = xp[j] - xp[lo]
    denom = np.where(denom == 0, 1, denom)
    frac = np.clip((x - xp[lo]) / denom, 0, 1)
    score = FP[lo] + frac * (FP[j] - FP[lo])
    score = np.where(xp[j] == x, FP[j], score)      # 恰好等于边界时取该边界的分数（并列时取高分）
    return np.clip(score, FP[-1], FP[0])


df = pd.read_csv(
    "./data/WCA_export_ranks_average.tsv",
    sep="\t",
    dtype={"person_id": str, "event_id": str},
)
df = df[~df["event_id"].isin(REMOVED)].copy()

# ---- 每个项目：算边界成绩，再给每个人的成绩打分 ----
df["score"] = 0.0
bound_rows = {}
for ev, g in df.groupby("event_id"):
    xp = boundaries(np.sort(g["best"].to_numpy()))
    bound_rows[ev] = xp
    df.loc[g.index, "score"] = piecewise_score(g["best"].to_numpy(), xp)

bounds = pd.DataFrame(bound_rows, index=BOUNDARY_NAMES).T
bounds.insert(0, "participants", df.groupby("event_id").size())

# ---- 选手 x 项目 的得分矩阵，没参加的记 MISSING_SCORE，再取平均 ----
scores = df.pivot(index="person_id", columns="event_id", values="score").fillna(MISSING_SCORE)

maple = (scores.mean(axis=1)
               .rename("maple")
               .reset_index()
               .sort_values(["maple", "person_id"], ascending=[False, True]))
maple["maple_rank"] = maple["maple"].rank(method="min", ascending=False).astype(int)

# ---- 姓名和国籍 ----
persons = pd.read_csv(
    "./data/WCA_export_persons.tsv",
    sep="\t",
    dtype=str,
    usecols=["wca_id", "sub_id", "name", "country_id"],
)
persons = persons[persons["sub_id"] == "1"]
persons = persons.rename(columns={"wca_id": "person_id", "country_id": "nationality"})

maple = maple.merge(persons[["person_id", "name", "nationality"]], on="person_id", how="left")
maple["maple"] = maple["maple"].round(2)
maple = maple[["maple_rank", "person_id", "name", "nationality", "maple"]]

os.makedirs("./output", exist_ok=True)
maple.to_csv("./output/maple.csv", index=False, encoding="utf-8-sig")
bounds.to_csv("./output/maple_boundaries.csv", encoding="utf-8-sig")

print(maple.head(10))
if "333" in bounds.index:                            # 用 3x3 对照你表里的边界成绩（单位：秒）
    print((bounds.loc["333", BOUNDARY_NAMES] / 100).round(2))
print(f"events counted: {scores.shape[1]}")

t1 = time.perf_counter()
print(f"Time taken: {t1 - t0:.2f} seconds")