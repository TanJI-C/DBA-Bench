# DM task configuration example template

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-task-configuration-guide.md`
- Source Title: `Data Migration Task Configuration Guide`
- Source Heading Path: `Data Migration Task Configuration Guide > Other configurations`
- Source Line Ranges: `187-256`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `task-config`, `yaml`, `data-sources`, `target-database`, `block-allow-list`, `filter-rules`, `route-rules`, `shard-merge`, `timezone`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0085_45e307496c`
- Source ID: `tidb-docs-8.1:dm/dm-task-configuration-guide.md#other-configurations`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `84f1c7536bbe05d129ae21889dd5ec94d0d45ce9b34fc156cb930b80492abedc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-task-configuration-guide#other-configurations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-task-configuration-guide.md

## Retrieval Guidance

- Use When: Use this chunk when looking for an overall DM task configuration example template that includes basic settings, mysql-instances, target-database, block-allow-list, filters, and routes in one YAML file.
- Retrieval Keywords: DM task configuration example, task configuration template, DM task configuration file full introduction, name, shard-mode, task-mode, timezone, mysql-instances, source-id, block-allow-list, black-white-list, filter-rules, route-rules, target-database, host, port, user, password, block-allow-list rule, do-dbs, ignore-dbs, do-tables, ignore-tables, filters, schema-pattern, table-pattern, events, action: Ignore, action: Do, routes, target-schema, target-table, pessimistic, optimistic, full, incremental, all
- Follow-up Guidance: The source states that the complete task configuration template can be found in DM task configuration file full introduction.
- Classification Note: This chunk is classified as configuration because it provides a full DM task YAML example covering task-level options, upstream source mappings, downstream TiDB connection settings, and rule sets for filtering and routing.

## Official Source Content

## Other configurations

The following is an overall task configuration example of this document. The complete task configuration template can be found in [DM task configuration file full introduction](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full).

```yaml
---

## ********* Basic configuration *********
name: test                      # The name of the task. Should be globally unique.
shard-mode: "pessimistic"       # The shard merge mode. Optional modes are ""/"pessimistic"/"optimistic". The "" mode is used by default which means sharding DDL merge is disabled. If the task is a shard merge task, set it to the "pessimistic" mode. After getting a deep understanding of the principles and restrictions of the "optimistic" mode, you can set it to the "optimistic" mode.
task-mode: all                  # The task mode. Can be set to `full`(only migrates full data)/`incremental`(replicates binlog synchronously)/`all` (replicates both full and incremental binlogs).
timezone: "UTC"               # The timezone used in SQL Session. By default, DM uses the global timezone setting in the target cluster, which ensures the correctness automatically. A customized timezone does not affect data migration but is unnecessary.

## ******** Data source configuration **********
mysql-instances:
  - source-id: "mysql-replica-01"                   # Migrate data from the data source whose `source-id` is `mysql-replica-01`.
    block-allow-list:  "bw-rule-1"                  # The name of the block and allow list rule. If the DM version is earlier than v2.0.0-beta.2, use `black-white-list` instead.
    filter-rules: ["filter-rule-1"]                 # The name of the rule that filters specific binlog events of the data source. You can configure multiple rules here.
    route-rules: ["route-rule-1", "route-rule-2"]   # The name of the routing mapping rule. You can configure multiple rules here.
  - source-id: "mysql-replica-02"                   # Migrate data from the data source whose `source-id` is `mysql-replica-02`.
    block-allow-list:  "bw-rule-2"                  # The name of the block and allow list rule. If the DM version is earlier than v2.0.0-beta.2, use `black-white-list` instead.
    filter-rules: ["filter-rule-2"]                 # The name of the rule that filters specific binlog events of the data source. You can configure multiple rules here.
    route-rules: ["route-rule-2"]                   # The name of the routing mapping rule. You can configure multiple rules here.

## ******** Downstream TiDB instance configuration **********
target-database:       # Configuration of the downstream database instance.
  host: "127.0.0.1"
  port: 4000
  user: "root"
  password: ""         # If the password is not null, it is recommended to use a password encrypted with dmctl.

## ******** Feature configuration set **********
# The filter rule set of tables to be migrated from the upstream database instance. You can set multiple rules at the same time.
block-allow-list:                      # Use black-white-list if the DM version is earlier than v2.0.0-beta.2.
  bw-rule-1:                           # The name of the block and allow list rule.
    do-dbs: ["test.*", "user"]         # The allow list of upstream schemas to be migrated. Wildcard characters (*?) are supported. You only need to configure either `do-dbs` or `ignore-dbs`. If both fields are configured, only `do-dbs` takes effect.
    # ignore-dbs: ["mysql", "account"] # The block list of upstream schemas to be migrated. Wildcard characters (*?) are supported.
    do-tables:                         # The allow list of upstream tables to be migrated. You only need to configure either `do-tables` or `ignore-tables`. If both fields are configured, only `do-tables` takes effect.
    - db-name: "test.*"
      tbl-name: "t.*"
    - db-name: "user"
      tbl-name: "information"
  bw-rule-2:                         # The name of the block allow list rule.
    ignore-tables:                   # The block list of data source tables needs to be migrated.
    - db-name: "user"
      tbl-name: "log"

# The filter rule set of data source binlog events.
filters:                                        # You can set multiple rules at the same time.
  filter-rule-1:                                # The name of the filtering rule.
    schema-pattern: "test_*"                    # The pattern of the data source schema name. Wildcard characters (*?) are supported.
    table-pattern: "t_*"                        # The pattern of the data source table name. Wildcard characters (*?) are supported.
    events: ["truncate table", "drop table"]    # The event types to be filtered out in schemas or tables that match the `schema-pattern` or the `table-pattern`.
    action: Ignore                              # Whether to migrate (Do) or ignore (Ignore) the binlog that matches the filtering rule.
  filter-rule-2:
    schema-pattern: "test"
    events: ["all dml"]
    action: Do

# The routing mapping rule set between the data source and target TiDB instance tables.
routes:                           # You can set multiple rules at the same time.
  route-rule-1:                   # The name of the routing mapping rule.
    schema-pattern: "test_*"      # The pattern of the data source schema name. Wildcard characters (*?) are supported.
    table-pattern: "t_*"          # The pattern of the data source table name. Wildcard characters (*?) are supported.
    target-schema: "test"         # The name of the downstream TiDB schema.
    target-table: "t"             # The name of the downstream TiDB table.
  route-rule-2:
    schema-pattern: "test_*"
    target-schema: "test"
```
