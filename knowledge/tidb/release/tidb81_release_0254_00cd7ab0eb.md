# New features in SQL, Dashboard security, PD performance, and unsafe recovery

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.3.0.md`
- Source Title: `TiDB 5.3 Release Notes`
- Source Heading Path: `TiDB 5.3 Release Notes > New features | TiDB 5.3 Release Notes > New features > SQL | TiDB 5.3 Release Notes > New features > Security | TiDB 5.3 Release Notes > New features > Performance | TiDB 5.3 Release Notes > New features > Stability`
- Source Line Ranges: `81-164`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dashboard`, `pd`, `sql`, `tidb`, `tikv`
- Topic Tags: `new-features`, `placement-rules`, `temporary-tables`, `pessimistic-locking`, `table-attributes`, `least-privilege`, `dashboard`, `tso`, `follower-proxy`, `unsafe-recovery`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0254_00cd7ab0eb`
- Source ID: `tidb-docs-8.1:releases/release-5.3.0.md#new-features`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8f8a03c9af7ee6009495cb83d98cfef3d60f6b42d6d32b02eed2a7e2ec820a85`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.3.0#new-features
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.3.0 new features in SQL, Dashboard security, PD TSO performance tuning, or PD online unsafe recovery.
- Retrieval Keywords: CREATE PLACEMENT POLICY, ALTER PLACEMENT POLICY, placement rules in SQL, CREATE GLOBAL TEMPORARY TABLE, tidb_tmp_table_max_size, FOR UPDATE OF TABLES, ALTER TABLE PARTITION ATTRIBUTES, merge_option=deny, split-merge-interval, least privileges on TiDB Dashboard, dashboard-user, tidb_enable_tso_follower_proxy, PD Follower Proxy, tidb_tso_client_batch_max_wait_time, TSO requests load, pd-ctl unsafe remove-failed-stores, Online Unsafe Recovery
- Follow-up Guidance: The source includes linked user documents for placement rules in SQL, temporary tables, SELECT syntax, table attributes, Dashboard users, TSO-related system variables, and online unsafe recovery.
- Classification Note: This is classified as a release new-features section because it introduces newly supported SQL syntax, security capabilities, PD performance options, and a new stability recovery command in TiDB 5.3.0.

## Official Source Content

## New features
### SQL

