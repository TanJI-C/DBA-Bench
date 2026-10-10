# CLI usage, TiUP access, reference link, and feedback

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/get-started-with-cli.md`
- Source Title: `TiDB Cloud CLI Quick Start`
- Source Heading Path: `TiDB Cloud CLI Quick Start > Use the TiDB Cloud CLI | TiDB Cloud CLI Quick Start > Use the TiDB Cloud CLI > Use the TiDB Cloud CLI through TiUP | TiDB Cloud CLI Quick Start > What's next | TiDB Cloud CLI Quick Start > Feedback`
- Source Line Ranges: `126-174`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tiup`
- Topic Tags: `help`, `version`, `update`, `tiup`, `reference`, `feedback`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0326_0074da7784`
- Source ID: `tidb-docs-8.1:tidb-cloud/get-started-with-cli.md#use-the-tidb-cloud-cli`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d81b2822686d0dbc1f213047e5c4a9a5b30444cc0e39c21a985a7cf91323dee9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/get-started-with-cli#use-the-tidb-cloud-cli
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/get-started-with-cli.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs basic TiDB Cloud CLI usage commands, the TiUP-based cloud component commands, the CLI reference link, or the feedback issue channel.
- Retrieval Keywords: Use the TiDB Cloud CLI, ticloud --help, ticloud version, ticloud update, Use the TiDB Cloud CLI through TiUP, cloud component name, tiup cloud --help, tiup cloud serverless create, tiup update cloud, CLI reference, Feedback, issue, tidbcloud-cli/issues/new/choose
- Follow-up Guidance: The official content points users to the CLI reference to explore more features of TiDB Cloud CLI and to the GitHub issue page for questions or suggestions.
- Classification Note: This is classified as a cloud operation chunk because the official content describes CLI command usage, version checks, updates, TiUP access, and support links.

## Official Source Content

## Use the TiDB Cloud CLI

View all commands available:

```shell
ticloud --help
```

Verify that you are using the latest version:

```shell
ticloud version
```

If not, update to the latest version:

```shell
ticloud update
```
### Use the TiDB Cloud CLI through TiUP

The TiDB Cloud CLI is also available through [TiUP](https://tiup.io/), with the component name as `cloud`.

View all commands available:

```shell
tiup cloud --help
```

Run commands with `tiup cloud <command>`. For example:

```shell
tiup cloud serverless create
```

Update to the latest version by TiUP:

```shell
tiup update cloud
```
## What's next

Check out [CLI reference](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference) to explore more features of TiDB Cloud CLI.
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
