# DM shard-ddl-lock command, unlock usage, and abnormal lock scenario

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/manually-handling-sharding-ddl-locks.md`
- Source Title: `Handle Sharding DDL Locks Manually in DM`
- Source Heading Path: `Handle Sharding DDL Locks Manually in DM | Handle Sharding DDL Locks Manually in DM > Command | Handle Sharding DDL Locks Manually in DM > Command > `shard-ddl-lock` | Handle Sharding DDL Locks Manually in DM > Command > `shard-ddl-lock` > Arguments description | Handle Sharding DDL Locks Manually in DM > Usage examples | Handle Sharding DDL Locks Manually in DM > Usage examples > `shard-ddl-lock [task] [flags]` | Handle Sharding DDL Locks Manually in DM > Usage examples > `shard-ddl-lock unlock` | Handle Sharding DDL Locks Manually in DM > Supported scenarios | Handle Sharding DDL Locks Manually in DM > Supported scenarios > Scenario 1: Some MySQL sources are removed | Handle Sharding DDL Locks Manually in DM > Supported scenarios > Scenario 1: Some MySQL sources are removed > The reason for the abnormal lock`
- Source Line Ranges: `5-162`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `sharding ddl lock`, `pessimistic mode`, `dmctl`, `unlock`, `owner`, `force remove`, `mysql sources`, `task management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0121_ca7f4cf786`
- Source ID: `tidb-docs-8.1:dm/manually-handling-sharding-ddl-locks.md#handle-sharding-ddl-locks-manually-in-dm`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `92a0dc7b83be1e3b6e49fad39ba7947b55dd1caa183c86a58f027575b3249597`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/manually-handling-sharding-ddl-locks#handle-sharding-ddl-locks-manually-in-dm
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/manually-handling-sharding-ddl-locks.md

## Retrieval Guidance

- Use When: Use this content when looking up how to inspect a DM sharding DDL lock or manually unlock an abnormal lock in pessimistic mode, especially when some MySQL sources were removed and the lock cannot be automatically resolved.
- Retrieval Keywords: shard-ddl-lock, dmctl shard-ddl-lock [task] [flags], shard-ddl-lock unlock, pessimistic mode, DDL lock, lock ID, owner, synced, unsynced, MySQL Source ID, --owner, --force-remove, unlock un-resolved DDL locks forcely, Some MySQL sources are removed, DM-master, DM-workers, stop-task, start-task, show-ddl-locks, unlock-ddl-locks
- Follow-up Guidance: The source notes that if DM-workers need to go offline when not in the process of migrating sharding DDL events, a better solution is to use stop-task, remove the corresponding configuration information from the task configuration file, and then use start-task with the new task configuration.
- Classification Note: This is classified as an operation topic because the content describes dmctl shard-ddl-lock viewing and unlock command usage, arguments, output fields, cautions, and the abnormal scenario of removed MySQL sources.

## Official Source Content

# Handle Sharding DDL Locks Manually in DM

DM uses the sharding DDL lock to ensure operations are performed in the correct order. This locking mechanism resolves sharding DDL locks automatically in most cases, but you need to use the `shard-ddl-lock` command to manually handle the abnormal DDL locks in some abnormal scenarios.

