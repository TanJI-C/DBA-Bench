# Execute traffic switchover and establish reverse replication

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-upgrade-migration-guide.md`
- Source Title: `Migrate and Upgrade a TiDB Cluster`
- Source Heading Path: `Migrate and Upgrade a TiDB Cluster > Step 4: Switch business traffic and rollback > 2. Execute the switchover`
- Source Line Ranges: `204-293`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`, `tiup`, `shared`
- Topic Tags: `traffic-cutover`, `account-locking`, `read-only-mode`, `tso`, `checkpointts`, `data-consistency`, `changefeed`, `auto-increment-cache`, `version-verification`, `grafana-monitoring`, `reverse-replication`, `rollback-preparation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0469_fb9a4a7409`
- Source ID: `tidb-docs-8.1:tidb-upgrade-migration-guide.md#2-execute-the-switchover`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `90d22fc598d10bc4dcdfcc533ec20715241e932d9a597ab685099538118afc8a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-upgrade-migration-guide#2-execute-the-switchover
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-upgrade-migration-guide.md

## Retrieval Guidance

- Use When: Use this chunk when executing the traffic switchover between old and new TiDB clusters and setting up TiCDC reverse replication for rollback readiness.
- Retrieval Keywords: ALTER USER ACCOUNT LOCK, SET GLOBAL tidb_super_read_only=ON, BEGIN; SELECT TIDB_CURRENT_TSO(); ROLLBACK;, up-tso, checkpointTs, down-tso, sync-diff-inspector, tiup ctl:${cluster_version} cdc changefeed pause, restart the TiDB nodes in the new cluster to clear the auto-increment ID cache, tiup cluster display <cluster-name>, INFORMATION_SCHEMA.CLUSTER_INFO, Grafana Overview > Services Port Status, ALTER USER ACCOUNT UNLOCK, SET GLOBAL tidb_super_read_only=OFF, tiup ctl:${cluster_version} cdc changefeed create, sink-uri, loopback writing risks, tiup ctl:${cluster_version} cdc changefeed list, redirect business traffic to the new cluster, TiDB Dashboard > Query Summary, Duration, QPS, Failed Query OPM, TiDB Dashboard > Server, Connection Count
- Follow-up Guidance: After the switchover, the source says to monitor the new cluster in Grafana and confirm the TiCDC reverse replication channel is established.
- Classification Note: This is classified as operation because the content provides the ordered switchover procedure, consistency verification, service checks, and reverse replication setup for migration cutover.

## Official Source Content

### 2. Execute the switchover

1. Stop application services to prevent the old cluster from handling business traffic. To further restrict access, you can use one of the following methods:

    - Lock user accounts in the old cluster:

        ```sql
        ALTER USER ACCOUNT LOCK;
        ```

    - Set the old cluster to read-only mode. It is recommended to restart TiDB nodes in the old cluster to clear active business sessions and prevent connections that have not entered read-only mode:

        ```sql
        SET GLOBAL tidb_super_read_only=ON;
        ```

2. Ensure TiCDC catches up:

    - After setting the old cluster to read-only mode, retrieve the current `up-tso`:

        ```sql
        BEGIN; SELECT TIDB_CURRENT_TSO(); ROLLBACK;
        ```

    - Monitor the Changefeed `checkpointTs` to confirm it has surpassed `up-tso`, indicating that TiCDC has completed data replication.

3. Verify data consistency between the new and old clusters:

    - After TiCDC catches up, obtain the `down-tso` from the new cluster.
    - Use the [sync-diff-inspector](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview) tool to compare data consistency between the new and old clusters at `up-tso` and `down-tso`.

4. Pause the forward Changefeed replication task:

    ```shell
    tiup ctl:${cluster_version} cdc changefeed pause --server http://${cdc_host}:${cdc_port} -c <changefeedid>
    ```

5. Restart the TiDB nodes in the new cluster to clear the auto-increment ID cache.

6. Check the operational status of the new cluster using the following methods:

    - Verify that the TiDB version matches the target version:

        ```shell
        tiup cluster display <cluster-name>
        ```

    - Log into the database and confirm component versions:

        ```sql
        SELECT * FROM INFORMATION_SCHEMA.CLUSTER_INFO;
        ```

    - Use Grafana to monitor service status: navigate to [**Overview > Services Port Status**](https://docs.pingcap.com/tidb/stable/grafana-overview-dashboard) and confirm that all services are in the **Up** state.

7. Set up reverse replication from the new cluster to the old cluster.

    1. Unlock user accounts in the old cluster and restore read-write mode:

        ```sql
        ALTER USER ACCOUNT UNLOCK;
        SET GLOBAL tidb_super_read_only=OFF;
        ```

    2. Record the current TSO of the new cluster:

        ```sql
        BEGIN; SELECT TIDB_CURRENT_TSO(); ROLLBACK;
        ```

    3. Configure the reverse replication link and ensure the Changefeed task is running properly:

        - Because business operations are stopped at this stage, you can use the current TSO.
        - Ensure that `sink-uri` is set to the address of the old cluster to avoid loopback writing risks.

        ```shell
        tiup ctl:${cluster_version} cdc changefeed create --server http://${cdc_host}:${cdc_port} --sink-uri="mysql://${username}:${password}@${tidb_endpoint}:${port}" --config config.toml --start-ts ${tso}

        tiup ctl:${cluster_version} cdc changefeed list --server http://${cdc_host}:${cdc_port}
        ```

8. Redirect business traffic to the new cluster.

9. Monitor the load and operational status of the new cluster using the following Grafana panels:

    - [**TiDB Dashboard > Query Summary**](https://docs.pingcap.com/tidb/stable/grafana-tidb-dashboard#query-summary): check the Duration, QPS, and Failed Query OPM metrics.
    - [**TiDB Dashboard > Server**](https://docs.pingcap.com/tidb/stable/grafana-tidb-dashboard#server): monitor the **Connection Count** metric to ensure even distribution of connections across nodes.

At this point, business traffic has successfully switched to the new cluster, and the TiCDC reverse replication channel is established.
