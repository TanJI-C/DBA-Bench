# Feature details for scalability and performance

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.0.md`
- Source Title: `TiDB 7.5.0 Release Notes`
- Source Heading Path: `TiDB 7.5.0 Release Notes > Feature details | TiDB 7.5.0 Release Notes > Feature details > Scalability | TiDB 7.5.0 Release Notes > Feature details > Performance`
- Source Line Ranges: `70-97`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `release-notes`, `feature-details`, `scalability`, `performance`, `dxf`, `add-index`, `import-into`, `service-scope`, `distributed-execution`, `system-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0519_f46eee8cf3`
- Source ID: `tidb-docs-8.1:releases/release-7.5.0.md#feature-details`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f4f0f1e804cd13e272ae241df22cd9c3b91a964e66205ba140a225fdf2d7f0e1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.0#feature-details
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 7.5.0 feature details about DXF scalability and performance, especially tidb_service_scope for isolating nodes for distributed ADD INDEX or IMPORT INTO tasks and tidb_enable_dist_task for enabling DXF.
- Retrieval Keywords: Feature details, Scalability, Performance, Distributed eXecution Framework, DXF, ADD INDEX, IMPORT INTO, tidb_service_scope, tidb_enable_dist_task, SET GLOBAL tidb_enable_dist_task = ON, multiple TiDB nodes, parallel execution, global sort, GA, improve the performance of adding multiple indexes in a single SQL statement
- Follow-up Guidance: The source includes an exact SQL statement to enable DXF and links to the tidb_service_scope system variable documentation and tidb-global-sort documentation.
- Classification Note: This is a TiDB feature-details release chunk because it gives detailed release-note behavior and configuration for TiDB scalability and performance features.

## Official Source Content

## Feature details
### Scalability

* Support designating and isolating TiDB nodes to distributedly execute `ADD INDEX` or `IMPORT INTO` tasks when the Distributed eXecution Framework (DXF) is enabled [#46258](https://github.com/pingcap/tidb/issues/46258) @[ywqzzy](https://github.com/ywqzzy)

    Executing `ADD INDEX` or `IMPORT INTO` tasks in parallel in a resource-intensive cluster can consume a large amount of TiDB node resources, which can lead to cluster performance degradation. To avoid performance impact on existing services, v7.4.0 introduces the system variable [`tidb_service_scope`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_service_scope-new-in-v740) as an experimental feature to control the service scope of each TiDB node under the [TiDB Distributed eXecution Framework (DXF)](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework). You can select several existing TiDB nodes or set the TiDB service scope for new TiDB nodes, and all distributedly executed `ADD INDEX` and `IMPORT INTO` tasks only run on these nodes. In v7.5.0, this feature becomes generally available (GA).

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/system-variables#tidb_service_scope-new-in-v740).
### Performance

* The TiDB Distributed eXecution Framework (DXF) becomes generally available (GA), improving the performance and stability of `ADD INDEX` and `IMPORT INTO` tasks in parallel execution [#45719](https://github.com/pingcap/tidb/issues/45719) @[wjhuang2016](https://github.com/wjhuang2016)

    The DXF introduced in v7.1.0 has become GA. In versions before TiDB v7.1.0, only one TiDB node can execute DDL tasks at the same time. Starting from v7.1.0, multiple TiDB nodes can execute the same DDL task in parallel under the DXF. Starting from v7.2.0, the DXF supports multiple TiDB nodes to execute the same `IMPORT INTO` task in parallel, thereby better utilizing the resources of the TiDB cluster and significantly improving the performance of DDL and `IMPORT INTO` tasks. In addition, you can also increase TiDB nodes to linearly improve the performance of these tasks.

    To use the DXF, set [`tidb_enable_dist_task`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_dist_task-new-in-v710) value to `ON`.

    ```sql
    SET GLOBAL tidb_enable_dist_task = ON;
    ```

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-global-sort).

* Improve the performance of adding multiple indexes in a single SQL statement [#41602](https://github.com/pingcap/tidb/issues/41602) @[tangenta](https://github.com/tangenta)

    Before v7.5.0, when you add multiple indexes (`ADD INDEX`) in a single SQL statement, the performance was similar to adding multiple indexes using separate SQL statements. Starting from v7.5.0, the performance of adding multiple indexes in a single SQL statement is significantly improved. Especially in scenarios with wide tables, internal test data shows that performance can be improved by up to 94%.
