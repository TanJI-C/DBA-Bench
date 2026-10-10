# tidb_auth_token JWT format and self-managed usage

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/security-compatibility-with-mysql.md`
- Source Title: `Security Compatibility with MySQL`
- Source Heading Path: `Security Compatibility with MySQL > Authentication plugin status > `tidb_auth_token` > JWT | Security Compatibility with MySQL > Authentication plugin status > `tidb_auth_token` > Usage`
- Source Line Ranges: `147-260`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`, `sql`
- Topic Tags: `authentication`, `jwt`, `jwks`, `tls`, `mysql_clear_password`, `user-creation`, `token-issuer`, `email-claim`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0147_6daf1a8e7c`
- Source ID: `tidb-docs-8.1:security-compatibility-with-mysql.md#jwt`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fb58ed7b0fc8c1254264a614e26f6fd8956023d068a4b262d6374875475bc4a8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/security-compatibility-with-mysql#jwt
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/security-compatibility-with-mysql.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about the `tidb_auth_token` JWT claim requirements, JWKS configuration, TLS and `mysql_clear_password` prerequisites, or how self-managed TiDB users authenticate with a JWT token.
- Retrieval Keywords: tidb_auth_token, JWT, JWKS, auth-token-jwks, auth-token-refresh-interval, mysql_clear_password, enable TLS between clients and servers, CREATE USER, REQUIRE TOKEN_ISSUER, ATTRIBUTE '{"email": "xxxx@pingcap.com"}', iss, sub, iat, exp, email, kid, alg, RS256, typ, tidb-server, config.toml, mycli, mysql --enable-cleartext-plugin, wronguser@pingcap.com, jwt.io
- Follow-up Guidance: The content includes an example `CREATE USER 'user@pingcap.com' IDENTIFIED WITH 'tidb_auth_token' REQUIRE TOKEN_ISSUER 'issuer-abc' ATTRIBUTE '{"email": "user@pingcap.com"}'`, an example `generate_jwt` command, and example login commands for `mycli` and `mysql --enable-cleartext-plugin`.
- Classification Note: This is classified as self-managed TiDB configuration content because it explains `tidb_auth_token` setup in the TiDB configuration file, required JWT claims, and the client authentication flow using `mysql_clear_password` and TLS.

## Official Source Content

#### JWT

JWT consists of three parts: Header, Payload, and Signature. After being encoded using base64, they are concatenated into a string separated by dots (`.`) for transmission between the client and server.

The Header describes the metadata of the JWT, including 3 parameters:

* `alg`: the algorithm for signature, which is `RS256` by default.
* `typ`: the type of token, which is `JWT`.
* `kid`: the key ID for generating token signature.

Here is an example for Header:

```json
{
  "alg": "RS256",
  "kid": "the-key-id-0",
  "typ": "JWT"
}
```

Payload is the main part of JWT, which stores the user information. Each field in the Payload is called a claim. The claims required for TiDB user authentication are as follows:

