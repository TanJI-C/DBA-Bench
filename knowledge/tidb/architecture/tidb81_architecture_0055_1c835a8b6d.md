# Privilege system implementation and cache behavior

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/privilege-management.md`
- Source Title: `Privilege Management`
- Source Heading Path: `Privilege Management > Implementation of the privilege system | Privilege Management > Implementation of the privilege system > Privilege table | Privilege Management > Implementation of the privilege system > Connection verification | Privilege Management > Implementation of the privilege system > Request verification | Privilege Management > Implementation of the privilege system > Time of effect`
- Source Line Ranges: `415-476`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `privilege-tables`, `mysql-schema`, `connection-verification`, `request-verification`, `privilege-cache`, `flush-privileges`, `authentication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0055_1c835a8b6d`
- Source ID: `tidb-docs-8.1:privilege-management.md#implementation-of-the-privilege-system`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8d95334b3c0c1984f56bbadf2c45aeeacfe8754aeec44583930d9db6212246bd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/privilege-management#implementation-of-the-privilege-system
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/privilege-management.md

## Retrieval Guidance

- Use When: Use this chunk when you need to understand how TiDB stores privilege data, verifies connections and requests, and when privilege changes take effect in the privilege cache.
- Retrieval Keywords: mysql.user, mysql.db, mysql.tables_priv, mysql.columns_priv, privilege table, connection verification, request verification, authentication_string, Host User match, privilege cache, FLUSH PRIVILEGES, GRANT immediate effect, REVOKE immediate effect, CREATE USER immediate effect, DROP USER immediate effect, manual edit mysql.user, Time of effect
- Follow-up Guidance: The source notes that direct edits to privilege tables do not automatically update the privilege cache and that FLUSH PRIVILEGES updates the cached privilege data.
- Classification Note: This is classified as architecture content because it explains the implementation of the privilege system, including system tables, matching logic, verification flow, and cache behavior.

## Official Source Content

## Implementation of the privilege system
### Privilege table

The following [`mysql` system tables](https://docs.pingcap.com/tidb/stable/mysql-schema/mysql-schema) are special because all the privilege-related data is stored in them:

- `mysql.user` (user account, global privilege)
- `mysql.db` (database-level privilege)
- `mysql.tables_priv` (table-level privilege)
- `mysql.columns_priv` (column-level privilege; not currently supported)

These tables contain the effective range and privilege information of the data. For example, in the `mysql.user` table:

```sql
mysql> SELECT User,Host,Select_priv,Insert_priv FROM mysql.user LIMIT 1;
+------|------|-------------|-------------+
| User | Host | Select_priv | Insert_priv |
+------|------|-------------|-------------+
| root | %    | Y           | Y           |
+------|------|-------------|-------------+
1 row in set (0.00 sec)
```

In this record, `Host` and `User` determine that the connection request sent by the `root` user from any host (`%`) can be accepted. `Select_priv` and `Insert_priv` mean that the user has global `Select` and `Insert` privilege. The effective range in the `mysql.user` table is global.

`Host` and `User` in `mysql.db` determine which databases users can access. The effective range is the database.

> **Note:**
>
> It is recommended to only update the privilege tables via the supplied syntax such as `GRANT`, `CREATE USER` and `DROP USER`. Making direct edits to the underlying privilege tables will not automatically update the privilege cache, leading to unpredictable behavior until `FLUSH PRIVILEGES` is executed.
### Connection verification

When the client sends a connection request, TiDB server will verify the login operation. TiDB server first checks the `mysql.user` table. If a record of `User` and `Host` matches the connection request, TiDB server then verifies the `authentication_string`.

User identity is based on two pieces of information: `Host`, the host that initiates the connection, and `User`, the user name. If the user name is not empty, the exact match of user named is a must.

`User`+`Host` may match several rows in `user` table. To deal with this scenario, the rows in the `user` table are sorted. The table rows will be checked one by one when the client connects; the first matched row will be used to verify. When sorting, Host is ranked before User.
### Request verification

When the connection is successful, the request verification process checks whether the operation has the privilege.

For database-related requests (`INSERT`, `UPDATE`), the request verification process first checks the user's global privileges in the `mysql.user` table. If the privilege is granted, you can access directly. If not, check the `mysql.db` table.

The `user` table has global privileges regardless of the default database. For example, the `DELETE` privilege in `user` can apply to any row, table, or database.

In the `db` table, an empty user is to match the anonymous user name. Wildcards are not allowed in the `User` column. The value for the `Host` and `Db` columns can use `%` and `_`, which can use pattern matching.

Data in the `user` and `db` tables is also sorted when loaded into memory.

The use of `%` in `tables_priv` and `columns_priv` is similar, but column value in `Db`, `Table_name` and `Column_name` cannot contain `%`. The sorting is also similar when loaded.
### Time of effect

When TiDB starts, some privilege-check tables are loaded into memory, and then the cached data is used to verify the privileges. Executing privilege management statements such as `GRANT`, `REVOKE`, `CREATE USER`, `DROP USER` will take effect immediately.

Manually editing tables such as `mysql.user` with statements such as `INSERT`, `DELETE`, `UPDATE` will not take effect immediately. This behavior is compatible with MySQL, and privilege cache can be updated with the following statement:

```sql
FLUSH PRIVILEGES;
```
