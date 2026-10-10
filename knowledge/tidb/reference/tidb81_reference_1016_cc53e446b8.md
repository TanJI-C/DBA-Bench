# tiup cluster tls command syntax, options, and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-tls.md`
- Source Title: `tiup cluster tls`
- Source Heading Path: `tiup cluster tls | tiup cluster tls > Syntax | tiup cluster tls > Options | tiup cluster tls > Options > --clean-certificate | tiup cluster tls > Options > --force | tiup cluster tls > Options > --reload-certificate | tiup cluster tls > Options > -h, --help | tiup cluster tls > Output`
- Source Line Ranges: `5-53`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `shared`
- Topic Tags: `tls`, `certificate-management`, `command-syntax`, `flags`, `self-signed-certificates`, `cluster-management`, `output-logs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1016_cc53e446b8`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-tls.md#tiup-cluster-tls`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9c714034281610659341b798aebece04d395cc9a6b9ea227abce8946ac3201dd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-tls#tiup-cluster-tls
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-tls.md

## Retrieval Guidance

- Use When: Use this when looking for the `tiup cluster tls` command syntax, its TLS-related flags, or the note about single PD node support.
- Retrieval Keywords: tiup cluster tls, tiup cluster tls <cluster-name> <enable/disable> [flags], --clean-certificate, --force, --reload-certificate, -h, --help, single PD node, Execution logs of the tiup-cluster command
- Follow-up Guidance: If the cluster has multiple PD nodes, scale in the PD nodes to one node before running `tiup cluster tls`.
- Classification Note: This is a command reference for enabling or disabling TLS between cluster components, including options and the output description.

## Official Source Content

# tiup cluster tls

The `tiup cluster tls` command is used to enable TLS (Transport Layer Security) between cluster components. It automatically generates and distributes self-signed certificates to each node in the cluster.
## Syntax

```shell
tiup cluster tls <cluster-name> <enable/disable> [flags]
```

`<cluster-name>` specifies the cluster for which you want to enable or disable TLS.

> **Note:**
>
> Currently, the `tiup cluster tls` command supports enabling or disabling TLS only for clusters with a single PD node. For clusters with multiple PD nodes, executing the `tiup cluster tls` command directly returns an error, because switching the TLS status can cause communication exceptions between PD nodes. To enable or disable TLS for a cluster with multiple PD nodes, first [`scale-in`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-scale-in) the PD nodes to one node, and then execute the `tiup cluster tls` command.
## Options
### --clean-certificate

- When you disable TLS, use this option to clean up previously generated certificates.
- Data type: `BOOLEAN`
- Default: `false`
- If you do not specify this option, old certificates might be reused when you enable TLS again.
### --force

- Forces enabling or disabling TLS, regardless of the cluster's current TLS status.
- Data type: `BOOLEAN`
- Default: `false`
- If you do not specify this option, the operation is skipped if the cluster is already in the requested state.
### --reload-certificate

- When you enable TLS, use this option to regenerate certificates.
- Data type: `BOOLEAN`
- Default: `false`
- If you do not specify this option, new certificates are not generated if certificates already exist.
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- Default: `false`
## Output

Execution logs of the tiup-cluster command.
