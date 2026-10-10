# Log redaction configuration across TiDB components

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/log-redaction.md`
- Source Title: `Log Redaction`
- Source Heading Path: `Log Redaction | Log Redaction > Log redaction in TiDB side | Log Redaction > Log redaction in TiKV side | Log Redaction > Log redaction in PD side | Log Redaction > Log redaction in TiFlash side`
- Source Line Ranges: `5-50`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`
- Topic Tags: `log-redaction`, `security`, `sensitive-data`, `logging`, `configuration`, `system-variable`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0115_98b4f9c304`
- Source ID: `tidb-docs-8.1:log-redaction.md#log-redaction`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `211ed405dfed770cf6c5d8254b1cf2f177bd7a3c2f1cecc34d75e2fbab07fb00`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/log-redaction#log-redaction
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/log-redaction.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about enabling log redaction for sensitive data in TiDB, TiKV, PD, or TiFlash logs and identifying the exact configuration names or SQL variable involved.
- Retrieval Keywords: log redaction, tidb_redact_log, global.tidb_redact_log, set @@global.tidb_redact_log=1;, security.redact-info-log, security.redact_info_log, TiDB side, TiKV side, PD side, TiFlash side, tiflash-server, tiflash-learner, sensitive data, logging, Duplicate entry '?' for key 't.a'
- Follow-up Guidance: The content also shows that after setting `@@global.tidb_redact_log=1`, logs generated in new sessions redact SQL values and error details with `?`.
- Classification Note: This is classified as configuration because the content defines component-specific settings and a system variable for enabling log redaction across TiDB, TiKV, PD, and TiFlash.

## Official Source Content

# Log Redaction

When TiDB provides detailed log information, it might print sensitive data (for example, user data) in the log, which causes data security risks. To avoid such risks, each component (TiDB, TiKV, and PD) provides a configuration item that enables log redaction to shield user data values.
## Log redaction in TiDB side

To enable log redaction in the TiDB side, set the value of [`global.tidb_redact_log`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_redact_log) to `1`. This configuration value defaults to `0`, which means that log redaction is disabled.

You can use the `set` syntax to set the global variable `tidb_redact_log`:

```sql
set @@global.tidb_redact_log=1;
```

After the setting, all logs generated in new sessions are redacted:

```sql
create table t (a int, unique key (a));
Query OK, 0 rows affected (0.00 sec)

insert into t values (1),(1);
ERROR 1062 (23000): Duplicate entry '1' for key 't.a'
```

The error log for the `INSERT` statement above is printed as follows:

```
[2020/10/20 11:45:49.539 +08:00] [INFO] [conn.go:800] ["command dispatched failed"] [conn=5] [connInfo="id:5, addr:127.0.0.1:57222 status:10, collation:utf8_general_ci,  user:root"] [command=Query] [status="inTxn:0, autocommit:1"] [sql="insert into t values ( ? ) , ( ? )"] [txn_mode=OPTIMISTIC] [err="[kv:1062]Duplicate entry '?' for key 't.a'"]
```

From the error log above, you can see that all sensitive information is shielded using `?` after `tidb_redact_log` is enabled. In this way, data security risks are avoided.
## Log redaction in TiKV side

To enable log redaction in the TiKV side, set the value of [`security.redact-info-log`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#redact-info-log-new-in-v408) to `true`. This configuration value defaults to `false`, which means that log redaction is disabled.
## Log redaction in PD side

To enable log redaction in the PD side, set the value of [`security.redact-info-log`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#redact-info-log-new-in-v50) to `true`. This configuration value defaults to `false`, which means that log redaction is disabled.
## Log redaction in TiFlash side

To enable log redaction in the TiFlash side, set both the [`security.redact_info_log`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file) value in tiflash-server and the [`security.redact-info-log`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflash-learnertoml-file) value in tiflash-learner to `true`. Both configuration values default to `false`, which means that log redaction is disabled.
