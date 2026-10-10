# Improvements across TiDB, TiKV, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.1.1.md`
- Source Title: `TiDB 5.1.1 Release Notes`
- Source Heading Path: `TiDB 5.1.1 Release Notes > Improvements`
- Source Line Ranges: `37-79`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `ticdc`, `lightning`, `dumpling`, `pd`, `tiflash`
- Topic Tags: `release-notes`, `improvements`, `stale-read`, `mpp`, `pushdown`, `latency`, `idempotency`, `load-balance`, `import`, `cdc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0226_43dba99d2c`
- Source ID: `tidb-docs-8.1:releases/release-5.1.1.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8e145a71e2237cca9ed9cb914fd56fe29baa5e67eae2b70ee3d5487a9795d984`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.1.1#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.1.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.1.1 improvements across TiDB, TiKV, TiCDC, TiDB Lightning, and Dumpling, including Stale Read, MPP, pushdown, latency, idempotency, and tool behavior changes.
- Retrieval Keywords: TiDB 5.1.1 Release Notes, Improvements, Stale Read GA, paramMarker, stable result mode, json_unquote(), push down to TiKV, retrying MPP queries, point get, batch point get, UPDATE reads, LOCK record, PUT record, stale queries, COUNT(DISTINCT), MPP mode, TiFlash availability, read timestamp future time, EXPLAIN statements, aggregation functions cannot be pushed down, statements_summary_evicted, str_to_date, %b, %M, %r, %T, prewrite requests idempotent, undetermined errors, expired commands, stack overflow, start_ts, max_ts, read ready and write ready separately, read latency, I/O rate limiting, data import speed, Raft gRPC connections, TiCDC, file sorter, PD endpoint misses the certificate, TiDB Lightning, retry mechanism for restoring schemas, Dumpling, _tidb_rowid, TiDB v3.x cluster, database metadata
- Follow-up Guidance: The source also lists tool-specific improvements, including removing TiCDC file sorter, adding a retry mechanism for restoring schemas in TiDB Lightning, and reducing metadata access frequency in Dumpling.
- Classification Note: This is a release-notes chunk summarizing improvements in TiDB 5.1.1 across the TiDB server, TiKV, and related tools.

## Official Source Content

## Improvements

+ TiDB

    - Announce the general availability (GA) of the Stale Read feature
    - Avoid allocation for `paramMarker` to speed up data insertion [#26076](https://github.com/pingcap/tidb/pull/26076)
    - Support the stable result mode to make the query results more stable [#25995](https://github.com/pingcap/tidb/pull/25995)
    - Support pushing down the built-in function `json_unquote()` to TiKV [#26265](https://github.com/pingcap/tidb/pull/26265)
    - Support retrying MPP queries [#26480](https://github.com/pingcap/tidb/pull/26480)
    - Change the `LOCK` record into the `PUT` record for the index keys using `point get` or `batch point get` for `UPDATE` reads [#26225](https://github.com/pingcap/tidb/pull/26225)
    - Forbid creating views from stale queries [#26200](https://github.com/pingcap/tidb/pull/26200)
    - Thoroughly push down the `COUNT(DISTINCT)` aggregation function in the MPP mode [#26194](https://github.com/pingcap/tidb/pull/26194)
    - Check the availability of TiFlash before launching MPP queries [#26192](https://github.com/pingcap/tidb/pull/26192)
    - Do not allow setting the read timestamp to a future time [#25763](https://github.com/pingcap/tidb/pull/25763)
    - Print log warnings when aggregation functions cannot be pushed down in `EXPLAIN` statements [#25737](https://github.com/pingcap/tidb/pull/25737)
    - Add the `statements_summary_evicted` table to record the evicted count information of a cluster [#25587](https://github.com/pingcap/tidb/pull/25587)
    - Improve the MySQL compatibility of the built-in function `str_to_date` for the format specifiers `%b/%M/%r/%T` [#25768](https://github.com/pingcap/tidb/pull/25768)

+ TiKV

    - Make the prewrite requests as idempotent as possible to reduce the chance of undetermined errors [#10586](https://github.com/tikv/tikv/pull/10586)
    - Prevent the risk of stack overflow when handling many expired commands [#10502](https://github.com/tikv/tikv/pull/10502)
    - Avoid excessive commit request retrying by not using the Stale Read request's `start_ts` to update `max_ts` [#10451](https://github.com/tikv/tikv/pull/10451)
    - Handle read ready and write ready separately to reduce read latency [#10592](https://github.com/tikv/tikv/pull/10592)
    - Reduce the impact on data import speed when the I/O rate limiting is enabled [#10390](https://github.com/tikv/tikv/pull/10390)
    - Improve the load balance between Raft gRPC connections [#10495](https://github.com/tikv/tikv/pull/10495)

+ Tools

    + TiCDC

        - Remove `file sorter` [#2327](https://github.com/pingcap/tiflow/pull/2327)
        - Improve the error message returned when a PD endpoint misses the certificate [#1973](https://github.com/pingcap/tiflow/issues/1973)

    + TiDB Lightning

        - Add a retry mechanism for restoring schemas [#1294](https://github.com/pingcap/br/pull/1294)

    + Dumpling

        - Always split tables using `_tidb_rowid` when the upstream is a TiDB v3.x cluster, which helps reduce TiDB's memory usage [#295](https://github.com/pingcap/dumpling/issues/295)
        - Reduce the frequency of accessing the database metadata to improve Dumpling's performance and stability [#315](https://github.com/pingcap/dumpling/pull/315)
