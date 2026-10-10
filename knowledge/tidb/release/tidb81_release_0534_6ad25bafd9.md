# TiDB 7.5.2 bug fixes for SQL execution, statistics, DDL, and related behavior

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.2.md`
- Source Title: `TiDB 7.5.2 Release Notes`
- Source Heading Path: `TiDB 7.5.2 Release Notes > Bug fixes`
- Source Line Ranges: `118-151`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `shared`
- Topic Tags: `bug-fixes`, `sql-execution`, `query-results`, `statistics`, `ddl`, `indexes`, `mpp`, `ttl`, `configuration`, `metrics`, `collation`, `partitioning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0534_6ad25bafd9`
- Source ID: `tidb-docs-8.1:releases/release-7.5.2.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8112057ca5baabb93c7f477c279583ba0b028500aa45eccf6b489d17581cb2db`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.2#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.5.2 bug fixes affecting SQL execution, query correctness, statistics loading, DDL, indexes, MPP, TTL, configuration handling, metrics, collations, or partition behavior.
- Retrieval Keywords: TiDB 7.5.2 bug fixes, default value dropped column returns error, force-init-stats port not listen, IN() predicate contains NULL incorrect result, fail to get stats version for this histogram, EXCHANGE PARTITION foreign keys, LIMIT pushdown OR type Index Merge, TopN correlated subqueries incorrect result, CPS by type metric incorrect values, EXPLAIN incorrect column IDs statistics not fully loaded, different collations query panic new framework for collations disabled, Can't find a proper physical plan for this query, system variable type conversion in expression, INSERT IGNORE unique index data inconsistency, automatic statistics collection stuck after OOM, tidb_mem_quota_analyze statistics exceeds the limit crash, max_execute_time settings at multiple levels interfere, adding multiple indexes using a single SQL statement index inconsistency, Window function related subquery panic, shuffleExec quits unexpectedly crash, rolling back the partition DDL tasks gets stuck, JSON of BINARY type error, Distributed eXecution Framework DXF adding indexes to large tables fails, TTL feature data hotspots incorrect data range splitting, ALTER TABLE ... COMPACT TIFLASH REPLICA primary key type VARCHAR, cluster upgrade during adding indexes inconsistent data indexes, predicate pushdown in TableDual performance regression, HTTP interface add label returns success but does not take effect, adding indexes in the ingest mode inconsistent data index, init-stats process panic load stats process quit, invalid configuration item configuration file does not take effect, MPP incorrect query results JOIN SELECT list contains only constants, tidb_opt_objective='determinate' statistics might not be loaded, SHOW CREATE PLACEMENT POLICY SURVIVAL_PREFERENCES missing, IndexJoin duplicate rows Left Outer Anti Semi
- Follow-up Guidance: This chunk lists the specific fixed issues and exact identifiers, errors, statements, metrics, and configuration names addressed in TiDB 7.5.2.
- Classification Note: The official content is a release-note bug-fix summary for TiDB 7.5.2 covering TiDB behavior and related TiFlash and shared features in self-managed deployments.

## Official Source Content

- Fix the issue that getting the default value of a column returns an error if the column default value is dropped [#50043](https://github.com/pingcap/tidb/issues/50043) [#51324](https://github.com/pingcap/tidb/issues/51324) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that TiDB does not listen to the corresponding port when `force-init-stats` is configured [#51473](https://github.com/pingcap/tidb/issues/51473) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the query result is incorrect when the `IN()` predicate contains `NULL` [#51560](https://github.com/pingcap/tidb/issues/51560) @[winoros](https://github.com/winoros)
    - Fix the issue that the TiDB synchronously loading statistics mechanism retries to load empty statistics indefinitely and prints the `fail to get stats version for this histogram` log [#52657](https://github.com/pingcap/tidb/issues/52657) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that `EXCHANGE PARTITION` incorrectly processes foreign keys [#51807](https://github.com/pingcap/tidb/issues/51807) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that `LIMIT` might not be pushed down to the `OR` type `Index Merge` [#48588](https://github.com/pingcap/tidb/issues/48588) @[AilinKid](https://github.com/AilinKid)
    - Fix the incorrect result of the TopN operator in correlated subqueries [#52777](https://github.com/pingcap/tidb/issues/52777) @[yibin87](https://github.com/yibin87)
    - Fix the issue that the `CPS by type` metric displays incorrect values [#52605](https://github.com/pingcap/tidb/issues/52605) @[nolouch](https://github.com/nolouch)
    - Fix the issue that the `EXPLAIN` statement might display incorrect column IDs in the result when statistics for certain columns are not fully loaded [#52207](https://github.com/pingcap/tidb/issues/52207) @[time-and-fate](https://github.com/time-and-fate)
    - Fix the issue that expressions containing different collations might cause the query to panic when the new framework for collations is disabled [#52772](https://github.com/pingcap/tidb/issues/52772) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that executing SQL statements containing tables with multi-valued indexes might return the `Can't find a proper physical plan for this query` error [#49438](https://github.com/pingcap/tidb/issues/49438) @[qw4990](https://github.com/qw4990)
    - Fix the issue that TiDB cannot correctly convert the type of a system variable in an expression [#43527](https://github.com/pingcap/tidb/issues/43527) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that executing `INSERT IGNORE` might result in inconsistency between the unique index and the data [#51784](https://github.com/pingcap/tidb/issues/51784) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that automatic statistics collection gets stuck after an OOM error occurs [#51993](https://github.com/pingcap/tidb/issues/51993) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that TiDB might crash when `tidb_mem_quota_analyze` is enabled and the memory used by updating statistics exceeds the limit [#52601](https://github.com/pingcap/tidb/issues/52601) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that `max_execute_time` settings at multiple levels interfere with each other [#50914](https://github.com/pingcap/tidb/issues/50914) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue of index inconsistency caused by adding multiple indexes using a single SQL statement [#51746](https://github.com/pingcap/tidb/issues/51746) @[tangenta](https://github.com/tangenta)
    - Fix the issue that the Window function might panic when there is a related subquery in it [#42734](https://github.com/pingcap/tidb/issues/42734) @[hi-rustin](https://github.com/Rustin170506)
    - Fix the issue that TiDB crashes when `shuffleExec` quits unexpectedly [#48230](https://github.com/pingcap/tidb/issues/48230) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that the status gets stuck when rolling back the partition DDL tasks [#51090](https://github.com/pingcap/tidb/issues/51090) @[jiyfhust](https://github.com/jiyfhust)
    - Fix the issue that querying JSON of `BINARY` type might cause an error in some cases [#51547](https://github.com/pingcap/tidb/issues/51547) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that adding indexes to large tables fails after enabling the Distributed eXecution Framework (DXF) [#52640](https://github.com/pingcap/tidb/issues/52640) @[tangenta](https://github.com/tangenta)
    - Fix the issue that the TTL feature causes data hotspots due to incorrect data range splitting in some cases [#51527](https://github.com/pingcap/tidb/issues/51527) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that `ALTER TABLE ... COMPACT TIFLASH REPLICA` might incorrectly end when the primary key type is `VARCHAR` [#51810](https://github.com/pingcap/tidb/issues/51810) @[breezewish](https://github.com/breezewish)
    - Fix the issue of inconsistent data indexes caused by cluster upgrade during adding indexes [#52411](https://github.com/pingcap/tidb/issues/52411) @[tangenta](https://github.com/tangenta)
    - Fix the performance regression issue caused by disabling predicate pushdown in TableDual [#50614](https://github.com/pingcap/tidb/issues/50614) @[time-and-fate](https://github.com/time-and-fate)
    - Fix the issue that the TiDB server adds a label via the HTTP interface and returns success, but does not take effect [#51427](https://github.com/pingcap/tidb/issues/51427) @[you06](https://github.com/you06)
    - Fix the issue that adding indexes in the ingest mode might cause inconsistent data index in some corner cases [#51954](https://github.com/pingcap/tidb/issues/51954) @[lance6716](https://github.com/lance6716)
    - Fix the issue that the `init-stats` process might cause TiDB to panic and the `load stats` process to quit [#51581](https://github.com/pingcap/tidb/issues/51581) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the configuration file does not take effect when it contains an invalid configuration item [#51399](https://github.com/pingcap/tidb/issues/51399) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that query execution using MPP might lead to incorrect query results when a SQL statement contains `JOIN` and the `SELECT` list in the statement contains only constants [#50358](https://github.com/pingcap/tidb/issues/50358) @[yibin87](https://github.com/yibin87)
    - Fix the issue that in `determinate` mode (`tidb_opt_objective='determinate'`), if a query does not contain predicates, statistics might not be loaded [#48257](https://github.com/pingcap/tidb/issues/48257) @[time-and-fate](https://github.com/time-and-fate)
    - Fix the issue that the `SURVIVAL_PREFERENCES` attribute might not appear in the output of the `SHOW CREATE PLACEMENT POLICY` statement under certain conditions [#51699](https://github.com/pingcap/tidb/issues/51699) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that IndexJoin produces duplicate rows when calculating hash values in the Left Outer Anti Semi type [#52902](https://github.com/pingcap/tidb/issues/52902) @[yibin87](https://github.com/yibin87)
