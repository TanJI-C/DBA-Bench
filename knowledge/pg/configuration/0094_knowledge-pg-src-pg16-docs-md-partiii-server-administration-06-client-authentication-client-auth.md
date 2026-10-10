# Password Authentication

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/06_client_authentication.md`
- Source Title: `Client Authentication`
- Source Heading Path: `Client Authentication > Password Authentication`
- Source Line Ranges: `860-942`
- Chunk ID: `pg16_configuration_0094_4cfd6c74ee`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d7a44be821d11cdc296b9c6fcc5609366f87e6bea449e4ff071d28e4aea7424b`

## Retrieval Guidance

- Use When: 配置或迁移 PostgreSQL 密码认证。
- Retrieval Keywords: scram-sha-256, md5, password authentication, password_encryption, pg_authid, ALTER ROLE PASSWORD, \password, SCRAM upgrade
- Follow-up Guidance: 升级到 SCRAM 前确认所有客户端库支持 SCRAM，并要求用户重设密码。
- Classification Note: 定义 scram-sha-256、md5、password 方法、存储 hash、password_encryption 和 md5 到 SCRAM 升级路径。

## Official Source Content

## Password Authentication

There are several password-based authentication methods.  These methods
operate similarly but differ in how the users' passwords are stored on the
server and how the password provided by a client is sent across the
connection.

**`scram-sha-256`**
: The method `scram-sha-256` performs SCRAM-SHA-256
authentication, as described in
[RFC 7677](https://datatracker.ietf.org/doc/html/rfc7677).  It
is a challenge-response scheme that prevents password sniffing on
untrusted connections and supports storing passwords on the server in a
cryptographically hashed form that is thought to be secure.

This is the most secure of the currently provided methods, but it is
not supported by older client libraries.

**`md5`**
: The method `md5` uses a custom less secure challenge-response
mechanism.  It prevents password sniffing and avoids storing passwords
on the server in plain text but provides no protection if an attacker
manages to steal the password hash from the server.  Also, the MD5 hash
algorithm is nowadays no longer considered secure against determined
attacks.

The `md5` method cannot be used with
the [guc-db-user-namespace](#guc-db-user-namespace) feature.

To ease transition from the `md5` method to the newer
SCRAM method, if `md5` is specified as a method
in `pg_hba.conf` but the user's password on the
server is encrypted for SCRAM (see below), then SCRAM-based
authentication will automatically be chosen instead.

**`password`**
: The method `password` sends the password in clear-text and is
therefore vulnerable to password "sniffing" attacks. It should
always be avoided if possible. If the connection is protected by SSL
encryption then `password` can be used safely, though.
(Though SSL certificate authentication might be a better choice if one
is depending on using SSL).

PostgreSQL database passwords are
separate from operating system user passwords. The password for
each database user is stored in the `pg_authid` system
catalog. Passwords can be managed with the SQL commands
[sql-createrole](#sql-createrole) and
[sql-alterrole](#sql-alterrole),
e.g., CREATE ROLE foo WITH LOGIN PASSWORD 'secret',
or the psql
command `\password`.
If no password has been set up for a user, the stored password
is null and password authentication will always fail for that user.

The availability of the different password-based authentication methods
depends on how a user's password on the server is encrypted (or hashed,
more accurately).  This is controlled by the configuration
parameter [guc-password-encryption](#guc-password-encryption) at the time the
password is set.  If a password was encrypted using
the `scram-sha-256` setting, then it can be used for the
authentication methods `scram-sha-256`
and `password` (but password transmission will be in
plain text in the latter case).  The authentication method
specification `md5` will automatically switch to using
the `scram-sha-256` method in this case, as explained
above, so it will also work.  If a password was encrypted using
the `md5` setting, then it can be used only for
the `md5` and `password` authentication
method specifications (again, with the password transmitted in plain text
in the latter case).  (Previous PostgreSQL releases supported storing the
password on the server in plain text.  This is no longer possible.)  To
check the currently stored password hashes, see the system
catalog `pg_authid`.

To upgrade an existing installation from `md5`
to `scram-sha-256`, after having ensured that all client
libraries in use are new enough to support SCRAM,
set `password_encryption = 'scram-sha-256'`
in `postgresql.conf`, make all users set new passwords,
and change the authentication method specifications
in `pg_hba.conf` to `scram-sha-256`.
