# TiDB Lightning compatibility and CSV header error troubleshooting

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/troubleshoot-tidb-lightning.md`
- Source Title: `Troubleshoot TiDB Lightning`
- Source Heading Path: `Troubleshoot TiDB Lightning > TiDB Lightning reports an error > Encounter `rpc error: code = Unimplemented ...` when TiDB Lightning switches the mode | Troubleshoot TiDB Lightning > TiDB Lightning reports an error > `tidb lightning encountered error: TiDB version too old, expected '>=4.0.0', found '3.0.18'` | Troubleshoot TiDB Lightning > TiDB Lightning reports an error > `restore table test.district failed: unknown columns in header [...]``
- Source Line Ranges: `161-184`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tiflash`, `tidb`
- Topic Tags: `switch-mode`, `rpc-error`, `version-compatibility`, `local-backend`, `importer-backend`, `tidb-backend`, `csv`, `header`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0102_dd4888c5b2`
- Source ID: `tidb-docs-8.1:tidb-lightning/troubleshoot-tidb-lightning.md#encounter-rpc-error-code-unimplemented-when-tidb-lightning-switches-the-mode`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0f059b7894f263bfdc7d8e74f644ebe228a74a8ee1c4e37af236724f77ece89f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/troubleshoot-tidb-lightning#encounter-rpc-error-code-unimplemented-when-tidb-lightning-switches-the-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/troubleshoot-tidb-lightning.md

## Retrieval Guidance

- Use When: Use this chunk when TiDB Lightning errors involve switch-mode RPC compatibility, Local-backend version requirements, or CSV imports failing because header columns are unknown.
- Retrieval Keywords: rpc error: code = Unimplemented, switch-mode, TiFlash, v4.0.0-rc.2, tidb lightning encountered error: TiDB version too old, expected '>=4.0.0', found '3.0.18', Local-backend, Importer-backend, TiDB-backend, check-requirements = false, restore table test.district failed: unknown columns in header, [mydumper.csv], header = false
- Follow-up Guidance: The content distinguishes switch-mode support by node version, explains that Local-backend requires TiDB v4.0.0 and later, and shows the CSV setting header = false for files without a header row.
- Classification Note: This is classified as diagnosis because it groups exact compatibility and CSV parsing error messages with the component or configuration conditions that trigger them.

## Official Source Content

### Encounter `rpc error: code = Unimplemented ...` when TiDB Lightning switches the mode

**Cause**: Some node(s) in the cluster does not support `switch-mode`. For example, if the TiFlash version is earlier than `v4.0.0-rc.2`, [`switch-mode` is not supported](https://github.com/pingcap/tidb-lightning/issues/273).

**Solutions**:

- If there are TiFlash nodes in the cluster, you can update the cluster to `v4.0.0-rc.2` or higher versions.
- Temporarily disable TiFlash if you do not want to upgrade the cluster.
### `tidb lightning encountered error: TiDB version too old, expected '>=4.0.0', found '3.0.18'`

TiDB Lightning Local-backend only supports importing data to TiDB clusters of v4.0.0 and later versions. If you try to use Local-backend to import data to a v2.x or v3.x cluster, the above error is reported. At this time, you can modify the configuration to use Importer-backend or TiDB-backend for data import.

Some `nightly` versions might be similar to v4.0.0-beta.2. These `nightly` versions of TiDB Lightning actually support Local-backend. If you encounter this error when using a `nightly` version, you can skip the version check by setting the configuration `check-requirements = false`. Before setting this parameter, make sure that the configuration of TiDB Lightning supports the corresponding version; otherwise, the import might fail.
### `restore table test.district failed: unknown columns in header [...]`

This error occurs usually because the CSV data file does not contain a header (the first row is not column names but data). Therefore, you need to add the following configuration to the TiDB Lightning configuration file:

```
[mydumper.csv]
header = false
```
