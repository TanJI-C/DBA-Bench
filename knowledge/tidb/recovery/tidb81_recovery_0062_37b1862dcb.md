# TiDB Lightning checkpoint control and recovery commands

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-checkpoints.md`
- Source Title: `TiDB Lightning Checkpoints`
- Source Heading Path: `TiDB Lightning Checkpoints > Checkpoints control | TiDB Lightning Checkpoints > Checkpoints control > `--checkpoint-error-destroy` | TiDB Lightning Checkpoints > Checkpoints control > `--checkpoint-error-ignore` | TiDB Lightning Checkpoints > Checkpoints control > `--checkpoint-remove` | TiDB Lightning Checkpoints > Checkpoints control > `--checkpoint-dump``
- Source Line Ranges: `58-111`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`
- Topic Tags: `checkpoint-control`, `error-recovery`, `destroy`, `ignore-errors`, `remove-checkpoints`, `dump-checkpoints`, `data-loss-warning`, `debugging`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0062_37b1862dcb`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-checkpoints.md#checkpoints-control`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `af31619d2e9c80fcb3929c5e4a9850c021d362f8f424b6ff4e601c4172690b8b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-checkpoints#checkpoints-control
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-checkpoints.md

## Retrieval Guidance

- Use When: Use this chunk when you need the tidb-lightning-ctl checkpoint control commands for abnormal exits, checkpoint error handling, checkpoint removal, or checkpoint dumping.
- Retrieval Keywords: Checkpoints control, tidb-lightning-ctl, --checkpoint-error-destroy, --checkpoint-error-ignore, --checkpoint-remove, --checkpoint-dump, `schema`.`table`, case-sensitive, backquotes, DROPs the table, resets the checkpoints record, not yet started, clears the error status, checksum, driver = "mysql", debugging
- Follow-up Guidance: The source notes that --checkpoint-error-ignore should be used only when you are sure the error can be ignored, because some imported data can be lost, and the final checksum check should remain enabled.
- Classification Note: This is classified as recovery because the content covers how to resolve checkpoint errors and control restart state after tidb-lightning exits abnormally due to unrecoverable errors.

## Official Source Content

## Checkpoints control

If `tidb-lightning` exits abnormally due to unrecoverable errors (for example, data corruption), it refuses to reuse the checkpoints until the errors are resolved. This is to prevent worsening the situation. The checkpoint errors can be resolved using the `tidb-lightning-ctl` program.
### `--checkpoint-error-destroy`

```sh
tidb-lightning-ctl --checkpoint-error-destroy='`schema`.`table`'
```

This option allows you to restart importing the table from scratch. The schema and table names must be quoted with backquotes and are case-sensitive.

- If importing the table `` `schema`.`table` `` failed previously, this option executes the following operations:

    1. DROPs the table `` `schema`.`table` `` from the target database, which means removing all imported data.
    2. Resets the checkpoints record of this table to be "not yet started".

- If there is no errors involving the table `` `schema`.`table` ``, this operation does nothing.

It is the same as applying the above on every table. This is the most convenient, safe and conservative solution to fix the checkpoint error problem:

```sh
tidb-lightning-ctl --checkpoint-error-destroy=all
```
### `--checkpoint-error-ignore`

```sh
tidb-lightning-ctl --checkpoint-error-ignore='`schema`.`table`'
tidb-lightning-ctl --checkpoint-error-ignore=all
```

If importing the table `` `schema`.`table` `` failed previously, this clears the error status as if nothing ever happened. The `all` variant applies this operation to all tables.

> **Note:**
>
> Use this option only when you are sure that the error can indeed be ignored. If not, some imported data can be lost. The only safety net is the final "checksum" check, and thus you need to keep the "checksum" option always enabled when using `--checkpoint-error-ignore`.
### `--checkpoint-remove`

```sh
tidb-lightning-ctl --checkpoint-remove='`schema`.`table`'
tidb-lightning-ctl --checkpoint-remove=all
```

This option simply removes all checkpoint information about one table or all tables, regardless of their status.
### `--checkpoint-dump`

```sh
tidb-lightning-ctl --checkpoint-dump=output/directory
```

This option dumps the content of the checkpoint into the given directory, which is mainly used for debugging by the technical staff. This option is only enabled when `driver = "mysql"`.
