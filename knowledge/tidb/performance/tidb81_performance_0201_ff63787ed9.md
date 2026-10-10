# TiDB Cloud Sysbench performance reference by vCPU scale

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-performance-reference.md`
- Source Title: `TiDB Cloud Performance Reference`
- Source Heading Path: `TiDB Cloud Performance Reference | TiDB Cloud Performance Reference > 4 vCPU performance | TiDB Cloud Performance Reference > 8 vCPU performance | TiDB Cloud Performance Reference > 16 vCPU performance | TiDB Cloud Performance Reference > 32 vCPU performance`
- Source Line Ranges: `5-166`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tikv`
- Topic Tags: `sysbench`, `benchmark`, `cluster-sizing`, `qps`, `tps`, `latency`, `p95`, `vcpu`, `read-workload`, `mixed-workload`, `write-workload`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0201_ff63787ed9`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-performance-reference.md#tidb-cloud-performance-reference`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7f30dc1fc3ccbde60752e8478bb19fdbd2ff88842158021f0e9a4dbf5ade979c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-performance-reference#tidb-cloud-performance-reference
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-performance-reference.md

## Retrieval Guidance

- Use When: Use this chunk when comparing TiDB Cloud Sysbench benchmark results across 4 vCPU, 8 vCPU, 16 vCPU, and 32 vCPU cluster scales for read, mixed, or write workloads with QPS, TPS, threads, and P95 transaction latency figures.
- Retrieval Keywords: TiDB Cloud Performance Reference, Sysbench, determine the cluster size, 4 vCPU performance, 8 vCPU performance, 16 vCPU performance, 32 vCPU performance, Read Only, Read Write, Write Only, QPS, TPS, P95 transaction latency, Average transaction latency, TiDB (8 vCPU, 16 GiB) * 12; TiKV (8 vCPU, 32 GiB) * 9, TiDB (32 vCPU, 64 GiB) * 2; TiKV (32 vCPU, 128 GiB) * 3, mysql-ignore-errors=1062,2013,8028,9002,9007
- Follow-up Guidance: The source also includes an example Sysbench configuration file and states that the tests were performed on TiDB v6.1.1 with P95 transaction latency below 105 ms.
- Classification Note: This is classified as performance content because it provides benchmark reference data for TiDB Cloud cluster sizing, including workload models, thread counts, throughput, and latency measurements.

## Official Source Content

# TiDB Cloud Performance Reference

