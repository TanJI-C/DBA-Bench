# Authentication, SQL defaults, charset/collation, and server variable reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > authentication_ldap_simple_server_port <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > authentication_ldap_simple_tls <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > auto_increment_increment | System Variables > Variable reference > auto_increment_offset | System Variables > Variable reference > autocommit | System Variables > Variable reference > block_encryption_mode | System Variables > Variable reference > character_set_client | System Variables > Variable reference > character_set_connection | System Variables > Variable reference > character_set_database | System Variables > Variable reference > character_set_results | System Variables > Variable reference > character_set_server | System Variables > Variable reference > collation_connection | System Variables > Variable reference > collation_database | System Variables > Variable reference > collation_server | System Variables > Variable reference > cte_max_recursion_depth | System Variables > Variable reference > datadir | System Variables > Variable reference > ddl_slow_threshold | System Variables > Variable reference > default_authentication_plugin`
- Source Line Ranges: `232-453`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `sql`, `shared`
- Topic Tags: `system-variables`, `ldap-authentication`, `auto-increment`, `auto-random`, `autocommit`, `encryption`, `character-set`, `collation`, `cte`, `datadir`, `ddl-logging`, `authentication-plugin`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0710_4eac3e429b`
- Source ID: `tidb-docs-8.1:system-variables.md#authentication-ldap-simple-server-port-span-class-version-mark-new-in-v7-1-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9e96393f18d8a59cc5a9f7b5e6a5b94e15c8b6c766dc5c276ea99a4ba3577e0b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#authentication-ldap-simple-server-port-span-class-version-mark-new-in-v7-1-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variable definitions for LDAP simple authentication settings, AUTO_INCREMENT or AUTO_RANDOM allocation behavior, autocommit, AES encryption mode, character set and collation defaults, CTE recursion depth, datadir meaning, DDL slow logging threshold, or the default authentication plugin.
- Retrieval Keywords: authentication_ldap_simple_server_port, authentication_ldap_simple_tls, auto_increment_increment, auto_increment_offset, AUTO_INCREMENT, AUTO_RANDOM, autocommit, block_encryption_mode, AES_ENCRYPT(), AES_DECRYPT(), character_set_client, character_set_connection, character_set_database, character_set_results, character_set_server, collation_connection, collation_database, collation_server, cte_max_recursion_depth, Common Table Expressions, datadir, ddl_slow_threshold, default_authentication_plugin, mysql_native_password, caching_sha2_password, tidb_sm3_password, tidb_auth_token, authentication_ldap_sasl, authentication_ldap_simple, SET NAMES, SET_VAR
- Follow-up Guidance: The content also points to Transaction Overview for autocommit, Character Set and Collation and SET NAMES for charset changes, and Authentication plugin status for more possible values of default_authentication_plugin.
- Classification Note: This is a reference chunk because it lists TiDB system variables with their scope, persistence, type, default value, range or possible values, and a short description of each variable.

## Official Source Content

