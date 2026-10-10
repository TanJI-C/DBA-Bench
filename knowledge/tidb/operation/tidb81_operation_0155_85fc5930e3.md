# Prepare backup data, deploy cluster, and install TiDB Lightning

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/get-started-with-tidb-lightning.md`
- Source Title: `Quick Start for TiDB Lightning`
- Source Heading Path: `Quick Start for TiDB Lightning | Quick Start for TiDB Lightning > Step 1: Prepare full backup data | Quick Start for TiDB Lightning > Step 2: Deploy the TiDB cluster | Quick Start for TiDB Lightning > Step 3: Install TiDB Lightning`
- Source Line Ranges: `5-58`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `dumpling`, `tiup`, `tidb`
- Topic Tags: `quickstart`, `import`, `backup-data`, `cluster-deployment`, `installation`, `tiup`, `dumpling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0155_85fc5930e3`
- Source ID: `tidb-docs-8.1:get-started-with-tidb-lightning.md#quick-start-for-tidb-lightning`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cedd4b7311d606312d6dd248ad09bab5dd3d378d068825c9f2f46f51c2ece730`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/get-started-with-tidb-lightning#quick-start-for-tidb-lightning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/get-started-with-tidb-lightning.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the quick-start steps to prepare MySQL backup data with Dumpling, deploy a TiDB cluster, and install TiDB Lightning with TiUP.
- Retrieval Keywords: Quick Start for TiDB Lightning, Prepare full backup data, Step 1: Prepare full backup data, Step 2: Deploy the TiDB cluster, Step 3: Install TiDB Lightning, tiup --version, tiup install dumpling, tiup dumpling -h 127.0.0.1 -P 3306 -u root -t 16 -F 256MB -B test -f 'test.t[12]' -o /data/my_database/, Use Dumpling to Export Data, tiup install tidb-lightning, Quick Start Guide for the TiDB Database Platform
- Follow-up Guidance: The next step is to create `tidb-lightning.toml` and start `tiup tidb-lightning` for the import.
- Classification Note: This is classified as an operation chunk because it provides procedural quick-start steps for backup preparation, cluster deployment, and TiDB Lightning installation in a self-managed test or trial setup.

## Official Source Content

# Quick Start for TiDB Lightning

This document provides a quick guide on getting started with TiDB Lightning by importing MySQL data into a TiDB cluster.

> **Warning:**
>
> The deployment method in this tutorial is only recommended for test and trial. **Do not apply it in the production or development environment.**
## Step 1: Prepare full backup data

First, you can use [dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview) to export data from MySQL.

1. Run `tiup --version` to check if TiUP is already installed. If TiUP is installed, skip this step. If TiUP is not installed, run the following command:

    ```
    curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh
    ```

2. Using TiUP to install Dumpling:

    ```shell
    tiup install dumpling
    ```

3. To export data from MySQL, you can refer to the detailed steps provided in [Use Dumpling to Export Data](https://docs.pingcap.com/tidb/stable/dumpling-overview#export-to-sql-files):

    ```sh
    tiup dumpling -h 127.0.0.1 -P 3306 -u root -t 16 -F 256MB -B test -f 'test.t[12]' -o /data/my_database/
    ```

    In the above command:

    - `-t 16`: Export data using 16 threads.
    - `-F 256MB`: Split each table into multiple files, with each file approximately 256 MB in size.
    - `-B test`: Export from the `test` database.
    - `-f 'test.t[12]'`: Export only the two tables `test.t1` and `test.t2`.

    The full backup data exported will be saved in the `/data/my_database` directory.
## Step 2: Deploy the TiDB cluster

Before starting the data import, you need to deploy a TiDB cluster for the import. If you already have a TiDB cluster, you can skip this step.

For the steps on deploying a TiDB cluster, refer to the [Quick Start Guide for the TiDB Database Platform](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb).
## Step 3: Install TiDB Lightning

Run the following command to install the latest version of TiDB Lightning:

```shell
tiup install tidb-lightning
```
