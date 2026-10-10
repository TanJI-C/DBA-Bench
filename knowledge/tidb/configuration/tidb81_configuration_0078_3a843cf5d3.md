# DM online DDL tool support and task configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-online-ddl-tool-support.md`
- Source Title: `TiDB Data Migration Support for Online DDL Tools`
- Source Heading Path: `TiDB Data Migration Support for Online DDL Tools | TiDB Data Migration Support for Online DDL Tools > Restrictions | TiDB Data Migration Support for Online DDL Tools > Configure parameters`
- Source Line Ranges: `5-55`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `online-ddl`, `gh-ost`, `pt-osc`, `task-configuration`, `incremental-replication`, `checkpoint`, `restrictions`, `deprecation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0078_3a843cf5d3`
- Source ID: `tidb-docs-8.1:dm/dm-online-ddl-tool-support.md#tidb-data-migration-support-for-online-ddl-tools`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b52ffb4ed560536f363c9d77d4b9ceb0841ab5b367d4c580ae6990aad73ac2f0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-online-ddl-tool-support#tidb-data-migration-support-for-online-ddl-tools
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-online-ddl-tool-support.md

## Retrieval Guidance

- Use When: Use this chunk when you need DM's documented support, restrictions, or task configuration for gh-ost and pt-osc online DDL tools.
- Retrieval Keywords: TiDB Data Migration Support for Online DDL Tools, DM only supports gh-ost and pt-osc, online-ddl, online-ddl-scheme, task configuration file, checkpoint corresponding to incremental replication, v2.0.5 and later, earlier than v2.0.5
- Follow-up Guidance: Check the task configuration file for the appropriate `online-ddl` or `online-ddl-scheme` setting and the listed checkpoint restriction.
- Classification Note: This chunk classifies as DM configuration content because it documents online DDL tool support, restrictions, and task parameters.

## Official Source Content

# TiDB Data Migration Support for Online DDL Tools

In the MySQL ecosystem, tools such as gh-ost and pt-osc are widely used. TiDB Data Migration (DM) provides supports for these tools to avoid migrating unnecessary intermediate data.

This document introduces the support for common online DDL tools, usage, and precautions in DM.

For the working principles and implementation methods of DM for online DDL tools, refer to [online-ddl](https://docs.pingcap.com/tidb/stable/dm/feature-online-ddl).
## Restrictions

- DM only supports gh-ost and pt-osc.
- When `online-ddl` is enabled, the checkpoint corresponding to incremental replication should not be in the process of online DDL execution. For example, if an upstream online DDL operation starts at `position-A` and ends at `position-B` of the binlog, the starting point of incremental replication should be earlier than `position-A` or later than `position-B`; otherwise, an error occurs. For details, refer to [FAQ](https://docs.pingcap.com/tidb/stable/dm/dm-faq#how-to-handle-the-error-returned-by-the-ddl-operation-related-to-the-gh-ost-table-after-online-ddl-true-is-set).
## Configure parameters

<div label="v2.0.5 and later">

In v2.0.5 and later versions, you need to use the `online-ddl` configuration item in the `task` configuration file.

- If the upstream MySQL/MariaDB (at the same time) uses the gh-ost or pt-osc tool, set `online-ddl` to `true` in the task configuration file:

```yml
online-ddl: true
```

> **Note:**
>
> Since v2.0.5, `online-ddl-scheme` has been deprecated, so you need to use `online-ddl` instead of `online-ddl-scheme`. That means that setting `online-ddl: true` overwrites `online-ddl-scheme`, and setting `online-ddl-scheme: "pt"` or `online-ddl-scheme: "gh-ost"` is converted to `online-ddl: true`.

</div>

<div label="earlier than v2.0.5">

Before v2.0.5 (not including v2.0.5), you need to use the `online-ddl-scheme` configuration item in the `task` configuration file.

- If the upstream MySQL/MariaDB uses the gh-ost tool, set it in the task configuration file:

```yml
online-ddl-scheme: "gh-ost"
```

- If the upstream MySQL/MariaDB uses the pt tool, set it in the task configuration file:

```yml
online-ddl-scheme: "pt"
```

</div>
