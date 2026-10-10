# ALTER RANGE syntax and placement policy examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-alter-range.md`
- Source Title: `ALTER RANGE`
- Source Heading Path: `ALTER RANGE | ALTER RANGE > Synopsis | ALTER RANGE > Examples`
- Source Line Ranges: `5-36`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `alter range`, `placement policy`, `syntax`, `global range`, `meta range`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0525_ba64a1be37`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-alter-range.md#alter-range`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3789977a819241e706fd6ac9279b6bfa0b51623a7df37ca81bf01637267da4dd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-range#alter-range
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-alter-range.md

## Retrieval Guidance

- Use When: You need the TiDB `ALTER RANGE` syntax or an example of applying a placement policy to the `global` or `meta` range.
- Retrieval Keywords: ALTER RANGE, AlterRangeStmt, PLACEMENT POLICY, global, meta, specific placement policy, TiDB, CREATE PLACEMENT POLICY, deploy111, five_replicas
- Follow-up Guidance: The example shows `ALTER RANGE global PLACEMENT POLICY = "deploy111";` and `ALTER RANGE meta PLACEMENT POLICY = "five_replicas";` after creating the two placement policies.
- Classification Note: The official content classifies `ALTER RANGE` as a SQL statement used only to modify the range of a specific placement policy, with `global` and `meta` as the two supported range parameters.

## Official Source Content

# ALTER RANGE

Currently, the `ALTER RANGE` statement can only be used to modify the range of a specific placement policy in TiDB.

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.
## Synopsis

```ebnf+diagram
AlterRangeStmt ::=
    'ALTER' 'RANGE' Identifier PlacementPolicyOption
```

`ALTER RANGE` supports the following two parameters:

- `global`: indicates the range of all data in a cluster.
- `meta`: indicates the range of internal metadata stored in TiDB.
## Examples

```sql
CREATE PLACEMENT POLICY `deploy111` CONSTRAINTS='{"+region=us-east-1":1, "+region=us-east-2": 1, "+region=us-west-1": 1}';
CREATE PLACEMENT POLICY `five_replicas` FOLLOWERS=4;

ALTER RANGE global PLACEMENT POLICY = "deploy111";
ALTER RANGE meta PLACEMENT POLICY = "five_replicas";
```

The preceding example creates two placement policies (`deploy111` and `five_replicas`), specifies constraints for different regions, and then applies the `deploy111` placement policy to all data in the cluster range and the `five_replicas` placement policy to the metadata range.
