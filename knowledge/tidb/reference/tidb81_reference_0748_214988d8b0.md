# Password validation system variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > validate_password.check_user_name <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > validate_password.dictionary <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > validate_password.enable <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > validate_password.length <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > validate_password.mixed_case_count <span class="version-mark">New in v6.5.0</span>`
- Source Line Ranges: `6209-6266`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `sql`, `cloud`
- Topic Tags: `system-variables`, `password-validation`, `authentication`, `security`, `global-scope`, `complexity-policy`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0748_214988d8b0`
- Source ID: `tidb-docs-8.1:system-variables.md#validate-password-check-user-name-span-class-version-mark-new-in-v6-5-0-span`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8230adb9e7891bcc3b127c682287846993c653f84b80c3b703467b16e7193ede`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#validate-password-check-user-name-span-class-version-mark-new-in-v6-5-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks about global password validation variables, password complexity checks, dictionary matching, username matching, minimum length, or mixed-case requirements in TiDB.
- Retrieval Keywords: validate_password.check_user_name, validate_password.dictionary, validate_password.enable, validate_password.length, validate_password.mixed_case_count, password complexity check, validate_password.policy, STRONG, MEDIUM, password matches the username, dictionary check, minimum password length, uppercase and lowercase letters
- Follow-up Guidance: The content states that `validate_password.enable` is always enabled for Starter and Essential, and that `validate_password.length` can be automatically changed to match `validate_password.number_count + validate_password.special_char_count + (2 * validate_password.mixed_case_count)`.
- Classification Note: This is reference content because it lists the exact global password validation system variables with their defaults, ranges, dependencies, and how each check item affects password acceptance.

## Official Source Content

### validate_password.check_user_name New in v6.5.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `ON`
- Type: Boolean
- This variable is a check item in the password complexity check. It checks whether the password matches the username. This variable takes effect only when [`validate_password.enable`](#validate_passwordenable-new-in-v650) is enabled.
- When this variable is effective and set to `ON`, if you set a password, TiDB compares the password with the username (excluding the hostname). If the password matches the username, the password is rejected.
- This variable is independent of [`validate_password.policy`](#validate_passwordpolicy-new-in-v650) and not affected by the password complexity check level.
### validate_password.dictionary New in v6.5.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `""`
- Type: String
- This variable is a check item in the password complexity check. It checks whether the password matches the dictionary. This variable takes effect only when [`validate_password.enable`](#validate_passwordenable-new-in-v650) is enabled and [`validate_password.policy`](#validate_passwordpolicy-new-in-v650) is set to `2` (STRONG).
- This variable is a string not longer than 1024 characters. It contains a list of words that cannot exist in the password. Each word is separated by semicolon (`;`).
- This variable is set to an empty string by default, which means no dictionary check is performed. To perform the dictionary check, you need to include the words to be matched in the string. If this variable is configured, when you set a password, TiDB compares each substring (length in 4 to 100 characters) of the password with the words in the dictionary. If any substring of the password matches a word in the dictionary, the password is rejected. The comparison is case-insensitive.
### validate_password.enable New in v6.5.0

> **Note:**
>
> This variable is always enabled for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential).

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `OFF`
- Type: Boolean
- This variable controls whether to perform password complexity check. If this variable is set to `ON`, TiDB performs the password complexity check when you set a password.
### validate_password.length New in v6.5.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `8`
- Range: `[0, 2147483647]` for TiDB Self-Managed and [TiDB Cloud Dedicated](https://docs.pingcap.com/tidbcloud/select-cluster-tier#tidb-cloud-dedicated), `[8, 2147483647]` for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential)
- This variable is a check item in the password complexity check. It checks whether the password length is sufficient. By default, the minimum password length is `8`. This variable takes effect only when [`validate_password.enable`](#validate_passwordenable-new-in-v650) is enabled.
- The value of this variable must not be smaller than the expression: `validate_password.number_count + validate_password.special_char_count + (2 * validate_password.mixed_case_count)`.
- If you change the value of `validate_password.number_count`, `validate_password.special_char_count`, or `validate_password.mixed_case_count` such that the expression value is larger than `validate_password.length`, the value of `validate_password.length` is automatically changed to match the expression value.
### validate_password.mixed_case_count New in v6.5.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `1`
- Range: `[0, 2147483647]` for TiDB Self-Managed and [TiDB Cloud Dedicated](https://docs.pingcap.com/tidbcloud/select-cluster-tier#tidb-cloud-dedicated), `[1, 2147483647]` for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential)
- This variable is a check item in the password complexity check. It checks whether the password contains sufficient uppercase and lowercase letters. This variable takes effect only when [`validate_password.enable`](#validate_passwordenable-new-in-v650) is enabled and [`validate_password.policy`](#validate_passwordpolicy-new-in-v650) is set to `1` (MEDIUM) or larger.
- Neither the number of uppercase letters nor the number of lowercase letters in the password can be fewer than the value of `validate_password.mixed_case_count`. For example, when the variable is set to `1`, the password must contain at least one uppercase letter and one lowercase letter.