> **Note:**
>
> - This document only applies to the processing of sharding DDL lock in pessimistic coordination mode.
> - The commands in the Command usage sections in this document are in interactive mode. In command-line mode, you need to add the escape characters to avoid an error report.
> - Do not use `shard-ddl-lock unlock` unless you are totally aware of the possible impacts brought by the command and you can accept them.
> - Before manually handling the abnormal DDL locks, make sure that you have already read the DM [shard merge principles](https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-pessimistic#principles).
## Command
### `shard-ddl-lock`

You can use this command to view the DDL lock and request DM-master to release the specified DDL lock. This command is only supported in DM v6.0 and later. For earlier versions, you must use the `show-ddl-locks` and `unlock-ddl-locks` commands.

```bash
shard-ddl-lock -h
```

```
maintain or show shard-ddl locks information
Usage:
  dmctl shard-ddl-lock [task] [flags]
  dmctl shard-ddl-lock [command]
Available Commands:
  unlock      Unlock un-resolved DDL locks forcely
Flags:
  -h, --help   help for shard-ddl-lock
Global Flags:
  -s, --source strings   MySQL Source ID.
Use "dmctl shard-ddl-lock [command] --help" for more information about a command.
```
#### Arguments description

* `shard-ddl-lock [task] [flags]`: view the DDL lock information on the current DM-master.

+ `shard-ddl-lock [command]`: request DM-master to release the specified DDL lock. `[command]` only accepts `unlock` as a value.
## Usage examples
### `shard-ddl-lock [task] [flags]`

You can use `shard-ddl-lock [task] [flags]` to view the DDL lock information on the current DM-master. For example:

```bash
shard-ddl-lock test
```

<details open>
<summary>Expected output</summary>

```
{
    "result": true,                                        # The result of the query for the lock information.
    "msg": "",                                             # The additional message for the failure to query the lock information or other descriptive information (for example, the lock task does not exist).
    "locks": [                                             # The existing lock information list.
        {
            "ID": "test-`shard_db`.`shard_table`",         # The lock ID, which is made up of the current task name and the schema/table information corresponding to the DDL.
            "task": "test",                                # The name of the task to which the lock belongs.
            "mode": "pessimistic"                          # The shard DDL mode. Can be set to "pessimistic" or "optimistic".
            "owner": "mysql-replica-01",                   # The owner of the lock (the ID of the first source that encounters this DDL operation in the pessimistic mode), which is always empty in the optimistic mode.
            "DDLs": [                                      # The list of DDL operations corresponding to the lock in the pessimistic mode, which is always empty in the optimistic mode.
                "USE `shard_db`; ALTER TABLE `shard_db`.`shard_table` DROP COLUMN `c2`;"
            ],
            "synced": [                                    # The list of sources that have received all sharding DDL events in the corresponding MySQL instance.
                "mysql-replica-01"
            ],
            "unsynced": [                                  # The list of sources that have not yet received all sharding DDL events in the corresponding MySQL instance.
                "mysql-replica-02"
            ]
        }
    ]
}
```

</details>
### `shard-ddl-lock unlock`

This command actively requests `DM-master` to unlock the specified DDL lock, including requesting the owner to execute the DDL statement, requesting all other DM-workers that are not the owner to skip the DDL statement, and removing the lock information on `DM-master`.

> **Note:**
>
> Currently, `shard-ddl-lock unlock` takes effect only for the lock in the `pessimistic` mode.

```bash
shard-ddl-lock unlock -h
```

```
Unlock un-resolved DDL locks forcely

Usage:
  dmctl shard-ddl-lock unlock <lock-id> [flags]

Flags:
  -a, --action string     accept skip/exec values which means whether to skip or execute ddls (default "skip")
  -d, --database string   database name of the table
  -f, --force-remove      force to remove DDL lock
  -h, --help              help for unlock
  -o, --owner string      source to replace the default owner
  -t, --table string      table name

Global Flags:
  -s, --source strings   MySQL Source ID.
```

`shard-ddl-lock unlock` accepts the following arguments:

+ `-o, --owner`:

    - Flag; string; optional
    - If it is not specified, this command requests for the default owner (the owner in the result of `shard-ddl-lock`) to execute the DDL statement; if it is specified, this command requests for the MySQL source (the alternative of the default owner) to execute the DDL statement.
    - The new owner should not be specified unless the original owner is already removed from the cluster.

+ `-f, --force-remove`:

    - Flag; boolean; optional
    - If it is not specified, this command removes the lock information only when the owner succeeds to execute the DDL statement; if it is specified, this command forcefully removes the lock information even though the owner fails to execute the DDL statement (after doing this you cannot query or operate on the lock again).

+ `lock-id`:

    - Non-flag; string; required
    - It specifies the ID of the DDL lock that needs to be unlocked (the `ID` in the result of `shard-ddl-lock`).

The following is an example of the `shard-ddl-lock unlock` command:

```bash
shard-ddl-lock unlock test-`shard_db`.`shard_table`
```

```
{
    "result": true,                                        # The result of the unlocking operation.
    "msg": "",                                             # The additional message for the failure to unlock the lock.
}
```
## Supported scenarios

Currently, the `shard-ddl-lock unlock` command only supports handling sharding DDL locks in the following two abnormal scenarios.
### Scenario 1: Some MySQL sources are removed
#### The reason for the abnormal lock

Before `DM-master` tries to automatically unlock the sharding DDL lock, all the MySQL sources need to receive the sharding DDL events (for details, see [shard merge principles](https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-pessimistic#principles)). If the sharding DDL event is already in the migration process, and some MySQL sources have been removed and are not to be reloaded (these MySQL sources have been removed according to the application demand), then the sharding DDL lock cannot be automatically migrated and unlocked because not all the DM-workers can receive the DDL event.

> **Note:**
>
> If you need to make some DM-workers offline when not in the process of migrating sharding DDL events, a better solution is to use `stop-task` to stop the running tasks first, make the DM-workers go offline, remove the corresponding configuration information from the task configuration file, and finally use `start-task` and the new task configuration to restart the migration task.
