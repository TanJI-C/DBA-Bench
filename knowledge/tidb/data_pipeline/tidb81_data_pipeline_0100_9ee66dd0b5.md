# Replicate incremental data from self-managed TiDB to TiDB Cloud with TiCDC

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-from-op-tidb.md`
- Source Title: `Migrate from TiDB Self-Managed to TiDB Cloud`
- Source Heading Path: `Migrate from TiDB Self-Managed to TiDB Cloud > Replicate incremental data`
- Source Line Ranges: `274-410`
- Source Scope: `all`
- Primary Component: `ticdc`
- Related Components: `cloud`, `pd`, `sql`, `tidb`
- Topic Tags: `incremental-replication`, `changefeed`, `networking`, `gc`, `timezone`, `query-bindings`, `users`, `privileges`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0100_9ee66dd0b5`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-from-op-tidb.md#replicate-incremental-data`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `36774e5c2eaf5c39d34f0410712f9af3e1d92921258a348d4f2e976d7a098d69`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-op-tidb#replicate-incremental-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-from-op-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented steps to replicate incremental data from a self-managed TiDB cluster to TiDB Cloud with TiCDC, including networking, changefeed creation, verification, timezone, query bindings, and user privilege migration.
- Retrieval Keywords: Replicate incremental data, TiCDC, tiup cdc cli changefeed create, --pd, --sink-uri, --changefeed-id, --start-ts, Create changefeed successfully!, tiup cdc cli changefeed list, state is normal, Settings > Networking, Add IP Address, Configure an IP Access List, Connect, Public, General, SET GLOBAL tidb_gc_enable = TRUE, SELECT @@global.tidb_gc_enable, SELECT @@global.time_zone, SET GLOBAL time_zone, mysql.bind_info, CREATE GLOBAL BINDING FOR, SHOW GRANTS, mysql.user
- Follow-up Guidance: The chunk includes follow-up verification by checking for "Create changefeed successfully!", confirming the changefeed state is normal, testing record replication, and then aligning timezone, query bindings, and user privileges.
- Classification Note: This is classified as a data pipeline chunk centered on TiCDC because the content documents incremental replication setup and validation between an upstream TiDB cluster and a downstream TiDB Cloud cluster.

## Official Source Content

## Replicate incremental data

To replicate incremental data, do the following:

1. Get the start time of the incremental data migration. For example, you can get it from the metadata file of the full data migration.

    ![Start Time in Metadata](/media/tidb-cloud/start_ts_in_metadata.png)

