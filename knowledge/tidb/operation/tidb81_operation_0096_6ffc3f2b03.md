# Transfer DM source bindings between workers

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-manage-source.md`
- Source Title: `Manage Data Source Configurations in TiDB Data Migration`
- Source Heading Path: `Manage Data Source Configurations in TiDB Data Migration > Change the bindings between upstream MySQL instances and DM-workers | Manage Data Source Configurations in TiDB Data Migration > Change the bindings between upstream MySQL instances and DM-workers > Usage example`
- Source Line Ranges: `153-262`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `transfer-source`, `worker-binding`, `list-member`, `pause-task`, `resume-task`, `source-transfer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0096_6ffc3f2b03`
- Source ID: `tidb-docs-8.1:dm/dm-manage-source.md#change-the-bindings-between-upstream-mysql-instances-and-dm-workers`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ae4b91670f4bf290934a5c611d196b6d48dcff27d1eeefe4041e5731067a7ea8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-manage-source#change-the-bindings-between-upstream-mysql-instances-and-dm-workers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-manage-source.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how to change the binding between an upstream MySQL or MariaDB source and a DM-worker with transfer-source.
- Retrieval Keywords: transfer-source, Change the bindings between upstream MySQL instances and DM-workers, list-member --worker, pause-task, resume-task, dmctl transfer-source <source-id> <worker-id>, mysql-replica-01, dm-worker-2, stage bound, stage free
- Follow-up Guidance: Before transferring, the source says DM checks whether the worker to be unbound still has running tasks, and if so you need to pause the tasks first, change the binding, and then resume the tasks.
- Classification Note: This is classified as operation because it explains the dmctl procedure and checks for transferring source bindings between DM-workers.

## Official Source Content

## Change the bindings between upstream MySQL instances and DM-workers

You can use the `transfer-source` command to change the bindings between upstream MySQL instances and DM-workers.

```bash
help transfer-source
```

```
Transfers an upstream MySQL/MariaDB source to a free worker.
Usage:
  dmctl transfer-source <source-id> <worker-id> [flags]
Flags:
  -h, --help   help for transfer-source
Global Flags:
  -s, --source strings   MySQL Source ID.
```

Before transferring, DM checks whether the worker to be unbound still has running tasks. If the worker has any running tasks, you need to [pause the tasks](https://docs.pingcap.com/tidb/stable/dm/dm-pause-task) first, change the binding, and then [resume the tasks](https://docs.pingcap.com/tidb/stable/dm/dm-resume-task).
### Usage example

If you do not know the bindings of DM-workers, you can run `dmctl --master-addr <master-addr> list-member --worker` to list the current bindings of all workers.

```bash
list-member --worker
```

```
{
    "result": true,
    "msg": "",
    "members": [
        {
            "worker": {
                "msg": "",
                "workers": [
                    {
                        "name": "dm-worker-1",
                        "addr": "127.0.0.1:8262",
                        "stage": "bound",
                        "source": "mysql-replica-01"
                    },
                    {
                        "name": "dm-worker-2",
                        "addr": "127.0.0.1:8263",
                        "stage": "free",
                        "source": ""
                    }
                ]
            }
        }
    ]
}
```

In the above example, `mysql-replica-01` is bound to `dm-worker-1`. The below command transfers the binding worker of `mysql-replica-01` to `dm-worker-2`.

```bash
transfer-source mysql-replica-01 dm-worker-2
```

```
{
    "result": true,
    "msg": ""
}
```

Check whether the command takes effect by running `dmctl --master-addr <master-addr> list-member --worker`.

```bash
list-member --worker
```

```
{
    "result": true,
    "msg": "",
    "members": [
        {
            "worker": {
                "msg": "",
                "workers": [
                    {
                        "name": "dm-worker-1",
                        "addr": "127.0.0.1:8262",
                        "stage": "free",
                        "source": ""
                    },
                    {
                        "name": "dm-worker-2",
                        "addr": "127.0.0.1:8263",
                        "stage": "bound",
                        "source": "mysql-replica-01"
                    }
                ]
            }
        }
    ]
}
```
