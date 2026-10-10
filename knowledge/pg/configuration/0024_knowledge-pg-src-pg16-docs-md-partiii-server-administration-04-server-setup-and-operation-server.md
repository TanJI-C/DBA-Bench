# Basic Setup

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/04_server_setup_and_operation.md`
- Source Title: `Server Setup and Operation`
- Source Heading Path: `Server Setup and Operation > Secure TCP/IP Connections with GSSAPI Encryption > Basic Setup`
- Source Line Ranges: `1560-1816, 1853-1885, 1886-1972`
- Chunk ID: `pg16_configuration_0024_b70626be73`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `471a2158be31257829276ecd95ce25b9ef6fe737dd083528f06aa5c55728ee62`

## Retrieval Guidance

- Use When: 需要配置 PostgreSQL GSSAPI 加密连接。
- Retrieval Keywords: GSSAPI encryption, hostgssenc, gssencmode, GSSAPI authentication, MIT Kerberos
- Follow-up Guidance: 与 gss 认证、Kerberos principal/keytab 配置一起验证。
- Classification Note: 说明 GSSAPI 加密协商、hostgssenc、GSSAPI 认证组合和构建依赖。

## Official Source Content

## Secure TCP/IP Connections with SSL

PostgreSQL has native support for using
SSL connections to encrypt client/server communications
for increased security. This requires that
OpenSSL is installed on both client and
server systems and that support in PostgreSQL is
enabled at build time (see [installation](#installation)).

The terms SSL and TLS are often used
interchangeably to mean a secure encrypted connection using a
TLS protocol. SSL protocols are the
precursors to TLS protocols, and the term
SSL is still used for encrypted connections even though
SSL protocols are no longer supported.
SSL is used interchangeably with TLS
in PostgreSQL.

### Basic Setup

With SSL support compiled in, the
PostgreSQL server can be started with
support for encrypted connections using TLS protocols
enabled by setting the parameter
[guc-ssl](#guc-ssl) to `on` in
`postgresql.conf`.  The server will listen for both normal
and SSL connections on the same TCP port, and will negotiate
with any connecting client on whether to use SSL.  By
default, this is at the client's option; see [auth-pg-hba-conf](#auth-pg-hba-conf) about how to set up the server to require
use of SSL for some or all connections.

To start in SSL mode, files containing the server certificate
and private key must exist.  By default, these files are expected to be
named `server.crt` and `server.key`, respectively, in
the server's data directory, but other names and locations can be specified
using the configuration parameters [guc-ssl-cert-file](#guc-ssl-cert-file)
and [guc-ssl-key-file](#guc-ssl-key-file).

On Unix systems, the permissions on `server.key` must
disallow any access to world or group; achieve this by the command
`chmod 0600 server.key`.  Alternatively, the file can be
owned by root and have group read access (that is, `0640`
permissions).  That setup is intended for installations where certificate
and key files are managed by the operating system.  The user under which
the PostgreSQL server runs should then be made a
member of the group that has access to those certificate and key files.

If the data directory allows group read access then certificate files may
need to be located outside of the data directory in order to conform to the
security requirements outlined above.  Generally, group access is enabled
to allow an unprivileged user to backup the database, and in that case the
backup software will not be able to read the certificate files and will
likely error.

If the private key is protected with a passphrase, the
server will prompt for the passphrase and will not start until it has
been entered.
Using a passphrase by default disables the ability to change the server's
SSL configuration without a server restart, but see [guc-ssl-passphrase-command-supports-reload](#guc-ssl-passphrase-command-supports-reload).
Furthermore, passphrase-protected private keys cannot be used at all
on Windows.

The first certificate in `server.crt` must be the
server's certificate because it must match the server's private key.
The certificates of "intermediate" certificate authorities
can also be appended to the file.  Doing this avoids the necessity of
storing intermediate certificates on clients, assuming the root and
intermediate certificates were created with `v3_ca`
extensions.  (This sets the certificate's basic constraint of
`CA` to `true`.)
This allows easier expiration of intermediate certificates.

It is not necessary to add the root certificate to
`server.crt`.  Instead, clients must have the root
certificate of the server's certificate chain.

### OpenSSL Configuration

PostgreSQL reads the system-wide
OpenSSL configuration file. By default, this
file is named `openssl.cnf` and is located in the
directory reported by `openssl version -d`.
This default can be overridden by setting environment variable
`OPENSSL_CONF` to the name of the desired configuration file.

OpenSSL supports a wide range of ciphers
and authentication algorithms, of varying strength.  While a list of
ciphers can be specified in the OpenSSL
configuration file, you can specify ciphers specifically for use by
the database server by modifying [guc-ssl-ciphers](#guc-ssl-ciphers) in
`postgresql.conf`.

> **Note:**

> It is possible to have authentication without encryption overhead by
> using `NULL-SHA` or `NULL-MD5` ciphers.  However,
> a man-in-the-middle could read and pass communications between client
> and server.  Also, encryption overhead is minimal compared to the
> overhead of authentication.  For these reasons NULL ciphers are not
> recommended.
>

### Using Client Certificates

To require the client to supply a trusted certificate,
place certificates of the root certificate authorities
(CAs) you trust in a file in the data
directory, set the parameter [guc-ssl-ca-file](#guc-ssl-ca-file) in
`postgresql.conf` to the new file name, and add the
authentication option `clientcert=verify-ca` or
`clientcert=verify-full` to the appropriate
`hostssl` line(s) in `pg_hba.conf`.
A certificate will then be requested from the client during SSL
connection startup.  (See [libpq-ssl](#libpq-ssl) for a description
of how to set up certificates on the client.)

For a `hostssl` entry with
`clientcert=verify-ca`, the server will verify
that the client's certificate is signed by one of the trusted
certificate authorities. If `clientcert=verify-full`
is specified, the server will not only verify the certificate
chain, but it will also check whether the username or its mapping
matches the `cn` (Common Name) of the provided certificate.
Note that certificate chain validation is always ensured when the
`cert` authentication method is used
(see [auth-cert](#auth-cert)).

Intermediate certificates that chain up to existing root certificates
can also appear in the [guc-ssl-ca-file](#guc-ssl-ca-file) file if
you wish to avoid storing them on clients (assuming the root and
intermediate certificates were created with `v3_ca`
extensions).  Certificate Revocation List (CRL) entries are also
checked if the parameter [guc-ssl-crl-file](#guc-ssl-crl-file) or
[guc-ssl-crl-dir](#guc-ssl-crl-dir) is set.

The `clientcert` authentication option is available for
all authentication methods, but only in `pg_hba.conf` lines
specified as `hostssl`.  When `clientcert` is
not specified, the server verifies the client certificate against its CA
file only if a client certificate is presented and the CA is configured.

There are two approaches to enforce that users provide a certificate during login.

The first approach makes use of the `cert` authentication
method for `hostssl` entries in `pg_hba.conf`,
such that the certificate itself is used for authentication while also
providing ssl connection security. See [auth-cert](#auth-cert) for details.
(It is not necessary to specify any `clientcert` options
explicitly when using the `cert` authentication method.)
In this case, the `cn` (Common Name) provided in
the certificate is checked against the user name or an applicable mapping.

The second approach combines any authentication method for `hostssl`
entries with the verification of client certificates by setting the
`clientcert` authentication option to `verify-ca`
or `verify-full`. The former option only enforces that
the certificate is valid, while the latter also ensures that the
`cn` (Common Name) in the certificate matches
the user name or an applicable mapping.

### SSL Server File Usage

[ssl-file-usage](#ssl-file-usage) summarizes the files that are
relevant to the SSL setup on the server.  (The shown file names are default
names.  The locally configured names could be different.)

| File | Contents | Effect |
| --- | --- | --- |
| [guc-ssl-cert-file](#guc-ssl-cert-file) (`$PGDATA/server.crt`) | server certificate | sent to client to indicate server's identity |
| [guc-ssl-key-file](#guc-ssl-key-file) (`$PGDATA/server.key`) | server private key | proves server certificate was sent by the owner; does not indicate       certificate owner is trustworthy |
| [guc-ssl-ca-file](#guc-ssl-ca-file) | trusted certificate authorities | checks that client certificate is       signed by a trusted certificate authority |
| [guc-ssl-crl-file](#guc-ssl-crl-file) | certificates revoked by certificate authorities | client certificate must not be on this list |

The server reads these files at server start and whenever the server
configuration is reloaded.  On Windows
systems, they are also re-read whenever a new backend process is spawned
for a new client connection.

If an error in these files is detected at server start, the server will
refuse to start.  But if an error is detected during a configuration
reload, the files are ignored and the old SSL configuration continues to
be used.  On Windows systems, if an error in
these files is detected at backend start, that backend will be unable to
establish an SSL connection.  In all these cases, the error condition is
reported in the server log.

### Creating Certificates

To create a simple self-signed certificate for the server, valid for 365
days, use the following OpenSSL command,
replacing `dbhost.yourdomain.com` with the
server's host name:

```
openssl req -new -x509 -days 365 -nodes -text -out server.crt \
-keyout server.key -subj "/CN=`dbhost.yourdomain.com`"
```

Then do:

```
chmod og-rwx server.key
```

because the server will reject the file if its permissions are more
liberal than this.
For more details on how to create your server private key and
certificate, refer to the OpenSSL documentation.

While a self-signed certificate can be used for testing, a certificate
signed by a certificate authority (CA) (usually an
enterprise-wide root CA) should be used in production.

To create a server certificate whose identity can be validated
by clients, first create a certificate signing request
(CSR) and a public/private key file:

```
openssl req -new -nodes -text -out root.csr \
-keyout root.key -subj "/CN=`root.yourdomain.com`"
chmod og-rwx root.key
```

Then, sign the request with the key to create a root certificate
authority (using the default OpenSSL
configuration file location on Linux):

```
openssl x509 -req -in root.csr -text -days 3650 \
-extfile /etc/ssl/openssl.cnf -extensions v3_ca \
-signkey root.key -out root.crt
```

Finally, create a server certificate signed by the new root certificate
authority:

```
openssl req -new -nodes -text -out server.csr \
-keyout server.key -subj "/CN=`dbhost.yourdomain.com`"
chmod og-rwx server.key

