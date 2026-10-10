# PAM Authentication

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/06_client_authentication.md`
- Source Title: `Client Authentication`
- Source Heading Path: `Client Authentication > PAM Authentication`
- Source Line Ranges: `1522-1556`
- Chunk ID: `pg16_configuration_0102_14c09ab47b`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2179b11a0276217111e54ffd2dd4e143f54020ce1e59dd959a82e23ee0126540`

## Retrieval Guidance

- Use When: 需要用 OS PAM 栈验证 PostgreSQL 用户密码。
- Retrieval Keywords: PAM authentication, pamservice, pam_use_hostname, PAM_RHOST, /etc/shadow
- Follow-up Guidance: 数据库 role 仍需存在；PAM 读取 /etc/shadow 可能因 postgres 非 root 失败。
- Classification Note: 定义 PAM service、pam_use_hostname、PAM_RHOST 以及非 root 读取 shadow 的失败风险。

## Official Source Content

## PAM Authentication

This authentication method operates similarly to
`password` except that it uses PAM (Pluggable
Authentication Modules) as the authentication mechanism. The
default PAM service name is `postgresql`.
PAM is used only to validate user name/password pairs and optionally the
connected remote host name or IP address. Therefore the user must already
exist in the database before PAM can be used for authentication.  For more
information about PAM, please read the
[
Linux-PAM Page](https://www.kernel.org/pub/linux/libs/pam/).

The following configuration options are supported for PAM:

**`pamservice`**
: PAM service name.

**`pam_use_hostname`**
: Determines whether the remote IP address or the host name is provided
to PAM modules through the `PAM_RHOST` item.  By
default, the IP address is used.  Set this option to 1 to use the
resolved host name instead.  Host name resolution can lead to login
delays.  (Most PAM configurations don't use this information, so it is
only necessary to consider this setting if a PAM configuration was
specifically created to make use of it.)

> **Note:**

> If PAM is set up to read `/etc/shadow`, authentication
> will fail because the PostgreSQL server is started by a non-root
> user.  However, this is not an issue when PAM is configured to use
> LDAP or other authentication methods.
>