This document provides [Sysbench](https://github.com/akopytov/sysbench) performance test results of different TiDB cluster scales, which can be used as a reference when you [determine the cluster size](https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster).

> **Note:**
>
> The tests are performed on TiDB v6.1.1, and the test results are based on the condition that the P95 transaction latency is below 105 ms.

Here is an example of a Sysbench configuration file:

```txt
mysql-host={TIDB_HOST}
mysql-port=4000
mysql-user=root
mysql-password=password
mysql-db=sbtest
time=1200
threads={100}
report-interval=10
db-driver=mysql
mysql-ignore-errors=1062,2013,8028,9002,9007
auto-inc=false
```

In this document, the transaction models `Read Only`, `Read Write`, and `Write Only` represent read workloads, mixed workloads, and write workloads.
## 4 vCPU performance

Test scales:

- TiDB (4 vCPU, 16 GiB) \* 1; TiKV (4 vCPU, 16 GiB) \* 3
- TiDB (4 vCPU, 16 GiB) \* 2; TiKV (4 vCPU, 16 GiB) \* 3

Test results:

**TiDB (4 vCPU, 16 GiB) \* 1; TiKV (4 vCPU, 16 GiB) \* 3**

| Transaction model | Threads | QPS      | TPS      | Average transaction latency (ms) | P95 transaction latency (ms) |
|-------------------|---------|----------|----------|----------------------|------------------|
| Read Only         | 35      | 8,064.89 | 504.06   | 69.43                | 104.84           |
| Read Write        | 25      | 6,747.60 | 337.38   | 74.10                | 102.97           |
| Write Only        | 90      | 8,805.21 | 1,467.53 | 61.32                | 99.33            |

**TiDB (4 vCPU, 16 GiB) \* 2; TiKV (4 vCPU, 16 GiB) \* 3**

| Transaction model | Threads | QPS       | TPS      | Average transaction latency (ms) | P95 transaction latency (ms) |
|-------------------|---------|-----------|----------|----------------------|------------------|
| Read Only         | 65      | 16,805.76 | 1,050.36 | 61.88                | 95.81            |
| Read Write        | 45      | 12,940.36 | 647.02   | 69.55                | 99.33            |
| Write Only        | 200     | 19,265.93 | 3,210.99 | 62.28                | 102.97           |
## 8 vCPU performance

Test scales:

- TiDB (8 vCPU, 16 GiB) \* 2; TiKV (8 vCPU, 32 GiB) \* 3
- TiDB (8 vCPU, 16 GiB) \* 4; TiKV (8 vCPU, 32 GiB) \* 3
- TiDB (8 vCPU, 16 GiB) \* 4; TiKV (8 vCPU, 32 GiB) \* 6
- TiDB (8 vCPU, 16 GiB) \* 6; TiKV (8 vCPU, 32 GiB) \* 9
- TiDB (8 vCPU, 16 GiB) \* 9; TiKV (8 vCPU, 32 GiB) \* 6
- TiDB (8 vCPU, 16 GiB) \* 12; TiKV (8 vCPU, 32 GiB) \* 9

Test results:

**TiDB (8 vCPU, 16 GiB) \* 2; TiKV (8 vCPU, 32 GiB) \* 3**

| Transaction model | Threads | QPS       | TPS      | Average transaction latency (ms) | P95 transaction latency (ms) |
|-------------------|---------|-----------|----------|----------------------|------------------|
| Read Only         | 150     | 37,863.64 | 2,366.48 | 63.38                | 99.33            |
| Read Write        | 100     | 30,218.42 | 1,510.92 | 66.18                | 94.10            |
| Write Only        | 350     | 30,763.72 | 5,127.29 | 68.26                | 104.84           |

**TiDB (8 vCPU, 16 GiB) \* 4; TiKV (8 vCPU, 32 GiB) \* 3**

| Transaction model | Threads | QPS       | TPS      | Average transaction latency (ms) | P95 transaction latency (ms) |
|-------------------|---------|-----------|----------|----------------------|------------------|
| Read Only         | 300     | 74,190.40 | 4,636.90 | 64.69                | 104.84           |
| Read Write        | 200     | 53,351.84 | 2,667.59 | 74.97                | 97.55            |
| Write Only        | 400     | 36,036.40 | 5,926.66 | 67.49                | 95.81            |

**TiDB (8 vCPU, 16 GiB) \* 4; TiKV (8 vCPU, 32 GiB) \* 6**

| Transaction model | Threads | QPS       | TPS       | Average transaction latency (ms) | P95 transaction latency (ms) |
|-------------------|---------|-----------|-----------|----------------------|------------------|
| Read Only         | 300     | 75,713.04 | 4,732.06  | 63.39                | 102.97           |
| Read Write        | 200     | 62,640.62 | 3,132.03  | 63.85                | 95.81            |
| Write Only        | 750     | 73,840.22 | 12,306.70 | 60.93                | 104.84           |

**TiDB (8 vCPU, 16 GiB) \* 6; TiKV (8 vCPU, 32 GiB) \* 9**

| Transaction model | Threads | QPS        | TPS       | Average transaction latency (ms) | P95 transaction latency (ms) |
|-------------------|---------|------------|-----------|----------------------|------------------|
| Read Only         | 450     | 113,407.94 | 7,088.00  | 63.48                | 104.84           |
| Read Write        | 300     | 92,387.31  | 4,619.37  | 64.93                | 99.33            |
| Write Only        | 1100    | 112,631.72 | 18,771.95 | 58.59                | 99.33            |

**TiDB (8 vCPU, 16 GiB) \* 9; TiKV (8 vCPU, 32 GiB) \* 6**

| Transaction model | Threads | QPS        | TPS       | Average transaction latency (ms) | P95 transaction latency (ms) |
|-------------------|---------|------------|-----------|----------------------|------------------|
| Read Only         | 650     | 168,486.65 | 10,530.42 | 61.72                | 101.13           |
| Read Write        | 400     | 106,853.63 | 5,342.68  | 74.86                | 101.13           |
| Write Only        | 950     | 88,461.20  | 14,743.53 | 64.42                | 102.97           |

**TiDB (8 vCPU, 16 GiB) \* 12; TiKV (8 vCPU, 32 GiB) \* 9**

| Transaction model | Threads | QPS        | TPS       | Average transaction latency (ms) | P95 transaction latency (ms) |
|-------------------|---------|------------|-----------|----------------------|------------------|
| Read Only         | 800     | 211,882.77 | 13,242.67 | 60.40                | 101.13           |
| Read Write        | 550     | 139,393.46 | 6,969.67  | 78.90                | 104.84           |
| Write Only        | 1500    | 139,330.14 | 23,221.69 | 64.58                | 99.33            |
## 16 vCPU performance

Test scales:

- TiDB (16 vCPU, 32 GiB) \* 1; TiKV (16 vCPU, 64 GiB) \* 3
- TiDB (16 vCPU, 32 GiB) \* 2; TiKV (16 vCPU, 64 GiB) \* 3

Test results:

**TiDB (16 vCPU, 32 GiB) \* 1; TiKV (16 vCPU, 64 GiB) \* 3**

| Transaction model | Threads | QPS      | TPS     | Average transaction latency (ms) | P95 transaction latency (ms) |
|-------------------|---------|----------|---------|----------------------|------------------|
| Read Only         | 125     | 37448.41 | 2340.53 | 53.40                | 89.16            |
| Read Write        | 100     | 28903.99 | 1445.20 | 69.19                | 104.84           |
| Write Only        | 400     | 40878.68 | 6813.11 | 58.71                | 101.13           |

**TiDB (16 vCPU, 32 GiB) \* 2; TiKV (16 vCPU, 64 GiB) \* 3**

| Transaction model | Threads | QPS      | TPS      | Average transaction latency (ms) | P95 transaction latency (ms) |
|-------------------|---------|----------|----------|----------------------|------------------|
| Read Only         | 300     | 77238.30 | 4827.39  | 62.14                | 102.97           |
| Read Write        | 200     | 58241.15 | 2912.06  | 68.67                | 97.55            |
| Write Only        | 700     | 68829.89 | 11471.65 | 61.01                | 101.13           |
## 32 vCPU performance

Test scales:

- TiDB (32 vCPU, 64 GiB) \* 1; TiKV (32 vCPU, 128 GiB) \* 3
- TiDB (32 vCPU, 64 GiB) \* 2; TiKV (32 vCPU, 128 GiB) \* 3

Test results:

**TiDB (32 vCPU, 64 GiB) \* 1; TiKV (32 vCPU, 128 GiB) \* 3**

| Transaction model | Threads | QPS      | TPS     | Average transaction latency (ms) | P95 transaction latency (ms) |
|-------------------|---------|----------|---------|----------------------|------------------|
| Read Only         | 300     | 83941.16 | 5246    | 57.20                | 87.6             |
| Read Write        | 250     | 71290.31 | 3565    | 70.10                | 105.0            |
| Write Only        | 700     | 72199.56 | 12033   | 58.20                | 101.0            |

**TiDB (32 vCPU, 64 GiB) \* 2; TiKV (32 vCPU, 128 GiB) \* 3**

| Transaction model | Threads | QPS       | TPS      | Average transaction latency (ms) | P95 transaction latency (ms) |
|-------------------|---------|-----------|----------|----------------------|------------------|
| Read Only         | 650     | 163101.68 | 10194    | 63.8                 | 99.3             |
| Read Write        | 450     | 123152.74 | 6158     | 73.1                 | 101              |
| Write Only        | 1200    | 112333.16 | 18722    | 64.1                 | 101              |
