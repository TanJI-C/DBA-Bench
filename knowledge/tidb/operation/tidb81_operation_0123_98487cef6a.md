# Start, verify, stop, and monitor a DM migration task

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/migrate-data-using-dm.md`
- Source Title: `Migrate Data Using Data Migration`
- Source Heading Path: `Migrate Data Using Data Migration > Step 5: Start the data migration task | Migrate Data Using Data Migration > Step 6: Check the data migration task | Migrate Data Using Data Migration > Step 7: Stop the data migration task | Migrate Data Using Data Migration > Step 8: Monitor the task and check logs`
- Source Line Ranges: `119-190`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`, `tidb`
- Topic Tags: `precheck`, `start-task`, `query-status`, `stop-task`, `monitoring`, `alerts`, `grafana`, `logs`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0123_98487cef6a`
- Source ID: `tidb-docs-8.1:dm/migrate-data-using-dm.md#step-5-start-the-data-migration-task`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `da4024a4607f3b296472d8f07f722a8e8bf93114fd20b994b33874b9de77afbc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/migrate-data-using-dm#step-5-start-the-data-migration-task
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/migrate-data-using-dm.md

## Retrieval Guidance

- Use When: Use this chunk when starting a DM migration task, checking task status, stopping a task, or locating monitoring and log access for DM-master, DM-worker, and dmctl.
- Retrieval Keywords: start-task ./task.yaml, check-task, precheck, query-status, stop-task test, tiup dmctl --master-addr 172.16.10.71:8261, Alertmanager, Grafana, DM dashboard, DM-master, DM-worker, --log-file, {log_dir}, monitor the task and check logs
- Follow-up Guidance: The source says that if start-task fails, modify the configuration according to the returned prompt and then run the `start-task task.yaml` command again.
- Classification Note: This is classified as an operation chunk because the content focuses on runtime task control, status verification, stopping tasks, monitoring, alerts, and log locations.

## Official Source Content

## Step 5: Start the data migration task

To detect possible errors of data migration configuration in advance, DM provides the precheck feature:

- DM automatically checks the corresponding privileges and configuration while starting the data migration task.
- You can also use the `check-task` command to manually precheck whether the upstream MySQL instance configuration satisfies the DM requirements.

For details about the precheck feature, see [Precheck the upstream MySQL instance configuration](https://docs.pingcap.com/tidb/stable/dm/dm-precheck).

> **Note:**
>
> Before starting the data migration task for the first time, you should have got the upstream configured. Otherwise, an error is reported while you start the task.

Run the `tiup dmctl` command to start the data migration tasks. `task.yaml` is the configuration file that is edited above.

```bash
tiup dmctl --master-addr 172.16.10.71:8261 start-task ./task.yaml
```

- If the above command returns the following result, it indicates the task is successfully started.

    ```json
    {
        "result": true,
        "msg": "",
        "workers": [
            {
                "result": true,
                "worker": "172.16.10.72:8262",
                "msg": ""
            },
            {
                "result": true,
                "worker": "172.16.10.73:8262",
                "msg": ""
            }
        ]
    }
    ```

- If you fail to start the data migration task, modify the configuration according to the returned prompt and then run the `start-task task.yaml` command to restart the task.
## Step 6: Check the data migration task

If you need to check the task state or whether a certain data migration task is running in the DM cluster, run the following command in `tiup dmctl`:

```bash
tiup dmctl --master-addr 172.16.10.71:8261 query-status
```
## Step 7: Stop the data migration task

If you do not need to migrate data any more, run the following command in `tiup dmctl` to stop the task:

```bash
tiup dmctl --master-addr 172.16.10.71:8261 stop-task test
```

`test` is the task name that you set in the `name` configuration item of the `task.yaml` configuration file.
## Step 8: Monitor the task and check logs

Assuming that Prometheus, Alertmanager, and Grafana are successfully deployed along with the DM cluster deployment using TiUP, and the Grafana address is `172.16.10.71`. To view the alert information related to DM, you can open <http://172.16.10.71:9093> in a browser and enter into Alertmanager; to check monitoring metrics, go to <http://172.16.10.71:3000>, and choose the DM dashboard.

While the DM cluster is running, DM-master, DM-worker, and dmctl output the monitoring metrics information through logs. The log directory of each component is as follows:

- DM-master log directory: It is specified by the `--log-file` DM-master process parameter. If DM is deployed using TiUP, the log directory is `{log_dir}` in the DM-master node.
- DM-worker log directory: It is specified by the `--log-file` DM-worker process parameter. If DM is deployed using TiUP, the log directory is `{log_dir}` in the DM-worker node.
