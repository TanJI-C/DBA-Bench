# Relay log purge and automatic purge settings

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/relay-log.md`
- Source Title: `Data Migration Relay Log`
- Source Heading Path: `Data Migration Relay Log > Use relay log > Purge relay logs | Data Migration Relay Log > Use relay log > Purge relay logs > Automatic purge`
- Source Line Ranges: `236-269`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `relay-log`, `purge`, `automatic-purge`, `retention`, `disk-space`, `expiration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0129_64182de164`
- Source ID: `tidb-docs-8.1:dm/relay-log.md#purge-relay-logs`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b6f2d0843baa4ee1299a1a82f80e921e8fc9e952abb7a2e71272d9b05da1234f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/relay-log#purge-relay-logs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/relay-log.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks how DM purges relay logs, what automatic purge settings mean, or how `purge.interval`, `purge.expires`, and `purge.remain-space` affect relay log retention and disk space handling.
- Retrieval Keywords: Purge relay logs, manual purge, automatic purge, active relay log, expired relay log, purge:, interval: 3600, expires: 24, remain-space: 15, purge.interval, purge.expires, purge.remain-space, remaining disk space, DM-worker machine, DM-master tries to purge the relay log securely
- Follow-up Guidance: The source defines active relay log and expired relay log and includes a YAML example for configuring automatic purge in the source configuration file.
- Classification Note: This is classified as operation because it describes relay log purge behavior and the configuration fields used to control automatic purge.

## Official Source Content

### Purge relay logs

DM provides two ways to purge relay logs: manual purge and automatic purge. Neither of these two methods purges active relay logs.

> **Note:**
>
> - Active relay log: The relay log is being used by a data migration task. An active relay log is currently only updated and written in the Syncer Unit. If a data migration task in All mode spends more time on full export/import than the expiration time configured in the purge of the data source, the relay log is still purged.
>
> - Expired relay log: The difference between the last modification time of the relay log file and the current time is greater than the value of the `expires` field in the configuration file.
#### Automatic purge

You can enable automatic purge and configure its strategy in the source configuration file. See the following example:

```yaml
# relay log purge strategy
purge:
    interval: 3600
    expires: 24
    remain-space: 15
```

+ `purge.interval`
    - The interval of automatic purge in the background, in seconds.
    - "3600" by default, indicating a background purge task is performed every 3600 seconds.

+ `purge.expires`
    - The number of hours for which the relay log (that has been previously written to the relay processing unit, and that is not being used or will not be read later by the currently running data migration task) can be retained before being purged in the automatic background purge.
    - "0" by default, indicating data purge is not performed according to the update time of the relay log.

+ `purge.remain-space`
    - The amount of remaining disk space in GB less than which the specified DM-worker machine tries to purge the relay log that can be purged securely in the automatic background purge. If it is set to `0`, data purge is not performed according to the remaining disk space.
    - "15" by default, indicating when the available disk space is less than 15 GB, DM-master tries to purge the relay log securely.
