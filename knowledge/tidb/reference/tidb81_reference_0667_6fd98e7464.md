# SHOW PLACEMENT syntax and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-placement.md`
- Source Title: `SHOW PLACEMENT`
- Source Heading Path: `SHOW PLACEMENT | SHOW PLACEMENT > Synopsis | SHOW PLACEMENT > Examples | SHOW PLACEMENT > MySQL compatibility | SHOW PLACEMENT > See also`
- Source Line Ranges: `5-58`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `pd`, `tidb`
- Topic Tags: `placement`, `placement-policy`, `syntax`, `examples`, `mysql-compatibility`, `scheduling-state`, `pd`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0667_6fd98e7464`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-placement.md#show-placement`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0a1298716c3c231b742919f5c79eaa41f09f711b3da312bd208ba05373591fa0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-placement#show-placement
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-placement.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the syntax, result fields, examples, or scheduling state meanings of the `SHOW PLACEMENT` SQL statement in TiDB.
- Retrieval Keywords: SHOW PLACEMENT, ShowStmt ::= "SHOW" "PLACEMENT" ShowLikeOrWhere?, Scheduling_State, PENDING, INPROGRESS, SCHEDULED, Placement Driver (PD), placement policies, canonical form, CREATE PLACEMENT POLICY, PRIMARY_REGION, REGIONS, FOLLOWERS, SHOW PLACEMENT FOR, TiDB extension to MySQL syntax
- Follow-up Guidance: Related official entries are `SHOW PLACEMENT FOR`, `CREATE PLACEMENT POLICY`, and Placement Rules in SQL.
- Classification Note: This is reference content because it defines `SHOW PLACEMENT` syntax, explains the `Scheduling_State` result field, and shows example output for placement policy information.

## Official Source Content

# SHOW PLACEMENT

`SHOW PLACEMENT` summarizes all placement options from placement policies, and presents them in canonical form.

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

The statement returns a result set in which the `Scheduling_State` field indicates the current progress that the Placement Driver (PD) has made in scheduling the placement:

* `PENDING`: The PD has not yet started scheduling the placement. This might indicate that the placement rules are semantically correct, but cannot currently be satisfied by the cluster. For example, if `FOLLOWERS=4` but there are only 3 TiKV stores which are candidates for followers.
* `INPROGRESS`: The PD is currently scheduling the placement.
* `SCHEDULED`: The PD has successfully scheduled the placement.
## Synopsis

```ebnf+diagram
ShowStmt ::=
    "SHOW" "PLACEMENT" ShowLikeOrWhere?
```
## Examples

```sql
CREATE PLACEMENT POLICY p1 PRIMARY_REGION="us-east-1" REGIONS="us-east-1,us-west-1" FOLLOWERS=4;
CREATE TABLE t1 (a INT) PLACEMENT POLICY=p1;
SHOW PLACEMENT;
```

```
Query OK, 0 rows affected (0.01 sec)

Query OK, 0 rows affected (0.00 sec)

+---------------+----------------------------------------------------------------------+------------------+
| Target        | Placement                                                            | Scheduling_State |
+---------------+----------------------------------------------------------------------+------------------+
| POLICY p1     | PRIMARY_REGION="us-east-1" REGIONS="us-east-1,us-west-1" FOLLOWERS=4 | NULL             |
| DATABASE test | PRIMARY_REGION="us-east-1" REGIONS="us-east-1,us-west-1" FOLLOWERS=4 | INPROGRESS       |
| TABLE test.t1 | PRIMARY_REGION="us-east-1" REGIONS="us-east-1,us-west-1" FOLLOWERS=4 | INPROGRESS       |
+---------------+----------------------------------------------------------------------+------------------+
4 rows in set (0.00 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [Placement Rules in SQL](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql)
* [SHOW PLACEMENT FOR](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-placement-for)
* [CREATE PLACEMENT POLICY](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-placement-policy)
