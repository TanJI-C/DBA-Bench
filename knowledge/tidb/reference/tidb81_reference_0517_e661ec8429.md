# ADMIN repair next row id and slow query statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-admin.md`
- Source Title: `ADMIN | TiDB SQL Statement Reference`
- Source Heading Path: `ADMIN > `ADMIN REPAIR` statement | ADMIN > `ADMIN SHOW NEXT_ROW_ID` statement | ADMIN > `ADMIN SHOW SLOW` statement`
- Source Line Ranges: `101-150`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `cloud`
- Topic Tags: `admin`, `repair`, `metadata`, `next-row-id`, `slow-queries`, `statement-reference`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0517_e661ec8429`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-admin.md#admin-repair-statement`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2a9bb5aed2b20403a9217e21d30d57ed8dfaaee57f47910e32e29a4ea4a9214e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin#admin-repair-statement
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-admin.md

## Retrieval Guidance

- Use When: Use this chunk when looking for ADMIN statements for table metadata repair, viewing NEXT_ROW_ID details, or showing slow queries.
- Retrieval Keywords: ADMIN REPAIR TABLE, repair-mode, repair-table-list, CREATE TABLE STATEMENT, untrusted, ADMIN SHOW NEXT_ROW_ID, SHOW TABLE NEXT_ROW_ID, ADMIN SHOW SLOW RECENT N, ADMIN SHOW SLOW TOP, INTERNAL | ALL, slow queries
- Follow-up Guidance: The source states that ADMIN REPAIR is not applicable to TiDB Cloud, requires repair-mode and repair-table-list, that ADMIN SHOW NEXT_ROW_ID has the same output as SHOW TABLE NEXT_ROW_ID, and that ADMIN SHOW SLOW details are documented in the ADMIN SHOW SLOW command page.
- Classification Note: This is reference content because it defines the syntax, scope notes, and stated usage of ADMIN REPAIR, ADMIN SHOW NEXT_ROW_ID, and ADMIN SHOW SLOW.

## Official Source Content

## `ADMIN REPAIR` statement

> **Note:**
>
> This TiDB statement is not applicable to TiDB Cloud.

To overwrite the metadata of the stored table in an untrusted way in extreme cases, use `ADMIN REPAIR TABLE`:

```sql
ADMIN REPAIR TABLE tbl_name CREATE TABLE STATEMENT;
```

Here "untrusted" means that you need to manually ensure that the metadata of the original table can be covered by the `CREATE TABLE STATEMENT` operation. To use this `REPAIR` statement, enable the [`repair-mode`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#repair-mode) configuration item, and make sure that the tables to be repaired are listed in the [`repair-table-list`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#repair-table-list).
## `ADMIN SHOW NEXT_ROW_ID` statement

```sql
ADMIN SHOW t NEXT_ROW_ID;
```

The above statement is used to view the details of some special columns of a table. The output is the same as [SHOW TABLE NEXT_ROW_ID](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-table-next-rowid).
## `ADMIN SHOW SLOW` statement

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

```sql
ADMIN SHOW SLOW RECENT N;
```

```sql
ADMIN SHOW SLOW TOP [INTERNAL | ALL] N;
```

For details, refer to [`ADMIN SHOW SLOW` command](https://docs.pingcap.com/tidb/stable/identify-slow-queries#admin-show-slow-command).
