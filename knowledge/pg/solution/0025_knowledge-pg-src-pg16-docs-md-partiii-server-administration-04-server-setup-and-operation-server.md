# Preventing Server Spoofing

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/04_server_setup_and_operation.md`
- Source Title: `Server Setup and Operation`
- Source Heading Path: `Server Setup and Operation > Preventing Server Spoofing`
- Source Line Ranges: `1410-1469`
- Chunk ID: `pg16_solution_0025_8370a0eab1`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4435c073a78ec454fe0270efe77ea30ade5e54cd4b4097356074dfc6f319b981`

## Retrieval Guidance

- Use When: 需要防止恶意本地或网络端点冒充 PostgreSQL server。
- Retrieval Keywords: server spoofing, Unix domain socket directory, requirepeer, sslmode verify-full, sslrootcert, channel_binding=require, hostssl, hostgssenc, gssencmode
- Follow-up Guidance: 客户端和服务端同时配置验证；仅加密但不验证证书不足以防 spoofing。
- Classification Note: 给出 local socket、requirepeer、SSL verify、GSSAPI、SCRAM channel_binding 等防伪服务器处置。

## Official Source Content

## Preventing Server Spoofing

While the server is running, it is not possible for a malicious user
to take the place of the normal database server.  However, when the
server is down, it is possible for a local user to spoof the normal
server by starting their own server.  The spoof server could read
passwords and queries sent by clients, but could not return any data
because the `PGDATA` directory would still be secure because
of directory permissions. Spoofing is possible because any user can
start a database server; a client cannot identify an invalid server
unless it is specially configured.

One way to prevent spoofing of `local`
connections is to use a Unix domain socket directory ([guc-unix-socket-directories](#guc-unix-socket-directories)) that has write permission only
for a trusted local user.  This prevents a malicious user from creating
their own socket file in that directory.  If you are concerned that
some applications might still reference `/tmp` for the
socket file and hence be vulnerable to spoofing, during operating system
startup create a symbolic link `/tmp/.s.PGSQL.5432` that points
to the relocated socket file.  You also might need to modify your
`/tmp` cleanup script to prevent removal of the symbolic link.

Another option for `local` connections is for clients to use
[`requirepeer`](#libpq-connect-requirepeer)
to specify the required owner of the server process connected to
the socket.

To prevent spoofing on TCP connections, either use
SSL certificates and make sure that clients check the server's certificate,
or use GSSAPI encryption (or both, if they're on separate connections).

To prevent spoofing with SSL, the server
must be configured to accept only `hostssl` connections ([auth-pg-hba-conf](#auth-pg-hba-conf)) and have SSL key and certificate files
([ssl-tcp](#ssl-tcp)). The TCP client must connect using
`sslmode=verify-ca` or
`verify-full` and have the appropriate root certificate
file installed ([libq-ssl-certificates](#libq-ssl-certificates)). Alternatively the
[system CA pool](#libpq-connect-sslrootcert), as defined
by the SSL implementation, can be used using `sslrootcert=system`; in
this case, `sslmode=verify-full` is forced for safety, since
it is generally trivial to obtain certificates which are signed by a public
CA.

To prevent server spoofing from occurring when using
[scram-sha-256](#auth-password) password authentication
over a network, you should ensure that you connect to the server using SSL
and with one of the anti-spoofing methods described in the previous
paragraph. Additionally, the SCRAM implementation in
libpq cannot protect the entire authentication
exchange, but using the `channel_binding=require` connection
parameter provides a mitigation against server spoofing. An attacker that
uses a rogue server to intercept a SCRAM exchange can use offline analysis to
potentially determine the hashed password from the client.

To prevent spoofing with GSSAPI, the server must be configured to accept
only `hostgssenc` connections
([auth-pg-hba-conf](#auth-pg-hba-conf)) and use `gss`
authentication with them.  The TCP client must connect
using `gssencmode=require`.
