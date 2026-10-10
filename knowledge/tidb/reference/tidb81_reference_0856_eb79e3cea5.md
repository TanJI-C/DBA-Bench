# ticloud auth whoami command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-auth-whoami.md`
- Source Title: `ticloud auth whoami`
- Source Heading Path: `ticloud auth whoami | ticloud auth whoami > Examples | ticloud auth whoami > Flags | ticloud auth whoami > Inherited flags | ticloud auth whoami > Feedback`
- Source Line Ranges: `5-40`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cli`, `authentication`, `user-info`, `flags`, `profiles`, `debug`, `help`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0856_eb79e3cea5`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-auth-whoami.md#ticloud-auth-whoami`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `08fe5a0b2737a82148f04076346530c6c13a7080720ca8d6990c9fa89b529f3f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auth-whoami#ticloud-auth-whoami
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-auth-whoami.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI reference for displaying information about the current user with the whoami command and its supported flags.
- Retrieval Keywords: ticloud auth whoami, Display information about the current user, ticloud auth whoami [flags], --help, --no-color, --profile, -P, user profile, --debug, -D, interactive mode, non-interactive mode
- Follow-up Guidance: The source also points users with questions or suggestions on the TiDB Cloud CLI to create an issue in the tidbcloud-cli GitHub repository.
- Classification Note: This is reference content because it defines the ticloud auth whoami command syntax, example invocation, and available flags for TiDB Cloud CLI.

## Official Source Content

# ticloud auth whoami

Display information about the current user:

```shell
ticloud auth whoami [flags]
```
## Examples

To display information about the current user:

```shell
ticloud auth whoami
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag       | Description                              | Required | Note                                                 |
|------------|------------------------------------------|----------|------------------------------------------------------|
| -h, --help | Shows help information for this command. | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                  | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
