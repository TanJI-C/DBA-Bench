# ticloud config set command reference and flags

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-config-set.md`
- Source Title: `ticloud config set`
- Source Heading Path: `ticloud config set | ticloud config set > Examples | ticloud config set > Flags | ticloud config set > Inherited flags | ticloud config set > Feedback`
- Source Line Ranges: `5-66`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `cli`, `config`, `user-profile`, `api-key`, `api-url`, `flags`, `examples`, `help`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0872_ffd44fb0b6`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-config-set.md#ticloud-config-set`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `faaea1ed74b44e98bc8860e7bb60d6c3f03f8d72a97e3a805677a31b205427fb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-config-set#ticloud-config-set
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-config-set.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs the TiDB Cloud CLI syntax, configurable properties, examples, or flags for the `ticloud config set` command and user profile handling.
- Retrieval Keywords: ticloud config set, Configure the properties for the active user profile, public-key, private-key, api-url, https://api.tidbcloud.com, -P, --profile, -D, --debug, --no-color, ticloud config set public-key <public-key>, ticloud config set api-url https://api.tidbcloud.com
- Follow-up Guidance: The source also points to creating an issue in the `tidbcloud-cli` GitHub repository for questions or suggestions about the TiDB Cloud CLI.
- Classification Note: This is reference content because it defines the `ticloud config set` command syntax, supported properties, examples, and command flags for the cloud CLI.

## Official Source Content

# ticloud config set

Configure the properties for the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile):

```shell
ticloud config set <property-name> <value> [flags]
```

The properties that can be configured include `public-key`, `private-key`, and `api-url`.

| Properties  | Description                                                        | Required |
|-------------|--------------------------------------------------------------------|----------|
| public-key  | Specifies the public key of the TiDB Cloud API.                               | Yes      |
| private-key | Specifies the private key of the TiDB Cloud API.                              | Yes      |
| api-url     | Specifies the base API URL of TiDB Cloud (`https://api.tidbcloud.com` by default). | No       |

> **Note:**
>
> If you want to configure properties for a specific user profile, you can add the `-P` flag and specify the target user profile name in the command.
## Examples

Set the value of the public-key for the active profile:

```shell
ticloud config set public-key <public-key>
```

Set the value of the public-key for a specific profile `test`:

```shell
ticloud config set public-key <public-key> -P test
```

Set the API host:

```shell
ticloud config set api-url https://api.tidbcloud.com
```

> **Note:**
>
> The TiDB Cloud API URL is `https://api.tidbcloud.com` by default. Usually, you do not need to set up it.
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
