# Finalize migration setup and prepare for switchover

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-upgrade-migration-guide.md`
- Source Title: `Migrate and Upgrade a TiDB Cluster`
- Source Heading Path: `Migrate and Upgrade a TiDB Cluster > Step 3: Replicate incremental data > 3. Finalize the environment setup | Migrate and Upgrade a TiDB Cluster > Step 4: Switch business traffic and rollback | Migrate and Upgrade a TiDB Cluster > Step 4: Switch business traffic and rollback > 1. Prepare for the switchover`
- Source Line Ranges: `179-203`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `br`, `ticdc`, `tidb`, `tiup`
- Topic Tags: `system-tables`, `privileges`, `configuration-consistency`, `auto-increment`, `statistics`, `capacity-planning`, `operational-tasks`, `replication-latency`, `throughput-validation`, `application-validation`, `switchover-preparation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0468_30ef167cfb`
- Source ID: `tidb-docs-8.1:tidb-upgrade-migration-guide.md#3-finalize-the-environment-setup`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dfeffc37554505133024301dfb925f8ae13b43b49cba5694fda4c77d8831771a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-upgrade-migration-guide#3-finalize-the-environment-setup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-upgrade-migration-guide.md

## Retrieval Guidance

- Use When: Use this chunk when preparing a TiDB migration switchover and checking final environment consistency, operational tasks, replication readiness, and application validation.
- Retrieval Keywords: BR --with-sys-table, mysql.user, user privileges, configuration items and system variables are consistent, auto-increment ID caches, collect statistics manually, automatic collection, scale out the new cluster, alert subscriptions, scheduled statistics collection scripts, data backup scripts, TiCDC Changefeed replication latency, incremental replication throughput, peak business write rate, data validation steps, sanity or integration tests
- Follow-up Guidance: It also states to confirm TiCDC Changefeed latency and throughput before switchover and to complete data validation and application sanity or integration tests on the new cluster.
- Classification Note: This is classified as operation because the content covers migration environment finalization and pre-switchover checks such as system tables, configuration consistency, replication status, and workload preparation.

## Official Source Content

### 3. Finalize the environment setup

This migration procedure restores some system table data using the BR `--with-sys-table` option. For tables that are not included in the scope, you need to manually restore. Common items to check and supplement include:

- User privileges: compare the `mysql.user` table.
- Configuration settings: ensure that configuration items and system variables are consistent.
- Auto-increment columns: clear auto-increment ID caches in the new cluster.
- Statistics: collect statistics manually or enable automatic collection in the new cluster.

Additionally, you can scale out the new cluster to handle expected workloads and migrate operational tasks, such as alert subscriptions, scheduled statistics collection scripts, and data backup scripts.
## Step 4: Switch business traffic and rollback
### 1. Prepare for the switchover

- Confirm replication status:

    - Monitor the latency of TiCDC Changefeed replication.
    - Ensure that the incremental replication throughput is greater than or equal to the peak business write rate.

- Perform multi-dimensional validation, such as:

    - Ensure that all data validation steps are complete and perform any necessary additional checks.
    - Conduct sanity or integration tests on the application in the new cluster.
