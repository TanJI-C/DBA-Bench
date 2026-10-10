# USER_ATTRIBUTES table schema and example usage

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-user-attributes.md`
- Source Title: `USER_ATTRIBUTES`
- Source Heading Path: `USER_ATTRIBUTES`
- Source Line Ranges: `5-49`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `information_schema`, `user_attributes`, `user metadata`, `user comments`, `user attributes`, `mysql.user`, `create user`, `alter user`, `schema`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0430_6c87ebba9b`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-user-attributes.md#user-attributes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0988cfe49d7aade42ec0e957fa1179c5ee1b35983f158be3f41eaf17092e5e65`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-user-attributes#user-attributes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-user-attributes.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the schema, field meanings, or example query results of the information_schema.USER_ATTRIBUTES table that shows user comments and attributes from mysql.user.
- Retrieval Keywords: USER_ATTRIBUTES, information_schema.user_attributes, mysql.user, DESC user_attributes, USER, HOST, ATTRIBUTE, CREATE USER COMMENT, CREATE USER ATTRIBUTE, ALTER USER, user comments, user attributes
- Follow-up Guidance: The source includes example SQL using CREATE USER with COMMENT or ATTRIBUTE and SELECT * FROM information_schema.user_attributes.
- Classification Note: This is reference content because it defines the USER_ATTRIBUTES table schema, explains the USER, HOST, and ATTRIBUTE fields, and shows example SQL and result output.

## Official Source Content

# USER_ATTRIBUTES

The `USER_PRIVILEGES` table provides information about user comments and user attributes. This information comes from the `mysql.user` system table.

```sql
USE information_schema;
DESC user_attributes;
```

```sql
+-----------+--------------+------+------+---------+-------+
| Field     | Type         | Null | Key  | Default | Extra |
+-----------+--------------+------+------+---------+-------+
| USER      | varchar(32)  | NO   |      | NULL    |       |
| HOST      | varchar(255) | NO   |      | NULL    |       |
| ATTRIBUTE | longtext     | YES  |      | NULL    |       |
+-----------+--------------+------+------+---------+-------+
3 rows in set (0.00 sec)
```

Fields in the `USER_ATTRIBUTES` table are described as follows:

* `USER`: The user name.
* `HOST`: The host from which the user can connect to TiDB. If the value of this field is `％`, it means that the user can connect to TiDB from any host.
* `ATTRIBUTE`: The comment and attribute of the user, which are set by the [`CREATE USER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-user) or [`ALTER USER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-user) statement.

The following is an example:

```sql
CREATE USER testuser1 COMMENT 'This user is created only for test';
CREATE USER testuser2 ATTRIBUTE '{"email": "user@pingcap.com"}';
SELECT * FROM information_schema.user_attributes;
```

```sql
+-----------+------+---------------------------------------------------+
| USER      | HOST | ATTRIBUTE                                         |
+-----------+------+---------------------------------------------------+
| root      | %    | NULL                                              |
| testuser1 | %    | {"comment": "This user is created only for test"} |
| testuser2 | %    | {"email": "user@pingcap.com"}                     |
+-----------+------+---------------------------------------------------+
3 rows in set (0.00 sec)
```