* `iss`: if `TOKEN_ISSUER` is not specified or set to empty when [`CREATE USER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-user), this claim is not required; otherwise, `iss` should use the same value as `TOKEN_ISSUER`.
* `sub`: this claim is required to be the same as the username to be authenticated.
* `iat`: it means `issued at`, the timestamp when the token is issued. In TiDB, this value must not be later than the authentication time or earlier than 15 minutes before authentication.
* `exp`: the timestamp when the token expires. If it is earlier than the time of authentication, the authentication fails.
* `email`: the email can be specified when creating a user by `ATTRIBUTE '{"email": "xxxx@pingcap.com"}`. If no email is specified when a user is created, this claim must be set as an empty string; otherwise, this claim must be the same as the specified value when the user is created.

Here is an example for Payload:

```json
{
  "email": "user@pingcap.com",
  "exp": 1703305494,
  "iat": 1703304594,
  "iss": "issuer-abc",
  "sub": "user@pingcap.com"
}
```

Signature is used to sign the Header and Payload data.

> **Warning:**
>
> - The encoding of the Header and Payload in base64 is reversible. Do **Not** attach any sensitive information to them.
> - The `tidb_auth_token` authentication method requires clients to support the [`mysql_clear_password`](https://dev.mysql.com/doc/refman/8.0/en/cleartext-pluggable-authentication.html) plugin to send the token to TiDB in plain text. Therefore, you need to [enable TLS between clients and servers](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers) before using `tidb_auth_token`.
#### Usage

To configure and use `tidb_auth_token` as the authentication method for TiDB Self-Managed users, take the following steps:

1. Configure [`auth-token-jwks`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#auth-token-jwks-new-in-v640) and [`auth-token-refresh-interval`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#auth-token-refresh-interval-new-in-v640) in the TiDB configuration file.

    For example, you can get an example JWKS using the following command:
    
    ```bash
    wget https://raw.githubusercontent.com/CbcWestwolf/generate_jwt/master/JWKS.json
    ```

    Then, configure the path of the example JWKS in `config.toml`:

    ```toml
    [security]
    auth-token-jwks = "JWKS.json"
    ```

2. Start `tidb-server` and periodically update and save the JWKS to the path specified by `auth-token-jwks`.

3. Create a user with `tidb_auth_token`, and specify `iss` and `email` as needed using `REQUIRE TOKEN_ISSUER` and `ATTRIBUTE '{"email": "xxxx@pingcap.com"}`.

    For example, create a user `user@pingcap.com` with `tidb_auth_token`:

    ```sql
    CREATE USER 'user@pingcap.com' IDENTIFIED WITH 'tidb_auth_token' REQUIRE TOKEN_ISSUER 'issuer-abc' ATTRIBUTE '{"email": "user@pingcap.com"}';
    ```

4. Generate and sign a token for authentication, and authenticate using the `mysql_clear_text` plugin of the MySQL client.

    Install the JWT generation tool via `go install github.com/cbcwestwolf/generate_jwt` (this tool is only used for testing `tidb_auth_token`). For example:

    ```text
    generate_jwt --kid "the-key-id-0" --sub "user@pingcap.com" --email "user@pingcap.com" --iss "issuer-abc"
    ```

    It prints the public key and token as follows:

    ```text
    -----BEGIN PUBLIC KEY-----
    MIIBCgKCAQEAq8G5n9XBidxmBMVJKLOBsmdOHrCqGf17y9+VUXingwDUZxRp2Xbu
    LZLbJtLgcln1lC0L9BsogrWf7+pDhAzWovO6Ai4Aybu00tJ2u0g4j1aLiDdsy0gy
    vSb5FBoL08jFIH7t/JzMt4JpF487AjzvITwZZcnsrB9a9sdn2E5B/aZmpDGi2+Is
    f5osnlw0zvveTwiMo9ba416VIzjntAVEvqMFHK7vyHqXbfqUPAyhjLO+iee99Tg5
    AlGfjo1s6FjeML4xX7sAMGEy8FVBWNfpRU7ryTWoSn2adzyA/FVmtBvJNQBCMrrA
    hXDTMJ5FNi8zHhvzyBKHU0kBTS1UNUbP9wIDAQAB
    -----END PUBLIC KEY-----

    eyJhbGciOiJSUzI1NiIsImtpZCI6InRoZS1rZXktaWQtMCIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InVzZXJAcGluZ2NhcC5jb20iLCJleHAiOjE3MDMzMDU0OTQsImlhdCI6MTcwMzMwNDU5NCwiaXNzIjoiaXNzdWVyLWFiYyIsInN1YiI6InVzZXJAcGluZ2NhcC5jb20ifQ.T4QPh2hTB5on5xCuvtWiZiDTuuKvckggNHtNaovm1F4RvwUv15GyOqj9yMstE-wSoV5eLEcPC2HgE6eN1C6yH_f4CU-A6n3dm9F1w-oLbjts7aYCl8OHycVYnq609fNnb8JLsQAmd1Zn9C0JW899-WSOQtvjLqVSPe9prH-cWaBVDQXzUJKxwywQzk9v-Z1Njt9H3Rn9vvwwJEEPI16VnaNK38I7YG-1LN4fAG9jZ6Zwvz7vb_s4TW7xccFf3dIhWTEwOQ5jDPCeYkwraRXU8NC6DPF_duSrYJc7d7Nu9Z2cr-E4i1Rt_IiRTuIIzzKlcQGg7jd9AGEfGe_SowsA-w
    ```

    Copy the preceding token in the last line for login:

    ```Shell
    mycli -h 127.0.0.1 -P 4000 -u 'user@pingcap.com' -p '<the-token-generated>'
    ```

    Ensure that the MySQL client here supports the `mysql_clear_password` plugin. [mycli](https://www.mycli.net/) supports and enables this plugin by default. If you are using the [mysql command-line client](https://dev.mysql.com/doc/refman/8.0/en/mysql.html), you need to use the `--enable-cleartext-plugin` option to enable this plugin:

    ```Shell
    mysql -h 127.0.0.1 -P 4000 -u 'user@pingcap.com' -p'<the-token-generated>' --enable-cleartext-plugin
    ```

    If an incorrect `--sub` is specified when the token is generated (such as `--sub "wronguser@pingcap.com"`), the authentication using this token would fail.

You can encode and decode a token using the debugger provided by [jwt.io](https://jwt.io/).
