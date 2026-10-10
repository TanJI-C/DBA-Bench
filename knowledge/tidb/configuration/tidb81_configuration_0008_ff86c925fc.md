# Expression pushdown blocklist schema and operations

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/blocklist-control-plan.md`
- Source Title: `The Blocklist of Optimization Rules and Expression Pushdown`
- Source Heading Path: `The Blocklist of Optimization Rules and Expression Pushdown > The blocklist of expression pushdown | The Blocklist of Optimization Rules and Expression Pushdown > The blocklist of expression pushdown > Expressions that are supported to be pushed down | The Blocklist of Optimization Rules and Expression Pushdown > The blocklist of expression pushdown > Disable the pushdown of specific expressions | The Blocklist of Optimization Rules and Expression Pushdown > The blocklist of expression pushdown > Usage | The Blocklist of Optimization Rules and Expression Pushdown > The blocklist of expression pushdown > Usage > Add to the blocklist | The Blocklist of Optimization Rules and Expression Pushdown > The blocklist of expression pushdown > Remove from the blocklist`
- Source Line Ranges: `75-138`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `tiflash`, `sql`
- Topic Tags: `expression-pushdown`, `blocklist`, `functions`, `operators`, `mysql-system-table`, `admin-reload`, `tikv`, `tiflash`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0008_ff86c925fc`
- Source ID: `tidb-docs-8.1:blocklist-control-plan.md#the-blocklist-of-expression-pushdown`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0989ba5914d17ce22c00dc9b36875ceeb53a01976fbbfbc4b44382ee930fd545`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/blocklist-control-plan#the-blocklist-of-expression-pushdown
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/blocklist-control-plan.md

## Retrieval Guidance

- Use When: Use this chunk when searching how to block specific expression pushdown targets by editing the expression pushdown blocklist table and reloading it.
- Retrieval Keywords: mysql.expr_pushdown_blacklist, admin reload expr_pushdown_blacklist, DESC mysql.expr_pushdown_blacklist, store_type, tikv, tiflash, tidb, reason, supported expressions for pushdown to TiKV, disable the pushdown of specific expressions, wrong results due to the expression pushdown
- Follow-up Guidance: The source describes adding or deleting function or operator names together with `store_type` values in `mysql.expr_pushdown_blacklist`, then executing `admin reload expr_pushdown_blacklist`; the reload only affects the TiDB server where it is run.
- Classification Note: This is classified as configuration because the content defines the schema and operational use of the `mysql.expr_pushdown_blacklist` system table and reload command to control pushdown behavior.

## Official Source Content

## The blocklist of expression pushdown

The blocklist of expression pushdown is one way to tune the expression pushdown, mainly used to manually disable some expressions of some specific data types.
### Expressions that are supported to be pushed down

For more information about the expressions that are supported to be pushed down, see [Supported expressions for pushdown to TiKV](https://docs.pingcap.com/tidb/stable/functions-and-operators/expressions-pushed-down#supported-expressions-for-pushdown-to-tikv).
### Disable the pushdown of specific expressions

When you get wrong results due to the expression pushdown, you can use the blocklist to make a quick recovery for the application. More specifically, you can add some of the supported functions or operators to the `mysql.expr_pushdown_blacklist` table to disable the pushdown of specific expressions.

The schema of `mysql.expr_pushdown_blacklist` is shown as follows:

```sql
DESC mysql.expr_pushdown_blacklist;
```

```sql
+------------+--------------+------+------+-------------------+-------+
| Field      | Type         | Null | Key  | Default           | Extra |
+------------+--------------+------+------+-------------------+-------+
| name       | char(100)    | NO   |      | NULL              |       |
| store_type | char(100)    | NO   |      | tikv,tiflash,tidb |       |
| reason     | varchar(200) | YES  |      | NULL              |       |
+------------+--------------+------+------+-------------------+-------+
3 rows in set (0.00 sec)
```

Here is the description of each field above:

+ `name`: The name of the function that is disabled to be pushed down.
+ `store_type`: To specify the component that you want to prevent the function from being pushed down to for computing. Available components are `tidb`, `tikv`, and `tiflash`. The `store_type` is case-insensitive. If you need to specify multiple components, use a comma to separate each component.
    - When `store_type` is `tidb`, it indicates whether the function can be executed in other TiDB servers while the TiDB memory table is being read.
    - When `store_type` is `tikv`, it indicates whether the function can be executed in TiKV server's Coprocessor component.
    - When `store_type` is `tiflash`, it indicates whether the function can be executed in TiFlash Server's Coprocessor component.
+ `reason`: To record the reason why this function is added to the blocklist.
### Usage

This section describes how to use the blocklist of expression pushdown.
#### Add to the blocklist

To add one or more expressions (functions or operators) to the blocklist, perform the following steps:

1. Insert the corresponding function name or operator name, and the set of components you want to disable the pushdown, to the `mysql.expr_pushdown_blacklist` table.

2. Execute `admin reload expr_pushdown_blacklist`.
### Remove from the blocklist

To remove one or more expressions from the blocklist, perform the following steps:

1. Delete the corresponding function name or operator name, and the set of components you want to disable the pushdown, from the `mysql.expr_pushdown_blacklist` table.

2. Execute `admin reload expr_pushdown_blacklist`.

> **Note:**
>
> `admin reload expr_pushdown_blacklist` only takes effect on the TiDB server where this statement is run. If you want all TiDB servers of the cluster to take effect, run this command on each TiDB server.
