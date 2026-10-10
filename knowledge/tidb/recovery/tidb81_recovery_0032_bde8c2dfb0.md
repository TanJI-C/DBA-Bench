# Recover PD from a surviving node

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-recover.md`
- Source Title: `PD Recover User Guide`
- Source Heading Path: `PD Recover User Guide > Method 1: Recover a PD cluster using a surviving PD node | PD Recover User Guide > Method 1: Recover a PD cluster using a surviving PD node > Step 1: Stop all nodes | PD Recover User Guide > Method 1: Recover a PD cluster using a surviving PD node > Step 2: Start the surviving PD node | PD Recover User Guide > Method 1: Recover a PD cluster using a surviving PD node > Step 3: Repair metadata using `pd-recover` | PD Recover User Guide > Method 1: Recover a PD cluster using a surviving PD node > Step 4: Restart the PD node | PD Recover User Guide > Method 1: Recover a PD cluster using a surviving PD node > Step 5: Scale out PD and start the cluster`
- Source Line Ranges: `25-62`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `disaster-recovery`, `force-new-cluster`, `metadata-repair`, `alloc-id`, `tso`, `ntp`, `restart`, `scale-out`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0032_bde8c2dfb0`
- Source ID: `tidb-docs-8.1:pd-recover.md#method-1-recover-a-pd-cluster-using-a-surviving-pd-node`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `03a65ae1cd7c40a50f733e3027dbbd08471b00bb5bc5a66109ae3ef20adf8269`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-recover#method-1-recover-a-pd-cluster-using-a-surviving-pd-node
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-recover.md

## Retrieval Guidance

- Use When: Use this chunk when recovering a PD cluster from a surviving PD node after a majority of PD nodes experience an unrecoverable error and the cluster cannot provide services.
- Retrieval Keywords: Method 1: Recover a PD cluster using a surviving PD node, majority of PD nodes, unrecoverable error, stop all nodes, TiDB TiKV TiFlash processes, --force-new-cluster, pd-server, pd-recover --from-old-member, --endpoints=http://127.0.0.1:2379, alloc_id, tso, recovery is successful, scale out PD cluster, deployment tool, NTP clock synchronization service
- Follow-up Guidance: After `recovery is successful`, restart the PD node, scale out the PD cluster using the deployment tool, and start the other components so the PD service is available.
- Classification Note: This is recovery content because it gives a step-by-step disaster recovery procedure using a surviving PD node, including `--force-new-cluster` and metadata repair with `pd-recover`.

## Official Source Content

## Method 1: Recover a PD cluster using a surviving PD node

When a majority of PD nodes in a cluster experience an unrecoverable error, the cluster becomes unable to provide services. If there are any surviving PD nodes, you can recover the service by selecting a surviving PD node and forcibly modifying the members of the Raft Group. The steps are as follows:
### Step 1: Stop all nodes

To prevent data corruption or other unrecoverable errors caused by interactions with PD parameters during the recovery process, stop the TiDB, TiKV, and TiFlash processes in the cluster.
### Step 2: Start the surviving PD node

Start the surviving PD node using the `--force-new-cluster` startup parameter. The following is an example:

```shell
./bin/pd-server --force-new-cluster --name=pd-127.0.0.10-2379 --client-urls=http://0.0.0.0:2379 --advertise-client-urls=http://127.0.0.1:2379 --peer-urls=http://0.0.0.0:2380 --advertise-peer-urls=http://127.0.0.1:2380 --config=conf/pd.toml
```
### Step 3: Repair metadata using `pd-recover`

Since this method relies on a minority PD node to recover the service, the node might contain outdated data. If the `alloc_id` and `tso` data roll back, the cluster data might be corrupted or unavailable. To prevent this, you need to use `pd-recover` to modify the metadata to ensure that the node can provide correct allocation IDs and TSO services. The following is an example:

```shell
./bin/pd-recover --from-old-member --endpoints=http://127.0.0.1:2379 # Specify the corresponding PD address
```

> **Note:**
>
> In this step, the `alloc_id` in the storage automatically increases by a safe value of `100000000`. As a result, the subsequent cluster will allocate larger IDs.
>
> Additionally, `pd-recover` does not modify the TSO. Therefore, before performing this step, make sure that the local time is later than the time when the failure occurs, and verify that the NTP clock synchronization service is enabled between the PD components before the failure. If it is not enabled, you need to adjust the local clock to a future time to prevent the TSO from rolling back.
### Step 4: Restart the PD node

Once you see the prompt message `recovery is successful`, restart the PD node.
### Step 5: Scale out PD and start the cluster

Scale out the PD cluster using the deployment tool and start the other components in the cluster. At this point, the PD service is available.
