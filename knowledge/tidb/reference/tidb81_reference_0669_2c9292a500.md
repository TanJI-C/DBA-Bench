# SHOW PRIVILEGES syntax, example output, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-privileges.md`
- Source Title: `SHOW PRIVILEGES | TiDB SQL Statement Reference`
- Source Heading Path: `SHOW PRIVILEGES | SHOW PRIVILEGES > Synopsis | SHOW PRIVILEGES > Examples | SHOW PRIVILEGES > MySQL compatibility | SHOW PRIVILEGES > See also`
- Source Line Ranges: `5-100`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `show privileges`, `privileges`, `syntax`, `examples`, `mysql compatibility`, `grant`, `access control`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0669_2c9292a500`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-privileges.md#show-privileges`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b88938fd2a763a9def64ed1fd3fbeec3369c7472ed2a212b0ead622782512e17`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-privileges#show-privileges
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-privileges.md

## Retrieval Guidance

- Use When: Use this chunk when someone asks for the syntax, example output, or MySQL compatibility of the SHOW PRIVILEGES statement in TiDB.
- Retrieval Keywords: SHOW PRIVILEGES, ShowPrivilegesStmt, SHOW PRIVILEGES syntax, assignable privileges, static list, does not reflect the privileges of the current user, Privilege Context Comment, SHOW PRIVILEGES example output, MySQL compatibility, SHOW GRANTS, Privilege Management, GRANT <privileges>, BACKUP_ADMIN, RESTORE_ADMIN, SYSTEM_USER, RESOURCE_GROUP_ADMIN
- Follow-up Guidance: The source also points to SHOW GRANTS, Privilege Management, and GRANT <privileges> for related privilege information.
- Classification Note: This is reference content because it defines the SHOW PRIVILEGES syntax, shows a fixed example result set of privileges and contexts, and states its MySQL compatibility.

## Official Source Content

# SHOW PRIVILEGES

This statement shows a list of assignable privileges in TiDB. It is a static list, and does not reflect the privileges of the current user.
## Synopsis

```ebnf+diagram
ShowPrivilegesStmt ::=
    "SHOW" "PRIVILEGES"
```
## Examples

```sql
SHOW PRIVILEGES;
```

```
+---------------------------------+---------------------------------------+-------------------------------------------------------+
| Privilege                       | Context                               | Comment                                               |
+---------------------------------+---------------------------------------+-------------------------------------------------------+
| Alter                           | Tables                                | To alter the table                                    |
| Alter routine                   | Functions,Procedures                  | To alter or drop stored functions/procedures          |
| Config                          | Server Admin                          | To use SHOW CONFIG and SET CONFIG statements          |
| Create                          | Databases,Tables,Indexes              | To create new databases and tables                    |
| Create routine                  | Databases                             | To use CREATE FUNCTION/PROCEDURE                      |
| Create role                     | Server Admin                          | To create new roles                                   |
| Create temporary tables         | Databases                             | To use CREATE TEMPORARY TABLE                         |
| Create view                     | Tables                                | To create new views                                   |
| Create user                     | Server Admin                          | To create new users                                   |
| Delete                          | Tables                                | To delete existing rows                               |
| Drop                            | Databases,Tables                      | To drop databases, tables, and views                  |
| Drop role                       | Server Admin                          | To drop roles                                         |
| Event                           | Server Admin                          | To create, alter, drop and execute events             |
| Execute                         | Functions,Procedures                  | To execute stored routines                            |
| File                            | File access on server                 | To read and write files on the server                 |
| Grant option                    | Databases,Tables,Functions,Procedures | To give to other users those privileges you possess   |
| Index                           | Tables                                | To create or drop indexes                             |
| Insert                          | Tables                                | To insert data into tables                            |
| Lock tables                     | Databases                             | To use LOCK TABLES (together with SELECT privilege)   |
| Process                         | Server Admin                          | To view the plain text of currently executing queries |
| Proxy                           | Server Admin                          | To make proxy user possible                           |
| References                      | Databases,Tables                      | To have references on tables                          |
| Reload                          | Server Admin                          | To reload or refresh tables, logs and privileges      |
| Replication client              | Server Admin                          | To ask where the slave or master servers are          |
| Replication slave               | Server Admin                          | To read binary log events from the master             |
| Select                          | Tables                                | To retrieve rows from table                           |
| Show databases                  | Server Admin                          | To see all databases with SHOW DATABASES              |
| Show view                       | Tables                                | To see views with SHOW CREATE VIEW                    |
| Shutdown                        | Server Admin                          | To shut down the server                               |
| Super                           | Server Admin                          | To use KILL thread, SET GLOBAL, CHANGE MASTER, etc.   |
| Trigger                         | Tables                                | To use triggers                                       |
| Create tablespace               | Server Admin                          | To create/alter/drop tablespaces                      |
| Update                          | Tables                                | To update existing rows                               |
| Usage                           | Server Admin                          | No privileges - allow connect only                    |
| BACKUP_ADMIN                    | Server Admin                          |                                                       |
| RESTORE_ADMIN                   | Server Admin                          |                                                       |
| SYSTEM_USER                     | Server Admin                          |                                                       |
| SYSTEM_VARIABLES_ADMIN          | Server Admin                          |                                                       |
| ROLE_ADMIN                      | Server Admin                          |                                                       |
| CONNECTION_ADMIN                | Server Admin                          |                                                       |
| PLACEMENT_ADMIN                 | Server Admin                          |                                                       |
| DASHBOARD_CLIENT                | Server Admin                          |                                                       |
| RESTRICTED_TABLES_ADMIN         | Server Admin                          |                                                       |
| RESTRICTED_STATUS_ADMIN         | Server Admin                          |                                                       |
| RESTRICTED_VARIABLES_ADMIN      | Server Admin                          |                                                       |
| RESTRICTED_USER_ADMIN           | Server Admin                          |                                                       |
| RESTRICTED_CONNECTION_ADMIN     | Server Admin                          |                                                       |
| RESTRICTED_REPLICA_WRITER_ADMIN | Server Admin                          |                                                       |
| RESOURCE_GROUP_ADMIN            | Server Admin                          |                                                       |
+---------------------------------+---------------------------------------+-------------------------------------------------------+
49 rows in set (0.00 sec)
```
## MySQL compatibility

The `SHOW PRIVILEGES` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [SHOW GRANTS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-grants)
* [Privilege Management](https://docs.pingcap.com/tidb/stable/privilege-management)
* [`GRANT <privileges>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-grant-privileges)

* [SHOW GRANTS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-grants)
* [Privilege Management](https://docs.pingcap.com/tidb/stable/privilege-management)
* [`GRANT <privileges>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-grant-privileges)
