# PPD case: predicates with user variables are not pushed down

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/predicate-push-down.md`
- Source Title: `Predicates Push Down`
- Source Heading Path: `Predicates Push Down (PPD) > Examples > Case 6: the predicates which contain user variables cannot be pushed down`
- Source Line Ranges: `114-150`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`
- Topic Tags: `predicate-push-down`, `user-variables`, `explain`, `query-optimization`, `storage-layer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0483_99cdaa679d`
- Source ID: `tidb-docs-8.1:predicate-push-down.md#case-6-the-predicates-which-contain-user-variables-cannot-be-pushed-down`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `399669762dc8d4b9924f068f39a13049c784114beffd2e8bab6aa39dc4d395da`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/predicate-push-down#case-6-the-predicates-which-contain-user-variables-cannot-be-pushed-down
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/predicate-push-down.md

## Retrieval Guidance

- Use When: Use this chunk when explaining why a predicate containing a user variable such as `a < @a` or `a = @a` is not pushed down in TiDB and how `EXPLAIN` shows the predicate staying at the root instead of being pushed to TiKV.
- Retrieval Keywords: predicate push down, PPD, user variables, @a, a < @a, a = @a, EXPLAIN, Selection_5, TableReader_7, TableFullScan_6, cop[tikv], getvar("a"), TiKV, TiDB, predicates which contain user variables cannot be pushed down
- Follow-up Guidance: The source also provides an example with `select id, a, @a:=@a+1 from t where a = @a;` to show that the user variable value can change during query execution, so replacing it with a constant and pushing it down is not equivalent.
- Classification Note: This is a reference example because the official content demonstrates with SQL and `EXPLAIN` output that predicates containing user variables are kept in TiDB rather than pushed down to TiKV.

## Official Source Content

### Case 6: the predicates which contain user variables cannot be pushed down

```sql
create table t(id int primary key, a char);
set @a = 1;
explain select * from t where a < @a;
+-------------------------+----------+-----------+---------------+--------------------------------+
| id                      | estRows  | task      | access object | operator info                  |
+-------------------------+----------+-----------+---------------+--------------------------------+
| Selection_5             | 8000.00  | root      |               | lt(test.t.a, getvar("a"))      |
| └─TableReader_7         | 10000.00 | root      |               | data:TableFullScan_6           |
|   └─TableFullScan_6     | 10000.00 | cop[tikv] | table:t       | keep order:false, stats:pseudo |
+-------------------------+----------+-----------+---------------+--------------------------------+
3 rows in set (0.00 sec)
```

In this query, there is a predicate `a < @a` on table `t`. The `@a` of the predicate is a user variable.

As can be seen from `explain` results, the predicate is not like case 2, which is simplified to `a < 1` and pushed down to TiKV. This is because the value of the user variable `@a` may change during the computation, and TiKV is not aware of the changes. So TiDB does not replace `@a` with `1`, and does not push down it to TiKV.

An example to help you understand is as follows:

```sql
create table t(id int primary key, a int);
insert into t values(1, 1), (2,2);
set @a = 1;
select id, a, @a:=@a+1 from t where a = @a;
+----+------+----------+
| id | a    | @a:=@a+1 |
+----+------+----------+
|  1 |    1 | 2        |
|  2 |    2 | 3        |
+----+------+----------+
2 rows in set (0.00 sec)
```

As you can see from this query, the value of `@a` will change during the query. So if you replace `a = @a` with `a = 1` and push it down to TiKV, it's not an equivalent execution plan.
