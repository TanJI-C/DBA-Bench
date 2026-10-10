# Password strength validation function

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/encryption-and-compression-functions.md`
- Source Title: `Encryption and Compression Functions`
- Source Heading Path: `Encryption and Compression Functions > Supported functions > [`VALIDATE_PASSWORD_STRENGTH()`](https://dev.mysql.com/doc/refman/8.0/en/encryption-functions.html#function_validate-password-strength)`
- Source Line Ranges: `284-419`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `password-management`, `password-strength`, `system-variables`, `validate-password`, `sql-functions`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0303_5bd641b3e0`
- Source ID: `tidb-docs-8.1:functions-and-operators/encryption-and-compression-functions.md#validate-password-strength-https-dev-mysql-com-doc-refman-8-0-en-encryption-functions-html-function-validate-password-strength`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e7a66f9428e6e78bcd8ccb6cab51f94f88bd1130d6ead89ad636f1b563b84e6e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/encryption-and-compression-functions#validate-password-strength-https-dev-mysql-com-doc-refman-8-0-en-encryption-functions-html-function-validate-password-strength
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/encryption-and-compression-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking up `VALIDATE_PASSWORD_STRENGTH()` behavior, its 0 to 100 return values, and the `validate_password.*` system variables that affect it.
- Retrieval Keywords: VALIDATE_PASSWORD_STRENGTH(), VALIDATE_PASSWORD_STRENGTH(str), password management, returns a value between 0 and 100, validate_password.*, validate_password.enable, SHOW VARIABLES LIKE 'validate_password.%', SET GLOBAL validate_password.enable=ON, validate_password.length, validate_password.policy, validate_password.mixed_case_count, validate_password.number_count, validate_password.special_char_count, validate_password.check_user_name, validate_password.dictionary
- Follow-up Guidance: The examples include checking `VALIDATE_PASSWORD_STRENGTH('')`, `VALIDATE_PASSWORD_STRENGTH('abcdef')`, `VALIDATE_PASSWORD_STRENGTH('abcdefghi')`, `VALIDATE_PASSWORD_STRENGTH('Abcdefghi')`, `VALIDATE_PASSWORD_STRENGTH('Abcdefghi123')`, and `VALIDATE_PASSWORD_STRENGTH('Abcdefghi123%$#')`, along with viewing related variables using `SHOW VARIABLES LIKE 'validate_password.%'`.
- Classification Note: This is reference content because it documents a SQL function used in password management, the related system variables, and concrete example queries with returned strength values.

## Official Source Content

### [`VALIDATE_PASSWORD_STRENGTH()`](https://dev.mysql.com/doc/refman/8.0/en/encryption-functions.html#function_validate-password-strength)

The `VALIDATE_PASSWORD_STRENGTH(str)` function is used as part of [password management](https://docs.pingcap.com/tidb/stable/password-management). It calculates the strength of a password and returns a value between 0 and 100.

The `VALIDATE_PASSWORD_STRENGTH(str)` function is used as part of password management. It calculates the strength of a password and returns a value between 0 and 100.

The [`validate_password.*`](https://docs.pingcap.com/tidb/stable/system-variables) system variables affect the behavior of the `VALIDATE_PASSWORD_STRENGTH()` function.

Examples:

- To enable the password complexity check, set the [`validate_password.enable`](https://docs.pingcap.com/tidb/stable/system-variables#validate_passwordenable-new-in-v650) system variable to `ON`:

    ```sql
    SET GLOBAL validate_password.enable=ON;
    ```

- View password validation-related system variables:

    ```sql
    SHOW VARIABLES LIKE 'validate_password.%';
    ```

    ```
    +--------------------------------------+--------+
    | Variable_name                        | Value  |
    +--------------------------------------+--------+
    | validate_password.check_user_name    | ON     |
    | validate_password.dictionary         |        |
    | validate_password.enable             | ON     |
    | validate_password.length             | 8      |
    | validate_password.mixed_case_count   | 1      |
    | validate_password.number_count       | 1      |
    | validate_password.policy             | MEDIUM |
    | validate_password.special_char_count | 1      |
    +--------------------------------------+--------+
    8 rows in set (0.01 sec)
    ```

- Check the password strength of an empty string, which returns `0`:

    ```sql
    SELECT VALIDATE_PASSWORD_STRENGTH('');
    ```

    ```
    +--------------------------------+
    | VALIDATE_PASSWORD_STRENGTH('') |
    +--------------------------------+
    |                              0 |
    +--------------------------------+
    1 row in set (0.00 sec)
    ```

- Check the password strength of a short string `abcdef`, which returns `25`:

    ```sql
    SELECT VALIDATE_PASSWORD_STRENGTH('abcdef');
    ```

    ```
    +--------------------------------------+
    | VALIDATE_PASSWORD_STRENGTH('abcdef') |
    +--------------------------------------+
    |                                   25 |
    +--------------------------------------+
    1 row in set (0.00 sec)
    ```

- Check the password strength of a longer string `abcdefghi`, which returns `50`. This string is longer than the default value of [`validate_password.length`](https://docs.pingcap.com/tidb/stable/system-variables#validate_passwordlength-new-in-v650):

    ```sql
    SELECT VALIDATE_PASSWORD_STRENGTH('abcdefghi');
    ```

    ```
    +-----------------------------------------+
    | VALIDATE_PASSWORD_STRENGTH('abcdefghi') |
    +-----------------------------------------+
    |                                      50 |
    +-----------------------------------------+
    1 row in set (0.00 sec)
    ```

- Adding an upper-case character to the string does not improve the password strength:

    ```sql
    SELECT VALIDATE_PASSWORD_STRENGTH('Abcdefghi');
    ```

    ```
    +-----------------------------------------+
    | VALIDATE_PASSWORD_STRENGTH('Abcdefghi') |
    +-----------------------------------------+
    |                                      50 |
    +-----------------------------------------+
    1 row in set (0.01 sec)
    ```

- Adding numbers to the string also does not improve the password strength:

    ```sql
    SELECT VALIDATE_PASSWORD_STRENGTH('Abcdefghi123');
    ```

    ```
    +--------------------------------------------+
    | VALIDATE_PASSWORD_STRENGTH('Abcdefghi123') |
    +--------------------------------------------+
    |                                         50 |
    +--------------------------------------------+
    1 row in set (0.00 sec)
    ```

- Finally, adding special characters to the string brings the password strength to `100`, indicating a strong password:

    ```sql
    SELECT VALIDATE_PASSWORD_STRENGTH('Abcdefghi123%$#');
    ```

    ```
    +-----------------------------------------------+
    | VALIDATE_PASSWORD_STRENGTH('Abcdefghi123%$#') |
    +-----------------------------------------------+
    |                                           100 |
    +-----------------------------------------------+
    1 row in set (0.00 sec)
    ```
