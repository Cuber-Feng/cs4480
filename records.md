# Running Time

## Kinch

- Dataset: 3.4 GB, .tsv
- Using `pyspark`

```
cores: 8 | startup 3.79s | compute+write 81.13s
cores: 8 | startup 3.53s | compute+write 82.69s
cores: 8 | startup 3.77s | compute+write 82.09s

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

- Using Manual Parallelism

```
cores: 8 | chunks: 26 | parallel 54.24s | post-processing 0.93s | total 55.17s
cores: 8 | chunks: 26 | parallel 53.74s | post-processing 0.93s | total 54.67s
cores: 8 | chunks: 26 | parallel 53.02s | post-processing 0.90s | total 53.92s

cores: 7 | chunks: 26 | parallel 53.28s | post-processing 0.97s | total 54.26s
cores: 7 | chunks: 26 | parallel 52.65s | post-processing 0.94s | total 53.59s
cores: 7 | chunks: 26 | parallel 53.04s | post-processing 0.97s | total 54.02s

cores: 6 | chunks: 26 | parallel 51.64s | post-processing 0.97s | total 52.61s
cores: 6 | chunks: 26 | parallel 51.98s | post-processing 0.97s | total 52.95s
cores: 6 | chunks: 26 | parallel 51.35s | post-processing 0.96s | total 52.31s

cores: 5 | chunks: 26 | parallel 52.13s | post-processing 0.97s | total 53.10s
cores: 5 | chunks: 26 | parallel 52.37s | post-processing 0.97s | total 53.34s
cores: 5 | chunks: 26 | parallel 52.00s | post-processing 0.96s | total 52.97s

cores: 4 | chunks: 26 | parallel 53.18s | post-processing 0.91s | total 54.09s
cores: 4 | chunks: 26 | parallel 53.65s | post-processing 0.96s | total 54.61s
cores: 4 | chunks: 26 | parallel 53.67s | post-processing 0.93s | total 54.60s

cores: 3 | chunks: 26 | parallel 56.43s | post-processing 0.97s | total 57.40s
cores: 3 | chunks: 26 | parallel 56.26s | post-processing 0.95s | total 57.20s
cores: 3 | chunks: 26 | parallel 56.01s | post-processing 0.97s | total 56.98s

cores: 2 | chunks: 26 | parallel 62.98s | post-processing 1.03s | total 64.01s
cores: 2 | chunks: 26 | parallel 63.72s | post-processing 0.96s | total 64.68s
cores: 2 | chunks: 26 | parallel 62.15s | post-processing 0.96s | total 63.11s

cores: 1 | chunks: 26 | parallel 107.35s | post-processing 1.00s | total 108.35s
cores: 1 | chunks: 26 | parallel 105.33s | post-processing 0.97s | total 106.29s
cores: 1 | chunks: 26 | parallel 106.71s | post-processing 1.02s | total 107.74s

```

- CityU Machine

```
cores: 96 | chunks: 96 | parallel 213.84s | post-processing 2.57s | total 216.41s
cores: 32 | chunks: 32 | parallel 135.37s | post-processing 2.54s | total 137.92s
cores: 26 | chunks: 26 | parallel 114.92s | post-processing 2.56s | total 117.48s
cores: 16 | chunks: 26 | parallel 111.94s | post-processing 2.44s | total 114.38s
cores: 15 | chunks: 26 | parallel 103.52s | post-processing 3.22s | total 106.74s
cores: 14 | chunks: 26 | parallel 109.85s | post-processing 3.22s | total 113.07s
cores: 13 | chunks: 26 | parallel 99.97s  | post-processing 2.60s | total 102.57s
cores: 12 | chunks: 26 | parallel 98.30s  | post-processing 2.53s | total 100.83s
cores: 11 | chunks: 26 | parallel 102.83s | post-processing 3.26s | total 106.09s
cores: 10 | chunks: 26 | parallel 93.95s  | post-processing 3.19s | total 97.13s
cores:  9 | chunks: 26 | parallel 103.11s | post-processing 2.51s | total 105.62s
cores:  8 | chunks: 26 | parallel 97.23s  | post-processing 2.47s | total 99.70s
cores:  7 | chunks: 26 | parallel 93.69s  | post-processing 2.64s | total 96.33s
cores:  6 | chunks: 26 | parallel 93.00s  | post-processing 2.57s | total 95.57s
cores:  5 | chunks: 26 | parallel 91.90s  | post-processing 2.53s | total 94.43s
cores:  4 | chunks: 26 | parallel 81.64s  | post-processing 2.57s | total 84.20s
cores:  3 | chunks: 26 | parallel 98.64s  | post-processing 2.64s | total 101.28s
cores:  2 | chunks: 26 | parallel 149.03s | post-processing 2.55s | total 151.58s
cores:  1 | chunks: 26 | parallel 296.74s | post-processing 2.57s | total 299.31s
```

When using pandas, the OS force to stop the program because it using too much memory. `Device memory is nearly full. An application was using a lot of memory and was forced to stop.`
