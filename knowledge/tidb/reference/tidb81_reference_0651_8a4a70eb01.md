# SHOW CREATE PLACEMENT POLICY syntax and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-create-placement-policy.md`
- Source Title: `SHOW CREATE PLACEMENT POLICY`
- Source Heading Path: `SHOW CREATE PLACEMENT POLICY | SHOW CREATE PLACEMENT POLICY > Synopsis | SHOW CREATE PLACEMENT POLICY > Examples | SHOW CREATE PLACEMENT POLICY > MySQL compatibility | SHOW CREATE PLACEMENT POLICY > See also`
- Source Line Ranges: `5-55`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `cloud`
- Topic Tags: `placement-policy`, `show-create`, `sql-syntax`, `examples`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0651_8a4a70eb01`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-create-placement-policy.md#show-create-placement-policy`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1208a17efdab9cadd7765925cc97bad79172e2c11d956c604d9eed888cfdafd0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-placement-policy#show-create-placement-policy
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-create-placement-policy.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, example output, or compatibility note for showing the definition of a placement policy with SHOW CREATE PLACEMENT POLICY.
- Retrieval Keywords: SHOW CREATE PLACEMENT POLICY, ShowCreatePlacementPolicyStmt, SHOW CREATE PLACEMENT POLICY p1, PolicyName, CREATE PLACEMENT POLICY `p1`, PRIMARY_REGION="us-east-1", REGIONS="us-east-1,us-west-1", FOLLOWERS=4, TiDB extension to MySQL syntax, show the definition of a placement policy, recreate it in another TiDB cluster
- Follow-up Guidance: The page also points to Placement Rules in SQL, SHOW PLACEMENT, CREATE PLACEMENT POLICY, ALTER PLACEMENT POLICY, and DROP PLACEMENT POLICY.
- Classification Note: This is reference content because it defines the SHOW CREATE PLACEMENT POLICY statement, gives its formal synopsis, and shows example SQL and output.

## Official Source Content

# SHOW CREATE PLACEMENT POLICY

`SHOW CREATE PLACEMENT POLICY` is used to show the definition of a placement policy. This can be used to see the current definition of a placement policy and recreate it in another TiDB cluster.

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.
## Synopsis

```ebnf+diagram
ShowCreatePlacementPolicyStmt ::=
    "SHOW" "CREATE" "PLACEMENT" "POLICY" PolicyName

PolicyName ::=
    Identifier
```
## Examples

```sql
CREATE PLACEMENT POLICY p1 PRIMARY_REGION="us-east-1" REGIONS="us-east-1,us-west-1" FOLLOWERS=4;
CREATE TABLE t1 (a INT) PLACEMENT POLICY=p1;
SHOW CREATE PLACEMENT POLICY p1\G
```

```
Query OK, 0 rows affected (0.08 sec)

Query OK, 0 rows affected (0.10 sec)

***************************[ 1. row ]***************************
Policy        | p1
Create Policy | CREATE PLACEMENT POLICY `p1` PRIMARY_REGION="us-east-1" REGIONS="us-east-1,us-west-1" FOLLOWERS=4
1 row in set (0.00 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [Placement Rules in SQL](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql)
* [SHOW PLACEMENT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-placement)
* [CREATE PLACEMENT POLICY](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-placement-policy)
* [ALTER PLACEMENT POLICY](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-placement-policy)
* [DROP PLACEMENT POLICY](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-placement-policy)
