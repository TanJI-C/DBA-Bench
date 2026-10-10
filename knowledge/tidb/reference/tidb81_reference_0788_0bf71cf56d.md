# TiDB Cloud CLI global flags and feedback

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/cli-reference.md`
- Source Title: `TiDB Cloud CLI Reference`
- Source Heading Path: `TiDB Cloud CLI Reference (Beta) > Global flags | TiDB Cloud CLI Reference (Beta) > Feedback`
- Source Line Ranges: `118-130`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `global-flags`, `debug`, `profile`, `no-color`, `feedback`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0788_0bf71cf56d`
- Source ID: `tidb-docs-8.1:tidb-cloud/cli-reference.md#global-flags`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `eef682a0b21f639412c0a3a726e86353c53d1002a96c90f7a1a3ac51321ddb75`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#global-flags
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/cli-reference.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB Cloud CLI global flags or the official feedback channel for questions and suggestions.
- Retrieval Keywords: Global flags, --no-color, -P, --profile string, -D, --debug, Disables color in output, Specifies the active user profile used in this command, Enable debug mode, Only works in non-interactive mode, Works in both non-interactive and interactive modes, Feedback, issue, tidbcloud-cli/issues/new/choose
- Follow-up Guidance: The source says questions or suggestions on the TiDB Cloud CLI can be submitted by creating an issue.
- Classification Note: This is reference content because it enumerates global flags with notes about interactive and non-interactive modes and provides the feedback entry point.

## Official Source Content

## Global flags

The following table lists the global flags for the TiDB Cloud CLI.

| Flag                 | Description                                             | Required | Note                                                                                                             |
|----------------------|---------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                               | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active user profile used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enable debug mode                                       | No       | Works in both non-interactive and interactive modes.                                                          |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
