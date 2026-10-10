# TPC-H benchmark execution plan and procedure

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/v4.0-performance-benchmarking-with-tpch.md`
- Source Title: `TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0`
- Source Heading Path: `TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0 > Test plan | TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0 > Test plan > Hardware prerequisite | TiDB TPC-H Performance Test Report -- v4.0 vs. v3.0 > Test plan > Test process`
- Source Line Ranges: `109-162`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `test-plan`, `hardware-prerequisite`, `deployment`, `data-import`, `query-execution`, `isolation-read-engines`, `timing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0043_2a30fd876c`
- Source ID: `tidb-docs-8.1:benchmark/v4.0-performance-benchmarking-with-tpch.md#test-plan`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4da3feef9be5f4eb99e1399c1c174a1fcdf41bc6eefe9e28ed0db2a901249c63`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/v4.0-performance-benchmarking-with-tpch#test-plan
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/v4.0-performance-benchmarking-with-tpch.md

## Retrieval Guidance

- Use When: Use this chunk when the request asks for the TPC-H benchmark procedure, TiUP commands, hardware prerequisite, data import steps, or isolation read engine settings for TiKV-only versus TiKV and TiFlash execution.
- Retrieval Keywords: Test plan, Hardware prerequisite, Test process, mount the two NVMe SSD disks, /data1, /data2, Deploy TiKV on /data1, deploy TiFlash on /data2, TiUP, tiup bench tpch prepare, --sf 10, --tiflash, --analyze, --tidb_build_stats_concurrency 8, --tidb_distsql_scan_concurrency 30, git clone https://github.com/pingcap/tidb-bench.git, tpch/queries, tidb_isolation_read_engines, set @@session.tidb_isolation_read_engines = 'tikv,tidb', set @@session.tidb_isolation_read_engines = 'tikv,tiflash,tidb', MySQL client
- Follow-up Guidance: The source ends the procedure by extracting and organizing the data of query execution time.
- Classification Note: This is classified as performance because it describes the benchmark execution workflow, including deployment, import, query execution, and timing collection for performance testing.

## Official Source Content

## Test plan
### Hardware prerequisite

To avoid TiKV and TiFlash racing for disk and I/O resources, mount the two NVMe SSD disks configured on EC2 to `/data1` and `/data2`. Deploy TiKV on `/data1` and deploy TiFlash on `/data2`.
### Test process

1. Deploy TiDB v4.0 and v3.0 using [TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-overview#tiup-overview).

2. Use the bench tool of TiUP to import the TPC-H data with the scale factor 10.

    * Execute the following command to import data into v3.0:

        ```bash
        tiup bench tpch prepare \
        --host ${tidb_v3_host} --port ${tidb_v3_port} --db tpch_10 \
        --sf 10 \
        --analyze --tidb_build_stats_concurrency 8 --tidb_distsql_scan_concurrency 30
        ```

    * Execute the following command to import data into v4.0:

        ```bash
        tiup bench tpch prepare \
          --host ${tidb_v4_host} --port ${tidb_v4_port} --db tpch_10 --password ${password} \
          --sf 10 \
          --tiflash \
          --analyze --tidb_build_stats_concurrency 8 --tidb_distsql_scan_concurrency 30
        ```

3. Execute the TPC-H queries.

    1. Download the TPC-H SQL query file:

        ```bash
        git clone https://github.com/pingcap/tidb-bench.git && cd tpch/queries
        ```

    2. Execute TPC-H queries and record the executing time of each query.

        * For TiDB v3.0, use the MySQL client to connect to TiDB, execute the queries, and record the execution time of each query.
        * For TiDB v4.0, use the MySQL client to connect to TiDB, and choose one of the following operations based on where data is read from:
            * If data is read only from TiKV, set `set @@session.tidb_isolation_read_engines = 'tikv,tidb';`, execute the queries, and record the execution time of each query.
            * If data is read from TiKV and TiFlash automatically based on cost-based intelligent choice, set `set @@session.tidb_isolation_read_engines = 'tikv,tiflash,tidb';`, execute the query, and record the execution time of each query.

4. Extract and organize the data of query execution time.
