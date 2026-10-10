# Password validation, version reporting, session timeout, and window precision variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > validate_password.number_count <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > validate_password.policy <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > validate_password.special_char_count <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > version | System Variables > Variable reference > version_comment | System Variables > Variable reference > version_compile_machine | System Variables > Variable reference > version_compile_os | System Variables > Variable reference > wait_timeout | System Variables > Variable reference > warning_count | System Variables > Variable reference > windowing_use_high_precision`
- Source Line Ranges: `6267-6358`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `cloud`, `sql`
- Topic Tags: `system-variables`, `password-policy`, `password-complexity`, `version-info`, `session-timeout`, `warnings`, `window-functions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0749_a3b65c3278`
- Source ID: `tidb-docs-8.1:system-variables.md#validate-password-number-count-span-class-version-mark-new-in-v6-5-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3b49ae54bc1f1c39a1000d2a17db20689a2d1737554727fc53f6d9430639fe2f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#validate-password-number-count-span-class-version-mark-new-in-v6-5-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variables for password complexity policy and counts, version reporting fields, idle session timeout, warning count, or window function high precision behavior.
- Retrieval Keywords: validate_password.number_count, validate_password.policy, validate_password.special_char_count, validate_password.enable, validate_password.check_user_name, version, version_comment, version_compile_machine, version_compile_os, wait_timeout, warning_count, windowing_use_high_precision, password complexity check, LOW MEDIUM STRONG, idle timeout of user sessions, number of warnings that occurred in the statement that was previously executed, high precision mode when computing the window functions, 8.0.11-TiDB-v8.1.2
- Follow-up Guidance: The content states that validate_password.number_count and validate_password.special_char_count take effect only when validate_password.enable is enabled and validate_password.policy is set to 1 (MEDIUM) or larger, and that validate_password.policy determines which password complexity checks take effect except for validate_password.check_user_name.
- Classification Note: This is reference content because it defines TiDB system variables with their scope, type, default value, range or value options, and what each variable returns or controls.

## Official Source Content

### validate_password.number_count New in v6.5.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `1`
- Range: `[0, 2147483647]` for TiDB Self-Managed and [TiDB Cloud Dedicated](https://docs.pingcap.com/tidbcloud/select-cluster-tier#tidb-cloud-dedicated), `[1, 2147483647]` for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential)
- This variable is a check item in the password complexity check. It checks whether the password contains sufficient numbers. This variable takes effect only when [`validate_password.enable`](#password_reuse_interval-new-in-v650) is enabled and [`validate_password.policy`](#validate_passwordpolicy-new-in-v650) is set to `1` (MEDIUM) or larger.
### validate_password.policy New in v6.5.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Enumeration
- Default value: `1`
- Value options: `0`, `1`, and `2` for TiDB Self-Managed and [TiDB Cloud Dedicated](https://docs.pingcap.com/tidbcloud/select-cluster-tier#tidb-cloud-dedicated); `1` and `2` for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential)
- This variable controls the policy for the password complexity check. This variable takes effect only when [`validate_password.enable`](#password_reuse_interval-new-in-v650) is enabled. The value of this variable determines whether other `validate-password` variables take effect in the password complexity check, except for `validate_password.check_user_name`.
- This value of this variable can be `0`, `1`, or `2` (corresponds to LOW, MEDIUM, or STRONG). Different policy levels have different checks:
    - 0 or LOW: password length.
    - 1 or MEDIUM: password length, uppercase and lowercase letters, numbers, and special characters.
    - 2 or STRONG: password length, uppercase and lowercase letters, numbers, special characters, and dictionary match.
### validate_password.special_char_count New in v6.5.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `1`
- Range: `[0, 2147483647]` for TiDB Self-Managed and [TiDB Cloud Dedicated](https://docs.pingcap.com/tidbcloud/select-cluster-tier#tidb-cloud-dedicated), `[1, 2147483647]` for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential)
- This variable is a check item in the password complexity check. It checks whether the password contains sufficient special characters. This variable takes effect only when [`validate_password.enable`](#password_reuse_interval-new-in-v650) is enabled and [`validate_password.policy`](#validate_passwordpolicy-new-in-v650) is set to `1` (MEDIUM) or larger.
### version

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `8.0.11-TiDB-`(tidb version)
- This variable returns the MySQL version, followed by the TiDB version. For example '8.0.11-TiDB-v8.1.2'.
### version_comment

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: (string)
- This variable returns additional details about the TiDB version. For example, 'TiDB Server (Apache License 2.0) Community Edition, MySQL 8.0 compatible'.
### version_compile_machine

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: (string)
- This variable returns the name of the CPU architecture on which TiDB is running.
### version_compile_os

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: (string)
- This variable returns the name of the OS on which TiDB is running.
### wait_timeout

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `28800`
- Range: `[0, 31536000]`
- Unit: Seconds
- This variable controls the idle timeout of user sessions. A zero-value means unlimited.
### warning_count

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `0`
- This read-only variable indicates the number of warnings that occurred in the statement that was previously executed.
### windowing_use_high_precision

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable controls whether to use the high precision mode when computing the [window functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/window-functions).
