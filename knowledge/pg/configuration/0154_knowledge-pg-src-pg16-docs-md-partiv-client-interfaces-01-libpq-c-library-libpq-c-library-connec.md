# Connection Strings; Parameter Key Words; Environment Variables; The Password File; The Connection Service File; LDAP Lookup of Connection Parameters; SSL Support

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIV_client_interfaces/01_libpq_-_c_library.md`
- Source Title: `libpq — C Library`
- Source Heading Path: `libpq - C Library > Connection Strings; Parameter Key Words; Environment Variables; The Password File; The Connection Service File; LDAP Lookup of Connection Parameters; SSL Support`
- Source Line Ranges: `589-737, 738-1446, 5405-5491, 5492-5538, 5539-5571, 5593-5654, 5662-5957`
- Chunk ID: `pg16_configuration_0154_94e22de223`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `01c320c95dede870e053508379b8e1f9d1420b8a560fb70721ef131f3fc13bd8`

## Retrieval Guidance

- Use When: Configure PostgreSQL client connection behavior, credentials, service aliases, LDAP lookup, or TLS verification in libpq-based tools.
- Retrieval Keywords: libpq connection string, host port dbname user password, PGHOST, PGSERVICE, pg_service.conf, .pgpass, sslmode, PGSSLMODE, PGSSLROOTCERT, client certificate
- Follow-up Guidance: Split SSL subsections if certificate trust and sslmode policy need separate retrieval labels.
- Classification Note: These sections define connection parameter syntax, environment defaults, password and service-file lookup, LDAP-provided parameters, SSL mode policy, certificate files, and client TLS behavior.

## Official Source Content

### Connection Strings

Several libpq functions parse a user-specified string to obtain
connection parameters.  There are two accepted formats for these strings:
plain keyword/value strings
and URIs.  URIs generally follow
[RFC
3986](https://datatracker.ietf.org/doc/html/rfc3986), except that multi-host connection strings are allowed
as further described below.

#### Keyword/Value Connection Strings

In the keyword/value format, each parameter setting is in the form
`keyword` `=`
`value`, with space(s) between settings.
Spaces around a setting's equal sign are
optional. To write an empty value, or a value containing spaces, surround it
with single quotes, for example `keyword = 'a value'`.
Single quotes and backslashes within
a value must be escaped with a backslash, i.e., `\'` and
`\\`.

Example:

```
host=localhost port=5432 dbname=mydb connect_timeout=10
```

