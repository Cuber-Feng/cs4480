import os
import sys
import time
from pyspark.sql import SparkSession, Window # type: ignore
from pyspark.sql import functions as F # type: ignore

cores = sys.argv[1] if len(sys.argv) > 1 else os.cpu_count()      # 用法: python kinch_spark.py 4

REMOVED = ["333ft", "magic", "mmagic", "333mbo"]

# ---------- 启动 Spark（单独计时）----------
t_start = time.perf_counter()
spark = (SparkSession.builder
         .master(f"local[{cores}]")
         .appName("kinch")
         .config("spark.sql.shuffle.partitions", "10")
         # .config("spark.sql.files.maxPartitionBytes", str(1024 * 1024))   # 1 MB
         .getOrCreate())
spark.sparkContext.setLogLevel("ERROR")
print("Spark dashboard: http://localhost:4040")
t_ready = time.perf_counter()

# ---------- 计算部分 ----------
t0 = time.perf_counter()

ranks_schema = ("best INT, person_id STRING, event_id STRING, "
                "world_rank INT, continent_rank INT, country_rank INT")

df = (spark.read.csv("./data/WCA_export_ranks_average.tsv",
                     sep="\t", header=True, schema=ranks_schema)
        .filter(~F.col("event_id").isin(REMOVED)))

# df = (spark.read.csv("./data/big.tsv",
#                      sep="\t", header=True, schema=ranks_schema)
#         .filter(~F.col("event_id").isin(REMOVED)))


# 每个项目的世界纪录（成绩越小越好，取最小值）
wr = df.groupBy("event_id").agg(F.min("best").alias("wr"))

# 项目总数，作为平均值的分母（没参加的项目记 0 分，所以分母是所有项目，不是选手参加的项目数）
num_events = wr.count()

# 单项得分 = WR / 选手成绩 * 100，再按选手求和后除以项目总数
kinch = (df.join(F.broadcast(wr), "event_id")
           .withColumn("score", F.col("wr") / F.col("best") * 100)
           .groupBy("person_id")
           .agg((F.sum("score") / F.lit(num_events)).alias("kinch")))

# 选手信息：只保留 sub_id = 1 的当前记录
persons = (spark.read.csv("./data/WCA_export_persons.tsv", sep="\t", header=True)
             .filter(F.col("sub_id") == "1")
             .select(F.col("wca_id").alias("person_id"),
                     "name",
                     F.col("country_id").alias("nationality")))

# kinch_rank：Kinch 越高越好，所以降序；rank() 并列取最小名次，等价于 pandas 的 method="min"
result = (kinch.withColumn("kinch_rank", F.rank().over(Window.orderBy(F.desc("kinch"))))
               .withColumn("kinch", F.round("kinch", 2))        # 先排名，再取两位小数
               .join(persons, "person_id", "left")
               .select("kinch_rank", "person_id", "name", "nationality", "kinch")
               .orderBy("kinch_rank", "person_id"))

result.coalesce(1).write.mode("overwrite").option("header", True).csv("./output/kinch_spark")

t1 = time.perf_counter()

result.show(10, truncate=False)     # 会重新计算一遍，所以放在计时之后

spark.stop()

print(f"cores: {cores} | startup {t_ready - t_start:.2f}s | compute+write {t1 - t0:.2f}s")
input("Press any key to exit...")
