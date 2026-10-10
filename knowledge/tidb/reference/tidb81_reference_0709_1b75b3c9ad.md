# System variable scopes and LDAP/authentication variable reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables | System Variables > Variable reference | System Variables > Variable reference > allow_auto_random_explicit_insert <span class="version-mark">New in v4.0.3</span> | System Variables > Variable reference > authentication_ldap_sasl_auth_method_name <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > authentication_ldap_sasl_bind_base_dn <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > authentication_ldap_sasl_bind_root_dn <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > authentication_ldap_sasl_bind_root_pwd <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > authentication_ldap_sasl_ca_path <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > authentication_ldap_sasl_init_pool_size <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > authentication_ldap_sasl_max_pool_size <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > authentication_ldap_sasl_server_host <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > authentication_ldap_sasl_server_port <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > authentication_ldap_sasl_tls <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > authentication_ldap_simple_auth_method_name <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > authentication_ldap_simple_bind_base_dn <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > authentication_ldap_simple_bind_root_dn <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > authentication_ldap_simple_bind_root_pwd <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > authentication_ldap_simple_ca_path <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > authentication_ldap_simple_init_pool_size <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > authentication_ldap_simple_max_pool_size <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > authentication_ldap_simple_server_host <span class="version-mark">New in v7.1.0</span>`
- Source Line Ranges: `5-231`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `system-variables`, `session-scope`, `global-scope`, `set-statement`, `set-var-hint`, `cluster-persistence`, `ldap`, `authentication`, `sasl`, `tls`, `connection-pool`, `auto-random`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0709_1b75b3c9ad`
- Source ID: `tidb-docs-8.1:system-variables.md#system-variables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `62e181f6aedb765d7c0c76f6882873aed6b4a2d8eb5f8bc5a586c948eb16c125`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#system-variables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variable scope behavior, SET or SET GLOBAL syntax, cluster persistence semantics, SET_VAR applicability, or the exact meanings and defaults of allow_auto_random_explicit_insert and LDAP authentication system variables.
- Retrieval Keywords: SESSION scope, GLOBAL scope, SET statement, SET SESSION tidb_distsql_scan_concurrency = 10, SET GLOBAL tidb_distsql_scan_concurrency = 10, Persists to cluster, Applies to hint SET_VAR, allow_auto_random_explicit_insert, AUTO_RANDOM, INSERT statement, authentication_ldap_sasl_auth_method_name, SCRAM-SHA-1, SCRAM-SHA-256, GSSAPI, authentication_ldap_sasl_bind_base_dn, authentication_ldap_sasl_bind_root_dn, authentication_ldap_sasl_bind_root_pwd, authentication_ldap_sasl_ca_path, authentication_ldap_sasl_init_pool_size, authentication_ldap_sasl_max_pool_size, authentication_ldap_sasl_server_host, authentication_ldap_sasl_server_port, authentication_ldap_sasl_tls, StartTLS, authentication_ldap_simple_auth_method_name, SIMPLE, authentication_ldap_simple_bind_base_dn, authentication_ldap_simple_bind_root_dn, authentication_ldap_simple_bind_root_pwd, authentication_ldap_simple_ca_path, authentication_ldap_simple_init_pool_size, authentication_ldap_simple_max_pool_size, authentication_ldap_simple_server_host, LDAP SASL authentication, LDAP simple authentication, connection pool, dn
- Follow-up Guidance: The chunk also states that some SESSION variables can be temporarily changed during statement execution using the SET_VAR hint and that variables are marked with whether SET_VAR applies.
- Classification Note: This is reference content because it enumerates system variables with their scope, persistence, SET_VAR applicability, type, default value, ranges, and exact LDAP authentication meanings.

## Official Source Content

# System Variables

TiDB system variables behave similar to MySQL, in that settings apply on a `SESSION` or `GLOBAL` scope:

- Changes on a `SESSION` scope will only affect the current session.
- Changes on a `GLOBAL` scope apply immediately. If this variable is also`SESSION` scoped, all sessions (including your session) will continue to use their current session value.
- Changes are made using the [`SET` statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-variable):

```sql
# These two identical statements change a session variable
SET tidb_distsql_scan_concurrency = 10;
SET SESSION tidb_distsql_scan_concurrency = 10;

# These two identical statements change a global variable
SET @@global.tidb_distsql_scan_concurrency = 10;
SET GLOBAL tidb_distsql_scan_concurrency = 10;
```

> **Note:**
>
> Several `GLOBAL` variables persist to the TiDB cluster. Some variables in this document have a `Persists to cluster` setting, which can be configured to `Yes` or `No`.
>
> - For variables with the `Persists to cluster: Yes` setting, when a global variable is changed, a notification is sent to all TiDB servers to refresh their system variable cache. When you add additional TiDB servers or restart existing TiDB servers, the persisted configuration value is automatically used.
> - For variables with the `Persists to cluster: No` setting, changes only apply to the local TiDB instance that you are connected to. To retain any values set, you need to specify the variables in your `tidb.toml` configuration file.
>
> Additionally, TiDB presents several MySQL variables as both readable and settable. This is required for compatibility, because it is common for both applications and connectors to read MySQL variables. For example, JDBC connectors both read and set query cache settings, despite not relying on the behavior.

