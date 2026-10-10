# ticloud upgrade command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-upgrade.md`
- Source Title: `ticloud upgrade`
- Source Heading Path: `ticloud upgrade | ticloud upgrade > Examples | ticloud upgrade > Flags | ticloud upgrade > Inherited flags | ticloud upgrade > Feedback`
- Source Line Ranges: `6-39`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `upgrade`, `command`, `flags`, `examples`, `help`, `profile`, `debug`, `feedback`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0898_0d5f81138b`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-upgrade.md#ticloud-upgrade`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1e923d653b20cd1b5479fec1dc85ea1d67bba606beb5846da97cd37f39459ae5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-upgrade#ticloud-upgrade
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-upgrade.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI command that upgrades the CLI to the latest version and its available flags.
- Retrieval Keywords: ticloud upgrade, Upgrade the TiDB Cloud CLI to the latest version, ticloud upgrade [flags], --help, -h, --no-color, --profile, -P, --debug, -D, TiDB Cloud CLI
- Follow-up Guidance: If there are questions or suggestions on the TiDB Cloud CLI, the content points to creating an issue in the tidbcloud-cli GitHub repository.
- Classification Note: This is a reference entry because it defines the ticloud upgrade command syntax, example invocation, flags, inherited flags, and feedback link.

## Official Source Content

# ticloud upgrade

Upgrade the TiDB Cloud CLI to the latest version:

```shell
ticloud upgrade [flags]
```
## Examples

Upgrade the TiDB Cloud CLI to the latest version:

```shell
ticloud upgrade
```
## Flags

| Flag       | Description                       |
|------------|-----------------------------------|
 | -h, --help | Shows help information for this command. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                   | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
