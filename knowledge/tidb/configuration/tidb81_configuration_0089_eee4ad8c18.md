# Prepare v2.0+ source and task configuration files

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/manually-upgrade-dm-1.0-to-2.0.md`
- Source Title: `Manually Upgrade TiDB Data Migration from v1.0.x to v2.0+`
- Source Heading Path: `Manually Upgrade TiDB Data Migration from v1.0.x to v2.0+ | Manually Upgrade TiDB Data Migration from v1.0.x to v2.0+ > Step 1: Prepare v2.0+ configuration file | Manually Upgrade TiDB Data Migration from v1.0.x to v2.0+ > Step 1: Prepare v2.0+ configuration file > Upstream database configuration file | Manually Upgrade TiDB Data Migration from v1.0.x to v2.0+ > Step 1: Prepare v2.0+ configuration file > Upstream database configuration file > Upgrade a v1.0.x cluster deployed by DM-Ansible | Manually Upgrade TiDB Data Migration from v1.0.x to v2.0+ > Step 1: Prepare v2.0+ configuration file > Upstream database configuration file > Upgrade a v1.0.x cluster deployed by binary | Manually Upgrade TiDB Data Migration from v1.0.x to v2.0+ > Step 1: Prepare v2.0+ configuration file > Data migration task configuration file`
- Source Line Ranges: `5-102`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`
- Topic Tags: `manual-upgrade`, `source-configuration`, `task-configuration`, `dm-ansible`, `binary-deployment`, `gtid`, `checkpoint-prerequisites`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0089_eee4ad8c18`
- Source ID: `tidb-docs-8.1:dm/manually-upgrade-dm-1.0-to-2.0.md#manually-upgrade-tidb-data-migration-from-v1-0-x-to-v2-0`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `951adab5c9a40274c31dab901e1fc2e1c58a6f0cf6d5e1f6b086926d07edbb1e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/manually-upgrade-dm-1.0-to-2.0#manually-upgrade-tidb-data-migration-from-v1-0-x-to-v2-0
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/manually-upgrade-dm-1.0-to-2.0.md

## Retrieval Guidance

- Use When: Use this chunk when preparing v2.0+ DM source and task configuration files for a manual upgrade from DM v1.0.x, including converting DM-Ansible inventory.ini or binary DM-worker settings into source YAML files.
- Retrieval Keywords: manual upgrade DM v1.0.x to v2.0+, Step 1 Prepare v2.0+ configuration file, upstream database configuration file, data migration task configuration file, dm_worker_servers, inventory.ini, server_id, source_id, mysql_host, mysql_user, mysql_password, mysql_port, DM-worker configuration, server-id, flavor, from.host, from.port, from.user, from.password, source1.yaml, source2.yaml, enable-gtid, parse the binlog or relay log file, GTID sets corresponding to the binlog position
- Follow-up Guidance: If enable-gtid is enabled in the source configuration, the content says you need to parse the binlog or relay log file to obtain the GTID sets corresponding to the binlog position.
- Classification Note: This chunk is classified as configuration because it explains how to prepare v2.0+ source configuration files from v1.0.x DM-worker or DM-Ansible settings and states that the v2.0+ task configuration is basically compatible with v1.0.x.

## Official Source Content

# Manually Upgrade TiDB Data Migration from v1.0.x to v2.0+

This document introduces how to manually upgrade the TiDB DM tool from v1.0.x to v2.0+. The main idea is to use the global checkpoint information in v1.0.x to start a new data migration task in the v2.0+ cluster.

