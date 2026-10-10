# INSPECTION_RULES table structure and example contents

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-inspection-rules.md`
- Source Title: `INSPECTION_RULES`
- Source Heading Path: `INSPECTION_RULES`
- Source Line Ranges: `5-59`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `information-schema`, `inspection-rules`, `diagnostic-tests`, `schema`, `sql-query`, `self-managed`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0391_3adf8ffbfa`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-inspection-rules.md#inspection-rules`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e571c6a6bde08de8687750c91ae6352ecd0887da6b6800ab2582ff4359370cfb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-inspection-rules#inspection-rules
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-inspection-rules.md

## Retrieval Guidance

- Use When: Use this chunk when identifying what the information_schema.INSPECTION_RULES table contains, its column structure, or the example diagnostic test names and types returned by querying it.
- Retrieval Keywords: INSPECTION_RULES, information_schema, DESC inspection_rules, SELECT * FROM inspection_rules, NAME, TYPE, COMMENT, diagnostic tests, inspection result, config, version, node-load, critical-error, threshold-check, ddl, gc, pd, query-summary, raftstore, read-link, rocksdb, stats, wait-events, write-link, inspection, summary
- Follow-up Guidance: The source points to inspection result for example usage of the diagnostic tests listed in INSPECTION_RULES.
- Classification Note: This is reference content because it defines the INSPECTION_RULES table schema and shows example query output, and the note states it is only applicable to TiDB Self-Managed and not available on TiDB Cloud.

## Official Source Content

# INSPECTION_RULES

The `INSPECTION_RULES` table provides information about which diagnostic tests are run in an inspection result. See [inspection result](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-inspection-result) for example usage.

> **Note:**
>
> This table is only applicable to TiDB Self-Managed and not available on [TiDB Cloud](https://docs.pingcap.com/tidbcloud/).

```sql
USE information_schema;
DESC inspection_rules;
```

```
+---------+--------------+------+------+---------+-------+
| Field   | Type         | Null | Key  | Default | Extra |
+---------+--------------+------+------+---------+-------+
| NAME    | varchar(64)  | YES  |      | NULL    |       |
| TYPE    | varchar(64)  | YES  |      | NULL    |       |
| COMMENT | varchar(256) | YES  |      | NULL    |       |
+---------+--------------+------+------+---------+-------+
3 rows in set (0.00 sec)
```

```sql
SELECT * FROM inspection_rules;
```

```
+-----------------+------------+---------+
| NAME            | TYPE       | COMMENT |
+-----------------+------------+---------+
| config          | inspection |         |
| version         | inspection |         |
| node-load       | inspection |         |
| critical-error  | inspection |         |
| threshold-check | inspection |         |
| ddl             | summary    |         |
| gc              | summary    |         |
| pd              | summary    |         |
| query-summary   | summary    |         |
| raftstore       | summary    |         |
| read-link       | summary    |         |
| rocksdb         | summary    |         |
| stats           | summary    |         |
| wait-events     | summary    |         |
| write-link      | summary    |         |
+-----------------+------------+---------+
15 rows in set (0.00 sec)
```
