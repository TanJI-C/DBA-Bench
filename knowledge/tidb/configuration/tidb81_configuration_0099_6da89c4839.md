# Modify TiKV configuration dynamically

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dynamic-config.md`
- Source Title: `Modify Configuration Dynamically`
- Source Heading Path: `Modify Configuration Dynamically > Common Operations > Modify TiKV configuration dynamically`
- Source Line Ranges: `56-125`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tiup`, `tidb`
- Topic Tags: `dynamic-configuration`, `set-config`, `tikv`, `batch-modification`, `warnings`, `persistence`, `backticks`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0099_6da89c4839`
- Source ID: `tidb-docs-8.1:dynamic-config.md#modify-tikv-configuration-dynamically`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `86e33158cbc0f89288b76206c8154c7efcc519ff5a9832b2235f58b313a1c63c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dynamic-config#modify-tikv-configuration-dynamically
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dynamic-config.md

## Retrieval Guidance

- Use When: Use this when you need the SQL syntax, warnings behavior, and persistence notes for dynamically modifying TiKV configuration with `set config`.
- Retrieval Keywords: set config tikv `split.qps-threshold`=1000;, set config "127.0.0.1:20180" `split.qps-threshold`=1000;, show warnings;, Query OK, 0 rows affected, 1 warning, config log-level can not be changed, tiup edit-config, tiup reload, batch modification does not guarantee atomicity, wrap variable names in backticks, `raftstore.raft-log-gc-size-limit`
- Follow-up Guidance: If batch modification returns warnings or some instances fail, the content states that you can inspect `show warnings`, re-execute the statement, or modify each failed instance after recovery.
- Classification Note: This is classified as TiKV configuration content because it specifically covers dynamic TiKV `set config` operations, instance targeting, warning handling, persistence, and TiUP-related overwrite notes.

## Official Source Content

### Modify TiKV configuration dynamically

> **Note:**
>
> - After dynamically changing TiKV configuration items, the TiKV configuration file is automatically updated. However, you also need to modify the corresponding configuration items by executing `tiup edit-config`; otherwise, operations such as `upgrade` and `reload` will overwrite your changes. For details of modifying configuration items, refer to [Modify configuration using TiUP](https://docs.pingcap.com/tidb/stable/maintain-tidb-using-tiup#modify-the-configuration).
> - After executing `tiup edit-config`, you do not need to execute `tiup reload`.

When using the `set config` statement, you can modify the configuration of a single instance or of all instances according to the instance address or the component type.

- Modify the configuration of all TiKV instances:

> **Note:**
>
> It is recommended to wrap variable names in backticks.

```sql
set config tikv `split.qps-threshold`=1000;
```

- Modify the configuration of a single TiKV instance:

    ```sql
    set config "127.0.0.1:20180" `split.qps-threshold`=1000;
    ```

If the modification is successful, `Query OK` is returned:

```sql
Query OK, 0 rows affected (0.01 sec)
```

If an error occurs during the batch modification, a warning is returned:

```sql
set config tikv `log-level`='warn';
```

```sql
Query OK, 0 rows affected, 1 warning (0.04 sec)
```

```sql
show warnings;
```

```sql
+---------+------+---------------------------------------------------------------------------------------------------------------+
| Level   | Code | Message                                                                                                       |
+---------+------+---------------------------------------------------------------------------------------------------------------+
| Warning | 1105 | bad request to http://127.0.0.1:20180/config: fail to update, error: "config log-level can not be changed" |
+---------+------+---------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```

The batch modification does not guarantee atomicity. The modification might succeed on some instances, while failing on others. If you modify the configuration of the entire TiKV cluster using `set tikv key=val`, your modification might fail on some instances. You can use `show warnings` to check the result.

If some modifications fail, you need to re-execute the corresponding statement or modify each failed instance. If some TiKV instances cannot be accessed due to network issues or machine failure, modify these instances after they are recovered.

If a configuration item is successfully modified, the result is persisted in the configuration file, which will prevail in the subsequent operations. The names of some configuration items might conflict with TiDB reserved words, such as `limit` and `key`. For these configuration items, use backtick `` ` `` to enclose them. For example, `` `raftstore.raft-log-gc-size-limit` ``.

The following TiKV configuration items can be modified dynamically:
