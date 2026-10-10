# Run command and generated output artifacts

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sync-diff-inspector/sync-diff-inspector-overview.md`
- Source Title: `sync-diff-inspector User Guide`
- Source Heading Path: `sync-diff-inspector User Guide > Run sync-diff-inspector`
- Source Line Ranges: `167-178`
- Source Scope: `shared`
- Primary Component: `ecosystem`
- Related Components: none
- Topic Tags: `run`, `command`, `output-dir`, `summary`, `log`, `checkpoint`, `fix-sql`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0239_49280fc840`
- Source ID: `tidb-docs-8.1:sync-diff-inspector/sync-diff-inspector-overview.md#run-sync-diff-inspector`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5caf95d97475ae31b12931882941ade9ed08ae4338a271e7707126454f72e24b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview#run-sync-diff-inspector
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sync-diff-inspector/sync-diff-inspector-overview.md

## Retrieval Guidance

- Use When: Use this when you need the command to run sync-diff-inspector and the names of the output artifacts it generates.
- Retrieval Keywords: Run sync-diff-inspector, ./sync_diff_inspector --config=./config.toml, summary.txt, sync_diff.log, output-dir, checkpoint node information, SQL file generated when the data is inconsistent, hash value of the config.toml file
- Follow-up Guidance: The output directory contains `summary.txt`, `sync_diff.log`, and a hash-named folder with checkpoint information and generated SQL files.
- Classification Note: This is operation content because it gives the execution command and describes the runtime output files and directories.

## Official Source Content

## Run sync-diff-inspector

Run the following command:

```bash
./sync_diff_inspector --config=./config.toml
```

This command outputs a check report `summary.txt` in the `output-dir` of `config.toml` and the log `sync_diff.log`. In the `output-dir`, a folder named by the hash value of the `config. toml` file is also generated. This folder includes the checkpoint node information of breakpoints and the SQL file generated when the data is inconsistent.
