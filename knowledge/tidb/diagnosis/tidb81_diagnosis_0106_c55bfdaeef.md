# TiDB DDL troubleshooting

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-troubleshooting-map.md`
- Source Title: `TiDB Troubleshooting Map`
- Source Heading Path: `TiDB Troubleshooting Map > 3. TiDB issues | TiDB Troubleshooting Map > 3. TiDB issues > 3.1 DDL`
- Source Line Ranges: `53-101`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`
- Topic Tags: `ddl`, `metadata-lock`, `schema-change`, `ddl-owner`, `owner-election`, `network`, `upgrade`, `information-schema`, `schema-version`, `graceful-kill`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0106_c55bfdaeef`
- Source ID: `tidb-docs-8.1:tidb-troubleshooting-map.md#3-tidb-issues`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c3787a2ab36c3bb6030232d5b8345c9857fb5c5ef7ce5f46fc8207dbcf2b2fb3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-troubleshooting-map#3-tidb-issues
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-troubleshooting-map.md

## Retrieval Guidance

- Use When: Use this content when diagnosing TiDB DDL errors, slow or hanging DDL jobs, DDL owner problems, or `information schema` change and out-of-date log errors.
- Retrieval Keywords: ERROR 1105 (HY000): unsupported modify decimal column precision, admin show ddl jobs, metadata lock, DDL job hangs, DDL owner migration, curl -X POST http://{TiDBIP}:10080/ddl/owner/resign, tidb-ctl etcd delowner [LeaseID] [flags] + ownerKey, information schema is changed, schema version, information schema is out of date, graceful kill, DDL lease, 45s by default, keep alive
- Follow-up Guidance: The content includes follow-up paths such as checking DDL progress with `admin show ddl jobs`, reviewing network connectivity with PD/TiKV, and using DDL owner re-election commands when needed.
- Classification Note: This is classified as diagnosis because it organizes DDL-related symptoms and log messages by cause, including metadata lock, network issues, version-specific behavior, and DDL owner election.

## Official Source Content

## 3. TiDB issues
### 3.1 DDL

- 3.1.1 An error `ERROR 1105 (HY000): unsupported modify decimal column precision` is reported when you modify the length of the `decimal` field.<!--See [case-1004](https://github.com/pingcap/tidb-map/blob/master/maps/diagnose-case-study/case517.md) in Chinese.--> TiDB does not support changing the length of the `decimal` field.

- 3.1.2 TiDB DDL job hangs or executes slowly (use `admin show ddl jobs` to check DDL progress)

    - Cause 1: TiDB introduces the [metadata lock](https://docs.pingcap.com/tidb/stable/metadata-lock) in v6.3.0, and enables it by default in v6.5.0 and later versions. If the table involved in the DDL operation has intersections with the table involved in the uncommitted transaction, the DDL operation is blocked until the transaction is committed or rolled back.

    - Cause 2: Network issue with other components (PD/TiKV).

    - Cause 3: Early versions of TiDB (earlier than v3.0.8) have heavy internal load because of a lot of goroutine at high concurrency.

    - Cause 4: In early versions (v2.1.15 & versions < v3.0.0-rc1), PD instances fail to delete TiDB keys, which causes every DDL change to wait for two leases.

    - For other unknown causes, [report a bug](https://github.com/pingcap/tidb/issues/new?labels=type%2Fbug&template=bug-report.md).

    - Solution:

        - For cause 1, check the network connection between TiDB and TiKV/PD.
        - For cause 2 and 3, the issues are already fixed in later versions. You can upgrade TiDB to a later version.
        - For other causes, you can use the following solution of migrating the DDL owner.

    - DDL owner migration:

        - If you can connect to the TiDB server, execute the owner election command again: `curl -X POST http://{TiDBIP}:10080/ddl/owner/resign`
        - If you cannot connect to the TiDB server, use `tidb-ctl` to delete the DDL owner from the etcd of the PD cluster to trigger re-election: `tidb-ctl etcd delowner [LeaseID] [flags] + ownerKey`

- 3.1.3 TiDB reports `information schema is changed` error in log

    - For the detailed causes and solution, see [Why the `Information schema is changed` error is reported](https://docs.pingcap.com/tidb/stable/faq/sql-faq#what-triggers-the-information-schema-is-changed-error).

    - Background: The increased number of `schema version` is consistent with the number of `schema state` of each DDL change operation. For example, the `create table` operation has 1 version change, and the `add column` operation has 4 version changes. Therefore, too many column change operations might cause `schema version` to increase fast. For details, refer to [online schema change](https://static.googleusercontent.com/media/research.google.com/zh-CN//pubs/archive/41376.pdf).

- 3.1.4 TiDB reports `information schema is out of date` in log

    - Cause 1: The TiDB server that is executing the DML statement is stopped by `graceful kill` and prepares to exit. The execution time of the transaction that contains the DML statement exceeds one DDL lease. An error is reported when the transaction is committed.

    - Cause 2: The TiDB server cannot connect to PD or TiKV when it is executing the DML statement. As a result, the TiDB server did not load the new schema within one DDL lease (`45s` by default), or the TiDB server disconnects from PD with the `keep alive` setting.

    - Cause 3: TiKV has high load or network timed out. Check the node loads in **Grafana** -> **TiDB** and **TiKV**.

    - Solution:

        - For cause 1, retry the DML operation when TiDB is started.
        - For cause 2, check the network between the TiDB server and PD/TiKV.
        - For cause 3, investigate why TiKV is busy. Refer to [4 TiKV issues](#4-tikv-issues).
