# CS4480 Group Project

> Last Edit: 14:01, Sat, Nov-14, 2026, by Cody Feng

## Download the dataset

```bash
curl -L -O https://www.worldcubeassociation.org/export/results/v2/tsv
```

And then, unzip the downloaded file, move it to directary called `data`.

## Environment

Need: `python`, `java`, `pyspark`, `pandas`

## Running

Run each .py file

For `*-parallel.py`, you can run it by `python *-parallel.py [num of cores]` to define how many cores you want to use.

### Make the dataset larger

```bash
head -n 1 WCA_export_ranks_average.tsv > big.tsv
for i in $(seq 300); do tail -n +2 WCA_export_ranks_average.tsv >> big.tsv; done
```