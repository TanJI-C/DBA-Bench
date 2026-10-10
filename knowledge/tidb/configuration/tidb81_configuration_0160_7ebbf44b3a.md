# Configuration file structure and complete example

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sync-diff-inspector/sync-diff-inspector-overview.md`
- Source Title: `sync-diff-inspector User Guide`
- Source Heading Path: `sync-diff-inspector User Guide > Configuration file description`
- Source Line Ranges: `51-166`
- Source Scope: `shared`
- Primary Component: `ecosystem`
- Related Components: `ticdc`, `tidb`
- Topic Tags: `configuration`, `toml`, `datasources`, `routes`, `tasks`, `table-configs`, `tls`, `snapshot`, `chunks`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0160_7ebbf44b3a`
- Source ID: `tidb-docs-8.1:sync-diff-inspector/sync-diff-inspector-overview.md#configuration-file-description`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a322d759522a75e9582fb7afa273a67bc5fd1a2ce857f5957b43666549b9f430`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview#configuration-file-description
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sync-diff-inspector/sync-diff-inspector-overview.md

## Retrieval Guidance

- Use When: Use this when you need the TOML configuration structure or a complete example for global config, data sources, routes, task config, and table-specific settings in sync-diff-inspector.
- Retrieval Keywords: Configuration file description, check-thread-count, export-fix-sql, check-data-only, check-struct-only, skip-non-existing-table, data-sources, route-rules, security.ca-path, security.cert-path, security.key-path, snapshot, snapshot = "auto", routes, schema-pattern, table-pattern, target-schema, target-table, task, output-dir, source-instances, target-instance, target-check-tables, target-configs, table-configs, target-tables, range, index-fields, ignore-columns, chunk-size, collation
- Follow-up Guidance: The example explains that `output-dir` contains SQL repair files, `sync-diff.log`, `summary.txt`, and a checkpoint directory.
- Classification Note: This is configuration content because it defines the available configuration sections, field names, and example values for sync-diff-inspector.

## Official Source Content

## Configuration file description

The configuration of sync-diff-inspector consists of the following parts:

- `Global config`: General configurations, such as number of threads to check, whether to export SQL statement to fix inconsistent tables, whether to compare the data, and whether to skip checking tables that do not exist in the upstream or downstream.
- `Databases config`: Configures the instances of the upstream and downstream databases.
- `Routes`: Rules for upstream multiple schema names to match downstream single schema names **(optional)**.
- `Task config`: Configures the tables for checking. If some tables have a certain mapping relationship between the upstream and downstream databases or have some special requirements, you must configure these tables.
- `Table config`: Special configurations for specific tables, such as specified ranges and columns to be ignored **(optional)**.

Below is the description of a complete configuration file:

- Note: configurations with `s` after their name can have multiple values, so you need to use square brackets `[]` to contain the configuration values.

``` toml
# Diff Configuration.

######################### Global config #########################
# The number of goroutines created to check data. The number of connections between sync-diff-inspector and upstream/downstream databases is slightly greater than this value.
check-thread-count = 4

# If enabled, SQL statements is exported to fix inconsistent tables.
export-fix-sql = true

# Only compares the data instead of the table structure. This configuration item is an experimental feature. It is not recommended that you use it in the production environment.
check-data-only = false

# Only compares the table structure instead of the data.
check-struct-only = false

# If enabled, sync-diff-inspector skips checking tables that do not exist in the upstream or downstream.
skip-non-existing-table = false

######################### Datasource config #########################
[data-sources]
[data-sources.mysql1] # mysql1 is the only custom ID for the database instance. It is used for the following `task.source-instances/task.target-instance` configuration.
    host = "127.0.0.1"
    port = 3306
    user = "root"
    password = ""  # The password for connecting to the upstream database. It can be plain text or Base64-encoded.

    # (optional) Use mapping rules to match multiple upstream sharded tables. Rule1 and rule2 are configured in the following Routes section.
    route-rules = ["rule1", "rule2"]

