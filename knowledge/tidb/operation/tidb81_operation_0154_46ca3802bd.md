# Post-upgrade utf8 insert error and utf8mb4 or check-skip handling

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/upgrade-faq.md`
- Source Title: `Upgrade and After Upgrade FAQs`
- Source Heading Path: `Upgrade and After Upgrade FAQs > After upgrade FAQs > The character set (charset) errors when executing DDL operations > `ERROR 1366 (HY000): incorrect utf8 value f09f8c80(🌀) for column a``
- Source Line Ranges: `236-360`
- Source Scope: `shared`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `upgrade`, `charset`, `utf8`, `utf8mb4`, `ddl`, `session-variables`, `http-api`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0154_46ca3802bd`
- Source ID: `tidb-docs-8.1:faq/upgrade-faq.md#error-1366-hy000-incorrect-utf8-value-f09f8c80-for-column-a`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `13a3a558bc71b9e276183299812e4df19da4fc70e3e7b5a3c954914fc28159cb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/upgrade-faq#error-1366-hy000-incorrect-utf8-value-f09f8c80-for-column-a
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/upgrade-faq.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting `ERROR 1366 (HY000): incorrect utf8 value f09f8c80(🌀) for column a` after an upgrade involving inserts or DDL on a `varchar` column with `charset utf8`.
- Retrieval Keywords: ERROR 1366 (HY000), incorrect utf8 value f09f8c80(🌀) for column a, create table t(a varchar(100) charset utf8), insert t values (unhex('f09f8c80')), utf8mb4, alter table t change column a a varchar(100) character set utf8mb4, tidb_skip_utf8_check, tidb_check_mb4_value_in_utf8, check-mb4-value-in-utf8, http://{TiDBIP}:10080/settings, check_mb4_value_in_utf8, replicate data from TiDB to MySQL
- Follow-up Guidance: The content also notes that skipping the UTF-8 check with `tidb_skip_utf8_check` can cause replication to MySQL to fail because MySQL performs the check, and from v2.1.5 `tidb_check_mb4_value_in_utf8` can be set through the HTTP API or a session variable.
- Classification Note: This is classified as an operation issue for TiDB because the official content explains post-upgrade runtime behavior changes for UTF-8 validation and the available session variable, configuration, HTTP API, and charset-handling options.

## Official Source Content

#### `ERROR 1366 (HY000): incorrect utf8 value f09f8c80(🌀) for column a`

In TiDB v2.1.1 and earlier versions, if the charset is UTF-8, there is no UTF-8 Unicode encoding check on the inserted 4-byte data. But in v2.1.2 and the later versions, this check is added.

- Before upgrading, the following operations are executed in v2.1.1 and earlier versions.

    ```sql
    create table t(a varchar(100) charset utf8);
    ```

    ```
    Query OK, 0 rows affected
    ```

    ```sql
    insert t values (unhex('f09f8c80'));
    ```

    ```
    Query OK, 1 row affected
    ```

- After upgrading, the following error is reported in v2.1.2 and the later versions.

    ```sql
    insert t values (unhex('f09f8c80'));
    ```

    ```
    ERROR 1366 (HY000): incorrect utf8 value f09f8c80(🌀) for column a
    ```

Solution:

- In v2.1.2: this version does not support modifying the column charset, so you have to skip the UTF-8 check.

    ```sql
    set @@session.tidb_skip_utf8_check=1;
    ```

    ```
    Query OK, 0 rows affected
    ```

    ```sql
    insert t values (unhex('f09f8c80'));
    ```

    ```
    Query OK, 1 row affected
    ```

- In v2.1.3 and the later versions: it is recommended to modify the column charset into UTF8MB4. Or you can set `tidb_skip_utf8_check` to skip the UTF-8 check. But if you skip the check, you might fail to replicate data from TiDB to MySQL because MySQL executes the check.

    ```sql
    alter table t change column a a varchar(100) character set utf8mb4;
    ```

    ```
    Query OK, 0 rows affected
    ```

    ```sql
    insert t values (unhex('f09f8c80'));
    ```

    ```
    Query OK, 1 row affected
    ```

    Specifically, you can use the variable `tidb_skip_utf8_check` to skip the legal UTF-8 and UTF8MB4 check on the data. But if you skip the check, you might fail to replicate the data from TiDB to MySQL because MySQL executes the check.

    If you only want to skip the UTF-8 check, you can set `tidb_check_mb4_value_in_utf8`. This variable is added to the `config.toml` file in v2.1.3, and you can modify `check-mb4-value-in-utf8` in the configuration file and then restart the cluster to enable it.

    Starting from v2.1.5, you can set `tidb_check_mb4_value_in_utf8` through the HTTP API and the session variable:

    * HTTP API（the HTTP API can be enabled only on a single server）

        * To enable HTTP API:

            ```sh
            curl -X POST -d "check_mb4_value_in_utf8=1" http://{TiDBIP}:10080/settings
            ```

        * To disable HTTP API:

            ```sh
            curl -X POST -d "check_mb4_value_in_utf8=0" http://{TiDBIP}:10080/settings
            ```

    * Session variable

        * To enable session variable:

            ```sql
            set @@session.tidb_check_mb4_value_in_utf8 = 1;
            ```

        * To disable session variable:

            ```sql
            set @@session.tidb_check_mb4_value_in_utf8 = 0;
            ```
