# Manual TiKV compaction commands

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-control.md`
- Source Title: `TiKV Control User Guide`
- Source Heading Path: `TiKV Control User Guide > Subcommands, some options and flags > Compact data of each TiKV manually | TiKV Control User Guide > Subcommands, some options and flags > Compact data of the whole TiKV cluster manually`
- Source Line Ranges: `296-328`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`
- Topic Tags: `compaction`, `rocksdb`, `column-family`, `cluster-wide`, `concurrency`, `bottommost`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0482_cfc55b972d`
- Source ID: `tidb-docs-8.1:tikv-control.md#compact-data-of-each-tikv-manually`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d146402071a36b1bd54ebbfa93f62439e20b67d576411fb03c404c23fdc1ad10`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-control#compact-data-of-each-tikv-manually
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-control.md

## Retrieval Guidance

- Use When: Use this chunk when you need the tikv-ctl syntax and flags for manually compacting data on a single TiKV or across the whole TiKV cluster.
- Retrieval Keywords: compact, compact-cluster, --from, --to, --region, -c, column family, default, lock, write, -d, kv, raft, --threads, --bottommost, default, skip, force, --data-dir, --host, --pd
- Follow-up Guidance: The content explains that compact-cluster uses --pd to locate all TiKV nodes, while compact uses --data-dir or --host to target a single TiKV.
- Classification Note: This is classified as operation because the official content describes manual compaction commands, ranges, targets, concurrency, and bottommost-file behavior.

## Official Source Content

### Compact data of each TiKV manually

Use the `compact` command to manually compact data of each TiKV.

- Use the `--from` and `--to` options to specify the compaction range in the form of escaped raw key. If not set, the whole range will be compacted.
- Use the `--region` option to compact the range of a specific region. If set, `--from` and `--to` will be ignored.
- Use the `-c` option to specify the column family name. The default value is `default`. The optional values are `default`, `lock`, and `write`.
- Use the `-d` option to specify the RocksDB that performs compaction. The default value is `kv`. The optional values are `kv` and `raft`.
- Use the `--threads` option allows you to specify the concurrency for the TiKV compaction and its default value is `8`. Generally, a higher concurrency comes with a faster compaction speed, which might yet affect the service. You need to choose an appropriate concurrency count based on your scenario.
- Use the `--bottommost` option to include or exclude the bottommost files when TiKV performs compaction. The value options are `default`, `skip`, and `force`. The default value is `default`.
    - `default` means that the bottommost files are included only when the Compaction Filter feature is enabled.
    - `skip` means that the bottommost files are excluded when TiKV performs compaction.
    - `force` means that the bottommost files are always included when TiKV performs compaction.

- To compact data in the local mode, use the following command:

    ```shell
    tikv-ctl --data-dir /path/to/tikv compact -d kv
    ```

- To compact data in the remote mode, use the following command:

    ```shell
    tikv-ctl --host ip:port compact -d kv
    ```
### Compact data of the whole TiKV cluster manually

Use the `compact-cluster` command to manually compact data of the whole TiKV cluster. The flags of this command have the same meanings and usage as those of the `compact` command. The only difference is as follows:

- For the `compact-cluster` command, use `--pd` to specify the address of the PD, so that `tikv-ctl` can locate all TiKV nodes in the cluster as the compact target.
- For the `compact` command, use `--data-dir` or `--host` to specify a single TiKV as the compact target.
