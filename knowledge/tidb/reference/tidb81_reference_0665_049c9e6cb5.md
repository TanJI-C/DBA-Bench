# SHOW PLACEMENT FOR syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-placement-for.md`
- Source Title: `SHOW PLACEMENT FOR`
- Source Heading Path: `SHOW PLACEMENT FOR | SHOW PLACEMENT FOR > Synopsis | SHOW PLACEMENT FOR > Examples | SHOW PLACEMENT FOR > MySQL compatibility | SHOW PLACEMENT FOR > See also`
- Source Line Ranges: `5-88`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `pd`, `tidb`, `tikv`, `cloud`
- Topic Tags: `placement`, `placement-policy`, `syntax`, `examples`, `mysql-compatibility`, `scheduling-state`, `partitions`, `database`, `table`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0665_049c9e6cb5`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-placement-for.md#show-placement-for`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d87038e8553d3e5f0fcf532ef3e7774d7e43f7f1b4e5fc796e2ec8ba413ea9b4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-placement-for#show-placement-for
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-placement-for.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to view the canonical placement options and Scheduling_State for a specific database, table, or table partition with SHOW PLACEMENT FOR.
- Retrieval Keywords: SHOW PLACEMENT FOR, Scheduling_State, PENDING, INPROGRESS, SCHEDULED, SHOW PLACEMENT FOR DATABASE, SHOW PLACEMENT FOR TABLE, SHOW PLACEMENT FOR TABLE PARTITION, ShowPlacementTarget, CREATE PLACEMENT POLICY, ALTER DATABASE test PLACEMENT POLICY=p1, SHOW CREATE TABLE, Placement Rules in SQL, MySQL compatibility
- Follow-up Guidance: The page also points to Placement Rules in SQL, SHOW PLACEMENT, and CREATE PLACEMENT POLICY.
- Classification Note: This is reference content because it defines SHOW PLACEMENT FOR syntax, explains the returned Scheduling_State values from PD, and shows example SQL and result sets.

## Official Source Content

# SHOW PLACEMENT FOR

`SHOW PLACEMENT FOR` summarizes all placement options, and presents them in the canonical form for a specific table, database schema, or partition.

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

The statement returns a result set in which the `Scheduling_State` field indicates the current progress that the Placement Driver (PD) has made in scheduling the placement:

* `PENDING`: The PD has not yet started scheduling the placement. This might indicate that the placement rules are semantically correct, but cannot currently be satisfied by the cluster. For example, if `FOLLOWERS=4` but there are only 3 TiKV stores that are candidates for followers.
* `INPROGRESS`: The PD is currently scheduling the placement.
* `SCHEDULED`: The PD has successfully scheduled the placement.
## Synopsis

```ebnf+diagram
ShowStmt ::=
    "SHOW" "PLACEMENT" "FOR" ShowPlacementTarget

ShowPlacementTarget ::=
    DatabaseSym DBName
|   "TABLE" TableName
|   "TABLE" TableName "PARTITION" Identifier
```
## Examples

```sql
CREATE PLACEMENT POLICY p1 PRIMARY_REGION="us-east-1" REGIONS="us-east-1,us-west-1" FOLLOWERS=4;
ALTER DATABASE test PLACEMENT POLICY=p1;
CREATE TABLE t1 (a INT);
SHOW PLACEMENT FOR DATABASE test;
SHOW PLACEMENT FOR TABLE t1;
SHOW CREATE TABLE t1\G
CREATE TABLE t3 (a INT) PARTITION BY RANGE (a) (PARTITION p1 VALUES LESS THAN (10), PARTITION p2 VALUES LESS THAN (20));
SHOW PLACEMENT FOR TABLE t3 PARTITION p1\G
```

```
Query OK, 0 rows affected (0.02 sec)

Query OK, 0 rows affected (0.00 sec)

Query OK, 0 rows affected (0.01 sec)

+---------------+----------------------------------------------------------------------+------------------+
| Target        | Placement                                                            | Scheduling_State |
+---------------+----------------------------------------------------------------------+------------------+
| DATABASE test | PRIMARY_REGION="us-east-1" REGIONS="us-east-1,us-west-1" FOLLOWERS=4 | INPROGRESS       |
+---------------+----------------------------------------------------------------------+------------------+
1 row in set (0.00 sec)

+---------------+-------------+------------------+
| Target        | Placement   | Scheduling_State |
+---------------+-------------+------------------+
| TABLE test.t1 | FOLLOWERS=4 | INPROGRESS       |
+---------------+-------------+------------------+
1 row in set (0.00 sec)

***************************[ 1. row ]***************************
Table        | t1
Create Table | CREATE TABLE `t1` (
  `a` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin /*T![placement] PLACEMENT POLICY=`p1` */
1 row in set (0.00 sec)

***************************[ 1. row ]***************************
Target           | TABLE test.t3 PARTITION p1
Placement        | PRIMARY_REGION="us-east-1" REGIONS="us-east-1,us-west-1" FOLLOWERS=4
Scheduling_State | PENDING
1 row in set (0.00 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [Placement Rules in SQL](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql)
* [SHOW PLACEMENT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-placement)
* [CREATE PLACEMENT POLICY](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-placement-policy)
