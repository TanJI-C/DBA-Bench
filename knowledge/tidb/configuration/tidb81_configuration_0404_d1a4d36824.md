# Configure topology, placement rules, and DR Auto-Sync mode

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/two-data-centers-in-one-city-deployment.md`
- Source Title: `Two Availability Zones in One Region Deployment`
- Source Heading Path: `Two Availability Zones in One Region Deployment > Configuration | Two Availability Zones in One Region Deployment > Configuration > Example | Two Availability Zones in One Region Deployment > Configuration > Placement Rules | Two Availability Zones in One Region Deployment > Configuration > Enable the DR Auto-Sync mode`
- Source Line Ranges: `35-269`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tiup`, `tikv`, `tidb`
- Topic Tags: `topology`, `placement-rules`, `labels`, `pd-ctl`, `replication-mode`, `dr-auto-sync`, `rollback`, `configuration-file`, `api`, `replication-status`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0404_d1a4d36824`
- Source ID: `tidb-docs-8.1:two-data-centers-in-one-city-deployment.md#configuration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f18bad3ea0ecbd1f9d3b2a55d6dbe3a0a1f073c33adcb225530a4a22b2eba6b2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/two-data-centers-in-one-city-deployment#configuration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/two-data-centers-in-one-city-deployment.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the topology.yaml example, Placement Rules JSON, pd-ctl commands, or PD replication-mode settings for a two availability zones in one region deployment.
- Retrieval Keywords: tiup topology.yaml, replication.location-labels, server.labels, Placement Rules, rule.json, default.json, pd-ctl config placement-rules rule-bundle load --out="default.json", pd-ctl config placement-rules rule-bundle save --in="rule.json", replication-mode = "dr-auto-sync", config set replication-mode dr-auto-sync, label-key, primary-replicas, dr-replicas, wait-store-timeout, wait-recover-timeout, pause-region-split, /pd/api/v1/replication_mode/status
- Follow-up Guidance: This chunk also provides the API response example for checking the current replication status of the cluster with curl against /pd/api/v1/replication_mode/status.
- Classification Note: This chunk is classified as configuration because it contains concrete topology settings, Placement Rules definitions, rollback content, PD DR Auto-Sync parameters, and commands to view replication status.

## Official Source Content

## Configuration
### Example

The following `tiup topology.yaml` example file is a typical topology configuration for the two availability zones in one region deployment mode:

```yaml
# # Global variables are applied to all deployments and used as the default value of
# # the deployments if a specific deployment value is missing.
global:
  user: "tidb"
  ssh_port: 22
  deploy_dir: "/data/tidb_cluster/tidb-deploy"
  data_dir: "/data/tidb_cluster/tidb-data"
server_configs:
  pd:
    replication.location-labels: ["az","rack","host"]
pd_servers:
  - host: 10.63.10.10
    name: "pd-10"
  - host: 10.63.10.11
    name: "pd-11"
  - host: 10.63.10.12
    name: "pd-12"
tidb_servers:
  - host: 10.63.10.10
  - host: 10.63.10.11
  - host: 10.63.10.12
tikv_servers:
  - host: 10.63.10.30
    config:
      server.labels: { az: "east", rack: "east-1", host: "30" }
  - host: 10.63.10.31
    config:
      server.labels: { az: "east", rack: "east-2", host: "31" }
  - host: 10.63.10.32
    config:
      server.labels: { az: "east", rack: "east-3", host: "32" }
  - host: 10.63.10.33
    config:
      server.labels: { az: "west", rack: "west-1", host: "33" }
  - host: 10.63.10.34
    config:
      server.labels: { az: "west", rack: "west-2", host: "34" }
  - host: 10.63.10.35
    config:
      server.labels: { az: "west", rack: "west-3", host: "35" }
monitoring_servers:
  - host: 10.63.10.60
grafana_servers:
  - host: 10.63.10.60
alertmanager_servers:
  - host: 10.63.10.60
```
### Placement Rules

