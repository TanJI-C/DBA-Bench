# PD control store settings, log level, and TSO parsing

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-control.md`
- Source Title: `PD Control User Guide`
- Source Heading Path: `PD Control User Guide > Command > `store [delete | cancel-delete | label | weight | remove-tombstone | limit ] <store_id> [--jq="<query string>"]` > Manage store labels | PD Control User Guide > Command > `store [delete | cancel-delete | label | weight | remove-tombstone | limit ] <store_id> [--jq="<query string>"]` > Configure store weight | PD Control User Guide > Command > `store [delete | cancel-delete | label | weight | remove-tombstone | limit ] <store_id> [--jq="<query string>"]` > Configure store scheduling speed | PD Control User Guide > Command > `log [fatal | error | warn | info | debug]` | PD Control User Guide > Command > `tso``
- Source Line Ranges: `1055-1137`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`, `tiup`
- Topic Tags: `store-labels`, `store-weight`, `store-limit`, `scheduling-speed`, `log-level`, `tso`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0189_174505bc18`
- Source ID: `tidb-docs-8.1:pd-control.md#manage-store-labels`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `533b602c1fa34f4e7ac5284478e2eef699cdb36cc1b1e1715d322b877bb52318`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-control#manage-store-labels
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-control.md

## Retrieval Guidance

- Use When: Use this content when you need pd-ctl commands for managing store labels, configuring store weight or store limit, setting the PD leader log level, or parsing a TSO value into physical and logical time.
- Retrieval Keywords: store label, store weight, store limit, --rewrite, --delete, store label 1 zone=cn, store label 1 zone=us, store label 1 region=us-est-1 disk=ssd --rewrite, store label 1 disk --delete, store weight 1 5 10, store limit add-peer, store limit remove-peer, store limit all 5, store limit 1 5 add-peer, store limit 1 5 remove-peer, log warn, log [fatal | error | warn | info | debug], tso 395181938313123110, parse TSO, physical and logical time of TSO, TiKV store state Up Disconnect Offline Down Tombstone
- Follow-up Guidance: The content also notes that store labels are merged between TiKV and PD after a TiKV configuration change and restart, and that pd-ctl can check TiKV store states such as Up, Disconnect, Offline, Down, and Tombstone.
- Classification Note: This is classified as operation because the content consists of executable pd-ctl commands for store configuration, PD log level changes, and TSO parsing.

## Official Source Content

#### Manage store labels

To manage the labels of a store, run the `store label` command.

- To set a label with the key being `"zone"` and value being `"cn"` to the store with id of 1, run the following command:

    ```bash
    store label 1 zone=cn
    ```

- To update the label of a store, for example, changing the value of the key `"zone"` from `"cn"` to `"us"` for the store with id of 1, run the following command:

    ```bash
    store label 1 zone=us
    ```

- To rewrite all labels of a store with id of 1, use the `--rewrite` option. Note that this option overwrites all existing labels:

    ```bash
    store label 1 region=us-est-1 disk=ssd --rewrite
    ```

- To delete the `"disk"` label for the store with id of 1, use the `--delete` option:

    ```bash
    store label 1 disk --delete
    ```

> **Note:**
>
> - The label of a store is updated by merging the label in TiKV and that in PD. Specifically, after you modify a store label in the TiKV configuration file and restart the cluster, PD merges its own store label with the TiKV store label, updates the label, and persists the merged result.
> - To manage labels of a store using TiUP, you can run the `store label <id> --force` command to empty the labels stored in PD before restarting the cluster.
#### Configure store weight

To set the leader weight to 5 and Region weight to 10 for the store with id of 1, run the following command:

```bash
store weight 1 5 10
```
#### Configure store scheduling speed

You can set the scheduling speed of stores by using `store limit`. For more details about the principles and usage of `store limit`, see [`store limit`](https://docs.pingcap.com/tidb/stable/configure-store-limit).

```bash
>> store limit                         // Show the speed limit of adding-peer operations and the limit of removing-peer operations per minute in all stores
>> store limit add-peer                // Show the speed limit of adding-peer operations per minute in all stores
>> store limit remove-peer             // Show the limit of removing-peer operations per minute in all stores
>> store limit all 5                   // Set the limit of adding-peer operations to 5 and the limit of removing-peer operations to 5 per minute for all stores
>> store limit 1 5                     // Set the limit of adding-peer operations to 5 and the limit of removing-peer operations to 5 per minute for store 1
>> store limit all 5 add-peer          // Set the limit of adding-peer operations to 5 per minute for all stores
>> store limit 1 5 add-peer            // Set the limit of adding-peer operations to 5 per minute for store 1
>> store limit 1 5 remove-peer         // Set the limit of removing-peer operations to 5 per minute for store 1
>> store limit all 5 remove-peer       // Set the limit of removing-peer operations to 5 per minute for all stores
```

> **Note:**
>
> You can use `pd-ctl` to check the state (`Up`, `Disconnect`, `Offline`, `Down`, or `Tombstone`) of a TiKV store. For the relationship between each state, refer to [Relationship between each state of a TiKV store](https://docs.pingcap.com/tidb/stable/tidb-scheduling#information-collection).
### `log [fatal | error | warn | info | debug]`

Use this command to set the log level of the PD leader.

Usage:

```bash
log warn
```
### `tso`

Use this command to parse the physical and logical time of TSO.

Usage:

```bash
>> tso 395181938313123110        // Parse TSO
system:  2017-10-09 05:50:59 +0800 CST
logic:  120102
```
