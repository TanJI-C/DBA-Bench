# ADMIN SET SHOW UNSET BDR ROLE syntax and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-admin-bdr-role.md`
- Source Title: `ADMIN [SET|SHOW|UNSET] BDR ROLE`
- Source Heading Path: `ADMIN [SET|SHOW|UNSET] BDR ROLE | ADMIN [SET|SHOW|UNSET] BDR ROLE > Synopsis | ADMIN [SET|SHOW|UNSET] BDR ROLE > Examples | ADMIN [SET|SHOW|UNSET] BDR ROLE > MySQL compatibility`
- Source Line Ranges: `5-88`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `ticdc`
- Topic Tags: `bdr-role`, `sql-syntax`, `admin-statement`, `ddl-synchronization`, `bidirectional-replication`, `mysql-compatibility`, `experimental-feature`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0505_e2fc235bdf`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-admin-bdr-role.md#admin-set-show-unset-bdr-role`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dd84ef7b19a881be704314fa93115bef49ea3e9cdf1be2bcc3c4f8e7d4fa1937`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-bdr-role#admin-set-show-unset-bdr-role
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-admin-bdr-role.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, examples, or MySQL compatibility of `ADMIN SET BDR ROLE`, `ADMIN SHOW BDR ROLE`, or `ADMIN UNSET BDR ROLE` in relation to TiCDC bidirectional replication DDL synchronization.
- Retrieval Keywords: ADMIN SET BDR ROLE, ADMIN SHOW BDR ROLE, ADMIN UNSET BDR ROLE, BDR ROLE, PRIMARY, SECONDARY, DDL Synchronization in TiCDC Bidirectional Replication, TiCDC bidirectional replication, TiDB extension to MySQL syntax, experimental feature
- Follow-up Guidance: The examples show that a cluster has no BDR role by default, `ADMIN SHOW BDR ROLE;` displays the current value, `ADMIN SET BDR ROLE PRIMARY;` sets it, and `ADMIN UNSET BDR ROLE;` clears it.
- Classification Note: This is reference content because it defines the statement synopsis, shows exact SQL examples and outputs, and notes that the statement is a TiDB extension to MySQL syntax.

## Official Source Content

# ADMIN [SET|SHOW|UNSET] BDR ROLE

- Use `ADMIN SET BDR ROLE` to set the BDR role of the cluster. Currently, you can set the following BDR roles for a TiDB cluster: `PRIMARY` and `SECONDARY`. For more information about BDR roles, see [DDL Synchronization in TiCDC Bidirectional Replication](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-bidirectional-replication#ddl-replication).
- Use `ADMIN SHOW BDR ROLE` to show the BDR role of the cluster.
- Use `ADMIN UNSET BDR ROLE` to unset the BDR role of the cluster.

> **Warning:**
>
> This feature is experimental. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.
## Synopsis

```ebnf+diagram
AdminShowBDRRoleStmt ::=
    'ADMIN' 'SHOW' 'BDR' 'ROLE'

AdminSetBDRRoleStmt ::=
    'ADMIN' 'SET' 'BDR' 'ROLE' ('PRIMARY' | 'SECONDARY')

AdminUnsetBDRRoleStmt ::=
    'ADMIN' 'UNSET' 'BDR' 'ROLE'
```
## Examples

By default, a TiDB cluster has no BDR role. Run the following command to show the BDR role of the cluster.

```sql
ADMIN SHOW BDR ROLE;
```

```sql
+------------+
| BDR_ROLE   |
+------------+
|            |
+------------+
1 row in set (0.01 sec)
```

Run the following command to set the BDR role to `PRIMARY`.

```sql
ADMIN SET BDR ROLE PRIMARY;
```

```sql
Query OK, 0 rows affected (0.01 sec)
```

```sql
ADMIN SHOW BDR ROLE;
+----------+
| BDR_ROLE |
+----------+
| primary  |
+----------+
1 row in set (0.00 sec)
```

Run the following command to unset the BDR role of the cluster.

```sql
ADMIN UNSET BDR ROLE;
```

```sql
Query OK, 0 rows affected (0.01 sec)
```

```sql
ADMIN SHOW BDR ROLE;
+----------+
| BDR_ROLE |
+----------+
|          |
+----------+
1 row in set (0.01 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
