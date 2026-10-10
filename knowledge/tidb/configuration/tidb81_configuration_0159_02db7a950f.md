# Sharding scenario data check configuration examples

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sync-diff-inspector/shard-diff.md`
- Source Title: `Data Check in the Sharding Scenario`
- Source Heading Path: `Data Check in the Sharding Scenario | Data Check in the Sharding Scenario > Note`
- Source Line Ranges: `5-136`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`, `shared`
- Topic Tags: `sharding`, `data-check`, `sync-diff-inspector`, `route-rules`, `table-rules`, `datasource-config`, `target-check-tables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0159_02db7a950f`
- Source ID: `tidb-docs-8.1:sync-diff-inspector/shard-diff.md#data-check-in-the-sharding-scenario`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e6d9824131daf0858cae9e7244994f659d46e2e428c09a41c0f8cda04511eeb0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sync-diff-inspector/shard-diff#data-check-in-the-sharding-scenario
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sync-diff-inspector/shard-diff.md

## Retrieval Guidance

- Use When: Use this chunk when looking for sync-diff-inspector configuration examples for checking sharded upstream MySQL data replicated by DM into TiDB, including route-rules, table-pattern matching, and target-check-tables mapping to a downstream table.
- Retrieval Keywords: sync-diff-inspector, Data Check in the Sharding Scenario, TiDB Data Migration, DM, Datasource config, route-rules, table-rules, data-sources.mysql1, data-sources.mysql2, data-sources.tidb0, routes.rule1, routes.rule2, schema-pattern, table-pattern, target-schema, target-table, target-check-tables, source-instances, target-instance, test.table-0, table-0, table-*, table-[1-2], table-3, export-fix-sql, check-thread-count, check-struct-only
- Follow-up Guidance: The note states that if `test.table-0` exists in the upstream database, the downstream database also compares this table.
- Classification Note: This is classified as configuration because the content provides complete TOML examples for sharding data check, including global settings, datasource definitions, route rules, and task fields such as `target-check-tables`.

## Official Source Content

# Data Check in the Sharding Scenario

sync-diff-inspector supports data check in the sharding scenario. Assume that you use the [TiDB Data Migration](https://docs.pingcap.com/tidb/stable/dm/dm-overview) tool to replicate data from multiple MySQL instances into TiDB, you can use sync-diff-inspector to check upstream and downstream data.

For scenarios where the number of upstream sharded tables is small and the naming rules of sharded tables do not have a pattern as shown below, you can use `Datasource config` to configure `table-0`, set corresponding `rules` and configure the tables that have the mapping relationship between the upstream and downstream databases. This configuration method requires setting all sharded tables.

![shard-table-replica-1](/media/shard-table-replica-1.png)

Below is a complete example of the sync-diff-inspector configuration.

``` toml
# Diff Configuration.

######################### Global config #########################

# The number of goroutines created to check data. The number of connections between upstream and downstream databases are slightly greater than this value
check-thread-count = 4

# If enabled, SQL statements is exported to fix inconsistent tables
export-fix-sql = true

# Only compares the table structure instead of the data
check-struct-only = false

######################### Datasource config #########################
[data-sources.mysql1]
    host = "127.0.0.1"
    port = 3306
    user = "root"
    password = ""

    route-rules = ["rule1"]

[data-sources.mysql2]
    host = "127.0.0.1"
    port = 3306
    user = "root"
    password = ""

    route-rules = ["rule2"]

[data-sources.tidb0]
    host = "127.0.0.1"
    port = 4000
    user = "root"
    password = ""

########################### Routes ###########################
[routes.rule1]
schema-pattern = "test"        # Matches the schema name of the data source. Supports the wildcards "*" and "?"
table-pattern = "table-[1-2]"  # Matches the table name of the data source. Supports the wildcards "*" and "?"
target-schema = "test"         # The name of the schema in the target database
target-table = "table-0"       # The name of the target table

[routes.rule2]
schema-pattern = "test"      # Matches the schema name of the data source. Supports the wildcards "*" and "?"
table-pattern = "table-3"    # Matches the table name of the data source. Supports the wildcards "*" and "?"
target-schema = "test"       # The name of the schema in the target database
target-table = "table-0"     # The name of the target table

######################### Task config #########################
[task]
    output-dir = "./output"

    source-instances = ["mysql1", "mysql2"]

    target-instance = "tidb0"

    # The tables of downstream databases to be compared. Each table needs to contain the schema name and the table name, separated by '.'
    target-check-tables = ["test.table-0"]
```

You can use `table-rules` for configuration when there are a large number of upstream sharded tables and the naming rules of all sharded tables have a pattern, as shown below:

![shard-table-replica-2](/media/shard-table-replica-2.png)

Below is a complete example of the sync-diff-inspector configuration.

```toml
# Diff Configuration.
######################### Global config #########################

# The number of goroutines created to check data. The number of connections between upstream and downstream databases are slightly greater than this value.
check-thread-count = 4

# If enabled, SQL statements is exported to fix inconsistent tables.
export-fix-sql = true

# Only compares the table structure instead of the data.
check-struct-only = false

######################### Datasource config #########################
[data-sources.mysql1]
    host = "127.0.0.1"
    port = 3306
    user = "root"
    password = ""

[data-sources.mysql2]
    host = "127.0.0.1"
    port = 3306
    user = "root"
    password = ""

[data-sources.tidb0]
    host = "127.0.0.1"
    port = 4000
    user = "root"
    password = ""

########################### Routes ###########################
[routes.rule1]
schema-pattern = "test"      # Matches the schema name of the data source. Supports the wildcards "*" and "?"
table-pattern = "table-*"    # Matches the table name of the data source. Supports the wildcards "*" and "?"
target-schema = "test"       # The name of the schema in the target database
target-table = "table-0"     # The name of the target table

######################### Task config #########################
[task]
    output-dir = "./output"
    source-instances = ["mysql1", "mysql2"]

    target-instance = "tidb0"

    # The tables of downstream databases to be compared. Each table needs to contain the schema name and the table name, separated by '.'
    target-check-tables = ["test.table-0"]
```
## Note

If `test.table-0` exists in the upstream database, the downstream database also compares this table.
