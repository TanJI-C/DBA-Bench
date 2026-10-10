# Bug fixes for TiDB

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.0.0-dmr.md`
- Source Title: `TiDB 6.0.0 Release Notes`
- Source Heading Path: `TiDB 6.0.0 Release Notes > Bug fixes`
- Source Line Ranges: `662-712`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tiflash`
- Topic Tags: `release-notes`, `bug-fixes`, `sql`, `placement-rules`, `transactions`, `collation`, `partitioning`, `restore`, `tiflash`, `oom`, `timezone`, `cte`, `generated-columns`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0293_f861fc012e`
- Source ID: `tidb-docs-8.1:releases/release-6.0.0-dmr.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d771699efddb3f74fb3510a88e3cefde9e43511daf1156d38e7613e51812fb83`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.0.0-dmr#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.0.0-dmr.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 6.0.0 bug fixes for specific SQL errors, wrong results, panics, placement rule issues, partitioning problems, TiFlash-related fixes, restore distribution issues, OOM during ChunkRPC export, or corrected error messages.
- Retrieval Keywords: TiDB 6.0.0 Bug fixes, SCHEDULE = majority_in_primary, PrimaryRegion and Regions are of the same value, invalid transaction index lookup join, show grants incorrect results, INSERT INTO t1 SET timestamp_col = DEFAULT, CURRENT_TIMESTAMP zero timestamp, load data panic escape character, greatest least collation wrong result, date_add date_sub incorrect data types, virtually generated columns insert panic, duplicate columns created list partition, select for update union select incorrect snapshots, Regions unevenly distributed after a restore operation, COERCIBILITY json type, json builtin-func collation, PD rules are not deleted when the count of TiFlash replicas is set to 0, alter column set default wrongly updates the table schema, date_format '\n' MySQL-incompatible, updating partitioned tables using join, Nulleq function on Enum values, upper() lower() panic, time zone changing columns to timestamp type, TiDB OOM exporting data using ChunkRPC, sub SELECT LIMIT dynamic partition pruning mode, INFORMATION_SCHEMA.COLUMNS bit default value format, partition table pruning after server restart, add column wrong default timestamp after SET timestamp, passwordless account MySQL 5.5 or 5.6 client may fail, reading partitioned tables in dynamic mode in transactions, dispatch duplicate tasks to TiFlash, timdiff millisecond wrong result, explicitly reading partitions IndexJoin plan, renaming a column changing its column type concurrently, TiFlash plans net cost formula, KILL TIDB idle connections, generated columns wrong results, left join deleting data of multiple tables, SUBTIME overflow wrong result, selection operator cannot be pushed down having condition, CTE might be blocked when a query reports errors, varbinary or varchar columns non-strict mode, information_schema.placement_policies wrong number of followers, column prefix length as 0, partition names ending with spaces, RENAME TABLE statement error message
- Follow-up Guidance: The chunk ends with a TiKV section header, but the supplied content here only includes the TiDB bug-fix items.
- Classification Note: This is a release-notes bug-fixes chunk because the official content is a list of resolved TiDB defects and corrected behaviors in TiDB 6.0.0.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix a bug that TiDB fails to create tables with placement rules when `SCHEDULE = majority_in_primary`, and `PrimaryRegion` and `Regions` are of the same value [#31271](https://github.com/pingcap/tidb/issues/31271)
    - Fix the `invalid transaction` error when executing a query using index lookup join [#30468](https://github.com/pingcap/tidb/issues/30468)
    - Fix a bug that `show grants` returns incorrect results when two or more privileges are granted [#30855](https://github.com/pingcap/tidb/issues/30855)
    - Fix a bug that `INSERT INTO t1 SET timestamp_col = DEFAULT` would set the timestamp to the zero timestamp for the field defaulted to `CURRENT_TIMESTAMP` [#29926](https://github.com/pingcap/tidb/issues/29926)
    - ​Fix errors reported in reading the results by avoiding encoding the maximum value and minimum non-null value of the string type [#31721](https://github.com/pingcap/tidb/issues/31721)
    - Fix load data panic if the data is broken at an escape character [#31589](https://github.com/pingcap/tidb/issues/31589)
    - Fix the issue that the `greatest` or `least` function with collation gets a wrong result [#31789](https://github.com/pingcap/tidb/issues/31789)
    - Fix a bug that the date_add and date_sub functions might return incorrect data types [#31809](https://github.com/pingcap/tidb/issues/31809)
    - Fix possible panic when inserting data to virtually generated columns using an insert statement [#31735](https://github.com/pingcap/tidb/issues/31735)
    - Fix a bug that no error is reported when duplicate columns are present in the created list partition [#31784](https://github.com/pingcap/tidb/issues/31784)
    - Fix wrong results returned when `select for update union select` uses incorrect snapshots [#31530](https://github.com/pingcap/tidb/issues/31530)
    - Fix the potential issue that Regions might be unevenly distributed after a restore operation is finished [#31034](https://github.com/pingcap/tidb/issues/31034)
    - Fix a bug that COERCIBILITY is wrong for the `json` type [#31541](https://github.com/pingcap/tidb/issues/31541)
    - Fix wrong collation of the `json` type when this type is processed using builtin-func [#31320](https://github.com/pingcap/tidb/issues/31320)
    - Fix a bug that PD rules are not deleted when the count of TiFlash replicas is set to 0 [#32190](https://github.com/pingcap/tidb/issues/32190)
    - Fix the issue that `alter column set default` wrongly updates the table schema [#31074](https://github.com/pingcap/tidb/issues/31074)
    - Fix the issue that `date_format` in TiDB handles `'\n'` in a MySQL-incompatible way [#32232](https://github.com/pingcap/tidb/issues/32232)
    - Fix a bug that errors may occur when updating partitioned tables using join [#31629](https://github.com/pingcap/tidb/issues/31629)
    - Fix wrong range calculation results for Nulleq function on Enum values [#32428](https://github.com/pingcap/tidb/issues/32428)
    - Fix possible panic in `upper()` and `lower()` functions [#32488](https://github.com/pingcap/tidb/issues/32488)
    - Fix time zone problems encountered when changing the other type columns to timestamp type columns [#29585](https://github.com/pingcap/tidb/issues/29585)
    - Fix TiDB OOM when exporting data using ChunkRPC [#31981](https://github.com/pingcap/tidb/issues/31981) [#30880](https://github.com/pingcap/tidb/issues/30880)
    - Fix a bug that sub SELECT LIMIT does not work as expected in dynamic partition pruning mode [#32516](https://github.com/pingcap/tidb/issues/32516)
    - Fix wrong or inconsistent format of bit default value in the `INFORMATION_SCHEMA.COLUMNS` table [#32655](https://github.com/pingcap/tidb/issues/32655)
    - Fix a bug that partition table pruning might not work for listing partition tables after server restart [#32416](https://github.com/pingcap/tidb/issues/32416)
    - Fix a bug that `add column` might use a wrong default timestamp after `SET timestamp` is executed [#31968](https://github.com/pingcap/tidb/issues/31968)
    - Fix a bug that connecting to a TiDB passwordless account from MySQL 5.5 or 5.6 client may fail [#32334](https://github.com/pingcap/tidb/issues/32334)
    - Fix wrong results when reading partitioned tables in dynamic mode in transactions [#29851](https://github.com/pingcap/tidb/issues/29851)
    - Fix a bug that TiDB may dispatch duplicate tasks to TiFlash [#32814](https://github.com/pingcap/tidb/issues/32814)
    - Fix wrong results returned when the input of the `timdiff` function contains a millisecond [#31680](https://github.com/pingcap/tidb/issues/31680)
    - Fix wrong results when explicitly reading partitions and using the IndexJoin plan [#32007](https://github.com/pingcap/tidb/issues/32007)
    - Fix a bug that renaming a column fails when changing its column type concurrently [#31075](https://github.com/pingcap/tidb/issues/31075)
    - Fix a bug that the formula for calculating net cost for TiFlash plans is not aligned with TiKV plans [#30103](https://github.com/pingcap/tidb/issues/30103)
    - Fix a bug that `KILL TIDB` cannot take effect immediately on idle connections [#24031](https://github.com/pingcap/tidb/issues/24031)
    - Fix possible wrong results when querying a table with generated columns [#33038](https://github.com/pingcap/tidb/issues/33038)
    - Fix wrong results of deleting data of multiple tables using `left join` [#31321](https://github.com/pingcap/tidb/issues/31321)
    - Fix a bug that the `SUBTIME` function returns a wrong result in case of overflow [#31868](https://github.com/pingcap/tidb/issues/31868)
    - Fix a bug that the `selection` operator cannot be pushed down when an aggregation query contains the `having` condition [#33166](https://github.com/pingcap/tidb/issues/33166)
    - Fix a bug that CTE might be blocked when a query reports errors [#31302](https://github.com/pingcap/tidb/issues/31302)
    - Fix a bug that excessive length of varbinary or varchar columns when creating tables in non-strict mode might result in errors [#30328](https://github.com/pingcap/tidb/issues/30328)
    - Fix the wrong number of followers in `information_schema.placement_policies` when no follower is specified [#31702](https://github.com/pingcap/tidb/issues/31702)
    - Fix the issue that TiDB allows to specify column prefix length as 0 when an index is created [#31972](https://github.com/pingcap/tidb/issues/31972)
    - Fix the issue that TiDB allows partition names ending with spaces [#31535](https://github.com/pingcap/tidb/issues/31535)
    - Correct the error message of the `RENAME TABLE` statement [#29893](https://github.com/pingcap/tidb/issues/29893)

+ TiKV
