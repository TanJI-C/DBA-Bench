# TiDB error codes 8052-8156

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/error-codes.md`
- Source Title: `Error Codes and Troubleshooting`
- Source Heading Path: `Error Codes and Troubleshooting > Error codes`
- Source Line Ranges: `166-365`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `sql`, `shared`
- Topic Tags: `error-codes`, `troubleshooting`, `sql-hints`, `plugins`, `prepared-statements`, `transactions`, `garbage-collection`, `auto-random`, `pd-connectivity`, `privileges`, `group-by`, `multi-statement`, `data-index-inconsistency`, `non-transactional-dml`, `load-data`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0242_b50106befb`
- Source ID: `tidb-docs-8.1:error-codes.md#error-codes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `973911412afe7fdc96cdb8035deffb167ba92a1ccd897d2692d048037fccb8a2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/error-codes#error-codes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/error-codes.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB error meanings and documented handling for error codes 8052 through 8156, including SQL Hint, plugin, prepared statement, PD connectivity, only_full_group_by, multi-statement, data-index inconsistency, non-transactional DML, and LOAD DATA cases.
- Retrieval Keywords: Error Number: 8052, Error Number: 8055, tidb_gc_life_time, garbage collection overview, Error Number: 8059, auto-random ID is exhausted, Error Number: 8060, auto_increment_increment, auto_increment_offset, Error Number: 8061, Unsupported SQL Hint, Error Number: 8062, invalid token is used in SQL Hint, Error Number: 8063, limited memory usage set in SQL Hint exceeds the upper limit, Error Number: 8064, fails to parse SQL Hint, Error Number: 8065, invalid integer is used in SQL Hint, Error Number: 8066, JSON_OBJECTAGG second parameter is invalid, Error Number: 8101, plugin ID format [name]-[version], Error Number: 8102, Unable to read the plugin definition information, Error Number: 8103, plugin name is incorrect, Error Number: 8104, plugin version does not match, Error Number: 8105, plugin is repeatedly loaded, Error Number: 8106, plugin defines a system variable whose name does not begin with the plugin name, Error Number: 8107, loaded plugin does not specify a version, Error Number: 8108, Unsupported execution plan type, Error Number: 8109, specified index cannot be found when the index is analyzed, Error Number: 8110, Cartesian product operation cannot be executed, cross-join, Error Number: 8111, EXECUTE statement corresponding Prepare statement cannot be found, Error Number: 8112, number of parameters in the EXECUTE statement is not consistent with the Prepare statement, Error Number: 8113, table schema related in the EXECUTE statement has changed after the Prepare statement is executed, Error Number: 8115, not supported to prepare multiple lines of statements, Error Number: 8116, not supported to prepare DDL statements, Error Number: 8120, start tso of transactions cannot be obtained, PD server, Error Number: 8121, Privilege check fails, Error Number: 8122, No corresponding table name is found given the specified wild cards, Error Number: 8123, only_full_group_by, aggregate functions returns non-aggregated columns, Error Number: 8129, JSON objects with the key length >= 65536, Error Number: 8130, client has multi-statement capability disabled, tidb_multi_statement_mode, COM_QUERY, Error Number: 8138, Troubleshoot Inconsistency Between Data and Indexes, Error Number: 8139, Error Number: 8140, Error Number: 8141, existence assertion of a key fails, Error Number: 8143, Non-transactional DML statements, Error Number: 8147, tidb_constraint_check_in_place_pessimistic, Constraints pessimistic transactions, Error Number: 8154, LOAD DATA does not support importing data locally from TiDB server, LOCAL, S3 or GCS
- Follow-up Guidance: The source points to related references including garbage collection overview and configuration, auto random, Optimizer Hints, Troubleshoot Inconsistency Between Data and Indexes, Non-transactional DML statements, Constraints, and LOAD DATA for more details on the listed errors.
- Classification Note: This chunk is reference content because it enumerates TiDB error codes 8052-8156 with their exact meanings and associated identifiers, variables, and linked troubleshooting topics.

## Official Source Content

