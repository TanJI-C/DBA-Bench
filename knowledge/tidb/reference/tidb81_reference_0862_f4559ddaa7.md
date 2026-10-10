# ticloud serverless create command reference and flags

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/ticloud-cluster-create.md`
- Source Title: `ticloud serverless create`
- Source Heading Path: `ticloud serverless create | ticloud serverless create > Examples | ticloud serverless create > Flags | ticloud serverless create > Inherited flags | ticloud serverless create > Feedback`
- Source Line Ranges: `5-58`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `cli`, `serverless`, `cluster-creation`, `interactive-mode`, `non-interactive-mode`, `flags`, `profiles`, `debug`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0862_f4559ddaa7`
- Source ID: `tidb-docs-8.1:tidb-cloud/ticloud-cluster-create.md#ticloud-serverless-create`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7b7d66b5cd80784a52330c5446b1db4bf29fe308bc291d73c8a8164c49f1215f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-cluster-create#ticloud-serverless-create
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/ticloud-cluster-create.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the `ticloud serverless create` command syntax, examples, and required flags for interactive or non-interactive TiDB Cloud Serverless cluster creation.
- Retrieval Keywords: ticloud serverless create, Create a TiDB Cloud Serverless cluster, interactive mode, non-interactive mode, --display-name, --region, --spending-limit-monthly, --project-id, --disable-public-endpoint, --encryption, --profile, --debug, --no-color, ticloud serverless region
- Follow-up Guidance: The source also points to `ticloud serverless region` to see all regions and to the TiDB Cloud CLI GitHub issues page for feedback.
- Classification Note: This is a reference chunk because it provides command-line syntax, examples, flag definitions, inherited flags, and notes for the `ticloud serverless create` command.

## Official Source Content

# ticloud serverless create

Create a TiDB Cloud Serverless cluster:

```shell
ticloud serverless create [flags]
```
## Examples

Create a TiDB Cloud Serverless cluster in interactive mode:

```shell
ticloud serverless create
```

Create a TiDB Cloud Serverless cluster in non-interactive mode:

```shell
ticloud serverless create --display-name <display-name> --region <region>
```

Create a TiDB Cloud Serverless cluster with a spending limit in non-interactive mode:

```shell
ticloud serverless create --display-name <display-name> --region <region> --spending-limit-monthly <spending-limit-monthly>
``` 
## Flags

In non-interactive mode, you need to manually enter the required flags. In interactive mode, you can just follow CLI prompts to fill them in.

| Flag                         | Description                                                                                                    | Required | Note                                                |
|------------------------------|----------------------------------------------------------------------------------------------------------------|----------|-----------------------------------------------------|
| -n --display-name string     | Specifies the name of the cluster to be created.                                                               | Yes      | Only works in non-interactive mode.                 |
| --spending-limit-monthly int | Specifies the maximum monthly spending limit in USD cents.                                                     | No       | Only works in non-interactive mode.                 |
| -p, --project-id string      | Specifies the ID of the project, in which the cluster will be created. The default value is `default project`. | No       | Only works in non-interactive mode.                 |
| -r, --region string          | Specifies the name of cloud region. You can use "ticloud serverless region" to see all regions.                          | Yes      | Only works in non-interactive mode.                 |
| --disable-public-endpoint    | Disables the public endpoint.                                                                       | No       | Only works in non-interactive mode.                 |
| --encryption                 | Enables enhanced encryption at rest.                                                                | No       | Only works in non-interactive mode.                 |
| -h, --help                   | Shows help information for this command.                                                                       | No       | Works in both non-interactive and interactive modes |
## Inherited flags

| Flag                 | Description                                                                                          | Required | Note                                                                                                             |
|----------------------|------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------------------|
| --no-color           | Disables color in output.                                                                            | No       | Only works in non-interactive mode. In interactive mode, disabling color might not work with some UI components. |
| -P, --profile string | Specifies the active [user profile](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#user-profile) used in this command. | No       | Works in both non-interactive and interactive modes.                                                             |
| -D, --debug          | Enables debug mode.                                                                                   | No       | Works in both non-interactive and interactive modes.                                                             |
## Feedback

If you have any questions or suggestions on the TiDB Cloud CLI, feel free to create an [issue](https://github.com/tidbcloud/tidbcloud-cli/issues/new/choose). Also, we welcome any contributions.
