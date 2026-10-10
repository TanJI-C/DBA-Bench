# Enable and disable relay log across versions

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/relay-log.md`
- Source Title: `Data Migration Relay Log`
- Source Heading Path: `Data Migration Relay Log > Use relay log > Enable and disable relay log`
- Source Line Ranges: `32-111`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `relay-log`, `enable-relay`, `start-relay`, `stop-relay`, `version-specific`, `deprecation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0127_c44ce520fa`
- Source ID: `tidb-docs-8.1:dm/relay-log.md#enable-and-disable-relay-log`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `beea79f34767dde92bcaf6ca14a65f1168cb4ce56c7bc6709aa3a5ada1b66e71`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/relay-log#enable-and-disable-relay-log
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/relay-log.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks how to enable or disable DM relay log and the answer depends on DM version, source configuration `enable-relay`, or the `start-relay` and `stop-relay` commands.
- Retrieval Keywords: enable-relay, start-relay, stop-relay, v5.4.0 and later versions, versions between v2.0.2 (included) and v5.3.0 (included), earlier than v2.0.2, binding the upstream data source, source configuration file, Please use `start-relay` to specify which workers should pull relay log of relay-enabled sources., start-relay/stop-relay with worker name will be deprecated soon, start-relay -s mysql-replica-01, start-relay -s mysql-replica-01 worker1 worker2, stop-relay -s mysql-replica-01 worker1 worker2
- Follow-up Guidance: The source also provides the exact commands and notes about when `enable-relay` is valid or no longer valid for different DM versions.
- Classification Note: This is classified as operation because it gives version-specific procedures and commands for turning relay log on or off.

## Official Source Content

### Enable and disable relay log

<div label="v5.4.0 and later versions">

In v5.4.0 and later versions, you can enable relay log by setting `enable-relay` to `true`. Since v5.4.0, when binding the upstream data source, DM-worker checks the `enable-relay` item in the configuration of the data source. If `enable-relay` is `true`, the relay log feature is enabled for this data source.

For the detailed configuration method, see [Upstream Database Configuration File](https://docs.pingcap.com/tidb/stable/dm/dm-source-configuration-file).

In addition, you can also dynamically adjust the `enable-relay` configuration of the data source using the `start-relay` or `stop-relay` command to enable or disable relay log in time.

```bash
start-relay -s mysql-replica-01
```

```
{
    "result": true,
    "msg": ""
}
```

</div>

<div label="versions between v2.0.2 (included) and v5.3.0 (included)">

> **Note:**
>
> In DM v2.0.x later than DM v2.0.2 and in v5.3.0, the configuration item `enable-relay` in the source configuration file is no longer valid, and you can only use `start-relay` and `stop-relay` to enable and disable relay log. If DM finds that `enable-relay` is set to `true` when [loading the data source configuration](https://docs.pingcap.com/tidb/stable/dm/dm-manage-source#operate-data-source), it outputs the following message:
>
> ```
> Please use `start-relay` to specify which workers should pull relay log of relay-enabled sources.
> ```

> **Warning:**
>
> This startup method is marked as deprecated in v6.1 and might be removed in a future release. You can see the following prompt in the output of the relevant command: `start-relay/stop-relay with worker name will be deprecated soon. You can try stopping relay first and use start-relay without worker name instead`.

In the command `start-relay`, you can configure one or more DM-workers to migrate relay logs for the specified data source, but the DM-workers specified in the parameter must be free or have been bound to the upstream data source. Examples are as follows:

```bash
start-relay -s mysql-replica-01 worker1 worker2
```

```
{
    "result": true,
    "msg": ""
}
```

```bash
stop-relay -s mysql-replica-01 worker1 worker2
```

```
{
    "result": true,
    "msg": ""
}
```

</div>

<div label="earlier than v2.0.2">

In DM versions earlier than v2.0.2 (not including v2.0.2), DM checks the configuration item `enable-relay` in the source configuration file when binding a DM-worker to an upstream data source. If `enable-relay` is set to `true`, DM enables the relay log feature for the data source.

See [Upstream Database Configuration File](https://docs.pingcap.com/tidb/stable/dm/dm-source-configuration-file) for how to set the configuration item `enable-relay`.

</div>
