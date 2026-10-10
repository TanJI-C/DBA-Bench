# tiup cluster template command usage and options

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-template.md`
- Source Title: `tiup cluster template`
- Source Heading Path: `tiup cluster template | tiup cluster template > Syntax | tiup cluster template > Options | tiup cluster template > Options > --full | tiup cluster template > Options > --local | tiup cluster template > Options > --multi-dc | tiup cluster template > Options > -h, --help | tiup cluster template > Output`
- Source Line Ranges: `5-51`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `tidb`, `tikv`, `tiflash`, `shared`
- Topic Tags: `topology-file`, `deployment-template`, `command-syntax`, `command-options`, `local-cluster`, `multi-dc`, `help-output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1015_a7163050fb`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-template.md#tiup-cluster-template`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0f82999662fcb855506793f957096d494aeda85564c6eef3d52a94e188d84aeb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-template#tiup-cluster-template
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-template.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, default output, or flags of the `tiup cluster template` command that prints a built-in topology file template before deployment.
- Retrieval Keywords: tiup cluster template, tiup cluster template [flags], topology file, built-in topology file template, --full, --local, --multi-dc, -h, --help, default template, simple topology template, detailed topology template, multiple data centers, single data center, local cluster, 3 PD instances, 3 TiKV instances, 3 TiDB instances, 2 TiFlash instances, 1 Prometheus instance, 1 Grafana instance, 1 Alertmanager instance
- Follow-up Guidance: The output topology template can be redirected to the topology file for deployment.
- Classification Note: This is reference content because it defines command syntax, command options, and the exact default template output of `tiup cluster template`.

## Official Source Content

# tiup cluster template

Before deploying the cluster, you need to prepare a [topology file](https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference) of the cluster. TiUP has a built-in topology file template, and you can modify this template to create the final topology file. To output the built-in template content, you can use the `tiup cluster template` command.
## Syntax

```shell
tiup cluster template [flags]
```

If this option is not specified, the output default template contains the following instances:

- 3 PD instances
- 3 TiKV instances
- 3 TiDB instances
- 2 TiFlash instances
- 1 Prometheus instance
- 1 Grafana instance
- 1 Alertmanager instance
## Options
### --full

- Outputs a detailed topology template that is commented with configurable parameters. To enable this option, add it to the command.
- If this option is not specified, the simple topology template is output by default.
### --local

- Outputs a simple topology template for the local cluster, which can be used directly, and the `global` parameter can be adjusted as needed.
- This template creates a PD service, a TiDB service, a TiKV service, a Prometheus service, and a Grafana service.
### --multi-dc

- Outputs the topology template of multiple data centers. To enable this option, add it to the command.
- If this option is not specified, the topology template of a single data center is output by default.
### -h, --help

Prints the help information.
## Output

Outputs the topology template according to the specified options, which can be redirected to the topology file for deployment.

[<< Back to the previous page - TiUP Cluster command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster#command-list)