- **Use SQL interface to set placement rules for data (experimental feature)**

    Support the `[CREATE | ALTER] PLACEMENT POLICY` syntax that provides a SQL interface to set placement rules for data. Using this feature, you can specify tables and partitions to be scheduled to specific regions, data centers, racks, hosts, or replica count rules. This meets your application demands for lower cost and higher flexibility. The typical user scenarios are as follows:

    - Merge multiple databases of different applications to reduce the cost on database maintenance, and achieve application resource isolation through the rule configuration
    - Increase replica count for important data to improve the application availability and data reliability
    - Store new data into SSDs and store old data into HHDs to lower the cost on data archiving and storage
    - Schedule the leaders of hotspot data to high-performance TiKV instances
    - Separate cold data to lower-cost storage mediums to improve cost efficiency

    [User document](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql), [#18030](https://github.com/pingcap/tidb/issues/18030)

- **Temporary tables**

    Support the `CREATE [GLOBAL] TEMPORARY TABLE` statement to create temporary tables. Using this feature, you can easily manage the temporary data generated in the calculation process of an application. Temporary data is stored in memory and you can use the `tidb_tmp_table_max_size` variable to limit the size of a temporary table. TiDB supports the following types of temporary tables:

    - Global temporary tables
        - Visible to all sessions in the cluster, and table schemas are persistent.
        - Provides transaction-level data isolation. The temporary data is effective only in the transaction. After the transaction finishes, the data is automatically dropped.
    - Local temporary tables
        - Visible only to the current session, and tables schemas are not persistent.
        - Supports duplicated table names. You do not need to design complicated naming rules for your application.
        - Provides session-level data isolation, which enables you to design a simpler application logic. After the transaction finishes, the temporary tables are dropped.

        [User document](https://docs.pingcap.com/tidb/stable/temporary-tables), [#24169](https://github.com/pingcap/tidb/issues/24169)

- **Support the `FOR UPDATE OF TABLES` syntax**

    For a SQL statement that joins multiple tables, TiDB supports acquiring pessimistic locks on the rows correlated to the tables that are included in `OF TABLES`.

    [User document](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-select), [#28689](https://github.com/pingcap/tidb/issues/28689)

- **Table attributes**

    Support the `ALTER TABLE [PARTITION] ATTRIBUTES` statement that allows you to set attributes for a table or partition. Currently, TiDB only supports setting the `merge_option` attribute. By adding this attribute, you can explicitly control the Region merge behavior.

    User scenarios: When you perform the `SPLIT TABLE` operation, if no data is inserted after a certain period of time (controlled by the PD parameter [`split-merge-interval`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#split-merge-interval)), the empty Regions are automatically merged by default. In this case, you can set the table attribute to `merge_option=deny` to avoid the automatic merging of Regions.

    [User document](https://docs.pingcap.com/tidb/stable/table-attributes), [#3839](https://github.com/tikv/pd/issues/3839)
### Security

- **Support creating users with the least privileges on TiDB Dashboard**

    The account system of TiDB Dashboard is consistent with that of TiDB SQL. Users accessing TiDB Dashboard are authenticated and authorized based on TiDB SQL users' privileges. Therefore, TiDB Dashboard requires limited privileges, or merely the read-only privilege. You can configure users to access TiDB Dashboard based on the principle of least privilege, thus avoiding access of high-privileged users.

    It is recommended that you create a least-privileged SQL user to access and sign in with TiDB Dashboard. This avoids access of high-privileged users and improves security.

    [User document](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-user)
### Performance

- **Optimize the timestamp processing flow of PD**

    TiDB optimizes its timestamp processing flow and reduces the timestamp processing load of PD by enabling PD Follower Proxy and modifying the batch waiting time required when the PD client requests TSO in batches. This helps improve the overall scalability of the system.

    - Support enabling or disabling PD Follower Proxy through the system variable [`tidb_enable_tso_follower_proxy`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_tso_follower_proxy-new-in-v530). Suppose that the TSO requests load of PD is too high. In this case, enabling PD follower proxy can batch forward the TSO requests collected during the request cycle on followers to the leader nodes. This solution can effectively reduce the number of direct interactions between clients and leaders, reduce the pressure of the load on leaders, and improve the overall performance of TiDB.

    > **Note:**
    >
    > When the number of clients is small and the PD leader CPU load is not full, it is NOT recommended to enable PD Follower Proxy.

    - Support using the system variable [`tidb_tso_client_batch_max_wait_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_tso_client_batch_max_wait_time-new-in-v530) to set the maximum waiting time needed for the PD client to batch request TSO. The unit of this time is milliseconds. In case that PD has a high TSO requests load, you can reduce the load and improve the throughput by increasing the waiting time to get a larger batch size.

    > **Note:**
    >
    > When the TSO request load is not high, it is NOT recommended to modify this variable value.

    [User document](https://docs.pingcap.com/tidb/stable/system-variables#tidb_tso_client_batch_max_wait_time-new-in-v530), [#3149](https://github.com/tikv/pd/issues/3149)
### Stability

- **Support Online Unsafe Recovery after some stores are permanently damaged (experimental feature)**

    Support the `pd-ctl unsafe remove-failed-stores` command that performs online data unsafe recovery. Suppose that the majority of data replicas encounter issues like permanent damage (such as disk damage), and these issues cause the data ranges in an application to be unreadable or unwritable. In this case, you can use the Online Unsafe Recovery feature implemented in PD to recover the data, so that the data is readable or writable again.

    It is recommended to perform the feature-related operations with the support of the TiDB team.

    [User document](https://docs.pingcap.com/tidb/stable/online-unsafe-recovery), [#10483](https://github.com/tikv/tikv/issues/10483)
