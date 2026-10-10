# ticloud auth login command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-auth-login.md`
- Source Title: `ticloud auth login`
- Source Heading Path: `ticloud auth login | ticloud auth login > Examples | ticloud auth login > Flags | ticloud auth login > Inherited flags | ticloud auth login > Feedback`
- Source Line Ranges: `5-47`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `authentication`, `login`, `cli`, `flags`, `interactive-mode`, `non-interactive-mode`, `profiles`, `debug`, `credential-storage`, `help`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0854_a339321d06`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-auth-login.md#ticloud-auth-login`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cb046876dafc9c9eff65f42a1ed4cd417b8df091eba35965158f0f4aac7068a0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-auth-login#ticloud-auth-login
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-auth-login.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI command syntax, examples, and flags for authenticating with `ticloud auth login` in interactive or non-interactive mode.
- Retrieval Keywords: ticloud auth login, Authenticate with TiDB Cloud, ticloud auth login [flags], --insecure-storage, plain text instead of credential store, interactive mode, non-interactive mode, --no-color, -P --profile, -D --debug, -h --help, user profile
- Follow-up Guidance: The source also points to the TiDB Cloud CLI GitHub issue page for questions, suggestions, and contributions.
- Classification Note: This is reference content because it documents the `ticloud auth login` command, examples, and supported flags for the TiDB Cloud CLI.

## Official Source Content

# ticloud auth login

Authenticate with TiDB Cloud:

```shell
ticloud auth login [flags]
```
## Examples

To log into TiDB Cloud:

```shell
ticloud auth login
```

To log into TiDB Cloud with insecure storage:

```shell
ticloud auth login --insecure-storage
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag               | Description                                                               | Required | Note                                                 |
|--------------------|---------------------------------------------------------------------------|----------|------------------------------------------------------|
| --insecure-storage | Saves authentication credentials in plain text instead of credential store. | No       | Works in both non-interactive and interactive modes. |
| -h, --help         | Shows help information for this command.                                         | No       | Works in both non-interactive and interactive modes. |
## Inherited flags

| Flag                 | Description                                                                                | Required | Note                                                                                                             |
|----------------------|--------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                  | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                          | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
