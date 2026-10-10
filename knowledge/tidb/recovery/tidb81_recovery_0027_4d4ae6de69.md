# BR recovery resumption, table re-recovery, and statistics memory FAQ

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/backup-and-restore-faq.md`
- Source Title: `Backup & Restore FAQs`
- Source Heading Path: `Backup & Restore FAQs > If the recovery process is interrupted, is it necessary to delete the already recovered data and start the recovery again? | Backup & Restore FAQs > After the recovery is complete, can I delete a specific table and then recover it again? | Backup & Restore FAQs > After the recovery is complete, can I delete a specific table and then recover it again? > Why does BR take a lot of memory when restoring statistics information?`
- Source Line Ranges: `316-328`
- Source Scope: `shared`
- Primary Component: `br`
- Related Components: `tidb`
- Topic Tags: `breakpoint-resume`, `interrupted-recovery`, `table-recovery`, `drop-table`, `truncate-table`, `mvcc`, `gc`, `statistics-restore`, `memory-usage`, `version-behavior`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0027_4d4ae6de69`
- Source ID: `tidb-docs-8.1:faq/backup-and-restore-faq.md#if-the-recovery-process-is-interrupted-is-it-necessary-to-delete-the-already-recovered-data-and-start-the-recovery-again`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d4d2a6c8609da85239a0e1fb26500417be3da802f8ae2d1386a18ede39ad8008`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/backup-and-restore-faq#if-the-recovery-process-is-interrupted-is-it-necessary-to-delete-the-already-recovered-data-and-start-the-recovery-again
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/backup-and-restore-faq.md

## Retrieval Guidance

- Use When: Use this chunk when answering whether BR recovery can resume after interruption, whether a deleted table can be recovered again, or why restoring statistics can consume a lot of memory.
- Retrieval Keywords: recovery process is interrupted, resuming data from a breakpoint, starting from v7.1.0, restart the recovery task, recover it again, DROP TABLE, TRUNCATE TABLE, DELETE FROM, MVCC version, GC, BR take a lot of memory when restoring statistics information, Before v7.6.0, statistics data backed up by BR is stored together with the table information, loaded into memory during recovery, Starting from v7.6.0, backup statistics is stored in a specific file separately
- Follow-up Guidance: For interrupted recovery, the content says to restart the recovery task so BR resumes from where it left off.
- Classification Note: This is recovery content because it focuses on interrupted recovery resumption, re-recovery conditions for deleted tables, and memory behavior during statistics restoration.

## Official Source Content

## If the recovery process is interrupted, is it necessary to delete the already recovered data and start the recovery again?

No, it is not necessary. Starting from v7.1.0, BR supports resuming data from a breakpoint. If the recovery is interrupted due to unexpected circumstances, simply restart the recovery task, and it will resume from where it left off.
## After the recovery is complete, can I delete a specific table and then recover it again?

Yes, after deleting a specific table, you can recover it again. But note that, you can only recover tables that are deleted using the `DROP TABLE` or `TRUNCATE TABLE` statement, not the `DELETE FROM` statement. This is because `DELETE FROM` only updates the MVCC version to mark the data to be deleted, and the actual data deletion occurs after GC.
### Why does BR take a lot of memory when restoring statistics information?

Before v7.6.0, the statistics data backed up by BR is stored together with the table information and loaded into memory during recovery. Therefore, when the backup statistics data is very large, BR needs to occupy a large amount of memory.

Starting from v7.6.0, the backup statistics is stored in a specific file separately. BR does not load statistic data of any table until BR starts to restore the table, which saves memory.
