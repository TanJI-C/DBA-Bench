# Raw key scanning and region property inspection

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-control.md`
- Source Title: `TiKV Control User Guide`
- Source Heading Path: `TiKV Control User Guide > Subcommands, some options and flags > Scan raw keys | TiKV Control User Guide > Subcommands, some options and flags > Print a specific key value | TiKV Control User Guide > Subcommands, some options and flags > Print some properties about Region`
- Source Line Ranges: `252-295`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `raw-scan`, `rocksdb`, `keys`, `region-properties`, `mvcc`, `sst`, `inspection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0121_e6b15bf0f4`
- Source ID: `tidb-docs-8.1:tikv-control.md#scan-raw-keys`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `83e4b57be728740aa56fa6bae7d6f6f1228ac7a69d004df13400816c56805d96`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-control#scan-raw-keys
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-control.md

## Retrieval Guidance

- Use When: Use this chunk when you need tikv-ctl commands for scanning raw keys from RocksDB, printing a specific key value, or inspecting Region SST properties such as MVCC statistics and middle keys.
- Retrieval Keywords: raw-scan, RocksDB, 'z' prefix, --from, --to, --limit, --cf, default, write, lock, print command, region-properties, tikv-ctl --host localhost:20160 region-properties -r 2, mvcc.min_ts, mvcc.max_ts, mvcc.num_rows, mvcc.num_versions, middle_key_by_approximate_size
- Follow-up Guidance: The content notes that Region properties can be used to check whether a Region is healthy and gives manual splitting by middle_key_approximate_size as an example if it is not.
- Classification Note: This is classified as diagnosis because the official content focuses on inspecting raw keys, key values, and Region properties to assess Region state and health.

## Official Source Content

### Scan raw keys

The `raw-scan` command scans directly from the RocksDB. Note that to scan data keys you need to add a `'z'` prefix to keys.

Use `--from` and `--to` options to specify the range to scan (unbounded by default). Use `--limit` to limit at most how many keys to print out (30 by default). Use `--cf` to specify which cf to scan (can be `default`, `write` or `lock`).

```shell
tikv-ctl --data-dir /var/lib/tikv raw-scan --from 'zt' --limit 2 --cf default
```

```
key: "zt\200\000\000\000\000\000\000\377\005_r\200\000\000\000\000\377\000\000\001\000\000\000\000\000\372\372b2,^\033\377\364", value: "\010\002\002\002%\010\004\002\010root\010\006\002\000\010\010\t\002\010\n\t\002\010\014\t\002\010\016\t\002\010\020\t\002\010\022\t\002\010\024\t\002\010\026\t\002\010\030\t\002\010\032\t\002\010\034\t\002\010\036\t\002\010 \t\002\010\"\t\002\010s\t\002\010&\t\002\010(\t\002\010*\t\002\010,\t\002\010.\t\002\0100\t\002\0102\t\002\0104\t\002"
key: "zt\200\000\000\000\000\000\000\377\025_r\200\000\000\000\000\377\000\000\023\000\000\000\000\000\372\372b2,^\033\377\364", value: "\010\002\002&slow_query_log_file\010\004\002P/usr/local/mysql/data/localhost-slow.log"

Total scanned keys: 2
```
### Print a specific key value

To print the value of a key, use the `print` command.
### Print some properties about Region

In order to record Region state details, TiKV writes some statistics into the SST files of Regions. To view these properties, run `tikv-ctl` with the `region-properties` sub-command:

```shell
tikv-ctl --host localhost:20160 region-properties -r 2
```

```
num_files: 0
num_entries: 0
num_deletes: 0
mvcc.min_ts: 18446744073709551615
mvcc.max_ts: 0
mvcc.num_rows: 0
mvcc.num_puts: 0
mvcc.num_versions: 0
mvcc.max_row_versions: 0
middle_key_by_approximate_size:
```

The properties can be used to check whether the Region is healthy or not. If not, you can use them to fix the Region. For example, splitting the Region manually by `middle_key_approximate_size`.
