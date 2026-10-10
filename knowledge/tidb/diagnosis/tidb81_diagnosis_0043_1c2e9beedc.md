# Post-upgrade JDBC collation and charset DDL issues

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/upgrade-faq.md`
- Source Title: `Upgrade and After Upgrade FAQs`
- Source Heading Path: `Upgrade and After Upgrade FAQs > After upgrade FAQs | Upgrade and After Upgrade FAQs > After upgrade FAQs > The collation in JDBC connections changes after upgrading TiDB | Upgrade and After Upgrade FAQs > After upgrade FAQs > The character set (charset) errors when executing DDL operations | Upgrade and After Upgrade FAQs > After upgrade FAQs > The character set (charset) errors when executing DDL operations > `unsupported modify column charset utf8mb4 not match origin utf8` | Upgrade and After Upgrade FAQs > After upgrade FAQs > The character set (charset) errors when executing DDL operations > `unsupported modify charset from utf8mb4 to utf8``
- Source Line Ranges: `34-235`
- Source Scope: `shared`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `upgrade`, `jdbc`, `collation`, `charset`, `ddl`, `http-api`, `schema-metadata`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0043_1c2e9beedc`
- Source ID: `tidb-docs-8.1:faq/upgrade-faq.md#after-upgrade-faqs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a95c52ae068095e9e92d7e886c8f2503d0fc1165324903745f58ad1a45c1d893`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/upgrade-faq#after-upgrade-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/upgrade-faq.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing post-upgrade JDBC collation changes or DDL charset errors such as `unsupported modify column charset utf8mb4 not match origin utf8` and `unsupported modify charset from utf8mb4 to utf8`.
- Retrieval Keywords: After upgrade FAQs, JDBC connections, connectionCollation, characterEncoding, UTF-8, utf8mb4_bin, utf8mb4_0900_ai_ci, Collation used in JDBC connections, character set errors when executing DDL operations, unsupported modify column charset utf8mb4 not match origin utf8, unsupported modify charset from utf8mb4 to utf8, show create table, alter table t change column a a varchar(20), alter table t change column a a varchar(22) character set utf8, alter table t convert to character set utf8mb4, HTTP API, curl http://$IP:10080/schema/test/t, Charset
- Follow-up Guidance: The content includes checking table metadata through the HTTP API at `http://$IP:10080/schema/test/t` and searching the column name and the keyword `Charset`, plus a related link to Collation used in JDBC connections.
- Classification Note: This is classified as diagnosis because the content focuses on identifying and resolving post-upgrade collation and charset mismatch symptoms and specific error messages.

## Official Source Content

## After upgrade FAQs

This section lists some FAQs and their solutions after you upgrade TiDB.
### The collation in JDBC connections changes after upgrading TiDB

When upgrading from an earlier version to v7.4 or later, if the `connectionCollation` is not configured, and the `characterEncoding` is either not configured or configured as `UTF-8` in the JDBC URL, the default collation in your JDBC connections might change from `utf8mb4_bin` to `utf8mb4_0900_ai_ci` after upgrading. If you need to maintain the collation as `utf8mb4_bin`, configure `connectionCollation=utf8mb4_bin` in the JDBC URL.

