# Bug fixes for TiDB, TiKV, PD, and Dashboard section start

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.9.md`
- Source Title: `TiDB 4.0.9 Release Notes`
- Source Heading Path: `TiDB 4.0.9 Release Notes > Bug Fixes`
- Source Line Ranges: `122-184`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `dashboard`
- Topic Tags: `bug-fixes`, `sql-correctness`, `transactions`, `partitions`, `locks`, `replication`, `data-loss-warning`, `coprocessor`, `placement-rules`, `dashboard-ui`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0195_0c6f7c77b8`
- Source ID: `tidb-docs-8.1:releases/release-4.0.9.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `443279f7f778b5843ac89a28c713363747df5be6472dd8d2bb60609e43a9c145`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.9#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.9.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 4.0.9 bug fixes across TiDB, TiKV, and PD involving wrong query results, partition and collation behavior, transaction and lock issues, Coprocessor errors, Region Merge data loss during network partition, or placement rules and service safepoint fixes.
- Retrieval Keywords: TiDB 4.0.9 Bug Fixes, prefix index OR condition incorrect results, automatic retry panic, partition definition column type, hash partition partition name unique, BigInt unsigned CASE WHEN converted to signed, index hash join collation, index merge join collation, slow_query miss some rows, DELETE not delete correctly database name not pure lower, table lock UPDATE statement, EXPLAIN FOR CONNECTION cannot show last query plan, Index Merge Read Committed incorrect result, LOAD DATA JSON data cannot be correctly imported, PointGet wrong results, snapshot reads hits the lock cache, Coprocessor wrong results more than 255 columns, Region Merge data loss network partition, ANALYZE latin1 panic, advertise-status-addr 0.0.0.0, Follower Read stale data after leader transfer, replica read stale data after leader transfer, placement rules leader roles do not take effect, trace-region-flow unexpectedly set to false, service safepoint infinite TTL does not work
- Follow-up Guidance: The following chunk continues the same Bug Fixes section with TiDB Dashboard, TiFlash, BR, TiCDC, Dumpling, and TiDB Lightning fixes.
- Classification Note: This is a release-notes bug-fix chunk covering multiple self-managed components under the TiDB 4.0.9 Bug Fixes heading.

## Official Source Content

## Bug Fixes

+ TiDB

    - Fix the issue of incorrect results when using a prefix index with the `OR` condition [#21287](https://github.com/pingcap/tidb/pull/21287)
    - Fix a bug that might cause panic when automatic retry is enabled [#21285](https://github.com/pingcap/tidb/pull/21285)
    - Fix a bug that occurs when checking partition definition according to column type [#21273](https://github.com/pingcap/tidb/pull/21273)
    - Fix a bug that the value type of the partition expression is not consistent with the partition column type [#21136](https://github.com/pingcap/tidb/pull/21136)
    - Fix a bug that the hash-type partition does not check whether the partition name is unique [#21257](https://github.com/pingcap/tidb/pull/21257)
    - Fix the wrong results returned after inserting a value of the non-`INT` type into the hash partitioned table [#21238](https://github.com/pingcap/tidb/pull/21238)
    - Fix the unexpected error when using index join in the `INSERT` statement in some cases [#21249](https://github.com/pingcap/tidb/pull/21249)
    - Fix the issue that the `BigInt` unsigned column value in the `CASE WHEN` operator is incorrectly converted to the `BigInt` signed value [#21236](https://github.com/pingcap/tidb/pull/21236)
    - Fix a bug that index hash join and index merge join do not consider collation [#21219](https://github.com/pingcap/tidb/pull/21219)
    - Fix a bug that the partitioned table does not consider collation in the `CREATE TABLE` and `SELECT` syntax [#21181](https://github.com/pingcap/tidb/pull/21181)
    - Fix the issue that the query result of `slow_query` might miss some rows [#21211](https://github.com/pingcap/tidb/pull/21211)
    - Fix the issue that `DELETE` might not delete data correctly when the database name is not in a pure lower representation [#21206](https://github.com/pingcap/tidb/pull/21206)
    - Fix a bug that causes schema change after DML operations [#21050](https://github.com/pingcap/tidb/pull/21050)
    - Fix the bug that the coalesced column cannot be queried when using join [#21021](https://github.com/pingcap/tidb/pull/21021)
    - Fix the wrong results of some semi-join queries [#21019](https://github.com/pingcap/tidb/pull/21019)
    - Fix the issue that the table lock does not take effect on the `UPDATE` statement [#21002](https://github.com/pingcap/tidb/pull/21002)
    - Fix the issue of stack overflow that occurs when building the recursive view [#21001](https://github.com/pingcap/tidb/pull/21001)
    - Fix the unexpected result returned when performing index merge join operations on outer join [#20954](https://github.com/pingcap/tidb/pull/20954)
    - Fix the issue that sometimes a transaction that has an undetermined result might be treated as failed [#20925](https://github.com/pingcap/tidb/pull/20925)
    - Fix the issue that `EXPLAIN FOR CONNECTION` cannot show the last query plan [#21315](https://github.com/pingcap/tidb/pull/21315)
    - Fix the issue that when Index Merge is used in a transaction with the Read Committed isolation level, the result might be incorrect [#21253](https://github.com/pingcap/tidb/pull/21253)
    - Fix the auto-ID allocation failure caused by the transaction retry after the write conflict [#21079](https://github.com/pingcap/tidb/pull/21079)
    - Fix the issue that JSON data cannot be correctly imported to TiDB using `LOAD DATA` [#21074](https://github.com/pingcap/tidb/pull/21074)
    - Fix the issue that the default value of newly added `Enum`-type columns is incorrect [#20998](https://github.com/pingcap/tidb/pull/20998)
    - Fix the issue that the `adddate` function inserts invalid characters [#21176](https://github.com/pingcap/tidb/pull/21176)
    - Fix the issue that the wrong `PointGet` plan generated in some situations causes wrong results [#21244](https://github.com/pingcap/tidb/pull/21244)
    - Ignore the conversion of daylight saving time in the `ADD_DATE` function to be compatible with MySQL [#20888](https://github.com/pingcap/tidb/pull/20888)
    - Fix a bug that prevents inserting strings with trailing spaces that exceed `varchar` or `char`'s length constraint [#21282](https://github.com/pingcap/tidb/pull/21282)
    - Fix a bug that does not converting the integer from `[1, 69]` to `[2001, 2069]` or from `[70, 99]` to `[1970, 1999]` when comparing `int` with `year` [#21283](https://github.com/pingcap/tidb/pull/21283)
    - Fix the panic caused by the overflowing result of the `sum()` function when calculating the `Double` type field [#21272](https://github.com/pingcap/tidb/pull/21272)
    - Fix a bug that `DELETE` fails to add lock on the unique key [#20705](https://github.com/pingcap/tidb/pull/20705)
    - Fix a bug that snapshot reads hits the lock cache [#21539](https://github.com/pingcap/tidb/pull/21539)
    - Fix an issue of potential memory leak after reading a lot of data in a long-lived transaction [#21129](https://github.com/pingcap/tidb/pull/21129)
    - Fix the issue that omitting the table alias in a subquery will have a syntax error returned [#20367](https://github.com/pingcap/tidb/pull/20367)
    - Fix the issue that when the argument of the `IN` function in a query is the time type, the query might return an incorrect result [#21290](https://github.com/pingcap/tidb/issues/21290)

+ TiKV

    - Fix the issue that Coprocessor might return wrong results when there are more than 255 columns [#9131](https://github.com/tikv/tikv/pull/9131)
    - Fix the issue that Region Merge might cause data loss during network partition [#9108](https://github.com/tikv/tikv/pull/9108)
    - Fix the issue that the `ANALYZE` statement might cause panic when using the `latin1` character set [#9082](https://github.com/tikv/tikv/pull/9082)
    - Fix the wrong results returned when converting the numeric type to the time type [#9031](https://github.com/tikv/tikv/pull/9031)
    - Fix a bug that TiDB Lightning fails to ingest SST files to TiKV with the Importer-backend or Local-backend when Transparent Data Encryption (TDE) is enabled [#8995](https://github.com/tikv/tikv/pull/8995)
    - Fix the invalid `advertise-status-addr` value (`0.0.0.0`) [#9036](https://github.com/tikv/tikv/pull/9036)
    - Fix the issue that an error is returned indicating that a key exists when this key is locked and deleted in a committed transaction [#8930](https://github.com/tikv/tikv/pull/8930)
    - Fix the issue that the RocksDB cache mapping error causes data corruption [#9029](https://github.com/tikv/tikv/pull/9029)
    - Fix a bug that Follower Read might return stale data after the leader is transferred [#9240](https://github.com/tikv/tikv/pull/9240)
    - Fix the issue that stale old values might be read in the pessimistic lock [#9282](https://github.com/tikv/tikv/pull/9282)
    - Fix a bug that replica read might get stale data after the leader transfer [#9240](https://github.com/tikv/tikv/pull/9240)
    - Fix the issue of TiKV crash that occurs when receiving `SIGPROF` after profiling [#9229](https://github.com/tikv/tikv/pull/9229)

+ PD

    - Fix the issue that the leader roles specified using placement rules do not take effect in some cases [#3208](https://github.com/pingcap/pd/pull/3208)
    - Fix the issue that the `trace-region-flow` value is unexpectedly set to `false` [#3120](https://github.com/pingcap/pd/pull/3120)
    - Fix a bug that the service safepoint with infinite Time To Live (TTL) does not work [#3143](https://github.com/pingcap/pd/pull/3143)

+ TiDB Dashboard
