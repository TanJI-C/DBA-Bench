# Bug fixes across TiDB SQL, DDL, import, TTL, and stability

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.6.md`
- Source Title: `TiDB 7.1.6 Release Notes`
- Source Heading Path: `TiDB 7.1.6 Release Notes > Bug fixes`
- Source Line Ranges: `143-177`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `sql`, `dm`, `pd`, `tikv`
- Topic Tags: `bug-fixes`, `sql-execution`, `statistics`, `plan-cache`, `ddl`, `add-index`, `import-into`, `load-data`, `ttl`, `stale-read`, `memory-tracking`, `panic`, `data-consistency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0483_4b40c5a3f2`
- Source ID: `tidb-docs-8.1:releases/release-7.1.6.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4affaeee74ae0e95ea52be0d316b7b6f1183d32bf677d46f016f99cbd2487d80`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.6#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.6.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 7.1.6 bug-fix notes for SQL execution correctness, DDL and ADD INDEX failures, IMPORT INTO or LOAD DATA consistency issues, TTL task problems, stale read consistency, plan cache, memory tracking, or TiDB panic and stability fixes.
- Retrieval Keywords: TiDB 7.1.6 bug fixes, Distinct_count GlobalStats incorrect, SELECT DISTINCT CAST(col AS DECIMAL) CAST(col AS SIGNED) incorrect results, read_from_storage hint Index Merge, TIMESTAMPADD incorrect results, PREPARE EXECUTE CONV ? incorrect query results, memory used by transactions tracked multiple times, column pruning panic, SQL binding window functions not take effect, parsing index data panic, GC when loading statistics at startup, DML nested generated columns error, SHOW ERRORS predicate always true panic, metadata locks plan cache anomalous data, data index inconsistency retries during index addition, unstable unique IDs of columns UPDATE errors, Trying to start aggressive locking while it's already started, RECOVER TABLE BY JOB JOB_ID panic, ADD INDEX fail after modifying PD member, two DDL Owners at the same time, rolling restart ADD INDEX fail, LOAD DATA REPLACE INTO data inconsistency, AUTO_INCREMENT after IMPORT INTO, restoring from a checkpoint local files existence, DM schema tracker indexes longer than the default length, ALTER TABLE AUTO_INCREMENT field correctly, unreleased session resources memory leaks, float or integer overflow affects the plan cache, IndexLookUp operator memory not tracked, stale read timestamp consistency TSO real physical time, TTL might fail if TiKV is not selected as the storage engine, TTL tasks cannot be canceled write conflict, ERROR 1264 22003 oversized numbers in scientific notation, canceling a TTL task SQL is not killed forcibly, INSERT ON DUPLICATE KEY mysql_insert_id, audit log filtering does not take effect when SQL cannot build an execution plan
- Follow-up Guidance: The release note lists issue-specific fixes across TiDB SQL, DDL, import, TTL, stale read, DM schema tracker, memory tracking, and audit log filtering in TiDB 7.1.6.
- Classification Note: This chunk is classified as a release note because the official content is a consolidated list of bug fixes included in TiDB 7.1.6.

## Official Source Content

- Fix the issue that the `Distinct_count` information in GlobalStats might be incorrect [#53752](https://github.com/pingcap/tidb/issues/53752) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that executing the `SELECT DISTINCT CAST(col AS DECIMAL), CAST(col AS SIGNED) FROM ...` query might return incorrect results [#53726](https://github.com/pingcap/tidb/issues/53726) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that the `read_from_storage` hint might not take effect when the query has an available Index Merge execution plan [#56217](https://github.com/pingcap/tidb/issues/56217) @[AilinKid](https://github.com/AilinKid)
    - Fix the issue that the `TIMESTAMPADD()` function returns incorrect results [#41052](https://github.com/pingcap/tidb/issues/41052) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue that `PREPARE`/`EXECUTE` statements with the `CONV` expression containing a `?` argument might result in incorrect query results when executed multiple times [#53505](https://github.com/pingcap/tidb/issues/53505) @[qw4990](https://github.com/qw4990)
    - Fix the issue that the memory used by transactions might be tracked multiple times [#53984](https://github.com/pingcap/tidb/issues/53984) @[ekexium](https://github.com/ekexium)
    - Fix the issue that column pruning without using shallow copies of slices might cause TiDB to panic [#52768](https://github.com/pingcap/tidb/issues/52768) @[winoros](https://github.com/winoros)
    - Fix the issue that a SQL binding containing window functions might not take effect in some cases [#55981](https://github.com/pingcap/tidb/issues/55981) @[winoros](https://github.com/winoros)
    - Fix the issue that TiDB might panic when parsing index data [#47115](https://github.com/pingcap/tidb/issues/47115) @[zyguan](https://github.com/zyguan)
    - Fix the issue that TiDB might report an error due to GC when loading statistics at startup [#53592](https://github.com/pingcap/tidb/issues/53592) @[you06](https://github.com/you06)
    - Fix the issue that an error occurs when a DML statement contains nested generated columns [#53967](https://github.com/pingcap/tidb/issues/53967) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that TiDB panics when executing the `SHOW ERRORS` statement with a predicate that is always `true` [#46962](https://github.com/pingcap/tidb/issues/46962) @[elsa0520](https://github.com/elsa0520)
    - Fix the issue that improper use of metadata locks might lead to writing anomalous data when using the plan cache under certain circumstances [#53634](https://github.com/pingcap/tidb/issues/53634) @[zimulala](https://github.com/zimulala)
    - Fix the issue of data index inconsistency caused by retries during index addition [#55808](https://github.com/pingcap/tidb/issues/55808) @[lance6716](https://github.com/lance6716)
    - Fix the issue that unstable unique IDs of columns might cause the `UPDATE` statement to return errors [#53236](https://github.com/pingcap/tidb/issues/53236) @[winoros](https://github.com/winoros)
    - Fix the issue that after a statement within a transaction is killed by OOM, if TiDB continues to execute the next statement within the same transaction, you might get an error `Trying to start aggressive locking while it's already started` and a panic occurs [#53540](https://github.com/pingcap/tidb/issues/53540) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that executing `RECOVER TABLE BY JOB JOB_ID;` might cause TiDB to panic [#55113](https://github.com/pingcap/tidb/issues/55113) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that executing `ADD INDEX` might fail after modifying the PD member in the distributed execution framework [#48680](https://github.com/pingcap/tidb/issues/48680) @[lance6716](https://github.com/lance6716)
    - Fix the issue that two DDL Owners might exist at the same time [#54689](https://github.com/pingcap/tidb/issues/54689) @[joccau](https://github.com/joccau)
    - Fix the issue that TiDB rolling restart during the execution of `ADD INDEX` might cause the adding index operation to fail [#52805](https://github.com/pingcap/tidb/issues/52805) @[tangenta](https://github.com/tangenta)
    - Fix the issue that the `LOAD DATA ... REPLACE INTO` operation causes data inconsistency [#56408](https://github.com/pingcap/tidb/issues/56408) @[fzzf678](https://github.com/fzzf678)
    - Fix the issue that the `AUTO_INCREMENT` field is not correctly set after importing data using the `IMPORT INTO` statement [#56476](https://github.com/pingcap/tidb/issues/56476) @[D3Hunter](https://github.com/D3Hunter)
    - Fix the issue that TiDB does not check for the existence of local files before restoring from a checkpoint [#53009](https://github.com/pingcap/tidb/issues/53009) @[lance6716](https://github.com/lance6716)
    - Fix the issue that the DM schema tracker cannot create indexes longer than the default length [#55138](https://github.com/pingcap/tidb/issues/55138) @[lance6716](https://github.com/lance6716)
    - Fix the issue that `ALTER TABLE` does not handle the `AUTO_INCREMENT` field correctly [#47899](https://github.com/pingcap/tidb/issues/47899) @[D3Hunter](https://github.com/D3Hunter)
    - Fix the issue that unreleased session resources might lead to memory leaks [#56271](https://github.com/pingcap/tidb/issues/56271) @[lance6716](https://github.com/lance6716)
    - Fix the issue that float or integer overflow affects the plan cache [#46538](https://github.com/pingcap/tidb/issues/46538) @[hawkingrei](https://github.com/hawkingrei)
    - Fix the issue that part of the memory of the `IndexLookUp` operator is not tracked [#56440](https://github.com/pingcap/tidb/issues/56440) @[wshwsh12](https://github.com/wshwsh12)
    - Fix the issue that stale read does not strictly verify the timestamp of the read operation, resulting in a small probability of affecting the consistency of the transaction when an offset exists between the TSO and the real physical time [#56809](https://github.com/pingcap/tidb/issues/56809) @[MyonKeminta](https://github.com/MyonKeminta)
    - Fix the issue that TTL might fail if TiKV is not selected as the storage engine [#56402](https://github.com/pingcap/tidb/issues/56402) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that TTL tasks cannot be canceled when there is a write conflict [#56422](https://github.com/pingcap/tidb/issues/56422) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that inserting oversized numbers in scientific notation causes an error `ERROR 1264 (22003)`, to make the behavior consistent with MySQL [#47787](https://github.com/pingcap/tidb/issues/47787) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that when canceling a TTL task, the corresponding SQL is not killed forcibly [#56511](https://github.com/pingcap/tidb/issues/56511) @[lcwangchao](https://github.com/lcwangchao)
    - Fix the issue that the `INSERT ... ON DUPLICATE KEY` statement is not compatible with `mysql_insert_id` [#55965](https://github.com/pingcap/tidb/issues/55965) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that audit log filtering does not take effect when SQL cannot build an execution plan [#50988](https://github.com/pingcap/tidb/issues/50988) @[CbcWestwolf](https://github.com/CbcWestwolf)