For more information, see [Collation used in JDBC connections](https://docs.pingcap.com/tidb/stable/faq/sql-faq#collation-used-in-jdbc-connections).
### The character set (charset) errors when executing DDL operations

In v2.1.0 and earlier versions (including all versions of v2.0), the character set of TiDB is UTF-8 by default. But starting from v2.1.1, the default character set has been changed into UTF8MB4.

If you explicitly specify the charset of a newly created table as UTF-8 in v2.1.0 or earlier versions, then you might fail to execute DDL operations after upgrading TiDB to v2.1.1.

To avoid this issue, you need to pay attention to:

- Before v2.1.3, TiDB does not support modifying the charset of the column. Therefore, when you execute DDL operations, you need to make sure that the charset of the new column is consistent with that of the original column.

- Before v2.1.3, even if the charset of the column is different from that of the table, `show create table` does not show the charset of the column. But as shown in the following example, you can view it by obtaining the metadata of the table through the HTTP API.
#### `unsupported modify column charset utf8mb4 not match origin utf8`

- Before upgrading, the following operations are executed in v2.1.0 and earlier versions.

    ```sql
    create table t(a varchar(10)) charset=utf8;
    ```

    ```
    Query OK, 0 rows affected
    Time: 0.106s
    ```

    ```sql
    show create table t;
    ```

    ```
    +-------+-------------------------------------------------------+
    | Table | Create Table                                          |
    +-------+-------------------------------------------------------+
    | t     | CREATE TABLE `t` (                                    |
    |       |   `a` varchar(10) DEFAULT NULL                        |
    |       | ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin |
    +-------+-------------------------------------------------------+
    1 row in set
    Time: 0.006s
    ```

- After upgrading, the following error is reported in v2.1.1 and v2.1.2 but there is no such error in v2.1.3 and the later versions.

    ```sql
    alter table t change column a a varchar(20);
    ```

    ```
    ERROR 1105 (HY000): unsupported modify column charset utf8mb4 not match origin utf8
    ```

Solution:

You can explicitly specify the column charset as the same with the original charset.

```sql
alter table t change column a a varchar(22) character set utf8;
```

- According to Point #1, if you do not specify the column charset, UTF8MB4 is used by default, so you need to specify the column charset to make it consistent with the original one.

- According to Point #2, you can obtain the metadata of the table through the HTTP API, and find the column charset by searching the column name and the keyword "Charset".

    ```sh
    curl "http://$IP:10080/schema/test/t" | python -m json.tool
    ```

    A python tool is used here to format JSON, which is not required and only for the convenience to add the comments.

    ```json
    {
        "ShardRowIDBits": 0,
        "auto_inc_id": 0,
        "charset": "utf8",   # The charset of the table.
        "collate": "",
        "cols": [            # The relevant information about the columns.
            {
                ...
                "id": 1,
                "name": {
                    "L": "a",
                    "O": "a"   # The column name.
                },
                "offset": 0,
                "origin_default": null,
                "state": 5,
                "type": {
                    "Charset": "utf8",   # The charset of column a.
                    "Collate": "utf8_bin",
                    "Decimal": 0,
                    "Elems": null,
                    "Flag": 0,
                    "Flen": 10,
                    "Tp": 15
                }
            }
        ],
        ...
    }
    ```
#### `unsupported modify charset from utf8mb4 to utf8`

- Before upgrading, the following operations are executed in v2.1.1 and v2.1.2.

    ```sql
    create table t(a varchar(10)) charset=utf8;
    ```

    ```
    Query OK, 0 rows affected
    Time: 0.109s
    ```

    ```sql
    show create table t;
    ```

    ```
    +-------+-------------------------------------------------------+
    | Table | Create Table                                          |
    +-------+-------------------------------------------------------+
    | t     | CREATE TABLE `t` (                                    |
    |       |   `a` varchar(10) DEFAULT NULL                        |
    |       | ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin |
    +-------+-------------------------------------------------------+
    ```

    In the above example, `show create table` only shows the charset of the table, but the charset of the column is actually UTF8MB4, which can be confirmed by obtaining the schema through the HTTP API. However, when a new table is created, the charset of the column should stay consistent with that of the table. This bug has been fixed in v2.1.3.

- After upgrading, the following operations are executed in v2.1.3 and the later versions.

    ```sql
    show create table t;
    ```

    ```
    +-------+--------------------------------------------------------------------+
    | Table | Create Table                                                       |
    +-------+--------------------------------------------------------------------+
    | t     | CREATE TABLE `t` (                                                 |
    |       |   `a` varchar(10) CHARSET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL |
    |       | ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin              |
    +-------+--------------------------------------------------------------------+
    1 row in set
    Time: 0.007s
    ```

    ```sql
    alter table t change column a a varchar(20);
    ```

    ```
    ERROR 1105 (HY000): unsupported modify charset from utf8mb4 to utf8
    ```

Solution:

- Starting from v2.1.3, TiDB supports modifying the charsets of the column and the table, so it is recommended to modify the table charset into UTF8MB4.

    ```sql
    alter table t convert to character set utf8mb4;
    ```

- You can also specify the column charset as done in Issue #1, making it stay consistent with the original column charset (UTF8MB4).

    ```sql
    alter table t change column a a varchar(20) character set utf8mb4;
    ```
