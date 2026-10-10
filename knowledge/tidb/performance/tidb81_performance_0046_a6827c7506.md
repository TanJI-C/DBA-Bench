# TPC-C benchmark procedure and result

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/v5.0-performance-benchmarking-with-tpcc.md`
- Source Title: `TiDB TPC-C Performance Test Report -- v5.0 vs. v4.0`
- Source Heading Path: `TiDB TPC-C Performance Test Report -- v5.0 vs. v4.0 > Test plan | TiDB TPC-C Performance Test Report -- v5.0 vs. v4.0 > Test result`
- Source Line Ranges: `119-149`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tiup`, `sql`, `ecosystem`
- Topic Tags: `tpcc`, `benchmarking`, `test-plan`, `benchmarksql`, `data-import`, `analyze-table`, `tpmc`, `performance-results`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0046_a6827c7506`
- Source ID: `tidb-docs-8.1:benchmark/v5.0-performance-benchmarking-with-tpcc.md#test-plan`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c154da6743a0732e89f60b1f33439c0a69e4dac06766a252cce8838459f1d651`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/v5.0-performance-benchmarking-with-tpcc#test-plan
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/v5.0-performance-benchmarking-with-tpcc.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact TPC-C benchmark procedure with BenchmarkSQL and the reported result for the TiDB v5.0 versus v4.0 comparison.
- Retrieval Keywords: Test plan, Test result, Deploy TiDB v5.0 and v4.0 using TiUP, BenchmarkSQL, TPC-C 5000 Warehouse data, git clone https://github.com/pingcap/benchmarksql, ant, props.mysql, conn, warehouses, loadWorkers, terminals, runMins, runSQL.sh ./props.mysql sql.mysql/tableCreates.sql, runSQL.sh ./props.mysql sql.mysql/indexCreates.sql, analyze table, runBenchmark.sh ./props.mysql, tpmC, New Order, increased by 36%
- Follow-up Guidance: The source also lists the AWS EC2 environment, software versions, parameter configuration, and TiDB global variable configuration used for this benchmark.
- Classification Note: This is classified as performance because the content describes the benchmark execution steps and the measured TPC-C performance result.

## Official Source Content

## Test plan

1. Deploy TiDB v5.0 and v4.0 using TiUP.

2. Use BenchmarkSQL to import the TPC-C 5000 Warehouse data.

    1. Compile BenchmarkSQL:

        ```bash
        git clone https://github.com/pingcap/benchmarksql && cd benchmarksql && ant
        ```

    2. Enter the `run` directory, edit the `props.mysql` file according to the actual situation, and modify the `conn`, `warehouses`, `loadWorkers`, `terminals`, and `runMins` configuration items.

    3. Execute the `runSQL.sh ./props.mysql sql.mysql/tableCreates.sql` command.

    4. Execute the `runSQL.sh ./props.mysql sql.mysql/indexCreates.sql` command.

    5. Run MySQL client and execute the `analyze table` statement on every table.

3. Execute the `runBenchmark.sh ./props.mysql` command.

4. Extract the tpmC data of New Order from the result.
## Test result

According to the test statistics, the TPC-C performance of TiDB v5.0 has **increased by 36%** compared with that of TiDB v4.0.

![TPC-C](/media/tpcc_v5vsv4_corrected_v2.png)
