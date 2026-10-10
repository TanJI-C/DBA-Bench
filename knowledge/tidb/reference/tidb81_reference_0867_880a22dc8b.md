# ticloud config create command reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-config-create.md`
- Source Title: `ticloud config create`
- Source Heading Path: `ticloud config create | ticloud config create > Examples | ticloud config create > Flags | ticloud config create > Inherited flags | ticloud config create > Feedback`
- Source Line Ranges: `5-53`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `cli`, `user-profile`, `api-key`, `interactive-mode`, `non-interactive-mode`, `flags`, `authentication`, `debug`, `feedback`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0867_880a22dc8b`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-config-create.md#ticloud-config-create`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `53426383a4cc9962fe0188c671d1f74880551433d0ae45bc0040f40716d7280e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-config-create#ticloud-config-create
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-config-create.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud CLI command to create a user profile, including interactive or non-interactive usage and the required API key flags.
- Retrieval Keywords: ticloud config create, Create a user profile, user profile, interactive mode, non-interactive mode, --profile-name, --public-key, --private-key, TiDB Cloud API Key, -P, --profile, -D, --debug, --no-color
- Follow-up Guidance: The source also points to creating an issue in the tidbcloud-cli GitHub repository for questions or suggestions on the TiDB Cloud CLI.
- Classification Note: This is a cloud CLI reference page because it defines the ticloud config create command syntax, examples, flags, inherited flags, and feedback link.

## Official Source Content

# ticloud config create

Create a [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) to store user profile settings:

```shell
ticloud config create [flags]
```

> **Note:**
>
> Before creating a user profile, you need to [create a TiDB Cloud API Key](https://docs.pingcap.com/tidbcloud/api/v1beta#section/Authentication/API-Key-Management).
## Examples

Create a user profile in interactive mode:

```shell
ticloud config create
```

Create a user profile in non-interactive mode:

```shell
ticloud config create --profile-name <profile-name> --public-key <public-key> --private-key <private-key>
```
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                  | Description                                   | Required | Note                             |
|-----------------------|-----------------------------------------------|----------|-----------------------------------|
| -h, --help            | Shows help information for this command.                    | No       | Works in both non-interactive and interactive modes. |
| --private-key string  | Specifies the private key of the TiDB Cloud API.         | Yes      | Only works in non-interactive mode. |
| --profile-name string | Specifies the name of the profile (which must not contain `.`). | Yes      | Only works in non-interactive mode. |
| --public-key string   | Specifies the public key of the TiDB Cloud API.          | Yes      | Only works in non-interactive mode. |
## Inherited flags

| Flag                 | Description                                  | Required | Note                                                                                                                    |
|----------------------|----------------------------------------------|----------|--------------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                     | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                                      |
| -D, --debug          | Enables debug mode.                                                                                   | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
