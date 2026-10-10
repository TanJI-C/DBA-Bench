# Region failure inspection and tombstone handling

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-control.md`
- Source Title: `TiKV Control User Guide`
- Source Heading Path: `TiKV Control User Guide > Subcommands, some options and flags > Set a Region to tombstone | TiKV Control User Guide > Subcommands, some options and flags > Send a `consistency-check` request to TiKV | TiKV Control User Guide > Subcommands, some options and flags > Dump snapshot meta | TiKV Control User Guide > Subcommands, some options and flags > Print the Regions where the Raft state machine corrupts | TiKV Control User Guide > Subcommands, some options and flags > View Region properties`
- Source Line Ranges: `329-414`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`
- Topic Tags: `tombstone`, `consistency-check`, `snapshot-meta`, `bad-regions`, `raft`, `corruption`, `region-properties`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0065_b6073ae478`
- Source ID: `tidb-docs-8.1:tikv-control.md#set-a-region-to-tombstone`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7283cab221828c8453eac3805bf1d7439e78d7f5713f4635ca6d5ed24a0f9e51`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-control#set-a-region-to-tombstone
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-control.md

## Retrieval Guidance

- Use When: Use this chunk when you need tikv-ctl guidance for tombstoning Regions, running consistency-check, dumping snapshot meta, listing bad-regions, or viewing Region properties during Region failure investigation.
- Retrieval Keywords: tombstone, remove-peer, pd-ctl operator add remove-peer <region_id> <store_id>, --force, -p 127.0.0.1:2379, consistency-check, Leader is on store 1, bad-regions, all regions are healthy, snapshot meta, Dump snapshot meta, region-properties, Raft state machine, last index, commit index, apply index, loss of Raft log
- Follow-up Guidance: The content states that tombstone only supports local mode, consistency-check only supports remote mode and is not recommended because it is incompatible with garbage collection in TiDB, and even a success result still requires checking whether TiKV panics.
- Classification Note: This is classified as recovery because the official content centers on handling damaged Raft state machines, skipping problematic Regions at startup, checking replica consistency, and identifying bad Regions.

## Official Source Content

### Set a Region to tombstone

The `tombstone` command is usually used in circumstances where the sync-log is not enabled, and some data written in the Raft state machine is lost caused by power down.

In a TiKV instance, you can use this command to set the status of some Regions to tombstone. Then when you restart the instance, those Regions are skipped to avoid the restart failure caused by damaged Raft state machines of those Regions. Those Regions need to have enough healthy replicas in other TiKV instances to be able to continue the reads and writes through the Raft mechanism.

In general cases, you can remove the corresponding Peer of this Region using the `remove-peer` command:

```shell
pd-ctl operator add remove-peer <region_id> <store_id>
```

Then use the `tikv-ctl` tool to set a Region to tombstone on the corresponding TiKV instance to skip the health check for this Region at startup:

```shell
tikv-ctl --data-dir /path/to/tikv tombstone -p 127.0.0.1:2379 -r <region_id>
```

```
success!
```

However, in some cases, you cannot easily remove this Peer of this Region from PD, so you can specify the `--force` option in `tikv-ctl` to forcibly set the Peer to tombstone:

```shell
tikv-ctl --data-dir /path/to/tikv tombstone -p 127.0.0.1:2379 -r <region_id>,<region_id> --force
```

```
success!
```

> **Note:**
>
> - The `tombstone` command only supports the local mode.
> - The argument of the `-p` option specifies the PD endpoints without the `http` prefix. Specifying the PD endpoints is to query whether PD can safely switch to Tombstone.
### Send a `consistency-check` request to TiKV

Use the `consistency-check` command to execute a consistency check among replicas in the corresponding Raft of a specific Region. If the check fails, TiKV itself panics. If the TiKV instance specified by `--host` is not the Region leader, an error is reported.

```shell
tikv-ctl --host 127.0.0.1:20160 consistency-check -r 2
success!
tikv-ctl --host 127.0.0.1:20161 consistency-check -r 2
DebugClient::check_region_consistency: RpcFailure(RpcStatus { status: Unknown, details: Some("StringError(\"Leader is on store 1\")") })
```

> **Note:**
>
> - It is **NOT** recommended to use the `consistency-check` command, because it is incompatible with the garbage collection in TiDB and might mistakenly report an error.
> - This command only supports the remote mode.
> - Even if this command returns `success!`, you need to check whether TiKV panics. This is because this command is only a proposal that requests a consistency check for the leader, and you cannot know from the client whether the whole check process is successful or not.
### Dump snapshot meta

This sub-command is used to parse a snapshot meta file at given path and print the result.
### Print the Regions where the Raft state machine corrupts

To avoid checking the Regions while TiKV is started, you can use the `tombstone` command to set the Regions where the Raft state machine reports an error to Tombstone. Before running this command, use the `bad-regions` command to find out the Regions with errors, so as to combine multiple tools for automated processing.

```shell
tikv-ctl --data-dir /path/to/tikv bad-regions
```

```
all regions are healthy
```

If the command is successfully executed, it prints the above information. If the command fails, it prints the list of bad Regions. Currently, the errors that can be detected include the mismatches between `last index`, `commit index` and `apply index`, and the loss of Raft log. Other conditions like the damage of snapshot files still need further support.
### View Region properties

- To view in local the properties of Region 2 on the TiKV instance that is deployed in `/path/to/tikv`:

    ```shell
    tikv-ctl --data-dir /path/to/tikv/data region-properties -r 2
    ```

- To view online the properties of Region 2 on the TiKV instance that is running on `127.0.0.1:20160`:

    ```shell
    tikv-ctl --host 127.0.0.1:20160 region-properties -r 2
    ```
