# SHOW TABLE REGIONS syntax and returned columns

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-table-regions.md`
- Source Title: `SHOW TABLE REGIONS`
- Source Heading Path: `SHOW TABLE REGIONS | SHOW TABLE REGIONS > Syntax | SHOW TABLE REGIONS > Synopsis`
- Source Line Ranges: `5-62`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `pd`, `tikv`, `tidb`
- Topic Tags: `show-table-regions`, `syntax`, `region-metadata`, `placement-policy`, `where-clause`, `estimated-metrics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0682_d64d3c4e42`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-table-regions.md#show-table-regions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `648a6bce34f1dc4202f3f4ed97eb002625bd83146d486c342bafb58a588869f3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-table-regions#show-table-regions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-table-regions.md

## Retrieval Guidance

- Use When: Use this chunk when you need the syntax of SHOW TABLE REGIONS or SHOW TABLE ... INDEX ... REGIONS and the meaning of the returned Region metadata columns.
- Retrieval Keywords: SHOW TABLE REGIONS, SHOW TABLE [table_name] REGIONS [WhereClauseOptional], SHOW TABLE [table_name] INDEX [index_name] REGIONS [WhereClauseOptional], ShowTableRegionStmt, WHERE Expression, REGION_ID, START_KEY, END_KEY, LEADER_ID, LEADER_STORE_ID, PEERS, SCATTERING, WRITTEN_BYTES, READ_BYTES, APPROXIMATE_SIZE(MB), APPROXIMATE_KEYS, SCHEDULING_CONSTRAINTS, SCHEDULING_STATE, placement policy settings, PD heartbeat information
- Follow-up Guidance: The source notes that WRITTEN_BYTES, READ_BYTES, APPROXIMATE_SIZE(MB), and APPROXIMATE_KEYS are estimated data from PD based on Region heartbeat information.
- Classification Note: This is reference content because it defines the SQL syntax and enumerates the columns returned by SHOW TABLE REGIONS.

## Official Source Content

# SHOW TABLE REGIONS

The `SHOW TABLE REGIONS` statement is used to show the Region information of a table in TiDB.

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.
## Syntax

```sql
SHOW TABLE [table_name] REGIONS [WhereClauseOptional];
SHOW TABLE [table_name] INDEX [index_name] REGIONS [WhereClauseOptional];
```
## Synopsis

```ebnf+diagram
ShowTableRegionStmt ::=
    "SHOW" "TABLE" TableName PartitionNameList? ("INDEX" IndexName)? "REGIONS" ("WHERE" Expression)?

TableName ::=
    (SchemaName ".")? Identifier
```

Executing `SHOW TABLE REGIONS` returns the following columns:

* `REGION_ID`: The Region ID.
* `START_KEY`: The start key of the Region.
* `END_KEY`: The end key of the Region.
* `LEADER_ID`: The Leader ID of the Region.
* `LEADER_STORE_ID`: The ID of the store (TiKV) where the Region leader is located.
* `PEERS`: The IDs of all Region replicas.
* `SCATTERING`: Whether the Region is being scheduled. `1` means true.
* `WRITTEN_BYTES`: The estimated amount of data written into the Region within one heartbeat cycle. The unit is byte.
* `READ_BYTES`: The estimated amount of data read from the Region within one heartbeat cycle. The unit is byte.
* `APPROXIMATE_SIZE(MB)`: The estimated amount of data in the Region. The unit is megabytes (MB).
* `APPROXIMATE_KEYS`: The estimated number of Keys in the Region.

* `SCHEDULING_CONSTRAINTS`: The [placement policy settings](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql) associated with the table or partition to which a Region belongs.

* `SCHEDULING_CONSTRAINTS`: The placement policy settings associated with the table or partition to which a Region belongs.

* `SCHEDULING_STATE`: The scheduling state of the Region which has a placement policy.

> **Note:**
>
> The values of `WRITTEN_BYTES`, `READ_BYTES`, `APPROXIMATE_SIZE(MB)`, `APPROXIMATE_KEYS` are not accurate data. They are estimated data from PD based on the heartbeat information that PD receives from the Region.
