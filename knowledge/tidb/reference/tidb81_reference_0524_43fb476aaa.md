# ALTER PLACEMENT POLICY syntax and usage

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-alter-placement-policy.md`
- Source Title: `ALTER PLACEMENT POLICY`
- Source Heading Path: `ALTER PLACEMENT POLICY | ALTER PLACEMENT POLICY > Synopsis | ALTER PLACEMENT POLICY > Examples | ALTER PLACEMENT POLICY > MySQL compatibility | ALTER PLACEMENT POLICY > See also`
- Source Line Ranges: `5-94`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `placement-policy`, `sql-syntax`, `ddl`, `regions`, `followers`, `constraints`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0524_43fb476aaa`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-alter-placement-policy.md#alter-placement-policy`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4b9867d1b4f3aeb0020f74c370c46da0a9ed45c7efcd19dc86f60856533590cd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-placement-policy#alter-placement-policy
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-alter-placement-policy.md

## Retrieval Guidance

- Use When: Use this chunk when asking about the SQL syntax, behavior, or examples of modifying an existing placement policy with ALTER PLACEMENT POLICY, including how changes affect tables and partitions using that policy.
- Retrieval Keywords: ALTER PLACEMENT POLICY, AlterPolicyStmt, PlacementOptionList, FOLLOWERS, PRIMARY_REGION, REGIONS, SCHEDULE, LEARNERS, CONSTRAINTS, LEADER_CONSTRAINTS, FOLLOWER_CONSTRAINTS, LEARNER_CONSTRAINTS, SURVIVAL_PREFERENCES, SHOW CREATE PLACEMENT POLICY, SHOW PLACEMENT LABELS, CREATE PLACEMENT POLICY, DROP PLACEMENT POLICY, placement rules in SQL, replaces the previous policy with the new definition, does not merge the old policy with the new one, tables and partitions will automatically be updated
- Follow-up Guidance: The source also points to SHOW PLACEMENT LABELS for available regions and notes that ALTER PLACEMENT POLICY is a TiDB extension to MySQL syntax.
- Classification Note: This is reference content because it defines the ALTER PLACEMENT POLICY statement, its EBNF synopsis, supported placement options, example SQL, and MySQL compatibility note from the official documentation.

## Official Source Content

# ALTER PLACEMENT POLICY

`ALTER PLACEMENT POLICY` is used to modify existing placement policies that have previously been created. All the tables and partitions which use the placement policy will automatically be updated.

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

`ALTER PLACEMENT POLICY` _replaces_ the previous policy with the new definition. It does not _merge_ the old policy with the new one. In the following example, `FOLLOWERS=4` is lost when the `ALTER PLACEMENT POLICY` is executed:

```sql
CREATE PLACEMENT POLICY p1 FOLLOWERS=4;
ALTER PLACEMENT POLICY p1 PRIMARY_REGION="us-east-1" REGIONS="us-east-1,us-west-1";
```
## Synopsis

```ebnf+diagram
AlterPolicyStmt ::=
    "ALTER" "PLACEMENT" "POLICY" IfExists PolicyName PlacementOptionList

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
CREATE PLACEMENT POLICY p1 PRIMARY_REGION="us-east-1" REGIONS="us-east-1,us-west-1";
CREATE TABLE t1 (i INT) PLACEMENT POLICY=p1; -- Assign policy p1 to table t1
ALTER PLACEMENT POLICY p1 PRIMARY_REGION="us-east-1" REGIONS="us-east-1,us-west-1,us-west-2" FOLLOWERS=4; -- The rules of t1 will be updated automatically.
SHOW CREATE PLACEMENT POLICY p1\G
```

```
Query OK, 0 rows affected (0.08 sec)

Query OK, 0 rows affected (0.10 sec)

***************************[ 1. row ]***************************
Policy        | p1
Create Policy | CREATE PLACEMENT POLICY `p1` PRIMARY_REGION="us-east-1" REGIONS="us-east-1,us-west-1,us-west-2" FOLLOWERS=4
1 row in set (0.00 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [Placement Rules in SQL](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql)
* [SHOW PLACEMENT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-placement)
* [CREATE PLACEMENT POLICY](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-placement-policy)
* [DROP PLACEMENT POLICY](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-placement-policy)
