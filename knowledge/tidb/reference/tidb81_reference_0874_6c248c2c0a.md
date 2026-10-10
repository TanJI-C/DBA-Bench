# ticloud help command usage, flags, and feedback

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-help.md`
- Source Title: `ticloud help`
- Source Heading Path: `ticloud help | ticloud help > Examples | ticloud help > Flags | ticloud help > Inherited flags | ticloud help > Feedback`
- Source Line Ranges: `5-46`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `cli`, `help`, `command-syntax`, `examples`, `flags`, `interactive-mode`, `non-interactive-mode`, `profile`, `debug`, `feedback`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0874_6c248c2c0a`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-help.md#ticloud-help`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `09a37ffa7fc1f5ccae7a38ca2e7cae8475dd46ada1e848e987b5d9ce0075a936`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-help#ticloud-help
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-help.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI help command syntax, examples for subcommand help, or the available help-related flags and inherited flags.
- Retrieval Keywords: ticloud help, ticloud help [command] [flags], ticloud help auth, ticloud help serverless create, -h, --help, --no-color, -P, --profile string, -D, --debug, non-interactive mode, interactive mode, Feedback, TiDB Cloud CLI issue
- Follow-up Guidance: The source also points users with questions or suggestions on the TiDB Cloud CLI to create an issue and notes that contributions are welcome.
- Classification Note: This is classified as reference content because it documents the command usage, examples, flags, inherited flags, and feedback entry for `ticloud help`.

## Official Source Content

# ticloud help

Get help information for any command in TiDB Cloud CLI:

```shell
ticloud help [command] [flags]
```
## Examples

To get help for the `auth` command:

```shell
ticloud help auth
```

To get help for the `serverless create` command:

```shell
ticloud help serverless create
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                    | Description                                                   | Required | Note                                                 |
|-------------------------|---------------------------------------------------------------|----------|------------------------------------------------------|
| -h, --help              | Shows help information for this command.                      | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                               | Required | Note                                                                                                                    |
|----------------------|-------------------------------------------------------------------------------------------|----------|--------------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                  | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                                      |
| -D, --debug          | Enables debug mode.                                                                                   | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
