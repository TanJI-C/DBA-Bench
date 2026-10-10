# Restricted read-only cluster mode variable

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_restricted_read_only <span class="version-mark">New in v5.2.0</span>`
- Source Line Ranges: `5004-5030`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `system-variables`, `read-only`, `cluster-scope`, `privileges`, `security-enhanced-mode`, `write-restriction`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0739_420f4f40c2`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-restricted-read-only-span-class-version-mark-new-in-v5-2-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cb6efb670d5b135d6240f1687473898447885db458a232f90c2e222ea6204f59`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-restricted-read-only-span-class-version-mark-new-in-v5-2-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about the tidb_restricted_read_only variable, cluster-wide read-only mode, its interaction with tidb_super_read_only, or privilege requirements including Security Enhanced Mode.
- Retrieval Keywords: tidb_restricted_read_only, read-only status of the entire cluster, tidb_super_read_only, Security Enhanced Mode, tidb_enable_enhanced_security, SUPER, SYSTEM_VARIABLES_ADMIN, RESTRICTED_VARIABLES_ADMIN, RESTRICTED_REPLICA_WRITER_ADMIN, GLOBAL, read-only mode, rejects INSERT and UPDATE, commit check since v6.2.0, uncommitted transactions, DBaaS providers, downstream database
- Follow-up Guidance: The chunk explains how tidb_restricted_read_only affects tidb_super_read_only, how propagation across TiDB servers works, and how uncommitted transactions and commit checks are handled in read-only mode.
- Classification Note: This is a reference chunk because it defines the variable semantics, privilege requirements, related variable interactions, and cluster-wide behavior of the read-only mode.

## Official Source Content

### tidb_restricted_read_only New in v5.2.0

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- `tidb_restricted_read_only` and [`tidb_super_read_only`](#tidb_super_read_only-new-in-v531) behave similarly. In most cases, you should use [`tidb_super_read_only`](#tidb_super_read_only-new-in-v531) only.
- Users with the `SUPER` or `SYSTEM_VARIABLES_ADMIN` privilege can modify this variable. However, if the [Security Enhanced Mode](#tidb_enable_enhanced_security) is enabled, the additional `RESTRICTED_VARIABLES_ADMIN` privilege is required to read or modify this variable.
- `tidb_restricted_read_only` affects [`tidb_super_read_only`](#tidb_super_read_only-new-in-v531) in the following cases:
    - Setting `tidb_restricted_read_only` to `ON` will update [`tidb_super_read_only`](#tidb_super_read_only-new-in-v531) to `ON`.
    - Setting `tidb_restricted_read_only` to `OFF` leaves [`tidb_super_read_only`](#tidb_super_read_only-new-in-v531) unchanged.
    - If `tidb_restricted_read_only` is `ON`, [`tidb_super_read_only`](#tidb_super_read_only-new-in-v531) cannot be set to `OFF`.
- For DBaaS providers of TiDB, if a TiDB cluster is a downstream database of another database, to make the TiDB cluster read-only, you might need to use `tidb_restricted_read_only` with [Security Enhanced Mode](#tidb_enable_enhanced_security) enabled, which prevents your customers from using [`tidb_super_read_only`](#tidb_super_read_only-new-in-v531) to make the cluster writable. To achieve this, you need to enable [Security Enhanced Mode](#tidb_enable_enhanced_security), use an admin user with the `SYSTEM_VARIABLES_ADMIN` and `RESTRICTED_VARIABLES_ADMIN` privileges to control `tidb_restricted_read_only`, and let your database users use the root user with the `SUPER` privilege to control [`tidb_super_read_only`](#tidb_super_read_only-new-in-v531) only.
- This variable controls the read-only status of the entire cluster. When the variable is `ON`, all TiDB servers in the entire cluster are in the read-only mode. In this case, TiDB only executes the statements that do not modify data, such as `SELECT`, `USE`, and `SHOW`. For other statements such as `INSERT` and `UPDATE`, TiDB rejects executing those statements in the read-only mode.
- Enabling the read-only mode using this variable only ensures that the entire cluster finally enters the read-only status. If you have changed the value of this variable in a TiDB cluster but the change has not yet propagated to other TiDB servers, the un-updated TiDB servers are still **not** in the read-only mode.
- TiDB checks the read-only flag before SQL statements are executed. Since v6.2.0, the flag is also checked before SQL statements are committed. This helps prevent the case where long-running [auto commit](https://docs.pingcap.com/tidb/stable/transaction-overview#autocommit) statements might modify data after the server has been placed in read-only mode.
- When this variable is enabled, TiDB handles the uncommitted transactions in the following ways:
    - For uncommitted read-only transactions, you can commit the transactions normally.
    - For uncommitted transactions that are not read-only, SQL statements that perform write operations in these transactions are rejected.
    - For uncommitted read-only transactions with modified data, the commit of these transactions is rejected.
- After the read-only mode is enabled, all users (including the users with the `SUPER` privilege) cannot execute the SQL statements that might write data unless the user is explicitly granted the `RESTRICTED_REPLICA_WRITER_ADMIN` privilege.
