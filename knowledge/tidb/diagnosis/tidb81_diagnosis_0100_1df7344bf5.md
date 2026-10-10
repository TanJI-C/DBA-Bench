# General TiDB Lightning troubleshooting: slow import, background exit, and cluster mode symptoms

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/troubleshoot-tidb-lightning.md`
- Source Title: `Troubleshoot TiDB Lightning`
- Source Heading Path: `Troubleshoot TiDB Lightning | Troubleshoot TiDB Lightning > Import speed is too slow | Troubleshoot TiDB Lightning > The `tidb-lightning` process suddenly quits while running in background | Troubleshoot TiDB Lightning > The TiDB cluster uses lots of CPU resources and runs very slowly after using TiDB Lightning`
- Source Line Ranges: `5-70`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`, `tikv`
- Topic Tags: `import-speed`, `region-concurrency`, `strict-format`, `background-process`, `sighup`, `context-canceled`, `import-mode`, `normal-mode`, `cpu-usage`, `grafana`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0100_1df7344bf5`
- Source ID: `tidb-docs-8.1:tidb-lightning/troubleshoot-tidb-lightning.md#troubleshoot-tidb-lightning`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5a803b1f113a4c621e65de0ef63b413effaac05d106c008c76b98b675636491f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/troubleshoot-tidb-lightning#troubleshoot-tidb-lightning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/troubleshoot-tidb-lightning.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing slow TiDB Lightning imports, unexpected background exits with SIGHUP or Context canceled, or a cluster left in import mode with high CPU usage after TiDB Lightning.
- Retrieval Keywords: restore chunk … takes, Grafana, region-concurrency, strict-format, [mydumper], strict-format = true, got signal to exit, signal=hangup, Context canceled, ERROR level log, import mode, normal mode, tidb-lightning-ctl --config tidb-lightning.toml --fetch-mode
- Follow-up Guidance: The content says to search the log for region-concurrency, restore chunk timing, the first ERROR level log, and got signal to exit when Context canceled appears.
- Classification Note: This is classified as diagnosis because the content lists common symptoms, likely causes such as high region-concurrency or SIGHUP, and commands or log phrases to verify the state.

## Official Source Content

# Troubleshoot TiDB Lightning

This document summarizes the common problems you might encounter when you use TiDB Lightning and their solutions.
## Import speed is too slow

Normally it takes 2 minutes per thread for TiDB Lightning to import a 256 MB data file. If the speed is much slower than this, there is an error. You can check the time taken for each data file from the log mentioning `restore chunk … takes`. This can also be observed from metrics on Grafana.

There are several reasons why TiDB Lightning becomes slow:

**Cause 1**: `region-concurrency` is set too high, which causes thread contention and reduces performance.

1. The setting can be found from the start of the log by searching `region-concurrency`.
2. If TiDB Lightning shares the same machine with other services (for example, TiKV Importer), `region-concurrency` must be **manually** set to 75% of the total number of CPU cores.
3. If there is a quota on CPU (for example, limited by Kubernetes settings), TiDB Lightning may not be able to read this out. In this case, `region-concurrency` must also be **manually** reduced.

**Cause 2**: The table schema is too complex.

Every additional index introduces a new KV pair for each row. If there are N indices, the actual size to be imported would be approximately (N+1) times the size of the Dumpling output. If the indices are negligible, you may first remove them from the schema, and add them back using `CREATE INDEX` after the import is complete.

**Cause 3**: Each file is too large.

TiDB Lightning works the best when the data source is broken down into multiple files of size around 256 MB so that the data can be processed in parallel. If each file is too large, TiDB Lightning might not respond.

If the data source is CSV, and all CSV files have no fields containing newline control characters (U+000A and U+000D), you can turn on "strict format" to let TiDB Lightning automatically split the large files.

```toml
[mydumper]
strict-format = true
```

**Cause 4**: TiDB Lightning is too old.

Try the latest version. Maybe there is new speed improvement.
## The `tidb-lightning` process suddenly quits while running in background

It is potentially caused by starting `tidb-lightning` incorrectly, which causes the system to send a SIGHUP signal to stop the `tidb-lightning` process. In this situation, `tidb-lightning.log` usually outputs the following log:

```
[2018/08/10 07:29:08.310 +08:00] [INFO] [main.go:41] ["got signal to exit"] [signal=hangup]
```

It is not recommended to directly use `nohup` in the command line to start `tidb-lightning`. You can [start `tidb-lightning`](https://docs.pingcap.com/tidb/stable/get-started-with-tidb-lightning#step-4-start-tidb-lightning) by executing a script.

In addition, if the last log of TiDB Lightning shows that the error is "Context canceled", you need to search for the first "ERROR" level log. This "ERROR" level log is usually followed by "got signal to exit", which indicates that TiDB Lightning received an interrupt signal and then exited.
## The TiDB cluster uses lots of CPU resources and runs very slowly after using TiDB Lightning

If `tidb-lightning` abnormally exited, the cluster might be stuck in the "import mode", which is not suitable for production. The current mode can be retrieved using the following command:

```sh
tidb-lightning-ctl --config tidb-lightning.toml --fetch-mode
```

You can force the cluster back to "normal mode" using the following command:

```sh
tidb-lightning-ctl --config tidb-lightning.toml --fetch-mode
```
