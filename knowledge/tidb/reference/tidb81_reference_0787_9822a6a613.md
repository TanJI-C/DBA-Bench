# TiDB Cloud CLI overview, setup, commands, and modes

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/cli-reference.md`
- Source Title: `TiDB Cloud CLI Reference`
- Source Heading Path: `TiDB Cloud CLI Reference (Beta) | TiDB Cloud CLI Reference (Beta) > Before you begin | TiDB Cloud CLI Reference (Beta) > Commands available | TiDB Cloud CLI Reference (Beta) > Command modes`
- Source Line Ranges: `5-51`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`, `tiup`
- Topic Tags: `cli`, `beta`, `setup`, `commands`, `interactive-mode`, `non-interactive-mode`, `subcommands`, `shell-completion`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0787_9822a6a613`
- Source ID: `tidb-docs-8.1:tidb-cloud/cli-reference.md#tidb-cloud-cli-reference-beta`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d987786815979e1af636890e191a87d70179d62099e50d8c83fa0e60305ee5f6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference#tidb-cloud-cli-reference-beta
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/cli-reference.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB Cloud CLI beta overview, the available command groups and subcommands, or the difference between interactive mode and non-interactive mode.
- Retrieval Keywords: TiDB Cloud CLI Reference (Beta), ticloud, tiup cloud, auth login logout whoami, serverless create delete describe list update spending-limit region shell, serverless branch create delete describe list shell, serverless import cancel describe list start, serverless export create describe list cancel download, serverless sql-user create list delete update, serverless audit-log config describe filter-rule filter download, ai, completion bash fish powershell zsh, config create delete describe edit list set use, project list, upgrade, help, interactive mode, non-interactive mode, ticloud config create --profile-name <profile-name> --public-key <public-key> --private-key <private-key>
- Follow-up Guidance: Before using the CLI, the source says to set up your TiDB Cloud CLI environment and install the `ticloud` CLI.
- Classification Note: This is reference content because it lists the TiDB Cloud CLI commands, command syntax, and command modes for TiDB Cloud.

## Official Source Content

# TiDB Cloud CLI Reference (Beta)

> **Note:**
>
> TiDB Cloud CLI is in beta.

TiDB Cloud CLI is a command line interface, which allows you to operate TiDB Cloud from your terminal with a few lines of commands. In the TiDB Cloud CLI, you can easily manage your TiDB Cloud clusters, import data to your clusters, and perform more operations.
## Before you begin

Make sure to first [set up your TiDB Cloud CLI environment](https://docs.pingcap.com/tidb/stable/tidb-cloud/get-started-with-cli). Once you have installed the `ticloud` CLI, you can use it to manage your TiDB Cloud clusters from the command lines.
## Commands available

The following table lists the commands available for the TiDB Cloud CLI.

To use the `ticloud` CLI in your terminal, run `ticloud [command] [subcommand]`. If you are using [TiUP](https://docs.pingcap.com/tidb/stable/tiup-overview), use `tiup cloud [command] [subcommand]` instead.

| Command               | Subcommand                                                            | Description                                    |
|-----------------------|-----------------------------------------------------------------------|------------------------------------------------|
| auth                  | login, logout, whoami                                                 | Login and logout                               |
| serverless (alias: s) | create, delete, describe, list, update, spending-limit, region, shell | Manage TiDB Cloud Serverless clusters          |
| serverless branch     | create, delete, describe, list, shell                                 | Manage TiDB Cloud Serverless branches          |
| serverless import     | cancel, describe, list, start                                         | Manage TiDB Cloud Serverless import tasks      |
| serverless export     | create, describe, list, cancel, download                              | Manage TiDB Cloud Serverless export tasks      |
| serverless sql-user   | create, list, delete, update                                          | Manage TiDB Cloud Serverless SQL users         |
| serverless audit-log  | config, describe, filter-rule (alias: filter), download                                    | Manage TiDB Cloud Serverless database audit logging         |
| ai                    | -                                                                     | Chat with TiDB Bot                             |
| completion            | bash, fish, powershell, zsh                                           | Generate completion script for specified shell |
| config                | create, delete, describe, edit, list, set, use                        | Configure user profiles                        |
| project               | list                                                                  | Manage projects                                |
| upgrade                | -                                                                     | Update the CLI to the latest version           |
| help                  | auth, config, serverless, ai, project, upgrade, help, completion            | View help for any command                      |
## Command modes

The TiDB Cloud CLI provides two modes for some commands for easy use:

- Interactive mode

    You can run a command without flags (such as `ticloud config create`), and the CLI prompts you for input.

- Non-interactive mode

    You must provide all arguments and flags that are required when running a command, such as `ticloud config create --profile-name <profile-name> --public-key <public-key> --private-key <private-key>`.
