import sys
import time
from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F

cores = sys.argv[1] if len(sys.argv) > 1 else "*"      # 用法: python sor_spark.py 4

K = 1.5                       # 惩罚因子，k >= 1
REMOVED = ["333ft", "magic", "mmagic", "333mbo"]

# ---------- 启动 Spark（单独计时）----------
t_start = time.perf_counter()
spark = (SparkSession.builder
         .master(f"local[{cores}]")
         .appName("sor")
         .config("spark.sql.shuffle.partitions", "10")   # 默认 200，本地小数据没必要
         .getOrCreate())
spark.sparkContext.setLogLevel("ERROR")
t_ready = time.perf_counter()

# ---------- 计算部分 ----------
t0 = time.perf_counter()

# 显式指定 schema：event_id 要保持字符串，否则 inferSchema 会把 "333" 当成整数
ranks_schema = ("best INT, person_id STRING, event_id STRING, "
                "world_rank INT, continent_rank INT, country_rank INT")
df = (spark.read.csv("./data/WCA_export_ranks_average.tsv",
                     sep="\t", header=True, schema=ranks_schema)
        .filter(~F.col("event_id").isin(REMOVED)))

# 每个项目的惩罚排名：n * K（想用 n + K 就改这里）
pen = df.groupBy("event_id").agg((F.count("*") * K).alias("pen"))
total_pen = pen.agg(F.sum("pen")).first()[0]

# SOR = 已有成绩的排名之和 + 所有项目的惩罚之和 - 该选手已参加项目的惩罚之和
sor = (df.join(F.broadcast(pen), "event_id")
         .groupBy("person_id")
         .agg((F.sum("world_rank") + F.lit(total_pen) - F.sum("pen")).alias("SOR")))

# 选手信息：只保留 sub_id = 1 的当前记录
persons = (spark.read.csv("./data/WCA_export_persons.tsv", sep="\t", header=True)
             .filter(F.col("sub_id") == "1")
             .select(F.col("wca_id").alias("person_id"),
                     "name",
                     F.col("country_id").alias("nationality")))

# sor_rank：rank() 并列取最小名次，等价于 pandas 的 method="min"
result = (sor.withColumn("sor_rank", F.rank().over(Window.orderBy("SOR")))
             .join(persons, "person_id", "left")
             .select("sor_rank", "person_id", "name", "nationality", "SOR")
             .orderBy("sor_rank", "person_id"))

result.coalesce(1).write.mode("overwrite").option("header", True).csv("./output/sor_spark")

t1 = time.perf_counter()

result.show(10, truncate=False)     # 注意：这会重新计算一遍，所以放在计时之后
print(f"Cores: {cores} | startup {t_ready - t_start:.2f}s | compute+write {t1 - t0:.2f}s")
spark.stop()