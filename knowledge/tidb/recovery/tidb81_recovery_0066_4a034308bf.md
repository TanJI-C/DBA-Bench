# Unsafe recovery and MVCC corruption recovery commands

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-control.md`
- Source Title: `TiKV Control User Guide`
- Source Heading Path: `TiKV Control User Guide > Subcommands, some options and flags > Force Regions to recover services from failure of multiple replicas (deprecated) | TiKV Control User Guide > Subcommands, some options and flags > Recover from MVCC data corruption`
- Source Line Ranges: `476-528`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`
- Topic Tags: `unsafe-recovery`, `deprecated`, `multi-replica-failure`, `mvcc-corruption`, `local-mode`, `region-recovery`, `store-operations`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0066_4a034308bf`
- Source ID: `tidb-docs-8.1:tikv-control.md#force-regions-to-recover-services-from-failure-of-multiple-replicas-deprecated`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `66b8972e01625ef8853ee897853780f9b1b935a111e8948169c475a9b7ad19cf`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-control#force-regions-to-recover-services-from-failure-of-multiple-replicas-deprecated
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-control.md

## Retrieval Guidance

- Use When: Use this content when looking for tikv-ctl commands for deprecated unsafe Region recovery after multiple replica failures or for recovering TiKV from MVCC data corruption in local mode.
- Retrieval Keywords: unsafe-recover remove-fail-stores, recover-mvcc, --all-regions, -s store_id, -r region_id, -p PD endpoints, local mode, success!, Online Unsafe Recovery, stop the service of the target TiKV store, default write lock CFs, MVCC data corruption
- Follow-up Guidance: The content notes that Online Unsafe Recovery in pd-ctl provides one-stop automatic recovery capabilities, and that recover-mvcc requires PD endpoints without the http prefix to validate the specified region_id.
- Classification Note: This is classified as recovery because the official content describes tikv-ctl procedures to restore Region service after failed stores and to recover from MVCC inconsistency that prevents TiKV from running normally.

## Official Source Content

### Force Regions to recover services from failure of multiple replicas (deprecated)

> **Warning:**
>
> It is not recommended to use this feature. Instead, you can use Online Unsafe Recovery in `pd-ctl` which provides one-stop automatic recovery capabilities. Extra operations such as stopping services are not needed. For detailed introduction, see [Online Unsafe Recovery](https://docs.pingcap.com/tidb/stable/online-unsafe-recovery).

You can use the `unsafe-recover remove-fail-stores` command to remove the failed machines from the peer list of Regions. Before running this command, you need to stop the service of the target TiKV store to release file locks.

The `-s` option accepts multiple `store_id` separated by comma and uses the `-r` flag to specify involved Regions. If you need to perform this operation on all Regions in a specific store, you can simply specify `--all-regions`.

> **Warning:**
>
> - If any misoperation is performed, it might be hard to recover the cluster. Be aware of the potential risks and avoid using this feature in a production environment.
> - If the `--all-regions` option is used, you are expected to run this command on all the remaining stores connected to the cluster. You need to ensure that these healthy stores stop providing services before recovering the damaged stores. Otherwise, the inconsistent peer lists in Region replicas will cause errors when you run `split-region` or `remove-peer`. This further causes inconsistency between other metadata, and finally, the Regions will become unavailable.
> - Once you have run `remove-fail-stores`, you cannot restart the removed nodes or add these nodes to the cluster. Otherwise, the metadata will be inconsistent, and finally, the Regions will be unavailable.

```shell
tikv-ctl --data-dir /path/to/tikv unsafe-recover remove-fail-stores -s 3 -r 1001,1002
```

```
success!
```

```shell
tikv-ctl --data-dir /path/to/tikv unsafe-recover remove-fail-stores -s 4,5 --all-regions
```

Then, after you restart TiKV, the Regions can continue providing services with the remaining healthy replicas. This command is commonly used when multiple TiKV stores are damaged or deleted.

> **Note:**
>
> - You are expected to run this command for all stores where the specified Regions' peers are located.
> - This command only supports the local mode. It prints `success!` when successfully run.
### Recover from MVCC data corruption

Use the `recover-mvcc` command in circumstances where TiKV cannot run normally caused by MVCC data corruption. It cross-checks 3 CFs ("default", "write", "lock") to recover from various kinds of inconsistency.

- Use the `-r` option to specify involved Regions by `region_id`.
- Use the `-p` option to specify PD endpoints.

```shell
tikv-ctl --data-dir /path/to/tikv recover-mvcc -r 1001,1002 -p 127.0.0.1:2379
success!
```

> **Note:**
>
> - This command only supports the local mode. It prints `success!` when successfully run.
> - The argument of the `-p` option specifies the PD endpoints without the `http` prefix. Specifying the PD endpoints is to query whether the specified `region_id` is validated or not.
> - You need to run this command for all stores where specified Regions' peers are located.
