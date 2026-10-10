# TiDB Cloud CLI overview, prerequisites, and installation

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/get-started-with-cli.md`
- Source Title: `TiDB Cloud CLI Quick Start`
- Source Heading Path: `TiDB Cloud CLI Quick Start | TiDB Cloud CLI Quick Start > Before you begin | TiDB Cloud CLI Quick Start > Installation`
- Source Line Ranges: `5-87`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`, `tiup`
- Topic Tags: `cli`, `installation`, `prerequisites`, `beta`, `mysql-client`, `github-actions`, `tiup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0324_591fdde481`
- Source ID: `tidb-docs-8.1:tidb-cloud/get-started-with-cli.md#tidb-cloud-cli-quick-start`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6b6848d012384dd32b6f2ad629bc4d30a09f8f6ded0c63ca246a62699171ec4a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/get-started-with-cli#tidb-cloud-cli-quick-start
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/get-started-with-cli.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB Cloud CLI overview, prerequisite account information, or installation methods for ticloud and the MySQL command-line client on macOS, Linux, Windows, or GitHub Actions.
- Retrieval Keywords: TiDB Cloud CLI Quick Start, ticloud, TiDB Cloud CLI is in beta, Have a TiDB Cloud account, sign up for a free trial, Installation, curl https://raw.githubusercontent.com/tidbcloud/tidbcloud-cli/main/install.sh | sh, tiup install cloud, releases, setup-tidbcloud-cli, GitHub Actions, mysql-client, sudo apt-get install mysql-client, sudo yum install mysql, brew install mysql-client, mysql.exe, PATH environment variable
- Follow-up Guidance: The page continues with quick start steps to create a user profile or log in and then create a TiDB Cloud Serverless cluster.
- Classification Note: This is classified as a cloud operation chunk because the official content introduces the TiDB Cloud CLI, its prerequisites, and platform-specific installation procedures.

## Official Source Content

# TiDB Cloud CLI Quick Start

TiDB Cloud provides a command-line interface (CLI) [`ticloud`](https://github.com/tidbcloud/tidbcloud-cli) for you to interact with TiDB Cloud from your terminal with a few lines of commands. For example, you can easily perform the following operations using `ticloud`:

- Create, delete, and list your clusters.
- Import data to your clusters.
- Export data from your clusters.

> **Note:**
>
> TiDB Cloud CLI is in beta.
## Before you begin

- Have a TiDB Cloud account. If you do not have one, [sign up for a free trial](https://tidbcloud.com/free-trial).
## Installation

<div label="macOS/Linux">

For macOS or Linux, you can install `ticloud` using any of the following methods:

- Install via script (recommended)

    ```shell
    curl https://raw.githubusercontent.com/tidbcloud/tidbcloud-cli/main/install.sh | sh
    ```

- Install via [TiUP](https://tiup.io/)

    ```shell
    tiup install cloud
    ```

- Install manually

    Download the pre-compiled binaries from the [releases](https://github.com/tidbcloud/tidbcloud-cli/releases/latest) page and copy them to your desired location for installation.

- Install in GitHub Actions

    To set up `ticloud` in GitHub Action, use [`setup-tidbcloud-cli`](https://github.com/tidbcloud/setup-tidbcloud-cli).

Install the MySQL command-line client if you do not have it. You can install it via your package manager:

- Debian-based distributions:

    ```shell
    sudo apt-get install mysql-client
    ```

- RPM-based distributions:

    ```shell
    sudo yum install mysql
    ```

- macOS:

  ```shell
  brew install mysql-client
  ```

</div>

<div label="Windows">

For Windows, you can install `ticloud` using either of the following methods:

- Install manually

    Download the pre-compiled binaries from the [releases](https://github.com/tidbcloud/tidbcloud-cli/releases/latest) page and copy them to the desired location for installation.

- Install in GitHub Actions

    To set up `ticloud` in GitHub Actions, use [`setup-tidbcloud-cli`](https://github.com/tidbcloud/setup-tidbcloud-cli).

Install the MySQL command-line client if you do not have it. You can refer to the instructions in [MySQL Installer for Windows](https://dev.mysql.com/doc/refman/8.0/en/mysql-installer.html) for the installation. To launch `ticloud connect` on Windows, you need to have the directory containing `mysql.exe` in the PATH environment variable.

</div>
