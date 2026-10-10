# Upgrade FAQs for rolling updates, DDL timing, and upgrade methods

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/upgrade-faq.md`
- Source Title: `Upgrade and After Upgrade FAQs`
- Source Heading Path: `Upgrade and After Upgrade FAQs | Upgrade and After Upgrade FAQs > Upgrade FAQs | Upgrade and After Upgrade FAQs > Upgrade FAQs > What are the effects of rolling updates? | Upgrade and After Upgrade FAQs > Upgrade FAQs > Can I upgrade the TiDB cluster during the DDL execution? | Upgrade and After Upgrade FAQs > Upgrade FAQs > How to upgrade TiDB using the binary?`
- Source Line Ranges: `5-33`
- Source Scope: `shared`
- Primary Component: `shared`
- Related Components: `pd`, `tidb`, `tikv`, `tiup`, `operator`
- Topic Tags: `upgrade`, `rolling-update`, `ddl`, `topology`, `compatibility`, `tiup`, `kubernetes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0153_e52409d8ce`
- Source ID: `tidb-docs-8.1:faq/upgrade-faq.md#upgrade-and-after-upgrade-faqs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4074c5a2d647f511325baadd1c9ace2b97cb0e95d68cb427de51cfc3beddbc89`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/upgrade-faq#upgrade-and-after-upgrade-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/upgrade-faq.md

## Retrieval Guidance

- Use When: Use this chunk when answering questions about rolling updates, DDL restrictions during upgrade, or whether to use TiUP, Kubernetes, or binary methods for upgrading TiDB.
- Retrieval Keywords: rolling updates, business peak hours, minimum cluster topology, TiDB * 2, PD * 3, TiKV * 3, Pump, Drainer, stop Drainer before rolling updates, Pump is also upgraded, DDL execution during upgrade, ADMIN SHOW DDL, ADMIN CANCEL DDL, undefined behavior, v7.1.0, TiDB Smooth Upgrade, upgrade TiDB using the binary, upgrade TiDB using TiUP, upgrade a TiDB cluster on Kubernetes
- Follow-up Guidance: For pre-v7.1.0 upgrades, the content points to `ADMIN SHOW DDL` and `ADMIN CANCEL DDL`, and for v7.1.0 or later it refers to TiDB Smooth Upgrade.
- Classification Note: This is classified as operation because the content describes upgrade procedures, rolling update effects, cluster topology requirements, and upgrade method choices.

## Official Source Content

# Upgrade and After Upgrade FAQs

This document introduces some FAQs and their solutions when or after you upgrade TiDB.
## Upgrade FAQs

This section lists some FAQs and their solutions when you upgrade TiDB.
### What are the effects of rolling updates?

When you apply rolling updates to the TiDB services, the running application is affected to varying degrees. Therefore, it is not recommended that you perform a rolling update during business peak hours. You need to configure the minimum cluster topology (TiDB \* 2, PD \* 3, TiKV \* 3). If the Pump or Drainer service is involved in the cluster, it is recommended to stop Drainer before rolling updates. When you upgrade TiDB, Pump is also upgraded.
### Can I upgrade the TiDB cluster during the DDL execution?

* If the TiDB version before upgrade is earlier than v7.1.0:

    * **DO NOT** upgrade a TiDB cluster when a DDL statement is being executed in the cluster (usually for the time-consuming DDL statements such as `ADD INDEX` and the column type changes). Before the upgrade, it is recommended to use the [`ADMIN SHOW DDL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl) command to check whether the TiDB cluster has an ongoing DDL job. If the cluster has a DDL job, to upgrade the cluster, wait until the DDL execution is finished or use the [`ADMIN CANCEL DDL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cancel-ddl) command to cancel the DDL job before you upgrade the cluster.

    * During the cluster upgrade, **DO NOT** execute any DDL statement. Otherwise, the issue of undefined behavior might occur.

* If the TiDB version before upgrade is v7.1.0 or later:

    * You do not need to follow the restrictions of upgrading from an earlier version to v7.1.0. That is, TiDB can receive user DDL tasks during the upgrade. For details, refer to [TiDB Smooth Upgrade](https://docs.pingcap.com/tidb/stable/smooth-upgrade-tidb).
### How to upgrade TiDB using the binary?

It is not recommended to upgrade TiDB using the binary. Instead, it is recommended to [upgrade TiDB using TiUP](https://docs.pingcap.com/tidb/stable/upgrade-tidb-using-tiup) or [upgrade a TiDB cluster on Kubernetes](https://docs.pingcap.com/tidb-in-kubernetes/stable/upgrade-a-tidb-cluster), which ensures both version consistency and compatibility.
