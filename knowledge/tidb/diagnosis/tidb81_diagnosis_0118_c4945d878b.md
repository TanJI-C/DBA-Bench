# Diagnose missing TiFlash data replication

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/troubleshoot-tiflash.md`
- Source Title: `Troubleshoot a TiFlash Cluster`
- Source Heading Path: `Troubleshoot a TiFlash Cluster > Data is not replicated to TiFlash`
- Source Line Ranges: `174-243`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `replication`, `placement-rules`, `ddl`, `progress`, `pd-ctl`, `logs`, `max-replicas`, `region-scheduling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0118_c4945d878b`
- Source ID: `tidb-docs-8.1:tiflash/troubleshoot-tiflash.md#data-is-not-replicated-to-tiflash`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c2e5c1540feb5f33926ddedfcc6c09729783a789bb9571d76fb7fb0bb965621c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/troubleshoot-tiflash#data-is-not-replicated-to-tiflash
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/troubleshoot-tiflash.md

## Retrieval Guidance

- Use When: Use this chunk when TiFlash replicas do not appear after `ALTER TABLE ... SET TIFLASH REPLICA` and you need to diagnose replication progress, placement rules, and PD scheduling.
- Retrieval Keywords: Data is not replicated to TiFlash, ALTER table <tbl_name> set tiflash replica <num>, SELECT * FROM information_schema.tiflash_replica, progress, Tiflash replica is not available, lag_region_info, pd-ctl, config show replication, Placement Rules, max-replicas, ConfigureTiFlashPDForTable, ConfigureTiFlashPDForPartitions, curl http://<pd-ip>:<pd-port>/pd/api/v1/config/rules/group/tiflash, table-<table_id>-r, pd.log, add operator
- Follow-up Guidance: If `progress` is not updated, the content says to search `tidb.log` for `Tiflash replica is not available`, check `tiflash log` such as `lag_region_info`, verify placement rules and `max-replicas`, and inspect PD rules and scheduling logs for `table-<table_id>-r` and `add operator`.
- Classification Note: This is classified as diagnosis because the content provides a step-by-step checklist to identify why data is not replicated to TiFlash across TiDB, PD, and placement rule scheduling.

## Official Source Content

## Data is not replicated to TiFlash

After deploying a TiFlash node and starting replication (by performing the ALTER operation), no data is replicated to it. In this case, you can identify and address the problem by following the steps below:

1. Check whether the replication is successful by running the `ALTER table <tbl_name> set tiflash replica <num>` command and check the output.

    - If there is output, go to the next step.
    - If there is no output, run the `SELECT * FROM information_schema.tiflash_replica` command to check whether TiFlash replicas have been created. If not, run the `ALTER table ${tbl_name} set tiflash replica ${num}` command again, check whether other statements (for example, `add index`) have been executed, or check whether DDL executions are successful.

2. Check whether TiFlash Region replication runs correctly.

   Check whether there is any change in `progress`:

   - If yes, TiFlash replication runs correctly.
   - If no, TiFlash replication is abnormal. In `tidb.log`, search the log saying `Tiflash replica is not available`. Check whether `progress` of the corresponding table is updated. If not, check the `tiflash log` for further information. For example, search `lag_region_info` in `tiflash log` to find out which Region lags behind.

3. Check whether the [Placement Rules](https://docs.pingcap.com/tidb/stable/configure-placement-rules) function has been enabled by using pd-ctl:

    ```shell
    echo 'config show replication' | /path/to/pd-ctl -u http://<pd-ip>:<pd-port>
    ```

    - If `true` is returned, go to the next step.
    - If `false` is returned, [enable the Placement Rules feature](https://docs.pingcap.com/tidb/stable/configure-placement-rules#enable-placement-rules) and go to the next step.

4. Check whether the `max-replicas` configuration is correct:

    - If the value of `max-replicas` does not exceed the number of TiKV nodes in the cluster, go to the next step.
    - If the value of `max-replicas` is greater than the number of TiKV nodes in the cluster, the PD does not replicate data to the TiFlash node. To address this issue, change `max-replicas` to an integer fewer than or equal to the number of TiKV nodes in the cluster.

    > **Note:**
    >
    > `max-replicas` is defaulted to 3. In production environments, the value is usually fewer than the number of TiKV nodes. In test environments, the value can be 1.

    ```shell
        curl -X POST -d '{
            "group_id": "pd",
            "id": "default",
            "start_key": "",
            "end_key": "",
            "role": "voter",
            "count": 3,
            "location_labels": [
            "host"
            ]
        }' <http://172.16.x.xxx:2379/pd/api/v1/config/rule>
    ```

5. Check whether TiDB has created any placement rule for tables.

    Search the logs of TiDB DDL Owner and check whether TiDB has notified PD to add placement rules. For non-partitioned tables, search `ConfigureTiFlashPDForTable`. For partitioned tables, search `ConfigureTiFlashPDForPartitions`.

    - If the keyword is found, go to the next step.
    - If not, collect logs of the corresponding component for troubleshooting.

6. Check whether PD has configured any placement rule for tables.

    Run the `curl http://<pd-ip>:<pd-port>/pd/api/v1/config/rules/group/tiflash` command to view  all TiFlash placement rules on the current PD. If a rule with the ID being `table-<table_id>-r` is found, the PD has configured a placement rule successfully.

7. Check whether the PD schedules properly.

    Search the `pd.log` file for the `table-<table_id>-r` keyword and scheduling behaviors like `add operator`.

    - If the keyword is found, the PD schedules properly.
    - If not, the PD does not schedule properly.
