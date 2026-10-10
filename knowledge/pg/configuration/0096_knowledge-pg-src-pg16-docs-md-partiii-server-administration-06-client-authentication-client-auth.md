# SSPI Authentication

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/06_client_authentication.md`
- Source Title: `Client Authentication`
- Source Heading Path: `Client Authentication > SSPI Authentication`
- Source Line Ranges: `1064-1137`
- Chunk ID: `pg16_configuration_0096_7b1d9491f7`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c2b5760bf112236b7e9cb6c1e88bee1ef0ad64279a3b7116e7b1164e666e4d9e`

## Retrieval Guidance

- Use When: Windows 客户端/服务端需要集成域认证。
- Retrieval Keywords: SSPI, Windows authentication, negotiate, Kerberos, NTLM, compat_realm, upn_username
- Follow-up Guidance: 除非域账号条件满足，不要禁用 compat_realm。
- Classification Note: 定义 Windows SSPI/negotiate/Kerberos/NTLM 以及 include_realm、compat_realm、upn_username、map、krb_realm。

## Official Source Content

## SSPI Authentication

SSPI is a Windows
technology for secure authentication with single sign-on.
PostgreSQL will use SSPI in
`negotiate` mode, which will use
Kerberos when possible and automatically
fall back to NTLM in other cases.
SSPI and GSSAPI
interoperate as clients and servers, e.g., an
SSPI client can authenticate to an
GSSAPI server.  It is recommended to use
SSPI on Windows clients and servers and
GSSAPI on non-Windows platforms.

When using Kerberos authentication,
SSPI works the same way
GSSAPI does; see [gssapi-auth](#gssapi-auth)
for details.

The following configuration options are supported for SSPI:

**`include_realm`**
: If set to 0, the realm name from the authenticated user principal is
stripped off before being passed through the user name mapping
([auth-username-maps](#auth-username-maps)). This is discouraged and is
primarily available for backwards compatibility, as it is not secure
in multi-realm environments unless `krb_realm` is
also used.  It is recommended to
leave `include_realm` set to the default (1) and to
provide an explicit mapping in `pg_ident.conf` to convert
principal names to PostgreSQL user names.

**`compat_realm`**
: If set to 1, the domain's SAM-compatible name (also known as the
NetBIOS name) is used for the `include_realm`
option. This is the default. If set to 0, the true realm name from
the Kerberos user principal name is used.

Do not disable this option unless your server runs under a domain
account (this includes virtual service accounts on a domain member
system) and all clients authenticating through SSPI are also using
domain accounts, or authentication will fail.

**`upn_username`**
: If this option is enabled along with `compat_realm`,
the user name from the Kerberos UPN is used for authentication. If
it is disabled (the default), the SAM-compatible user name is used.
By default, these two names are identical for new user accounts.

Note that libpq uses the SAM-compatible name if no
explicit user name is specified. If you use
libpq or a driver based on it, you should
leave this option disabled or explicitly specify user name in the
connection string.

**`map`**
: Allows for mapping between system and database user names. See
[auth-username-maps](#auth-username-maps) for details.  For an SSPI/Kerberos
principal, such as `username@EXAMPLE.COM` (or, less
commonly, `username/hostbased@EXAMPLE.COM`), the
user name used for mapping is
`username@EXAMPLE.COM` (or
`username/hostbased@EXAMPLE.COM`, respectively),
unless `include_realm` has been set to 0, in which case
`username` (or `username/hostbased`)
is what is seen as the system user name when mapping.

**`krb_realm`**
: Sets the realm to match user principal names against. If this parameter
is set, only users of that realm will be accepted.  If it is not set,
users of any realm can connect, subject to whatever user name mapping
is done.
