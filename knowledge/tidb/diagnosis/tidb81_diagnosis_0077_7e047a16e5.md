# TiCDC troubleshooting for timezone, upgrade compatibility, buffering, DDL blocking, GC safepoint, and Kafka size errors

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/troubleshoot-ticdc.md`
- Source Title: `Troubleshoot TiCDC`
- Source Heading Path: `Troubleshoot TiCDC > How do I handle the `Error 1298: Unknown or incorrect time zone: 'UTC'` error when creating the replication task or replicating data to MySQL? | Troubleshoot TiCDC > How do I handle the incompatibility issue of configuration files caused by TiCDC upgrade? | Troubleshoot TiCDC > The `start-ts` timestamp of the TiCDC task is quite different from the current time. During the execution of this task, replication is interrupted and an error `[CDC:ErrBufferReachLimit]` occurs. What should I do? | Troubleshoot TiCDC > When the downstream of a changefeed is a database similar to MySQL and TiCDC executes a time-consuming DDL statement, all other changefeeds are blocked. What should I do? | Troubleshoot TiCDC > The `[tikv:9006]GC life time is shorter than transaction duration, transaction starts at xx, GC safe point is yy` error is reported when I use TiCDC to create a changefeed. What should I do? | Troubleshoot TiCDC > When I use TiCDC to replicate messages to Kafka, Kafka returns the `Message was too large` error. Why?`
- Source Line Ranges: `59-120`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `pd`, `tikv`, `br`
- Topic Tags: `timezone`, `mysql`, `upgrade`, `compatibility`, `start-ts`, `buffer-limit`, `ddl`, `blocking`, `gc`, `kafka`, `message-size`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0077_7e047a16e5`
- Source ID: `tidb-docs-8.1:ticdc/troubleshoot-ticdc.md#how-do-i-handle-the-error-1298-unknown-or-incorrect-time-zone-utc-error-when-creating-the-replication-task-or-replicating-data-to-mysql`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9039e485d407dac52f2f32d89ead54351b21884e3ce3cfa42269a8a61be7ac0b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/troubleshoot-ticdc#how-do-i-handle-the-error-1298-unknown-or-incorrect-time-zone-utc-error-when-creating-the-replication-task-or-replicating-data-to-mysql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/troubleshoot-ticdc.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting TiCDC errors or behavior related to MySQL time zone loading, configuration incompatibility after upgrade, `[CDC:ErrBufferReachLimit]`, long-running downstream DDL blocking other changefeeds, GC safepoint checks, or Kafka `Message was too large` errors.
- Retrieval Keywords: Error 1298: Unknown or incorrect time zone: 'UTC', mysql_tzinfo_to_sql, time-zone="", time-zone="Asia/Shanghai", tz, Notes for compatibility, ticdc-compatibility, start-ts, [CDC:ErrBufferReachLimit], unified sorter, BR tool, incremental backup and restore, apply job, ignore-txn-start-ts, [tikv:9006]GC life time is shorter than transaction duration, pd-ctl service-gc-safepoint --pd <pd-addrs>, --disable-gc-check, gc_worker service_id, Message was too large, max-message-bytes, message.max.bytes, replica.fetch.max.bytes, fetch.message.max.bytes
- Follow-up Guidance: The content includes exact commands, configuration items, and log fields such as `mysql_tzinfo_to_sql`, `pd-ctl service-gc-safepoint`, `--disable-gc-check`, `apply job`, and Kafka broker byte limit settings.
- Classification Note: This chunk is classified as diagnosis because it groups several specific TiCDC troubleshooting cases and the exact error strings, configuration names, and operational conditions used to identify them.

## Official Source Content

## How do I handle the `Error 1298: Unknown or incorrect time zone: 'UTC'` error when creating the replication task or replicating data to MySQL?

