# Data migration feature updates in 7.6.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.6.0.md`
- Source Title: `TiDB 7.6.0 Release Notes`
- Source Heading Path: `TiDB 7.6.0 Release Notes > Feature details > Data migration`
- Source Line Ranges: `229-254`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dm`, `ticdc`, `tidb`
- Topic Tags: `data-migration`, `mysql-8-0`, `ga`, `bidirectional-replication`, `ddl-replication`, `changefeed`, `sync-status`, `csv-output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0563_4d9083aee2`
- Source ID: `tidb-docs-8.1:releases/release-7.6.0.md#data-migration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4b620b98d9cae30cee06d714297016fde13c2554800355e929ba162b545c1871`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.6.0#data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.6.0 data migration release updates covering DM MySQL 8.0 GA support, TiCDC bi-directional replication DDL support, changefeed sync-status API, or CSV delimiter enhancements.
- Retrieval Keywords: TiDB 7.6.0 Data migration, DM MySQL 8.0 GA, Data Migration DM support for migrating MySQL 8.0 becomes generally available, TiCDC bi-directional replication BDR DDL statements, PRIMARY BDR role, GET /api/v2/changefeed/{changefeed_id}/synced, query downstream synchronization status of a changefeed, changefeed synced API, TiCDC CSV output protocol delimiters 1 to 3 characters, three-character delimiters with CSV output protocol
- Follow-up Guidance: The source links to documentation for the DM compatibility catalog, TiCDC bi-directional replication, the TiCDC OpenAPI v2 synced endpoint, and TiCDC CSV output.
- Classification Note: This is a release-note feature summary for self-managed data migration components, specifically DM and TiCDC changes introduced in TiDB 7.6.0.

## Official Source Content

### Data migration

* Data Migration (DM) support for migrating MySQL 8.0 becomes generally available (GA) [#10405](https://github.com/pingcap/tiflow/issues/10405) @[lyzx2001](https://github.com/lyzx2001)

    Previously, using DM to migrate data from MySQL 8.0 is an experimental feature and is not available for production environments. TiDB v7.6.0 enhances the stability and compatibility of this feature to help you smoothly and quickly migrate data from MySQL 8.0 to TiDB in production environments. In v7.6.0, this feature becomes generally available (GA).

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/dm/dm-compatibility-catalog).

* TiCDC supports replicating DDL statements in bi-directional replication (BDR) mode (experimental) [#10301](https://github.com/pingcap/tiflow/issues/10301) [#48519](https://github.com/pingcap/tidb/issues/48519) @[okJiang](https://github.com/okJiang) @[asddongmen](https://github.com/asddongmen)

    Starting from v7.6.0, TiCDC supports replication of DDL statements with bi-directional replication configured. Previously, replicating DDL statements was not supported by TiCDC, so users of TiCDC's bi-directional replication had to apply DDL statements to both TiDB clusters separately. With this feature, TiCDC allows for a cluster to be assigned the `PRIMARY` BDR role, and enables the replication of DDL statements from that cluster to the downstream cluster.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-bidirectional-replication).

* TiCDC supports querying the downstream synchronization status of a changefeed [#10289](https://github.com/pingcap/tiflow/issues/10289) @[hongyunyan](https://github.com/hongyunyan)

    Starting from v7.6.0, TiCDC introduces a new API `GET /api/v2/changefeed/{changefeed_id}/synced` to query the downstream synchronization status of a specified replication task (changefeed). By using this API, you can determine whether the upstream data received by TiCDC has been synchronized to the downstream system completely.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-api-v2#query-whether-a-specific-replication-task-is-completed).

* TiCDC adds support for three-character delimiters with CSV output protocol [#9969](https://github.com/pingcap/tiflow/issues/9969) @[zhangjinpeng87](https://github.com/zhangjinpeng87)

    Starting from v7.6.0, you can specify the CSV output protocol delimiters as 1 to 3 characters long. With this change, you can configure TiCDC to generate file output using two-character delimiters (such as `||` or `$^`) or three-character delimiters (such as `|@|`) to separate fields in the output.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-csv).
