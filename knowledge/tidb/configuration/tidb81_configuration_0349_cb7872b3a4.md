# Runaway query management and watch list configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-resource-control.md`
- Source Title: `Use Resource Control to Achieve Resource Isolation`
- Source Heading Path: `Use Resource Control to Achieve Resource Isolation > How to use resource control > Manage queries that consume more resources than expected (Runaway Queries) | Use Resource Control to Achieve Resource Isolation > How to use resource control > Manage queries that consume more resources than expected (Runaway Queries) > `QUERY_LIMIT` parameters | Use Resource Control to Achieve Resource Isolation > How to use resource control > Manage queries that consume more resources than expected (Runaway Queries) > Examples | Use Resource Control to Achieve Resource Isolation > How to use resource control > Manage queries that consume more resources than expected (Runaway Queries) > `QUERY WATCH` parameters | Use Resource Control to Achieve Resource Isolation > How to use resource control > Manage queries that consume more resources than expected (Runaway Queries) > Observability`
- Source Line Ranges: `259-396`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `resource-control`, `runaway-queries`, `query-limit`, `query-watch`, `resource-groups`, `observability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0349_cb7872b3a4`
- Source ID: `tidb-docs-8.1:tidb-resource-control.md#manage-queries-that-consume-more-resources-than-expected-runaway-queries`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8dacfea622f6c99ec1d54167da74b146ca372bdc7cb76b3a59e06ac44de76a6c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-resource-control#manage-queries-that-consume-more-resources-than-expected-runaway-queries
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-resource-control.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how TiDB resource control defines and handles runaway queries, including QUERY_LIMIT, WATCH matching, QUERY WATCH statements, errors, and observability tables.
- Retrieval Keywords: runaway query, QUERY_LIMIT, CREATE RESOURCE GROUP, ALTER RESOURCE GROUP, EXEC_ELAPSED, ACTION=DRYRUN, ACTION=COOLDOWN, ACTION=KILL, WATCH=SIMILAR, WATCH=EXACT, WATCH=PLAN, DURATION, QUERY WATCH, QUERY WATCH ADD, QUERY WATCH REMOVE, SQL DIGEST, PLAN DIGEST, SQL TEXT, INFORMATION_SCHEMA.RUNAWAY_WATCHES, information_schema.runaway_watches, mysql.tidb_runaway_queries, Query execution was interrupted, identified as runaway query, Quarantined and interrupted because of being in runaway watch list, match_type identify, match_type watch
- Follow-up Guidance: The source also shows example SQL for CREATE RESOURCE GROUP, ALTER RESOURCE GROUP, QUERY WATCH ADD, querying information_schema.runaway_watches, and QUERY WATCH REMOVE.
- Classification Note: The official content is classified as configuration because it explains runaway query management through resource group settings such as QUERY_LIMIT and manual QUERY WATCH rules in TiDB.

## Official Source Content

### Manage queries that consume more resources than expected (Runaway Queries)

A runaway query is a query (`SELECT` statement only) that consumes more time or resources than expected. The term **runaway queries** is used in the following to describe the feature of managing the runaway query.

- Starting from v7.2.0, the resource control feature introduces the management of runaway queries. You can set criteria for a resource group to identify runaway queries and automatically take actions to prevent them from exhausting resources and affecting other queries. You can manage runaway queries for a resource group by including the `QUERY_LIMIT` field in [`CREATE RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-resource-group) or [`ALTER RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-resource-group).
- Starting from v7.3.0, the resource control feature introduces manual management of runaway watches, enabling quick identification of runaway queries for a given SQL statement or Digest. You can execute the statement [`QUERY WATCH`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-query-watch) to manually manage the runaway queries watch list in the resource group.
#### `QUERY_LIMIT` parameters

Supported condition setting:

- `EXEC_ELAPSED`: a query is identified as a runaway query when the query execution time exceeds this limit.

Supported operations (`ACTION`):

- `DRYRUN`: no action is taken. The records are appended for the runaway queries. This is mainly used to observe whether the condition setting is reasonable.
- `COOLDOWN`: the execution priority of the query is lowered to the lowest level. The query continues to execute with the lowest priority and does not occupy resources of other operations.
- `KILL`: the identified query is automatically terminated and reports an error `Query execution was interrupted, identified as runaway query`.

To avoid too many concurrent runaway queries that exhaust system resources, the resource control feature introduces a quick identification mechanism, which can quickly identify and isolate runaway queries. You can use this feature through the `WATCH` clause. When a query is identified as a runaway query, this mechanism extracts the matching feature (defined by the parameter after `WATCH`) of the query. In the next period of time (defined by `DURATION`), the matching feature of the runaway query is added to the watch list, and the TiDB instance matches queries with the watch list. The matching queries are directly marked as runaway queries and isolated according to the corresponding action, instead of waiting for them to be identified by conditions. The `KILL` operation terminates the query and reports an error `Quarantined and interrupted because of being in runaway watch list`.

There are three methods for `WATCH` to match for quick identification:

- `EXACT` indicates that only SQL statements with exactly the same SQL text are quickly identified.
- `SIMILAR` indicates all SQL statements with the same pattern are matched by SQL Digest, and the literal values are ignored.
- `PLAN` indicates all SQL statements with the same pattern are matched by Plan Digest.

The `DURATION` option in `WATCH` indicates the duration of the identification item, which is infinite by default.

After a watch item is added, neither the matching feature nor the `ACTION` is changed or deleted whenever the `QUERY_LIMIT` configuration is changed or deleted. You can use `QUERY WATCH REMOVE` to remove a watch item.

The parameters of `QUERY_LIMIT` are as follows:

| Parameter          | Description            | Note                                  |
|---------------|--------------|--------------------------------------|
| `EXEC_ELAPSED`  | When the query execution time exceeds this value, it is identified as a runaway query | EXEC_ELAPSED =`60s` means the query is identified as a runaway query if it takes more than 60 seconds to execute. |
| `ACTION`    | Action taken when a runaway query is identified | The optional values are `DRYRUN`, `COOLDOWN`, and `KILL`. |
| `WATCH`   | Quickly match the identified runaway query. If the same or similar query is encountered again within a certain period of time, the corresponding action is performed immediately. | Optional. For example, `WATCH=SIMILAR DURATION '60s'`, `WATCH=EXACT DURATION '1m'`, and `WATCH=PLAN`. |
#### Examples

1. Create a resource group `rg1` with a quota of 500 RUs per second, and define a runaway query as one that exceeds 60 seconds, and lower the priority of the runaway query.

    ```sql
    CREATE RESOURCE GROUP IF NOT EXISTS rg1 RU_PER_SEC = 500 QUERY_LIMIT=(EXEC_ELAPSED='60s', ACTION=COOLDOWN);
    ```

2. Change the `rg1` resource group to terminate the runaway queries, and mark the queries with the same pattern as runaway queries immediately in the next 10 minutes.

    ```sql
    ALTER RESOURCE GROUP rg1 QUERY_LIMIT=(EXEC_ELAPSED='60s', ACTION=KILL, WATCH=SIMILAR DURATION='10m');
    ```

3. Change the `rg1` resource group to cancel the runaway query check.

    ```sql
    ALTER RESOURCE GROUP rg1 QUERY_LIMIT=NULL;
    ```
#### `QUERY WATCH` parameters

For more information about the synopsis of `QUERY WATCH`, see [`QUERY WATCH`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-query-watch).

The parameters are as follows:

- The `RESOURCE GROUP` specifies a resource group. The matching features of runaway queries added by this statement are added to the watch list of the resource group. This parameter can be omitted. If omitted, it applies to the `default` resource group.
- The meaning of `ACTION` is the same as `QUERY LIMIT`. This parameter can be omitted. If omitted, the corresponding action after identification adopts the `ACTION` configured by `QUERY LIMIT` in the resource group, and the action does not change with the `QUERY LIMIT` configuration. If there is no `ACTION` configured in the resource group, an error is reported.
- The `QueryWatchTextOption` parameter has three options: `SQL DIGEST`, `PLAN DIGEST`, and `SQL TEXT`.
    - `SQL DIGEST` is the same as that of `SIMILAR`. The following parameters accept strings, user-defined variables, or other expressions that yield string result. The string length must be 64, which is the same as the Digest definition in TiDB.
    - `PLAN DIGEST` is the same as `PLAN`. The following parameter is a Digest string.
    - `SQL TEXT` matches the input SQL as a raw string (`EXACT`), or parses and compiles it into `SQL DIGEST` (`SIMILAR`) or `PLAN DIGEST` (`PLAN`), depending on the following parameter.

- Add a matching feature to the runaway query watch list for the default resource group (you need to set `QUERY LIMIT` for the default resource group in advance).

    ```sql
    QUERY WATCH ADD ACTION KILL SQL TEXT EXACT TO 'select * from test.t2';
    ```

- Add a matching feature to the runaway query watch list for the `rg1` resource group by parsing the SQL into SQL Digest. When `ACTION` is not specified, the `ACTION` option already configured for the `rg1` resource group is used.

    ```sql
    QUERY WATCH ADD RESOURCE GROUP rg1 SQL TEXT SIMILAR TO 'select * from test.t2';
    ```

- Add a matching feature to the runaway query watch list for the `rg1` resource group using `PLAN DIGEST`.

    ```sql
    QUERY WATCH ADD RESOURCE GROUP rg1 ACTION KILL PLAN DIGEST 'd08bc323a934c39dc41948b0a073725be3398479b6fa4f6dd1db2a9b115f7f57';
    ```

- Get the watch item ID by querying `INFORMATION_SCHEMA.RUNAWAY_WATCHES` and delete the watch item.

    ```sql
    SELECT * from information_schema.runaway_watches ORDER BY id;
    ```

    ```sql
    *************************** 1. row ***************************
                    ID: 20003
    RESOURCE_GROUP_NAME: rg2
            START_TIME: 2023-07-28 13:06:08
            END_TIME: UNLIMITED
                WATCH: Similar
            WATCH_TEXT: 5b7fd445c5756a16f910192ad449c02348656a5e9d2aa61615e6049afbc4a82e
                SOURCE: 127.0.0.1:4000
                ACTION: Kill
    1 row in set (0.00 sec)
    ```

    ```sql
    QUERY WATCH REMOVE 20003;
    ```
#### Observability

You can get more information about runaway queries from the following system tables and `INFORMATION_SCHEMA`:

+ The `mysql.tidb_runaway_queries` table contains the history records of all runaway queries identified in the past 7 days. Take one of the rows as an example:

    ```sql
    MySQL [(none)]> SELECT * FROM mysql.tidb_runaway_queries LIMIT 1\G
    *************************** 1. row ***************************
    resource_group_name: rg1
                   time: 2023-06-16 17:40:22
             match_type: identify
                 action: kill
           original_sql: select * from sbtest.sbtest1
            plan_digest: 5b7d445c5756a16f910192ad449c02348656a5e9d2aa61615e6049afbc4a82e
            tidb_server: 127.0.0.1:4000
    ```

    In the preceding output,`match_type` indicates how the runaway query is identified. The value can be one of the following:

    - `identify` means that it matches the condition of the runaway query.
    - `watch` means that it matches the quick identification rule in the watch list.

+ The `information_schema.runaway_watches` table contains records of quick identification rules for runaway queries. For more information, see [`RUNAWAY_WATCHES`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-runaway-watches).
