# Recover a sharding DDL lock when DM-workers restart or networking fails

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/manually-handling-sharding-ddl-locks.md`
- Source Title: `Handle Sharding DDL Locks Manually in DM`
- Source Heading Path: `Handle Sharding DDL Locks Manually in DM > Supported scenarios > Scenario 2: Some DM-workers stop abnormally or the network failure occurs during the DDL unlocking process | Handle Sharding DDL Locks Manually in DM > Supported scenarios > Scenario 2: Some DM-workers stop abnormally or the network failure occurs during the DDL unlocking process > The reason for the abnormal lock | Handle Sharding DDL Locks Manually in DM > Supported scenarios > Scenario 2: Some DM-workers stop abnormally or the network failure occurs during the DDL unlocking process > Manual solution | Handle Sharding DDL Locks Manually in DM > Supported scenarios > Scenario 2: Some DM-workers stop abnormally or the network failure occurs during the DDL unlocking process > Impact`
- Source Line Ranges: `292-363`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `sharding-ddl-lock`, `dm-worker-failure`, `network-failure`, `checkpoint-update`, `manual-unlock`, `query-status`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0020_35ef2e991d`
- Source ID: `tidb-docs-8.1:dm/manually-handling-sharding-ddl-locks.md#scenario-2-some-dm-workers-stop-abnormally-or-the-network-failure-occurs-during-the-ddl-unlocking-process`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5a5b2eae5197434993f08a8b1c59ce98d6f7a49a952a3030b5e14f6389e99e1f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/manually-handling-sharding-ddl-locks#scenario-2-some-dm-workers-stop-abnormally-or-the-network-failure-occurs-during-the-ddl-unlocking-process
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/manually-handling-sharding-ddl-locks.md

## Retrieval Guidance

- Use When: Use this content when a sharding DDL lock reappears or cannot be automatically unlocked after a DM-worker restart or network anomaly causes a non-owner checkpoint update failure during DDL unlocking.
- Retrieval Keywords: DM-workers stop abnormally, network failure occurs during the DDL unlocking process, checkpoint fails to update, non-owner skips the DDL, shard-ddl-lock unlock, query-status, test-`shard_db`.`shard_table`, mysql-replica-02, owner tries to execute the DDL operation to the downstream again, Only `mysql-replica-02` is at the `synced` state
- Follow-up Guidance: The content says to confirm the lock with `shard-ddl-lock`, unlock it, verify the lock is gone, and then use `query-status` to confirm the migration task is normal.
- Classification Note: This is classified as recovery because it explains why a non-atomic unlocking process can leave an abnormal sharding DDL lock after DM-worker or network failures and provides a manual unlock path.

## Official Source Content

### Scenario 2: Some DM-workers stop abnormally or the network failure occurs during the DDL unlocking process
#### The reason for the abnormal lock

After `DM-master` receives the DDL events of all DM-workers, automatically running `unlock DDL lock` mainly include the following steps:

1. Ask the owner of the lock to execute the DDL and update the checkpoints of corresponding sharded tables.
2. Remove the DDL lock information stored on `DM-master` after the owner successfully executes the DDL.
3. Ask all other non-owners to skip the DDL and update the checkpoints of corresponding sharded tables after the owner successfully executes the DDL.
4. DM-master removes the corresponding DDL lock information after all the owners or non-owners' operations are successful.

Currently, the above unlocking process is not atomic. If the non-owner skips the DDL operation successfully, the DM-worker where the non-owner is located stops abnormally or a network anomaly occurs with the downstream TiDB, which can cause the checkpoint updating to fail.

When the MySQL source corresponding to the non-owner restores data migration, the non-owner tries to request the DM-master to re-coordinate the DDL operation that has been coordinated before the exception occurs and will never receives the corresponding DDL operation from other MySQL sources. This can cause the DDL operation to automatically unlock the corresponding lock.
#### Manual solution

Suppose that now we have the same upstream and downstream table structures and the same demand for merging tables and migration as in the manual solution of [Some MySQL sources are removed](#scenario-1-some-mysql-sources-are-removed).

When `DM-master` automatically executes the unlocking process, the owner (`mysql-replica-01`) successfully executes the DDL and continues the migration process. However, in the process of requesting the non-owner (`mysql-replica-02`) to skip the DDL operation, the checkpoint fails to update after the DM-worker skips the DDL operation because the corresponding DM-worker was restarted.

After the data migration subtask corresponding to `mysql-replica-02` restores, a new lock is created on the DM-master, but other MySQL sources have executed or skipped DDL operations and are performing subsequent migration.

The operation processes are:

1. Use `shard-ddl-lock` to confirm if the corresponding lock of the DDL exists on `DM-master`.

    Only `mysql-replica-02` is at the `synced` state.

    ```bash
    » shard-ddl-lock
    {
        "result": true,
        "msg": "",
        "locks": [
            {
                "ID": "test-`shard_db`.`shard_table`",
                "task": "test",
                "mode": "pessimistic"
                "owner": "mysql-replica-02",
                "DDLs": [
                    "USE `shard_db`; ALTER TABLE `shard_db`.`shard_table` ADD COLUMN `c2` int(11);"
                ],
                "synced": [
                    "mysql-replica-02"
                ],
                "unsynced": [
                    "mysql-replica-01"
                ]
            }
        ]
    }
    ```

2. Use `shard-ddl-lock` to ask `DM-master` to unlock the lock.

    - During the unlocking process, the owner tries to execute the DDL operation to the downstream again (the original owner before restarting has executed the DDL operation to the downstream once). Make sure that the DDL operation can be executed multiple times.

        ```bash
        shard-ddl-lock unlock test-`shard_db`.`shard_table`
        {
            "result": true,
            "msg": "",
        }
        ```

3. Use `shard-ddl-lock` to confirm if the DDL lock has been successfully unlocked.
4. Use `query-status` to confirm if the migration task is normal.
#### Impact

After manually unlocking the lock, the following sharding DDL can be migrated automatically and normally.
