# Running Time

## Kinch

- Dataset: 3.4GB, tsv
- Using `pyspark`

```

cores: 8 | startup 7.37s | compute+write 93.07s
cores: 8 | startup 4.08s | compute+write 82.88s
cores: 8 | startup 3.96s | compute+write 83.76s

cores: 7 | startup 3.83s | compute+write 79.77s
cores: 7 | startup 3.79s | compute+write 78.97s
cores: 7 | startup 3.79s | compute+write 80.42s

cores: 6 | startup 4.09s | compute+write 81.28s
cores: 6 | startup 4.13s | compute+write 82.07s
cores: 6 | startup 3.89s | compute+write 87.60s

cores: 5 | startup 3.88s | compute+write 86.77s
cores: 5 | startup 3.87s | compute+write 81.49s
cores: 5 | startup 3.98s | compute+write 83.39s

cores: 4 | startup 4.00s | compute+write 93.75s
cores: 4 | startup 4.03s | compute+write 99.81s
cores: 4 | startup 4.29s | compute+write 93.78s

cores: 3 | startup 4.01s | compute+write 106.92s
cores: 3 | startup 4.33s | compute+write 106.80s
cores: 3 | startup 4.08s | compute+write 107.61s

cores: 2 | startup 3.92s | compute+write 130.59s
cores: 2 | startup 3.89s | compute+write 120.14s
cores: 2 | startup 4.26s | compute+write 123.12s

cores: 1 | startup 3.93s | compute+write 199.92s
cores: 1 | startup 4.02s | compute+write 196.55s
cores: 1 | startup 4.05s | compute+write 193.88s
```

When using pandas, the os force to stop the program because it using too much memory. `Device memory is nearly full. An application was using a lot of memory and was forced to stop.`