This error is returned when the downstream MySQL does not load the time zone. You can load the time zone by running [`mysql_tzinfo_to_sql`](https://dev.mysql.com/doc/refman/8.0/en/mysql-tzinfo-to-sql.html). After loading the time zone, you can create tasks and replicate data normally.

```shell
mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root mysql -p
```

If the output of the command above is similar to the following one, the import is successful:

```
Enter password:
Warning: Unable to load '/usr/share/zoneinfo/iso3166.tab' as time zone. Skipping it.
Warning: Unable to load '/usr/share/zoneinfo/leap-seconds.list' as time zone. Skipping it.
Warning: Unable to load '/usr/share/zoneinfo/zone.tab' as time zone. Skipping it.
Warning: Unable to load '/usr/share/zoneinfo/zone1970.tab' as time zone. Skipping it.
```

If the downstream is a special MySQL environment (a public cloud RDS or some MySQL derivative versions) and importing the time zone using the preceding method fails, you can use the default time zone of the downstream by setting `time-zone` to an empty value, such as `time-zone=""`.

When using time zones in TiCDC, it is recommended to explicitly specify the time zone, such as `time-zone="Asia/Shanghai"`. Also, make sure that the `tz` specified in TiCDC server configurations and the `time-zone` specified in Sink URI are consistent with the time zone configuration of the downstream database. This prevents data inconsistency caused by inconsistent time zones.
## How do I handle the incompatibility issue of configuration files caused by TiCDC upgrade?

Refer to [Notes for compatibility](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-compatibility).
## The `start-ts` timestamp of the TiCDC task is quite different from the current time. During the execution of this task, replication is interrupted and an error `[CDC:ErrBufferReachLimit]` occurs. What should I do?

Since v4.0.9, you can try to enable the unified sorter feature in your replication task, or use the BR tool for an incremental backup and restore, and then start the TiCDC replication task from a new time.
## When the downstream of a changefeed is a database similar to MySQL and TiCDC executes a time-consuming DDL statement, all other changefeeds are blocked. What should I do?

1. Pause the execution of the changefeed that contains the time-consuming DDL statement. Then you can see that other changefeeds are no longer blocked.
2. Search for the `apply job` field in the TiCDC log and confirm the `start-ts` of the time-consuming DDL statement.
3. Manually execute the DDL statement in the downstream. After the execution finishes, go on performing the following operations.
4. Modify the changefeed configuration and add the above `start-ts` to the `ignore-txn-start-ts` configuration item.
5. Resume the paused changefeed.
## The `[tikv:9006]GC life time is shorter than transaction duration, transaction starts at xx, GC safe point is yy` error is reported when I use TiCDC to create a changefeed. What should I do?

You need to run the `pd-ctl service-gc-safepoint --pd <pd-addrs>` command to query the current GC safepoint and service GC safepoint. If the GC safepoint is smaller than the `start-ts` of the TiCDC replication task (changefeed), you can directly add the `--disable-gc-check` option to the `cdc cli create changefeed` command to create a changefeed.

If the result of `pd-ctl service-gc-safepoint --pd <pd-addrs>` does not have `gc_worker service_id`:

- If your PD version is v4.0.8 or earlier, refer to [PD issue #3128](https://github.com/tikv/pd/issues/3128) for details.
- If your PD is upgraded from v4.0.8 or an earlier version to a later version, refer to [PD issue #3366](https://github.com/tikv/pd/issues/3366) for details.
## When I use TiCDC to replicate messages to Kafka, Kafka returns the `Message was too large` error. Why?

For TiCDC v4.0.8 or earlier versions, you cannot effectively control the size of the message output to Kafka only by configuring the `max-message-bytes` setting for Kafka in the Sink URI. To control the message size, you also need to increase the limit on the bytes of messages to be received by Kafka. To add such a limit, add the following configuration to the Kafka server configuration.

```
# The maximum byte number of a message that the broker receives
message.max.bytes=2147483648
# The maximum byte number of a message that the broker copies
replica.fetch.max.bytes=2147483648
# The maximum message byte number that the consumer side reads
fetch.message.max.bytes=2147483648
```
