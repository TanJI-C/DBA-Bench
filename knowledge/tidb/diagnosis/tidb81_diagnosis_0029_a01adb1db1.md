# DM access denied and load packet size error handling

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-error-handling.md`
- Source Title: `Handle Errors in TiDB Data Migration`
- Source Heading Path: `Handle Errors in TiDB Data Migration > Handle common errors > `Access denied for user 'root'@'172.31.43.27' (using password: YES)` shows when you query the task or check the log | Handle Errors in TiDB Data Migration > Handle common errors > The `load` processing unit reports the error `packet for query is too large. Try adjusting the 'max_allowed_packet' variable` | Handle Errors in TiDB Data Migration > Handle common errors > The `load` processing unit reports the error `packet for query is too large. Try adjusting the 'max_allowed_packet' variable` > Reasons | Handle Errors in TiDB Data Migration > Handle common errors > The `load` processing unit reports the error `packet for query is too large. Try adjusting the 'max_allowed_packet' variable` > Solutions`
- Source Line Ranges: `179-209`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`, `sql`
- Topic Tags: `access-denied`, `password-encryption`, `privileges`, `precheck`, `load-unit`, `max-allowed-packet`, `statement-size`, `wide-table`, `task-configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0029_a01adb1db1`
- Source ID: `tidb-docs-8.1:dm/dm-error-handling.md#access-denied-for-user-root-172-31-43-27-using-password-yes-shows-when-you-query-the-task-or-check-the-log`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5815502e30e638b2ab8f92748ce52a76d004da8639f8d0d817d82401aed4c975`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-error-handling#access-denied-for-user-root-172-31-43-27-using-password-yes-shows-when-you-query-the-task-or-check-the-log
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-error-handling.md

## Retrieval Guidance

- Use When: Use this chunk when DM shows `Access denied for user 'root'@'172.31.43.27' (using password: YES)` or when the `load` unit reports `packet for query is too large. Try adjusting the 'max_allowed_packet' variable`.
- Retrieval Keywords: Access denied for user 'root'@'172.31.43.27' (using password: YES), dmctl, Encrypt the database password using dmctl, precheck, read and write privileges, load processing unit, packet for query is too large. Try adjusting the 'max_allowed_packet' variable, max_allowed_packet, statement-size, extra-args, Insert Statement, Row bigger than statement_size for xxx, wide tables, set @@global.max_allowed_packet=134217728, max-allowed-packet: 134217728, target-database, stop-task, start-task
- Follow-up Guidance: The source notes encrypted passwords in DM configuration, automatic privilege prechecks at task start, `statement-size` for the Dump unit, and `max_allowed_packet` settings in TiDB server and DM task configuration with `stop-task` and `start-task` for changes to take effect.
- Classification Note: This is classified as diagnosis because the content explains the reasons and relevant configuration or privilege conditions behind access denied and oversized packet errors.

## Official Source Content

### `Access denied for user 'root'@'172.31.43.27' (using password: YES)` shows when you query the task or check the log

For database related passwords in all the DM configuration files, it is recommended to use the passwords encrypted by `dmctl`. If a database password is empty, it is unnecessary to encrypt it. For how to encrypt the plaintext password, see [Encrypt the database password using dmctl](https://docs.pingcap.com/tidb/stable/dm/dm-manage-source#encrypt-the-database-password).

In addition, the user of the upstream and downstream databases must have the corresponding read and write privileges. Data Migration also [prechecks the corresponding privileges automatically](https://docs.pingcap.com/tidb/stable/dm/dm-precheck) while starting the data migration task.
### The `load` processing unit reports the error `packet for query is too large. Try adjusting the 'max_allowed_packet' variable`
#### Reasons

* Both MySQL client and MySQL/TiDB server have the quota limits for `max_allowed_packet`. If any `max_allowed_packet` exceeds a limit, the client receives the error message. Currently, for the latest version of DM and TiDB server, the default value of `max_allowed_packet` is `64M`.

* The full data import processing unit in DM does not support splitting the SQL file exported by the Dump processing unit in DM.
#### Solutions

* It is recommended to set the `statement-size` option of `extra-args` for the Dump processing unit:

    According to the default `--statement-size` setting, the default size of `Insert Statement` generated by the Dump processing unit is about `1M`. With this default setting, the load processing unit does not report the error `packet for query is too large. Try adjusting the 'max_allowed_packet' variable` in most cases.

    Sometimes you might receive the following `WARN` log during the data dump. This `WARN` log does not affect the dump process. This only means that wide tables are dumped.

    ```
    Row bigger than statement_size for xxx
    ```

* If the single row of the wide table exceeds `64M`, you need to modify the following configurations and make sure the configurations take effect.

    * Execute `set @@global.max_allowed_packet=134217728` (`134217728` = 128 MB) in the TiDB server.

    * First add the `max-allowed-packet: 134217728` (128 MB) to the `target-database` section in the DM task configuration file. Then, execute the `stop-task` command and execute the `start-task` command.