For how to automatically upgrade the TiDB DM tool from v1.0.x to v2.0+, refer to [Using TiUP to automatically import the 1.0 cluster deployed by DM-Ansible](https://docs.pingcap.com/tidb/stable/dm/maintain-dm-using-tiup#import-and-upgrade-a-dm-10-cluster-deployed-using-dm-ansible).

> **Note:**
>
> - Currently, upgrading DM from v1.0.x to v2.0+ is not supported when the data migration task is in the process of full export or full import.
> - As the gRPC protocol used for interaction between the components of the DM cluster is updated greatly, you need to make sure that the DM components (including dmctl) use the same version before and after the upgrade.
> - Because the metadata storage of the DM cluster (such as checkpoint, shard DDL lock status, and online DDL metadata) is updated greatly, the metadata of v1.0.x cannot be reused automatically in v2.0+. So you need to make sure the following requirements are satisfied before performing the upgrade operation:
>     - All data migration tasks are not in the process of shard DDL coordination.
>     - All data migration tasks are not in the process of online DDL coordination.

The steps for manual upgrade are as follows.
## Step 1: Prepare v2.0+ configuration file

The prepared configuration files of v2.0+ include the configuration files of the upstream database and the configuration files of the data migration task.
### Upstream database configuration file

In v2.0+, the [upstream database configuration file](https://docs.pingcap.com/tidb/stable/dm/dm-source-configuration-file) is separated from the process configuration of the DM-worker, so you need to obtain the source configuration based on the [v1.0.x DM-worker configuration](https://docs.pingcap.com/tidb/stable/dm/dm-worker-configuration-file).

> **Note:**
>
> If `enable-gtid` in the source configuration is enabled during the upgrade from v1.0.x to v2.0+, you need to parse the binlog or relay log file to obtain the GTID sets corresponding to the binlog position.
#### Upgrade a v1.0.x cluster deployed by DM-Ansible

Assume that the v1.0.x DM cluster is deployed by DM-Ansible, and the following `dm_worker_servers` configuration is in the `inventory.ini` file:

```ini
[dm_master_servers]
dm_worker1 ansible_host=172.16.10.72 server_id=101 source_id="mysql-replica-01" mysql_host=172.16.10.81 mysql_user=root mysql_password='VjX8cEeTX+qcvZ3bPaO4h0C80pe/1aU=' mysql_port=3306
dm_worker2 ansible_host=172.16.10.73 server_id=102 source_id="mysql-replica-02" mysql_host=172.16.10.82 mysql_user=root mysql_password='VjX8cEeTX+qcvZ3bPaO4h0C80pe/1aU=' mysql_port=3306
```

Then you can convert it to the following two source configuration files:

```yaml
# The source configuration corresponding to the original dm_worker1. For example, it is named as source1.yaml.
server-id: 101                                   # Corresponds to the original `server_id`.
source-id: "mysql-replica-01"                    # Corresponds to the original `source_id`.
from:
  host: "172.16.10.81"                           # Corresponds to the original `mysql_host`.
  port: 3306                                     # Corresponds to the original `mysql_port`.
  user: "root"                                   # Corresponds to the original `mysql_user`.
  password: "VjX8cEeTX+qcvZ3bPaO4h0C80pe/1aU="   # Corresponds to the original `mysql_password`.
```

```yaml
# The source configuration corresponding to the original dm_worker2. For example, it is named as source2.yaml.
server-id: 102                                   # Corresponds to the original `server_id`.
source-id: "mysql-replica-02"                    # Corresponds to the original `source_id`.
from:
  host: "172.16.10.82"                           # Corresponds to the original `mysql_host`.
  port: 3306                                     # Corresponds to the original `mysql_port`.
  user: "root"                                   # Corresponds to the original `mysql_user`.
  password: "VjX8cEeTX+qcvZ3bPaO4h0C80pe/1aU="   # Corresponds to the original `mysql_password`.
```
#### Upgrade a v1.0.x cluster deployed by binary

Assume that the v1.0.x DM cluster is deployed by binary, and the corresponding DM-worker configuration is as follows:

```toml
log-level = "info"
log-file = "dm-worker.log"
worker-addr = ":8262"
server-id = 101
source-id = "mysql-replica-01"
flavor = "mysql"
[from]
host = "172.16.10.81"
user = "root"
password = "VjX8cEeTX+qcvZ3bPaO4h0C80pe/1aU="
port = 3306
```

Then you can convert it to the following source configuration file:

```yaml
server-id: 101                                   # Corresponds to the original `server-id`.
source-id: "mysql-replica-01"                    # Corresponds to the original `source-id`.
flavor: "mysql"                                  # Corresponds to the original `flavor`.
from:
  host: "172.16.10.81"                           # Corresponds to the original `from.host`.
  port: 3306                                     # Corresponds to the original `from.port`.
  user: "root"                                   # Corresponds to the original `from.user`.
  password: "VjX8cEeTX+qcvZ3bPaO4h0C80pe/1aU="   # Corresponds to the original `from.password`.
```
### Data migration task configuration file

For [data migration task configuration guide](https://docs.pingcap.com/tidb/stable/dm/dm-task-configuration-guide), v2.0+ is basically compatible with v1.0.x. You can directly copy the configuration of v1.0.x.
