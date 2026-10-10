# ticloud ai command usage, flags, and feedback

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-ai.md`
- Source Title: `ticloud ai`
- Source Heading Path: `ticloud ai | ticloud ai > Examples | ticloud ai > Flags | ticloud ai > Inherited flags | ticloud ai > Feedback`
- Source Line Ranges: `5-47`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `ai`, `interactive-mode`, `non-interactive-mode`, `flags`, `user-profile`, `debug`, `help`, `feedback`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0844_c59e75d6b4`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-ai.md#ticloud-ai`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c50301db164a708851654fe150b8ee391ada07d30251dd3ed55eebaba7f3a487`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-ai#ticloud-ai
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-ai.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the `ticloud ai` command syntax, examples for interactive or non-interactive mode, supported flags, inherited flags, or the feedback link for TiDB Cloud CLI.
- Retrieval Keywords: ticloud ai, Chat with TiDB Bot, interactive mode, non-interactive mode, ticloud ai -q "How to create a cluster?", -q, --query string, -h, --help, --no-color, -P, --profile string, -D, --debug, user profile, TiDB Cloud CLI issue
- Follow-up Guidance: The source also points to creating an issue at `https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose` for questions or suggestions on the TiDB Cloud CLI.
- Classification Note: This is reference content because it lists the `ticloud ai` command usage, examples, flags, inherited flags, and feedback information for the cloud CLI.

## Official Source Content

# ticloud ai

Chat with TiDB Bot:

```shell
ticloud ai [flags]
```
## Examples

Chat with TiDB Bot in interactive mode:

```shell
ticloud ai
```

Chat with TiDB Bot in non-interactive mode:

```shell
ticloud ai -q "How to create a cluster?"
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag               | Description                       | Required | Note                                                 |
|--------------------|-----------------------------------|----------|------------------------------------------------------|
| -q, --query string | Specifies your query to TiDB Bot.   | Yes      | Only works in non-interactive mode.                  |
| -h, --help         | Shows help information for this command. | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                | Required | Note                                                                                                             |
|----------------------|--------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                  | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                         | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