> **Note:**
>
> Larger values do not always yield better performance. It is also important to consider the number of concurrent connections that are executing statements, because most settings apply to each connection.
>
> Consider the unit of a variable when you determine safe values:
>
> * For threads, safe values are typically up to the number of CPU cores.
> * For bytes, safe values are typically less than the amount of system memory.
> * For time, pay attention that the unit might be seconds or milliseconds.
>
> Variables using the same unit might compete for the same set of resources.

Starting from v7.4.0, you can temporarily modify the value of some `SESSION` variables during statement execution using [`SET_VAR`](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value). After the statement is executed, the value of the system variable in the current session is automatically changed back to the original value. This hint can be used to modify some system variables related to the optimizer and executor. Variables in this document have a `Applies to hint SET_VAR` setting, which can be configured to `Yes` or `No`.

- For variables with the `Applies to hint SET_VAR: Yes` setting, you can use the [`SET_VAR`](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value) hint to modify the value of the system variable in the current session during statement execution.
- For variables with the `Applies to hint SET_VAR: No` setting, you cannot use the [`SET_VAR`](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value) hint to modify the value of the system variable in the current session during statement execution.

For more information about the `SET_VAR` hint, see [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value).
## Variable reference
### allow_auto_random_explicit_insert New in v4.0.3

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- Determines whether to allow explicitly specifying the values of the column with the `AUTO_RANDOM` attribute in the `INSERT` statement.
### authentication_ldap_sasl_auth_method_name New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Enumeration
- Default value: `SCRAM-SHA-1`
- Possible values: `SCRAM-SHA-1`, `SCRAM-SHA-256`, and `GSSAPI`.
- For LDAP SASL authentication, this variable specifies the authentication method name.
### authentication_ldap_sasl_bind_base_dn New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: String
- Default value: ""
- For LDAP SASL authentication, this variable limits the search scope within the search tree. If a user is created without the `AS ...` clause, TiDB will automatically search the `dn` in LDAP server according to the user name.
### authentication_ldap_sasl_bind_root_dn New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: String
- Default value: ""
- For LDAP SASL authentication, this variable specifies the `dn` used to log in to the LDAP server to search users.
### authentication_ldap_sasl_bind_root_pwd New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: String
- Default value: ""
- For LDAP SASL authentication, this variable specifies the password used to log in to the LDAP server to search users.
### authentication_ldap_sasl_ca_path New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: String
- Default value: ""
- For LDAP SASL authentication, this variable specifies the absolute path of the certificate authority file for StartTLS connections.
### authentication_ldap_sasl_init_pool_size New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `10`
- Range: `[1, 32767]`
- For LDAP SASL authentication, this variable specifies the initial connections in the connection pool to the LDAP server.
### authentication_ldap_sasl_max_pool_size New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `1000`
- Range: `[1, 32767]`
- For LDAP SASL authentication, this variable specifies the maximum connections in the connection pool to the LDAP server.
### authentication_ldap_sasl_server_host New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: String
- Default value: ""
- For LDAP SASL authentication, this variable specifies the LDAP server host name or IP address.
### authentication_ldap_sasl_server_port New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `389`
- Range: `[1, 65535]`
- For LDAP SASL authentication, this variable specifies the TCP/IP port number of the LDAP server.
### authentication_ldap_sasl_tls New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- For LDAP SASL authentication, this variable controls whether connections by the plugin to the LDAP server are protected with StartTLS.
### authentication_ldap_simple_auth_method_name New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Enumeration
- Default value: `SIMPLE`
- Possible values: `SIMPLE`.
- For LDAP simple authentication, this variable specifies the authentication method name. The only supported value is `SIMPLE`.
### authentication_ldap_simple_bind_base_dn New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: String
- Default value: ""
- For LDAP simple authentication, this variable limits the search scope within the search tree. If a user is created without the `AS ...` clause, TiDB will automatically search the `dn` in LDAP server according to the user name.
### authentication_ldap_simple_bind_root_dn New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: String
- Default value: ""
- For LDAP simple authentication, this variable specifies the `dn` used to log in to the LDAP server to search users.
### authentication_ldap_simple_bind_root_pwd New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: String
- Default value: ""
- For LDAP simple authentication, this variable specifies the password used to log in to the LDAP server to search users.
### authentication_ldap_simple_ca_path New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: String
- Default value: ""
- For LDAP simple authentication, this variable specifies the absolute path of the certificate authority file for StartTLS connections.
### authentication_ldap_simple_init_pool_size New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `10`
- Range: `[1, 32767]`
- For LDAP simple authentication, this variable specifies the initial connections in the connection pool to the LDAP server.
### authentication_ldap_simple_max_pool_size New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `1000`
- Range: `[1, 32767]`
- For LDAP simple authentication, this variable specifies the maximum connections in the connection pool to the LDAP server.
### authentication_ldap_simple_server_host New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: String
- Default value: ""
- For LDAP simple authentication, this variable specifies the LDAP server host name or IP address.
