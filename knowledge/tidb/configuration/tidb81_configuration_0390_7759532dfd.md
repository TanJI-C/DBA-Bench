# Dynamic TiKV configuration modification

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-control.md`
- Source Title: `TiKV Control User Guide`
- Source Heading Path: `TiKV Control User Guide > Subcommands, some options and flags > Modify the TiKV configuration dynamically`
- Source Line Ranges: `415-475`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `sql`, `tidb`
- Topic Tags: `dynamic-configuration`, `modify-tikv-config`, `block-cache`, `compaction`, `rate-limiter`, `raftstore`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0390_7759532dfd`
- Source ID: `tidb-docs-8.1:tikv-control.md#modify-the-tikv-configuration-dynamically`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3d96c2345c73cd57e2b80f5a02e33b10f2b841e807b2684496403487d5d2ce35`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-control#modify-the-tikv-configuration-dynamically
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-control.md

## Retrieval Guidance

- Use When: Use this chunk when you need the modify-tikv-config command and example dynamic configuration names for changing TiKV settings through tikv-ctl.
- Retrieval Keywords: modify-tikv-config, -n, -v, storage.block-cache.capacity, rocksdb.writecf.block-cache-size, raftdb.defaultcf.disable-auto-compactions, raftstore.sync-log, rocksdb.rate-limiter-auto-tuned, rocksdb.rate-bytes-per-sec, shared block cache, write CF, compaction pending bytes
- Follow-up Guidance: The content says the dynamically modifiable TiKV configuration items and modification details are consistent with modifying configuration using SQL statements.
- Classification Note: This is classified as configuration because the official content is about dynamically modifying TiKV configuration items and provides exact configurable names and values.

## Official Source Content

### Modify the TiKV configuration dynamically

You can use the `modify-tikv-config` command to dynamically modify the configuration arguments. Currently, the TiKV configuration items that can be dynamically modified and the detailed modification are consistent with modifying configuration using SQL statements. For details, see [Modify TiKV configuration dynamically](https://docs.pingcap.com/tidb/stable/dynamic-config#modify-tikv-configuration-dynamically).

- `-n` is used to specify the full name of the configuration item. For the list of configuration items that can be modified dynamically, see [Modify TiKV configuration dynamically](https://docs.pingcap.com/tidb/stable/dynamic-config#modify-tikv-configuration-dynamically).
- `-v` is used to specify the configuration value.

Set the size of `shared block cache`:

```shell
tikv-ctl --host ip:port modify-tikv-config -n storage.block-cache.capacity -v 10GB
```

```
success
```

When `shared block cache` is disabled, set `block cache size` for the `write` CF:

```shell
tikv-ctl --host ip:port modify-tikv-config -n rocksdb.writecf.block-cache-size -v 256MB
```

```
success
```

```shell
tikv-ctl --host ip:port modify-tikv-config -n raftdb.defaultcf.disable-auto-compactions -v true
```

```
success
```

```shell
tikv-ctl --host ip:port modify-tikv-config -n raftstore.sync-log -v false
```

```
success
```

When the compaction rate limit causes accumulated compaction pending bytes, disable the `rate-limiter-auto-tuned` mode or set a higher limit for the compaction flow:

```shell
tikv-ctl --host ip:port modify-tikv-config -n rocksdb.rate-limiter-auto-tuned -v false
```

```
success
```

```shell
tikv-ctl --host ip:port modify-tikv-config -n rocksdb.rate-bytes-per-sec -v "1GB"
```

```
success
```
