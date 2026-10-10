# Trigger online unsafe recovery and monitor progress

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/online-unsafe-recovery.md`
- Source Title: `Online Unsafe Recovery`
- Source Heading Path: `Online Unsafe Recovery > Usage > Step 1. Specify the stores that cannot be recovered | Online Unsafe Recovery > Usage > Step 2. Check the recovery progress and wait for the completion`
- Source Line Ranges: `39-164`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`, `tiflash`, `sql`
- Topic Tags: `pd-ctl`, `failed-stores`, `tombstone`, `recovery-progress`, `force-leader`, `demote-voter`, `create-empty-region`, `scheduling-pause`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0029_bf6ef29245`
- Source ID: `tidb-docs-8.1:online-unsafe-recovery.md#step-1-specify-the-stores-that-cannot-be-recovered`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fa37079de708b2f8622b471736dc199f3906c9888c6ff4def55b516e70a16fde`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/online-unsafe-recovery#step-1-specify-the-stores-that-cannot-be-recovered
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/online-unsafe-recovery.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the exact PD Control commands, progress stages, timeout behavior, status output, or related notes for running and monitoring online unsafe recovery.
- Retrieval Keywords: pd-ctl -u <pd_addr> unsafe remove-failed-stores <store_id1,store_id2,...>, unsafe remove-failed-stores <store_id>[,<store_id>,...], unsafe remove-failed-stores show, --timeout <seconds>, Success, Failed, unsafe recovery is running, invalid input store x doesn't exist, invalid input store x is up and connected, Tombstone status, all scheduling tasks and split/merge are paused, collect report, tombstone tiflash learner, force leader for commit merge, force leader, demote failed voter, create empty region, Collecting reports from alive stores, Unsafe recovery finished, Affected table ids, Affected meta regions, INFORMATION_SCHEMA.TABLES, SELECT TABLE_SCHEMA, TABLE_NAME, TIDB_TABLE_ID FROM INFORMATION_SCHEMA.TABLES WHERE TIDB_TABLE_ID IN (64, 27), Unsafe recovery failed
- Follow-up Guidance: After recovery finishes, the source says you can query INFORMATION_SCHEMA.TABLES with the affected table IDs and notes that failed voters might become failed learners that PD scheduling later removes.
- Classification Note: This chunk is classified as recovery for PD because it centers on PD Control operations, PD-managed recovery stages, and PD status reporting while involving TiKV, TiFlash, and SQL identifiers shown in the official output and follow-up query.

## Official Source Content

### Step 1. Specify the stores that cannot be recovered

