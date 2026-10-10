# ticloud project list command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-project-list.md`
- Source Title: `ticloud project list`
- Source Heading Path: `ticloud project list | ticloud project list > Examples | ticloud project list > Flags | ticloud project list > Inherited flags | ticloud project list > Feedback`
- Source Line Ranges: `5-53`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `cli`, `project`, `list`, `flags`, `output`, `json`, `profile`, `debug`, `help`, `feedback`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0879_599ec731eb`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-project-list.md#ticloud-project-list`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4fd620227b7558b7475299c05d7e52b6c443622dfb63bb2022a81ea9a3d43eb1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-project-list#ticloud-project-list
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-project-list.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to list all accessible projects with the TiDB Cloud CLI, including the alias command, output formats, or inherited flags.
- Retrieval Keywords: ticloud project list, ticloud project ls, List all accessible projects, ticloud project list -o json, --output, human, json, --profile, --debug, --no-color, --help, TiDB Cloud CLI project list
- Follow-up Guidance: The source also notes that to get a complete result, use the json output format and that required flags must be entered manually in non-interactive mode.
- Classification Note: This is a command reference for the TiDB Cloud CLI project listing command, including examples, command flags, inherited flags, and feedback information.

## Official Source Content

# ticloud project list

List all accessible projects:

```shell
ticloud project list [flags]
```

Or use the following alias command:

```shell
ticloud project ls [flags]
```
## Examples

List all accessible projects:

```shell
ticloud project list
```

List all accessible projects in the JSON format:

```shell
ticloud project list -o json
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                | Description                                                                                                              | Required | Note                                                 |
|---------------------|--------------------------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------|
| -h, --help          | Shows help information for this command.                                                                                       | No       | Works in both non-interactive and interactive modes. |
| -o, --output string | Specifies the output format (`human` by default). Valid values are `human` or `json`. To get a complete result, use the `json` format. | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                   | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