[data-sources.tidb0]
    host = "127.0.0.1"
    port = 4000
    user = "root"
    password = ""  # The password for connecting to the downstream database. It can be plain text or Base64-encoded.

    # (optional) Use TLS to connect TiDB.
    # security.ca-path = ".../ca.crt"
    # security.cert-path = ".../cert.crt"
    # security.key-path = ".../key.crt"

    # (optional) Use the snapshot feature. If enabled, historical data is used for comparison.
    # snapshot = "386902609362944000"
    # When "snapshot" is set to "auto", the last syncpoints generated by TiCDC in the upstream and downstream are used for comparison. For details, see <https://github.com/pingcap/tidb-tools/issues/663>.
    # snapshot = "auto"

########################### Routes ##############################
# To compare the data of a large number of tables with different schema names or table names, or check the data of multiple upstream sharded tables and downstream table family, use the table-rule to configure the mapping relationship. You can configure the mapping rule only for the schema or table. Also, you can configure the mapping rules for both the schema and the table.
[routes]
[routes.rule1] # rule1 is the only custom ID for the configuration. It is used for the above `data-sources.route-rules` configuration.
schema-pattern = "test_*"      # Matches the schema name of the data source. Supports the wildcards "*" and "?"
table-pattern = "t_*"          # Matches the table name of the data source. Supports the wildcards "*" and "?"
target-schema = "test"         # The name of the schema in the target database
target-table = "t"             # The name of the target table
[routes.rule2]
schema-pattern = "test2_*"      # Matches the schema name of the data source. Supports the wildcards "*" and "?"
table-pattern = "t2_*"          # Matches the table name of the data source. Supports the wildcards "*" and "?"
target-schema = "test2"         # The name of the schema in the target database
target-table = "t2"             # The name of the target table

######################### task config #########################
# Configures the tables of the target database that need to be compared.
[task]
    # output-dir saves the following information:
    # 1 sql: The SQL file to fix tables that is generated after error is detected. One chunk corresponds to one SQL file.
    # 2 log: sync-diff.log
    # 3 summary: summary.txt
    # 4 checkpoint: a dir
    output-dir = "./output"
    # The upstream database. The value is the unique ID declared by data-sources.
    source-instances = ["mysql1"]
    # The downstream database. The value is the unique ID declared by data-sources.
    target-instance = "tidb0"
    # The tables of downstream databases to be compared. Each table needs to contain the schema name and the table name, separated by '.'
    # Use "?" to match any character and "*" to match characters of any length.
    # For detailed match rules, refer to golang regexp pkg: https://github.com/google/re2/wiki/Syntax.
    target-check-tables = ["schema*.table*", "!c.*", "test2.t2"]
    # (optional) Extra configurations for some tables, Config1 is defined in the following table config example.
    target-configs = ["config1"]

######################### Table config #########################
# Special configurations for specific tables. The tables to be configured must be in `task.target-check-tables`.
[table-configs.config1] # config1  is the only custom ID for this configuration. It is used for the above `task.target-configs` configuration.
# The name of the target table, you can use regular expressions to match multiple tables, but one table is not allowed to be matched by multiple special configurations at the same time.
target-tables = ["schema*.test*", "test2.t2"]
# (optional) Specifies the range of the data to be checked
# It needs to comply with the syntax of the WHERE clause in SQL.
range = "age > 10 AND age < 20"
# (optional) Specifies the column used to divide data into chunks. If you do not configure it,
# sync-diff-inspector chooses an appropriate column (primary key, unique key, or a field with index).
index-fields = ["col1","col2"]
# (optional) Ignores checking some columns such as some types (json, bit, blob, etc.)
# that sync-diff-inspector does not currently support.
# The floating-point data type behaves differently in TiDB and MySQL. You can use
# `ignore-columns` to skip checking these columns.
ignore-columns = ["",""]
# (optional) Specifies the size of the chunk for dividing the table. If not specified, this configuration can be deleted or be set as 0.
chunk-size = 0
# (optional) Specifies the "collation" for the table. If not specified, this configuration can be deleted or be set as an empty string.
collation = ""
```
