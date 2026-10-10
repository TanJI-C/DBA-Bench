# RADIUS Authentication

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/06_client_authentication.md`
- Source Title: `Client Authentication`
- Source Heading Path: `Client Authentication > RADIUS Authentication`
- Source Line Ranges: `1427-1496`
- Chunk ID: `pg16_configuration_0100_699d2854e6`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3eb83a04a0565b60777da04067211fdf6d6d2ce13a37a614e0c89989852bdc3a`

## Retrieval Guidance

- Use When: 需要把 PostgreSQL 密码验证委托给 RADIUS。
- Retrieval Keywords: RADIUS authentication, radiusservers, radiussecrets, radiusports, radiusidentifiers, Access Request, Access Accept, Access Reject
- Follow-up Guidance: 无 OpenSSL 构建时 RADIUS 传输仅混淆，应另加外部保护。
- Classification Note: 定义 RADIUS server/secret/port/identifier、多服务器尝试和加密注意。

## Official Source Content

## RADIUS Authentication

This authentication method operates similarly to
`password` except that it uses RADIUS
as the password verification method. RADIUS is used only to validate
the user name/password pairs. Therefore the user must already
exist in the database before RADIUS can be used for
authentication.

When using RADIUS authentication, an Access Request message will be sent
to the configured RADIUS server. This request will be of type
`Authenticate Only`, and include parameters for
`user name`, `password` (encrypted) and
`NAS Identifier`. The request will be encrypted using
a secret shared with the server. The RADIUS server will respond to
this request with either `Access Accept` or
`Access Reject`. There is no support for RADIUS accounting.

Multiple RADIUS servers can be specified, in which case they will
be tried sequentially. If a negative response is received from
a server, the authentication will fail. If no response is received,
the next server in the list will be tried. To specify multiple
servers, separate the server names with commas and surround the list
with double quotes. If multiple servers are specified, the other
RADIUS options can also be given as comma-separated lists, to provide
individual values for each server. They can also be specified as
a single value, in which case that value will apply to all servers.

The following configuration options are supported for RADIUS:

**`radiusservers`**
: The DNS names or IP addresses of the RADIUS servers to connect to.
This parameter is required.

**`radiussecrets`**
: The shared secrets used when talking securely to the RADIUS
servers. This must have exactly the same value on the PostgreSQL
and RADIUS servers. It is recommended that this be a string of
at least 16 characters. This parameter is required.

> **Note:**
> The encryption vector used will only be cryptographically
> strong if PostgreSQL is built with support for
> OpenSSL. In other cases, the transmission to the
> RADIUS server should only be considered obfuscated, not secured, and
> external security measures should be applied if necessary.
>

**`radiusports`**
: The port numbers to connect to on the RADIUS servers. If no port
is specified, the default RADIUS port (`1812`)
will be used.

**`radiusidentifiers`**
: The strings to be used as `NAS Identifier` in the
RADIUS requests. This parameter can be used, for example, to
identify which database cluster the user is attempting to connect
to, which can be useful for policy matching on
the RADIUS server. If no identifier is specified, the default
`postgresql` will be used.

If it is necessary to have a comma or whitespace in a RADIUS parameter
value, that can be done by putting double quotes around the value, but
it is tedious because two layers of double-quoting are now required.
An example of putting whitespace into RADIUS secret strings is:

```
host ... radius radiusservers="server1,server2" radiussecrets="""secret one"",""secret two"""
```
