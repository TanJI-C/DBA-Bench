# Read behavior, logging, and optimizer-related system variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_rc_write_check_ts <span class="version-mark">New in v6.3.0</span> | System Variables > Variable reference > tidb_read_consistency <span class="version-mark">New in v5.4.0</span> | System Variables > Variable reference > tidb_read_staleness <span class="version-mark">New in v5.4.0</span> | System Variables > Variable reference > tidb_record_plan_in_slow_log | System Variables > Variable reference > tidb_redact_log | System Variables > Variable reference > tidb_regard_null_as_point <span class="version-mark">New in v5.4.0</span> | System Variables > Variable reference > tidb_remove_orderby_in_subquery <span class="version-mark">New in v6.1.0</span> | System Variables > Variable reference > tidb_replica_read <span class="version-mark">New in v4.0</span>`
- Source Line Ranges: `4909-5003`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `system-variables`, `read-consistency`, `stale-read`, `slow-log`, `log-redaction`, `optimizer`, `subquery-order`, `replica-read`, `point-write`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0738_82d8724b44`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-rc-write-check-ts-span-class-version-mark-new-in-v6-3-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1457624a330ad04526d1ae54b1de9b04ab1629309aae6e4ac1a206ef821b9c6a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-rc-write-check-ts-span-class-version-mark-new-in-v6-3-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about TiDB system variables for read consistency or stale reads, replica read behavior, slow log plan recording, log redaction, or optimizer behavior around null equivalence, subquery ORDER BY removal, and READ-COMMITTED point-write timestamp optimization.
- Retrieval Keywords: tidb_rc_write_check_ts, replica-read incompatibility, READ-COMMITTED isolation level, pessimistic transactions, point-write statements, POINT-GET, UPDATE, DELETE, SELECT ... FOR UPDATE, tidb_read_consistency, weak consistency read mode, auto-commit read statement, strict, weak, tidb_read_staleness, historical data, stale read, current session, tidb_record_plan_in_slow_log, slow log execution plan, tidb_redact_log, OFF, ON, MARKER, hide user information, INSERT INTO t VALUES (?,?), tidb_regard_null_as_point, null equivalence, a<=>null and b=1, index(a, b), tidb_remove_orderby_in_subquery, remove ORDER BY clause in a subquery, tidb_replica_read, leader, follower, leader-and-follower, prefer-leader, closest-replicas, closest-adaptive, learner, Follower read
- Follow-up Guidance: The chunk also points to related details in Read Committed isolation level and Follower read, and notes TiDB Cloud exceptions for tidb_record_plan_in_slow_log and tidb_redact_log.
- Classification Note: This is a reference chunk because it lists variable scopes, defaults, types, possible values, warnings, and behavior descriptions for multiple TiDB system variables.

## Official Source Content

### tidb_rc_write_check_ts New in v6.3.0

> **Warning:**
>
> This feature is currently incompatible with [`replica-read`](#tidb_replica_read-new-in-v40). After this variable is enabled, all requests sent by the client cannot use `replica-read`. Therefore, do not enable `tidb_rc_write_check_ts` and `replica-read` at the same time.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used to optimize the acquisition of timestamps and is suitable for scenarios with few point-write conflicts in `READ-COMMITTED` isolation level of pessimistic transactions. Enabling this variable can avoid the latency and overhead brought by obtaining the global timestamps during the execution of point-write statements. Currently, this variable is applicable to three types of point-write statements: `UPDATE`, `DELETE`, and `SELECT ...... FOR UPDATE`. A point-write statement refers to a write statement that uses the primary key or unique key as a filter condition and the final execution operator contains `POINT-GET`.
- If the point-write conflicts are severe, enabling this variable will increase extra overhead and latency, resulting in performance regression. For details, see [Read Committed isolation level](https://docs.pingcap.com/tidb/stable/transaction-isolation-levels#read-committed-isolation-level).
### tidb_read_consistency New in v5.4.0

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes (Note that if [non-transactional DML statements](https://docs.pingcap.com/tidb/stable/non-transactional-dml) exist, modifying the value of this variable using hint might not take effect.)
- Type: String
- Default value: `strict`
- This variable is used to control the read consistency for an auto-commit read statement.
- If the variable value is set to `weak`, the locks encountered by the read statement are skipped directly and the read execution might be faster, which is the weak consistency read mode. However, the transaction semantics (such as atomicity) and distributed consistency (such as linearizability) are not guaranteed.
- For user scenarios where the auto-commit read needs to return fast and weak consistency read results are acceptable, you can use the weak consistency read mode.
### tidb_read_staleness New in v5.4.0

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- Range: `[-2147483648, 0]`
- This variable is used to set the time range of historical data that TiDB can read in the current session. After setting the value, TiDB selects a timestamp as new as possible from the range allowed by this variable, and all subsequent read operations are performed against this timestamp. For example, if the value of this variable is set to `-5`, on the condition that TiKV has the corresponding historical version's data, TiDB selects a timestamp as new as possible within a 5-second time range.
### tidb_record_plan_in_slow_log

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: GLOBAL
- Persists to cluster: No, only applicable to the current TiDB instance that you are connecting to.
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable is used to control whether to include the execution plan of slow queries in the slow log.
### tidb_redact_log

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Enumeration
- Default value: `OFF`
- Possible values: `OFF`, `ON`, `MARKER`
- This variable controls whether to hide the user information in the SQL statement being recorded into the TiDB log and slow log.
- The default value is `OFF`, which means that the user information is not processed in any way.
- When you set the variable to `ON`, the user information is hidden. For example, if the executed SQL statement is `INSERT INTO t VALUES (1,2)`, the statement is recorded as `INSERT INTO t VALUES (?,?)` in the log.
- When you set the variable to `MARKER`, the user information is wrapped in `‹ ›`. For example, if the executed SQL statement is `INSERT INTO t VALUES (1,2)`, the statement is recorded as `INSERT INTO t VALUES (‹1›,‹2›)` in the log. If the input has `‹`, it is escaped as `‹‹`, and `›` is escaped as `››`. Based on the marked logs, you can decide whether to desensitize the marked information when the logs are displayed.
### tidb_regard_null_as_point New in v5.4.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable controls whether the optimizer can use a query condition including null equivalence as a prefix condition for index access.
- This variable is enabled by default. When it is enabled, the optimizer can reduce the volume of index data to be accessed, which accelerates query execution. For example, if a query involves multiple-column indexes `index(a, b)` and the query condition contains `a<=>null and b=1`, the optimizer can use both `a<=>null` and `b=1` in the query condition for index access. If the variable is disabled, because `a<=>null and b=1` includes the null equivalence condition, the optimizer does not use `b=1` for index access.
### tidb_remove_orderby_in_subquery New in v6.1.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: Before v7.2.0, the default value is `OFF`. Starting from v7.2.0, the default value is `ON`.
- Specifies whether to remove `ORDER BY` clause in a subquery.
- In the ISO/IEC SQL standard, `ORDER BY` is mainly used to sort the results of top-level queries. For subqueries, the standard does not require that the results be sorted by `ORDER BY`. 
- To sort subquery results, you can usually handle it in the outer query, such as using the window function or using `ORDER BY` again in the outer query. Doing so ensures the order of the final result set.
### tidb_replica_read New in v4.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Enumeration
- Default value: `leader`
- Possible values: `leader`, `follower`, `leader-and-follower`, `prefer-leader`, `closest-replicas`, `closest-adaptive`, and `learner`. The `learner` value is introduced in v6.6.0.
- This variable is used to control where TiDB reads data.
- For more details about usage and implementation, see [Follower read](https://docs.pingcap.com/tidb/stable/follower-read).