Unknown data type is encountered when TiDB parses the Exec argument list sent by the client.

    If you encounter this error, check the client. If the client is normal, [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.

* Error Number: 8052

    The serial number of the data packet from the client is incorrect.

    If you encounter this error, check the client. If the client is normal, [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.

* Error Number: 8055

    The current snapshot is too old. The data may have been garbage collected. You can increase the value of [`tidb_gc_life_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_life_time-new-in-v50) to avoid this problem. TiDB automatically reserves data for long-running transactions. Usually this error does not occur.

    See [garbage collection overview](https://docs.pingcap.com/tidb/stable/garbage-collection-overview) and [garbage collection configuration](https://docs.pingcap.com/tidb/stable/garbage-collection-configuration).

* Error Number: 8059

    The auto-random ID is exhausted and cannot be allocated. There is no way to recover from such errors currently. It is recommended to use bigint when using the auto random feature to obtain the maximum number of assignment. And try to avoid manually assigning values to the auto random column.

    See [auto random](https://docs.pingcap.com/tidb/stable/auto-random) for reference.

* Error Number: 8060

    Invalid auto-incrementing offset. Check the values of `auto_increment_increment` and `auto_increment_offset`.

* Error Number: 8061

    Unsupported SQL Hint.

    See [Optimizer Hints](https://docs.pingcap.com/tidb/stable/optimizer-hints) to check and modify the SQL Hint.

* Error Number: 8062

    An invalid token is used in SQL Hint. It conflicts with reserved words in SQL Hint.

    See [Optimizer Hints](https://docs.pingcap.com/tidb/stable/optimizer-hints) to check and modify the SQL Hint.

* Error Number: 8063

    The limited memory usage set in SQL Hint exceeds the upper limit of the system. The setting in SQL Hint is ignored.

    See [Optimizer Hints](https://docs.pingcap.com/tidb/stable/optimizer-hints) to check and modify the SQL Hint.

* Error Number: 8064

    It fails to parse SQL Hint.

    See [Optimizer Hints](https://docs.pingcap.com/tidb/stable/optimizer-hints) to check and modify the SQL Hint.

* Error Number: 8065

    An invalid integer is used in SQL Hint.

    See [Optimizer Hints](https://docs.pingcap.com/tidb/stable/optimizer-hints) to check and modify the SQL Hint.

* Error Number: 8066

    The second parameter in the `JSON_OBJECTAGG` function is invalid.

* Error Number: 8101

    The format of plugin ID is incorrect.

    The correct format is `[name]-[version]`, and no `-` is allowed in `name` and `version`.

* Error Number: 8102

    Unable to read the plugin definition information.

    Check the configuration related to the plugin.

* Error Number: 8103

    The plugin name is incorrect.

    Check the configuration of the plugin.

* Error Number: 8104

    The plugin version does not match.

    Check the configuration of the plugin.

* Error Number: 8105

    The plugin is repeatedly loaded.

* Error Number: 8106

    The plugin defines a system variable whose name does not begin with the plugin name.

    Contact the developer of the plugin to modify, or [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.

* Error Number: 8107

    The loaded plugin does not specify a version, or the specified version is too low.

    Check the configuration of the plugin.

* Error Number: 8108

    Unsupported execution plan type. This error is an internal error.

    If you encounter this error, [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.

* Error Number: 8109

    The specified index cannot be found when the index is analyzed.

* Error Number: 8110

    The Cartesian product operation cannot be executed.

    Set `cross-join` in the configuration to `true`.

* Error Number: 8111

    When executing the `EXECUTE` statement, the corresponding `Prepare` statement cannot be found.

* Error Number: 8112

    The number of parameters in the `EXECUTE` statement is not consistent with the `Prepare` statement.

* Error Number: 8113

    The table schema related in the `EXECUTE` statement has changed after the `Prepare` statement is executed.

* Error Number: 8115

    It is not supported to prepare multiple lines of statements.

* Error Number: 8116

    It is not supported to prepare DDL statements.

* Error Number: 8120

    The `start tso` of transactions cannot be obtained.

    Check the state/monitor/log of the PD server and the network between the TiDB server and the PD server.

* Error Number: 8121

    Privilege check fails.

    Check the privilege configuration of the database.

* Error Number: 8122

    No corresponding table name is found, given the specified wild cards.

* Error Number: 8123

    An SQL query with aggregate functions returns non-aggregated columns, which violates the `only_full_group_by` mode.

    Modify the SQL statement or disable the `only_full_group_by` mode.

* Error Number: 8129

    TiDB does not yet support JSON objects with the key length >= 65536.

* Error Number: 8130

    The complete error message: `ERROR 8130 (HY000): client has multi-statement capability disabled`

    This error might occur after you upgrade from an earlier version of TiDB. To reduce the impact of SQL injection attacks, TiDB now prevents multiple queries from being executed in the same `COM_QUERY` call by default.

    The system variable [`tidb_multi_statement_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_multi_statement_mode-new-in-v4011) can be used to control this behavior.

* Error Number: 8138

    The transaction attempts to write an incorrect row value. For more information, see [Troubleshoot Inconsistency Between Data and Indexes](https://docs.pingcap.com/tidb/stable/troubleshoot-data-inconsistency-errors#error-8138).

* Error Number: 8139

    The transaction attempts to write a row whose handle is inconsistent with that in the index. For more information, see [Troubleshoot Inconsistency Between Data and Indexes](https://docs.pingcap.com/tidb/stable/troubleshoot-data-inconsistency-errors#error-8139).

* Error Number: 8140

   The transaction attempts to write a row whose data is inconsistent with the index data. For more information, see [Troubleshoot Inconsistency Between Data and Indexes](https://docs.pingcap.com/tidb/stable/troubleshoot-data-inconsistency-errors#error-8140).

* Error Number: 8141

    When a transaction is being committed, the existence assertion of a key fails. For more information,see [Troubleshoot Inconsistency Between Data and Indexes](https://docs.pingcap.com/tidb/stable/troubleshoot-data-inconsistency-errors#error-8141).

* Error Number: 8143

    During the execution of a non-transactional DML statement, if a batch fails, the statement is stopped. For more information, see [Non-transactional DML statements](https://docs.pingcap.com/tidb/stable/non-transactional-dml).

* Error Number: 8147

    When [`tidb_constraint_check_in_place_pessimistic`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_constraint_check_in_place_pessimistic-new-in-v630) is set to `OFF`, to ensure the correctness of transactions, any errors in the SQL statement execution might cause TiDB to return this `8147` error and abort the current transaction. For specific causes of the error, refer to the error message. For more information, see [Constraints](https://docs.pingcap.com/tidb/stable/constraints#pessimistic-transactions).

* Error Number: 8154

    Currently `LOAD DATA` does not support importing data locally from TiDB server. You can specify `LOCAL` to import from client, or upload data to S3 or GCS and then import it. See [`LOAD DATA`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-load-data).

* Error Number: 8156
