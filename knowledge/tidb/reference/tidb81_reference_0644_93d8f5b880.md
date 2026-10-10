# SHOW BUILTINS syntax, example output, and MySQL compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-builtins.md`
- Source Title: `SHOW BUILTINS`
- Source Heading Path: `SHOW BUILTINS | SHOW BUILTINS > Synopsis | SHOW BUILTINS > Examples | SHOW BUILTINS > MySQL compatibility`
- Source Line Ranges: `5-302`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `show builtins`, `builtin functions`, `sql syntax`, `examples`, `mysql compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0644_93d8f5b880`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-builtins.md#show-builtins`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b8ccaefa48286d2421439b76d12520c9adca1b2a28e10bb8313938349e04d52e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-builtins#show-builtins
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-builtins.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the syntax or example output for listing all supported builtin functions in TiDB, or asks whether SHOW BUILTINS is compatible with MySQL syntax.
- Retrieval Keywords: SHOW BUILTINS, ShowBuiltinsStmt, SHOW BUILTINS syntax, list all supported builtin functions in TiDB, Supported_builtin_functions, SHOW BUILTINS;, TiDB extension to MySQL syntax, MySQL compatibility, builtin functions, sql statement
- Follow-up Guidance: The source includes the synopsis "SHOW BUILTINS", an example using "SHOW BUILTINS;", and example output under the "Supported_builtin_functions" column.
- Classification Note: This is reference content because it defines the SHOW BUILTINS statement syntax, shows example output, and states its MySQL compatibility status.

## Official Source Content

# SHOW BUILTINS

`SHOW BUILTINS` is used to list all supported builtin functions in TiDB.
## Synopsis

```ebnf+diagram
ShowBuiltinsStmt ::=
    "SHOW" "BUILTINS"
```
## Examples

```sql
SHOW BUILTINS;
```
```
+-----------------------------+
| Supported_builtin_functions |
+-----------------------------+
| abs                         |
| acos                        |
| adddate                     |
| addtime                     |
| aes_decrypt                 |
| aes_encrypt                 |
| and                         |
| any_value                   |
| ascii                       |
| asin                        |
| atan                        |
| atan2                       |
| benchmark                   |
| bin                         |
| bit_count                   |
| bit_length                  |
| bitand                      |
| bitneg                      |
| bitor                       |
| bitxor                      |
| case                        |
| ceil                        |
| ceiling                     |
| char_func                   |
| char_length                 |
| character_length            |
| charset                     |
| coalesce                    |
| coercibility                |
| collation                   |
| compress                    |
| concat                      |
| concat_ws                   |
| connection_id               |
| conv                        |
| convert                     |
| convert_tz                  |
| cos                         |
| cot                         |
| crc32                       |
| curdate                     |
| current_date                |
| current_role                |
| current_time                |
| current_timestamp           |
| current_user                |
| curtime                     |
| database                    |
| date                        |
| date_add                    |
| date_format                 |
| date_sub                    |
| datediff                    |
| day                         |
| dayname                     |
| dayofmonth                  |
| dayofweek                   |
| dayofyear                   |
| decode                      |
| default_func                |
| degrees                     |
| des_decrypt                 |
| des_encrypt                 |
| div                         |
| elt                         |
| encode                      |
| encrypt                     |
| eq                          |
| exp                         |
| export_set                  |
| extract                     |
| field                       |
| find_in_set                 |
| floor                       |
| format                      |
| format_bytes                |
| format_nano_time            |
| found_rows                  |
| from_base64                 |
| from_days                   |
| from_unixtime               |
| ge                          |
| get_format                  |
| get_lock                    |
| getparam                    |
| getvar                      |
| greatest                    |
| gt                          |
| hex                         |
| hour                        |
| if                          |
| ifnull                      |
| in                          |
| inet6_aton                  |
| inet6_ntoa                  |
| inet_aton                   |
| inet_ntoa                   |
| insert_func                 |
| instr                       |
| intdiv                      |
| interval                    |
| is_free_lock                |
| is_ipv4                     |
| is_ipv4_compat              |
| is_ipv4_mapped              |
| is_ipv6                     |
| is_used_lock                |
| isfalse                     |
| isnull                      |
| istrue                      |
| json_array                  |
| json_array_append           |
| json_array_insert           |
| json_contains               |
| json_contains_path          |
| json_depth                  |
| json_extract                |
| json_insert                 |
| json_keys                   |
| json_length                 |
| json_merge                  |
| json_merge_patch            |
| json_merge_preserve         |
| json_object                 |
| json_pretty                 |
| json_quote                  |
| json_remove                 |
| json_replace                |
| json_search                 |
| json_set                    |
| json_storage_size           |
| json_type                   |
| json_unquote                |
| json_valid                  |
| last_day                    |
| last_insert_id              |
| lastval                     |
| lcase                       |
| le                          |
| least                       |
| left                        |
| leftshift                   |
| length                      |
| like                        |
| ln                          |
| load_file                   |
| localtime                   |
| localtimestamp              |
| locate                      |
| log                         |
| log10                       |
| log2                        |
| lower                       |
| lpad                        |
| lt                          |
| ltrim                       |
| make_set                    |
| makedate                    |
| maketime                    |
| master_pos_wait             |
| md5                         |
| microsecond                 |
| mid                         |
| minus                       |
| minute                      |
| mod                         |
| month                       |
| monthname                   |
| mul                         |
| name_const                  |
| ne                          |
| nextval                     |
| not                         |
| now                         |
| nulleq                      |
| oct                         |
| octet_length                |
| old_password                |
| or                          |
| ord                         |
| password_func               |
| period_add                  |
| period_diff                 |
| pi                          |
| plus                        |
| position                    |
| pow                         |
| power                       |
| quarter                     |
| quote                       |
| radians                     |
| rand                        |
| random_bytes                |
| regexp                      |
| release_all_locks           |
| release_lock                |
| repeat                      |
| replace                     |
| reverse                     |
| right                       |
| rightshift                  |
| round                       |
| row_count                   |
| rpad                        |
| rtrim                       |
| schema                      |
| sec_to_time                 |
| second                      |
| session_user                |
| setval                      |
| setvar                      |
| sha                         |
| sha1                        |
| sha2                        |
| sign                        |
| sin                         |
| sleep                       |
| sm3                         |
| space                       |
| sqrt                        |
| str_to_date                 |
| strcmp                      |
| subdate                     |
| substr                      |
| substring                   |
| substring_index             |
| subtime                     |
| sysdate                     |
| system_user                 |
| tan                         |
| tidb_decode_key             |
| tidb_decode_plan            |
| tidb_is_ddl_owner           |
| tidb_parse_tso              |
| tidb_version                |
| time                        |
| time_format                 |
| time_to_sec                 |
| timediff                    |
| timestamp                   |
| timestampadd                |
| timestampdiff               |
| to_base64                   |
| to_days                     |
| to_seconds                  |
| trim                        |
| truncate                    |
| ucase                       |
| unaryminus                  |
| uncompress                  |
| uncompressed_length         |
| unhex                       |
| unix_timestamp              |
| upper                       |
| user                        |
| utc_date                    |
| utc_time                    |
| utc_timestamp               |
| uuid                        |
| uuid_short                  |
| validate_password_strength  |
| version                     |
| week                        |
| weekday                     |
| weekofyear                  |
| weight_string               |
| xor                         |
| year                        |
| yearweek                    |
+-----------------------------+
268 rows in set (0.00 sec)
```

## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
