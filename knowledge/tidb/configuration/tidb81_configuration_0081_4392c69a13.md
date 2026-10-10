# Source configuration template and version note

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-source-configuration-file.md`
- Source Title: `Upstream Database Configuration File of TiDB Data Migration`
- Source Heading Path: `Upstream Database Configuration File of TiDB Data Migration | Upstream Database Configuration File of TiDB Data Migration > Configuration file template`
- Source Line Ranges: `5-61`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `source-config`, `configuration-template`, `gtid`, `relay-log`, `tls`, `encrypted-password`, `version-note`, `data-loss-warning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0081_4392c69a13`
- Source ID: `tidb-docs-8.1:dm/dm-source-configuration-file.md#upstream-database-configuration-file-of-tidb-data-migration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `884b594e080eedc6ccf6cc2f28582a025e3f74cd962f13c4355b8f1e1f4c5042`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-source-configuration-file#upstream-database-configuration-file-of-tidb-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-source-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the upstream database source configuration file template for DM, including `source-id`, `enable-gtid`, `enable-relay`, `from`, `security`, `purge`, `checker`, and `filters`, or when checking the note about `enable-gtid` and `enable-relay` in DM v2.0.1.
- Retrieval Keywords: upstream database configuration file template, source-id, enable-gtid, enable-relay, relay-binlog-name, relay-binlog-gtid, from, host, port, user, password, security, ssl-ca, ssl-cert, ssl-key, purge, checker, case-sensitive, filters, dmctl encrypted password, DM v2.0.1 data loss warning
- Follow-up Guidance: The note states that in DM v2.0.1, `enable-gtid` and `enable-relay` must not both be set to `true`, or loss of incremental data might occur.
- Classification Note: This chunk is classified as configuration because it provides the YAML template and embedded parameter examples for the DM upstream source configuration file.

## Official Source Content

# Upstream Database Configuration File of TiDB Data Migration

This document introduces the configuration file of the upstream database, including a configuration file template and the description of each configuration parameter in this file.
## Configuration file template

The following is a configuration file template of the upstream database:

```yaml
source-id: "mysql-replica-01"

# Whether to enable GTID.
enable-gtid: false

# Whether to enable relay log.
enable-relay: false
relay-binlog-name: ""     # The file name from which DM-worker starts to pull the binlog.
relay-binlog-gtid: ""     # The GTID from which DM-worker starts to pull the binlog.
# relay-dir: "relay-dir"  # The directory used to store relay log. The default value is "relay-dir". This configuration item is marked as deprecated since v6.1 and replaced by a parameter of the same name in the dm-worker configuration.


from:
  host: "127.0.0.1"
  port: 3306
  user: "root"
  password: "ZqMLjZ2j5khNelDEfDoUhkD5aV5fIJOe0fiog9w=" # The user password of the upstream database. It is recommended to use the password encrypted with dmctl.
  security:                       # The TLS configuration of the upstream database
    ssl-ca: "/path/to/ca.pem"
    ssl-cert: "/path/to/cert.pem"
    ssl-key: "/path/to/key.pem"

# purge:
#   interval: 3600
#   expires: 0
#   remain-space: 15

# checker:
#   check-enable: true
#   backoff-rollback: 5m0s
#   backoff-max: 5m0s       # The maximum value of backoff, should be larger than 1s

# Configure binlog event filters. New in DM v2.0.2
# case-sensitive: false
# filters:
# - schema-pattern: dmctl
#   table-pattern: t_1
#   events: []
#   sql-pattern:
#   - alter table .* add column `aaa` int
#   action: Ignore
```

> **Note:**
>
> In DM v2.0.1, DO NOT set `enable-gtid` and `enable-relay` to `true` at the same time. Otherwise, it may cause loss of incremental data.
