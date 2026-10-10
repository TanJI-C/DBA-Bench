# Dynamic configuration through TiDB system variables for TiDB and TiFlash

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dynamic-config.md`
- Source Title: `Modify Configuration Dynamically`
- Source Heading Path: `Modify Configuration Dynamically > Common Operations > Modify TiDB configuration dynamically | Modify Configuration Dynamically > Common Operations > Modify TiFlash configuration dynamically`
- Source Line Ranges: `337-413`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `sql`
- Topic Tags: `dynamic-configuration`, `system-variables`, `slow-log`, `instance-settings`, `max-connections`, `ddl-owner`, `tiflash-concurrency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0101_862dbf0788`
- Source ID: `tidb-docs-8.1:dynamic-config.md#modify-tidb-configuration-dynamically`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1c73aa1b7c642918012afadae25c5423eaa5e2b3e03b986a6c8b68846d7aa6e3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dynamic-config#modify-tidb-configuration-dynamically
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dynamic-config.md

## Retrieval Guidance

- Use When: Use this chunk when looking for which TiDB and TiFlash settings can be changed dynamically through system variables, including slow log thresholds, instance settings, DDL owner control, and TiFlash max_threads.
- Retrieval Keywords: modify TiDB configuration by using system variables, set tidb_slow_log_threshold = 200, select @@tidb_slow_log_threshold, instance.tidb_enable_slow_log, tidb_enable_slow_log, instance.tidb_slow_log_threshold, tidb_slow_log_threshold, instance.tidb_expensive_query_time_threshold, tidb_expensive_query_time_threshold, instance.tidb_enable_collect_execution_info, instance.tidb_record_plan_in_slow_log, instance.tidb_force_priority, instance.max_connections, max_connections, instance.tidb_enable_ddl, tidb_enable_ddl, tidb_constraint_check_in_place_pessimistic, tidb_max_tiflash_threads, max_threads, set tidb_max_tiflash_threads = 10, select @@tidb_max_tiflash_threads
- Follow-up Guidance: The content links to the system variables reference for TiDB system variables and tidb_max_tiflash_threads.
- Classification Note: This is classified as configuration because the official content maps configurable TiDB and TiFlash runtime settings to SQL system variables that can be changed dynamically.

## Official Source Content

### Modify TiDB configuration dynamically

Currently, the method of changing TiDB configuration is different from that of changing TiKV and PD configurations. You can modify TiDB configuration by using [system variables](https://docs.pingcap.com/tidb/stable/system-variables).

The following example shows how to dynamically modify `slow-threshold` by using the `tidb_slow_log_threshold` variable.

The default value of `slow-threshold` is 300 ms. You can set it to 200 ms by using `tidb_slow_log_threshold`.

```sql
set tidb_slow_log_threshold = 200;
```

```sql
Query OK, 0 rows affected (0.00 sec)
```

```sql
select @@tidb_slow_log_threshold;
```

```sql
+---------------------------+
| @@tidb_slow_log_threshold |
+---------------------------+
| 200                       |
+---------------------------+
1 row in set (0.00 sec)
```

The following TiDB configuration items can be modified dynamically:

| Configuration item | SQL variable | Description |
| --- | --- | --- |
| `instance.tidb_enable_slow_log` | `tidb_enable_slow_log` | Controls whether to enable slow log |
| `instance.tidb_slow_log_threshold` | `tidb_slow_log_threshold` | Specifies the threshold of slow log |
| `instance.tidb_expensive_query_time_threshold` | `tidb_expensive_query_time_threshold` | Specifies the threshold of an expensive query |
| `instance.tidb_enable_collect_execution_info` | `tidb_enable_collect_execution_info` | Controls whether to record the execution information of operators |
| `instance.tidb_record_plan_in_slow_log` | `tidb_record_plan_in_slow_log` | Controls whether to record execution plans in the slow log |
| `instance.tidb_force_priority` | `tidb_force_priority` | Specifies the priority of statements that are submitted from this TiDB instance |
| `instance.max_connections` | `max_connections` | Specifies the maximum number of concurrent connections permitted for this TiDB instance |
| `instance.tidb_enable_ddl` | `tidb_enable_ddl` | Controls whether this TiDB instance can become a DDL owner |
| `pessimistic-txn.constraint-check-in-place-pessimistic` | `tidb_constraint_check_in_place_pessimistic` | Controls whether to defer the unique constraint check of a unique index to the next time when this index requires a lock or to the time when the transaction is committed |
### Modify TiFlash configuration dynamically

Currently, you can modify the TiFlash configuration `max_threads` by using the system variable [`tidb_max_tiflash_threads`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_max_tiflash_threads-new-in-v610), which specifies the maximum concurrency for TiFlash to execute a request.

The default value of `tidb_max_tiflash_threads` is `-1`, indicating that this system variable is invalid and depends on the setting of the TiFlash configuration file. You can set `max_threads` to 10 by using `tidb_max_tiflash_threads`:

```sql
set tidb_max_tiflash_threads = 10;
```

```sql
Query OK, 0 rows affected (0.00 sec)
```

```sql
select @@tidb_max_tiflash_threads;
```

```sql
+----------------------------+
| @@tidb_max_tiflash_threads |
+----------------------------+
| 10                         |
+----------------------------+
1 row in set (0.00 sec)
```
