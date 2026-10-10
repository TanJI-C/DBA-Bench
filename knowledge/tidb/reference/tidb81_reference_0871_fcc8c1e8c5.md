# ticloud config list command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-config-list.md`
- Source Title: `ticloud config list`
- Source Heading Path: `ticloud config list | ticloud config list > Examples | ticloud config list > Flags | ticloud config list > Inherited flags | ticloud config list > Feedback`
- Source Line Ranges: `5-44`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `cli`, `config`, `user-profiles`, `flags`, `help`, `debug`, `output`, `examples`, `feedback`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0871_fcc8c1e8c5`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-config-list.md#ticloud-config-list`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `89a7096ff61c01de7413e35d59b0184cf78f0816408615eab1794bfa90c28d2f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-config-list#ticloud-config-list
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-config-list.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI command that lists all user profiles and its alias, examples, or supported flags.
- Retrieval Keywords: ticloud config list, ticloud config ls, List all user profiles, user profiles, TiDB Cloud CLI, --help, --no-color, --profile, --debug, list all user profiles available
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue page for questions, suggestions, and contributions.
- Classification Note: This is a reference entry for the cloud CLI command `ticloud config list`, including syntax, alias, example usage, flags, inherited flags, and feedback information.

## Official Source Content

# ticloud config list

List all [user profiles](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile):

```shell
ticloud config list [flags]
```

Or use the following alias command:

```shell
ticloud config ls [flags]
```
## Examples

List all user profiles available:

```shell
ticloud config list
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