The recognized parameter key words are listed in [libpq-paramkeywords](#libpq-paramkeywords).

#### Connection URIs

The general form for a connection URI is:

```
postgresql://``userspec`@`hostspec`/`dbname`?`paramspec`

where `userspec` is:

`user`:`password`

and `hostspec` is:

`host`:`port`,...

and `paramspec` is:

`name`=`value`&...
```

The URI scheme designator can be either
`postgresql://` or `postgres://`.  Each
of the remaining URI parts is optional.  The
following examples illustrate valid URI syntax:

```
postgresql://
postgresql://localhost
postgresql://localhost:5433
postgresql://localhost/mydb
postgresql://user@localhost
postgresql://user:secret@localhost
postgresql://other@localhost/otherdb?connect_timeout=10&application_name=myapp
postgresql://host1:123,host2:456/somedb?target_session_attrs=any&application_name=myapp
```

Values that would normally appear in the hierarchical part of
the URI can alternatively be given as named
parameters.  For example:

```
postgresql:///mydb?host=localhost&port=5433
```

All named parameters must match key words listed in
[libpq-paramkeywords](#libpq-paramkeywords), except that for compatibility
with JDBC connection URIs, instances
of `ssl=true` are translated into
`sslmode=require`.

The connection URI needs to be encoded with [percent-encoding](https://datatracker.ietf.org/doc/html/rfc3986#section-2.1)
if it includes symbols with special meaning in any of its parts.  Here is
an example where the equal sign (`=`) is replaced with
`%3D` and the space character with
`%20`:

```
postgresql://user@localhost:5433/mydb?options=-c%20synchronous_commit%3Doff
```

The host part may be either a host name or an IP address.  To specify an
IPv6 address, enclose it in square brackets:

```
postgresql://[2001:db8::1234]/database
```

The host part is interpreted as described for the parameter [libpq-connect-host](#libpq-connect-host).  In particular, a Unix-domain socket
connection is chosen if the host part is either empty or looks like an
absolute path name,
otherwise a TCP/IP connection is initiated.  Note, however, that the
slash is a reserved character in the hierarchical part of the URI.  So, to
specify a non-standard Unix-domain socket directory, either omit the host
part of the URI and specify the host as a named parameter, or
percent-encode the path in the host part of the URI:

```
postgresql:///dbname?host=/var/lib/postgresql
postgresql://%2Fvar%2Flib%2Fpostgresql/dbname
```

It is possible to specify multiple host components, each with an optional
port component, in a single URI.  A URI of the form
`postgresql://host1:port1,host2:port2,host3:port3/`
is equivalent to a connection string of the form
`host=host1,host2,host3 port=port1,port2,port3`.
As further described below, each
host will be tried in turn until a connection is successfully established.

#### Specifying Multiple Hosts

It is possible to specify multiple hosts to connect to, so that they are
tried in the given order. In the Keyword/Value format, the `host`,
`hostaddr`, and `port` options accept comma-separated
lists of values. The same number of elements must be given in each
option that is specified, such
that e.g., the first `hostaddr` corresponds to the first host name,
the second `hostaddr` corresponds to the second host name, and so
forth. As an exception, if only one `port` is specified, it
applies to all the hosts.

In the connection URI format, you can list multiple `host:port` pairs
separated by commas in the `host` component of the URI.

In either format, a single host name can translate to multiple network
addresses. A common example of this is a host that has both an IPv4 and
an IPv6 address.

When multiple hosts are specified, or when a single host name is
translated to multiple addresses,  all the hosts and addresses will be
tried in order, until one succeeds. If none of the hosts can be reached,
the connection fails. If a connection is established successfully, but
authentication fails, the remaining hosts in the list are not tried.

If a password file is used, you can have different passwords for
different hosts. All the other connection options are the same for every
host in the list; it is not possible to e.g., specify different
usernames for different hosts.

### Parameter Key Words

The currently recognized parameter key words are:

**`host`**
: Name of host to connect to. If a host name looks like an absolute path
name, it specifies Unix-domain communication rather than TCP/IP
communication; the value is the name of the directory in which the
socket file is stored.  (On Unix, an absolute path name begins with a
slash.  On Windows, paths starting with drive letters are also
recognized.)  If the host name starts with `@`, it is
taken as a Unix-domain socket in the abstract namespace (currently
supported on Linux and Windows).
The default behavior when `host` is not
specified, or is empty, is to connect to a Unix-domain
socket in
`/tmp` (or whatever socket directory was specified
when PostgreSQL was built).  On Windows,
the default is to connect to `localhost`.

A comma-separated list of host names is also accepted, in which case
each host name in the list is tried in order; an empty item in the
list selects the default behavior as explained above. See
[libpq-multiple-hosts](#libpq-multiple-hosts) for details.

**`hostaddr`**
: Numeric IP address of host to connect to.  This should be in the
standard IPv4 address format, e.g., `172.28.40.9`.  If
your machine supports IPv6, you can also use those addresses.
TCP/IP communication is
always used when a nonempty string is specified for this parameter.
If this parameter is not specified, the value of `host`
will be looked up to find the corresponding IP address — or, if
`host` specifies an IP address, that value will be
used directly.

Using `hostaddr` allows the
application to avoid a host name look-up, which might be important
in applications with time constraints. However, a host name is
required for GSSAPI or SSPI authentication
methods, as well as for `verify-full` SSL
certificate verification.  The following rules are used:

- If `host` is specified
without `hostaddr`, a host name lookup occurs.
(When using `PQconnectPoll`, the lookup occurs
when `PQconnectPoll` first considers this host
name, and it may cause `PQconnectPoll` to block
for a significant amount of time.)
- If `hostaddr` is specified without `host`,
the value for `hostaddr` gives the server network address.
The connection attempt will fail if the authentication
method requires a host name.
- If both `host` and `hostaddr` are specified,
the value for `hostaddr` gives the server network address.
The value for `host` is ignored unless the
authentication method requires it, in which case it will be
used as the host name.

Note that authentication is likely to fail if `host`
is not the name of the server at network address `hostaddr`.
Also, when both `host` and `hostaddr`
are specified, `host`
is used to identify the connection in a password file (see
[libpq-pgpass](#libpq-pgpass)).

A comma-separated list of `hostaddr` values is also
accepted, in which case each host in the list is tried in order.
An empty item in the list causes the corresponding host name to be
used, or the default host name if that is empty as well. See
[libpq-multiple-hosts](#libpq-multiple-hosts) for details.

Without either a host name or host address,
libpq will connect using a local
Unix-domain socket; or on Windows, it will attempt to connect to
`localhost`.

**`port`**
: Port number to connect to at the server host, or socket file
name extension for Unix-domain
connections.
If multiple hosts were given in the `host` or
`hostaddr` parameters, this parameter may specify a
comma-separated list of ports of the same length as the host list, or
it may specify a single port number to be used for all hosts.
An empty string, or an empty item in a comma-separated list,
specifies the default port number established
when PostgreSQL was built.

**`dbname`**
: The database name.  Defaults to be the same as the user name.
In certain contexts, the value is checked for extended
formats; see [libpq-connstring](#libpq-connstring) for more details on
those.

**`user`**
: PostgreSQL user name to connect as.
Defaults to be the same as the operating system name of the user
running the application.

**`password`**
: Password to be used if the server demands password authentication.

**`passfile`**
: Specifies the name of the file used to store passwords
(see [libpq-pgpass](#libpq-pgpass)).
Defaults to `~/.pgpass`, or
`%APPDATA%\postgresql\pgpass.conf` on Microsoft Windows.
(No error is reported if this file does not exist.)

**`require_auth`**
: Specifies the authentication method that the client requires from the
server. If the server does not use the required method to authenticate
the client, or if the authentication handshake is not fully completed by
the server, the connection will fail. A comma-separated list of methods
may also be provided, of which the server must use exactly one in order
for the connection to succeed. By default, any authentication method is
accepted, and the server is free to skip authentication altogether.

Methods may be negated with the addition of a `!`
prefix, in which case the server must *not* attempt
the listed method; any other method is accepted, and the server is free
not to authenticate the client at all. If a comma-separated list is
provided, the server may not attempt *any* of the
listed negated methods. Negated and non-negated forms may not be
combined in the same setting.

As a final special case, the `none` method requires the
server not to use an authentication challenge. (It may also be negated,
to require some form of authentication.)

The following methods may be specified:

`password`

The server must request plaintext password authentication.

**`md5`**
: The server must request MD5 hashed password authentication.

**`gss`**
: The server must either request a Kerberos handshake via
GSSAPI or establish a
GSS-encrypted channel (see also
[libpq-connect-gssencmode](#libpq-connect-gssencmode)).

**`sspi`**
: The server must request Windows SSPI
authentication.

**`scram-sha-256`**
: The server must successfully complete a SCRAM-SHA-256 authentication
exchange with the client.

**`none`**
: The server must not prompt the client for an authentication
exchange. (This does not prohibit client certificate authentication
via TLS, nor GSS authentication via its encrypted transport.)

`channel_binding`

This option controls the client's use of channel binding. A setting
of `require` means that the connection must employ
channel binding, `prefer` means that the client will
choose channel binding if available, and `disable`
prevents the use of channel binding. The default
is `prefer` if
PostgreSQL is compiled with SSL support;
otherwise the default is `disable`.

Channel binding is a method for the server to authenticate itself to
the client. It is only supported over SSL connections
with PostgreSQL 11 or later servers using
the `SCRAM` authentication method.

`connect_timeout`

Maximum time to wait while connecting, in seconds (write as a decimal integer,
e.g., `10`).  Zero, negative, or not specified means
wait indefinitely.  The minimum allowed timeout is 2 seconds, therefore
a value of `1` is interpreted as `2`.
This timeout applies separately to each host name or IP address.
For example, if you specify two hosts and `connect_timeout`
is 5, each host will time out if no connection is made within 5
seconds, so the total time spent waiting for a connection might be
up to 10 seconds.

`client_encoding`

This sets the `client_encoding`
configuration parameter for this connection.  In addition to
the values accepted by the corresponding server option, you
can use `auto` to determine the right
encoding from the current locale in the client
(`LC_CTYPE` environment variable on Unix
systems).

`options`

Specifies command-line options to send to the server at connection
start.  For example, setting this to `-c geqo=off` sets the
session's value of the `geqo` parameter to
`off`.  Spaces within this string are considered to
separate command-line arguments, unless escaped with a backslash
(`\`); write `\\` to represent a literal
backslash.  For a detailed discussion of the available
options, consult [runtime-config](#runtime-config).

`application_name`

Specifies a value for the [guc-application-name](#guc-application-name)
configuration parameter.

`fallback_application_name`

Specifies a fallback value for the [guc-application-name](#guc-application-name) configuration parameter.
This value will be used if no value has been given for
`application_name` via a connection parameter or the
`PGAPPNAME` environment variable.  Specifying
a fallback name is useful in generic utility programs that
wish to set a default application name but allow it to be
overridden by the user.

`keepalives`

Controls whether client-side TCP keepalives are used. The default
value is 1, meaning on, but you can change this to 0, meaning off,
if keepalives are not wanted.  This parameter is ignored for
connections made via a Unix-domain socket.

`keepalives_idle`

Controls the number of seconds of inactivity after which TCP should
send a keepalive message to the server.  A value of zero uses the
system default. This parameter is ignored for connections made via a
Unix-domain socket, or if keepalives are disabled.
It is only supported on systems where `TCP_KEEPIDLE` or
an equivalent socket option is available, and on Windows; on other
systems, it has no effect.

`keepalives_interval`

Controls the number of seconds after which a TCP keepalive message
that is not acknowledged by the server should be retransmitted.  A
value of zero uses the system default. This parameter is ignored for
connections made via a Unix-domain socket, or if keepalives are disabled.
It is only supported on systems where `TCP_KEEPINTVL` or
an equivalent socket option is available, and on Windows; on other
systems, it has no effect.

`keepalives_count`

Controls the number of TCP keepalives that can be lost before the
client's connection to the server is considered dead.  A value of
zero uses the system default. This parameter is ignored for
connections made via a Unix-domain socket, or if keepalives are disabled.
It is only supported on systems where `TCP_KEEPCNT` or
an equivalent socket option is available; on other systems, it has no
effect.

`tcp_user_timeout`

Controls the number of milliseconds that transmitted data may
remain unacknowledged before a connection is forcibly closed.
A value of zero uses the system default. This parameter is
ignored for connections made via a Unix-domain socket.
It is only supported on systems where `TCP_USER_TIMEOUT`
is available; on other systems, it has no effect.

`replication`

This option determines whether the connection should use the
replication protocol instead of the normal protocol.  This is what
PostgreSQL replication connections as well as tools such as
pg_basebackup use internally, but it can
also be used by third-party applications.  For a description of the
replication protocol, consult [protocol-replication](#protocol-replication).

The following values, which are case-insensitive, are supported:

**`true`, `on`,
`yes`, `1`**
: The connection goes into physical replication mode.

**`database`**
: The connection goes into logical replication mode, connecting to
the database specified in the `dbname` parameter.

**`false`, `off`,
`no`, `0`**
: The connection is a regular one, which is the default behavior.

In physical or logical replication mode, only the simple query protocol
can be used.

`gssencmode`

This option determines whether or with what priority a secure
GSS TCP/IP connection will be negotiated with the
server. There are three modes:

**`disable`**
: only try a non-GSSAPI-encrypted connection

**`prefer` (default)**
: if there are GSSAPI credentials present (i.e.,
in a credentials cache), first try
a GSSAPI-encrypted connection; if that fails or
there are no credentials, try a
non-GSSAPI-encrypted connection.  This is the
default when PostgreSQL has been
compiled with GSSAPI support.

**`require`**
: only try a GSSAPI-encrypted connection

`gssencmode` is ignored for Unix domain socket
communication.  If PostgreSQL is compiled
without GSSAPI support, using the `require` option
will cause an error, while `prefer` will be accepted
but libpq will not actually attempt
a GSSAPI-encrypted
connection.

`sslmode`

This option determines whether or with what priority a secure
SSL TCP/IP connection will be negotiated with the
server. There are six modes:

**`disable`**
: only try a non-SSL connection

**`allow`**
: first try a non-SSL connection; if that
fails, try an SSL connection

**`prefer` (default)**
: first try an SSL connection; if that fails,
try a non-SSL connection

**`require`**
: only try an SSL connection. If a root CA
file is present, verify the certificate in the same way as
if `verify-ca` was specified

**`verify-ca`**
: only try an SSL connection, and verify that
the server certificate is issued by a trusted
certificate authority (CA)

**`verify-full`**
: only try an SSL connection, verify that the
server certificate is issued by a
trusted CA and that the requested server host name
matches that in the certificate

See [libpq-ssl](#libpq-ssl) for a detailed description of how
these options work.

`sslmode` is ignored for Unix domain socket
communication.
If PostgreSQL is compiled without SSL support,
using options `require`, `verify-ca`, or
`verify-full` will cause an error, while
options `allow` and `prefer` will be
accepted but libpq will not actually attempt
an SSL
connection.

Note that if GSSAPI encryption is possible,
that will be used in preference to SSL
encryption, regardless of the value of `sslmode`.
To force use of SSL encryption in an
environment that has working GSSAPI
infrastructure (such as a Kerberos server), also
set `gssencmode` to `disable`.

`requiressl`

This option is deprecated in favor of the `sslmode`
setting.

If set to 1, an SSL connection to the server
is required (this is equivalent to `sslmode`
`require`).  libpq will then refuse
to connect if the server does not accept an
SSL connection.  If set to 0 (default),
libpq will negotiate the connection type with
the server (equivalent to `sslmode`
`prefer`).  This option is only available if
PostgreSQL is compiled with SSL support.

`sslcompression`

If set to 1, data sent over SSL connections will be compressed.  If
set to 0, compression will be disabled.  The default is 0.  This
parameter is ignored if a connection without SSL is made.

SSL compression is nowadays considered insecure and its use is no
longer recommended.  OpenSSL 1.1.0 disables
compression by default, and many operating system distributions
disable it in prior versions as well, so setting this parameter to on
will not have any effect if the server does not accept compression.
PostgreSQL 14 disables compression
completely in the backend.

If security is not a primary concern, compression can improve
throughput if the network is the bottleneck.  Disabling compression
can improve response time and throughput if CPU performance is the
limiting factor.

`sslcert`

This parameter specifies the file name of the client SSL
certificate, replacing the default
`~/.postgresql/postgresql.crt`.
This parameter is ignored if an SSL connection is not made.

`sslkey`

This parameter specifies the location for the secret key used for
the client certificate. It can either specify a file name that will
be used instead of the default
`~/.postgresql/postgresql.key`, or it can specify a key
obtained from an external "engine" (engines are
OpenSSL loadable modules).  An external engine
specification should consist of a colon-separated engine name and
an engine-specific key identifier.  This parameter is ignored if an
SSL connection is not made.

`sslpassword`

This parameter specifies the password for the secret key specified in
`sslkey`, allowing client certificate private keys
to be stored in encrypted form on disk even when interactive passphrase
input is not practical.

Specifying this parameter with any non-empty value suppresses the
`Enter PEM pass phrase:`
prompt that OpenSSL will emit by default
when an encrypted client certificate key is provided to
`libpq`.

If the key is not encrypted this parameter is ignored. The parameter
has no effect on keys specified by OpenSSL
engines unless the engine uses the OpenSSL
password callback mechanism for prompts.

There is no environment variable equivalent to this option, and no
facility for looking it up in `.pgpass`. It can be
used in a service file connection definition. Users with
more sophisticated uses should consider using OpenSSL engines and
tools like PKCS#11 or USB crypto offload devices.

`sslcertmode`

This option determines whether a client certificate may be sent to the
server, and whether the server is required to request one. There are
three modes:

**`disable`**
: A client certificate is never sent, even if one is available
(default location or provided via
[libpq-connect-sslcert](#libpq-connect-sslcert)).

**`allow` (default)**
: A certificate may be sent, if the server requests one and the
client has one to send.

**`require`**
: The server *must* request a certificate. The
connection will fail if the client does not send a certificate and
the server successfully authenticates the client anyway.

> **Note:**

> `sslcertmode=require` doesn't add any additional
> security, since there is no guarantee that the server is validating
> the certificate correctly; PostgreSQL servers generally request TLS
> certificates from clients whether they validate them or not. The
> option may be useful when troubleshooting more complicated TLS
> setups.
>

`sslrootcert`

This parameter specifies the name of a file containing SSL
certificate authority (CA) certificate(s).
If the file exists, the server's certificate will be verified
to be signed by one of these authorities.  The default is
`~/.postgresql/root.crt`.

The special value `system` may be specified instead, in
which case the trusted CA roots from the SSL implementation will be loaded. The exact
locations of these root certificates differ by SSL implementation and
platform. For OpenSSL in particular, the
locations may be further modified by the `SSL_CERT_DIR`
and `SSL_CERT_FILE` environment variables.

> **Note:**

> When using `sslrootcert=system`, the default
> `sslmode` is changed to `verify-full`,
> and any weaker setting will result in an error. In most cases it is
> trivial for anyone to obtain a certificate trusted by the system for a
> hostname they control, rendering `verify-ca` and all
> weaker modes useless.
>

>

> The magic `system` value will take precedence over a
> local certificate file with the same name. If for some reason you find
> yourself in this situation, use an alternative path like
> `sslrootcert=./system` instead.
>

`sslcrl`

This parameter specifies the file name of the SSL server certificate
revocation list (CRL).  Certificates listed in this file, if it
exists, will be rejected while attempting to authenticate the
server's certificate.  If neither
[libpq-connect-sslcrl](#libpq-connect-sslcrl) nor
[libpq-connect-sslcrldir](#libpq-connect-sslcrldir) is set, this setting is
taken as
`~/.postgresql/root.crl`.

`sslcrldir`

This parameter specifies the directory name of the SSL server certificate
revocation list (CRL).  Certificates listed in the files in this
directory, if it exists, will be rejected while attempting to
authenticate the server's certificate.

The directory needs to be prepared with the
OpenSSL command
`openssl rehash` or `c_rehash`.  See
its documentation for details.

Both `sslcrl` and `sslcrldir` can be
specified together.

`sslsni`

If set to 1 (default), libpq sets the TLS extension "Server Name
Indication" (SNI) on SSL-enabled connections.
By setting this parameter to 0, this is turned off.

The Server Name Indication can be used by SSL-aware proxies to route
connections without having to decrypt the SSL stream.  (Note that this
requires a proxy that is aware of the PostgreSQL protocol handshake,
not just any SSL proxy.)  However, SNI makes the
destination host name appear in cleartext in the network traffic, so
it might be undesirable in some cases.

`requirepeer`

This parameter specifies the operating-system user name of the
server, for example `requirepeer=postgres`.
When making a Unix-domain socket connection, if this
parameter is set, the client checks at the beginning of the
connection that the server process is running under the specified
user name; if it is not, the connection is aborted with an error.
This parameter can be used to provide server authentication similar
to that available with SSL certificates on TCP/IP connections.
(Note that if the Unix-domain socket is in
`/tmp` or another publicly writable location,
any user could start a server listening there.  Use this parameter
to ensure that you are connected to a server run by a trusted user.)
This option is only supported on platforms for which the
`peer` authentication method is implemented; see
[auth-peer](#auth-peer).

`ssl_min_protocol_version`

This parameter specifies the minimum SSL/TLS protocol version to allow
for the connection. Valid values are `TLSv1`,
`TLSv1.1`, `TLSv1.2` and
`TLSv1.3`. The supported protocols depend on the
version of OpenSSL used, older versions
not supporting the most modern protocol versions. If not specified,
the default is `TLSv1.2`, which satisfies industry
best practices as of this writing.

`ssl_max_protocol_version`

This parameter specifies the maximum SSL/TLS protocol version to allow
for the connection. Valid values are `TLSv1`,
`TLSv1.1`, `TLSv1.2` and
`TLSv1.3`. The supported protocols depend on the
version of OpenSSL used, older versions
not supporting the most modern protocol versions. If not set, this
parameter is ignored and the connection will use the maximum bound
defined by the backend, if set. Setting the maximum protocol version
is mainly useful for testing or if some component has issues working
with a newer protocol.

`krbsrvname`

Kerberos service name to use when authenticating with GSSAPI.
This must match the service name specified in the server
configuration for Kerberos authentication to succeed. (See also
[gssapi-auth](#gssapi-auth).)
The default value is normally `postgres`,
but that can be changed when
building PostgreSQL via
the --with-krb-srvnam` option
of configure.
In most environments, this parameter never needs to be changed.
Some Kerberos implementations might require a different service name,
such as Microsoft Active Directory which requires the service name
to be in upper case (`POSTGRES`).

`gsslib`

GSS library to use for GSSAPI authentication.
Currently this is disregarded except on Windows builds that include
both GSSAPI and SSPI support.  In that case, set
this to `gssapi` to cause libpq to use the GSSAPI
library for authentication instead of the default SSPI.

`gssdelegation`

Forward (delegate) GSS credentials to the server.  The default is
`0` which means credentials will not be forwarded
to the server.  Set this to `1` to have credentials
forwarded when possible.

`service`

Service name to use for additional parameters.  It specifies a service
name in `pg_service.conf` that holds additional connection parameters.
This allows applications to specify only a service name so connection parameters
can be centrally maintained. See [libpq-pgservice](#libpq-pgservice).

`target_session_attrs`

This option determines whether the session must have certain
properties to be acceptable.  It's typically used in combination
with multiple host names to select the first acceptable alternative
among several hosts.  There are six modes:

**`any` (default)**
: any successful connection is acceptable

**`read-write`**
: session must accept read-write transactions by default (that
is, the server must not be in hot standby mode and
the `default_transaction_read_only` parameter
must be `off`)

**`read-only`**
: session must not accept read-write transactions by default (the
converse)

**`primary`**
: server must not be in hot standby mode

**`standby`**
: server must be in hot standby mode

**`prefer-standby`**
: first try to find a standby server, but if none of the listed
hosts is a standby server, try again in `any`
mode

`load_balance_hosts`

Controls the order in which the client tries to connect to the available
hosts and addresses. Once a connection attempt is successful no other
hosts and addresses will be tried. This parameter is typically used in
combination with multiple host names or a DNS record that returns
multiple IPs. This parameter can be used in combination with
[libpq-connect-target-session-attrs](#libpq-connect-target-session-attrs)
to, for example, load balance over standby servers only. Once successfully
connected, subsequent queries on the returned connection will all be
sent to the same server. There are currently two modes:

**`disable` (default)**
: No load balancing across hosts is performed.  Hosts are tried in
the order in which they are provided and addresses are tried in
the order they are received from DNS or a hosts file.

**`random`**
: Hosts and addresses are tried in random order. This value is mostly
useful when opening multiple connections at the same time, possibly
from different machines. This way connections can be load balanced
across multiple PostgreSQL servers.

While random load balancing, due to its random nature, will almost
never result in a completely uniform distribution, it statistically
gets quite close. One important aspect here is that this algorithm
uses two levels of random choices: First the hosts
will be resolved in random order. Then secondly, before resolving
the next host, all resolved addresses for the current host will be
tried in random order. This behaviour can skew the amount of
connections each node gets greatly in certain cases, for instance
when some hosts resolve to more addresses than others. But such a
skew can also be used on purpose, e.g. to increase the number of
connections a larger server gets by providing its hostname multiple
times in the host string.

When using this value it's recommended to also configure a reasonable
value for [libpq-connect-connect-timeout](#libpq-connect-connect-timeout). Because then,
if one of the nodes that are used for load balancing is not responding,
a new node will be tried.

## Environment Variables

The following environment variables can be used to select default
connection parameter values, which will be used by
[libpq-PQconnectdb](#libpq-PQconnectdb), [libpq-PQsetdbLogin](#libpq-PQsetdbLogin) and
[libpq-PQsetdb](#libpq-PQsetdb) if no value is directly specified by the calling
code.  These are useful to avoid hard-coding database connection
information into simple client applications, for example.

- `PGHOST` behaves the same as the [libpq-connect-host](#libpq-connect-host) connection parameter.
- `PGHOSTADDR` behaves the same as the [libpq-connect-hostaddr](#libpq-connect-hostaddr) connection parameter.
This can be set instead of or in addition to `PGHOST`
to avoid DNS lookup overhead.
- `PGPORT` behaves the same as the [libpq-connect-port](#libpq-connect-port) connection parameter.
- `PGDATABASE` behaves the same as the [libpq-connect-dbname](#libpq-connect-dbname) connection parameter.
- `PGUSER` behaves the same as the [libpq-connect-user](#libpq-connect-user) connection parameter.
- `PGPASSWORD` behaves the same as the [libpq-connect-password](#libpq-connect-password) connection parameter.
Use of this environment variable
is not recommended for security reasons, as some operating systems
allow non-root users to see process environment variables via
ps; instead consider using a password file
(see [libpq-pgpass](#libpq-pgpass)).
- `PGPASSFILE` behaves the same as the [libpq-connect-passfile](#libpq-connect-passfile) connection parameter.
- `PGREQUIREAUTH` behaves the same as the [libpq-connect-require-auth](#libpq-connect-require-auth) connection parameter.
- `PGCHANNELBINDING` behaves the same as the [libpq-connect-channel-binding](#libpq-connect-channel-binding) connection parameter.
- `PGSERVICE` behaves the same as the [libpq-connect-service](#libpq-connect-service) connection parameter.
- `PGSERVICEFILE` specifies the name of the per-user
connection service file
(see [libpq-pgservice](#libpq-pgservice)).
Defaults to `~/.pg_service.conf`, or
`%APPDATA%\postgresql\.pg_service.conf` on
Microsoft Windows.
- `PGOPTIONS` behaves the same as the [libpq-connect-options](#libpq-connect-options) connection parameter.
- `PGAPPNAME` behaves the same as the [libpq-connect-application-name](#libpq-connect-application-name) connection parameter.
- `PGSSLMODE` behaves the same as the [libpq-connect-sslmode](#libpq-connect-sslmode) connection parameter.
- `PGREQUIRESSL` behaves the same as the [libpq-connect-requiressl](#libpq-connect-requiressl) connection parameter.
This environment variable is deprecated in favor of the
`PGSSLMODE` variable; setting both variables suppresses the
effect of this one.
- `PGSSLCOMPRESSION` behaves the same as the [libpq-connect-sslcompression](#libpq-connect-sslcompression) connection parameter.
- `PGSSLCERT` behaves the same as the [libpq-connect-sslcert](#libpq-connect-sslcert) connection parameter.
- `PGSSLKEY` behaves the same as the [libpq-connect-sslkey](#libpq-connect-sslkey) connection parameter.
- `PGSSLCERTMODE` behaves the same as the [libpq-connect-sslcertmode](#libpq-connect-sslcertmode) connection parameter.
- `PGSSLROOTCERT`  behaves the same as the [libpq-connect-sslrootcert](#libpq-connect-sslrootcert) connection parameter.
- `PGSSLCRL`  behaves the same as the [libpq-connect-sslcrl](#libpq-connect-sslcrl) connection parameter.
- `PGSSLCRLDIR` behaves the same as the [libpq-connect-sslcrldir](#libpq-connect-sslcrldir) connection parameter.
- `PGSSLSNI`  behaves the same as the [libpq-connect-sslsni](#libpq-connect-sslsni) connection parameter.
- `PGREQUIREPEER` behaves the same as the [libpq-connect-requirepeer](#libpq-connect-requirepeer) connection parameter.
- `PGSSLMINPROTOCOLVERSION` behaves the same as the [libpq-connect-ssl-min-protocol-version](#libpq-connect-ssl-min-protocol-version) connection parameter.
- `PGSSLMAXPROTOCOLVERSION` behaves the same as the [libpq-connect-ssl-max-protocol-version](#libpq-connect-ssl-max-protocol-version) connection parameter.
- `PGGSSENCMODE` behaves the same as the [libpq-connect-gssencmode](#libpq-connect-gssencmode) connection parameter.
- `PGKRBSRVNAME`  behaves the same as the [libpq-connect-krbsrvname](#libpq-connect-krbsrvname) connection parameter.
- `PGGSSLIB` behaves the same as the [libpq-connect-gsslib](#libpq-connect-gsslib) connection parameter.
- `PGGSSDELEGATION` behaves the same as the [libpq-connect-gssdelegation](#libpq-connect-gssdelegation) connection parameter.
- `PGCONNECT_TIMEOUT`  behaves the same as the [libpq-connect-connect-timeout](#libpq-connect-connect-timeout) connection parameter.
- `PGCLIENTENCODING` behaves the same as the [libpq-connect-client-encoding](#libpq-connect-client-encoding) connection parameter.
- `PGTARGETSESSIONATTRS` behaves the same as the [libpq-connect-target-session-attrs](#libpq-connect-target-session-attrs) connection parameter.
- `PGLOADBALANCEHOSTS` behaves the same as the [libpq-connect-load-balance-hosts](#libpq-connect-load-balance-hosts) connection parameter.

The following environment variables can be used to specify default
behavior for each PostgreSQL session.  (See
also the [sql-alterrole](#sql-alterrole)
and [sql-alterdatabase](#sql-alterdatabase)
commands for ways to set default behavior on a per-user or per-database
basis.)

- `PGDATESTYLE` sets the default style of date/time
representation.  (Equivalent to `SET datestyle TO
...`.)
- `PGTZ` sets the default time zone.  (Equivalent to
`SET timezone TO ...`.)
- `PGGEQO` sets the default mode for the genetic query
optimizer.  (Equivalent to `SET geqo TO ...`.)

Refer to the SQL command [sql-set](#sql-set)
for information on correct values for these
environment variables.

The following environment variables determine internal behavior of
libpq; they override compiled-in defaults.

- `PGSYSCONFDIR` sets the directory containing the
`pg_service.conf` file and in a future version
possibly other system-wide configuration files.
- `PGLOCALEDIR` sets the directory containing the
`locale` files for message localization.

## The Password File

The file `.pgpass` in a user's home directory can
contain passwords to
be used if the connection requires a password (and no password has been
specified otherwise). On Microsoft Windows the file is named
`%APPDATA%\postgresql\pgpass.conf` (where
`%APPDATA%` refers to the Application Data subdirectory in
the user's profile).
Alternatively, the password file to use can be specified
using the connection parameter [libpq-connect-passfile](#libpq-connect-passfile)
or the environment variable `PGPASSFILE`.

This file should contain lines of the following format:

```
`hostname`:`port`:`database`:`username`:`password`
```

(You can add a reminder comment to the file by copying the line above and
preceding it with `#`.)
Each of the first four fields can be a literal value, or
`*`, which matches anything.  The password field from
the first line that matches the current connection parameters will be
used.  (Therefore, put more-specific entries first when you are using
wildcards.) If an entry needs to contain `:` or
`\`, escape this character with `\`.
The host name field is matched to the `host` connection
parameter if that is specified, otherwise to
the `hostaddr` parameter if that is specified; if neither
are given then the host name `localhost` is searched for.
The host name `localhost` is also searched for when
the connection is a Unix-domain socket connection and
the `host` parameter
matches libpq's default socket directory path.
In a standby server, a database field of `replication`
matches streaming replication connections made to the primary server.
The database field is of limited usefulness otherwise, because users have
the same password for all databases in the same cluster.

On Unix systems, the permissions on a password file must
disallow any access to world or group; achieve this by a command such as
`chmod 0600 ~/.pgpass`.  If the permissions are less
strict than this, the file will be ignored.  On Microsoft Windows, it
is assumed that the file is stored in a directory that is secure, so
no special permissions check is made.

## The Connection Service File

The connection service file allows libpq connection parameters to be
associated with a single service name. That service name can then be
specified in a libpq connection string, and the associated settings will be
used. This allows connection parameters to be modified without requiring
a recompile of the libpq-using application. The service name can also be
specified using the `PGSERVICE` environment variable.

Service names can be defined in either a per-user service file or a
system-wide file.  If the same service name exists in both the user
and the system file, the user file takes precedence.
By default, the per-user service file is named
`~/.pg_service.conf`.
On Microsoft Windows, it is named
`%APPDATA%\postgresql\.pg_service.conf` (where
`%APPDATA%` refers to the Application Data subdirectory
in the user's profile).  A different file name can be specified by
setting the environment variable `PGSERVICEFILE`.
The system-wide file is named `pg_service.conf`.
By default it is sought in the `etc` directory
of the PostgreSQL installation
(use `pg_config --sysconfdir` to identify this
directory precisely).  Another directory, but not a different file
name, can be specified by setting the environment variable
`PGSYSCONFDIR`.

Either service file uses an "INI file" format where the section
name is the service name and the parameters are connection
parameters; see [libpq-paramkeywords](#libpq-paramkeywords) for a list.  For
example:

```

## LDAP Lookup of Connection Parameters

If libpq has been compiled with LDAP support (option
``--with-ldap`` for `configure`)
it is possible to retrieve connection options like `host`
or `dbname` via LDAP from a central server.
The advantage is that if the connection parameters for a database change,
the connection information doesn't have to be updated on all client machines.

LDAP connection parameter lookup uses the connection service file
`pg_service.conf` (see [libpq-pgservice](#libpq-pgservice)).  A line in a
`pg_service.conf` stanza that starts with
`ldap://` will be recognized as an LDAP URL and an
LDAP query will be performed. The result must be a list of
`keyword = value` pairs which will be used to set
connection options.  The URL must conform to
[RFC 1959](https://datatracker.ietf.org/doc/html/rfc1959)
and be of the form

```
ldap://[`hostname`[:`port`]]/`search_base`?`attribute`?`search_scope`?`filter`
```

where `hostname` defaults to
`localhost` and `port`
defaults to 389.

Processing of `pg_service.conf` is terminated after
a successful LDAP lookup, but is continued if the LDAP server cannot
be contacted.  This is to provide a fallback with further LDAP URL
lines that point to different LDAP servers, classical `keyword
= value` pairs, or default connection options.  If you would
rather get an error message in this case, add a syntactically incorrect
line after the LDAP URL.

A sample LDAP entry that has been created with the LDIF file

```
version:1
dn:cn=mydatabase,dc=mycompany,dc=com
changetype:add
objectclass:top
objectclass:device
cn:mydatabase
description:host=dbserver.mycompany.com
description:port=5439
description:dbname=mydb
description:user=mydb_user
description:sslmode=require
```

might be queried with the following LDAP URL:

```
ldap://ldap.mycompany.com/dc=mycompany,dc=com?description?one?(cn=mydatabase)
```

You can also mix regular service file entries with LDAP lookups.
A complete example for a stanza in `pg_service.conf`
would be:

```

## SSL Support

PostgreSQL has native support for using SSL
connections to encrypt client/server communications using
TLS protocols for increased security.
See [ssl-tcp](#ssl-tcp) for details about the server-side
SSL functionality.

libpq reads the system-wide
OpenSSL configuration file. By default, this
file is named `openssl.cnf` and is located in the
directory reported by `openssl version -d`.  This default
can be overridden by setting environment variable
`OPENSSL_CONF` to the name of the desired configuration
file.

### Client Verification of Server Certificates

By default, PostgreSQL will not perform any verification of
the server certificate. This means that it is possible to spoof the server
identity (for example by modifying a DNS record or by taking over the server
IP address) without the client knowing. In order to prevent spoofing,
the client must be able to verify the server's identity via a chain of
trust.  A chain of trust is established by placing a root (self-signed)
certificate authority (CA) certificate on one
computer and a leaf certificate *signed* by the
root certificate on another computer.  It is also possible to use an
"intermediate" certificate which is signed by the root
certificate and signs leaf certificates.

To allow the client to verify the identity of the server, place a root
certificate on the client and a leaf certificate signed by the root
certificate on the server.  To allow the server to verify the identity
of the client, place a root certificate on the server and a leaf
certificate signed by the root certificate on the client.  One or more
intermediate certificates (usually stored with the leaf certificate)
can also be used to link the leaf certificate to the root certificate.

Once a chain of trust has been established, there are two ways for
the client to validate the leaf certificate sent by the server.
If the parameter `sslmode` is set to `verify-ca`,
libpq will verify that the server is trustworthy by checking the
certificate chain up to the root certificate stored on the client.
If `sslmode` is set to `verify-full`,
libpq will *also* verify that the server host
name matches the name stored in the server certificate. The
SSL connection will fail if the server certificate cannot be
verified. `verify-full` is recommended in most
security-sensitive environments.

In `verify-full` mode, the host name is matched against the
certificate's Subject Alternative Name attribute(s) (SAN), or against the
Common Name attribute if no SAN of type `dNSName` is
present.  If the certificate's name attribute starts with an asterisk
(`*`), the asterisk will be treated as
a wildcard, which will match all characters *except* a dot
(`.`). This means the certificate will not match subdomains.
If the connection is made using an IP address instead of a host name, the
IP address will be matched (without doing any DNS lookups) against SANs of
type `iPAddress` or `dNSName`.  If no
`iPAddress` SAN is present and no
matching `dNSName` SAN is present, the host IP address is
matched against the Common Name attribute.

> **Note:**

> For backward compatibility with earlier versions of PostgreSQL, the host
> IP address is verified in a manner different
> from [RFC 6125](https://datatracker.ietf.org/doc/html/rfc6125).
> The host IP address is always matched against `dNSName`
> SANs as well as `iPAddress` SANs, and can be matched
> against the Common Name attribute if no relevant SANs exist.
>

To allow server certificate verification, one or more root certificates
must be placed in the file `~/.postgresql/root.crt`
in the user's home directory.  (On Microsoft Windows the file is named
`%APPDATA%\postgresql\root.crt`.)  Intermediate
certificates should also be added to the file if they are needed to link
the certificate chain sent by the server to the root certificates
stored on the client.

Certificate Revocation List (CRL) entries are also checked
if the file `~/.postgresql/root.crl` exists
(`%APPDATA%\postgresql\root.crl` on Microsoft
Windows).

The location of the root certificate file and the CRL can be changed by
setting
the connection parameters `sslrootcert` and `sslcrl`
or the environment variables `PGSSLROOTCERT` and `PGSSLCRL`.
`sslcrldir` or the environment variable `PGSSLCRLDIR`
can also be used to specify a directory containing CRL files.

> **Note:**

> For backwards compatibility with earlier versions of PostgreSQL, if a
> root CA file exists, the behavior of
> `sslmode`=`require` will be the same
> as that of `verify-ca`, meaning the server certificate
> is validated against the CA. Relying on this behavior is discouraged,
> and applications that need certificate validation should always use
> `verify-ca` or `verify-full`.
>

### Client Certificates

If the server attempts to verify the identity of the
client by requesting the client's leaf certificate,
libpq will send the certificate(s) stored in
file `~/.postgresql/postgresql.crt` in the user's home
directory.  The certificates must chain to the root certificate trusted
by the server.  A matching
private key file `~/.postgresql/postgresql.key` must also
be present.
On Microsoft Windows these files are named
`%APPDATA%\postgresql\postgresql.crt` and
`%APPDATA%\postgresql\postgresql.key`.
The location of the certificate and key files can be overridden by the
connection parameters `sslcert`
and `sslkey`, or by the
environment variables `PGSSLCERT` and `PGSSLKEY`.

On Unix systems, the permissions on the private key file must disallow
any access to world or group; achieve this by a command such as
`chmod 0600 ~/.postgresql/postgresql.key`.
Alternatively, the file can be owned by root and have group read access
(that is, `0640` permissions).  That setup is intended
for installations where certificate and key files are managed by the
operating system.  The user of libpq should
then be made a member of the group that has access to those certificate
and key files.  (On Microsoft Windows, there is no file permissions
check, since the `%APPDATA%\postgresql` directory is
presumed secure.)

The first certificate in `postgresql.crt` must be the
client's certificate because it must match the client's private key.
"Intermediate" certificates can be optionally appended
to the file — doing so avoids requiring storage of intermediate
certificates on the server ([guc-ssl-ca-file](#guc-ssl-ca-file)).

The certificate and key may be in PEM or ASN.1 DER format.

The key may be
stored in cleartext or encrypted with a passphrase using any algorithm
supported by OpenSSL, like AES-128. If the key
is stored encrypted, then the passphrase may be provided in the
[libpq-connect-sslpassword](#libpq-connect-sslpassword) connection option. If an
encrypted key is supplied and the `sslpassword` option
is absent or blank, a password will be prompted for interactively by
OpenSSL with a
`Enter PEM pass phrase:` prompt if a TTY is available.
Applications can override the client certificate prompt and the handling
of the `sslpassword` parameter by supplying their own
key password callback; see
[libpq-pqsetsslkeypasshook-openssl](#libpq-pqsetsslkeypasshook-openssl).

For instructions on creating certificates, see [ssl-certificate-creation](#ssl-certificate-creation).

### Protection Provided in Different Modes

The different values for the `sslmode` parameter provide different
levels of protection. SSL can provide
protection against three types of attacks:

**Eavesdropping**
: If a third party can examine the network traffic between the
client and the server, it can read both connection information (including
the user name and password) and the data that is passed. SSL
uses encryption to prevent this.

**Man-in-the-middle (MITM)**
: If a third party can modify the data while passing between the
client and server, it can pretend to be the server and therefore see and
modify data *even if it is encrypted*. The third party can then
forward the connection information and data to the original server,
making it impossible to detect this attack. Common vectors to do this
include DNS poisoning and address hijacking, whereby the client is directed
to a different server than intended. There are also several other
attack methods that can accomplish this. SSL uses certificate
verification to prevent this, by authenticating the server to the client.

**Impersonation**
: If a third party can pretend to be an authorized client, it can
simply access data it should not have access to. Typically this can
happen through insecure password management. SSL uses
client certificates to prevent this, by making sure that only holders
of valid certificates can access the server.

For a connection to be known SSL-secured, SSL usage must be configured
on *both the client and the server* before the connection
is made. If it is only configured on the server, the client may end up
sending sensitive information (e.g., passwords) before
it knows that the server requires high security. In libpq, secure
connections can be ensured
by setting the `sslmode` parameter to `verify-full` or
`verify-ca`, and providing the system with a root certificate to
verify against. This is analogous to using an `https`
URL for encrypted web browsing.

Once the server has been authenticated, the client can pass sensitive data.
This means that up until this point, the client does not need to know if
certificates will be used for authentication, making it safe to specify that
only in the server configuration.

All SSL options carry overhead in the form of encryption and
key-exchange, so there is a trade-off that has to be made between performance
and security. [libpq-ssl-sslmode-statements](#libpq-ssl-sslmode-statements)
illustrates the risks the different `sslmode` values
protect against, and what statement they make about security and overhead.

| `sslmode` | Eavesdropping protection | MITM protection | Statement |
| --- | --- | --- | --- |
| `disable` | No | No | I don't care about security, and I don't want to pay the overhead        of encryption. |
| `allow` | Maybe | No | I don't care about security, but I will pay the overhead of        encryption if the server insists on it. |
| `prefer` | Maybe | No | I don't care about encryption, but I wish to pay the overhead of        encryption if the server supports it. |
| `require` | Yes | No | I want my data to be encrypted, and I accept the overhead. I trust        that the network will make sure I always connect to the server I want. |
| `verify-ca` | Yes | Depends on CA policy | I want my data encrypted, and I accept the overhead. I want to be        sure that I connect to a server that I trust. |
| `verify-full` | Yes | Yes | I want my data encrypted, and I accept the overhead. I want to be         sure that I connect to a server I trust, and that it's the one I         specify. |

The difference between `verify-ca` and `verify-full`
depends on the policy of the root CA. If a public
CA is used, `verify-ca` allows connections to a server
that *somebody else* may have registered with the CA.
In this case, `verify-full` should always be used. If
a local CA is used, or even a self-signed certificate, using
`verify-ca` often provides enough protection.

The default value for `sslmode` is `prefer`. As is shown
in the table, this makes no sense from a security point of view, and it only
promises performance overhead if possible. It is only provided as the default
for backward compatibility, and is not recommended in secure deployments.

### SSL Client File Usage

[libpq-ssl-file-usage](#libpq-ssl-file-usage) summarizes the files that are
relevant to the SSL setup on the client.

| File | Contents | Effect |
| --- | --- | --- |
| `~/.postgresql/postgresql.crt` | client certificate | sent to server |
| `~/.postgresql/postgresql.key` | client private key | proves client certificate sent by owner; does not indicate       certificate owner is trustworthy |
| `~/.postgresql/root.crt` | trusted certificate authorities | checks that server certificate is signed by a trusted certificate       authority |
| `~/.postgresql/root.crl` | certificates revoked by certificate authorities | server certificate must not be on this list |

### SSL Library Initialization

If your application initializes `libssl` and/or
`libcrypto` libraries and libpq
is built with SSL support, you should call
[libpq-PQinitOpenSSL](#libpq-PQinitOpenSSL) to tell libpq
that the `libssl` and/or `libcrypto` libraries
have been initialized by your application, so that
libpq will not also initialize those libraries.
However, this is unnecessary when using OpenSSL
version 1.1.0 or later, as duplicate initializations are no longer problematic.

**`PQinitOpenSSL`**
: Allows applications to select which security libraries to initialize.

```
void PQinitOpenSSL(int do_ssl, int do_crypto);
```

When do_ssl is non-zero, libpq
will initialize the OpenSSL library before first
opening a database connection.  When do_crypto is
non-zero, the `libcrypto` library will be initialized.  By
default (if [libpq-PQinitOpenSSL](#libpq-PQinitOpenSSL) is not called), both libraries
are initialized.  When SSL support is not compiled in, this function is
present but does nothing.

If your application uses and initializes either OpenSSL
or its underlying `libcrypto` library, you *must*
call this function with zeroes for the appropriate parameter(s)
before first opening a database connection.  Also be sure that you
have done that initialization before opening a database connection.

**`PQinitSSL`**
: Allows applications to select which security libraries to initialize.

```
void PQinitSSL(int do_ssl);
```

This function is equivalent to
`PQinitOpenSSL(do_ssl, do_ssl)`.
It is sufficient for applications that initialize both or neither
of OpenSSL and `libcrypto`.

[libpq-PQinitSSL](#libpq-PQinitSSL) has been present since
PostgreSQL 8.0, while [libpq-PQinitOpenSSL](#libpq-PQinitOpenSSL)
was added in PostgreSQL 8.4, so [libpq-PQinitSSL](#libpq-PQinitSSL)
might be preferable for applications that need to work with older
versions of libpq.
