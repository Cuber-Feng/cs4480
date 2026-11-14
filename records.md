# Running Time

## Kinch

- Dataset: 3.4GB, tsv
- Using `pyspark`

```
cores: 8 | startup 7.36s | compute+write 109.77s
cores: 7 | startup 6.40s | compute+write 106.56s
cores: 6 | startup 6.48s | compute+write 107.59s
cores: 5 | startup 6.50s | compute+write 118.20s
cores: 4 | startup 6.46s | compute+write 132.43s
cores: 3 | startup 6.62s | compute+write 155.94s
cores: 2 | startup 6.68s | compute+write 193.33s
cores: 1 | startup 6.55s | compute+write 345.80s
```

When using pandas, the os force to stop the program because it using too much memory. `Device memory is nearly full. An application was using a lot of memory and was forced to stop.`