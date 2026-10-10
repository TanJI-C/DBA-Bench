# ticloud completion command reference and flags

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-completion.md`
- Source Title: `ticloud completion`
- Source Heading Path: `ticloud completion | ticloud completion > Examples | ticloud completion > Flags | ticloud completion > Inherited flags | ticloud completion > Feedback`
- Source Line Ranges: `5-46`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `cli`, `autocomplete`, `shell`, `flags`, `interactive-mode`, `non-interactive-mode`, `user-profile`, `debug`, `help`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0866_4d3583666d`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-completion.md#ticloud-completion`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `502dd89b3208d37693bb9600f31e1b3800317adc8d697553b9717ffd4e37c79d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-completion#ticloud-completion
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-completion.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI command that generates shell autocompletion scripts and its supported flags or usage modes.
- Retrieval Keywords: ticloud completion, Generate the autocompletion script for the specified shell of TiDB Cloud CLI, ticloud completion bash, ticloud completion zsh, --help, --no-color, --profile, --debug, interactive mode, non-interactive mode, user profile
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue page for questions, suggestions, and contributions.
- Classification Note: This is reference content because it defines the ticloud completion command syntax, examples, and flag behavior for TiDB Cloud CLI.

## Official Source Content

# ticloud completion

Generate the autocompletion script for the specified shell of TiDB Cloud CLI:

```shell
ticloud completion [command]
```
## Examples

Generate the autocompletion script for bash:

```shell
ticloud completion bash
```

Generate the autocompletion script for zsh:

```shell
ticloud completion zsh
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
