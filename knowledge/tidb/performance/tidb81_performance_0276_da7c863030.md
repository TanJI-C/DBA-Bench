# TiUP Bench workload commands and test procedures

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-bench.md`
- Source Title: `Stress Test TiDB Using TiUP Bench Component`
- Source Heading Path: `Stress Test TiDB Using TiUP Bench Component | Stress Test TiDB Using TiUP Bench Component > Run TPC-C test using TiUP | Stress Test TiDB Using TiUP Bench Component > Run TPC-C test using TiUP > Test procedures | Stress Test TiDB Using TiUP Bench Component > Run TPC-H test using TiUP | Stress Test TiDB Using TiUP Bench Component > Run TPC-H test using TiUP > Test procedures | Stress Test TiDB Using TiUP Bench Component > Run YCSB test using TiUP | Stress Test TiDB Using TiUP Bench Component > Run YCSB test using TiUP > Stress test TiDB | Stress Test TiDB Using TiUP Bench Component > Run YCSB test using TiUP > Stress test TiKV | Stress Test TiDB Using TiUP Bench Component > Run RawSQL test using TiUP`
- Source Line Ranges: `5-234`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `lightning`
- Topic Tags: `benchmarking`, `stress-testing`, `tpcc`, `tpch`, `ycsb`, `rawsql`, `workloads`, `command-flags`, `data-preparation`, `consistency-check`, `cleanup`, `csv-export`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0276_da7c863030`
- Source ID: `tidb-docs-8.1:tiup/tiup-bench.md#stress-test-tidb-using-tiup-bench-component`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `748c7de3f7d4c43e7ea0108e33a503275d51b611b23b0c77abfc1ef0553890f3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-bench#stress-test-tidb-using-tiup-bench-component
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-bench.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiUP bench workload commands, shared flags, and example procedures for running TPC-C, TPC-H, YCSB, or RawSQL stress tests.
- Retrieval Keywords: tiup bench tpcc, tiup bench tpch, tiup bench ch, tiup bench ycsb, tiup bench rawsql, prepare run check cleanup, --warehouses, --parts, --partition-type, --sf, --queries, --check=true, --count, --time, --host, --port, --conn-params, client-side load balancing, tidb_isolation_read_engines='tiflash', sslmode=disable, --ap-host, --ap-port, --ap-conn-params, output-dir data, output-type=csv, --tables history,orders, TiDB Lightning, ycsb load tidb, ycsb run tidb, ycsb load tikv, ycsb run tikv, tidb.instances, tikv.pd, operationcount, recordcount, rawsql run --query-files demo.sql
- Follow-up Guidance: The source also points to the YCSB usage guide for .properties-based configuration and to detailed TPC-C and TiDB Lightning documentation.
- Classification Note: This is classified as performance for the self-managed TiUP component because the content describes stress testing and benchmarking workflows, workload commands, and execution flags for TiDB, TiKV, PD, TiFlash, and Lightning.

## Official Source Content

# Stress Test TiDB Using TiUP Bench Component

When you test the performance of a database, it is often required to stress test the database. To facilitate this, TiUP has integrated the bench component, which provides multiple workloads for stress testing. You can access these workloads by the following commands:

```bash
tiup bench tpcc   # Benchmark a database using TPC-C
tiup bench tpch   # Benchmark a database using TPC-H
tiup bench ch     # Benchmark a database using CH-benCHmark
tiup bench ycsb   # Benchmark a database using YCSB
tiup bench rawsql # Benchmark a database using arbitrary SQL files
```

`tpcc`, `tpch`, `ch`, and `rawsql` share the following common command flags. However, `ycsb` is mainly configured by a `.properties` file, which is described in its [usage guide](https://github.com/pingcap/go-ycsb#usage).

```
  -t, --acThreads int         OLAP client concurrency, only for CH-benCHmark (default to 1)
      --conn-params string    Session variables, such as setting `--conn-params tidb_isolation_read_engines='tiflash'` for TiDB queries and setting `--conn-params sslmode=disable` for PostgreSQL connections
      --count int             Total execution count (0 means infinite count)
  -D, --db string             Database name (default to "test")
  -d, --driver string         Database driver: mysql, postgres (default to "mysql")
      --dropdata              Clean up historical data before preparing
  -H, --host strings          Database host (default to [127.0.0.1])
      --ignore-error          Ignore errors when running workload
      --interval duration     Output interval time (default to 10s)
      --isolation int         Isolation Level (0: Default; 1: ReadUncommitted;
                              2: ReadCommitted; 3: WriteCommitted; 4: RepeatableRead;
                              5: Snapshot; 6: Serializable; 7: Linerizable)
      --max-procs int         runtime.GOMAXPROCS of golang, the limits of how many cores can be used
      --output string         Output style. Valid values can be { plain | table | json } (default to "plain")
  -p, --password string       Database password
  -P, --port ints             Database port (default to [4000])
      --pprof string          Address of pprof endpoint
      --silence               Don't print errors when running workload
  -S, --statusPort int        Database status port (default to 10080)
  -T, --threads int           Thread concurrency (default to 1)
      --time duration         Total execution time (default to 2562047h47m16.854775807s)
  -U, --user string           Database user (default to "root")
