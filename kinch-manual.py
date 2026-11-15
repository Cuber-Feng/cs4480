import io
import os
import sys
import time
import pandas as pd
from multiprocessing import Pool
from tqdm import tqdm

PATH = "./data/big.tsv"                    # 或 ./data/WCA_export_ranks_average.tsv
REMOVED = ["333ft", "magic", "mmagic", "333mbo"]


def make_chunks(path, n_chunks):
    """按字节切分文件，每块都从一行的开头开始，返回 (表头, [(start, end), ...])。"""
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        header = f.readline()
        start = f.tell()
        step = (size - start) // n_chunks + 1
        offsets = [start]
        for i in range(1, n_chunks):
            f.seek(start + i * step)
            f.readline()                   # 跳到下一行的开头，避免把一行切成两半
            offsets.append(f.tell())
        offsets.append(size)
    return header, [(s, e) for s, e in zip(offsets[:-1], offsets[1:]) if s < e]


def read_chunk(path, header, start, end):
    with open(path, "rb") as f:
        f.seek(start)
        data = f.read(end - start)
    df = pd.read_csv(
        io.BytesIO(header + data), sep="\t",
        usecols=["person_id", "event_id", "best"],
        dtype={"person_id": str, "event_id": str, "best": "int32"},
    )
    return df[~df["event_id"].isin(REMOVED)]


# ---------- Map 1：每块算每个项目的局部最小成绩 ----------
def map_wr(task):
    df = read_chunk(*task)
    return df.groupby("event_id")["best"].min().to_dict()


# ---------- Map 2：每块算每个选手的得分之和（块内先聚合）----------
def map_score(args):
    wr, path, header, start, end = args
    df = read_chunk(path, header, start, end)
    score = df["event_id"].map(wr) / df["best"] * 100
    return score.groupby(df["person_id"]).sum()


def main():
    cores = int(sys.argv[1]) if len(sys.argv) > 1 else os.cpu_count()   # 用法: python kinch_mp.py 4
    size = os.path.getsize(PATH)
    n_chunks = max(cores, size // (128 << 20) + 1)       # 每块约 128 MB，且不少于核数
    header, ranges = make_chunks(PATH, n_chunks)
    tasks = [(PATH, header, s, e) for s, e in ranges]

    t0 = time.perf_counter()
    with Pool(cores) as pool:
        # Reduce 1：合并局部 WR，取全局最小
        wr = {}
        for part in tqdm(pool.imap_unordered(map_wr, tasks),
                         total=len(tasks), desc="1/2 world records", unit="chunk"):
            for ev, v in part.items():
                wr[ev] = min(v, wr.get(ev, v))

        # Reduce 2：把各块的选手得分之和累加
        total = None
        for part in tqdm(pool.imap_unordered(map_score, [(wr,) + t for t in tasks]),
                         total=len(tasks), desc="2/2 kinch scores  ", unit="chunk"):
            total = part if total is None else total.add(part, fill_value=0)
    t1 = time.perf_counter()

    # ---------- 以下是串行的收尾工作 ----------
    kinch = (total / len(wr)).rename("kinch").reset_index()
    kinch = kinch.sort_values(["kinch", "person_id"], ascending=[False, True])
    kinch["kinch_rank"] = kinch["kinch"].rank(method="min", ascending=False).astype(int)

    persons = pd.read_csv("./data/WCA_export_persons.tsv", sep="\t", dtype=str,
                          usecols=["wca_id", "sub_id", "name", "country_id"])
    persons = persons[persons["sub_id"] == "1"].rename(
        columns={"wca_id": "person_id", "country_id": "nationality"})
    kinch = kinch.merge(persons[["person_id", "name", "nationality"]], on="person_id", how="left")
    kinch["kinch"] = kinch["kinch"].round(2)
    kinch = kinch[["kinch_rank", "person_id", "name", "nationality", "kinch"]]

    os.makedirs("./output", exist_ok=True)
    kinch.to_csv("./output/kinch_mp.csv", index=False, encoding="utf-8-sig")
    t2 = time.perf_counter()

    print(kinch.head(5))
    # print(f"cores: {cores} | chunks: {len(tasks)} | map+reduce {t1 - t0:.2f}s | total {t2 - t0:.2f}s")

    t_par = t1 - t0          # parallel phase
    t_post = t2 - t1         # post-processing (serial)
    print(f"cores: {cores} | chunks: {len(tasks)} | parallel {t_par:.2f}s | "
        f"post-processing {t_post:.2f}s | total {t2 - t0:.2f}s")


if __name__ == "__main__":                 # macOS 用 spawn 启动进程，这一行必须有
    main()