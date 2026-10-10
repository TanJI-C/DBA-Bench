# ticloud config describe command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-config-describe.md`
- Source Title: `ticloud config describe`
- Source Heading Path: `ticloud config describe | ticloud config describe > Examples | ticloud config describe > Flags | ticloud config describe > Inherited flags | ticloud config describe > Feedback`
- Source Line Ranges: `5-44`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `user-profile`, `command-syntax`, `examples`, `flags`, `debug`, `help`, `output-format`, `feedback`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0869_893d84db67`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-config-describe.md#ticloud-config-describe`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `685d11457270a2dc9066b6da59a79ccf8d45ed2a6d60b2d4a8376408a8acb3c2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-config-describe#ticloud-config-describe
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-config-describe.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI syntax, alias, examples, or flags for describing a specific user profile with the config command.
- Retrieval Keywords: ticloud config describe, ticloud config get, ticloud config describe <profile-name>, ticloud config get <profile-name>, user profile, TiDB Cloud CLI, --help, --no-color, --profile, --debug, describe a user profile
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue page for questions, suggestions, and contributions.
- Classification Note: This is reference content because it provides command syntax, an alias command, an example invocation, and available flags for the cloud CLI command.

## Official Source Content

# ticloud config describe

Get the property information of a specific [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile):

```shell
ticloud config describe <profile-name> [flags]
```

Or use the following alias command:

```shell
ticloud config get <profile-name> [flags]
```
## Examples

Describe a user profile:

```shell
ticloud config describe <profile-name>
```
## Flags

| Flag       | Description              |
|------------|--------------------------|
| -h, --help | Shows help information for this command. |
## Inherited flags

| Flag                 | Description                                   | Required | Note                                                                                                                    |
|----------------------|-----------------------------------------------|----------|--------------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                      | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                                      |
| -D, --debug          | Enables debug mode.                                                                                   | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
