# CREATE PLACEMENT POLICY syntax and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-create-placement-policy.md`
- Source Title: `CREATE PLACEMENT POLICY`
- Source Heading Path: `CREATE PLACEMENT POLICY | CREATE PLACEMENT POLICY > Synopsis | CREATE PLACEMENT POLICY > Examples | CREATE PLACEMENT POLICY > MySQL compatibility | CREATE PLACEMENT POLICY > See also`
- Source Line Ranges: `5-88`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `cloud`
- Topic Tags: `placement-policy`, `sql-syntax`, `examples`, `mysql-compatibility`, `region-labels`, `table-placement`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0556_3f59a95afd`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-create-placement-policy.md#create-placement-policy`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3f12a1c21ccea295af0eb8cfef7705668bbbf1a21e23d8af3278e574ba15b7e1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-placement-policy#create-placement-policy
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-create-placement-policy.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks for the syntax, options, examples, or MySQL compatibility of CREATE PLACEMENT POLICY in TiDB.
- Retrieval Keywords: CREATE PLACEMENT POLICY, CreatePolicyStmt, PlacementOptionList, FOLLOWERS, PRIMARY_REGION, REGIONS, SCHEDULE, LEARNERS, CONSTRAINTS, LEADER_CONSTRAINTS, FOLLOWER_CONSTRAINTS, LEARNER_CONSTRAINTS, SURVIVAL_PREFERENCES, CREATE TABLE t1 (a INT) PLACEMENT POLICY=p1, SHOW CREATE PLACEMENT POLICY p1, SHOW PLACEMENT LABELS, placement policy, Placement Rules in SQL
- Follow-up Guidance: The examples note that available regions can be checked with SHOW PLACEMENT LABELS, and related statements include SHOW PLACEMENT, ALTER PLACEMENT POLICY, and DROP PLACEMENT POLICY.
- Classification Note: This is reference content because it defines the CREATE PLACEMENT POLICY statement with formal syntax, supported placement options, example SQL, and a MySQL compatibility note.

## Official Source Content

# CREATE PLACEMENT POLICY

`CREATE PLACEMENT POLICY` is used to create a named placement policy that can later be assigned to tables, partitions, or database schemas.

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.
## Synopsis

```ebnf+diagram
CreatePolicyStmt ::=
    "CREATE" "PLACEMENT" "POLICY" IfNotExists PolicyName PlacementOptionList

PolicyName ::=
    Identifier

PlacementOptionList ::=
    PlacementOption
|   PlacementOptionList PlacementOption
|   PlacementOptionList ',' PlacementOption

PlacementOption ::=
    CommonPlacementOption
|   SugarPlacementOption
|   AdvancedPlacementOption

CommonPlacementOption ::=
    "FOLLOWERS" EqOpt LengthNum

SugarPlacementOption ::=
    "PRIMARY_REGION" EqOpt stringLit
|   "REGIONS" EqOpt stringLit
|   "SCHEDULE" EqOpt stringLit

AdvancedPlacementOption ::=
    "LEARNERS" EqOpt LengthNum
|   "CONSTRAINTS" EqOpt stringLit
|   "LEADER_CONSTRAINTS" EqOpt stringLit
|   "FOLLOWER_CONSTRAINTS" EqOpt stringLit
|   "LEARNER_CONSTRAINTS" EqOpt stringLit
|   "SURVIVAL_PREFERENCES" EqOpt stringLit
```
## Examples

> **Note:**
>
> To know which regions are available in your cluster, see [`SHOW PLACEMENT LABELS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-placement-labels).
>
> If you do not see any available regions, your TiKV installation might not have labels set correctly.

```sql
CREATE PLACEMENT POLICY p1 PRIMARY_REGION="us-east-1" REGIONS="us-east-1,us-west-1" FOLLOWERS=4;
CREATE TABLE t1 (a INT) PLACEMENT POLICY=p1;
SHOW CREATE PLACEMENT POLICY p1;
```

```
Query OK, 0 rows affected (0.08 sec)

Query OK, 0 rows affected (0.10 sec)

+--------+---------------------------------------------------------------------------------------------------+
| Policy | Create Policy                                                                                     |
+--------+---------------------------------------------------------------------------------------------------+
| p1     | CREATE PLACEMENT POLICY `p1` PRIMARY_REGION="us-east-1" REGIONS="us-east-1,us-west-1" FOLLOWERS=4 |
+--------+---------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [Placement Rules in SQL](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql)
* [SHOW PLACEMENT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-placement)
* [ALTER PLACEMENT POLICY](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-placement-policy)
* [DROP PLACEMENT POLICY](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-placement-policy)
