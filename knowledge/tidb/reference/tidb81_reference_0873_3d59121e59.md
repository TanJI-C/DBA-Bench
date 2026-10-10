# ticloud config use command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-config-use.md`
- Source Title: `ticloud config use`
- Source Heading Path: `ticloud config use | ticloud config use > Examples | ticloud config use > Flags | ticloud config use > Inherited flags | ticloud config use > Feedback`
- Source Line Ranges: `5-38`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `cli`, `profiles`, `flags`, `help`, `debug`, `user-profile`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0873_3d59121e59`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-config-use.md#ticloud-config-use`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `699f70539fc27cc1370d855f0eecda620f8bf13a3f89adb2d69554fa1832495c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-config-use#ticloud-config-use
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-config-use.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI command that sets a specified profile as the active user profile and its available flags.
- Retrieval Keywords: ticloud config use, Set a specified profile as the active user profile, ticloud config use <profile-name> [flags], ticloud config use test, --help, --no-color, --profile string, --debug, active user profile, TiDB Cloud CLI
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue page for questions, suggestions, and contributions.
- Classification Note: This is a reference entry because it documents the command syntax, example usage, flags, inherited flags, and feedback link for the cloud CLI command.

## Official Source Content

# ticloud config use

Set a specified profile as the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile):

```shell
ticloud config use <profile-name> [flags]
```
## Examples

Set the `test` profile as the active user profile:

```shell
ticloud config use test
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
