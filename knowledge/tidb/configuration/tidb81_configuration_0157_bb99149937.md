# DM replication data check configuration example

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sync-diff-inspector/dm-diff.md`
- Source Title: `Data Check in the DM Replication Scenario`
- Source Heading Path: `Data Check in the DM Replication Scenario`
- Source Line Ranges: `5-40`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `shared`
- Topic Tags: `data-consistency`, `replication`, `task-name`, `dm-master`, `sync-diff-inspector`, `diff-configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0157_bb99149937`
- Source ID: `tidb-docs-8.1:sync-diff-inspector/dm-diff.md#data-check-in-the-dm-replication-scenario`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `480852324964fabd12cf88e30ee849ccd05eb4ad81a93c52a636263d5387c7cf`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sync-diff-inspector/dm-diff#data-check-in-the-dm-replication-scenario
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sync-diff-inspector/dm-diff.md

## Retrieval Guidance

- Use When: Use this chunk when looking for a Sync-diff-inspector configuration example to check data consistency in a DM replication task using a specific `task-name` from `DM-master`.
- Retrieval Keywords: Data Check in the DM Replication Scenario, DM replication data check configuration example, sync-diff-inspector, TiDB Data Migration, DM-master, task-name, dm-addr, dm-task, check-thread-count, export-fix-sql, check-struct-only, target-check-tables, hb_test.*, output-dir
- Follow-up Guidance: The source notes that the complete configuration is in the Sync-diff-inspector User Guide and that this example checks all tables of the `hb_test` schema under the `test` task by automatically getting the regular matching of schemas between upstream and downstream databases.
- Classification Note: This is classified as configuration because the official content provides a TOML example with global and task settings such as `dm-addr`, `dm-task`, and `target-check-tables` for DM replication data checking.

## Official Source Content

# Data Check in the DM Replication Scenario

When using replication tools such as [TiDB Data Migration](https://docs.pingcap.com/tidb/stable/dm/dm-overview), you need to check the data consistency before and after the replication process. You can set a specific `task-name` configuration from `DM-master` to perform a data check.

The following is a simple configuration example. To learn the complete configuration, refer to [Sync-diff-inspector User Guide](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview).

```toml
# Diff Configuration.

######################### Global config #########################

# The number of goroutines created to check data. The number of connections between upstream and downstream databases are slightly greater than this value.
check-thread-count = 4

# If enabled, SQL statements is exported to fix inconsistent tables.
export-fix-sql = true

# Only compares the table structure instead of the data.
check-struct-only = false

# The IP address of dm-master and the format is "http://127.0.0.1:8261".
dm-addr = "http://127.0.0.1:8261"

# Specifies the `task-name` of DM.
dm-task = "test"

######################### Task config #########################
[task]
    output-dir = "./output"

    # The tables of downstream databases to be compared. Each table needs to contain the schema name and the table name, separated by '.'
    target-check-tables = ["hb_test.*"]
```

This example is configured in dm-task = "test", which checks all the tables of hb_test schema under the "test" task. It automatically gets the regular matching of the schemas between upstream and downstream databases to verify the data consistency after DM replication.
