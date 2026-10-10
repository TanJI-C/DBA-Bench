# DROP PLACEMENT POLICY syntax, usage constraints, and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-drop-placement-policy.md`
- Source Title: `DROP PLACEMENT POLICY`
- Source Heading Path: `DROP PLACEMENT POLICY | DROP PLACEMENT POLICY > Synopsis | DROP PLACEMENT POLICY > Examples | DROP PLACEMENT POLICY > MySQL compatibility | DROP PLACEMENT POLICY > See also`
- Source Line Ranges: `5-73`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `placement-policy`, `drop-statement`, `sql-syntax`, `examples`, `mysql-compatibility`, `information-schema`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0576_0c80a0a16c`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-drop-placement-policy.md#drop-placement-policy`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5329eea67919e4c7e8d2a4ff13eef456b540ac187514213fcf1035816e4c24fe`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-placement-policy#drop-placement-policy
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-drop-placement-policy.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the SQL syntax, constraints, examples, or compatibility details for dropping a placement policy in TiDB.
- Retrieval Keywords: DROP PLACEMENT POLICY, DropPolicyStmt, IfExists, PolicyName, placement policy 'p1' is still in use, ERROR 8241 (HY000), information_schema.tables, information_schema.partitions, tidb_placement_policy_name, ALTER TABLE t1 PLACEMENT POLICY=default, TiDB extension to MySQL syntax
- Follow-up Guidance: The content also points to Placement Rules in SQL, SHOW PLACEMENT, CREATE PLACEMENT POLICY, and ALTER PLACEMENT POLICY.
- Classification Note: This is reference content because it defines DROP PLACEMENT POLICY syntax, states the rule that referenced policies cannot be dropped, and shows exact SQL examples and error output.

## Official Source Content

# DROP PLACEMENT POLICY

`DROP PLACEMENT POLICY` is used to drop a previously created placement policy.

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.
## Synopsis

```ebnf+diagram
DropPolicyStmt ::=
    "DROP" "PLACEMENT" "POLICY" IfExists PolicyName

PolicyName ::=
    Identifier
```
## Examples

Placement policies can only be dropped when they are not referenced by any tables or partitions.

```sql
CREATE PLACEMENT POLICY p1 FOLLOWERS=4;
CREATE TABLE t1 (a INT PRIMARY KEY) PLACEMENT POLICY=p1;
DROP PLACEMENT POLICY p1;  -- This statement fails because the placement policy p1 is referenced.

-- Finds which tables and partitions reference the placement policy.
SELECT table_schema, table_name FROM information_schema.tables WHERE tidb_placement_policy_name='p1';
SELECT table_schema, table_name FROM information_schema.partitions WHERE tidb_placement_policy_name='p1';

ALTER TABLE t1 PLACEMENT POLICY=default;  -- Removes the placement policy from t1.
DROP PLACEMENT POLICY p1;  -- Succeeds.
```

```sql
Query OK, 0 rows affected (0.10 sec)

Query OK, 0 rows affected (0.11 sec)

ERROR 8241 (HY000): Placement policy 'p1' is still in use

+--------------+------------+
| table_schema | table_name |
+--------------+------------+
| test         | t1         |
+--------------+------------+
1 row in set (0.00 sec)

Empty set (0.01 sec)

Query OK, 0 rows affected (0.08 sec)

Query OK, 0 rows affected (0.21 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [Placement Rules in SQL](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql)
* [SHOW PLACEMENT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-placement)
* [CREATE PLACEMENT POLICY](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-placement-policy)
* [ALTER PLACEMENT POLICY](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-placement-policy)
