# SHOW PLACEMENT LABELS syntax and example output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-placement-labels.md`
- Source Title: `SHOW PLACEMENT LABELS`
- Source Heading Path: `SHOW PLACEMENT LABELS | SHOW PLACEMENT LABELS > Synopsis | SHOW PLACEMENT LABELS > Examples | SHOW PLACEMENT LABELS > MySQL compatibility | SHOW PLACEMENT LABELS > See also`
- Source Line Ranges: `5-45`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `placement-rules`, `labels`, `sql-syntax`, `examples`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0666_9ad8750773`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-placement-labels.md#show-placement-labels`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fccd2d18a5828ffc1e29fb0306575096f03c1817714296dda9bf64bf8a43408e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-placement-labels#show-placement-labels
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-placement-labels.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the syntax, purpose, or example output of the SHOW PLACEMENT LABELS statement for summarizing labels and values available for Placement Rules.
- Retrieval Keywords: SHOW PLACEMENT LABELS, SHOW PLACEMENT LABELS syntax, SHOW PLACEMENT LABELS example output, Placement Rules, ShowLikeOrWhere, Key, Values, region, zone, TiDB extension to MySQL syntax
- Follow-up Guidance: The page also points to Placement Rules in SQL, SHOW PLACEMENT, and CREATE PLACEMENT POLICY as related statements and concepts.
- Classification Note: This is reference content because it defines the SHOW PLACEMENT LABELS statement, gives its synopsis and example result set, and notes that it is a TiDB extension to MySQL syntax.

## Official Source Content

# SHOW PLACEMENT LABELS

`SHOW PLACEMENT LABELS` is used to summarize the labels and values that are available for Placement Rules.

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.
## Synopsis

```ebnf+diagram
ShowStmt ::=
    "SHOW" "PLACEMENT" "LABELS" ShowLikeOrWhere?
```
## Examples

```sql
SHOW PLACEMENT LABELS;
```

```
+--------+----------------+
| Key    | Values         |
+--------+----------------+
| region | ["us-east-1"]  |
| zone   | ["us-east-1a"] |
+--------+----------------+
2 rows in set (0.00 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [Placement Rules in SQL](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql)
* [SHOW PLACEMENT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-placement)
* [CREATE PLACEMENT POLICY](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-placement-policy)
