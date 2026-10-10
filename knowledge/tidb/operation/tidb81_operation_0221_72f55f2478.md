# Remove, change, and view SQL bindings

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-plan-management.md`
- Source Title: `SQL Plan Management (SPM)`
- Source Heading Path: `SQL Plan Management (SPM) > SQL binding > Remove a binding | SQL Plan Management (SPM) > SQL binding > Remove a binding > Remove a binding according to a SQL statement | SQL Plan Management (SPM) > SQL binding > Remove a binding > Remove a binding according to `sql_digest` | SQL Plan Management (SPM) > SQL binding > Change binding status | SQL Plan Management (SPM) > SQL binding > Change binding status > Change binding status according to a SQL statement | SQL Plan Management (SPM) > SQL binding > Change binding status > Change binding status according to `sql_digest` | SQL Plan Management (SPM) > SQL binding > View bindings`
- Source Line Ranges: `311-400`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `sql-binding`, `drop-binding`, `sql-digest`, `binding-status`, `show-bindings`, `global-binding`, `session-binding`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0221_72f55f2478`
- Source ID: `tidb-docs-8.1:sql-plan-management.md#remove-a-binding`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `300824846dfc969d22858e2c5e1410cb2a1f3a95068583ee379097f8f110beaa`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-plan-management#remove-a-binding
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-plan-management.md

## Retrieval Guidance

- Use When: Use this chunk when you need SQL syntax and behavior for removing bindings, changing binding status, or listing bindings by SQL statement or `sql_digest`.
- Retrieval Keywords: DROP [GLOBAL | SESSION] BINDING FOR BindableStmt, DROP [GLOBAL | SESSION] BINDING FOR SQL DIGEST, SET BINDING ENABLED FOR, SET BINDING DISABLED FOR, SET BINDING [ENABLED | DISABLED] FOR SQL DIGEST, SHOW [GLOBAL | SESSION] BINDINGS, sql_digest, binding status, deleted, disabled, pending verify, source manual, source history, source capture, source evolve
- Follow-up Guidance: It also describes SESSION versus GLOBAL scope behavior, warning messages for missing bindings, and the 11 output columns of `SHOW BINDINGS` including `status`, `source`, `sql_digest`, and `plan_digest`.
- Classification Note: This is classified as an operation because the content defines executable SQL statements and their effects for deleting, enabling, disabling, and viewing SQL bindings in TiDB.

## Official Source Content

### Remove a binding

You can remove a binding according to a SQL statement or `sql_digest`.
#### Remove a binding according to a SQL statement

```sql
DROP [GLOBAL | SESSION] BINDING FOR BindableStmt;
```

This statement removes a specified execution plan binding at the GLOBAL or SESSION level. The default scope is SESSION.

Generally, the binding in the SESSION scope is mainly used for test or in special situations. For a binding to take effect in all TiDB processes, you need to use the GLOBAL binding. A created SESSION binding shields the corresponding GLOBAL binding until the end of the SESSION, even if the SESSION binding is dropped before the session closes. In this case, no binding takes effect and the plan is selected by the optimizer.

The following example is based on the example in [create binding](#create-a-binding) in which the SESSION binding shields the GLOBAL binding:

```sql
-- Drops the binding created in the SESSION scope.
drop session binding for SELECT * FROM t1, t2 WHERE t1.id = t2.id;

-- Views the SQL execution plan again.
explain SELECT * FROM t1,t2 WHERE t1.id = t2.id;
```

In the example above, the dropped binding in the SESSION scope shields the corresponding binding in the GLOBAL scope. The optimizer does not add the `sm_join(t1, t2)` hint to the statement. The top node of the execution plan in the `explain` result is not fixed to MergeJoin by this hint. Instead, the top node is independently selected by the optimizer according to the cost estimation.
#### Remove a binding according to `sql_digest`

In addition to removing a binding according to a SQL statement, you can also remove a binding according to `sql_digest`.

```sql
DROP [GLOBAL | SESSION] BINDING FOR SQL DIGEST 'sql_digest';
```

This statement removes an execution plan binding corresponding to `sql_digest` at the GLOBAL or SESSION level. The default scope is SESSION. You can get the `sql_digest` by [viewing bindings](#view-bindings).

> **Note:**
>
> Executing `DROP GLOBAL BINDING` drops the binding in the current tidb-server instance cache and changes the status of the corresponding row in the system table to 'deleted'. This statement does not directly delete the records in the system table, because other tidb-server instances need to read the 'deleted' status to drop the corresponding binding in their cache. For the records in these system tables with the status of 'deleted', at every 100 `bind-info-lease` (the default value is `3s`, and `300s` in total) interval, the background thread triggers an operation of reclaiming and clearing on the bindings of `update_time` before 10 `bind-info-lease` (to ensure that all tidb-server instances have read the 'deleted' status and updated the cache).
### Change binding status
#### Change binding status according to a SQL statement

```sql
SET BINDING [ENABLED | DISABLED] FOR BindableStmt;
```

You can execute this statement to change the status of a binding. The default status is ENABLED. The effective scope is GLOBAL by default and cannot be modified.

When executing this statement, you can only change the status of a binding from `Disabled` to `Enabled` or from `Enabled` to `Disabled`. If no binding is available for status changes, a warning message is returned, saying `There are no bindings can be set the status. Please check the SQL text`. Note that a binding in `Disabled` status is not used by any query.
#### Change binding status according to `sql_digest`

In addition to changing the binding status according to a SQL statement, you can also change the binding status according to `sql_digest`:

```sql
SET BINDING [ENABLED | DISABLED] FOR SQL DIGEST 'sql_digest';
```

The binding status that can be changed by `sql_digest` and the effect is the same as those changed [according to a SQL statement](#change-binding-status-according-to-a-sql-statement). If no binding is available for status changes, a warning message `can't find any binding for 'sql_digest'` is returned.
### View bindings

```sql
SHOW [GLOBAL | SESSION] BINDINGS [ShowLikeOrWhere]
```

This statement outputs the execution plan bindings at the GLOBAL or SESSION level according to the order of binding update time from the latest to earliest. The default scope is SESSION. Currently `SHOW BINDINGS` outputs 11 columns, as shown below:

| Column Name | Note |
| :-------- | :------------- |
| original_sql  |  Original SQL statement after parameterization |
| bind_sql | Bound SQL statement with hints |
| default_db | Default database |
| status | Status including `enabled` (replacing the `using` status from v6.0), `disabled`, `deleted`, `invalid`, `rejected`, and `pending verify`|
| create_time | Creating time |
| update_time | Updating time |
| charset | Character set |
| collation | Ordering rule |
| source | The way in which a binding is created, including `manual` (created according to a SQL statement), `history` (created according to a historical execution plan), `capture` (captured automatically by TiDB), and `evolve` (evolved automatically by TiDB) |
| sql_digest | Digest of a normalized SQL statement |
| plan_digest | Digest of an execution plan |
