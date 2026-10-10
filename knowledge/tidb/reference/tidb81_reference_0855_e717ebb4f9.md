# ticloud auth logout command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-auth-logout.md`
- Source Title: `ticloud auth logout`
- Source Heading Path: `ticloud auth logout | ticloud auth logout > Examples | ticloud auth logout > Inherited flags | ticloud auth logout > Feedback`
- Source Line Ranges: `5-32`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `authentication`, `logout`, `flags`, `profiles`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0855_e717ebb4f9`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-auth-logout.md#ticloud-auth-logout`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5e5706a6d88a63a3f25d6fbded097fb4051aebaad9e5714054204537990cf967`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auth-logout#ticloud-auth-logout
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-auth-logout.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI command reference for logging out, including the basic syntax, example invocation, and inherited flags.
- Retrieval Keywords: ticloud auth logout, Log out of TiDB Cloud, ticloud auth logout [flags], --no-color, -P, --profile string, -D, --debug, user profile, TiDB Cloud CLI
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue page for questions, suggestions, and contributions.
- Classification Note: This is a reference chunk because it documents the ticloud auth logout command syntax, example usage, and inherited flags for the cloud CLI.

## Official Source Content

# ticloud auth logout

Log out of TiDB Cloud:

```shell
ticloud auth logout [flags]
```
## Examples

To log out of TiDB Cloud:

```shell
ticloud auth logout
```
## Inherited flags

| Flag                 | Description                                                                                | Required | Note                                                                                                             |
|----------------------|--------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                  | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                          | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
