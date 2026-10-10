# Configure user certificate verification requirements for login

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/certificate-authentication.md`
- Source Title: `Certificate-Based Authentication for Login`
- Source Heading Path: `Certificate-Based Authentication for Login > Configure the user certificate information for login verification > Configure user certificate information`
- Source Line Ranges: `322-392`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `tls`, `ssl`, `certificate-authentication`, `user-management`, `login-verification`, `require-subject`, `require-issuer`, `require-san`, `require-cipher`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0015_78655f9524`
- Source ID: `tidb-docs-8.1:certificate-authentication.md#configure-user-certificate-information`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f9d0b420a6f78da3b6569e10f4ebef669288835a6082e875aa05195d1aa6cc1e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/certificate-authentication#configure-user-certificate-information
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/certificate-authentication.md

## Retrieval Guidance

- Use When: Use this chunk when searching how TiDB verifies client certificate attributes at login and how to set REQUIRE options on a user.
- Retrieval Keywords: CREATE USER REQUIRE ISSUER SUBJECT SAN CIPHER, ALTER USER REQUIRE ISSUER SUBJECT SAN CIPHER, REQUIRE SUBJECT, REQUIRE ISSUER, REQUIRE SAN, REQUIRE CIPHER, ERROR 1045 (28000): Access denied, SHOW VARIABLES LIKE '%ssl%';, \s, SSL: Cipher in use is TLS_AES_128_GCM_SHA256, ssl_ca, ssl_cert, ssl_key, have_ssl, have_openssl
- Follow-up Guidance: The source also shows using \s and SHOW VARIABLES LIKE '%ssl%'; to check the TLS version, cipher algorithm, and SSL-related variables for the current connection.
- Classification Note: This is classified as configuration because it defines SQL statements and login verification requirements for configuring certificate-based authentication on users.

## Official Source Content

### Configure user certificate information

After getting the user certificate information (`REQUIRE SUBJECT`, `REQUIRE ISSUER`, `REQUIRE SAN`, `REQUIRE CIPHER`), configure these information to be verified when creating a user, granting privileges, or altering a user. Replace `<replaceable>` with the corresponding information in the following statements.

You can configure one option or multiple options using the space or `and` as the separator.

+ Configure user certificate when creating a user (`CREATE USER`):

    ```sql
    CREATE USER 'u1'@'%' REQUIRE ISSUER '<replaceable>' SUBJECT '<replaceable>' SAN '<replaceable>' CIPHER '<replaceable>';
    ```

+ Configure user certificate when altering a user:

    ```sql
    ALTER USER 'u1'@'%' REQUIRE ISSUER '<replaceable>' SUBJECT '<replaceable>' SAN '<replaceable>' CIPHER '<replaceable>';
    ```

After the above configuration, the following items will be verified when you log in:

+ SSL is used; the CA that issues the client certificate is consistent with the CA configured in the server.
+ The `issuer` information of the client certificate matches the information specified in `REQUIRE ISSUER`.
+ The `subject` information of the client certificate matches the information specified in `REQUIRE CIPHER`.
+ The `Subject Alternative Name` information of the client certificate matches the information specified in `REQUIRE SAN`.

You can log into TiDB only after all the above items are verified. Otherwise, the `ERROR 1045 (28000): Access denied` error is returned. You can use the following command to check the TLS version, the cipher algorithm and whether the current connection uses the certificate for the login.

Connect the MySQL client and execute the following statement:

```sql
\s
```

The output:

```
--------------
mysql  Ver 8.3.0 for Linux on x86_64 (MySQL Community Server - GPL)

Connection id:       1
Current database:    test
Current user:        root@127.0.0.1
SSL:                 Cipher in use is TLS_AES_128_GCM_SHA256
```

Then execute the following statement:

```sql
SHOW VARIABLES LIKE '%ssl%';
```

The output:

```
+---------------+----------------------------------+
| Variable_name | Value                            |
+---------------+----------------------------------+
| have_openssl  | YES                              |
| have_ssl      | YES                              |
| ssl_ca        | /path/to/ca-cert.pem             |
| ssl_cert      | /path/to/server-cert.pem         |
| ssl_cipher    |                                  |
| ssl_key       | /path/to/server-key.pem          |
+---------------+----------------------------------+
6 rows in set (0.06 sec)
```