openssl x509 -req -in server.csr -text -days 365 \
-CA root.crt -CAkey root.key -CAcreateserial \
-out server.crt
```

`server.crt` and `server.key`
should be stored on the server, and `root.crt` should
be stored on the client so the client can verify that the server's leaf
certificate was signed by its trusted root certificate.
`root.key` should be stored offline for use in
creating future certificates.

It is also possible to create a chain of trust that includes
intermediate certificates:

```

## Secure TCP/IP Connections with GSSAPI Encryption

PostgreSQL also has native support for
using GSSAPI to encrypt client/server communications for
increased security.  Support requires that a GSSAPI
implementation (such as MIT Kerberos) is installed on both client and server
systems, and that support in PostgreSQL is
enabled at build time (see [installation](#installation)).

### Basic Setup

The PostgreSQL server will listen for both
normal and GSSAPI-encrypted connections on the same TCP
port, and will negotiate with any connecting client whether to
use GSSAPI for encryption (and for authentication).  By
default, this decision is up to the client (which means it can be
downgraded by an attacker); see [auth-pg-hba-conf](#auth-pg-hba-conf) about
setting up the server to require the use of GSSAPI for
some or all connections.

When using GSSAPI for encryption, it is common to
use GSSAPI for authentication as well, since the
underlying mechanism will determine both client and server identities
(according to the GSSAPI implementation) in any
case.  But this is not required;
another PostgreSQL authentication method
can be chosen to perform additional verification.

Other than configuration of the negotiation
behavior, GSSAPI encryption requires no setup beyond
that which is necessary for GSSAPI authentication.  (For more information
on configuring that, see [gssapi-auth](#gssapi-auth).)

## Secure TCP/IP Connections with SSH Tunnels

It is possible to use SSH to encrypt the network
connection between clients and a
PostgreSQL server. Done properly, this
provides an adequately secure network connection, even for non-SSL-capable
clients.

First make sure that an SSH server is
running properly on the same machine as the
PostgreSQL server and that you can log in using
`ssh` as some user;  you then can establish a
secure tunnel to the remote server.  A secure tunnel listens on a
local port and forwards all traffic to a port on the remote machine.
Traffic sent to the remote port can arrive on its
`localhost` address, or different bind
address if desired;  it does not appear as coming from your
local machine.  This command creates a secure tunnel from the client
machine to the remote machine `foo.com`:

```
ssh -L 63333:localhost:5432 joe@foo.com
```

The first number in the `-L` argument, 63333, is the
local port number of the tunnel; it can be any unused port.  (IANA
reserves ports 49152 through 65535 for private use.)  The name or IP
address after this is the remote bind address you are connecting to,
i.e., `localhost`, which is the default.  The second
number, 5432, is the remote end of the tunnel, e.g., the port number
your database server is using.  In order to connect to the database
server using this tunnel, you connect to port 63333 on the local
machine:

```
psql -h localhost -p 63333 postgres
```

To the database server it will then look as though you are
user `joe` on host `foo.com`
connecting to the `localhost` bind address, and it
will use whatever authentication procedure was configured for
connections by that user to that bind address.  Note that the server will not
think the connection is SSL-encrypted, since in fact it is not
encrypted between the
SSH server and the
PostgreSQL server.  This should not pose any
extra security risk because they are on the same machine.

In order for the
tunnel setup to succeed you must be allowed to connect via
`ssh` as `joe@foo.com`, just
as if you had attempted to use `ssh` to create a
terminal session.

You could also have set up port forwarding as

```
ssh -L 63333:foo.com:5432 joe@foo.com
```

but then the database server will see the connection as coming in
on its `foo.com` bind address, which is not opened by
the default setting `listen_addresses =
'localhost'`.  This is usually not what you want.

If you have to "hop" to the database server via some
login host, one possible setup could look like this:

```
ssh -L 63333:db.foo.com:5432 joe@shell.foo.com
```

Note that this way the connection
from `shell.foo.com`
to `db.foo.com` will not be encrypted by the SSH
tunnel.
SSH offers quite a few configuration possibilities when the network
is restricted in various ways.  Please refer to the SSH
documentation for details.

> **Tip:**

> Several other applications exist that can provide secure tunnels using
> a procedure similar in concept to the one just described.
>
