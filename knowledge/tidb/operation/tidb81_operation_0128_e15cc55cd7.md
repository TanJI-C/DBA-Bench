# Query, pause, and resume relay log

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/relay-log.md`
- Source Title: `Data Migration Relay Log`
- Source Heading Path: `Data Migration Relay Log > Use relay log > Query relay log status | Data Migration Relay Log > Use relay log > Pause and resume relay log`
- Source Line Ranges: `112-235`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `relay-log`, `query-status`, `pause-relay`, `resume-relay`, `status`, `worker`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0128_e15cc55cd7`
- Source ID: `tidb-docs-8.1:dm/relay-log.md#query-relay-log-status`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6d14fa885a29f7e8d96842a3898034e2c9855998546e819d67f7f466437b86f9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/relay-log#query-relay-log-status
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/relay-log.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks how to check relay log status or how to pause and resume relay log pulling for one or more upstream sources.
- Retrieval Keywords: query-status -s, pause-relay, resume-relay, relayStatus, masterBinlog, masterBinlogGtid, relaySubDir, relayBinlog, relayBinlogGtid, relayCatchUpMaster, stage, source-id, mysql-replica-01, mysql-replica-02
- Follow-up Guidance: The examples show expected output fields such as `relayStatus`, `worker`, `stage`, and `relayCatchUpMaster` for `query-status -s`, plus result objects for `pause-relay` and `resume-relay`.
- Classification Note: This is classified as operation because it documents CLI commands and expected status output for managing relay log pulling.

## Official Source Content

### Query relay log status

You can use the command `query-status -s` to query the status of the relay log:

```bash
query-status -s mysql-replica-01
```

<details>
<summary>Expected output</summary>

```
{
    "result": true,
    "msg": "",
    "sources": [
        {
            "result": true,
            "msg": "no sub task started",
            "sourceStatus": {
                "source": "mysql-replica-01",
                "worker": "worker2",
                "result": null,
                "relayStatus": {
                    "masterBinlog": "(mysql-bin.000005, 916)",
                    "masterBinlogGtid": "09bec856-ba95-11ea-850a-58f2b4af5188:1-28",
                    "relaySubDir": "09bec856-ba95-11ea-850a-58f2b4af5188.000001",
                    "relayBinlog": "(mysql-bin.000005, 4)",
                    "relayBinlogGtid": "09bec856-ba95-11ea-850a-58f2b4af5188:1-28",
                    "relayCatchUpMaster": false,
                    "stage": "Running",
                    "result": null
                }
            },
            "subTaskStatus": [
            ]
        },
        {
            "result": true,
            "msg": "no sub task started",
            "sourceStatus": {
                "source": "mysql-replica-01",
                "worker": "worker1",
                "result": null,
                "relayStatus": {
                    "masterBinlog": "(mysql-bin.000005, 916)",
                    "masterBinlogGtid": "09bec856-ba95-11ea-850a-58f2b4af5188:1-28",
                    "relaySubDir": "09bec856-ba95-11ea-850a-58f2b4af5188.000001",
                    "relayBinlog": "(mysql-bin.000005, 916)",
                    "relayBinlogGtid": "",
                    "relayCatchUpMaster": true,
                    "stage": "Running",
                    "result": null
                }
            },
            "subTaskStatus": [
            ]
        }
    ]
}
```

</details>
### Pause and resume relay log

You can use the command `pause-relay` to pause the pulling process of relay logs and use the command `resume-relay` to resume the process. You need to specify the `source-id` of the upstream data source when executing these two commands. See the following examples:

```bash
pause-relay -s mysql-replica-01 -s mysql-replica-02
```

<details>
<summary>Expected output</summary>

```
{
    "op": "PauseRelay",
    "result": true,
    "msg": "",
    "sources": [
        {
            "result": true,
            "msg": "",
            "source": "mysql-replica-01",
            "worker": "worker1"
        },
        {
            "result": true,
            "msg": "",
            "source": "mysql-replica-02",
            "worker": "worker2"
        }
    ]
}
```

</details>

```bash
resume-relay -s mysql-replica-01
```

<details>
<summary>Expected output</summary>

```
{
    "op": "ResumeRelay",
    "result": true,
    "msg": "",
    "sources": [
        {
            "result": true,
            "msg": "",
            "source": "mysql-replica-01",
            "worker": "worker1"
        }
    ]
}
```

</details>
