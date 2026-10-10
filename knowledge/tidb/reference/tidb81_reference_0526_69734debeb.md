# ALTER RESOURCE GROUP syntax and options

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-alter-resource-group.md`
- Source Title: `ALTER RESOURCE GROUP`
- Source Heading Path: `ALTER RESOURCE GROUP | ALTER RESOURCE GROUP > Synopsis`
- Source Line Ranges: `5-92`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `resource-groups`, `syntax`, `request-unit`, `priority`, `burstable`, `query-limit`, `runaway-queries`, `background-tasks`, `resource-control`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0526_69734debeb`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-alter-resource-group.md#alter-resource-group`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7b3b7869f6e3529b869b6cd72209c7b4fd04691e69564c7755e8aa3b8c167feb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-resource-group#alter-resource-group
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-alter-resource-group.md

## Retrieval Guidance

- Use When: Use this chunk when you need the ALTER RESOURCE GROUP syntax, supported DirectResourceGroupOption values, or the documented constraints for QUERY_LIMIT, BACKGROUND, and tidb_enable_resource_control.
- Retrieval Keywords: ALTER RESOURCE GROUP, AlterResourceGroupStmt, RU_PER_SEC, PRIORITY, BURSTABLE, QUERY_LIMIT, BACKGROUND, EXEC_ELAPSED, ACTION, WATCH, EXACT, SIMILAR, DRYRUN, COOLDOWN, KILL, TASK_TYPES, tidb_enable_resource_control, Request Unit (RU), incremental changes, only the default resource group supports modifying the BACKGROUND configuration
- Follow-up Guidance: The source notes that ALTER RESOURCE GROUP can only be executed when tidb_enable_resource_control is ON, unspecified parameters remain unchanged, and QUERY_LIMIT and BACKGROUND cannot be partially modified.
- Classification Note: This is reference content because it defines the official statement grammar, option meanings, and usage notes for the SQL statement ALTER RESOURCE GROUP.

## Official Source Content

# ALTER RESOURCE GROUP

The `ALTER RESOURCE GROUP` statement is used to modify a resource group in a database.

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.
## Synopsis

```ebnf+diagram
AlterResourceGroupStmt ::=
   "ALTER" "RESOURCE" "GROUP" IfExists ResourceGroupName ResourceGroupOptionList

IfExists ::=
    ('IF' 'EXISTS')?

ResourceGroupName ::=
    Identifier
|   "DEFAULT"

ResourceGroupOptionList ::=
    DirectResourceGroupOption
|   ResourceGroupOptionList DirectResourceGroupOption
|   ResourceGroupOptionList ',' DirectResourceGroupOption

DirectResourceGroupOption ::=
    "RU_PER_SEC" EqOpt stringLit
|   "PRIORITY" EqOpt ResourceGroupPriorityOption
|   "BURSTABLE"
|   "BURSTABLE" EqOpt Boolean
|   "QUERY_LIMIT" EqOpt '(' ResourceGroupRunawayOptionList ')'
|   "QUERY_LIMIT" EqOpt '(' ')'
|   "QUERY_LIMIT" EqOpt "NULL"
|   "BACKGROUND" EqOpt '(' BackgroundOptionList ')'
|   "BACKGROUND" EqOpt '(' ')'
|   "BACKGROUND" EqOpt "NULL"

ResourceGroupPriorityOption ::=
    LOW
|   MEDIUM
|   HIGH

ResourceGroupRunawayOptionList ::=
    DirectResourceGroupRunawayOption
|   ResourceGroupRunawayOptionList DirectResourceGroupRunawayOption
|   ResourceGroupRunawayOptionList ',' DirectResourceGroupRunawayOption

DirectResourceGroupRunawayOption ::=
    "EXEC_ELAPSED" EqOpt stringLit
|   "ACTION" EqOpt ResourceGroupRunawayActionOption
|   "WATCH" EqOpt ResourceGroupRunawayWatchOption "DURATION" EqOpt stringLit

ResourceGroupRunawayWatchOption ::=
    EXACT
|   SIMILAR

ResourceGroupRunawayActionOption ::=
    DRYRUN
|   COOLDOWN
|   KILL

BackgroundOptionList ::=
    DirectBackgroundOption
|   BackgroundOptionList DirectBackgroundOption
|   BackgroundOptionList ',' DirectBackgroundOption

DirectBackgroundOption ::=
    "TASK_TYPES" EqOpt stringLit
```

TiDB supports the following `DirectResourceGroupOption`, where [Request Unit (RU)](https://docs.pingcap.com/tidb/stable/tidb-resource-control#what-is-request-unit-ru) is a unified abstraction unit in TiDB for CPU, IO, and other system resources.

| Option     | Description                         | Example                |
|---------------|-------------------------------------|------------------------|
| `RU_PER_SEC` | Rate of RU backfilling per second | `RU_PER_SEC = 500` indicates that this resource group is backfilled with 500 RUs per second |
| `PRIORITY`    | The absolute priority of tasks to be processed on TiKV  | `PRIORITY = HIGH` indicates that the priority is high. If not specified, the default value is `MEDIUM`. |
| `BURSTABLE`   | If the `BURSTABLE` attribute is set, TiDB allows the corresponding resource group to use the available system resources when the quota is exceeded. |
| `QUERY_LIMIT` | When the query execution meets this condition, the query is identified as a runaway query and the corresponding action is executed. | `QUERY_LIMIT=(EXEC_ELAPSED='60s', ACTION=KILL, WATCH=EXACT DURATION='10m')` indicates that the query is identified as a runaway query when the execution time exceeds 60 seconds. The query is terminated. All SQL statements with the same SQL text will be terminated immediately in the coming 10 minutes. `QUERY_LIMIT=()` or `QUERY_LIMIT=NULL` means that runaway control is not enabled. See [Runaway Queries](https://docs.pingcap.com/tidb/stable/tidb-resource-control#manage-queries-that-consume-more-resources-than-expected-runaway-queries). |
| `BACKGROUND`  | Configure the background tasks. For more details, see [Manage background tasks](https://docs.pingcap.com/tidb/stable/tidb-resource-control#manage-background-tasks). | `BACKGROUND=(TASK_TYPES="br,stats")` indicates that the backup and restore and statistics collection related tasks are scheduled as background tasks. |

> **Note:**
>
> - The `ALTER RESOURCE GROUP` statement can only be executed when the global variable [`tidb_enable_resource_control`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_resource_control-new-in-v660) is set to `ON`.
> - The `ALTER RESOURCE GROUP` statement supports incremental changes, leaving unspecified parameters unchanged. However, both `QUERY_LIMIT` and `BACKGROUND` are used as a whole and cannot be partially modified.
> - Currently, only the `default` resource group supports modifying the `BACKGROUND` configuration.
