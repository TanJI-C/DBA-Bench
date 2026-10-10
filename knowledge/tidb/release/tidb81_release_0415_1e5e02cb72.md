# Availability features: survival preferences and flashback DDL rollback

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.6.0.md`
- Source Title: `TiDB 6.6.0 Release Notes`
- Source Heading Path: `TiDB 6.6.0 Release Notes > Feature details > Availability`
- Source Line Ranges: `160-176`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `shared`
- Topic Tags: `availability`, `placement-rules`, `survival-preference`, `disaster-recovery`, `flashback-cluster`, `ddl-rollback`, `gc-lifetime`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0415_1e5e02cb72`
- Source ID: `tidb-docs-8.1:releases/release-6.6.0.md#availability`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a1693a30597cbe046b4f1093f9f8d447ae5ba4012f4a294bb84c0416d6b6d24c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.6.0#availability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.6.0 availability features about placement rule survival preferences or rolling back DDL with flashback.
- Retrieval Keywords: TiDB 6.6.0 Availability, SURVIVAL_PREFERENCE, SURVIVAL_PREFERENCES, placement rules in SQL, specify survival preferences, cloud region fails, availability zone fails, FLASHBACK CLUSTER TO TIMESTAMP, rolling back DDL operations, GC lifetime, flashback cluster
- Follow-up Guidance: The content points to the placement rules in SQL documentation for survival preferences and the SQL statement documentation for FLASHBACK CLUSTER TO TIMESTAMP.
- Classification Note: This is classified under availability because the official content describes disaster survivability settings and cluster point-in-time rollback including DDL rollback.

## Official Source Content

### Availability

* Support configuring `SURVIVAL_PREFERENCE` for [placement rules in SQL](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql) [#38605](https://github.com/pingcap/tidb/issues/38605) @[nolouch](https://github.com/nolouch)

    `SURVIVAL_PREFERENCES` provides data survival preference settings to increase the disaster survivability of data. By specifying `SURVIVAL_PREFERENCE`, you can control the following:

    - For TiDB clusters deployed across cloud regions, when a cloud region fails, the specified databases or tables can survive in another cloud region.
    - For TiDB clusters deployed in a single cloud region, when an availability zone fails, the specified databases or tables can survive in another availability zone.

  For more information, see [documentation](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql#specify-survival-preferences).

* Support rolling back DDL operations via the `FLASHBACK CLUSTER TO TIMESTAMP` statement [#14045](https://github.com/tikv/tikv/issues/14045) @[Defined2014](https://github.com/Defined2014) @[JmPotato](https://github.com/JmPotato)

    The [`FLASHBACK CLUSTER TO TIMESTAMP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-cluster) statement supports restoring the entire cluster to a specified point in time within the Garbage Collection (GC) lifetime. In TiDB v6.6.0, this feature adds support for rolling back DDL operations. This can be used to quickly undo a DML or DDL misoperation on a cluster, roll back a cluster within minutes, and roll back a cluster multiple times on the timeline to determine when specific data changes occurred.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-cluster).