To deploy a cluster based on the planned topology, you need to use [Placement Rules](https://docs.pingcap.com/tidb/stable/configure-placement-rules) to determine the locations of the cluster replicas. Taking the deployment of four replicas (two Voter replicas are at the primary AZ, one Voter replica, and one Learner replica are at the disaster recovery AZ) as an example, you can use the Placement Rules to configure the replicas as follows:

```
cat rule.json
[
  {
    "group_id": "pd",
    "group_index": 0,
    "group_override": false,
    "rules": [
      {
        "group_id": "pd",
        "id": "az-east",
        "start_key": "",
        "end_key": "",
        "role": "voter",
        "count": 3,
        "label_constraints": [
          {
            "key": "az",
            "op": "in",
            "values": [
              "east"
            ]
          }
        ],
        "location_labels": [
          "az",
          "rack",
          "host"
        ]
      },
      {
        "group_id": "pd",
        "id": "az-west-1",
        "start_key": "",
        "end_key": "",
        "role": "follower",
        "count": 2,
        "label_constraints": [
          {
            "key": "az",
            "op": "in",
            "values": [
              "west"
            ]
          }
        ],
        "location_labels": [
          "az",
          "rack",
          "host"
        ]
      },
      {
        "group_id": "pd",
        "id": "az-west-2",
        "start_key": "",
        "end_key": "",
        "role": "learner",
        "count": 1,
        "label_constraints": [
          {
            "key": "az",
            "op": "in",
            "values": [
              "west"
            ]
          }
        ],
        "location_labels": [
          "az",
          "rack",
          "host"
        ]
      }
    ]
  }
]
```

To use the configurations in `rule.json`, run the following command to back up the existing configuration to the `default.json` file and overwrite the existing configuration with `rule.json`:

```bash
pd-ctl config placement-rules rule-bundle load --out="default.json"
pd-ctl config placement-rules rule-bundle save --in="rule.json"
```

If you need to roll back to the previous configuration, you can restore the backup file `default.json` or write the following JSON file manually and overwrite the current configuration with this JSON file:

```
cat default.json
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
        "count": 5
      }
    ]
  }
]
```
### Enable the DR Auto-Sync mode

The replication mode is controlled by PD. You can configure the replication mode in the PD configuration file using one of the following methods:

- Method 1: Configure the PD configuration file, and then deploy a cluster.

    ```toml
    [replication-mode]
    replication-mode = "dr-auto-sync"
    [replication-mode.dr-auto-sync]
    label-key = "az"
    primary = "east"
    dr = "west"
    primary-replicas = 3
    dr-replicas = 2
    wait-store-timeout = "1m"
    wait-recover-timeout = "0s"
    pause-region-split = false  
    ```

- Method 2: If you have deployed a cluster, use pd-ctl commands to modify the configurations of PD.

    ```shell
    config set replication-mode dr-auto-sync
    config set replication-mode dr-auto-sync label-key az
    config set replication-mode dr-auto-sync primary east
    config set replication-mode dr-auto-sync dr west
    config set replication-mode dr-auto-sync primary-replicas 3
    config set replication-mode dr-auto-sync dr-replicas 2
    ```

Descriptions of configuration items:

+ `replication-mode` is the replication mode to be enabled. In the preceding example, it is set to `dr-auto-sync`. By default, the majority protocol is used.
+ `label-key` is used to distinguish different AZs and needs to match Placement Rules. In this example, the primary AZ is "east" and the disaster recovery AZ is "west".
+ `primary-replicas` is the number of Voter replicas in the primary AZ.
+ `dr-replicas` is the number of Voter replicas in the disaster recovery (DR) AZ.
+ `wait-store-timeout` is the waiting time for switching to asynchronous replication mode when network isolation or failure occurs. If the time of network failure exceeds the waiting time, asynchronous replication mode is enabled. The default waiting time is 60 seconds.
+ `wait-recover-timeout` is the waiting time for switching back to the `sync-recover` status after the network recovers. The default value is 0 seconds.
+ `pause-region-split` controls whether to pause Region split operations in the `async_wait` and `async` statuses. Pausing Region split can prevent temporary partial data loss in the DR AZ when synchronizing data in the `sync-recover` status. The default value is `false`.

To check the current replication status of the cluster, use the following API:

```bash
curl http://pd_ip:pd_port/pd/api/v1/replication_mode/status
```

```bash
{
  "mode": "dr-auto-sync",
  "dr-auto-sync": {
    "label-key": "az",
    "state": "sync"
  }
}
```
