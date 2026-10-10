# PD-CTL resource manager and scheduler commands

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-control.md`
- Source Title: `PD Control User Guide`
- Source Heading Path: `PD Control User Guide > Command > `resource-manager [command]` | PD Control User Guide > Command > `resource-manager [command]` > View the controller configuration of Resource Control | PD Control User Guide > Command > `resource-manager [command]` > Modify the controller configuration of Resource Control | PD Control User Guide > Command > `scheduler [show | add | remove | pause | resume | config | describe]``
- Source Line Ranges: `763-821`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tidb`, `tikv`
- Topic Tags: `pd-ctl`, `resource-control`, `resource-manager`, `controller-config`, `request-unit`, `scheduler`, `leader-scheduling`, `pause-resume`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0135_4e5af68153`
- Source ID: `tidb-docs-8.1:pd-control.md#resource-manager-command`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2f7c9ef31ad94d02f11df5c8576c595a038bd13b382c0ab4f27d71456b1c06ce`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-control#resource-manager-command
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-control.md

## Retrieval Guidance

- Use When: Use this chunk when looking for pd-ctl commands to view or modify Resource Control controller configuration or to show, add, remove, pause, resume, configure, or describe schedulers.
- Retrieval Keywords: resource-manager config controller show, resource-manager config controller set ltb-max-wait-duration 30m, ltb-max-wait-duration, enable-controller-trace-log, request-unit, Request Unit (RU), ERROR 8252 (HY000) : Exceeded resource group quota limitation, scheduler show, scheduler add grant-leader-scheduler, scheduler add evict-leader-scheduler, scheduler config evict-leader-scheduler, scheduler config evict-leader-scheduler add-store, scheduler config evict-leader-scheduler delete-store, scheduler add evict-slow-store-scheduler, scheduler remove grant-leader-scheduler-1, scheduler pause balance-region-scheduler, scheduler pause all, scheduler resume balance-region-scheduler, scheduler resume all, scheduler config balance-hot-region-scheduler, scheduler describe balance-region-scheduler
- Follow-up Guidance: The content explains `ltb-max-wait-duration`, `enable-controller-trace-log`, and that the `request-unit` configuration is shown with a note saying not to modify it.
- Classification Note: This is classified as configuration content because it covers controller configuration fields for Resource Control and scheduler policy configuration and control commands.

## Official Source Content

### `resource-manager [command]`
#### View the controller configuration of Resource Control

```bash
resource-manager config controller show
```

```bash
{
    "degraded-mode-wait-duration": "0s",
    "ltb-max-wait-duration": "30s",
    "request-unit": {                    # Configurations of RU. Do not modify.
        "read-base-cost": 0.125,
        "read-per-batch-base-cost": 0.5,
        "read-cost-per-byte": 0.0000152587890625,
        "write-base-cost": 1,
        "write-per-batch-base-cost": 1,
        "write-cost-per-byte": 0.0009765625,
        "read-cpu-ms-cost": 0.3333333333333333
    },
    "enable-controller-trace-log": "false"
}
```

- `ltb-max-wait-duration`: the maximum waiting time of Local Token Bucket (LTB). The default value is `30s`, and the value range is `[0, 24h]`. If the estimated [Request Unit (RU)](https://docs.pingcap.com/tidb/stable/tidb-resource-control#what-is-request-unit-ru) consumption of the SQL request exceeds the current accumulated RU of LTB, the request needs to wait for a certain period of time. If the estimated waiting time exceeds this maximum value, an error message [`ERROR 8252 (HY000) : Exceeded resource group quota limitation`](https://docs.pingcap.com/tidb/stable/error-codes) is returned to the application in advance. Increasing this value can reduce the occurrence of encountering `ERROR 8252` in cases of sudden concurrency increase, large transactions, and large queries.
- `enable-controller-trace-log`: control whether to enable the controller diagnostic log.
#### Modify the controller configuration of Resource Control

To modify the `ltb-max-wait-duration` configuration, use the following command:

```bash
pd-ctl resource-manager config controller set ltb-max-wait-duration 30m
```
### `scheduler [show | add | remove | pause | resume | config | describe]`

Use this command to view and control the scheduling policy.

Usage:

```bash
>> scheduler show                                          // Display all created schedulers
>> scheduler add grant-leader-scheduler 1                  // Schedule all the leaders of the Regions on store 1 to store 1
>> scheduler add evict-leader-scheduler 1                  // Move all the Region leaders on store 1 out
>> scheduler config evict-leader-scheduler                 // Display the stores in which the scheduler is located since v4.0.0
>> scheduler config evict-leader-scheduler add-store 2     // Add leader eviction scheduling for store 2
>> scheduler config evict-leader-scheduler delete-store 2  // Remove leader eviction scheduling for store 2
>> scheduler add evict-slow-store-scheduler                // When there is one and only one slow store, evict all Region leaders of that store
>> scheduler remove grant-leader-scheduler-1               // Remove the corresponding scheduler, and `-1` corresponds to the store ID
>> scheduler pause balance-region-scheduler 10             // Pause the balance-region scheduler for 10 seconds
>> scheduler pause all 10                                  // Pause all schedulers for 10 seconds
>> scheduler resume balance-region-scheduler               // Continue to run the balance-region scheduler
>> scheduler resume all                                    // Continue to run all schedulers
>> scheduler config balance-hot-region-scheduler           // Display the configuration of the balance-hot-region scheduler
>> scheduler describe balance-region-scheduler             // Display the running state and related diagnostic information of the balance-region scheduler
```
