# Reliability feature: cross-database execution plan binding

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.6.0.md`
- Source Title: `TiDB 7.6.0 Release Notes`
- Source Heading Path: `TiDB 7.6.0 Release Notes > Feature details > Reliability`
- Source Line Ranges: `126-147`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `reliability`, `sql-plan-management`, `plan-binding`, `cross-database`, `saas`, `system-variable`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0558_cbbfc1b3bc`
- Source ID: `tidb-docs-8.1:releases/release-7.6.0.md#reliability`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d6d8576ae46adced1e1f19e7e1297814233d6411c4b978af4d3f22c45db64ec5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.6.0#reliability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks about cross-database execution plan binding, fuzzy binding, or applying one global binding across databases with the same schema in TiDB 7.6.0.
- Retrieval Keywords: Cross-database execution plan binding, cross-database binding, CREATE GLOBAL BINDING, *.t1, *.t2, wildcard * database name, tidb_opt_enable_fuzzy_binding, SQL plan management, same schema different databases, SaaS services on TiDB, less than 1% overhead
- Follow-up Guidance: The content says the feature is disabled by default and must be enabled with the tidb_opt_enable_fuzzy_binding system variable before use.
- Classification Note: This is classified as a reliability feature because it describes a SQL plan management capability that stabilizes execution plans across many databases with the same schema.

## Official Source Content

### Reliability

* Cross-database execution plan binding [#48875](https://github.com/pingcap/tidb/issues/48875) @[qw4990](https://github.com/qw4990)

    When running SaaS services on TiDB, it is common practice to store data for each tenant in separate databases for easier data maintenance and management. This results in hundreds of databases with the same table and index definitions, and similar SQL statements. In such scenario, when you create an execution plan binding for a SQL statement, this binding usually applies to the SQL statements in other databases as well.

    For this scenario, TiDB v7.6.0 introduces the cross-database binding feature, which supports binding the same execution plan to SQL statements with the same schema, even if they are in different databases. When creating a cross-database binding, you need to use the wildcard `*` to represent the database name, as shown in the following example. After the binding is created, regardless of which database the tables `t1` and `t2` are in, TiDB will try to use this binding to generate an execution plan for any SQL statement with the same schema, which saves your effort to create a binding for each database.

    ```sql
    CREATE GLOBAL BINDING FOR
    USING
        SELECT /*+ merge_join(t1, t2) */ t1.id, t2.amount
        FROM *.t1, *.t2
        WHERE t1.id = t2.id;
    ```

    In addition, cross-database binding can effectively mitigate SQL performance issues caused by uneven distribution and rapid changes in user data and workload. SaaS providers can use cross-database binding to fix execution plans validated by users with large data volumes, thereby fixing execution plans for all users. For SaaS providers, this feature provides significant convenience and experience improvements.

    Due to the system overhead (less than 1%) introduced by cross-database binding, TiDB disables this feature by default. To use cross-database binding, you need to first enable the [`tidb_opt_enable_fuzzy_binding`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_enable_fuzzy_binding-new-in-v760) system variable.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-plan-management#cross-database-binding).
