# DXF prerequisites and enablement

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-distributed-execution-framework.md`
- Source Title: `TiDB Distributed eXecution Framework (DXF)`
- Source Heading Path: `TiDB Distributed eXecution Framework (DXF) > Prerequisites | TiDB Distributed eXecution Framework (DXF) > Usage`
- Source Line Ranges: `45-91`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `prerequisites`, `fast-online-ddl`, `system-variables`, `temp-dir`, `enablement`, `distributed-ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0329_c80b03a193`
- Source ID: `tidb-docs-8.1:tidb-distributed-execution-framework.md#prerequisites`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `42ea50b2f22d3bbc917aa7a0754fc5082f941ad947b3328df2cbf30c2ecb6af3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework#prerequisites
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-distributed-execution-framework.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks how to enable DXF, what prerequisites apply to distributed ADD INDEX tasks, or which Fast Online DDL and DXF variables are involved.
- Retrieval Keywords: tidb_enable_dist_task, SET GLOBAL tidb_enable_dist_task = ON, tidb_ddl_enable_fast_reorg, tidb_ddl_disk_quota, temp-dir, Fast Online DDL, ADD INDEX prerequisites, distributed DDL execution, tidb_ddl_reorg_worker_cnt, tidb_ddl_reorg_priority, tidb_ddl_error_count_limit, tidb_ddl_reorg_batch_size
- Follow-up Guidance: The source notes that when DXF tasks are running, supported statements such as ADD INDEX and IMPORT INTO are executed in a distributed manner and all TiDB nodes run DXF tasks by default.
- Classification Note: This is classified as configuration because the content centers on system variables, a configuration item, and SQL used to enable and tune DXF-related behavior.

## Official Source Content

## Prerequisites

Before using the DXF to execute [`ADD INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-index) tasks, you need to enable the [Fast Online DDL](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_enable_fast_reorg-new-in-v630) mode.

1. Adjust the following system variables related to Fast Online DDL:

    * [`tidb_ddl_enable_fast_reorg`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_enable_fast_reorg-new-in-v630): used to enable Fast Online DDL mode. It is enabled by default starting from TiDB v6.5.0.
    * [`tidb_ddl_disk_quota`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_disk_quota-new-in-v630): used to control the maximum quota of local disks that can be used in Fast Online DDL mode.

2. Adjust the following configuration item related to Fast Online DDL:

    * [`temp-dir`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#temp-dir-new-in-v630): specifies the local disk path that can be used in Fast Online DDL mode.

> **Note:**
>
> It is recommended that you prepare at least 100 GiB of free space for the TiDB `temp-dir` directory.

Adjust the following system variables related to Fast Online DDL:

* [`tidb_ddl_enable_fast_reorg`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_enable_fast_reorg-new-in-v630): used to enable Fast Online DDL mode. It is enabled by default starting from TiDB v6.5.0.
* [`tidb_ddl_disk_quota`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_disk_quota-new-in-v630): used to control the maximum quota of local disks that can be used in Fast Online DDL mode.
## Usage

1. To enable the DXF, set the value of [`tidb_enable_dist_task`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_dist_task-new-in-v710) to `ON`. Starting from v8.1.0, this variable is enabled by default. For newly created clusters of v8.1.0 or later versions, you can skip this step.

    ```sql
    SET GLOBAL tidb_enable_dist_task = ON;
    ```

    When the DXF tasks are running, the statements supported by the framework (such as [`ADD INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-index) and [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into)) are executed in a distributed manner. All TiDB nodes run DXF tasks by default.

2. In general, for the following system variables that might affect the distributed execution of DDL tasks, it is recommended that you use their default values:

    * [`tidb_ddl_reorg_worker_cnt`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_reorg_worker_cnt): use the default value `4`. The recommended maximum value is `16`.
    * [`tidb_ddl_reorg_priority`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_reorg_priority)
    * [`tidb_ddl_error_count_limit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_error_count_limit)
    * [`tidb_ddl_reorg_batch_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_reorg_batch_size): use the default value. The recommended maximum value is `1024`.
