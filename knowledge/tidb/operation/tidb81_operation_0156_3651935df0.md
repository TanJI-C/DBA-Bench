# Configure, start, and verify TiDB Lightning import

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/get-started-with-tidb-lightning.md`
- Source Title: `Quick Start for TiDB Lightning`
- Source Heading Path: `Quick Start for TiDB Lightning > Step 4: Start TiDB Lightning | Quick Start for TiDB Lightning > Step 5: Check data integrity | Quick Start for TiDB Lightning > Summary`
- Source Line Ranges: `59-115`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`, `pd`, `tikv`, `tiup`
- Topic Tags: `configuration`, `startup`, `import`, `verification`, `logs`, `pd-address`, `local-backend`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0156_3651935df0`
- Source ID: `tidb-docs-8.1:get-started-with-tidb-lightning.md#step-4-start-tidb-lightning`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `218d2c7ff9031df978e3e6c66bfda1eb5c34519f2828a243f1ac2652ad847537`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/get-started-with-tidb-lightning#step-4-start-tidb-lightning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/get-started-with-tidb-lightning.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to configure `tidb-lightning.toml`, start TiDB Lightning, and verify a successful import from the log output.
- Retrieval Keywords: Step 4: Start TiDB Lightning, Step 5: Check data integrity, tidb-lightning.toml, [lightning], [tikv-importer], backend = "local", sorted-kv-dir, [mydumper], data-source-dir, filter = ['*.*', '!mysql.*', '!sys.*', '!INFORMATION_SCHEMA.*', '!PERFORMANCE_SCHEMA.*', '!METRICS_SCHEMA.*', '!INSPECTION_SCHEMA.*'], cannot find schema, [tidb], status-port = 10080, pd-addr, Starting from v7.6.0, TiDB supports setting multiple PD addresses, nohup tiup tidb-lightning -config tidb-lightning.toml > nohup.out &, tidb lightning exit, TiDB Lightning FAQs, TiDB Lightning Overview
- Follow-up Guidance: If an error occurs, the source points to `TiDB Lightning FAQs`, and for more features and usage it points to `TiDB Lightning Overview`.
- Classification Note: This is classified as an operation chunk because it contains the configuration settings, startup command, and import verification details for running TiDB Lightning.

## Official Source Content

## Step 4: Start TiDB Lightning

> **Note:**
>
> The import method in this section is only suitable for testing and functional experience. For production environments, refer to [Migrate Large Datasets from MySQL to TiDB](https://docs.pingcap.com/tidb/stable/migrate-large-mysql-to-tidb)

1. Create the configuration file `tidb-lightning.toml` and fill in the following settings based on your cluster information:

    ```toml
    [lightning]
    # Logging
    level = "info"
    file = "tidb-lightning.log"

    [tikv-importer]
    # Configure the import mode
    backend = "local"
    # Sets the directory for temporarily storing the sorted key-value pairs. The target directory must be empty.
    sorted-kv-dir = "/mnt/ssd/sorted-kv-dir"

    [mydumper]
    # Local source data directory
    data-source-dir = "/data/my_datasource/"

    # Configures the wildcard rule. By default, all tables in the mysql, sys, INFORMATION_SCHEMA, PERFORMANCE_SCHEMA, METRICS_SCHEMA, and INSPECTION_SCHEMA system databases are filtered.
    # If this item is not configured, the "cannot find schema" error occurs when system tables are imported.
    filter = ['*.*', '!mysql.*', '!sys.*', '!INFORMATION_SCHEMA.*', '!PERFORMANCE_SCHEMA.*', '!METRICS_SCHEMA.*', '!INSPECTION_SCHEMA.*']
    [tidb]
    # Information of the target cluster
    host = "172.16.31.2"
    port = 4000
    user = "root"
    password = "rootroot"
    # Table schema information is fetched from TiDB via this status-port.
    status-port = 10080
    # The PD address of the cluster. Starting from v7.6.0, TiDB supports setting multiple PD addresses.
    pd-addr = "172.16.31.3:2379,56.78.90.12:3456"
    ```

2. Run `tidb-lightning`. To avoid the program exiting due to the `SIGHUP` signal when starting the program directly in the command line using `nohup`, it is recommended to put the `nohup` command in a script. For example:

    ```shell
    #!/bin/bash
    nohup tiup tidb-lightning -config tidb-lightning.toml > nohup.out &
    ```
## Step 5: Check data integrity

After the import is completed, TiDB Lightning exits automatically. If the import is successful, you can find `tidb lightning exit` in the last line of the log file.

If any error occurs, refer to [TiDB Lightning FAQs](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-faq).
## Summary

This tutorial briefly introduces what TiDB Lightning is and how to quickly deploy a TiDB Lightning cluster to import full backup data to the TiDB cluster.

For detailed features and usage about TiDB Lightning, refer to [TiDB Lightning Overview](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview).