To trigger automatic recovery, use PD Control to execute [`unsafe remove-failed-stores <store_id>[,<store_id>,...]`](/pd-control.md#unsafe-remove-failed-stores-store-ids--show) and specify **all** the TiKV nodes that cannot be recovered, separated by commas.

```bash
pd-ctl -u <pd_addr> unsafe remove-failed-stores <store_id1,store_id2,...>
```

If the command returns `Success`, PD Control has successfully registered the task to PD. This only means that the request has been accepted, not that the recovery has been successfully performed. The recovery task is performed in the background. To see the recovery progress, use [`show`](#step-2-check-the-recovery-progress-and-wait-for-the-completion).

If the command returns `Failed`, PD Control has failed to register the task to PD. The possible errors are as follows:

- `unsafe recovery is running`: There is already an ongoing recovery task.
- `invalid input store x doesn't exist`: The specified store ID does not exist.
- `invalid input store x is up and connected`: The specified store with the ID is still healthy and should not be recovered.

To specify the longest allowable duration of a recovery task, use the `--timeout <seconds>` option. If this option is not specified, the longest duration is 5 minutes by default. When the timeout occurs, the recovery is interrupted and returns an error.

> **Note:**
>
> - Because this command needs to collect information from all peers, it might cause an increase in memory usage (100,000 peers are estimated to use 500 MiB of memory).
> - If PD restarts when the command is running, the recovery is interrupted and you need to trigger the task again.
> - Once the command is running, the specified stores will be set to the Tombstone status, and you cannot restart these stores.
> - When the command is running, all scheduling tasks and split/merge are paused and will be resumed automatically after the recovery is successful or fails.
### Step 2. Check the recovery progress and wait for the completion

When the above store removal command runs successfully, you can use PD Control to check the removal progress by running [`unsafe remove-failed-stores show`](https://docs.pingcap.com/tidb/stable/pd-control#config-show--set-option-value--placement-rules).

```bash
pd-ctl -u <pd_addr> unsafe remove-failed-stores show
```

The recovery process has multiple possible stages:

- `collect report`: The initial stage in which PD collects reports from TiKV and gets global information.
- `tombstone tiflash learner`: Among the unhealthy Regions, delete the TiFlash learners that are newer than other healthy peers, to prevent such an extreme situation and the possible panic.
- `force leader for commit merge`: A special stage. When there is an uncompleted commit merge, `force leader` is first performed on the Regions with commit merge, in case of extreme situations.
- `force leader`: Forces unhealthy Regions to assign a Raft leader among the remaining healthy peers.
- `demote failed voter`: Demotes the Region's failed voters to learners, and then the Regions can select a Raft leader as normal.
- `create empty region`: Creates an empty Region to fill in the space in the key range. This is to resolve the case that the stores with all replicas of some Regions have been damaged.

Each of the above stages is output in the JSON format, including information, time, and a detailed recovery plan. For example:

```json
[
    {
        "info": "Unsafe recovery enters collect report stage: failed stores 4, 5, 6",
        "time": "......"
    },
    {
        "info": "Unsafe recovery enters force leader stage",
        "time": "......",
        "actions": {
            "store 1": [
                "force leader on regions: 1001, 1002"
            ],
            "store 2": [
                "force leader on regions: 1003"
            ]
        }
    },
    {
        "info": "Unsafe recovery enters demote failed voter stage",
        "time": "......",
        "actions": {
            "store 1": [
                "region 1001 demotes peers { id:101 store_id:4 }, { id:102 store_id:5 }",
                "region 1002 demotes peers { id:103 store_id:5 }, { id:104 store_id:6 }",
            ],
            "store 2": [
                "region 1003 demotes peers { id:105 store_id:4 }, { id:106 store_id:6 }",
            ]
        }
    },
    {
        "info": "Collecting reports from alive stores(1/3)",
        "time": "......",
        "details": [
            "Stores that have not dispatched plan: ",
            "Stores that have reported to PD: 4",
            "Stores that have not reported to PD: 5, 6",
        ]
    }
]
```

After PD has successfully dispatched the recovery plan, it waits for TiKV to report the execution results. As you can see in `Collecting reports from alive stores`, the last stage of the above output, this part of the output shows the detailed statuses of PD dispatching recovery plan and receiving reports from TiKV.

The whole recovery process takes multiple stages and one stage might be retried multiple times. Usually, the estimated duration is 3 to 10 periods of store heartbeat (one period of store heartbeat is 10 seconds by default). After the recovery is completed, the last stage in the command output shows `"Unsafe recovery finished"`, the table IDs to which the affected Regions belong (if there is none or RawKV is used, the output does not show the table IDs), and the affected SQL meta Regions. For example:

```json
{
    "info": "Unsafe recovery finished",
    "time": "......",
    "details": [
        "Affected table ids: 64, 27",
        "Affected meta regions: 1001",
    ]
}
```

After you get the affected table IDs, you can query `INFORMATION_SCHEMA.TABLES` to view the affected table names.

```sql
SELECT TABLE_SCHEMA, TABLE_NAME, TIDB_TABLE_ID FROM INFORMATION_SCHEMA.TABLES WHERE TIDB_TABLE_ID IN (64, 27);
```

> **Note:**
>
> - The recovery operation has turned some failed voters to failed learners. Then PD scheduling needs some time to remove these failed learners.
> - It is recommended to add new stores in time.

If an error occurs during the task, the last stage in the output shows `"Unsafe recovery failed"` and the error message. For example:

```json
{
    "info": "Unsafe recovery failed: <error>",
    "time": "......"
}
```
