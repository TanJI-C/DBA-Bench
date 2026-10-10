# Set up DM source for incremental replication

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-large-mysql-shards-to-tidb.md`
- Source Title: `Migrate and Merge MySQL Shards of Large Datasets to TiDB`
- Source Heading Path: `Migrate and Merge MySQL Shards of Large Datasets to TiDB > Step 3. (Optional) Use DM to perform incremental replication | Migrate and Merge MySQL Shards of Large Datasets to TiDB > Step 3. (Optional) Use DM to perform incremental replication > Add the data source`
- Source Line Ranges: `230-272`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`, `tiup`
- Topic Tags: `incremental-replication`, `binlog`, `data-source`, `gtid`, `dmctl`, `source-config`, `upstream-mysql`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0168_61e9b4a028`
- Source ID: `tidb-docs-8.1:migrate-large-mysql-shards-to-tidb.md#step-3-optional-use-dm-to-perform-incremental-replication`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2e2d7678761d5c912ab147c48434c24b244ec297c8b938e7284e3db33a461454`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-large-mysql-shards-to-tidb#step-3-optional-use-dm-to-perform-incremental-replication
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-large-mysql-shards-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented DM source configuration and `dmctl` command for adding an upstream MySQL data source for optional incremental replication from binlog.
- Retrieval Keywords: Step 3. (Optional) Use DM to perform incremental replication, Add the data source, source1.yaml, source-id: "mysql-01", enable-gtid: true, GTID, from:, host, user, password, port, tiup dmctl --master-addr ${advertise-addr} operate-source create source1.yaml, operate-source create, --master-addr, DM-master, DM-worker, upstream MySQL, binlog
- Follow-up Guidance: The content states that you should repeat the same steps until all MySQL upstream instances are added to DM as data sources.
- Classification Note: This is classified as an operation chunk because the official content provides the source YAML example and the exact `tiup dmctl` command to load a data source into a DM cluster.

## Official Source Content

## Step 3. (Optional) Use DM to perform incremental replication

To replicate the data changes based on binlog from a specified position in the source database to TiDB, you can use TiDB DM to perform incremental replication.
### Add the data source

Create a new data source file called `source1.yaml`, which configures an upstream data source into DM, and add the following content:

```yaml
# Configuration.
source-id: "mysql-01" # Must be unique.

# Specifies whether DM-worker pulls binlogs with GTID (Global Transaction Identifier).
# The prerequisite is that you have already enabled GTID in the upstream MySQL.
# If you have configured the upstream database service to switch master between different nodes automatically, you must enable GTID.
enable-gtid: true

from:
  host: "${host}"           # For example: 172.16.10.81
  user: "root"
  password: "${password}"   # Plaintext passwords are supported but not recommended. It is recommended that you use dmctl encrypt to encrypt plaintext passwords.
  port: ${port}             # For example: 3306
```

Run the following command in a terminal. Use `tiup dmctl` to load the data source configuration into the DM cluster:

```shell
tiup dmctl --master-addr ${advertise-addr} operate-source create source1.yaml
```

The parameters are described as follows.

|Parameter      | Description |
|-              |-            |
|`--master-addr`         | {advertise-addr} of any DM-master node in the cluster that dmctl connects to. For example: 172.16.10.71:8261|
| `operate-source create` | Load data sources to DM clusters. |

Repeat the above steps until all MySQL upstream instances are added to the DM as data sources.
