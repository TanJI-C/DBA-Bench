# tidb-lightning-ctl flags for engine, mode, and checkpoint operations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-command-line-full.md`
- Source Title: `TiDB Lightning Command Line Flags`
- Source Heading Path: `TiDB Lightning Command Line Flags > `tidb-lightning-ctl``
- Source Line Ranges: `43-59`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tikv`, `tidb`
- Topic Tags: `command-line-flags`, `control-utility`, `compaction`, `switch-mode`, `import-engine`, `cleanup-engine`, `checkpoint-dump`, `checkpoint-removal`, `error-ignore`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0936_a6aba2a9fb`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-command-line-full.md#tidb-lightning-ctl`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9e2a1043dfcc5130303ca07442af338f34880cc3dad1dcd25c10b91a3706a715`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-command-line-full#tidb-lightning-ctl
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-command-line-full.md

## Retrieval Guidance

- Use When: Use this chunk when identifying `tidb-lightning-ctl` flags for compaction, TiKV mode switching, engine import or cleanup, and checkpoint dump or removal operations.
- Retrieval Keywords: tidb-lightning-ctl, all parameters of tidb-lightning apply to tidb-lightning-ctl, --compact, full compaction, --switch-mode <mode>, normal or import, --fetch-mode, current mode of every TiKV store, --import-engine <uuid>, closed engine file, TiKV Importer, --cleanup-engine <uuid>, --checkpoint-dump <folder>, dump current checkpoint as CSVs, --checkpoint-error-destroy <table_name>, remove the checkpoint, drop the table, --checkpoint-error-ignore <table_name>, ignore any error recorded in the checkpoint, --checkpoint-remove <table_name>, unconditionally remove the checkpoint, qualified table name, `db`.`tbl`, all
- Follow-up Guidance: The source specifies that `<table_name>` must be either a qualified table name in the form `` `db`.`tbl` `` including the backquotes, or the keyword `all`.
- Classification Note: This is reference content because it lists the additional `tidb-lightning-ctl` parameters and defines the accepted `<table_name>` format from the official content.

## Official Source Content

## `tidb-lightning-ctl`

All parameters of `tidb-lightning` apply to `tidb-lightning-ctl`. In addition, you can also configure the following parameters using `tidb-lightning-ctl`:

| Parameter | Description |
|:----|:----|
| `--compact` | Perform a full compaction. |
| `--switch-mode <mode>` | Switch every TiKV store to the given mode: normal or import. |
| `--fetch-mode` | Print the current mode of every TiKV store. |
| `--import-engine <uuid>` | Import the closed engine file from TiKV Importer into the TiKV cluster. |
| `--cleanup-engine <uuid>` | Delete the engine file from TiKV Importer. |
| `--checkpoint-dump <folder>` | Dump current checkpoint as CSVs into the folder. |
| `--checkpoint-error-destroy <table_name>` | Remove the checkpoint. If it causes an error, drop the table. |
| `--checkpoint-error-ignore <table_name>` | Ignore any error recorded in the checkpoint involving the given table. |
|`--checkpoint-remove <table_name>` | Unconditionally remove the checkpoint of the table. |

The `<table_name>` must either be a qualified table name in the form `` `db`.`tbl` `` (including the backquotes), or the keyword `all`.
