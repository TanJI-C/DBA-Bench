# Rebuild a PD cluster and recover metadata

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-recover.md`
- Source Title: `PD Recover User Guide`
- Source Heading Path: `PD Recover User Guide > Method 2: Entirely rebuild a PD cluster | PD Recover User Guide > Method 2: Entirely rebuild a PD cluster > Step 1: Get cluster ID | PD Recover User Guide > Method 2: Entirely rebuild a PD cluster > Step 1: Get cluster ID > Get cluster ID from PD log (recommended) | PD Recover User Guide > Method 2: Entirely rebuild a PD cluster > Step 1: Get cluster ID > Get cluster ID from TiDB log | PD Recover User Guide > Method 2: Entirely rebuild a PD cluster > Step 1: Get cluster ID > Get cluster ID from TiKV log | PD Recover User Guide > Method 2: Entirely rebuild a PD cluster > Step 2: Get allocated ID | PD Recover User Guide > Method 2: Entirely rebuild a PD cluster > Step 2: Get allocated ID > Get allocated ID from the monitor (recommended) | PD Recover User Guide > Method 2: Entirely rebuild a PD cluster > Step 2: Get allocated ID > Get allocated ID from PD log | PD Recover User Guide > Method 2: Entirely rebuild a PD cluster > Step 3: Deploy a new PD cluster | PD Recover User Guide > Method 2: Entirely rebuild a PD cluster > Step 4: Use pd-recover | PD Recover User Guide > Method 2: Entirely rebuild a PD cluster > Step 5: Restart the whole cluster`
- Source Line Ranges: `63-158`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `dashboard`, `tidb`, `tikv`, `tiflash`
- Topic Tags: `cluster-rebuild`, `cluster-id`, `allocated-id`, `logs`, `monitoring`, `data-dir`, `restart`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0033_dec4d86d85`
- Source ID: `tidb-docs-8.1:pd-recover.md#method-2-entirely-rebuild-a-pd-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `009841be3e0c6ad6496b472a1e7ce487124f8dc54bdca618745cea3cf7b9aee2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-recover#method-2-entirely-rebuild-a-pd-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-recover.md

## Retrieval Guidance

- Use When: Use this chunk when all PD data is lost but TiDB, TiKV, or TiFlash data still exists and you need to rebuild the PD cluster and recover metadata with `pd-recover`.
- Retrieval Keywords: Method 2: Entirely rebuild a PD cluster, all PD data is lost, get cluster ID, init cluster id, connect to PD cluster, pd.log, tidb.log, tikv.log, get allocated ID, Current ID allocation, PD dashboard, last PD leader, idAllocator allocates a new id, --data-dir, pd-recover, -cluster-id, -alloc-id, restart the whole cluster
- Follow-up Guidance: When the recovery is successful, restart the whole cluster.
- Classification Note: This is recovery content because it covers rebuilding a PD cluster, obtaining `cluster-id` and allocated ID from logs or monitoring, and running `pd-recover` with `-cluster-id` and `-alloc-id`.

## Official Source Content

## Method 2: Entirely rebuild a PD cluster

This method is applicable to scenarios in which all PD data is lost, but the data of other components, such as TiDB, TiKV, and TiFlash, still exists.
### Step 1: Get cluster ID

The cluster ID can be obtained from the log of PD, TiKV, or TiDB. To get the cluster ID, you can view the log directly on the server.
#### Get cluster ID from PD log (recommended)

To get the cluster ID from the PD log, run the following command:

```bash
cat {{/path/to}}/pd.log | grep "init cluster id"
```

```bash
[2019/10/14 10:35:38.880 +00:00] [INFO] [server.go:212] ["init cluster id"] [cluster-id=6747551640615446306]
...
```
#### Get cluster ID from TiDB log

To get the cluster ID from the TiDB log, run the following command:

```bash
cat {{/path/to}}/tidb.log | grep "init cluster id"
```

```bash
2019/10/14 19:23:04.688 client.go:161: [info] [pd] init cluster id 6747551640615446306
...
```
#### Get cluster ID from TiKV log

To get the cluster ID from the TiKV log, run the following command:

```bash
cat {{/path/to}}/tikv.log | grep "connect to PD cluster"
```

```bash
[2019/10/14 07:06:35.278 +00:00] [INFO] [tikv-server.rs:464] ["connect to PD cluster 6747551640615446306"]
...
```
### Step 2: Get allocated ID

The allocated ID value you specify must be larger than the currently largest allocated ID value. To get allocated ID, you can either get it from the monitor, or view the log directly on the server.
#### Get allocated ID from the monitor (recommended)

To get allocated ID from the monitor, you need to make sure that the metrics you are viewing are the metrics of **the last PD leader**, and you can get the largest allocated ID from the **Current ID allocation** panel in PD dashboard.
#### Get allocated ID from PD log

To get the allocated ID from the PD log, you need to make sure that the log you are viewing is the log of **the last PD leader**, and you can get the maximum allocated ID by running the following command:

```bash
cat {{/path/to}}/pd*.log | grep "idAllocator allocates a new id" |  awk -F'=' '{print $2}' | awk -F']' '{print $1}' | sort -r -n | head -n 1
```

```bash
4000
...
```

Or you can simply run the above command in all PD servers to find the largest one.
### Step 3: Deploy a new PD cluster

Before deploying a new PD cluster, you need to stop the existing PD cluster and then delete the previous data directory or specify a new data directory using `--data-dir`.
### Step 4: Use pd-recover

You only need to run `pd-recover` on one PD node. Note that to avoid reallocation, it is recommended to set the `-alloc-id` parameter to a value larger than the allocated ID. For example, if the maximum allocated ID obtained from monitoring or logs is `9000`, it is recommended to pass `10000` or a larger value to the `-alloc-id` parameter.

```bash
./pd-recover -endpoints http://10.0.1.13:2379 -cluster-id 6747551640615446306 -alloc-id 10000
```
### Step 5: Restart the whole cluster

When you see the prompted information that the recovery is successful, restart the whole cluster.
