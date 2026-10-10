# listen_addresses, port

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/05_server_configuration.md`
- Source Title: `Server Configuration`
- Source Heading Path: `Server Configuration > Connections and Authentication > Connection Settings > listen_addresses, port`
- Source Line Ranges: `429-998, 3651-4707`
- Chunk ID: `pg16_configuration_0031_261cce60a9`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5d7ba67c8116b2e5e80c5bdd766c2fba0afc8cfa8460d0f7f5cb1e8ed2f66ebb`

## Retrieval Guidance

- Use When: 客户端 connection refused 或需要开放远程连接时确认监听配置。
- Retrieval Keywords: listen_addresses, port, localhost, 0.0.0.0, ::, TCP/IP connections
- Follow-up Guidance: 同时配置 pg_hba.conf；listen_addresses 变更需重启。
- Classification Note: 定义 TCP 监听地址和端口，直接决定服务器接受哪些网络连接。

## Official Source Content

## Connections and Authentication

### Connection Settings

**`listen_addresses` (`string`)**
: Specifies the TCP/IP address(es) on which the server is
to listen for connections from client applications.
The value takes the form of a comma-separated list of host names
and/or numeric IP addresses.  The special entry `*`
corresponds to all available IP interfaces.  The entry
`0.0.0.0` allows listening for all IPv4 addresses and
`::` allows listening for all IPv6 addresses.
If the list is empty, the server does not listen on any IP interface
at all, in which case only Unix-domain sockets can be used to connect
to it.  If the list is not empty, the server will start if it
can listen on at least one TCP/IP address.  A warning will be
emitted for any TCP/IP address which cannot be opened.
The default value is localhost,
which allows only local TCP/IP "loopback" connections to be
made.