### authentication_ldap_simple_server_port New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `389`
- Range: `[1, 65535]`
- For LDAP simple authentication, this variable specifies the TCP/IP port number of the LDAP server.
### authentication_ldap_simple_tls New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- For LDAP simple authentication, this variable controls whether connections by the plugin to the LDAP server are protected with StartTLS.
### auto_increment_increment

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `1`
- Range: `[1, 65535]`
- Controls the step size of `AUTO_INCREMENT` values to be allocated to a column, and allocation rules for `AUTO_RANDOM` IDs. It is often used in combination with [`auto_increment_offset`](#auto_increment_offset).
### auto_increment_offset

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `1`
- Range: `[1, 65535]`
- Controls the initial offset of `AUTO_INCREMENT` values to be allocated to a column, and allocation rules for `AUTO_RANDOM` IDs. This setting is often used in combination with [`auto_increment_increment`](#auto_increment_increment). For example:

```sql
mysql> CREATE TABLE t1 (a int not null primary key auto_increment);
Query OK, 0 rows affected (0.10 sec)

mysql> set auto_increment_offset=1;
Query OK, 0 rows affected (0.00 sec)

mysql> set auto_increment_increment=3;
Query OK, 0 rows affected (0.00 sec)

mysql> INSERT INTO t1 VALUES (),(),(),();
Query OK, 4 rows affected (0.04 sec)
Records: 4  Duplicates: 0  Warnings: 0

mysql> SELECT * FROM t1;
+----+
| a  |
+----+
|  1 |
|  4 |
|  7 |
| 10 |
+----+
4 rows in set (0.00 sec)
```
### autocommit

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- Controls whether statements should automatically commit when not in an explicit transaction. See [Transaction Overview](https://docs.pingcap.com/tidb/stable/transaction-overview#autocommit) for more information.
### block_encryption_mode

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Enumeration
- Default value: `aes-128-ecb`
- Value options: `aes-128-ecb`, `aes-192-ecb`, `aes-256-ecb`, `aes-128-cbc`, `aes-192-cbc`, `aes-256-cbc`, `aes-128-ofb`, `aes-192-ofb`, `aes-256-ofb`, `aes-128-cfb`, `aes-192-cfb`, `aes-256-cfb`
- This variable sets the encryption mode for the built-in functions [`AES_ENCRYPT()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/encryption-and-compression-functions#aes_encrypt) and [`AES_DECRYPT()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/encryption-and-compression-functions#aes_decrypt).
### character_set_client

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `utf8mb4`
- The character set for data sent from the client. See [Character Set and Collation](https://docs.pingcap.com/tidb/stable/character-set-and-collation) for details on the use of character sets and collations in TiDB. It is recommended to use [`SET NAMES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-names) to change the character set when needed.
### character_set_connection

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `utf8mb4`
- The character set for string literals that do not have a specified character set.
### character_set_database

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `utf8mb4`
- This variable indicates the character set of the default database in use. **It is NOT recommended to set this variable**. When a new default database is selected, the server changes the variable value.
### character_set_results

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `utf8mb4`
- The character set that is used when data is sent to the client.
### character_set_server

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `utf8mb4`
- The default character set for the server.
### collation_connection

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `utf8mb4_bin`
- This variable indicates the collation used in the current connection. It is consistent with the MySQL variable `collation_connection`.
### collation_database

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `utf8mb4_bin`
- This variable indicates the default collation of the database in use. **It is NOT recommended to set this variable**. When a new database is selected, TiDB changes this variable value.
### collation_server

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `utf8mb4_bin`
- The default collation used when the database is created.
### cte_max_recursion_depth

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `1000`
- Range: `[0, 4294967295]`
- Controls the maximum recursion depth in Common Table Expressions.
### datadir

> **Note:**
>
> This variable is not supported on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential).

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: it depends on the component and the deployment method.
    - `/tmp/tidb`: when you set `"unistore"` for [`--store`](https://docs.pingcap.com/tidb/stable/command-line-flags-for-tidb-configuration#--store) or if you don't set `--store`.
    - `${pd-ip}:${pd-port}`: when you use TiKV, which is the default storage engine for TiUP and TiDB Operator for Kubernetes deployments.
- This variable indicates the location where data is stored. This location can be a local path `/tmp/tidb`, or point to a PD server if the data is stored on TiKV. A value in the format of `${pd-ip}:${pd-port}` indicates the PD server that TiDB connects to on startup.

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: it depends on the component and the deployment method.
    - `/tmp/tidb`: when you set `"unistore"` for [`--store`](https://docs.pingcap.com/tidb/stable/command-line-flags-for-tidb-configuration#--store) or if you don't set `--store`.
    - `${pd-ip}:${pd-port}`: when you use TiKV, which is the default storage engine for TiUP and TiDB Operator for Kubernetes deployments.
- This variable indicates the location where data is stored. This location can be a local path `/tmp/tidb`, or point to a PD server if the data is stored on TiKV. A value in the format of `${pd-ip}:${pd-port}` indicates the PD server that TiDB connects to on startup.
### ddl_slow_threshold

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: GLOBAL
- Persists to cluster: No, only applicable to the current TiDB instance that you are connecting to.
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `300`
- Range: `[0, 2147483647]`
- Unit: Milliseconds
- Log DDL operations whose execution time exceeds the threshold value.
### default_authentication_plugin

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Enumeration
- Default value: `mysql_native_password`
- Possible values: `mysql_native_password`, `caching_sha2_password`, `tidb_sm3_password`, `tidb_auth_token`, `authentication_ldap_sasl`, and `authentication_ldap_simple`.
- This variable sets the authentication method that the server advertises when the server-client connection is being established.
- To authenticate using the `tidb_sm3_password` method, you can connect to TiDB using [TiDB-JDBC](https://github.com/pingcap/mysql-connector-j/tree/release/8.0-sm3).

For more possible values of this variable, see [Authentication plugin status](https://docs.pingcap.com/tidb/stable/security-compatibility-with-mysql#authentication-plugin-status).