2. Grant TiCDC to connect to TiDB Cloud.

    1. In the [TiDB Cloud console](https://tidbcloud.com/project/clusters), navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.
    2. In the left navigation pane, click **Settings** > **Networking**.
    3. On the **Networking** page, click **Add IP Address**.
    4. In the displayed dialog, select **Use IP addresses**, click **+**, fill in the public IP address of the TiCDC component in the **IP Address** field, and then click **Confirm**. Now TiCDC can access TiDB Cloud. For more information, see [Configure an IP Access List](https://docs.pingcap.com/tidb/stable/tidb-cloud/configure-ip-access-list).

3. Get the connection information of the downstream TiDB Cloud cluster.

    1. In the [TiDB Cloud console](https://tidbcloud.com/project/clusters), navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.
    2. Click **Connect** in the upper-right corner.
    3. In the connection dialog, select **Public** from the **Connection Type** drop-down list and select **General** from the **Connect With** drop-down list.
    4. From the connection information, you can get the host IP address and port of the cluster. For more information, see [Connect via public connection](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-standard-connection).

4. Create and run the incremental replication task. In the upstream cluster, run the following:

    ```shell
    tiup cdc cli changefeed create \
    --pd=http://172.16.6.122:2379  \
    --sink-uri="tidb://root:123456@172.16.6.125:4000"  \
    --changefeed-id="upstream-to-downstream"  \
    --start-ts="431434047157698561"
    ```

    - `--pd`: the PD address of the upstream cluster. The format is: `[upstream_pd_ip]:[pd_port]`
    - `--sink-uri`: the downstream address of the replication task. Configure `--sink-uri` according to the following format. Currently, the scheme supports `mysql`, `tidb`, `kafka`, `s3`, and `local`.

        ```shell
        [scheme]://[userinfo@][host]:[port][/path]?[query_parameters]
        ```

    - `--changefeed-id`: the ID of the replication task. The format must match the ^[a-zA-Z0-9]+(\-[a-zA-Z0-9]+)*$ regular expression. If this ID is not specified, TiCDC automatically generates a UUID (the version 4 format) as the ID.
    - `--start-ts`: specifies the starting TSO of the changefeed. From this TSO, the TiCDC cluster starts pulling data. The default value is the current time.

    For more information, see [CLI and Configuration Parameters of TiCDC Changefeeds](https://docs.pingcap.com/tidb/dev/ticdc-changefeed-config).

5. Enable the GC mechanism again in the upstream cluster. If no error or delay is found in incremental replication, enable the GC mechanism to resume garbage collection of the cluster.

    Run the following command to verify whether the setting works.

    ```sql
    SET GLOBAL tidb_gc_enable = TRUE;
    ```

    The following is an example output, in which `1` indicates that GC is disabled.

    ```sql
    SELECT @@global.tidb_gc_enable;
    +-------------------------+
    | @@global.tidb_gc_enable |
    +-------------------------+
    |                       1 |
    +-------------------------+
    1 row in set (0.01 sec)
    ```

6. Verify the incremental replication task.

    - If the message "Create changefeed successfully!" is displayed in the output, the replication task is created successfully.
    - If the state is `normal`, the replication task is normal.

        ```shell
         tiup cdc cli changefeed list --pd=http://172.16.6.122:2379
        ```

        ![Update Filter](/media/tidb-cloud/normal_status_in_replication_task.png)

    - Verify the replication. Write a new record to the upstream cluster, and then check whether the record is replicated to the downstream TiDB Cloud cluster.

7. Set the same timezone for the upstream and downstream clusters. By default, TiDB Cloud sets the timezone to UTC. If the timezone is different between the upstream and downstream clusters, you need to set the same timezone for both clusters.

    1. In the upstream cluster, run the following command to check the timezone:

        ```sql
        SELECT @@global.time_zone;
        ```

    2. In the downstream cluster, run the following command to set the timezone:

        ```sql
        SET GLOBAL time_zone = '+08:00';
        ```

    3. Check the timezone again to verify the setting:

        ```sql
        SELECT @@global.time_zone;
        ```

8. Back up the [query bindings](https://docs.pingcap.com/tidb/stable/sql-plan-management) in the upstream cluster and restore them in the downstream cluster. You can use the following query to back up the query bindings:

    ```sql
    SELECT DISTINCT(CONCAT('CREATE GLOBAL BINDING FOR ', original_sql,' USING ', bind_sql,';')) FROM mysql.bind_info WHERE status='enabled';
    ```

    If you do not get any output, query bindings might not be used in the upstream cluster. In this case, you can skip this step.

    After you get the query bindings, run them in the downstream cluster to restore the query bindings.

9. Back up the user and privilege information in the upstream cluster and restore them in the downstream cluster. You can use the following script to back up the user and privilege information. Note that you need to replace the placeholders with the actual values.

    ```shell
    #!/bin/bash

    export MYSQL_HOST={tidb_op_host}
    export MYSQL_TCP_PORT={tidb_op_port}
    export MYSQL_USER=root
    export MYSQL_PWD={root_password}
    export MYSQL="mysql -u${MYSQL_USER} --default-character-set=utf8mb4"
    
    function backup_user_priv(){
        ret=0
        sql="SELECT CONCAT(user,':',host,':',authentication_string) FROM mysql.user WHERE user NOT IN ('root')"
        for usr in `$MYSQL -se "$sql"`;do
            u=`echo $usr | awk -F ":" '{print $1}'`
            h=`echo $usr | awk -F ":" '{print $2}'`
            p=`echo $usr | awk -F ":" '{print $3}'`
            echo "-- Grants for '${u}'@'${h}';"
            [[ ! -z "${p}" ]] && echo "CREATE USER IF NOT EXISTS '${u}'@'${h}' IDENTIFIED WITH 'mysql_native_password' AS '${p}' ;"
            $MYSQL -se "SHOW GRANTS FOR '${u}'@'${h}';" | sed 's/$/;/g'
            [ $? -ne 0 ] && ret=1 && break
        done
        return $ret
    }
    
    backup_user_priv
    ```
    
    After you get the user and privilege information, run the generated SQL statements in the downstream cluster to restore the user and privilege information.
