# ticloud config delete command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-config-delete.md`
- Source Title: `ticloud config delete`
- Source Heading Path: `ticloud config delete | ticloud config delete > Examples | ticloud config delete > Flags | ticloud config delete > Inherited flags | ticloud config delete > Feedback`
- Source Line Ranges: `5-45`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `cli`, `config`, `delete`, `user-profile`, `flags`, `examples`, `help`, `debug`, `non-interactive`, `interactive`, `feedback`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0868_7a790fdc4d`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-config-delete.md#ticloud-config-delete`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a6b77957e9601d31887557443392c3f33456083a85e25b5bd55d23b2028f5862`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-config-delete#ticloud-config-delete
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-config-delete.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI command syntax, alias, flags, or examples for deleting a user profile.
- Retrieval Keywords: ticloud config delete, ticloud config rm, Delete a user profile, ticloud config delete <profile-name> [flags], --force, -h, --help, --no-color, -P, --profile string, -D, --debug, inherited flags, non-interactive mode, interactive mode
- Follow-up Guidance: The source also points users to create an issue in the TiDB Cloud CLI GitHub repository for questions, suggestions, or contributions.
- Classification Note: This is reference content because it defines the command usage, alias, examples, flags, inherited flags, and feedback link for the cloud CLI command.

## Official Source Content

# ticloud config delete

Delete a [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile):

```shell
ticloud config delete <profile-name> [flags]
```

Or use the following alias command:

```shell
ticloud config rm <profile-name> [flags]
```
## Examples

Delete a user profile:

```shell
ticloud config delete <profile-name>
```
## Flags

| Flag       | Description                           |
|------------|---------------------------------------|
| --force    | Deletes a profile without confirmation. |
| -h, --help | Shows help information for this command.            |
## Inherited flags

| Flag                 | Description                                   | Required | Note                                                                                                                    |
|----------------------|-----------------------------------------------|----------|--------------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                      | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                                      |
| -D, --debug          | Enables debug mode.                                                                                   | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
