# SESSION_CONNECT_ATTRS table overview and columns

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/performance-schema/performance-schema-session-connect-attrs.md`
- Source Title: `SESSION_CONNECT_ATTRS`
- Source Heading Path: `SESSION\_CONNECT\_ATTRS`
- Source Line Ranges: `5-68`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `performance_schema`, `session attributes`, `connection metadata`, `table schema`, `processlist`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0476_744f36b0c6`
- Source ID: `tidb-docs-8.1:performance-schema/performance-schema-session-connect-attrs.md#session-connect-attrs`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `81f112e8d4bd2e68a2e17dbcebd59d19eed5c4bd688132851ab219ce66408c32`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/performance-schema/performance-schema-session-connect-attrs#session-connect-attrs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/performance-schema/performance-schema-session-connect-attrs.md

## Retrieval Guidance

- Use When: Use this chunk when looking up what the performance_schema SESSION_CONNECT_ATTRS table stores, its columns, or examples of client connection attributes tied to a session processlist entry.
- Retrieval Keywords: SESSION_CONNECT_ATTRS, performance_schema, session_connect_attrs, connection attributes, session attributes, PROCESSLIST_ID, ATTR_NAME, ATTR_VALUE, ORDINAL_POSITION, _client_name, _client_version, _os, _pid, _platform, program_name, DESCRIBE session_connect_attrs, TABLE SESSION_CONNECT_ATTRS, Processlist ID of the session
- Follow-up Guidance: The source also shows SQL examples for USE performance_schema; DESCRIBE session_connect_attrs; and USE performance_schema; TABLE SESSION_CONNECT_ATTRS;.
- Classification Note: This is reference content because it defines the SESSION_CONNECT_ATTRS table, lists its schema fields, and provides example rows for connection metadata.

## Official Source Content

# SESSION\_CONNECT\_ATTRS

The `SESSION_CONNECT_ATTRS` table provides information about connection attributes. Session attributes are key-value pairs that are sent by the client when establishing a connection.

Common attributes:

| Attribute Name    | Example       | Description                |
|-------------------|---------------|----------------------------|
| `_client_name`    | `libmysql`    | Client library name        |
| `_client_version` | `8.0.33`      | Client library version     |
| `_os`             | `Linux`       | Operating System           |
| `_pid`            | `712927`      | Process ID                 |
| `_platform`       | `x86_64`      | CPU Architecture           |
| `program_name`    | `mysqlsh`     | Program name               |

You can view the columns of the `SESSION_CONNECT_ATTRS` table as follows:

```sql
USE performance_schema;
DESCRIBE session_connect_attrs;
```

```
+------------------+---------------------+------+-----+---------+-------+
| Field            | Type                | Null | Key | Default | Extra |
+------------------+---------------------+------+-----+---------+-------+
| PROCESSLIST_ID   | bigint(20) unsigned | NO   |     | NULL    |       |
| ATTR_NAME        | varchar(32)         | NO   |     | NULL    |       |
| ATTR_VALUE       | varchar(1024)       | YES  |     | NULL    |       |
| ORDINAL_POSITION | int(11)             | YES  |     | NULL    |       |
+------------------+---------------------+------+-----+---------+-------+
```

You can view the information on session attributes stored in the `SESSION_CONNECT_ATTRS` table as follows:

```sql
USE performance_schema;
TABLE SESSION_CONNECT_ATTRS;
```

```
+----------------+-----------------+------------+------------------+
| PROCESSLIST_ID | ATTR_NAME       | ATTR_VALUE | ORDINAL_POSITION |
+----------------+-----------------+------------+------------------+
|        2097154 | _client_name    | libmysql   |                0 |
|        2097154 | _client_version | 8.1.2      |                1 |
|        2097154 | _os             | Linux      |                2 |
|        2097154 | _pid            | 1299203    |                3 |
|        2097154 | _platform       | x86_64     |                4 |
|        2097154 | program_name    | mysqlsh    |                5 |
+----------------+-----------------+------------+------------------+
```

Fields in the `SESSION_CONNECT_ATTRS` table are described as follows:

* `PROCESSLIST_ID`: Processlist ID of the session.
* `ATTR_NAME`: Attribute name.
* `ATTR_VALUE`: Attribute value.
* `ORDINAL_POSITION`: Ordinal position of the name/value pair.
