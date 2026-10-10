# record order and fields

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/06_client_authentication.md`
- Source Title: `Client Authentication`
- Source Heading Path: `Client Authentication > The pg_hba.conf File > record order and fields`
- Source Line Ranges: `41-527`
- Chunk ID: `pg16_configuration_0087_ba7fe71f15`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6d82184a5c5691425b1fffc9d020d6f082a471dcd4c2d7ed10b77b548c5bcf77`

## Retrieval Guidance

- Use When: 需要编写或解释 HBA 访问控制规则。
- Retrieval Keywords: pg_hba.conf, local, host, hostssl, hostnossl, hostgssenc, database, user, address, auth-method, first match
- Follow-up Guidance: 规则按顺序匹配，认证失败不会 fall through 到后续规则。
- Classification Note: 定义 pg_hba.conf 记录格式、匹配顺序、连接类型、database/user/address/auth-method/auth-options 字段。

## Official Source Content

## The `pg_hba.conf` File

Client authentication is controlled by a configuration file,
which traditionally is named
`pg_hba.conf` and is stored in the database
cluster's data directory.
(HBA stands for host-based authentication.) A default
`pg_hba.conf` file is installed when the data
directory is initialized by [app-initdb](#app-initdb).  It is
possible to place the authentication configuration file elsewhere,
however; see the [guc-hba-file](#guc-hba-file) configuration parameter.

The general format of the `pg_hba.conf` file is
a set of records, one per line. Blank lines are ignored, as is any
text after the `#` comment character.
A record can be continued onto the next line by ending the line with
a backslash. (Backslashes are not special except at the end of a line.)
A record is made
up of a number of fields which are separated by spaces and/or tabs.
Fields can contain white space if the field value is double-quoted.
Quoting one of the keywords in a database, user, or address field (e.g.,
`all` or `replication`) makes the word lose its special
meaning, and just match a database, user, or host with that name.
Backslash line continuation applies even within quoted text or comments.

Each authentication record specifies a connection type, a client IP address
range (if relevant for the connection type), a database name, a user name,
and the authentication method to be used for connections matching
these parameters. The first record with a matching connection type,
client address, requested database, and user name is used to perform
authentication. There is no "fall-through" or
"backup": if one record is chosen and the authentication
fails, subsequent records are not considered. If no record matches,
access is denied.

Each record can be an include directive or an authentication record.
Include directives specify files that can be included, that contain
additional records. The records will be inserted in place of the
include directives. Include directives only contain two fields:
`include`, `include_if_exists` or
`include_dir` directive and the file or directory to be
included. The file or directory can be a relative or absolute path, and can
be double-quoted.  For the `include_dir` form, all files
not starting with a `.` and ending with
`.conf` will be included. Multiple files within an include
directory are processed in file name order (according to C locale rules,
i.e., numbers before letters, and uppercase letters before lowercase ones).

A record can have several formats:

```
local               `database`  `user`  `auth-method` `auth-options`
host                `database`  `user`  `address`     `auth-method`  `auth-options`
hostssl             `database`  `user`  `address`     `auth-method`  `auth-options`
hostnossl           `database`  `user`  `address`     `auth-method`  `auth-options`
hostgssenc          `database`  `user`  `address`     `auth-method`  `auth-options`
hostnogssenc        `database`  `user`  `address`     `auth-method`  `auth-options`
host                `database`  `user`  `IP-address`  `IP-mask`      `auth-method`  `auth-options`
hostssl             `database`  `user`  `IP-address`  `IP-mask`      `auth-method`  `auth-options`
hostnossl           `database`  `user`  `IP-address`  `IP-mask`      `auth-method`  `auth-options`
hostgssenc          `database`  `user`  `IP-address`  `IP-mask`      `auth-method`  `auth-options`
hostnogssenc        `database`  `user`  `IP-address`  `IP-mask`      `auth-method`  `auth-options`
include             `file`
include_if_exists   `file`
include_dir         `directory`
```

The meaning of the fields is as follows:

**`local`**
: This record matches connection attempts using Unix-domain
sockets.  Without a record of this type, Unix-domain socket
connections are disallowed.

**`host`**
: This record matches connection attempts made using TCP/IP.
`host` records match
SSL or non-SSL connection
attempts as well as GSSAPI encrypted or
non-GSSAPI encrypted connection attempts.

> **Note:**
> Remote TCP/IP connections will not be possible unless
> the server is started with an appropriate value for the
> [guc-listen-addresses](#guc-listen-addresses) configuration parameter,
> since the default behavior is to listen for TCP/IP connections
> only on the local loopback address `localhost`.
>

**`hostssl`**
: This record matches connection attempts made using TCP/IP,
but only when the connection is made with SSL
encryption.

To make use of this option the server must be built with
SSL support. Furthermore,
SSL must be enabled
by setting the [guc-ssl](#guc-ssl) configuration parameter (see
[ssl-tcp](#ssl-tcp) for more information).
Otherwise, the `hostssl` record is ignored except for
logging a warning that it cannot match any connections.

**`hostnossl`**
: This record type has the opposite behavior of `hostssl`;
it only matches connection attempts made over
TCP/IP that do not use SSL.

**`hostgssenc`**
: This record matches connection attempts made using TCP/IP,
but only when the connection is made with GSSAPI
encryption.

To make use of this option the server must be built with
GSSAPI support.  Otherwise,
the `hostgssenc` record is ignored except for logging
a warning that it cannot match any connections.

**`hostnogssenc`**
: This record type has the opposite behavior of `hostgssenc`;
it only matches connection attempts made over
TCP/IP that do not use GSSAPI encryption.

**`database`**
: Specifies which database name(s) this record matches.  The value
`all` specifies that it matches all databases.
The value `sameuser` specifies that the record
matches if the requested database has the same name as the
requested user.  The value `samerole` specifies that
the requested user must be a member of the role with the same
name as the requested database.  (`samegroup` is an
obsolete but still accepted spelling of `samerole`.)
Superusers are not considered to be members of a role for the
purposes of `samerole` unless they are explicitly
members of the role, directly or indirectly, and not just by
virtue of being a superuser.
The value `replication` specifies that the record
matches if a physical replication connection is requested, however, it
doesn't match with logical replication connections. Note that physical
replication connections do not specify any particular database whereas
logical replication connections do specify it.
Otherwise, this is the name of a specific
PostgreSQL database or a regular expression.
Multiple database names and/or regular expressions can be supplied by
separating them with commas.

If the database name starts with a slash (`/`), the
remainder of the name is treated as a regular expression.
(See [posix-syntax-details](#posix-syntax-details) for details of
PostgreSQL's regular expression syntax.)

A separate file containing database names and/or regular expressions
can be specified by preceding the file name with `@`.

**`user`**
: Specifies which database user name(s) this record
matches. The value `all` specifies that it
matches all users.  Otherwise, this is either the name of a specific
database user, a regular expression (when starting with a slash
(`/`), or a group name preceded by `+`.
(Recall that there is no real distinction between users and groups
in PostgreSQL; a `+` mark really means
"match any of the roles that are directly or indirectly members
of this role", while a name without a `+` mark matches
only that specific role.) For this purpose, a superuser is only
considered to be a member of a role if they are explicitly a member
of the role, directly or indirectly, and not just by virtue of
being a superuser.
Multiple user names and/or regular expressions can be supplied by
separating them with commas.

If the user name starts with a slash (`/`), the
remainder of the name is treated as a regular expression.
(See [posix-syntax-details](#posix-syntax-details) for details of
PostgreSQL's regular expression syntax.)

A separate file containing user names and/or regular expressions can
be specified by preceding the file name with `@`.

**`address`**
: Specifies the client machine address(es) that this record
matches.  This field can contain either a host name, an IP
address range, or one of the special key words mentioned below.

An IP address range is specified using standard numeric notation
for the range's starting address, then a slash (`/`)
and a CIDR mask length.  The mask
length indicates the number of high-order bits of the client
IP address that must match.  Bits to the right of this should
be zero in the given IP address.
There must not be any white space between the IP address, the
`/`, and the CIDR mask length.

Typical examples of an IPv4 address range specified this way are
`172.20.143.89/32` for a single host, or
`172.20.143.0/24` for a small network, or
`10.6.0.0/16` for a larger one.
An IPv6 address range might look like `::1/128`
for a single host (in this case the IPv6 loopback address) or
`fe80::7a31:c1ff:0000:0000/96` for a small
network.
`0.0.0.0/0` represents all
IPv4 addresses, and `::0/0` represents
all IPv6 addresses.
To specify a single host, use a mask length of 32 for IPv4 or
128 for IPv6.  In a network address, do not omit trailing zeroes.

An entry given in IPv4 format will match only IPv4 connections,
and an entry given in IPv6 format will match only IPv6 connections,
even if the represented address is in the IPv4-in-IPv6 range.

You can also write `all` to match any IP address,
`samehost` to match any of the server's own IP
addresses, or `samenet` to match any address in any
subnet that the server is directly connected to.

If a host name is specified (anything that is not an IP address
range or a special key word is treated as a host name),
that name is compared with the result of a reverse name
resolution of the client's IP address (e.g., reverse DNS
lookup, if DNS is used).  Host name comparisons are case
insensitive.  If there is a match, then a forward name
resolution (e.g., forward DNS lookup) is performed on the host
name to check whether any of the addresses it resolves to are
equal to the client's IP address.  If both directions match,
then the entry is considered to match.  (The host name that is
used in `pg_hba.conf` should be the one that
address-to-name resolution of the client's IP address returns,
otherwise the line won't be matched.  Some host name databases
allow associating an IP address with multiple host names, but
the operating system will only return one host name when asked
to resolve an IP address.)

A host name specification that starts with a dot
(`.`) matches a suffix of the actual host
name.  So `.example.com` would match
`foo.example.com` (but not just
`example.com`).

When host names are specified
in `pg_hba.conf`, you should make sure that
name resolution is reasonably fast.  It can be of advantage to
set up a local name resolution cache such
as `nscd`.  Also, you may wish to enable the
configuration parameter `log_hostname` to see
the client's host name instead of the IP address in the log.

These fields do not apply to `local` records.

> **Note:**
> Users sometimes wonder why host names are handled
> in this seemingly complicated way, with two name resolutions
> including a reverse lookup of the client's IP address.  This
> complicates use of the feature in case the client's reverse DNS
> entry is not set up or yields some undesirable host name.
> It is done primarily for efficiency: this way, a connection attempt
> requires at most two resolver lookups, one reverse and one forward.
> If there is a resolver problem with some address, it becomes only
> that client's problem.  A hypothetical alternative
> implementation that only did forward lookups would have to
> resolve every host name mentioned in
> `pg_hba.conf` during every connection attempt.
> That could be quite slow if many names are listed.
> And if there is a resolver problem with one of the host names,
> it becomes everyone's problem.
>
>
> Also, a reverse lookup is necessary to implement the suffix
> matching feature, because the actual client host name needs to
> be known in order to match it against the pattern.
>
>
> Note that this behavior is consistent with other popular
> implementations of host name-based access control, such as the
> Apache HTTP Server and TCP Wrappers.
>

**`IP-address`**
: These two fields can be used as an alternative to the
`IP-address``/``mask-length`
notation.  Instead of
specifying the mask length, the actual mask is specified in a
separate column. For example, `255.0.0.0` represents an IPv4
CIDR mask length of 8, and `255.255.255.255` represents a
CIDR mask length of 32.

These fields do not apply to `local` records.

**`auth-method`**
: Specifies the authentication method to use when a connection matches
this record. The possible choices are summarized here; details
are in [auth-methods](#auth-methods).  All the options
are lower case and treated case sensitively, so even acronyms like
`ldap` must be specified as lower case.

`trust`

Allow the connection unconditionally. This method
allows anyone that can connect to the
PostgreSQL database server to login as
any PostgreSQL user they wish,
without the need for a password or any other authentication.  See [auth-trust](#auth-trust) for details.

**`reject`**
: Reject the connection unconditionally. This is useful for
"filtering out" certain hosts from a group, for example a
`reject` line could block a specific host from connecting,
while a later line allows the remaining hosts in a specific
network to connect.

**`scram-sha-256`**
: Perform SCRAM-SHA-256 authentication to verify the user's
password. See [auth-password](#auth-password) for details.

**`md5`**
: Perform SCRAM-SHA-256 or MD5 authentication to verify the
user's password. See [auth-password](#auth-password)
for details.

**`password`**
: Require the client to supply an unencrypted password for
authentication.
Since the password is sent in clear text over the
network, this should not be used on untrusted networks.
See [auth-password](#auth-password) for details.

**`gss`**
: Use GSSAPI to authenticate the user. This is only
available for TCP/IP connections. See [gssapi-auth](#gssapi-auth) for details.  It can be used in conjunction
with GSSAPI encryption.

**`sspi`**
: Use SSPI to authenticate the user. This is only
available on Windows. See [sspi-auth](#sspi-auth) for details.

**`ident`**
: Obtain the operating system user name of the client
by contacting the ident server on the client
and check if it matches the requested database user name.
Ident authentication can only be used on TCP/IP
connections. When specified for local connections, peer
authentication will be used instead.
See [auth-ident](#auth-ident) for details.

**`peer`**
: Obtain the client's operating system user name from the operating
system and check if it matches the requested database user name.
This is only available for local connections.
See [auth-peer](#auth-peer) for details.

**`ldap`**
: Authenticate using an LDAP server. See [auth-ldap](#auth-ldap) for details.

**`radius`**
: Authenticate using a RADIUS server. See [auth-radius](#auth-radius) for details.

**`cert`**
: Authenticate using SSL client certificates. See
[auth-cert](#auth-cert) for details.

**`pam`**
: Authenticate using the Pluggable Authentication Modules
(PAM) service provided by the operating system.  See [auth-pam](#auth-pam) for details.

**`bsd`**
: Authenticate using the BSD Authentication service provided by the
operating system. See [auth-bsd](#auth-bsd) for details.

`auth-options`

After the `auth-method` field, there can be field(s) of
the form `name``=``value` that
specify options for the authentication method. Details about which
options are available for which authentication methods appear below.

In addition to the method-specific options listed below, there is a
method-independent authentication option `clientcert`, which
can be specified in any `hostssl` record.
This option can be set to `verify-ca` or
`verify-full`. Both options require the client
to present a valid (trusted) SSL certificate, while
`verify-full` additionally enforces that the
`cn` (Common Name) in the certificate matches
the username or an applicable mapping.
This behavior is similar to the `cert` authentication
method (see [auth-cert](#auth-cert)) but enables pairing
the verification of client certificates with any authentication
method that supports `hostssl` entries.

On any record using client certificate authentication (i.e. one
using the `cert` authentication method or one
using the `clientcert` option), you can specify
which part of the client certificate credentials to match using
the `clientname` option. This option can have one
of two values. If you specify `clientname=CN`, which
is the default, the username is matched against the certificate's
`Common Name (CN)`. If instead you specify
`clientname=DN` the username is matched against the
entire `Distinguished Name (DN)` of the certificate.
This option is probably best used in conjunction with a username map.
The comparison is done with the `DN` in
[RFC 2253](https://datatracker.ietf.org/doc/html/rfc2253)
format. To see the `DN` of a client certificate
in this format, do

```
openssl x509 -in myclient.crt -noout -subject -nameopt RFC2253 | sed "s/^subject=//"
```

Care needs to be taken when using this option, especially when using
regular expression matching against the `DN`.

`include`

This line will be replaced by the contents of the given file.

`include_if_exists`

This line will be replaced by the content of the given file if the
file exists. Otherwise, a message is logged to indicate that the file
has been skipped.

`include_dir`

This line will be replaced by the contents of all the files found in
the directory, if they don't start with a `.` and end
with `.conf`, processed in file name order (according
to C locale rules, i.e., numbers before letters, and uppercase letters
before lowercase ones).

Files included by `@` constructs are read as lists of names,
which can be separated by either whitespace or commas.  Comments are
introduced by `#`, just as in
`pg_hba.conf`, and nested `@` constructs are
allowed.  Unless the file name following `@` is an absolute
path, it is taken to be relative to the directory containing the
referencing file.

Since the `pg_hba.conf` records are examined
sequentially for each connection attempt, the order of the records is
significant. Typically, earlier records will have tight connection
match parameters and weaker authentication methods, while later
records will have looser match parameters and stronger authentication
methods. For example, one might wish to use `trust`
authentication for local TCP/IP connections but require a password for
remote TCP/IP connections. In this case a record specifying
`trust` authentication for connections from 127.0.0.1 would
appear before a record specifying password authentication for a wider
range of allowed client IP addresses.

The `pg_hba.conf` file is read on start-up and when
the main server process receives a
SIGHUP
signal. If you edit the file on an
active system, you will need to signal the postmaster
(using `pg_ctl reload`, calling the SQL function
`pg_reload_conf()`, or using `kill
-HUP`) to make it re-read the file.

> **Note:**

> The preceding statement is not true on Microsoft Windows: there, any
> changes in the `pg_hba.conf` file are immediately
> applied by subsequent new connections.
>

The system view
[`pg_hba_file_rules`](#view-pg-hba-file-rules)
can be helpful for pre-testing changes to the `pg_hba.conf`
file, or for diagnosing problems if loading of the file did not have the
desired effects.  Rows in the view with
non-null `error` fields indicate problems in the
corresponding lines of the file.

> **Tip:**

> To connect to a particular database, a user must not only pass the
> `pg_hba.conf` checks, but must have the
> `CONNECT` privilege for the database.  If you wish to
> restrict which users can connect to which databases, it's usually
> easier to control this by granting/revoking `CONNECT` privilege
> than to put the rules in `pg_hba.conf` entries.
>

Some examples of `pg_hba.conf` entries are shown in
[example-pg-hba.conf](#example-pg-hba.conf). See the next section for details on the
different authentication methods.
