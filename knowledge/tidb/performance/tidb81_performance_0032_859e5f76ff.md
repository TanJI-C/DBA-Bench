# Sysbench test plan and TiDB/TiKV performance configuration

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-tidb-using-sysbench.md`
- Source Title: `How to Test TiDB Using Sysbench`
- Source Heading Path: `How to Test TiDB Using Sysbench | How to Test TiDB Using Sysbench > Test plan | How to Test TiDB Using Sysbench > Test plan > TiDB configuration | How to Test TiDB Using Sysbench > Test plan > TiKV configuration`
- Source Line Ranges: `5-55`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `tiup`, `sql`
- Topic Tags: `sysbench`, `benchmarking`, `log-level`, `plan-cache`, `prepared-statements`, `rocksdb`, `block-cache`, `memory-tuning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0032_859e5f76ff`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-tidb-using-sysbench.md#how-to-test-tidb-using-sysbench`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b64d969034eb33f79e48572df870aec66332594a42e8d7ba17f3524551dcea74`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-tidb-using-sysbench#how-to-test-tidb-using-sysbench
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-tidb-using-sysbench.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the official Sysbench test plan settings for TiDB and TiKV performance, including log levels, prepared plan cache, and RocksDB block cache sizing.
- Retrieval Keywords: Sysbench 1.0 or later, log.level: "error", tidb_enable_prepared_plan_cache, --db-ps-mode=auto, SQL Prepared Execution Plan Cache, TiKV log-level: "error", Default CF : Write CF = 4 : 1, rocksdb.defaultcf.block-cache-size, rocksdb.writecf.block-cache-size, storage.block-cache.capacity, Tune TiKV Performance
- Follow-up Guidance: The source also points to SQL Prepared Execution Plan Cache documentation and Tune TiKV Performance for more detailed information.
- Classification Note: This is classified as performance because the content describes benchmark-oriented TiDB and TiKV configuration choices intended to positively influence performance.

## Official Source Content

# How to Test TiDB Using Sysbench

It is recommended to use Sysbench 1.0 or later, which can be [downloaded here](https://github.com/akopytov/sysbench/releases/tag/1.0.20).
## Test plan
### TiDB configuration

Higher log level means fewer logs to be printed and thus positively influences TiDB performance. Specifically, you can add the following command in the TiUP configuration file:

```yaml
server_configs:
  tidb:
    log.level: "error"
```

It is also recommended to make sure [`tidb_enable_prepared_plan_cache`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_prepared_plan_cache-new-in-v610) is enabled and that you allow sysbench to use prepared statements by using `--db-ps-mode=auto`. See the [SQL Prepared Execution Plan Cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache) for documentation about what the SQL plan cache does and how to monitor it.

> **Note:**
>
> In different versions of Sysbench, the default value of `db-ps-mode` might be different. It is recommended to explicitly specify it in the command.
### TiKV configuration

Higher log level also means better performance for TiKV.

There are multiple Column Families on TiKV cluster which are mainly used to store different types of data, including Default CF, Write CF, and Lock CF. For the Sysbench test, you only need to focus on Default CF and Write CF. The Column Family that is used to import data has a constant proportion among TiDB clusters:

Default CF : Write CF = 4 : 1

Configuring the block cache of RocksDB on TiKV should be based on the machine's memory size, in order to make full use of the memory. To deploy a TiKV cluster on a 40GB virtual machine, it is recommended to configure the block cache as follows:

```yaml
server_configs:
  tikv:
    log-level: "error"
    rocksdb.defaultcf.block-cache-size: "24GB"
    rocksdb.writecf.block-cache-size: "6GB"
```

You can also configure TiKV to share block cache:

```yaml
server_configs:
  tikv:
    storage.block-cache.capacity: "30GB"
```

For more detailed information on TiKV performance tuning, see [Tune TiKV Performance](https://docs.pingcap.com/tidb/stable/tune-tikv-memory-performance).
