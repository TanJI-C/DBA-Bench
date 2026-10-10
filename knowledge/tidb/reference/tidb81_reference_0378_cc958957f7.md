# CLUSTER_INFO topology and instance metadata table

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-cluster-info.md`
- Source Title: `CLUSTER_INFO`
- Source Heading Path: `CLUSTER_INFO`
- Source Line Ranges: `5-63`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `pd`, `tikv`, `cloud`
- Topic Tags: `information_schema`, `cluster_topology`, `instance_metadata`, `version`, `git_hash`, `start_time`, `uptime`, `server_id`, `sql-query`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0378_cc958957f7`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-cluster-info.md#cluster-info`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `39d037cdbb9bce88ff71c46a6aae28381dcd01a3f22309f1152935b3f867b904`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-cluster-info#cluster-info
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-cluster-info.md

## Retrieval Guidance

- Use When: Use this when you need the INFORMATION_SCHEMA table that shows cluster topology, instance metadata, version, Git Hash, start time, uptime, and server ID for TiDB, PD, and TiKV instances.
- Retrieval Keywords: CLUSTER_INFO, information_schema, cluster_info, desc cluster_info, SELECT * FROM cluster_info, TYPE, INSTANCE, STATUS_ADDRESS, VERSION, GIT_HASH, START_TIME, UPTIME, SERVER_ID, cluster topology table, instance metadata, version information, Git Hash, server ID, tidb, pd, tikv
- Follow-up Guidance: The content also shows the field descriptions and example SQL output for `desc cluster_info` and `SELECT * FROM cluster_info`.
- Classification Note: This is classified as a reference because it defines the `CLUSTER_INFO` table, its columns, value meanings, availability note, and example query results from the official documentation.

## Official Source Content

# CLUSTER_INFO

The `CLUSTER_INFO` cluster topology table provides the current topology information of the cluster, the version information of each instance, the Git Hash corresponding to the instance version, the starting time of each instance, and the running time of each instance.

> **Note:**
>
> This table is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

```sql
USE information_schema;
desc cluster_info;
```

```sql
+----------------+-------------+------+------+---------+-------+
| Field          | Type        | Null | Key  | Default | Extra |
+----------------+-------------+------+------+---------+-------+
| TYPE           | varchar(64) | YES  |      | NULL    |       |
| INSTANCE       | varchar(64) | YES  |      | NULL    |       |
| STATUS_ADDRESS | varchar(64) | YES  |      | NULL    |       |
| VERSION        | varchar(64) | YES  |      | NULL    |       |
| GIT_HASH       | varchar(64) | YES  |      | NULL    |       |
| START_TIME     | varchar(32) | YES  |      | NULL    |       |
| UPTIME         | varchar(32) | YES  |      | NULL    |       |
| SERVER_ID      | bigint(21)  | YES  |      | NULL    |       |
+----------------+-------------+------+------+---------+-------+
8 rows in set (0.01 sec)
```

Field description:

* `TYPE`: The instance type. The optional values are `tidb`, `pd`, and `tikv`.
* `INSTANCE`: The instance address, which is a string in the format of `IP:PORT`.
* `STATUS_ADDRESS`: The service address of HTTP API. Some commands in tikv-ctl, pd-ctl, or tidb-ctl might use this API and this address. You can also get more cluster information via this address. Refer to [TiDB HTTP API document](https://github.com/pingcap/tidb/blob/release-8.1/docs/tidb_http_api.md) for details.
* `VERSION`: The semantic version number of the corresponding instance. To be compatible with the MySQL version number, the TiDB version is displayed in the format of `${mysql-version}-${tidb-version}`.
* `GIT_HASH`: The Git Commit Hash when compiling the instance version, which is used to identify whether two instances are of the absolutely consistent version.
* `START_TIME`: The starting time of the corresponding instance.
* `UPTIME`: The uptime of the corresponding instance.
* `SERVER_ID`: The server ID of the corresponding instance.

```sql
SELECT * FROM cluster_info;
```

```sql
+------+-----------------+-----------------+--------------+------------------------------------------+---------------------------+---------------------+
| TYPE | INSTANCE        | STATUS_ADDRESS  | VERSION      | GIT_HASH                                 | START_TIME                | UPTIME              |
+------+-----------------+-----------------+--------------+------------------------------------------+---------------------------+---------------------+
| tidb | 0.0.0.0:4000    | 0.0.0.0:10080   | 4.0.0-beta.2 | 0df3b74f55f8f8fbde39bbd5d471783f49dc10f7 | 2020-07-05T09:25:53-06:00 | 26h39m4.352862693s  |
| pd   | 127.0.0.1:2379  | 127.0.0.1:2379  | 4.1.0-alpha  | 1ad59bcbf36d87082c79a1fffa3b0895234ac862 | 2020-07-05T09:25:47-06:00 | 26h39m10.352868103s |
| tikv | 127.0.0.1:20165 | 127.0.0.1:20180 | 4.1.0-alpha  | b45e052df8fb5d66aa8b3a77b5c992ddbfbb79df | 2020-07-05T09:25:50-06:00 | 26h39m7.352869963s  |
+------+-----------------+-----------------+--------------+------------------------------------------+---------------------------+---------------------+
3 rows in set (0.00 sec)
```
