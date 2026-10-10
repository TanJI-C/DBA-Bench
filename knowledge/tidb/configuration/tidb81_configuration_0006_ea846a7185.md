# Configure read-only TiKV nodes, placement rules, and follower reads

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/readonly-nodes.md`
- Source Title: `Best Practices for Read-Only Storage Nodes`
- Source Heading Path: `Best Practices for Read-Only Storage Nodes | Best Practices for Read-Only Storage Nodes > Procedures | Best Practices for Read-Only Storage Nodes > Procedures > 1. Specify some TiKV nodes as read-only | Best Practices for Read-Only Storage Nodes > Procedures > 2. Use Placement Rules to store data on read-only nodes as learners | Best Practices for Read-Only Storage Nodes > Procedures > 3. Use Follower Read to read data from read-only nodes | Best Practices for Read-Only Storage Nodes > Procedures > 3. Use Follower Read to read data from read-only nodes > 3.1 Use Follower Read in TiDB | Best Practices for Read-Only Storage Nodes > Procedures > 3. Use Follower Read to read data from read-only nodes > 3.2 Use Follower Read in TiSpark | Best Practices for Read-Only Storage Nodes > Procedures > 3. Use Follower Read to read data from read-only nodes > 3.3 Use Follower Read when backing up cluster data`
- Source Line Ranges: `5-131`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`, `tidb`, `br`
- Topic Tags: `read-only-nodes`, `labels`, `placement-rules`, `learners`, `follower-read`, `replica-read`, `backup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0006_ea846a7185`
- Source ID: `tidb-docs-8.1:best-practices/readonly-nodes.md#best-practices-for-read-only-storage-nodes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `581a6c29abd50ecf86d2fe6f27b71506d57697d3a0b8d0398f475a13be193940`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/readonly-nodes#best-practices-for-read-only-storage-nodes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/readonly-nodes.md

## Retrieval Guidance

- Use When: Use this when looking for how to mark TiKV nodes as read-only, place learner replicas on them with PD placement rules, and direct TiDB, TiSpark, or BR reads to those nodes.
- Retrieval Keywords: $mode: readonly, tiup cluster edit-config, pd-ctl config placement-rules, rule-bundle load --out="rules.json", rule-bundle save --in="rules.json", Placement Rules, role: learner, label_constraints, key: "$mode", values: ["readonly"], tidb_replica_read, set tidb_replica_read=learner;, spark.tispark.replica_read learner, tiup br backup full --replica-read-label '$mode:readonly', Follower Read, learner, read-only storage nodes
- Follow-up Guidance: The content notes that large datasets can take time to fully replicate to read-only nodes, and that the learner number of each label cannot exceed 1 because backup can otherwise generate duplicate data.
- Classification Note: This is classified as configuration because the content defines TiKV labels, PD placement rules, TiDB and TiSpark replica-read settings, and a BR backup option for using read-only nodes.

## Official Source Content

# Best Practices for Read-Only Storage Nodes

This document introduces how to configure read-only storage nodes and how to direct backup, analysis, testing, and other traffic to these nodes. In this way, loads with high tolerance for delay can be physically isolated from important online services.
## Procedures
### 1. Specify some TiKV nodes as read-only

To specify some TiKV nodes as read-only, you can mark these nodes with a special label (use `$` as the prefix of the label key). Unless you explicitly specify these nodes to store some data using Placement Rules, PD does not schedule any data to these nodes.

You can configure a read-only node by running the `tiup cluster edit-config` command:

```
tikv_servers:
  - host: ...
    ...
    labels:
      $mode: readonly
```
### 2. Use Placement Rules to store data on read-only nodes as learners

1. Run the `pd-ctl config placement-rules` command to export the default Placement Rules:

    ```shell
    pd-ctl config placement-rules rule-bundle load --out="rules.json"
    ```

    If you have not configured Placement Rules before, the output is as follows:

    ```json
    [
      {
        "group_id": "pd",
        "group_index": 0,
        "group_override": false,
        "rules": [
          {
            "group_id": "pd",
            "id": "default",
            "start_key": "",
            "end_key": "",
            "role": "voter",
            "count": 3
          }
        ]
      }
    ]
    ```

2. Store all data on the read-only nodes as a learner. The following example is based on the default configuration:

    ```json
    [
      {
        "group_id": "pd",
        "group_index": 0,
        "group_override": false,
        "rules": [
          {
            "group_id": "pd",
            "id": "default",
            "start_key": "",
            "end_key": "",
            "role": "voter",
            "count": 3
          },
          {
            "group_id": "pd",
            "id": "readonly",
            "start_key": "",
            "end_key": "",
            "role": "learner",
            "count": 1,
            "label_constraints": [
              {
                "key": "$mode",
                "op": "in",
                "values": [
                  "readonly"
                ]
              }
            ],
            "version": 1
          }
        ]
      }
    ]
    ```

3. Use the `pd-ctl config placement-rules` command to write the preceding configurations to PD:

    ```shell
    pd-ctl config placement-rules rule-bundle save --in="rules.json"
    ```

> **Note:**
>
> - If you perform the preceding operations on a cluster with a large dataset, the entire cluster might need some time to completely replicate data to read-only nodes. During this period, the read-only nodes might not be able to provide services.
> - Because of the special implementation of backup, the learner number of each label cannot exceed 1. Otherwise, it will generate duplicate data during backup.
### 3. Use Follower Read to read data from read-only nodes
#### 3.1 Use Follower Read in TiDB

To read data from read-only nodes when using TiDB, you can set the system variable [`tidb_replica_read`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_replica_read-new-in-v40) to `learner`:

```sql
set tidb_replica_read=learner;
```
#### 3.2 Use Follower Read in TiSpark

To read data from read-only nodes when using TiSpark, you can set the configuration item `spark.tispark.replica_read` to `learner` in the Spark configuration file:

```
spark.tispark.replica_read learner
```
#### 3.3 Use Follower Read when backing up cluster data

To read data from read-only nodes when backing up cluster data, you can specify the `--replica-read-label` option in the br command line. Note that when running the following command in shell, you need to use single quotes to wrap the label to prevent `$` from being parsed.

```shell
tiup br backup full ... --replica-read-label '$mode:readonly'
```