While client authentication ([client-authentication](#client-authentication)) allows fine-grained control
over who can access the server, `listen_addresses`
controls which interfaces accept connection attempts, which
can help prevent repeated malicious connection requests on
insecure network interfaces.  This parameter can only be set
at server start.

**`port` (`integer`)**
: The TCP port the server listens on; 5432 by default.  Note that the
same port number is used for all IP addresses the server listens on.
This parameter can only be set at server start.

**`max_connections` (`integer`)**
: Determines the maximum number of concurrent connections to the
database server. The default is typically 100 connections, but
might be less if your kernel settings will not support it (as
determined during initdb).  This parameter can
only be set at server start.

When running a standby server, you must set this parameter to the
same or higher value than on the primary server. Otherwise, queries
will not be allowed in the standby server.

**`reserved_connections` (`integer`)**
: Determines the number of connection "slots" that are
reserved for connections by roles with privileges of the
[`pg_use_reserved_connections`](#predefined-roles-table)
role.  Whenever the number of free connection slots is greater than
[guc-superuser-reserved-connections](#guc-superuser-reserved-connections) but less than or
equal to the sum of `superuser_reserved_connections`
and `reserved_connections`, new connections will be
accepted only for superusers and roles with privileges of
`pg_use_reserved_connections`.  If
`superuser_reserved_connections` or fewer connection
slots are available, new connections will be accepted only for
superusers.

The default value is zero connections.  The value must be less than
`max_connections` minus
`superuser_reserved_connections`.  This parameter can
only be set at server start.

**`superuser_reserved_connections`
(`integer`)**
: Determines the number of connection "slots" that
are reserved for connections by PostgreSQL
superusers.  At most [guc-max-connections](#guc-max-connections)
connections can ever be active simultaneously.  Whenever the
number of active concurrent connections is at least
`max_connections` minus
`superuser_reserved_connections`, new
connections will be accepted only for superusers.  The connection slots
reserved by this parameter are intended as final reserve for emergency
use after the slots reserved by
[guc-reserved-connections](#guc-reserved-connections) have been exhausted.

The default value is three connections. The value must be less
than `max_connections` minus
`reserved_connections`.
This parameter can only be set at server start.

**`unix_socket_directories` (`string`)**
: Specifies the directory of the Unix-domain socket(s) on which the
server is to listen for connections from client applications.
Multiple sockets can be created by listing multiple directories
separated by commas.  Whitespace between entries is
ignored; surround a directory name with double quotes if you need
to include whitespace or commas in the name.
An empty value
specifies not listening on any Unix-domain sockets, in which case
only TCP/IP sockets can be used to connect to the server.

A value that starts with `@` specifies that a
Unix-domain socket in the abstract namespace should be created
(currently supported on Linux only).  In that case, this value
does not specify a "directory" but a prefix from which
the actual socket name is computed in the same manner as for the
file-system namespace.  While the abstract socket name prefix can be
chosen freely, since it is not a file-system location, the convention
is to nonetheless use file-system-like values such as
`@/tmp`.

The default value is normally
`/tmp`, but that can be changed at build time.
On Windows, the default is empty, which means no Unix-domain socket is
created by default.
This parameter can only be set at server start.

In addition to the socket file itself, which is named
`.s.PGSQL.`nnnn`` where
`nnnn` is the server's port number, an ordinary file
named `.s.PGSQL.`nnnn`.lock` will be
created in each of the `unix_socket_directories` directories.
Neither file should ever be removed manually.
For sockets in the abstract namespace, no lock file is created.

**`unix_socket_group` (`string`)**
: Sets the owning group of the Unix-domain socket(s).  (The owning
user of the sockets is always the user that starts the
server.)  In combination with the parameter
`unix_socket_permissions` this can be used as
an additional access control mechanism for Unix-domain connections.
By default this is the empty string, which uses the default
group of the server user.  This parameter can only be set at
server start.

This parameter is not supported on Windows.  Any setting will be
ignored.  Also, sockets in the abstract namespace have no file owner,
so this setting is also ignored in that case.

**`unix_socket_permissions` (`integer`)**
: Sets the access permissions of the Unix-domain socket(s).  Unix-domain
sockets use the usual Unix file system permission set.
The parameter value is expected to be a numeric mode
specified in the format accepted by the
`chmod` and `umask`
system calls.  (To use the customary octal format the number
must start with a `0` (zero).)

The default permissions are `0777`, meaning
anyone can connect. Reasonable alternatives are
`0770` (only user and group, see also
`unix_socket_group`) and `0700`
(only user). (Note that for a Unix-domain socket, only write
permission matters, so there is no point in setting or revoking
read or execute permissions.)

This access control mechanism is independent of the one
described in [client-authentication](#client-authentication).

This parameter can only be set at server start.

This parameter is irrelevant on systems, notably Solaris as of Solaris
10, that ignore socket permissions entirely.  There, one can achieve a
similar effect by pointing `unix_socket_directories` to a
directory having search permission limited to the desired audience.

Sockets in the abstract namespace have no file permissions, so this
setting is also ignored in that case.

**`bonjour` (`boolean`)**
: Enables advertising the server's existence via
Bonjour.  The default is off.
This parameter can only be set at server start.

**`bonjour_name` (`string`)**
: Specifies the Bonjour service
name.  The computer name is used if this parameter is set to the
empty string `''` (which is the default).  This parameter is
ignored if the server was not compiled with
Bonjour support.
This parameter can only be set at server start.

### TCP Settings

**`tcp_keepalives_idle` (`integer`)**
: Specifies the amount of time with no network activity after which
the operating system should send a TCP keepalive message to the client.
If this value is specified without units, it is taken as seconds.
A value of 0 (the default) selects the operating system's default.
On Windows, setting a value of 0 will set this parameter to 2 hours,
since Windows does not provide a way to read the system default value.
This parameter is supported only on systems that support
`TCP_KEEPIDLE` or an equivalent socket option, and on
Windows; on other systems, it must be zero.
In sessions connected via a Unix-domain socket, this parameter is
ignored and always reads as zero.

**`tcp_keepalives_interval` (`integer`)**
: Specifies the amount of time after which a TCP keepalive message
that has not been acknowledged by the client should be retransmitted.
If this value is specified without units, it is taken as seconds.
A value of 0 (the default) selects the operating system's default.
On Windows, setting a value of 0 will set this parameter to 1 second,
since Windows does not provide a way to read the system default value.
This parameter is supported only on systems that support
`TCP_KEEPINTVL` or an equivalent socket option, and on
Windows; on other systems, it must be zero.
In sessions connected via a Unix-domain socket, this parameter is
ignored and always reads as zero.

**`tcp_keepalives_count` (`integer`)**
: Specifies the number of TCP keepalive messages that can be lost before
the server's connection to the client is considered dead.
A value of 0 (the default) selects the operating system's default.
This parameter is supported only on systems that support
`TCP_KEEPCNT` or an equivalent socket option (which does not include Windows);
on other systems, it must be zero.
In sessions connected via a Unix-domain socket, this parameter is
ignored and always reads as zero.

**`tcp_user_timeout` (`integer`)**
: Specifies the amount of time that transmitted data may
remain unacknowledged before the TCP connection is forcibly closed.
If this value is specified without units, it is taken as milliseconds.
A value of 0 (the default) selects the operating system's default.
This parameter is supported only on systems that support
`TCP_USER_TIMEOUT` (which does not include Windows); on other systems, it must be zero.
In sessions connected via a Unix-domain socket, this parameter is
ignored and always reads as zero.

**`client_connection_check_interval` (`integer`)**
: Sets the time interval between optional checks that the client is still
connected, while running queries.  The check is performed by polling
the socket, and allows long running queries to be aborted sooner if
the kernel reports that the connection is closed.

This option relies on kernel events exposed by Linux, macOS, illumos
and the BSD family of operating systems, and is not currently available
on other systems.

If the value is specified without units, it is taken as milliseconds.
The default value is `0`, which disables connection
checks.  Without connection checks, the server will detect the loss of
the connection only at the next interaction with the socket, when it
waits for, receives or sends data.

For the kernel itself to detect lost TCP connections reliably and within
a known timeframe in all scenarios including network failure, it may
also be necessary to adjust the TCP keepalive settings of the operating
system, or the [guc-tcp-keepalives-idle](#guc-tcp-keepalives-idle),
[guc-tcp-keepalives-interval](#guc-tcp-keepalives-interval) and
[guc-tcp-keepalives-count](#guc-tcp-keepalives-count) settings of
PostgreSQL.

### Authentication

**`authentication_timeout` (`integer`)**
: Maximum amount of time allowed to complete client authentication. If a
would-be client has not completed the authentication protocol in
this much time, the server closes the connection. This prevents
hung clients from occupying a connection indefinitely.
If this value is specified without units, it is taken as seconds.
The default is one minute (`1m`).
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`password_encryption` (`enum`)**
: When a password is specified in [sql-createrole](#sql-createrole) or
[sql-alterrole](#sql-alterrole), this parameter determines the
algorithm to use to encrypt the password.  Possible values are
`scram-sha-256`, which will encrypt the password with
SCRAM-SHA-256, and `md5`, which stores the password
as an MD5 hash.  The default is `scram-sha-256`.

Note that older clients might lack support for the SCRAM authentication
mechanism, and hence not work with passwords encrypted with
SCRAM-SHA-256.  See [auth-password](#auth-password) for more details.

**`scram_iterations` (`integer`)**
: The number of computational iterations to be performed when encrypting
a password using SCRAM-SHA-256. The default is `4096`.
A higher number of iterations provides additional protection against
brute-force attacks on stored passwords, but makes authentication
slower. Changing the value has no effect on existing passwords
encrypted with SCRAM-SHA-256 as the iteration count is fixed at the
time of encryption. In order to make use of a changed value, a new
password must be set.

**`krb_server_keyfile` (`string`)**
: Sets the location of the server's Kerberos key file.  The default is
`FILE:/usr/local/pgsql/etc/krb5.keytab`
(where the directory part is whatever was specified
as `sysconfdir` at build time; use
`pg_config --sysconfdir` to determine that).
If this parameter is set to an empty string, it is ignored and a
system-dependent default is used.
This parameter can only be set in the
`postgresql.conf` file or on the server command line.
See [gssapi-auth](#gssapi-auth) for more information.

**`krb_caseins_users` (`boolean`)**
: Sets whether GSSAPI user names should be treated
case-insensitively.
The default is `off` (case sensitive). This parameter can only be
set in the `postgresql.conf` file or on the server command line.

**`gss_accept_delegation` (`boolean`)**
: Sets whether GSSAPI delegation should be accepted from the client.
The default is `off` meaning credentials from the client will
*not* be accepted.  Changing this to `on` will make the server
accept credentials delegated to it from the client. This parameter can only be
set in the `postgresql.conf` file or on the server command line.

**`db_user_namespace` (`boolean`)**
: This parameter enables per-database user names.  It is off by default.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

If this is on, you should create users as `username@dbname`.
When `username` is passed by a connecting client,
`@` and the database name are appended to the user
name and that database-specific user name is looked up by the
server. Note that when you create users with names containing
`@` within the SQL environment, you will need to
quote the user name.

With this parameter enabled, you can still create ordinary global
users.  Simply append `@` when specifying the user
name in the client, e.g., `joe@`.  The `@`
will be stripped off before the user name is looked up by the
server.

`db_user_namespace` causes the client's and
server's user name representation to differ.
Authentication checks are always done with the server's user name
so authentication methods must be configured for the
server's user name, not the client's.  Because
`md5` uses the user name as salt on both the
client and server, `md5` cannot be used with
`db_user_namespace`.

> **Note:**
> This feature is intended as a temporary measure until a
> complete solution is found.  At that time, this option will
> be removed.
>

### SSL

See [ssl-tcp](#ssl-tcp) for more information about setting up
SSL. The configuration parameters for controlling
transfer encryption using TLS protocols are named
`ssl` for historic reasons, even though support for
the SSL protocol has been deprecated.
SSL is in this context used interchangeably with
TLS.

**`ssl` (`boolean`)**
: Enables SSL connections.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.
The default is `off`.

**`ssl_ca_file` (`string`)**
: Specifies the name of the file containing the SSL server certificate
authority (CA).
Relative paths are relative to the data directory.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.
The default is empty, meaning no CA file is loaded,
and client certificate verification is not performed.

**`ssl_cert_file` (`string`)**
: Specifies the name of the file containing the SSL server certificate.
Relative paths are relative to the data directory.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.
The default is `server.crt`.

**`ssl_crl_file` (`string`)**
: Specifies the name of the file containing the SSL client certificate
revocation list (CRL).
Relative paths are relative to the data directory.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.
The default is empty, meaning no CRL file is loaded (unless
[guc-ssl-crl-dir](#guc-ssl-crl-dir) is set).

**`ssl_crl_dir` (`string`)**
: Specifies the name of the directory containing the SSL client
certificate revocation list (CRL).  Relative paths are relative to the
data directory.  This parameter can only be set in
the `postgresql.conf` file or on the server command
line.  The default is empty, meaning no CRLs are used (unless
[guc-ssl-crl-file](#guc-ssl-crl-file) is set).

The directory needs to be prepared with the
OpenSSL command
`openssl rehash` or `c_rehash`.  See
its documentation for details.

When using this setting, CRLs in the specified directory are loaded
on-demand at connection time.  New CRLs can be added to the directory
and will be used immediately.  This is unlike [guc-ssl-crl-file](#guc-ssl-crl-file), which causes the CRL in the file to be
loaded at server start time or when the configuration is reloaded.
Both settings can be used together.

**`ssl_key_file` (`string`)**
: Specifies the name of the file containing the SSL server private key.
Relative paths are relative to the data directory.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.
The default is `server.key`.

**`ssl_ciphers` (`string`)**
: Specifies a list of SSL cipher suites that are
allowed to be used by SSL connections.  See the
ciphers
manual page in the OpenSSL package for the
syntax of this setting and a list of supported values.  Only
connections using TLS version 1.2 and lower are affected.  There is
currently no setting that controls the cipher choices used by TLS
version 1.3 connections.  The default value is
`HIGH:MEDIUM:+3DES:!aNULL`.  The default is usually a
reasonable choice unless you have specific security requirements.

This parameter can only be set in the
`postgresql.conf` file or on the server command
line.

Explanation of the default value:

`HIGH`

Cipher suites that use ciphers from `HIGH` group (e.g.,
AES, Camellia, 3DES)

**`MEDIUM`**
: Cipher suites that use ciphers from `MEDIUM` group
(e.g., RC4, SEED)

**`+3DES`**
: The OpenSSL default order for
`HIGH` is problematic because it orders 3DES
higher than AES128.  This is wrong because 3DES offers less
security than AES128, and it is also much slower.
`+3DES` reorders it after all other
`HIGH` and `MEDIUM` ciphers.

**`!aNULL`**
: Disables anonymous cipher suites that do no authentication.  Such
cipher suites are vulnerable to MITM attacks and
therefore should not be used.

Available cipher suite details will vary across
OpenSSL versions.  Use the command
`openssl ciphers -v 'HIGH:MEDIUM:+3DES:!aNULL'` to
see actual details for the currently installed
OpenSSL version.  Note that this list is
filtered at run time based on the server key type.

`ssl_prefer_server_ciphers` (`boolean`)

Specifies whether to use the server's SSL cipher preferences, rather
than the client's.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.
The default is `on`.

PostgreSQL versions before 9.4 do not have
this setting and always use the client's preferences.  This setting is
mainly for backward compatibility with those versions.  Using the
server's preferences is usually better because it is more likely that
the server is appropriately configured.

`ssl_ecdh_curve` (`string`)

Specifies the name of the curve to use in ECDH key
exchange.  It needs to be supported by all clients that connect.
It does not need to be the same curve used by the server's Elliptic
Curve key.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.
The default is `prime256v1`.

OpenSSL names for the most common curves
are:
`prime256v1` (NIST P-256),
`secp384r1` (NIST P-384),
`secp521r1` (NIST P-521).
The full list of available curves can be shown with the command
`openssl ecparam -list_curves`.  Not all of them
are usable in TLS though.

`ssl_min_protocol_version` (`enum`)

Sets the minimum SSL/TLS protocol version to use.  Valid values are
currently: `TLSv1`, `TLSv1.1`,
`TLSv1.2`, `TLSv1.3`.  Older
versions of the OpenSSL library do not
support all values; an error will be raised if an unsupported setting
is chosen.  Protocol versions before TLS 1.0, namely SSL version 2 and
3, are always disabled.

The default is `TLSv1.2`, which satisfies industry
best practices as of this writing.

This parameter can only be set in the `postgresql.conf`
file or on the server command line.

`ssl_max_protocol_version` (`enum`)

Sets the maximum SSL/TLS protocol version to use.  Valid values are as
for [guc-ssl-min-protocol-version](#guc-ssl-min-protocol-version), with addition of
an empty string, which allows any protocol version.  The default is to
allow any version.  Setting the maximum protocol version is mainly
useful for testing or if some component has issues working with a
newer protocol.

This parameter can only be set in the `postgresql.conf`
file or on the server command line.

`ssl_dh_params_file` (`string`)

Specifies the name of the file containing Diffie-Hellman parameters
used for so-called ephemeral DH family of SSL ciphers. The default is
empty, in which case compiled-in default DH parameters used. Using
custom DH parameters reduces the exposure if an attacker manages to
crack the well-known compiled-in DH parameters. You can create your own
DH parameters file with the command
`openssl dhparam -out dhparams.pem 2048`.

This parameter can only be set in the `postgresql.conf`
file or on the server command line.

`ssl_passphrase_command` (`string`)

Sets an external command to be invoked when a passphrase for
decrypting an SSL file such as a private key needs to be obtained.  By
default, this parameter is empty, which means the built-in prompting
mechanism is used.

The command must print the passphrase to the standard output and exit
with code 0.  In the parameter value, `%p` is
replaced by a prompt string.  (Write `%%` for a
literal `%`.)  Note that the prompt string will
probably contain whitespace, so be sure to quote adequately.  A single
newline is stripped from the end of the output if present.

The command does not actually have to prompt the user for a
passphrase.  It can read it from a file, obtain it from a keychain
facility, or similar.  It is up to the user to make sure the chosen
mechanism is adequately secure.

This parameter can only be set in the `postgresql.conf`
file or on the server command line.

`ssl_passphrase_command_supports_reload` (`boolean`)

This parameter determines whether the passphrase command set by
`ssl_passphrase_command` will also be called during a
configuration reload if a key file needs a passphrase.  If this
parameter is `off` (the default), then
`ssl_passphrase_command` will be ignored during a
reload and the SSL configuration will not be reloaded if a passphrase
is needed.  That setting is appropriate for a command that requires a
TTY for prompting, which might not be available when the server is
running.  Setting this parameter to on might be appropriate if the
passphrase is obtained from a file, for example.

This parameter must be set to `on` when running on
Windows since all connections
will perform a configuration reload due to the different process model
of that platform.

This parameter can only be set in the `postgresql.conf`
file or on the server command line.

## Error Reporting and Logging

### Where to Log

**`log_destination` (`string`)**
: PostgreSQL supports several methods
for logging server messages, including
stderr, csvlog,
jsonlog, and
syslog. On Windows,
eventlog is also supported. Set this
parameter to a list of desired log destinations separated by
commas. The default is to log to stderr
only.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

If csvlog is included in `log_destination`,
log entries are output in "comma separated
value" (CSV) format, which is convenient for
loading logs into programs.
See [runtime-config-logging-csvlog](#runtime-config-logging-csvlog) for details.
[guc-logging-collector](#guc-logging-collector) must be enabled to generate
CSV-format log output.

If jsonlog is included in
`log_destination`, log entries are output in
JSON format, which is convenient for loading logs
into programs.
See [runtime-config-logging-jsonlog](#runtime-config-logging-jsonlog) for details.
[guc-logging-collector](#guc-logging-collector) must be enabled to generate
JSON-format log output.

When either stderr,
csvlog or jsonlog are
included, the file `current_logfiles` is created to
record the location of the log file(s) currently in use by the logging
collector and the associated logging destination. This provides a
convenient way to find the logs currently in use by the instance. Here
is an example of this file's content:

```
stderr log/postgresql.log
csvlog log/postgresql.csv
jsonlog log/postgresql.json
```

`current_logfiles` is recreated when a new log file
is created as an effect of rotation, and
when `log_destination` is reloaded.  It is removed when
none of stderr,
csvlog or jsonlog are
included in `log_destination`, and when the logging
collector is disabled.

> **Note:**
> On most Unix systems, you will need to alter the configuration of
> your system's syslog daemon in order
> to make use of the syslog option for
> `log_destination`.  PostgreSQL
> can log to syslog facilities
> `LOCAL0` through `LOCAL7` (see  linkend="guc-syslog-facility"/>), but the default
> syslog configuration on most platforms
> will discard all such messages.  You will need to add something like:
> ```
> local0.*    /var/log/postgresql
> ```
> to the  syslog daemon's configuration file
> to make it work.
>
>
> On Windows, when you use the `eventlog`
> option for `log_destination`, you should
> register an event source and its library with the operating
> system so that the Windows Event Viewer can display event
> log messages cleanly.
> See [event-log-registration](#event-log-registration) for details.
>

**`logging_collector` (`boolean`)**
: This parameter enables the *logging collector*, which
is a background process that captures log messages
sent to stderr and redirects them into log files.
This approach is often more useful than
logging to syslog, since some types of messages
might not appear in syslog output.  (One common
example is dynamic-linker failure messages; another is error messages
produced by scripts such as `archive_command`.)
This parameter can only be set at server start.

> **Note:**
> It is possible to log to stderr without using the
> logging collector; the log messages will just go to wherever the
> server's stderr is directed.  However, that method is
> only suitable for low log volumes, since it provides no convenient
> way to rotate log files.  Also, on some platforms not using the
> logging collector can result in lost or garbled log output, because
> multiple processes writing concurrently to the same log file can
> overwrite each other's output.
>

> **Note:**
> The logging collector is designed to never lose messages.  This means
> that in case of extremely high load, server processes could be
> blocked while trying to send additional log messages when the
> collector has fallen behind.  In contrast, syslog
> prefers to drop messages if it cannot write them, which means it
> may fail to log some messages in such cases but it will not block
> the rest of the system.
>

**`log_directory` (`string`)**
: When `logging_collector` is enabled,
this parameter determines the directory in which log files will be created.
It can be specified as an absolute path, or relative to the
cluster data directory.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.
The default is `log`.

**`log_filename` (`string`)**
: When `logging_collector` is enabled,
this parameter sets the file names of the created log files.  The value
is treated as a `strftime` pattern,
so `%`-escapes can be used to specify time-varying
file names.  (Note that if there are
any time-zone-dependent `%`-escapes, the computation
is done in the zone specified
by [guc-log-timezone](#guc-log-timezone).)
The supported `%`-escapes are similar to those
listed in the Open Group's [strftime
](https://pubs.opengroup.org/onlinepubs/009695399/functions/strftime.html) specification.
Note that the system's `strftime` is not used
directly, so platform-specific (nonstandard) extensions do not work.
The default is `postgresql-%Y-%m-%d_%H%M%S.log`.

If you specify a file name without escapes, you should plan to
use a log rotation utility to avoid eventually filling the
entire disk.  In releases prior to 8.4, if
no `%` escapes were
present, PostgreSQL would append
the epoch of the new log file's creation time, but this is no
longer the case.

If CSV-format output is enabled in `log_destination`,
`.csv` will be appended to the timestamped
log file name to create the file name for CSV-format output.
(If `log_filename` ends in `.log`, the suffix is
replaced instead.)

If JSON-format output is enabled in `log_destination`,
`.json` will be appended to the timestamped
log file name to create the file name for JSON-format output.
(If `log_filename` ends in `.log`, the suffix is
replaced instead.)

This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`log_file_mode` (`integer`)**
: On Unix systems this parameter sets the permissions for log files
when `logging_collector` is enabled. (On Microsoft
Windows this parameter is ignored.)
The parameter value is expected to be a numeric mode
specified in the format accepted by the
`chmod` and `umask`
system calls.  (To use the customary octal format the number
must start with a `0` (zero).)

The default permissions are `0600`, meaning only the
server owner can read or write the log files.  The other commonly
useful setting is `0640`, allowing members of the owner's
group to read the files.  Note however that to make use of such a
setting, you'll need to alter [guc-log-directory](#guc-log-directory) to
store the files somewhere outside the cluster data directory.  In
any case, it's unwise to make the log files world-readable, since
they might contain sensitive data.

This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`log_rotation_age` (`integer`)**
: When `logging_collector` is enabled,
this parameter determines the maximum amount of time to use an
individual log file, after which a new log file will be created.
If this value is specified without units, it is taken as minutes.
The default is 24 hours.
Set to zero to disable time-based creation of new log files.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`log_rotation_size` (`integer`)**
: When `logging_collector` is enabled,
this parameter determines the maximum size of an individual log file.
After this amount of data has been emitted into a log file,
a new log file will be created.
If this value is specified without units, it is taken as kilobytes.
The default is 10 megabytes.
Set to zero to disable size-based creation of new log files.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`log_truncate_on_rotation` (`boolean`)**
: When `logging_collector` is enabled,
this parameter will cause PostgreSQL to truncate (overwrite),
rather than append to, any existing log file of the same name.
However, truncation will occur only when a new file is being opened
due to time-based rotation, not during server startup or size-based
rotation.  When off, pre-existing files will be appended to in
all cases.  For example, using this setting in combination with
a `log_filename` like `postgresql-%H.log`
would result in generating twenty-four hourly log files and then
cyclically overwriting them.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

Example:  To keep 7 days of logs, one log file per day named
`server_log.Mon`, `server_log.Tue`,
etc., and automatically overwrite last week's log with this week's log,
set `log_filename` to `server_log.%a`,
`log_truncate_on_rotation` to `on`, and
`log_rotation_age` to `1440`.

Example: To keep 24 hours of logs, one log file per hour, but
also rotate sooner if the log file size exceeds 1GB, set
`log_filename` to `server_log.%H%M`,
`log_truncate_on_rotation` to `on`,
`log_rotation_age` to `60`, and
`log_rotation_size` to `1000000`.
Including `%M` in `log_filename` allows
any size-driven rotations that might occur to select a file name
different from the hour's initial file name.

**`syslog_facility` (`enum`)**
: When logging to syslog is enabled, this parameter
determines the syslog
"facility" to be used.  You can choose
from `LOCAL0`, `LOCAL1`,
`LOCAL2`, `LOCAL3`, `LOCAL4`,
`LOCAL5`, `LOCAL6`, `LOCAL7`;
the default is `LOCAL0`. See also the
documentation of your system's
syslog daemon.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`syslog_ident` (`string`)**
: When logging to syslog is enabled, this parameter
determines the program name used to identify
PostgreSQL messages in
syslog logs. The default is
`postgres`.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`syslog_sequence_numbers` (`boolean`)**
: When logging to syslog and this is on (the
default), then each message will be prefixed by an increasing
sequence number (such as `[2]`).  This circumvents
the "--- last message repeated N times ---" suppression
that many syslog implementations perform by default.  In more modern
syslog implementations, repeated message suppression can be configured
(for example, `$RepeatedMsgReduction`
in rsyslog), so this might not be
necessary.  Also, you could turn this off if you actually want to
suppress repeated messages.

This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`syslog_split_messages` (`boolean`)**
: When logging to syslog is enabled, this parameter
determines how messages are delivered to syslog.  When on (the
default), messages are split by lines, and long lines are split so
that they will fit into 1024 bytes, which is a typical size limit for
traditional syslog implementations.  When off, PostgreSQL server log
messages are delivered to the syslog service as is, and it is up to
the syslog service to cope with the potentially bulky messages.

If syslog is ultimately logging to a text file, then the effect will
be the same either way, and it is best to leave the setting on, since
most syslog implementations either cannot handle large messages or
would need to be specially configured to handle them.  But if syslog
is ultimately writing into some other medium, it might be necessary or
more useful to keep messages logically together.

This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`event_source` (`string`)**
: When logging to event log is enabled, this parameter
determines the program name used to identify
PostgreSQL messages in
the log. The default is `PostgreSQL`.
This parameter can only be set at server start.

### When to Log

**`log_min_messages` (`enum`)**
: Controls which [message
levels](#runtime-config-severity-levels) are written to the server log.
Valid values are `DEBUG5`, `DEBUG4`,
`DEBUG3`, `DEBUG2`, `DEBUG1`,
`INFO`, `NOTICE`, `WARNING`,
`ERROR`, `LOG`, `FATAL`, and
`PANIC`.  Each level includes all the levels that
follow it.  The later the level, the fewer messages are sent
to the log.  The default is `WARNING`.  Note that
`LOG` has a different rank here than in
[guc-client-min-messages](#guc-client-min-messages).
Only superusers and users with the appropriate `SET`
privilege can change this setting.

**`log_min_error_statement` (`enum`)**
: Controls which SQL statements that cause an error
condition are recorded in the server log.  The current
SQL statement is included in the log entry for any message of
the specified
[severity](#runtime-config-severity-levels)
or higher.
Valid values are `DEBUG5`,
`DEBUG4`, `DEBUG3`,
`DEBUG2`, `DEBUG1`,
`INFO`, `NOTICE`,
`WARNING`, `ERROR`,
`LOG`,
`FATAL`, and `PANIC`.
The default is `ERROR`, which means statements
causing errors, log messages, fatal errors, or panics will be logged.
To effectively turn off logging of failing statements,
set this parameter to `PANIC`.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

**`log_min_duration_statement` (`integer`)**
: Causes the duration of each completed statement to be logged
if the statement ran for at least the specified amount of time.
For example, if you set it to `250ms`
then all SQL statements that run 250ms or longer will be
logged.  Enabling this parameter can be helpful in tracking down
unoptimized queries in your applications.
If this value is specified without units, it is taken as milliseconds.
Setting this to zero prints all statement durations.
`-1` (the default) disables logging statement
durations.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

This overrides [guc-log-min-duration-sample](#guc-log-min-duration-sample),
meaning that queries with duration exceeding this setting are not
subject to sampling and are always logged.

For clients using extended query protocol, durations of the Parse,
Bind, and Execute steps are logged independently.

> **Note:**
> When using this option together with
> [guc-log-statement](#guc-log-statement),
> the text of statements that are logged because of
> `log_statement` will not be repeated in the
> duration log message.
> If you are not using syslog, it is recommended
> that you log the PID or session ID using
> [guc-log-line-prefix](#guc-log-line-prefix)
> so that you can link the statement message to the later
> duration message using the process ID or session ID.
>

**`log_min_duration_sample` (`integer`)**
: Allows sampling the duration of completed statements that ran for
at least the specified amount of time.  This produces the same
kind of log entries as
[guc-log-min-duration-statement](#guc-log-min-duration-statement), but only for a
subset of the executed statements, with sample rate controlled by
[guc-log-statement-sample-rate](#guc-log-statement-sample-rate).
For example, if you set it to `100ms` then all
SQL statements that run 100ms or longer will be considered for
sampling.  Enabling this parameter can be helpful when the
traffic is too high to log all queries.
If this value is specified without units, it is taken as milliseconds.
Setting this to zero samples all statement durations.
`-1` (the default) disables sampling statement
durations.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

This setting has lower priority
than `log_min_duration_statement`, meaning that
statements with durations
exceeding `log_min_duration_statement` are not
subject to sampling and are always logged.

Other notes for `log_min_duration_statement`
apply also to this setting.

**`log_statement_sample_rate` (`floating point`)**
: Determines the fraction of statements with duration exceeding
[guc-log-min-duration-sample](#guc-log-min-duration-sample) that will be logged.
Sampling is stochastic, for example `0.5` means
there is statistically one chance in two that any given statement
will be logged.
The default is `1.0`, meaning to log all sampled
statements.
Setting this to zero disables sampled statement-duration logging,
the same as setting
`log_min_duration_sample` to
`-1`.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

**`log_transaction_sample_rate` (`floating point`)**
: Sets the fraction of transactions whose statements are all logged,
in addition to statements logged for other reasons.  It applies to
each new transaction regardless of its statements' durations.
Sampling is stochastic, for example `0.1` means
there is statistically one chance in ten that any given transaction
will be logged.
`log_transaction_sample_rate` can be helpful to
construct a sample of transactions.
The default is `0`, meaning not to log
statements from any additional transactions.  Setting this
to `1` logs all statements of all transactions.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

> **Note:**
> Like all statement-logging options, this option can add significant
> overhead.
>

**`log_startup_progress_interval` (`integer`)**
: Sets the amount of time after which the startup process will log
a message about a long-running operation that is still in progress,
as well as the interval between further progress messages for that
operation. The default is 10 seconds. A setting of `0`
disables the feature.  If this value is specified without units,
it is taken as milliseconds.  This setting is applied separately to
each operation.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

For example, if syncing the data directory takes 25 seconds and
thereafter resetting unlogged relations takes 8 seconds, and if this
setting has the default value of 10 seconds, then a messages will be
logged for syncing the data directory after it has been in progress
for 10 seconds and again after it has been in progress for 20 seconds,
but nothing will be logged for resetting unlogged relations.

[runtime-config-severity-levels](#runtime-config-severity-levels) explains the message
severity levels used by PostgreSQL.  If logging output
is sent to syslog or Windows'
eventlog, the severity levels are translated
as shown in the table.

| Severity | Usage | syslog | eventlog |
| --- | --- | --- | --- |
| `DEBUG1 .. DEBUG5` | Provides successively-more-detailed information for use by          developers. | `DEBUG` | `INFORMATION` |
| `INFO` | Provides information implicitly requested by the user,          e.g., output from `VACUUM VERBOSE`. | `INFO` | `INFORMATION` |
| `NOTICE` | Provides information that might be helpful to users, e.g.,          notice of truncation of long identifiers. | `NOTICE` | `INFORMATION` |
| `WARNING` | Provides warnings of likely problems, e.g., `COMMIT`          outside a transaction block. | `NOTICE` | `WARNING` |
| `ERROR` | Reports an error that caused the current command to          abort. | `WARNING` | `ERROR` |
| `LOG` | Reports information of interest to administrators, e.g.,          checkpoint activity. | `INFO` | `INFORMATION` |
| `FATAL` | Reports an error that caused the current session to          abort. | `ERR` | `ERROR` |
| `PANIC` | Reports an error that caused all database sessions to abort. | `CRIT` | `ERROR` |

### What to Log

> **Note:**

> What you choose to log can have security implications;  see
> [logfile-maintenance](#logfile-maintenance).
>

**`application_name` (`string`)**
: The `application_name` can be any string of less than
`NAMEDATALEN` characters (64 characters in a standard build).
It is typically set by an application upon connection to the server.
The name will be displayed in the `pg_stat_activity` view
and included in CSV log entries.  It can also be included in regular
log entries via the [guc-log-line-prefix](#guc-log-line-prefix) parameter.
Only printable ASCII characters may be used in the
`application_name` value.
Other characters are replaced with [C-style hexadecimal escapes](#sql-syntax-strings-escape).

**`debug_print_parse` (`boolean`)**
: These parameters enable various debugging output to be emitted.
When set, they print the resulting parse tree, the query rewriter
output, or the execution plan for each executed query.
These messages are emitted at `LOG` message level, so by
default they will appear in the server log but will not be sent to the
client.  You can change that by adjusting
[guc-client-min-messages](#guc-client-min-messages) and/or
[guc-log-min-messages](#guc-log-min-messages).
These parameters are off by default.

**`debug_pretty_print` (`boolean`)**
: When set, `debug_pretty_print` indents the messages
produced by `debug_print_parse`,
`debug_print_rewritten`, or
`debug_print_plan`.  This results in more readable
but much longer output than the "compact" format used when
it is off.  It is on by default.

**`log_autovacuum_min_duration` (`integer`)**
: Causes each action executed by autovacuum to be logged if it ran for at
least the specified amount of time.  Setting this to zero logs
all autovacuum actions. `-1` disables logging autovacuum
actions. If this value is specified without units, it is taken as milliseconds.
For example, if you set this to
`250ms` then all automatic vacuums and analyzes that run
250ms or longer will be logged.  In addition, when this parameter is
set to any value other than `-1`, a message will be
logged if an autovacuum action is skipped due to a conflicting lock or a
concurrently dropped relation. The default is `10min`.
Enabling this parameter can be helpful in tracking autovacuum activity.
This parameter can only be set in the `postgresql.conf`
file or on the server command line; but the setting can be overridden for
individual tables by changing table storage parameters.

**`log_checkpoints` (`boolean`)**
: Causes checkpoints and restartpoints to be logged in the server log.
Some statistics are included in the log messages, including the number
of buffers written and the time spent writing them.
This parameter can only be set in the `postgresql.conf`
file or on the server command line. The default is on.

**`log_connections` (`boolean`)**
: Causes each attempted connection to the server to be logged,
as well as successful completion of both client authentication (if
necessary) and authorization.
Only superusers and users with the appropriate `SET`
privilege can change this parameter at session start,
and it cannot be changed at all within a session.
The default is `off`.

> **Note:**
> Some client programs, like psql, attempt
> to connect twice while determining if a password is required, so
> duplicate "connection received" messages do not
> necessarily indicate a problem.
>

**`log_disconnections` (`boolean`)**
: Causes session terminations to be logged.  The log output
provides information similar to `log_connections`,
plus the duration of the session.
Only superusers and users with the appropriate `SET`
privilege can change this parameter at session start,
and it cannot be changed at all within a session.
The default is `off`.

**`log_duration` (`boolean`)**
: Causes the duration of every completed statement to be logged.
The default is `off`.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

For clients using extended query protocol, durations of the Parse,
Bind, and Execute steps are logged independently.

> **Note:**
> The difference between enabling `log_duration` and setting
> [guc-log-min-duration-statement](#guc-log-min-duration-statement) to zero is that
> exceeding `log_min_duration_statement` forces the text of
> the query to be logged, but this option doesn't.  Thus, if
> `log_duration` is `on` and
> `log_min_duration_statement` has a positive value, all
> durations are logged but the query text is included only for
> statements exceeding the threshold.  This behavior can be useful for
> gathering statistics in high-load installations.
>

**`log_error_verbosity` (`enum`)**
: Controls the amount of detail written in the server log for each
message that is logged.  Valid values are `TERSE`,
`DEFAULT`, and `VERBOSE`, each adding more
fields to displayed messages.  `TERSE` excludes
the logging of `DETAIL`, `HINT`,
`QUERY`, and `CONTEXT` error information.
`VERBOSE` output includes the `SQLSTATE` error
code (see also [errcodes-appendix](#errcodes-appendix)) and the source code file name, function name,
and line number that generated the error.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

**`log_hostname` (`boolean`)**
: By default, connection log messages only show the IP address of the
connecting host. Turning this parameter on causes logging of the
host name as well.  Note that depending on your host name resolution
setup this might impose a non-negligible performance penalty.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`log_line_prefix` (`string`)**
: This is a `printf`-style string that is output at the
beginning of each log line.
`%` characters begin "escape sequences"
that are replaced with status information as outlined below.
Unrecognized escapes are ignored. Other
characters are copied straight to the log line. Some escapes are
only recognized by session processes, and will be treated as empty by
background processes such as the main server process. Status
information may be aligned either left or right by specifying a
numeric literal after the % and before the option. A negative
value will cause the status information to be padded on the
right with spaces to give it a minimum width, whereas a positive
value will pad on the left. Padding can be useful to aid human
readability in log files.

This parameter can only be set in the `postgresql.conf`
file or on the server command line. The default is
`'%m [%p] '` which logs a time stamp and the process ID.

Escape
Effect
Session only

`%a`
Application name
yes

`%u`
User name
yes

`%d`
Database name
yes

`%r`
Remote host name or IP address, and remote port
yes

`%h`
Remote host name or IP address
yes

`%b`
Backend type
no

`%p`
Process ID
no

`%P`
Process ID of the parallel group leader, if this process
is a parallel query worker
no

`%t`
Time stamp without milliseconds
no

`%m`
Time stamp with milliseconds
no

`%n`
Time stamp with milliseconds (as a Unix epoch)
no

`%i`
Command tag: type of session's current command
yes

`%e`
SQLSTATE error code
no

`%c`
Session ID: see below
no

`%l`
Number of the log line for each session or process, starting at 1
no

`%s`
Process start time stamp
no

`%v`
Virtual transaction ID (backendID/localXID);  see
[transaction-id](#transaction-id)
no

`%x`
Transaction ID (0 if none is assigned);  see
[transaction-id](#transaction-id)
no

`%q`
Produces no output, but tells non-session
processes to stop at this point in the string; ignored by
session processes
no

`%Q`
Query identifier of the current query.  Query
identifiers are not computed by default, so this field
will be zero unless [guc-compute-query-id](#guc-compute-query-id)
parameter is enabled or a third-party module that computes
query identifiers is configured.
yes

`%%`
Literal `%`
no

The backend type corresponds to the column
`backend_type` in the view
[
`pg_stat_activity`](#monitoring-pg-stat-activity-view),
but additional types can appear
in the log that don't show in that view.

The `%c` escape prints a quasi-unique session identifier,
consisting of two 4-byte hexadecimal numbers (without leading zeros)
separated by a dot.  The numbers are the process start time and the
process ID, so `%c` can also be used as a space saving way
of printing those items.  For example, to generate the session
identifier from `pg_stat_activity`, use this query:

```
SELECT to_hex(trunc(EXTRACT(EPOCH FROM backend_start))::integer) || '.' ||
to_hex(pid)
FROM pg_stat_activity;
```

> **Tip:**
> If you set a nonempty value for `log_line_prefix`,
> you should usually make its last character be a space, to provide
> visual separation from the rest of the log line.  A punctuation
> character can be used too.
>

> **Tip:**
> Syslog produces its own
> time stamp and process ID information, so you probably do not want to
> include those escapes if you are logging to syslog.
>

> **Tip:**
> The `%q` escape is useful when including information that is
> only available in session (backend) context like user or database
> name.  For example:
> ```
> log_line_prefix = '%m [%p] %q%u@%d/%a '
> ```
>

> **Note:**
> The `%Q` escape always reports a zero identifier
> for lines output by [guc-log-statement](#guc-log-statement) because
> `log_statement` generates output before an
> identifier can be calculated, including invalid statements for
> which an identifier cannot be calculated.
>

**`log_lock_waits` (`boolean`)**
: Controls whether a log message is produced when a session waits
longer than [guc-deadlock-timeout](#guc-deadlock-timeout) to acquire a
lock.  This is useful in determining if lock waits are causing
poor performance.  The default is `off`.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

**`log_recovery_conflict_waits` (`boolean`)**
: Controls whether a log message is produced when the startup process
waits longer than `deadlock_timeout`
for recovery conflicts.  This is useful in determining if recovery
conflicts prevent the recovery from applying WAL.

The default is `off`.  This parameter can only be set
in the `postgresql.conf` file or on the server
command line.

**`log_parameter_max_length` (`integer`)**
: If greater than zero, each bind parameter value logged with a
non-error statement-logging message is trimmed to this many bytes.
Zero disables logging of bind parameters for non-error statement logs.
`-1` (the default) allows bind parameters to be
logged in full.
If this value is specified without units, it is taken as bytes.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

This setting only affects log messages printed as a result of
[guc-log-statement](#guc-log-statement),
[guc-log-duration](#guc-log-duration), and related settings.  Non-zero
values of this setting add some overhead, particularly if parameters
are sent in binary form, since then conversion to text is required.

**`log_parameter_max_length_on_error` (`integer`)**
: If greater than zero, each bind parameter value reported in error
messages is trimmed to this many bytes.
Zero (the default) disables including bind parameters in error
messages.
`-1` allows bind parameters to be printed in full.
If this value is specified without units, it is taken as bytes.

Non-zero values of this setting add overhead, as
PostgreSQL will need to store textual
representations of parameter values in memory at the start of each
statement, whether or not an error eventually occurs.  The overhead
is greater when bind parameters are sent in binary form than when
they are sent as text, since the former case requires data
conversion while the latter only requires copying the string.

**`log_statement` (`enum`)**
: Controls which SQL statements are logged. Valid values are
`none` (off), `ddl`, `mod`, and
`all` (all statements). `ddl` logs all data definition
statements, such as `CREATE`, `ALTER`, and
`DROP` statements. `mod` logs all
`ddl` statements, plus data-modifying statements
such as `INSERT`,
`UPDATE`, `DELETE`, `TRUNCATE`,
and `COPY FROM`.
`PREPARE`, `EXECUTE`, and
`EXPLAIN ANALYZE` statements are also logged if their
contained command is of an appropriate type.  For clients using
extended query protocol, logging occurs when an Execute message
is received, and values of the Bind parameters are included
(with any embedded single-quote marks doubled).

The default is `none`.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

> **Note:**
> Statements that contain simple syntax errors are not logged
> even by the `log_statement` = `all` setting,
> because the log message is emitted only after basic parsing has
> been done to determine the statement type.  In the case of extended
> query protocol, this setting likewise does not log statements that
> fail before the Execute phase (i.e., during parse analysis or
> planning).  Set `log_min_error_statement` to
> `ERROR` (or lower) to log such statements.
>
>
> Logged statements might reveal sensitive data and even contain
> plaintext passwords.
>

**`log_replication_commands` (`boolean`)**
: Causes each replication command to be logged in the server log.
See [protocol-replication](#protocol-replication) for more information about
replication command. The default value is `off`.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

**`log_temp_files` (`integer`)**
: Controls logging of temporary file names and sizes.
Temporary files can be
created for sorts, hashes, and temporary query results.
If enabled by this setting, a log entry is emitted for each
temporary file, with the file size specified in bytes, when it is deleted.
A value of zero logs all temporary file information, while positive
values log only files whose size is greater than or equal to
the specified amount of data.
If this value is specified without units, it is taken as kilobytes.
The default setting is -1, which disables such logging.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

**`log_timezone` (`string`)**
: Sets the time zone used for timestamps written in the server log.
Unlike [guc-timezone](#guc-timezone), this value is cluster-wide,
so that all sessions will report timestamps consistently.
The built-in default is `GMT`, but that is typically
overridden in `postgresql.conf`; initdb
will install a setting there corresponding to its system environment.
See [datatype-timezones](#datatype-timezones) for more information.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

### Using CSV-Format Log Output

Including `csvlog` in the `log_destination` list
provides a convenient way to import log files into a database table.
This option emits log lines in comma-separated-values
(CSV) format,
with these columns:
time stamp with milliseconds,
user name,
database name,
process ID,
client host:port number,
session ID,
per-session line number,
command tag,
session start time,
virtual transaction ID,
regular transaction ID,
error severity,
SQLSTATE code,
error message,
error message detail,
hint,
internal query that led to the error (if any),
character count of the error position therein,
error context,
user query that led to the error (if any and enabled by
`log_min_error_statement`),
character count of the error position therein,
location of the error in the PostgreSQL source code
(if `log_error_verbosity` is set to `verbose`),
application name, backend type, process ID of parallel group leader,
and query id.
Here is a sample table definition for storing CSV-format log output:

```
CREATE TABLE postgres_log
(
log_time timestamp(3) with time zone,
user_name text,
database_name text,
process_id integer,
connection_from text,
session_id text,
session_line_num bigint,
command_tag text,
session_start_time timestamp with time zone,
virtual_transaction_id text,
transaction_id bigint,
error_severity text,
sql_state_code text,
message text,
detail text,
hint text,
internal_query text,
internal_query_pos integer,
context text,
query text,
query_pos integer,
location text,
application_name text,
backend_type text,
leader_pid integer,
query_id bigint,
PRIMARY KEY (session_id, session_line_num)
);
```

To import a log file into this table, use the `COPY FROM`
command:

```
COPY postgres_log FROM '/full/path/to/logfile.csv' WITH csv;
```

It is also possible to access the file as a foreign table, using
the supplied [file-fdw](#file-fdw) module.

There are a few things you need to do to simplify importing CSV log
files:

1. Set `log_filename` and
`log_rotation_age` to provide a consistent,
predictable naming scheme for your log files.  This lets you
predict what the file name will be and know when an individual log
file is complete and therefore ready to be imported.
2. Set `log_rotation_size` to 0 to disable
size-based log rotation, as it makes the log file name difficult
to predict.
3. Set `log_truncate_on_rotation` to `on` so
that old log data isn't mixed with the new in the same file.
4. The table definition above includes a primary key specification.
This is useful to protect against accidentally importing the same
information twice.  The `COPY` command commits all of the
data it imports at one time, so any error will cause the entire
import to fail.  If you import a partial log file and later import
the file again when it is complete, the primary key violation will
cause the import to fail.  Wait until the log is complete and
closed before importing.  This procedure will also protect against
accidentally importing a partial line that hasn't been completely
written, which would also cause `COPY` to fail.

### Using JSON-Format Log Output

Including `jsonlog` in the
`log_destination` list provides a convenient way to
import log files into many different programs. This option emits log
lines in JSON format.

String fields with null values are excluded from output.
Additional fields may be added in the future. User applications that
process `jsonlog` output should ignore unknown fields.

Each log line is serialized as a JSON object with the set of keys and
their associated values shown in [runtime-config-logging-jsonlog-keys-values](#runtime-config-logging-jsonlog-keys-values).

| Key name | Type | Description |
| --- | --- | --- |
| `timestamp` | string | Time stamp with milliseconds |
| `user` | string | User name |
| `dbname` | string | Database name |
| `pid` | number | Process ID |
| `remote_host` | string | Client host |
| `remote_port` | number | Client port |
| `session_id` | string | Session ID |
| `line_num` | number | Per-session line number |
| `ps` | string | Current ps display |
| `session_start` | string | Session start time |
| `vxid` | string | Virtual transaction ID |
| `txid` | string | Regular transaction ID |
| `error_severity` | string | Error severity |
| `state_code` | string | SQLSTATE code |
| `message` | string | Error message |
| `detail` | string | Error message detail |
| `hint` | string | Error message hint |
| `internal_query` | string | Internal query that led to the error |
| `internal_position` | number | Cursor index into internal query |
| `context` | string | Error context |
| `statement` | string | Client-supplied query string |
| `cursor_position` | number | Cursor index into query string |
| `func_name` | string | Error location function name |
| `file_name` | string | File name of error location |
| `file_line_num` | number | File line number of the error location |
| `application_name` | string | Client application name |
| `backend_type` | string | Type of backend |
| `leader_pid` | number | Process ID of leader for active parallel workers |
| `query_id` | number | Query ID |

### Process Title

These settings control how process titles of server processes are
modified.  Process titles are typically viewed using programs like
ps or, on Windows, Process Explorer.
See [monitoring-ps](#monitoring-ps) for details.

**`cluster_name` (`string`)**
: Sets a name that identifies this database cluster (instance) for
various purposes.  The cluster name appears in the process title for
all server processes in this cluster.  Moreover, it is the default
application name for a standby connection (see [guc-synchronous-standby-names](#guc-synchronous-standby-names)).

The name can be any string of less
than `NAMEDATALEN` characters (64 characters in a standard
build). Only printable ASCII characters may be used in the
`cluster_name` value.
Other characters are replaced with [C-style hexadecimal escapes](#sql-syntax-strings-escape).
No name is shown if this parameter is set to the empty string
`''` (which is the default).
This parameter can only be set at server start.

**`update_process_title` (`boolean`)**
: Enables updating of the process title every time a new SQL command
is received by the server.
This setting defaults to `on` on most platforms, but it
defaults to `off` on Windows due to that platform's larger
overhead for updating the process title.
Only superusers and users with the appropriate `SET`
privilege can change this setting.
