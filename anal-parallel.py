import time
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.master("local[10]").appName("wca").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

df = spark.read.csv("./data/WCA_export_ranks_average.tsv", sep="\t", header=True, inferSchema=True)

t0 = time.perf_counter()

removed_events = ["333ft", "magic", "mmagic", "333mbo"]
df = df[~df["event_id"].isin(removed_events)]

qs = ",".join(str(i / 10) for i in range(1,11))
out = (df.groupBy("event_id")
         .agg(F.count("*").alias("participants"),
              F.min("best").alias("world_record"),
              F.expr(f"percentile_approx(best, array({qs}))").alias("pcts")))
for i in range(1, 11):
    out = out.withColumn(f"p{i*10}", F.col("pcts")[i])
out = out.drop("pcts").orderBy(F.desc("participants"))

out.coalesce(1).write.mode("overwrite").csv("./output/event_stats_spark", sep=",", header=True)

t1 = time.perf_counter()
print(f"Time taken: {t1 - t0:.2f} seconds")