```

- You can pass comma-separated values to `--host` and `--port` to enable client-side load balancing. For example, when you specify `--host 172.16.4.1,172.16.4.2 --port 4000,4001`, the program will connect to 172.16.4.1:4000, 172.16.4.1:4001, 172.16.4.2:4000, and 172.16.4.2:4001, chosen in round-robin fashion.
- For a local deployment, the default database host address is `127.0.0.1`. If you are connecting to a remote database, you need to specify the host and other relevant parameters. For example: `tiup bench tpcc -H 192.168.169.31 -P 4000 -D tpcc -U root -p tidb --warehouses 4 --parts 4 prepare`
- `--conn-params` must follow the format of [query string](https://en.wikipedia.org/wiki/Query_string). Different databases might have different parameters. For example:
    - `--conn-params tidb_isolation_read_engines='tiflash'` forces TiDB to read from TiFlash.
    - `--conn-params sslmode=disable` disables SSL when you connect to PostgreSQL.
- When running CH-benCHmark, you can use `--ap-host`, `--ap-port`, and `--ap-conn-params` to specify a standalone TiDB server for OLAP queries.

The following sections describe how to run TPC-C, TPC-H, YCSB tests using TiUP.
## Run TPC-C test using TiUP

The TiUP bench component supports the following commands and flags to run the TPC-C test:

```bash
Available Commands:
  check       Check data consistency for the workload
  cleanup     Cleanup data for the workload
  prepare     Prepare data for the workload
  run         Run workload

Flags:
      --check-all            Run all consistency checks
  -h, --help                 Help for TPC-C
      --partition-type int   Partition type: 1 - HASH, 2 - RANGE, 3 - LIST (HASH-like), 4 - LIST (RANGE-like) (default to 1)
      --parts int            Number of partitions (default to 1)
      --warehouses int       Number of warehouses (default to 10)

```
### Test procedures

The following provides simplified steps for running a TPC-C test. For detailed steps, see [How to Run TPC-C Test on TiDB](https://docs.pingcap.com/tidb/stable/benchmark/benchmark-tidb-using-tpcc).

1. Create 4 warehouses using 4 partitions via hash:

    ```shell
    tiup bench tpcc --warehouses 4 --parts 4 prepare
    ```

2. Run the TPC-C test:

    ```shell
    tiup bench tpcc --warehouses 4 --time 10m run
    ```

3. Check the consistency:

    ```shell
    tiup bench tpcc --warehouses 4 check
    ```

4. Clean up data:

    ```shell
    tiup bench tpcc --warehouses 4 cleanup
    ```

Preparing data via SQL might be slow when you want to run a benchmark with a large data set. In that case, you can generate data in the CSV format by the following commands and then import it to TiDB via [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview).

- Generate the CSV file:

    ```shell
    tiup bench tpcc --warehouses 4 prepare --output-dir data --output-type=csv
    ```

- Generate the CSV file for the specified table:

    ```shell
    tiup bench tpcc --warehouses 4 prepare --output-dir data --output-type=csv --tables history,orders
    ```
## Run TPC-H test using TiUP

The TiUP bench component supports the following commands and parameters to run the TPC-H test:

```bash
Available Commands:
  cleanup     Cleanup data for the workload
  prepare     Prepare data for the workload
  run         Run workload

Flags:
      --check            Check output data, only when the scale factor equals 1
  -h, --help             help for tpch
      --queries string   All queries (default "q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,q11,q12,q13,q14,q15,q16,q17,q18,q19,q20,q21,q22")
      --sf int           scale factor
```
### Test procedures

1. Prepare data:

    ```shell
    tiup bench tpch --sf=1 prepare
    ```

2. Run the TPC-H test by executing one of the following commands:

    - If you check the result, run this command:

        ```shell
        tiup bench tpch --count=22 --sf=1 --check=true run
        ```

    - If you do not check the result, run this command:

        ```shell
        tiup bench tpch --count=22 --sf=1 run
        ```

3. Clean up data:

    ```shell
    tiup bench tpch cleanup
    ```
## Run YCSB test using TiUP

You can stress test both TiDB and TiKV via YCSB.
### Stress test TiDB

1. Prepare data:

    ```shell
    tiup bench ycsb load tidb -p tidb.instances="127.0.0.1:4000" -p recordcount=10000
    ```

2. Run the YCSB workload:

    ```shell
    # The read-write percent is 95% by default
    tiup bench ycsb run tidb -p tidb.instances="127.0.0.1:4000" -p operationcount=10000
    ```
### Stress test TiKV

1. Prepare data:

    ```shell
    tiup bench ycsb load tikv -p tikv.pd="127.0.0.1:2379" -p recordcount=10000
    ```

2. Run the YCSB workload:

    ```shell
    # The read-write percent is 95% by default
    tiup bench ycsb run tikv -p tikv.pd="127.0.0.1:2379" -p operationcount=10000
    ```
## Run RawSQL test using TiUP

You can write an arbitrary query in a SQL file, and then use it for the test by executing `tiup bench rawsql` as follows:

1. Prepare data and the query:

    ```sql
    -- Prepare data
    CREATE TABLE t (a int);
    INSERT INTO t VALUES (1), (2), (3);

    -- Save your query in a SQL file. For example, you can save the following query in `demo.sql`.
    SELECT a, sleep(rand()) FROM t WHERE a < 4*rand();
    ```

2. Run the RawSQL test:

    ```shell
    tiup bench rawsql run --count 60 --query-files demo.sql
    ```
