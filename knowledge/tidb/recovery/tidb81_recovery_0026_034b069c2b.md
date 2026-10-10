# Restoring mysql schema tables and rewrite rule conflicts

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/backup-and-restore-faq.md`
- Source Title: `Backup & Restore FAQs`
- Source Heading Path: `Backup & Restore FAQs > Data restore issues > Why are tables in the `mysql` schema not restored? | Backup & Restore FAQs > Data restore issues > How to deal with the error of `cannot find rewrite rule` during restoration? | Backup & Restore FAQs > Other things you may want to know about backup and restore`
- Source Line Ranges: `248-285`
- Source Scope: `all`
- Primary Component: `br`
- Related Components: `tidb`
- Topic Tags: `restore`, `mysql-schema`, `system-tables`, `table-filters`, `with-sys-table`, `rewrite-rules`, `schema-conflicts`, `indexes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0026_034b069c2b`
- Source ID: `tidb-docs-8.1:faq/backup-and-restore-faq.md#why-are-tables-in-the-mysql-schema-not-restored`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5b3e3e42463ae1d631d0462c47a76d808c948146627cc6513213eb660a328592`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/backup-and-restore-faq#why-are-tables-in-the-mysql-schema-not-restored
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/backup-and-restore-faq.md

## Retrieval Guidance

- Use When: You need guidance on restoring `mysql` schema tables or diagnosing `cannot find rewrite rule` during restoration.
- Retrieval Keywords: mysql schema, mysql.usertable, --with-sys-table, table filters, -f '*.*', -f '!mysql.*', -f 'mysql.usertable', mysql.stat_*, mysql.tidb, mysql.global_variables, cannot find rewrite rule, missing indexes
- Follow-up Guidance: The examples show how to restore `mysql.usertable`, and the rewrite-rule issue is associated with inconsistent table structures or missing indexes in the restoration cluster.
- Classification Note: This chunk is a recovery FAQ about `mysql` schema restore behavior and rewrite rule conflicts.

## Official Source Content

### Why are tables in the `mysql` schema not restored?

Starting from BR v5.1.0, when you perform a full backup, BR backs up the **tables in the `mysql` schema**. Before BR v6.2.0, under default configuration, BR only restores user data, but does not restore tables in the **`mysql` schema**.

To restore a table created by the user in the `mysql` schema (not system tables), you can explicitly include the table using [table filters](https://docs.pingcap.com/tidb/stable/table-filter#syntax). The following example shows how to restore the `mysql.usertable` table when BR performs a normal restore.

```shell
br restore full -f '*.*' -f '!mysql.*' -f 'mysql.usertable' -s $external_storage_url --with-sys-table
```

In the preceding command,

- `-f '*.*'` is used to override the default rules
- `-f '!mysql.*'` instructs BR not to restore tables in `mysql` unless otherwise stated.
- `-f 'mysql.usertable'` indicates that `mysql.usertable` should be restored.

If you only need to restore `mysql.usertable`, run the following command:

```shell
br restore full -f 'mysql.usertable' -s $external_storage_url --with-sys-table
```

Note that even if you configures [table filter](https://docs.pingcap.com/tidb/stable/table-filter#syntax), **BR does not restore the following system tables**:

- Statistics tables (`mysql.stat_*`). But statistics can be restored. See [Back up statistics](https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual#back-up-statistics).
- System variable tables (`mysql.tidb`, `mysql.global_variables`)
- [Other system tables](https://github.com/pingcap/tidb/blob/release-8.1/br/pkg/restore/systable_restore.go#L31)
### How to deal with the error of `cannot find rewrite rule` during restoration?

Examine whether there are tables in the restoration cluster sharing the same name as other tables in the backup data but having inconsistent structures. In most cases, this issue is caused by missing indexes in the tables of the restoration cluster. A recommended approach is to delete such tables in the restoration cluster first and then retry restoration.
## Other things you may want to know about backup and restore
