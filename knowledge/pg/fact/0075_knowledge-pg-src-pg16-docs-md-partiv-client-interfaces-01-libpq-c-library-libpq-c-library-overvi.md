# Overview; Database Connection Control Functions; Command Execution Functions; Asynchronous Command Processing; Pipeline Mode; COPY; Large Objects; Control Functions; Miscellaneous Functions

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIV_client_interfaces/01_libpq_-_c_library.md`
- Source Title: `libpq — C Library`
- Source Heading Path: `libpq - C Library > Overview; Database Connection Control Functions; Command Execution Functions; Asynchronous Command Processing; Pipeline Mode; COPY; Large Objects; Control Functions; Miscellaneous Functions`
- Source Line Ranges: `30-1446, 1920-3095, 3096-3438, 3439-3796, 4128-4451, 4452-4606, 4607-4868`
- Chunk ID: `pg16_fact_0075_dfad75ae21`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `31c52170d057a502fa33375698a245a2a663de9fe280aa24f9de4cb962f91b8c`

## Retrieval Guidance

- Use When: Look up client-library functions, return values, call ordering, and C API behavior.
- Retrieval Keywords: libpq API, PGconn, PGresult, PQconnectdb, PQexec, PQsendQuery, pipeline mode, COPY protocol, lo_open
- Follow-up Guidance: Use the diagnostic or cancellation records when the question is about failure confirmation or interrupting a running query.
- Classification Note: These sections are API reference material for libpq functions, result objects, command submission, COPY handling, large-object calls, and general client-library behavior.

## Official Source Content

## Database Connection Control Functions

The following functions deal with making a connection to a
PostgreSQL backend server.  An
application program can have several backend connections open at
one time.  (One reason to do that is to access more than one
database.)  Each connection is represented by a
`PGconn` object, which
is obtained from the function [libpq-PQconnectdb](#libpq-PQconnectdb),
[libpq-PQconnectdbParams](#libpq-PQconnectdbParams), or
[libpq-PQsetdbLogin](#libpq-PQsetdbLogin).  Note that these functions will always
return a non-null object pointer, unless perhaps there is too
little memory even to allocate the `PGconn` object.
The [libpq-PQstatus](#libpq-PQstatus) function should be called to check
the return value for a successful connection before queries are sent
via the connection object.

> **Warning:**

> If untrusted users have access to a database that has not adopted a
> [secure schema usage pattern](#ddl-schemas-patterns),
> begin each session by removing publicly-writable schemas from
> `search_path`.  One can set parameter key
> word `options` to
> value `-csearch_path=`.  Alternately, one can
> issue `PQexec(`conn`, "SELECT
> pg_catalog.set_config('search_path', '', false)")` after
> connecting.  This consideration is not specific
> to libpq; it applies to every interface for
> executing arbitrary SQL commands.
>

> **Warning:**

> On Unix, forking a process with open libpq connections can lead to
> unpredictable results because the parent and child processes share
> the same sockets and operating system resources.  For this reason,
> such usage is not recommended, though doing an `exec` from
> the child process to load a new executable is safe.
>

**`PQconnectdbParams`**
: Makes a new connection to the database server.

```
PGconn *PQconnectdbParams(const char * const *keywords,
const char * const *values,
int expand_dbname);
```

This function opens a new database connection using the parameters taken
from two `NULL`-terminated arrays. The first,
`keywords`, is defined as an array of strings, each one
being a key word. The second, `values`, gives the value
for each key word. Unlike [libpq-PQsetdbLogin](#libpq-PQsetdbLogin) below, the parameter
set can be extended without changing the function signature, so use of
this function (or its nonblocking analogs [libpq-PQconnectStartParams](#libpq-PQconnectStartParams)
and `PQconnectPoll`) is preferred for new application
programming.

The currently recognized parameter key words are listed in
[libpq-paramkeywords](#libpq-paramkeywords).

The passed arrays can be empty to use all default parameters, or can
contain one or more parameter settings. They must be matched in length.
Processing will stop at the first `NULL` entry
in the `keywords` array.
Also, if the `values` entry associated with a
non-`NULL` `keywords` entry is
`NULL` or an empty string, that entry is ignored and
processing continues with the next pair of array entries.

When `expand_dbname` is non-zero, the value for
the first dbname key word is checked to see
if it is a *connection string*.  If so, it
is "expanded" into the individual connection
parameters extracted from the string.  The value is considered to
be a connection string, rather than just a database name, if it
contains an equal sign (`=`) or it begins with a
URI scheme designator.  (More details on connection string formats
appear in [libpq-connstring](#libpq-connstring).)  Only the first
occurrence of dbname is treated in this way;
any subsequent dbname parameter is processed
as a plain database name.

In general the parameter arrays are processed from start to end.
If any key word is repeated, the last value (that is
not `NULL` or empty) is used.  This rule applies in
particular when a key word found in a connection string conflicts
with one appearing in the `keywords` array.  Thus,
the programmer may determine whether array entries can override or
be overridden by values taken from a connection string.  Array
entries appearing before an expanded dbname
entry can be overridden by fields of the connection string, and in
turn those fields are overridden by array entries appearing
after dbname (but, again, only if those
entries supply non-empty values).

After processing all the array entries and any expanded connection
string, any connection parameters that remain unset are filled with
default values.  If an unset parameter's corresponding environment
variable (see [libpq-envars](#libpq-envars)) is set, its value is
used.  If the environment variable is not set either, then the
parameter's built-in default value is used.

**`PQconnectdb`**
: Makes a new connection to the database server.

```
PGconn *PQconnectdb(const char *conninfo);
```

This function opens a new database connection using the parameters taken
from the string `conninfo`.

The passed string can be empty to use all default parameters, or it can
contain one or more parameter settings separated by whitespace,
or it can contain a URI.
See [libpq-connstring](#libpq-connstring) for details.

**`PQsetdbLogin`**
: Makes a new connection to the database server.

```
PGconn *PQsetdbLogin(const char *pghost,
const char *pgport,
const char *pgoptions,
const char *pgtty,
const char *dbName,
const char *login,
const char *pwd);
```

This is the predecessor of [libpq-PQconnectdb](#libpq-PQconnectdb) with a fixed
set of parameters.  It has the same functionality except that the
missing parameters will always take on default values.  Write `NULL` or an
empty string for any one of the fixed parameters that is to be defaulted.

If the dbName contains
an `=` sign or has a valid connection URI prefix, it
is taken as a conninfo string in exactly the same way as
if it had been passed to [libpq-PQconnectdb](#libpq-PQconnectdb), and the remaining
parameters are then applied as specified for [libpq-PQconnectdbParams](#libpq-PQconnectdbParams).

`pgtty` is no longer used and any value passed will
be ignored.

**`PQsetdb`**
: Makes a new connection to the database server.

```
PGconn *PQsetdb(char *pghost,
char *pgport,
char *pgoptions,
char *pgtty,
char *dbName);
```

This is a macro that calls [libpq-PQsetdbLogin](#libpq-PQsetdbLogin) with null pointers
for the login and pwd parameters.  It is provided
for backward compatibility with very old programs.

**`PQconnectStartParams`**
: Make a connection to the database server in a nonblocking manner.

```
PGconn *PQconnectStartParams(const char * const *keywords,
const char * const *values,
int expand_dbname);

PGconn *PQconnectStart(const char *conninfo);

PostgresPollingStatusType PQconnectPoll(PGconn *conn);
```

These three functions are used to open a connection to a database server such
that your application's thread of execution is not blocked on remote I/O
whilst doing so. The point of this approach is that the waits for I/O to
complete can occur in the application's main loop, rather than down inside
[libpq-PQconnectdbParams](#libpq-PQconnectdbParams) or [libpq-PQconnectdb](#libpq-PQconnectdb), and so the
application can manage this operation in parallel with other activities.

With [libpq-PQconnectStartParams](#libpq-PQconnectStartParams), the database connection is made
using the parameters taken from the `keywords` and
`values` arrays, and controlled by `expand_dbname`,
as described above for [libpq-PQconnectdbParams](#libpq-PQconnectdbParams).

With `PQconnectStart`, the database connection is made
using the parameters taken from the string `conninfo` as
described above for [libpq-PQconnectdb](#libpq-PQconnectdb).

Neither [libpq-PQconnectStartParams](#libpq-PQconnectStartParams) nor `PQconnectStart`
nor `PQconnectPoll` will block, so long as a number of
restrictions are met:

- The `hostaddr` parameter must be used appropriately
to prevent DNS queries from being made.  See the documentation of
this parameter in [libpq-paramkeywords](#libpq-paramkeywords) for details.
- If you call [libpq-PQtrace](#libpq-PQtrace), ensure that the stream object
into which you trace will not block.
- You must ensure that the socket is in the appropriate state
before calling `PQconnectPoll`, as described below.

To begin a nonblocking connection request,
call `PQconnectStart`
or [libpq-PQconnectStartParams](#libpq-PQconnectStartParams).  If the result is null,
then libpq has been unable to allocate a
new `PGconn` structure.  Otherwise, a
valid `PGconn` pointer is returned (though not
yet representing a valid connection to the database).  Next
call `PQstatus(conn)`.  If the result
is `CONNECTION_BAD`, the connection attempt has already
failed, typically because of invalid connection parameters.

If `PQconnectStart`
or [libpq-PQconnectStartParams](#libpq-PQconnectStartParams) succeeds, the next stage
is to poll libpq so that it can proceed with
the connection sequence.
Use `PQsocket(conn)` to obtain the descriptor of the
socket underlying the database connection.
(Caution: do not assume that the socket remains the same
across `PQconnectPoll` calls.)
Loop thus: If `PQconnectPoll(conn)` last returned
`PGRES_POLLING_READING`, wait until the socket is ready to
read (as indicated by `select()`, `poll()`, or
similar system function).
Then call `PQconnectPoll(conn)` again.
Conversely, if `PQconnectPoll(conn)` last returned
`PGRES_POLLING_WRITING`, wait until the socket is ready
to write, then call `PQconnectPoll(conn)` again.
On the first iteration, i.e., if you have yet to call
`PQconnectPoll`, behave as if it last returned
`PGRES_POLLING_WRITING`.  Continue this loop until
`PQconnectPoll(conn)` returns
`PGRES_POLLING_FAILED`, indicating the connection procedure
has failed, or `PGRES_POLLING_OK`, indicating the connection
has been successfully made.

At any time during connection, the status of the connection can be
checked by calling [libpq-PQstatus](#libpq-PQstatus). If this call returns `CONNECTION_BAD`, then the
connection procedure has failed; if the call returns `CONNECTION_OK`, then the
connection is ready.  Both of these states are equally detectable
from the return value of `PQconnectPoll`, described above. Other states might also occur
during (and only during) an asynchronous connection procedure. These
indicate the current stage of the connection procedure and might be useful
to provide feedback to the user for example. These statuses are:

`CONNECTION_STARTED`

Waiting for connection to be made.

**`CONNECTION_MADE`**
: Connection OK; waiting to send.

**`CONNECTION_AWAITING_RESPONSE`**
: Waiting for a response from the server.

**`CONNECTION_AUTH_OK`**
: Received authentication; waiting for backend start-up to finish.

**`CONNECTION_SSL_STARTUP`**
: Negotiating SSL encryption.

**`CONNECTION_SETENV`**
: Negotiating environment-driven parameter settings.

**`CONNECTION_CHECK_WRITABLE`**
: Checking if connection is able to handle write transactions.

**`CONNECTION_CONSUME`**
: Consuming any remaining response messages on connection.

Note that, although these constants will remain (in order to maintain
compatibility), an application should never rely upon these occurring in a
particular order, or at all, or on the status always being one of these
documented values. An application might do something like this:

```
switch(PQstatus(conn))
{
case CONNECTION_STARTED:
feedback = "Connecting...";
break;

case CONNECTION_MADE:
feedback = "Connected to server...";
break;
.
.
.
default:
feedback = "Connecting...";
}
```

The `connect_timeout` connection parameter is ignored
when using `PQconnectPoll`; it is the application's
responsibility to decide whether an excessive amount of time has elapsed.
Otherwise, `PQconnectStart` followed by a
`PQconnectPoll` loop is equivalent to
[libpq-PQconnectdb](#libpq-PQconnectdb).

Note that when `PQconnectStart`
or [libpq-PQconnectStartParams](#libpq-PQconnectStartParams) returns a non-null
pointer, you must call [libpq-PQfinish](#libpq-PQfinish) when you are
finished with it, in order to dispose of the structure and any
associated memory blocks.  This must be done even if the connection
attempt fails or is abandoned.

`PQconndefaults`

Returns the default connection options.

```
PQconninfoOption *PQconndefaults(void);

typedef struct
{
char   *keyword;   /* The keyword of the option */
char   *envvar;    /* Fallback environment variable name */
char   *compiled;  /* Fallback compiled in default value */
char   *val;       /* Option's current value, or NULL */
char   *label;     /* Label for field in connect dialog */
char   *dispchar;  /* Indicates how to display this field
in a connect dialog. Values are:
""        Display entered value as is
"*"       Password field - hide value
"D"       Debug option - don't show by default */
int     dispsize;  /* Field size in characters for dialog */
} PQconninfoOption;
```

Returns a connection options array.  This can be used to determine
all possible [libpq-PQconnectdb](#libpq-PQconnectdb) options and their
current default values.  The return value points to an array of
`PQconninfoOption` structures, which ends
with an entry having a null `keyword` pointer.  The
null pointer is returned if memory could not be allocated. Note that
the current default values (`val` fields)
will depend on environment variables and other context.  A
missing or invalid service file will be silently ignored.  Callers
must treat the connection options data as read-only.

After processing the options array, free it by passing it to
[libpq-PQconninfoFree](#libpq-PQconninfoFree).  If this is not done, a small amount of memory
is leaked for each call to [libpq-PQconndefaults](#libpq-PQconndefaults).

`PQconninfo`

Returns the connection options used by a live connection.

```
PQconninfoOption *PQconninfo(PGconn *conn);
```

Returns a connection options array.  This can be used to determine
all possible [libpq-PQconnectdb](#libpq-PQconnectdb) options and the
values that were used to connect to the server. The return
value points to an array of `PQconninfoOption`
structures, which ends with an entry having a null `keyword`
pointer. All notes above for [libpq-PQconndefaults](#libpq-PQconndefaults) also
apply to the result of [libpq-PQconninfo](#libpq-PQconninfo).

`PQconninfoParse`

Returns parsed connection options from the provided connection string.

```
PQconninfoOption *PQconninfoParse(const char *conninfo, char **errmsg);
```

Parses a connection string and returns the resulting options as an
array; or returns `NULL` if there is a problem with the connection
string.  This function can be used to extract
the [libpq-PQconnectdb](#libpq-PQconnectdb) options in the provided
connection string.  The return value points to an array of
`PQconninfoOption` structures, which ends
with an entry having a null `keyword` pointer.

All legal options will be present in the result array, but the
`PQconninfoOption` for any option not present
in the connection string will have `val` set to
`NULL`; default values are not inserted.

If `errmsg` is not `NULL`, then `*errmsg` is set
to `NULL` on success, else to a `malloc`'d error string explaining
the problem.  (It is also possible for `*errmsg` to be
set to `NULL` and the function to return `NULL`;
this indicates an out-of-memory condition.)

After processing the options array, free it by passing it to
[libpq-PQconninfoFree](#libpq-PQconninfoFree).  If this is not done, some memory
is leaked for each call to [libpq-PQconninfoParse](#libpq-PQconninfoParse).
Conversely, if an error occurs and `errmsg` is not `NULL`,
be sure to free the error string using [libpq-PQfreemem](#libpq-PQfreemem).

`PQfinish`

Closes  the  connection to the server.  Also frees
memory used by the `PGconn` object.

```
void PQfinish(PGconn *conn);
```

Note that even if the server connection attempt fails (as
indicated by [libpq-PQstatus](#libpq-PQstatus)), the application should call [libpq-PQfinish](#libpq-PQfinish)
to free the memory used by the `PGconn` object.
The `PGconn` pointer must not be used again after
[libpq-PQfinish](#libpq-PQfinish) has been called.

`PQreset`

Resets the communication channel to the server.

```
void PQreset(PGconn *conn);
```

This function will close the connection
to the server and attempt to establish a new
connection, using all the same
parameters previously used.  This might be useful for
error recovery if a working connection is lost.

`PQresetStart`
`PQresetPoll`

Reset the communication channel to the server, in a nonblocking manner.

```
int PQresetStart(PGconn *conn);

PostgresPollingStatusType PQresetPoll(PGconn *conn);
```

These functions will close the connection to the server and attempt to
establish a new connection, using all the same
parameters previously used. This can be useful for error recovery if a
working connection is lost. They differ from [libpq-PQreset](#libpq-PQreset) (above) in that they
act in a nonblocking manner. These functions suffer from the same
restrictions as [libpq-PQconnectStartParams](#libpq-PQconnectStartParams), `PQconnectStart`
and `PQconnectPoll`.

To initiate a connection reset, call
[libpq-PQresetStart](#libpq-PQresetStart). If it returns 0, the reset has
failed. If it returns 1, poll the reset using
`PQresetPoll` in exactly the same way as you
would create the connection using `PQconnectPoll`.

`PQpingParams`

[libpq-PQpingParams](#libpq-PQpingParams) reports the status of the
server.  It accepts connection parameters identical to those of
[libpq-PQconnectdbParams](#libpq-PQconnectdbParams), described above.  It is not
necessary to supply correct user name, password, or database name
values to obtain the server status; however, if incorrect values
are provided, the server will log a failed connection attempt.

```
PGPing PQpingParams(const char * const *keywords,
const char * const *values,
int expand_dbname);
```

The function returns one of the following values:

**`PQPING_OK`**
: The server is running and appears to be accepting connections.

**`PQPING_REJECT`**
: The server is running but is in a state that disallows connections
(startup, shutdown, or crash recovery).

**`PQPING_NO_RESPONSE`**
: The server could not be contacted.  This might indicate that the
server is not running, or that there is something wrong with the
given connection parameters (for example, wrong port number), or
that there is a network connectivity problem (for example, a
firewall blocking the connection request).

**`PQPING_NO_ATTEMPT`**
: No attempt was made to contact the server, because the supplied
parameters were obviously incorrect or there was some client-side
problem (for example, out of memory).

`PQping`

[libpq-PQping](#libpq-PQping) reports the status of the
server.  It accepts connection parameters identical to those of
[libpq-PQconnectdb](#libpq-PQconnectdb), described above.  It is not
necessary to supply correct user name, password, or database name
values to obtain the server status; however, if incorrect values
are provided, the server will log a failed connection attempt.

```
PGPing PQping(const char *conninfo);
```

The return values are the same as for [libpq-PQpingParams](#libpq-PQpingParams).

`PQsetSSLKeyPassHook_OpenSSL`

`PQsetSSLKeyPassHook_OpenSSL` lets an application override
libpq's [default
handling of encrypted client certificate key files](#libpq-ssl-clientcert) using
[libpq-connect-sslpassword](#libpq-connect-sslpassword) or interactive prompting.

```
void PQsetSSLKeyPassHook_OpenSSL(PQsslKeyPassHook_OpenSSL_type hook);
```

The application passes a pointer to a callback function with signature:

```
int callback_fn(char *buf, int size, PGconn *conn);
```

which libpq will then call
*instead of* its default
`PQdefaultSSLKeyPassHook_OpenSSL` handler. The
callback should determine the password for the key and copy it to
result-buffer
buf of size

size. The string in
buf
must be null-terminated. The callback must return the length of the
password stored in
buf excluding the null
terminator. On failure, the callback should set
`buf[0] = '\0'` and return 0. See
`PQdefaultSSLKeyPassHook_OpenSSL` in
libpq's source code for an example.

If the user specified an explicit key location,
its path will be in `conn->sslkey` when the callback
is invoked. This will be empty if the default key path is being used.
For keys that are engine specifiers, it is up to engine implementations
whether they use the OpenSSL password
callback or define their own handling.

The app callback may choose to delegate unhandled cases to
`PQdefaultSSLKeyPassHook_OpenSSL`,
or call it first and try something else if it returns 0, or completely override it.

The callback *must not* escape normal flow control with exceptions,
`longjmp(...)`, etc. It must return normally.

`PQgetSSLKeyPassHook_OpenSSL`

`PQgetSSLKeyPassHook_OpenSSL` returns the current
client certificate key password hook, or `NULL`
if none has been set.

```
PQsslKeyPassHook_OpenSSL_type PQgetSSLKeyPassHook_OpenSSL(void);
```

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

## Command Execution Functions

Once a connection to a database server has been successfully
established, the functions described here are used to perform
SQL queries and commands.

### Main Functions

**`PQexec`**
: Submits a command to the server and waits for the result.

```
PGresult *PQexec(PGconn *conn, const char *command);
```

Returns a `PGresult` pointer or possibly a null
pointer.  A non-null pointer will generally be returned except in
out-of-memory conditions or serious errors such as inability to send
the command to the server.  The [libpq-PQresultStatus](#libpq-PQresultStatus) function
should be called to check the return value for any errors (including
the value of a null pointer, in which case it will return
`PGRES_FATAL_ERROR`).  Use
[libpq-PQerrorMessage](#libpq-PQerrorMessage) to get more information about such
errors.

The command string can include multiple SQL commands
(separated by semicolons).  Multiple queries sent in a single
[libpq-PQexec](#libpq-PQexec) call are processed in a single transaction, unless
there are explicit `BEGIN`/`COMMIT`
commands included in the query string to divide it into multiple
transactions.  (See [protocol-flow-multi-statement](#protocol-flow-multi-statement)
for more details about how the server handles multi-query strings.)
Note however that the returned
`PGresult` structure describes only the result
of the last command executed from the string.  Should one of the
commands fail, processing of the string stops with it and the returned
`PGresult` describes the error condition.

**`PQexecParams`**
: Submits a command to the server and waits for the result,
with the ability to pass parameters separately from the SQL
command text.

```
PGresult *PQexecParams(PGconn *conn,
const char *command,
int nParams,
const Oid *paramTypes,
const char * const *paramValues,
const int *paramLengths,
const int *paramFormats,
int resultFormat);
```

[libpq-PQexecParams](#libpq-PQexecParams) is like [libpq-PQexec](#libpq-PQexec), but offers additional
functionality: parameter values can be specified separately from the command
string proper, and query results can be requested in either text or binary
format.

The function arguments are:

conn

The connection object to send the command through.

**command**
: The SQL command string to be executed. If parameters are used,
they are referred to in the command string as `$1`,
`$2`, etc.

**nParams**
: The number of parameters supplied; it is the length of the arrays
paramTypes[], paramValues[],
paramLengths[], and paramFormats[]. (The
array pointers can be `NULL` when nParams
is zero.)

**paramTypes[]**
: Specifies, by OID, the data types to be assigned to the
parameter symbols.  If paramTypes is
`NULL`, or any particular element in the array
is zero, the server infers a data type for the parameter symbol
in the same way it would do for an untyped literal string.

**paramValues[]**
: Specifies the actual values of the parameters.  A null pointer
in this array means the corresponding parameter is null;
otherwise the pointer points to a zero-terminated text string
(for text format) or binary data in the format expected by the
server (for binary format).

**paramLengths[]**
: Specifies the actual data lengths of binary-format parameters.
It is ignored for null parameters and text-format parameters.
The array pointer can be null when there are no binary parameters.

**paramFormats[]**
: Specifies whether parameters are text (put a zero in the
array entry for the corresponding parameter) or binary (put
a one in the array entry for the corresponding parameter).
If the array pointer is null then all parameters are presumed
to be text strings.

Values passed in binary format require knowledge of
the internal representation expected by the backend.
For example, integers must be passed in network byte
order.  Passing `numeric` values requires
knowledge of the server storage format, as implemented
in
`src/backend/utils/adt/numeric.c::numeric_send()` and
`src/backend/utils/adt/numeric.c::numeric_recv()`.

**resultFormat**
: Specify zero to obtain results in text format, or one to obtain
results in binary format.  (There is not currently a provision
to obtain different result columns in different formats,
although that is possible in the underlying protocol.)

The primary advantage of [libpq-PQexecParams](#libpq-PQexecParams) over
[libpq-PQexec](#libpq-PQexec) is that parameter values can be separated from the
command string, thus avoiding the need for tedious and error-prone
quoting and escaping.

Unlike [libpq-PQexec](#libpq-PQexec), [libpq-PQexecParams](#libpq-PQexecParams) allows at most
one SQL command in the given string.  (There can be semicolons in it,
but not more than one nonempty command.)  This is a limitation of the
underlying protocol, but has some usefulness as an extra defense against
SQL-injection attacks.

> **Tip:**

> Specifying parameter types via OIDs is tedious, particularly if you prefer
> not to hard-wire particular OID values into your program.  However, you can
> avoid doing so even in cases where the server by itself cannot determine the
> type of the parameter, or chooses a different type than you want.  In the
> SQL command text, attach an explicit cast to the parameter symbol to show what
> data type you will send.  For example:
> ```
> SELECT * FROM mytable WHERE x = $1::bigint;
> ```
> This forces parameter `$1` to be treated as `bigint`, whereas
> by default it would be assigned the same type as `x`.  Forcing the
> parameter type decision, either this way or by specifying a numeric type OID,
> is strongly recommended when sending parameter values in binary format, because
> binary format has less redundancy than text format and so there is less chance
> that the server will detect a type mismatch mistake for you.
>

**`PQprepare`**
: Submits a request to create a prepared statement with the
given parameters, and waits for completion.

```
PGresult *PQprepare(PGconn *conn,
const char *stmtName,
const char *query,
int nParams,
const Oid *paramTypes);
```

[libpq-PQprepare](#libpq-PQprepare) creates a prepared statement for later
execution with [libpq-PQexecPrepared](#libpq-PQexecPrepared).  This feature allows
commands to be executed repeatedly without being parsed and
planned each time;  see [sql-prepare](#sql-prepare) for details.

The function creates a prepared statement named
stmtName from the query string, which
must contain a single SQL command.  stmtName can be
`""` to create an unnamed statement, in which case any
pre-existing unnamed statement is automatically replaced; otherwise
it is an error if the statement name is already defined in the
current session.  If any parameters are used, they are referred
to in the query as `$1`, `$2`, etc.
nParams is the number of parameters for which types
are pre-specified in the array paramTypes[].  (The
array pointer can be `NULL` when
nParams is zero.) paramTypes[]
specifies, by OID, the data types to be assigned to the parameter
symbols.  If paramTypes is `NULL`,
or any particular element in the array is zero, the server assigns
a data type to the parameter symbol in the same way it would do
for an untyped literal string.  Also, the query can use parameter
symbols with numbers higher than nParams; data types
will be inferred for these symbols as well.  (See
[libpq-PQdescribePrepared](#libpq-PQdescribePrepared) for a means to find out
what data types were inferred.)

As with [libpq-PQexec](#libpq-PQexec), the result is normally a
`PGresult` object whose contents indicate
server-side success or failure.  A null result indicates
out-of-memory or inability to send the command at all.  Use
[libpq-PQerrorMessage](#libpq-PQerrorMessage) to get more information about
such errors.

Prepared statements for use with [libpq-PQexecPrepared](#libpq-PQexecPrepared) can also
be created by executing SQL [sql-prepare](#sql-prepare)
statements.  Also, although there is no libpq
function for deleting a prepared statement, the SQL [sql-deallocate](#sql-deallocate) statement
can be used for that purpose.

**`PQexecPrepared`**
: Sends a request to execute a prepared statement with given
parameters, and waits for the result.

```
PGresult *PQexecPrepared(PGconn *conn,
const char *stmtName,
int nParams,
const char * const *paramValues,
const int *paramLengths,
const int *paramFormats,
int resultFormat);
```

[libpq-PQexecPrepared](#libpq-PQexecPrepared) is like [libpq-PQexecParams](#libpq-PQexecParams),
but the command to be executed is specified by naming a
previously-prepared statement, instead of giving a query string.
This feature allows commands that will be used repeatedly to be
parsed and planned just once, rather than each time they are
executed.  The statement must have been prepared previously in
the current session.

The parameters are identical to [libpq-PQexecParams](#libpq-PQexecParams), except that the
name of a prepared statement is given instead of a query string, and the
paramTypes[] parameter is not present (it is not needed since
the prepared statement's parameter types were determined when it was created).

**`PQdescribePrepared`**
: Submits a request to obtain information about the specified
prepared statement, and waits for completion.

```
PGresult *PQdescribePrepared(PGconn *conn, const char *stmtName);
```

[libpq-PQdescribePrepared](#libpq-PQdescribePrepared) allows an application to obtain
information about a previously prepared statement.

stmtName can be `""` or `NULL` to reference
the unnamed statement, otherwise it must be the name of an existing
prepared statement.  On success, a `PGresult` with
status `PGRES_COMMAND_OK` is returned.  The
functions [libpq-PQnparams](#libpq-PQnparams) and
[libpq-PQparamtype](#libpq-PQparamtype) can be applied to this
`PGresult` to obtain information about the parameters
of the prepared statement, and the functions
[libpq-PQnfields](#libpq-PQnfields), [libpq-PQfname](#libpq-PQfname),
[libpq-PQftype](#libpq-PQftype), etc. provide information about the
result columns (if any) of the statement.

**`PQdescribePortal`**
: Submits a request to obtain information about the specified
portal, and waits for completion.

```
PGresult *PQdescribePortal(PGconn *conn, const char *portalName);
```

[libpq-PQdescribePortal](#libpq-PQdescribePortal) allows an application to obtain
information about a previously created portal.
(libpq does not provide any direct access to
portals, but you can use this function to inspect the properties
of a cursor created with a `DECLARE CURSOR` SQL command.)

portalName can be `""` or `NULL` to reference
the unnamed portal, otherwise it must be the name of an existing
portal.  On success, a `PGresult` with status
`PGRES_COMMAND_OK` is returned.  The functions
[libpq-PQnfields](#libpq-PQnfields), [libpq-PQfname](#libpq-PQfname),
[libpq-PQftype](#libpq-PQftype), etc. can be applied to the
`PGresult` to obtain information about the result
columns (if any) of the portal.

The `PGresult`
structure encapsulates the result returned by the server.
libpq application programmers should be
careful to maintain the `PGresult` abstraction.
Use the accessor functions below to get at the contents of
`PGresult`.  Avoid directly referencing the
fields of the `PGresult` structure because they
are subject to change in the future.

**`PQresultStatus`**
: Returns the result status of the command.

```
ExecStatusType PQresultStatus(const PGresult *res);
```

[libpq-PQresultStatus](#libpq-PQresultStatus) can return one of the following values:

`PGRES_EMPTY_QUERY`

The string sent to the server was empty.

**`PGRES_COMMAND_OK`**
: Successful completion of a command returning no data.

**`PGRES_TUPLES_OK`**
: Successful completion of a command returning data (such as
a `SELECT` or `SHOW`).

**`PGRES_COPY_OUT`**
: Copy Out (from server) data transfer started.

**`PGRES_COPY_IN`**
: Copy In (to server) data transfer started.

**`PGRES_BAD_RESPONSE`**
: The server's response was not understood.

**`PGRES_NONFATAL_ERROR`**
: A nonfatal error (a notice or warning) occurred.

**`PGRES_FATAL_ERROR`**
: A fatal error occurred.

**`PGRES_COPY_BOTH`**
: Copy In/Out (to and from server) data transfer started.  This
feature is currently used only for streaming replication,
so this status should not occur in ordinary applications.

**`PGRES_SINGLE_TUPLE`**
: The `PGresult` contains a single result tuple
from the current command.  This status occurs only when
single-row mode has been selected for the query
(see [libpq-single-row-mode](#libpq-single-row-mode)).

**`PGRES_PIPELINE_SYNC`**
: The `PGresult` represents a
synchronization point in pipeline mode, requested by
[libpq-PQpipelineSync](#libpq-PQpipelineSync).
This status occurs only when pipeline mode has been selected.

**`PGRES_PIPELINE_ABORTED`**
: The `PGresult` represents a pipeline that has
received an error from the server.  `PQgetResult`
must be called repeatedly, and each time it will return this status code
until the end of the current pipeline, at which point it will return
`PGRES_PIPELINE_SYNC` and normal processing can
resume.

If the result status is `PGRES_TUPLES_OK` or
`PGRES_SINGLE_TUPLE`, then
the functions described below can be used to retrieve the rows
returned by the query.  Note that a `SELECT`
command that happens to retrieve zero rows still shows
`PGRES_TUPLES_OK`.
`PGRES_COMMAND_OK` is for commands that can never
return rows (`INSERT` or `UPDATE`
without a `RETURNING` clause,
etc.). A response of `PGRES_EMPTY_QUERY` might
indicate a bug in the client software.

A result of status `PGRES_NONFATAL_ERROR` will
never be returned directly by [libpq-PQexec](#libpq-PQexec) or other
query execution functions; results of this kind are instead passed
to the notice processor (see [libpq-notice-processing](#libpq-notice-processing)).

`PQresStatus`

Converts the enumerated type returned by
[libpq-PQresultStatus](#libpq-PQresultStatus) into a string constant describing the
status code. The caller should not free the result.

```
char *PQresStatus(ExecStatusType status);
```

`PQresultErrorMessage`

Returns the error message associated with the command, or an empty string
if there was no error.

```
char *PQresultErrorMessage(const PGresult *res);
```

If there was an error, the returned string will include a trailing
newline.  The caller should not free the result directly. It will
be freed when the associated `PGresult` handle is
passed to [libpq-PQclear](#libpq-PQclear).

Immediately following a [libpq-PQexec](#libpq-PQexec) or
[libpq-PQgetResult](#libpq-PQgetResult) call,
[libpq-PQerrorMessage](#libpq-PQerrorMessage) (on the connection) will return
the same string as [libpq-PQresultErrorMessage](#libpq-PQresultErrorMessage) (on
the result).  However, a `PGresult` will
retain its error message until destroyed, whereas the connection's
error message will change when subsequent operations are done.
Use [libpq-PQresultErrorMessage](#libpq-PQresultErrorMessage) when you want to
know the status associated with a particular
`PGresult`; use
[libpq-PQerrorMessage](#libpq-PQerrorMessage) when you want to know the
status from the latest operation on the connection.

`PQresultVerboseErrorMessage`

Returns a reformatted version of the error message associated with
a `PGresult` object.

```
char *PQresultVerboseErrorMessage(const PGresult *res,
PGVerbosity verbosity,
PGContextVisibility show_context);
```

In some situations a client might wish to obtain a more detailed
version of a previously-reported error.
[libpq-PQresultVerboseErrorMessage](#libpq-PQresultVerboseErrorMessage) addresses this need
by computing the message that would have been produced
by [libpq-PQresultErrorMessage](#libpq-PQresultErrorMessage) if the specified
verbosity settings had been in effect for the connection when the
given `PGresult` was generated.  If
the `PGresult` is not an error result,
"PGresult is not an error result" is reported instead.
The returned string includes a trailing newline.

Unlike most other functions for extracting data from
a `PGresult`, the result of this function is a freshly
allocated string.  The caller must free it
using `PQfreemem()` when the string is no longer needed.

A NULL return is possible if there is insufficient memory.

`PQresultErrorField`

Returns an individual field of an error report.

```
char *PQresultErrorField(const PGresult *res, int fieldcode);
```

fieldcode is an error field identifier; see the symbols
listed below.  `NULL` is returned if the
`PGresult` is not an error or warning result,
or does not include the specified field.  Field values will normally
not include a trailing newline. The caller should not free the
result directly. It will be freed when the
associated `PGresult` handle is passed to
[libpq-PQclear](#libpq-PQclear).

The following field codes are available:

**`PG_DIAG_SEVERITY`**
: The severity; the field contents are `ERROR`,
`FATAL`, or `PANIC` (in an error message),
or `WARNING`, `NOTICE`, `DEBUG`,
`INFO`, or `LOG` (in a notice message), or
a localized translation of one of these.  Always present.

**`PG_DIAG_SEVERITY_NONLOCALIZED`**
: The severity; the field contents are `ERROR`,
`FATAL`, or `PANIC` (in an error message),
or `WARNING`, `NOTICE`, `DEBUG`,
`INFO`, or `LOG` (in a notice message).
This is identical to the `PG_DIAG_SEVERITY` field except
that the contents are never localized.  This is present only in
reports generated by PostgreSQL versions 9.6
and later.

**`PG_DIAG_SQLSTATE`**
: The SQLSTATE code for the error. The SQLSTATE code identifies
the type of error that has occurred; it can be used by
front-end applications to perform specific operations (such
as error handling) in response to a particular database error.
For a list of the possible SQLSTATE codes, see [errcodes-appendix](#errcodes-appendix). This field is not localizable,
and is always present.

**`PG_DIAG_MESSAGE_PRIMARY`**
: The primary human-readable error message (typically one line).
Always present.

**`PG_DIAG_MESSAGE_DETAIL`**
: Detail: an optional secondary error message carrying more
detail about the problem.  Might run to multiple lines.

**`PG_DIAG_MESSAGE_HINT`**
: Hint: an optional suggestion what to do about the problem.
This is intended to differ from detail in that it offers advice
(potentially inappropriate) rather than hard facts.  Might
run to multiple lines.

**`PG_DIAG_STATEMENT_POSITION`**
: A string containing a decimal integer indicating an error cursor
position as an index into the original statement string.  The
first character has index 1, and positions are measured in
characters not bytes.

**`PG_DIAG_INTERNAL_POSITION`**
: This is defined the same as the
`PG_DIAG_STATEMENT_POSITION` field, but it is used
when the cursor position refers to an internally generated
command rather than the one submitted by the client.  The
`PG_DIAG_INTERNAL_QUERY` field will always appear when
this field appears.

**`PG_DIAG_INTERNAL_QUERY`**
: The text of a failed internally-generated command.  This could
be, for example, an SQL query issued by a PL/pgSQL function.

**`PG_DIAG_CONTEXT`**
: An indication of the context in which the error occurred.
Presently this includes a call stack traceback of active
procedural language functions and internally-generated queries.
The trace is one entry per line, most recent first.

**`PG_DIAG_SCHEMA_NAME`**
: If the error was associated with a specific database object,
the name of the schema containing that object, if any.

**`PG_DIAG_TABLE_NAME`**
: If the error was associated with a specific table, the name of the
table.  (Refer to the schema name field for the name of the
table's schema.)

**`PG_DIAG_COLUMN_NAME`**
: If the error was associated with a specific table column, the name
of the column.  (Refer to the schema and table name fields to
identify the table.)

**`PG_DIAG_DATATYPE_NAME`**
: If the error was associated with a specific data type, the name of
the data type.  (Refer to the schema name field for the name of
the data type's schema.)

**`PG_DIAG_CONSTRAINT_NAME`**
: If the error was associated with a specific constraint, the name
of the constraint.  Refer to fields listed above for the
associated table or domain.  (For this purpose, indexes are
treated as constraints, even if they weren't created with
constraint syntax.)

**`PG_DIAG_SOURCE_FILE`**
: The file name of the source-code location where the error was
reported.

**`PG_DIAG_SOURCE_LINE`**
: The line number of the source-code location where the error
was reported.

**`PG_DIAG_SOURCE_FUNCTION`**
: The name of the source-code function reporting the error.

> **Note:**

> The fields for schema name, table name, column name, data type name,
> and constraint name are supplied only for a limited number of error
> types; see [errcodes-appendix](#errcodes-appendix).  Do not assume that
> the presence of any of these fields guarantees the presence of
> another field.  Core error sources observe the interrelationships
> noted above, but user-defined functions may use these fields in other
> ways.  In the same vein, do not assume that these fields denote
> contemporary objects in the current database.
>

The client is responsible for formatting displayed information to meet
its needs; in particular it should break long lines as needed.
Newline characters appearing in the error message fields should be
treated as paragraph breaks, not line breaks.

Errors generated internally by libpq will
have severity and primary message, but typically no other fields.

Note that error fields are only available from
`PGresult` objects, not
`PGconn` objects; there is no
`PQerrorField` function.

`PQclear`

Frees  the  storage  associated with a
`PGresult`.  Every command result should be
freed via [libpq-PQclear](#libpq-PQclear) when it  is  no  longer
needed.

```
void PQclear(PGresult *res);
```

If the argument is a `NULL` pointer, no operation is
performed.

You can keep a `PGresult` object around for
as long as you need it; it does not go away when you issue a new
command, nor even if you close the connection.  To get rid of it,
you must call [libpq-PQclear](#libpq-PQclear).  Failure to do this
will result in memory leaks in your application.

### Retrieving Query Result Information

These functions are used to extract information from a
`PGresult` object that represents a successful
query result (that is, one that has status
`PGRES_TUPLES_OK` or `PGRES_SINGLE_TUPLE`).
They can also be used to extract
information from a successful Describe operation: a Describe's result
has all the same column information that actual execution of the query
would provide, but it has zero rows.  For objects with other status values,
these functions will act as though the result has zero rows and zero columns.

**`PQntuples`**
: Returns the number of rows (tuples) in the query result.
(Note that `PGresult` objects are limited to no more
than `INT_MAX` rows, so an `int` result is
sufficient.)

```
int PQntuples(const PGresult *res);
```

**`PQnfields`**
: Returns the number of columns (fields) in each row of the query
result.

```
int PQnfields(const PGresult *res);
```

**`PQfname`**
: Returns the column name associated with the given column number.
Column numbers start at 0. The caller should not free the result
directly. It will be freed when the associated
`PGresult` handle is passed to
[libpq-PQclear](#libpq-PQclear).

```
char *PQfname(const PGresult *res,
int column_number);
```

`NULL` is returned if the column number is out of range.

**`PQfnumber`**
: Returns the column number associated with the given column name.

```
int PQfnumber(const PGresult *res,
const char *column_name);
```

-1 is returned if the given name does not match any column.

The given name is treated like an identifier in an SQL command,
that is, it is downcased unless double-quoted.  For example, given
a query result generated from the SQL command:

```
SELECT 1 AS FOO, 2 AS "BAR";
```

we would have the results:

```
PQfname(res, 0)              foo
PQfname(res, 1)              BAR
PQfnumber(res, "FOO")        0
PQfnumber(res, "foo")        0
PQfnumber(res, "BAR")        -1
PQfnumber(res, "\"BAR\"")    1
```

**`PQftable`**
: Returns the OID of the table from which the given column was
fetched.  Column numbers start at 0.

```
Oid PQftable(const PGresult *res,
int column_number);
```

`InvalidOid` is returned if the column number is out of range,
or if the specified column is not a simple reference to a table column.
You can query the system table `pg_class` to determine
exactly which table is referenced.

The type `Oid` and the constant
`InvalidOid` will be defined when you include
the libpq header file. They will both
be some integer type.

**`PQftablecol`**
: Returns the column number (within its table) of the column making
up the specified query result column.  Query-result column numbers
start at 0, but table columns have nonzero numbers.

```
int PQftablecol(const PGresult *res,
int column_number);
```

Zero is returned if the column number is out of range, or if the
specified column is not a simple reference to a table column.

**`PQfformat`**
: Returns the format code indicating the format of the given
column.  Column numbers start at 0.

```
int PQfformat(const PGresult *res,
int column_number);
```

Format code zero indicates textual data representation, while format
code one indicates binary representation.  (Other codes are reserved
for future definition.)

**`PQftype`**
: Returns the data type associated with the given  column number.
The  integer  returned is the internal OID number of the type.
Column numbers start at 0.

```
Oid PQftype(const PGresult *res,
int column_number);
```

You can query the system table `pg_type` to
obtain the names and properties of the various data types. The
OIDs of the built-in data types are defined
in the file `catalog/pg_type_d.h`
in the PostgreSQL
installation's `include` directory.

**`PQfmod`**
: Returns  the type modifier of the column associated with the
given column number.  Column numbers start at 0.

```
int PQfmod(const PGresult *res,
int column_number);
```

The interpretation of modifier values is type-specific; they
typically indicate precision or size limits.  The value -1 is
used to indicate "no information available".  Most data
types do not use modifiers, in which case the value is always
-1.

**`PQfsize`**
: Returns  the  size  in bytes of the column associated with the
given column number.  Column numbers start at 0.

```
int PQfsize(const PGresult *res,
int column_number);
```

[libpq-PQfsize](#libpq-PQfsize) returns the space allocated for this column
in a database row, in other words the size of the server's
internal representation of the data type.  (Accordingly, it is
not really very useful to clients.) A negative value indicates
the data type is variable-length.

**`PQbinaryTuples`**
: Returns 1 if the `PGresult` contains binary data
and 0 if it contains text data.

```
int PQbinaryTuples(const PGresult *res);
```

This function is deprecated (except for its use in connection with
`COPY`), because it is possible for a single
`PGresult` to contain text data in some columns and
binary data in others.  [libpq-PQfformat](#libpq-PQfformat) is preferred.
[libpq-PQbinaryTuples](#libpq-PQbinaryTuples) returns 1 only if all columns of the
result are binary (format 1).

**`PQgetvalue`**
: Returns a single field value of one row of a
`PGresult`.  Row and column numbers start
at 0.  The caller should not free the result directly.  It will
be freed when the associated `PGresult` handle is
passed to [libpq-PQclear](#libpq-PQclear).

```
char *PQgetvalue(const PGresult *res,
int row_number,
int column_number);
```

For data in text format, the value returned by
[libpq-PQgetvalue](#libpq-PQgetvalue) is a null-terminated character
string  representation of the field value.  For data in binary
format, the value is in the binary representation determined by
the data type's `typsend` and `typreceive`
functions.  (The value is actually followed by a zero byte in
this case too, but that is not ordinarily useful, since the
value is likely to contain embedded nulls.)

An empty string is returned if the field value is null.  See
[libpq-PQgetisnull](#libpq-PQgetisnull) to distinguish null values from
empty-string values.

The pointer returned  by  [libpq-PQgetvalue](#libpq-PQgetvalue) points
to storage that is part of the `PGresult`
structure.  One should not modify the data it points to, and one
must explicitly copy the data into other storage if it is to be
used past the lifetime of the  `PGresult`
structure itself.

**`PQgetisnull`**
: Tests a field for a null value.  Row and column numbers start
at 0.

```
int PQgetisnull(const PGresult *res,
int row_number,
int column_number);
```

This function returns  1 if the field is null and 0 if it
contains a non-null value.  (Note that
[libpq-PQgetvalue](#libpq-PQgetvalue) will return an empty string,
not a null pointer, for a null field.)

**`PQgetlength`**
: Returns the actual length of a field value in bytes.  Row and
column numbers start at 0.

```
int PQgetlength(const PGresult *res,
int row_number,
int column_number);
```

This is the actual data length for the particular data value,
that is, the size of the object pointed to by
[libpq-PQgetvalue](#libpq-PQgetvalue).  For text data format this is
the same as `strlen()`.  For binary format this is
essential information.  Note that one should *not*
rely on [libpq-PQfsize](#libpq-PQfsize) to obtain the actual data
length.

**`PQnparams`**
: Returns the number of parameters of a prepared statement.

```
int PQnparams(const PGresult *res);
```

This function is only useful when inspecting the result of
[libpq-PQdescribePrepared](#libpq-PQdescribePrepared).  For other types of results it
will return zero.

**`PQparamtype`**
: Returns the data type of the indicated statement parameter.
Parameter numbers start at 0.

```
Oid PQparamtype(const PGresult *res, int param_number);
```

This function is only useful when inspecting the result of
[libpq-PQdescribePrepared](#libpq-PQdescribePrepared).  For other types of results it
will return zero.

**`PQprint`**
: Prints out all the rows and,  optionally,  the column names  to
the specified output stream.

```
void PQprint(FILE *fout,      /* output stream */
const PGresult *res,
const PQprintOpt *po);
typedef struct
{
pqbool  header;      /* print output field headings and row count */
pqbool  align;       /* fill align the fields */
pqbool  standard;    /* old brain dead format */
pqbool  html3;       /* output HTML tables */
pqbool  expanded;    /* expand tables */
pqbool  pager;       /* use pager for output if needed */
char    *fieldSep;   /* field separator */
char    *tableOpt;   /* attributes for HTML table element */
char    *caption;    /* HTML table caption */
char    **fieldName; /* null-terminated array of replacement field names */
} PQprintOpt;
```

This function was formerly used by psql
to print query results, but this is no longer the case.  Note
that it assumes all the data is in text format.

### Retrieving Other Result Information

These functions are used to extract other information from
`PGresult` objects.

**`PQcmdStatus`**
: Returns the command status tag from the SQL command that generated
the `PGresult`.

```
char *PQcmdStatus(PGresult *res);
```

Commonly this is just the name of the command, but it might include
additional data such as the number of rows processed. The caller
should not free the result directly. It will be freed when the
associated `PGresult` handle is passed to
[libpq-PQclear](#libpq-PQclear).

**`PQcmdTuples`**
: Returns the number of rows affected by the SQL command.

```
char *PQcmdTuples(PGresult *res);
```

This function returns a string containing the number of rows
affected by the SQL statement that generated the
`PGresult`. This function can only be used following
the execution of a `SELECT`, `CREATE TABLE AS`,
`INSERT`, `UPDATE`, `DELETE`,
`MERGE`, `MOVE`, `FETCH`,
or `COPY` statement, or an `EXECUTE` of a
prepared query that contains an `INSERT`,
`UPDATE`, `DELETE`,
or `MERGE` statement.
If the command that generated the `PGresult` was anything
else, [libpq-PQcmdTuples](#libpq-PQcmdTuples) returns an empty string. The caller
should not free the return value directly. It will be freed when
the associated `PGresult` handle is passed to
[libpq-PQclear](#libpq-PQclear).

**`PQoidValue`**
: Returns the OID
of the inserted row, if the SQL command was an
`INSERT` that inserted exactly one row into a table that
has OIDs, or a `EXECUTE` of a prepared query containing
a suitable `INSERT` statement.  Otherwise, this function
returns `InvalidOid`. This function will also
return `InvalidOid` if the table affected by the
`INSERT` statement does not contain OIDs.

```
Oid PQoidValue(const PGresult *res);
```

**`PQoidStatus`**
: This function is deprecated in favor of
[libpq-PQoidValue](#libpq-PQoidValue) and is not thread-safe.
It returns a string with the OID of the inserted row, while
[libpq-PQoidValue](#libpq-PQoidValue) returns the OID value.

```
char *PQoidStatus(const PGresult *res);
```

### Escaping Strings for Inclusion in SQL Commands

**`PQescapeLiteral`**
: ```
char *PQescapeLiteral(PGconn *conn, const char *str, size_t length);
```

[libpq-PQescapeLiteral](#libpq-PQescapeLiteral) escapes a string for
use within an SQL command.  This is useful when inserting data
values as literal constants in SQL commands.  Certain characters
(such as quotes and backslashes) must be escaped to prevent them
from being interpreted specially by the SQL parser.
[libpq-PQescapeLiteral](#libpq-PQescapeLiteral) performs this operation.

[libpq-PQescapeLiteral](#libpq-PQescapeLiteral) returns an escaped version of the
str parameter in memory allocated with
`malloc()`.  This memory should be freed using
`PQfreemem()` when the result is no longer needed.
A terminating zero byte is not required, and should not be
counted in length.  (If a terminating zero byte is found
before length bytes are processed,
[libpq-PQescapeLiteral](#libpq-PQescapeLiteral) stops at the zero; the behavior is
thus rather like `strncpy`.) The
return string has all special characters replaced so that they can
be properly processed by the PostgreSQL
string literal parser.  A terminating zero byte is also added.  The
single quotes that must surround PostgreSQL
string literals are included in the result string.

On error, [libpq-PQescapeLiteral](#libpq-PQescapeLiteral) returns `NULL` and a suitable
message is stored in the conn object.

> **Tip:**
> It is especially important to do proper escaping when handling
> strings that were received from an untrustworthy source.
> Otherwise there is a security risk: you are vulnerable to
> "SQL injection" attacks wherein unwanted SQL commands are
> fed to your database.
>

Note that it is neither necessary nor correct to do escaping when a data
value is passed as a separate parameter in [libpq-PQexecParams](#libpq-PQexecParams) or
its sibling routines.

**`PQescapeIdentifier`**
: ```
char *PQescapeIdentifier(PGconn *conn, const char *str, size_t length);
```

[libpq-PQescapeIdentifier](#libpq-PQescapeIdentifier) escapes a string for
use as an SQL identifier, such as a table, column, or function name.
This is useful when a user-supplied identifier might contain
special characters that would otherwise not be interpreted as part
of the identifier by the SQL parser, or when the identifier might
contain upper case characters whose case should be preserved.

[libpq-PQescapeIdentifier](#libpq-PQescapeIdentifier) returns a version of the
str parameter escaped as an SQL identifier
in memory allocated with `malloc()`.  This memory must be
freed using `PQfreemem()` when the result is no longer
needed.  A terminating zero byte is not required, and should not be
counted in length.  (If a terminating zero byte is found
before length bytes are processed,
[libpq-PQescapeIdentifier](#libpq-PQescapeIdentifier) stops at the zero; the behavior is
thus rather like `strncpy`.) The
return string has all special characters replaced so that it
will be properly processed as an SQL identifier.  A terminating zero byte
is also added.  The return string will also be surrounded by double
quotes.

On error, [libpq-PQescapeIdentifier](#libpq-PQescapeIdentifier) returns `NULL` and a suitable
message is stored in the conn object.

> **Tip:**
> As with string literals, to prevent SQL injection attacks,
> SQL identifiers must be escaped when they are received from an
> untrustworthy source.
>

**`PQescapeStringConn`**
: ```
size_t PQescapeStringConn(PGconn *conn,
char *to, const char *from, size_t length,
int *error);
```

[libpq-PQescapeStringConn](#libpq-PQescapeStringConn) escapes string literals, much like
[libpq-PQescapeLiteral](#libpq-PQescapeLiteral).  Unlike [libpq-PQescapeLiteral](#libpq-PQescapeLiteral),
the caller is responsible for providing an appropriately sized buffer.
Furthermore, [libpq-PQescapeStringConn](#libpq-PQescapeStringConn) does not generate the
single quotes that must surround PostgreSQL string
literals; they should be provided in the SQL command that the
result is inserted into.  The parameter from points to
the first character of the string that is to be escaped, and the
length parameter gives the number of bytes in this
string.  A terminating zero byte is not required, and should not be
counted in length.  (If a terminating zero byte is found
before length bytes are processed,
[libpq-PQescapeStringConn](#libpq-PQescapeStringConn) stops at the zero; the behavior is
thus rather like `strncpy`.) to shall point
to a buffer that is able to hold at least one more byte than twice
the value of length, otherwise the behavior is undefined.
Behavior is likewise undefined if the to and
from strings overlap.

If the error parameter is not `NULL`, then
`*error` is set to zero on success, nonzero on error.
Presently the only possible error conditions involve invalid multibyte
encoding in the source string.  The output string is still generated
on error, but it can be expected that the server will reject it as
malformed.  On error, a suitable message is stored in the
conn object, whether or not error is `NULL`.

[libpq-PQescapeStringConn](#libpq-PQescapeStringConn) returns the number of bytes written
to to, not including the terminating zero byte.

**`PQescapeString`**
: [libpq-PQescapeString](#libpq-PQescapeString) is an older, deprecated version of
[libpq-PQescapeStringConn](#libpq-PQescapeStringConn).

```
size_t PQescapeString (char *to, const char *from, size_t length);
```

The only difference from [libpq-PQescapeStringConn](#libpq-PQescapeStringConn) is that
[libpq-PQescapeString](#libpq-PQescapeString) does not take `PGconn`
or error parameters.
Because of this, it cannot adjust its behavior depending on the
connection properties (such as character encoding) and therefore
*it might give the wrong results*.  Also, it has no way
to report error conditions.

[libpq-PQescapeString](#libpq-PQescapeString) can be used safely in
client programs that work with only one PostgreSQL
connection at a time (in this case it can find out what it needs to
know "behind the scenes").  In other contexts it is a security
hazard and should be avoided in favor of
[libpq-PQescapeStringConn](#libpq-PQescapeStringConn).

**`PQescapeByteaConn`**
: Escapes binary data for use within an SQL command with the type
`bytea`.  As with [libpq-PQescapeStringConn](#libpq-PQescapeStringConn),
this is only used when inserting data directly into an SQL command string.

```
unsigned char *PQescapeByteaConn(PGconn *conn,
const unsigned char *from,
size_t from_length,
size_t *to_length);
```

Certain byte values must be escaped when used as part of a
`bytea` literal in an SQL statement.
[libpq-PQescapeByteaConn](#libpq-PQescapeByteaConn) escapes bytes using
either hex encoding or backslash escaping.  See [datatype-binary](#datatype-binary) for more information.

The from parameter points to the first
byte of the string that is to be escaped, and the
from_length parameter gives the number of
bytes in this binary string.  (A terminating zero byte is
neither necessary nor counted.)  The to_length
parameter points to a variable that will hold the resultant
escaped string length. This result string length includes the terminating
zero byte of the result.

[libpq-PQescapeByteaConn](#libpq-PQescapeByteaConn) returns an escaped version of the
from parameter binary string in memory
allocated with `malloc()`.  This memory should be freed using
`PQfreemem()` when the result is no longer needed.  The
return string has all special characters replaced so that they can
be properly processed by the PostgreSQL
string literal parser, and the `bytea` input function. A
terminating zero byte is also added.  The single quotes that must
surround PostgreSQL string literals are
not part of the result string.

On error, a null pointer is returned, and a suitable error message
is stored in the conn object.  Currently, the only
possible error is insufficient memory for the result string.

**`PQescapeBytea`**
: [libpq-PQescapeBytea](#libpq-PQescapeBytea) is an older, deprecated version of
[libpq-PQescapeByteaConn](#libpq-PQescapeByteaConn).

```
unsigned char *PQescapeBytea(const unsigned char *from,
size_t from_length,
size_t *to_length);
```

The only difference from [libpq-PQescapeByteaConn](#libpq-PQescapeByteaConn) is that
[libpq-PQescapeBytea](#libpq-PQescapeBytea) does not take a `PGconn`
parameter.  Because of this, [libpq-PQescapeBytea](#libpq-PQescapeBytea) can
only be used safely in client programs that use a single
PostgreSQL connection at a time (in this case
it can find out what it needs to know "behind the
scenes").  It *might give the wrong results* if
used in programs that use multiple database connections (use
[libpq-PQescapeByteaConn](#libpq-PQescapeByteaConn) in such cases).

**`PQunescapeBytea`**
: Converts a string representation of binary data into binary data
— the reverse of [libpq-PQescapeBytea](#libpq-PQescapeBytea).  This
is needed when retrieving `bytea` data in text format,
but not when retrieving it in binary format.

```
unsigned char *PQunescapeBytea(const unsigned char *from, size_t *to_length);
```

The from parameter points to a string
such as might be returned by [libpq-PQgetvalue](#libpq-PQgetvalue) when applied
to a `bytea` column. [libpq-PQunescapeBytea](#libpq-PQunescapeBytea)
converts this string representation into its binary representation.
It returns a pointer to a buffer allocated with
`malloc()`, or `NULL` on error, and puts the size of
the buffer in to_length. The result must be
freed using [libpq-PQfreemem](#libpq-PQfreemem) when it is no longer needed.

This conversion is not exactly the inverse of
[libpq-PQescapeBytea](#libpq-PQescapeBytea), because the string is not expected
to be "escaped" when received from [libpq-PQgetvalue](#libpq-PQgetvalue).
In particular this means there is no need for string quoting considerations,
and so no need for a `PGconn` parameter.

## Asynchronous Command Processing

The [libpq-PQexec](#libpq-PQexec) function is adequate for submitting
commands in normal, synchronous applications.  It has a few
deficiencies, however, that can be of importance to some users:

- [libpq-PQexec](#libpq-PQexec) waits for the command to be completed.
The application might have other work to do (such as maintaining a
user interface), in which case it won't want to block waiting for
the response.
- Since the execution of the client application is suspended while it
waits for the result, it is hard for the application to decide that
it would like to try to cancel the ongoing command.  (It can be done
from a signal handler, but not otherwise.)
- [libpq-PQexec](#libpq-PQexec) can return only one
`PGresult` structure.  If the submitted command
string contains multiple SQL commands, all but
the last `PGresult` are discarded by
[libpq-PQexec](#libpq-PQexec).
- [libpq-PQexec](#libpq-PQexec) always collects the command's entire result,
buffering it in a single `PGresult`.  While
this simplifies error-handling logic for the application, it can be
impractical for results containing many rows.

Applications that do not like these limitations can instead use the
underlying functions that [libpq-PQexec](#libpq-PQexec) is built from:
[libpq-PQsendQuery](#libpq-PQsendQuery) and [libpq-PQgetResult](#libpq-PQgetResult).
There are also
[libpq-PQsendQueryParams](#libpq-PQsendQueryParams),
[libpq-PQsendPrepare](#libpq-PQsendPrepare),
[libpq-PQsendQueryPrepared](#libpq-PQsendQueryPrepared),
[libpq-PQsendDescribePrepared](#libpq-PQsendDescribePrepared), and
[libpq-PQsendDescribePortal](#libpq-PQsendDescribePortal),
which can be used with [libpq-PQgetResult](#libpq-PQgetResult) to duplicate
the functionality of
[libpq-PQexecParams](#libpq-PQexecParams),
[libpq-PQprepare](#libpq-PQprepare),
[libpq-PQexecPrepared](#libpq-PQexecPrepared),
[libpq-PQdescribePrepared](#libpq-PQdescribePrepared), and
[libpq-PQdescribePortal](#libpq-PQdescribePortal)
respectively.

**`PQsendQuery`**
: Submits a command to the server without waiting for the result(s).
1 is returned if the command was successfully dispatched and 0 if
not (in which case, use [libpq-PQerrorMessage](#libpq-PQerrorMessage) to get more
information about the failure).

```
int PQsendQuery(PGconn *conn, const char *command);
```

After successfully calling [libpq-PQsendQuery](#libpq-PQsendQuery), call
[libpq-PQgetResult](#libpq-PQgetResult) one or more times to obtain the
results.  [libpq-PQsendQuery](#libpq-PQsendQuery) cannot be called again
(on the same connection) until [libpq-PQgetResult](#libpq-PQgetResult)
has returned a null pointer, indicating that the command is done.

In pipeline mode, this function is disallowed.

**`PQsendQueryParams`**
: Submits a command and separate parameters to the server without
waiting for the result(s).

```
int PQsendQueryParams(PGconn *conn,
const char *command,
int nParams,
const Oid *paramTypes,
const char * const *paramValues,
const int *paramLengths,
const int *paramFormats,
int resultFormat);
```

This is equivalent to [libpq-PQsendQuery](#libpq-PQsendQuery) except that
query parameters can be specified separately from the query string.
The function's parameters are handled identically to
[libpq-PQexecParams](#libpq-PQexecParams).  Like
[libpq-PQexecParams](#libpq-PQexecParams), it allows only one command in the
query string.

**`PQsendPrepare`**
: Sends a request to create a prepared statement with the given
parameters, without waiting for completion.

```
int PQsendPrepare(PGconn *conn,
const char *stmtName,
const char *query,
int nParams,
const Oid *paramTypes);
```

This is an asynchronous version of [libpq-PQprepare](#libpq-PQprepare): it
returns 1 if it was able to dispatch the request, and 0 if not.
After a successful call, call [libpq-PQgetResult](#libpq-PQgetResult) to
determine whether the server successfully created the prepared
statement.  The function's parameters are handled identically to
[libpq-PQprepare](#libpq-PQprepare).

**`PQsendQueryPrepared`**
: Sends a request to execute a prepared statement with given
parameters, without waiting for the result(s).

```
int PQsendQueryPrepared(PGconn *conn,
const char *stmtName,
int nParams,
const char * const *paramValues,
const int *paramLengths,
const int *paramFormats,
int resultFormat);
```

This is similar to [libpq-PQsendQueryParams](#libpq-PQsendQueryParams), but
the command to be executed is specified by naming a
previously-prepared statement, instead of giving a query string.
The function's parameters are handled identically to
[libpq-PQexecPrepared](#libpq-PQexecPrepared).

**`PQsendDescribePrepared`**
: Submits a request to obtain information about the specified
prepared statement, without waiting for completion.

```
int PQsendDescribePrepared(PGconn *conn, const char *stmtName);
```

This is an asynchronous version of [libpq-PQdescribePrepared](#libpq-PQdescribePrepared):
it returns 1 if it was able to dispatch the request, and 0 if not.
After a successful call, call [libpq-PQgetResult](#libpq-PQgetResult) to
obtain the results.  The function's parameters are handled
identically to [libpq-PQdescribePrepared](#libpq-PQdescribePrepared).

**`PQsendDescribePortal`**
: Submits a request to obtain information about the specified
portal, without waiting for completion.

```
int PQsendDescribePortal(PGconn *conn, const char *portalName);
```

This is an asynchronous version of [libpq-PQdescribePortal](#libpq-PQdescribePortal):
it returns 1 if it was able to dispatch the request, and 0 if not.
After a successful call, call [libpq-PQgetResult](#libpq-PQgetResult) to
obtain the results.  The function's parameters are handled
identically to [libpq-PQdescribePortal](#libpq-PQdescribePortal).

**`PQgetResult`**
: Waits for the next result from a prior
[libpq-PQsendQuery](#libpq-PQsendQuery),
[libpq-PQsendQueryParams](#libpq-PQsendQueryParams),
[libpq-PQsendPrepare](#libpq-PQsendPrepare),
[libpq-PQsendQueryPrepared](#libpq-PQsendQueryPrepared),
[libpq-PQsendDescribePrepared](#libpq-PQsendDescribePrepared),
[libpq-PQsendDescribePortal](#libpq-PQsendDescribePortal), or
[libpq-PQpipelineSync](#libpq-PQpipelineSync)
call, and returns it.
A null pointer is returned when the command is complete and there
will be no more results.

```
PGresult *PQgetResult(PGconn *conn);
```

[libpq-PQgetResult](#libpq-PQgetResult) must be called repeatedly until
it returns a null pointer, indicating that the command is done.
(If called when no command is active,
[libpq-PQgetResult](#libpq-PQgetResult) will just return a null pointer
at once.) Each non-null result from
[libpq-PQgetResult](#libpq-PQgetResult) should be processed using the
same `PGresult` accessor functions previously
described.  Don't forget to free each result object with
[libpq-PQclear](#libpq-PQclear) when done with it.  Note that
[libpq-PQgetResult](#libpq-PQgetResult) will block only if a command is
active and the necessary response data has not yet been read by
[libpq-PQconsumeInput](#libpq-PQconsumeInput).

In pipeline mode, `PQgetResult` will return normally
unless an error occurs; for any subsequent query sent after the one
that caused the error until (and excluding) the next synchronization point,
a special result of type `PGRES_PIPELINE_ABORTED` will
be returned, and a null pointer will be returned after it.
When the pipeline synchronization point is reached, a result of type
`PGRES_PIPELINE_SYNC` will be returned.
The result of the next query after the synchronization point follows
immediately (that is, no null pointer is returned after
the synchronization point).

> **Note:**
> Even when [libpq-PQresultStatus](#libpq-PQresultStatus) indicates a fatal
> error, [libpq-PQgetResult](#libpq-PQgetResult) should be called until it
> returns a null pointer, to allow libpq to
> process the error information completely.
>

Using [libpq-PQsendQuery](#libpq-PQsendQuery) and
[libpq-PQgetResult](#libpq-PQgetResult) solves one of
[libpq-PQexec](#libpq-PQexec)'s problems:  If a command string contains
multiple SQL commands, the results of those commands
can be obtained individually.  (This allows a simple form of overlapped
processing, by the way: the client can be handling the results of one
command while the server is still working on later queries in the same
command string.)

Another frequently-desired feature that can be obtained with
[libpq-PQsendQuery](#libpq-PQsendQuery) and [libpq-PQgetResult](#libpq-PQgetResult)
is retrieving large query results a row at a time.  This is discussed
in [libpq-single-row-mode](#libpq-single-row-mode).

By itself, calling [libpq-PQgetResult](#libpq-PQgetResult)
will still cause the client to block until the server completes the
next SQL command.  This can be avoided by proper
use of two more functions:

**`PQconsumeInput`**
: If input is available from the server, consume it.

```
int PQconsumeInput(PGconn *conn);
```

[libpq-PQconsumeInput](#libpq-PQconsumeInput) normally returns 1 indicating
"no error", but returns 0 if there was some kind of
trouble (in which case [libpq-PQerrorMessage](#libpq-PQerrorMessage) can be
consulted).  Note that the result does not say whether any input
data was actually collected. After calling
[libpq-PQconsumeInput](#libpq-PQconsumeInput), the application can check
[libpq-PQisBusy](#libpq-PQisBusy) and/or
`PQnotifies` to see if their state has changed.

[libpq-PQconsumeInput](#libpq-PQconsumeInput) can be called even if the
application is not prepared to deal with a result or notification
just yet.  The function will read available data and save it in
a buffer, thereby causing a `select()`
read-ready indication to go away.  The application can thus use
[libpq-PQconsumeInput](#libpq-PQconsumeInput) to clear the
`select()` condition immediately, and then
examine the results at leisure.

**`PQisBusy`**
: Returns 1 if a command is busy, that is,
[libpq-PQgetResult](#libpq-PQgetResult) would block waiting for input.
A 0 return indicates that [libpq-PQgetResult](#libpq-PQgetResult) can be
called with assurance of not blocking.

```
int PQisBusy(PGconn *conn);
```

[libpq-PQisBusy](#libpq-PQisBusy) will not itself attempt to read data
from the server; therefore [libpq-PQconsumeInput](#libpq-PQconsumeInput)
must be invoked first, or the busy state will never end.

A typical application using these functions will have a main loop that
uses `select()` or `poll()` to wait for
all the conditions that it must respond to.  One of the conditions
will be input available from the server, which in terms of
`select()` means readable data on the file
descriptor identified by [libpq-PQsocket](#libpq-PQsocket).  When the main
loop detects input ready, it should call
[libpq-PQconsumeInput](#libpq-PQconsumeInput) to read the input.  It can then
call [libpq-PQisBusy](#libpq-PQisBusy), followed by
[libpq-PQgetResult](#libpq-PQgetResult) if [libpq-PQisBusy](#libpq-PQisBusy)
returns false (0).  It can also call `PQnotifies`
to detect `NOTIFY` messages (see [libpq-notify](#libpq-notify)).

A client that uses
[libpq-PQsendQuery](#libpq-PQsendQuery)/[libpq-PQgetResult](#libpq-PQgetResult)
can also attempt to cancel a command that is still being processed
by the server; see [libpq-cancel](#libpq-cancel).  But regardless of
the return value of [libpq-PQcancel](#libpq-PQcancel), the application
must continue with the normal result-reading sequence using
[libpq-PQgetResult](#libpq-PQgetResult).  A successful cancellation will
simply cause the command to terminate sooner than it would have
otherwise.

By using the functions described above, it is possible to avoid
blocking while waiting for input from the database server.  However,
it is still possible that the application will block waiting to send
output to the server.  This is relatively uncommon but can happen if
very long SQL commands or data values are sent.  (It is much more
probable if the application sends data via `COPY IN`,
however.)  To prevent this possibility and achieve completely
nonblocking database operation, the following additional functions
can be used.

**`PQsetnonblocking`**
: Sets the nonblocking status of the connection.

```
int PQsetnonblocking(PGconn *conn, int arg);
```

Sets the state of the connection to nonblocking if
arg is 1, or blocking if
arg is 0.  Returns 0 if OK, -1 if error.

In the nonblocking state, successful calls to
[libpq-PQsendQuery](#libpq-PQsendQuery), [libpq-PQputline](#libpq-PQputline),
[libpq-PQputnbytes](#libpq-PQputnbytes), [libpq-PQputCopyData](#libpq-PQputCopyData),
and [libpq-PQendcopy](#libpq-PQendcopy) will not block;  their changes
are stored in the local output buffer until they are flushed.
Unsuccessful calls will return an error and must be retried.

Note that [libpq-PQexec](#libpq-PQexec) does not honor nonblocking
mode; if it is called, it will act in blocking fashion anyway.

**`PQisnonblocking`**
: Returns the blocking status of the database connection.

```
int PQisnonblocking(const PGconn *conn);
```

Returns 1 if the connection is set to nonblocking mode and 0 if
blocking.

**`PQflush`**
: Attempts to flush any queued output data to the server.  Returns
0 if successful (or if the send queue is empty), -1 if it failed
for some reason, or 1 if it was unable to send all the data in
the send queue yet (this case can only occur if the connection
is nonblocking).

```
int PQflush(PGconn *conn);
```

After sending any command or data on a nonblocking connection, call
[libpq-PQflush](#libpq-PQflush).  If it returns 1, wait for the socket
to become read- or write-ready.  If it becomes write-ready, call
[libpq-PQflush](#libpq-PQflush) again.  If it becomes read-ready, call
[libpq-PQconsumeInput](#libpq-PQconsumeInput), then call
[libpq-PQflush](#libpq-PQflush) again.  Repeat until
[libpq-PQflush](#libpq-PQflush) returns 0.  (It is necessary to check for
read-ready and drain the input with [libpq-PQconsumeInput](#libpq-PQconsumeInput),
because the server can block trying to send us data, e.g., NOTICE
messages, and won't read our data until we read its.)  Once
[libpq-PQflush](#libpq-PQflush) returns 0, wait for the socket to be
read-ready and then read the response as described above.

## Pipeline Mode

libpq pipeline mode allows applications to
send a query without having to read the result of the previously
sent query.  Taking advantage of the pipeline mode, a client will wait
less for the server, since multiple queries/results can be
sent/received in a single network transaction.

While pipeline mode provides a significant performance boost, writing
clients using the pipeline mode is more complex because it involves
managing a queue of pending queries and finding which result
corresponds to which query in the queue.

Pipeline mode also generally consumes more memory on both the client and server,
though careful and aggressive management of the send/receive queue can mitigate
this.  This applies whether or not the connection is in blocking or non-blocking
mode.

While libpq's pipeline API was introduced in
PostgreSQL 14, it is a client-side feature
which doesn't require special server support and works on any server
that supports the v3 extended query protocol.  For more information see
[protocol-flow-pipelining](#protocol-flow-pipelining).

### Using Pipeline Mode

To issue pipelines, the application must switch the connection
into pipeline mode,
which is done with [libpq-PQenterPipelineMode](#libpq-PQenterPipelineMode).
[libpq-PQpipelineStatus](#libpq-PQpipelineStatus) can be used
to test whether pipeline mode is active.
In pipeline mode, only [asynchronous operations](#libpq-async)
that utilize the extended query protocol
are permitted, command strings containing multiple SQL commands are
disallowed, and so is `COPY`.
Using synchronous command execution functions
such as `PQfn`,
`PQexec`,
`PQexecParams`,
`PQprepare`,
`PQexecPrepared`,
`PQdescribePrepared`,
`PQdescribePortal`,
is an error condition.
`PQsendQuery` is
also disallowed, because it uses the simple query protocol.
Once all dispatched commands have had their results processed, and
the end pipeline result has been consumed, the application may return
to non-pipelined mode with [libpq-PQexitPipelineMode](#libpq-PQexitPipelineMode).

> **Note:**

> It is best to use pipeline mode with libpq in
> [non-blocking mode](#libpq-PQsetnonblocking). If used
> in blocking mode it is possible for a client/server deadlock to occur.
>  (Note: >
> The client will block trying to send queries to the server, but the
> server will block trying to send results to the client from queries
> it has already processed. This only occurs when the client sends
> enough queries to fill both its output buffer and the server's receive
> buffer before it switches to processing input from the server,
> but it's hard to predict exactly when that will happen.
>
>)
>

#### Issuing Queries

After entering pipeline mode, the application dispatches requests using
[libpq-PQsendQueryParams](#libpq-PQsendQueryParams)
or its prepared-query sibling
[libpq-PQsendQueryPrepared](#libpq-PQsendQueryPrepared).
These requests are queued on the client-side until flushed to the server;
this occurs when [libpq-PQpipelineSync](#libpq-PQpipelineSync) is used to
establish a synchronization point in the pipeline,
or when [libpq-PQflush](#libpq-PQflush) is called.
The functions [libpq-PQsendPrepare](#libpq-PQsendPrepare),
[libpq-PQsendDescribePrepared](#libpq-PQsendDescribePrepared), and
[libpq-PQsendDescribePortal](#libpq-PQsendDescribePortal) also work in pipeline mode.
Result processing is described below.

The server executes statements, and returns results, in the order the
client sends them.  The server will begin executing the commands in the
pipeline immediately, not waiting for the end of the pipeline.
Note that results are buffered on the server side; the server flushes
that buffer when a synchronization point is established with
`PQpipelineSync`, or when
`PQsendFlushRequest` is called.
If any statement encounters an error, the server aborts the current
transaction and does not execute any subsequent command in the queue
until the next synchronization point;
a `PGRES_PIPELINE_ABORTED` result is produced for
each such command.
(This remains true even if the commands in the pipeline would rollback
the transaction.)
Query processing resumes after the synchronization point.

It's fine for one operation to depend on the results of a
prior one; for example, one query may define a table that the next
query in the same pipeline uses. Similarly, an application may
create a named prepared statement and execute it with later
statements in the same pipeline.

#### Processing Results

To process the result of one query in a pipeline, the application calls
`PQgetResult` repeatedly and handles each result
until `PQgetResult` returns null.
The result from the next query in the pipeline may then be retrieved using
`PQgetResult` again and the cycle repeated.
The application handles individual statement results as normal.
When the results of all the queries in the pipeline have been
returned, `PQgetResult` returns a result
containing the status value `PGRES_PIPELINE_SYNC`

The client may choose to defer result processing until the complete
pipeline has been sent, or interleave that with sending further
queries in the pipeline; see [libpq-pipeline-interleave](#libpq-pipeline-interleave).

To enter single-row mode, call `PQsetSingleRowMode`
before retrieving results with `PQgetResult`.
This mode selection is effective only for the query currently
being processed. For more information on the use of
`PQsetSingleRowMode`,
refer to [libpq-single-row-mode](#libpq-single-row-mode).

`PQgetResult` behaves the same as for normal
asynchronous processing except that it may contain the new
`PGresult` types `PGRES_PIPELINE_SYNC`
and `PGRES_PIPELINE_ABORTED`.
`PGRES_PIPELINE_SYNC` is reported exactly once for each
`PQpipelineSync` at the corresponding point
in the pipeline.
`PGRES_PIPELINE_ABORTED` is emitted in place of a normal
query result for the first error and all subsequent results
until the next `PGRES_PIPELINE_SYNC`;
see [libpq-pipeline-errors](#libpq-pipeline-errors).

`PQisBusy`, `PQconsumeInput`, etc
operate as normal when processing pipeline results.  In particular,
a call to `PQisBusy` in the middle of a pipeline
returns 0 if the results for all the queries issued so far have been
consumed.

libpq does not provide any information to the
application about the query currently being processed (except that
`PQgetResult` returns null to indicate that we start
returning the results of next query). The application must keep track
of the order in which it sent queries, to associate them with their
corresponding results.
Applications will typically use a state machine or a FIFO queue for this.

#### Error Handling

From the client's perspective, after `PQresultStatus`
returns `PGRES_FATAL_ERROR`,
the pipeline is flagged as aborted.
`PQresultStatus` will report a
`PGRES_PIPELINE_ABORTED` result for each remaining queued
operation in an aborted pipeline. The result for
`PQpipelineSync` is reported as
`PGRES_PIPELINE_SYNC` to signal the end of the aborted pipeline
and resumption of normal result processing.

The client *must* process results with
`PQgetResult` during error recovery.

If the pipeline used an implicit transaction, then operations that have
already executed are rolled back and operations that were queued to follow
the failed operation are skipped entirely. The same behavior holds if the
pipeline starts and commits a single explicit transaction (i.e. the first
statement is `BEGIN` and the last is
`COMMIT`) except that the session remains in an aborted
transaction state at the end of the pipeline. If a pipeline contains
*multiple explicit transactions*, all transactions that
committed prior to the error remain committed, the currently in-progress
transaction is aborted, and all subsequent operations are skipped completely,
including subsequent transactions.  If a pipeline synchronization point
occurs with an explicit transaction block in aborted state, the next pipeline
will become aborted immediately unless the next command puts the transaction
in normal mode with `ROLLBACK`.

> **Note:**

> The client must not assume that work is committed when it
> *sends* a `COMMIT` — only when the
> corresponding result is received to confirm the commit is complete.
> Because errors arrive asynchronously, the application needs to be able to
> restart from the last *received* committed change and
> resend work done after that point if something goes wrong.
>

#### Interleaving Result Processing and Query Dispatch

To avoid deadlocks on large pipelines the client should be structured
around a non-blocking event loop using operating system facilities
such as `select`, `poll`,
`WaitForMultipleObjectEx`, etc.

The client application should generally maintain a queue of work
remaining to be dispatched and a queue of work that has been dispatched
but not yet had its results processed. When the socket is writable
it should dispatch more work. When the socket is readable it should
read results and process them, matching them up to the next entry in
its corresponding results queue.  Based on available memory, results from the
socket should be read frequently: there's no need to wait until the
pipeline end to read the results.  Pipelines should be scoped to logical
units of work, usually (but not necessarily) one transaction per pipeline.
There's no need to exit pipeline mode and re-enter it between pipelines,
or to wait for one pipeline to finish before sending the next.

An example using `select()` and a simple state
machine to track sent and received work is in
`src/test/modules/libpq_pipeline/libpq_pipeline.c`
in the PostgreSQL source distribution.

### Functions Associated with Pipeline Mode

**`PQpipelineStatus`**
: Returns the current pipeline mode status of the
libpq connection.

```
PGpipelineStatus PQpipelineStatus(const PGconn *conn);
```

`PQpipelineStatus` can return one of the following values:

`PQ_PIPELINE_ON`

The libpq connection is in
pipeline mode.

**`PQ_PIPELINE_OFF`**
: The libpq connection is
*not* in pipeline mode.

**`PQ_PIPELINE_ABORTED`**
: The libpq connection is in pipeline
mode and an error occurred while processing the current pipeline.
The aborted flag is cleared when `PQgetResult`
returns a result of type `PGRES_PIPELINE_SYNC`.

`PQenterPipelineMode`

Causes a connection to enter pipeline mode if it is currently idle or
already in pipeline mode.

```
int PQenterPipelineMode(PGconn *conn);
```

Returns 1 for success.
Returns 0 and has no effect if the connection is not currently
idle, i.e., it has a result ready, or it is waiting for more
input from the server, etc.
This function does not actually send anything to the server,
it just changes the libpq connection
state.

`PQexitPipelineMode`

Causes a connection to exit pipeline mode if it is currently in pipeline mode
with an empty queue and no pending results.

```
int PQexitPipelineMode(PGconn *conn);
```

Returns 1 for success.  Returns 1 and takes no action if not in
pipeline mode. If the current statement isn't finished processing,
or `PQgetResult` has not been called to collect
results from all previously sent query, returns 0 (in which case,
use [libpq-PQerrorMessage](#libpq-PQerrorMessage) to get more information
about the failure).

`PQpipelineSync`

Marks a synchronization point in a pipeline by sending a
[sync message](#protocol-flow-ext-query)
and flushing the send buffer. This serves as
the delimiter of an implicit transaction and an error recovery
point; see [libpq-pipeline-errors](#libpq-pipeline-errors).

```
int PQpipelineSync(PGconn *conn);
```

Returns 1 for success. Returns 0 if the connection is not in
pipeline mode or sending a
[sync message](#protocol-flow-ext-query)
failed.

`PQsendFlushRequest`

Sends a request for the server to flush its output buffer.

```
int PQsendFlushRequest(PGconn *conn);
```

Returns 1 for success.  Returns 0 on any failure.

The server flushes its output buffer automatically as a result of
`PQpipelineSync` being called, or
on any request when not in pipeline mode; this function is useful
to cause the server to flush its output buffer in pipeline mode
without establishing a synchronization point.
Note that the request is not itself flushed to the server automatically;
use `PQflush` if necessary.

### When to Use Pipeline Mode

Much like asynchronous query mode, there is no meaningful performance
overhead when using pipeline mode. It increases client application complexity,
and extra caution is required to prevent client/server deadlocks, but
pipeline mode can offer considerable performance improvements, in exchange for
increased memory usage from leaving state around longer.

Pipeline mode is most useful when the server is distant, i.e., network latency
("ping time") is high, and also when many small operations
are being performed in rapid succession.  There is usually less benefit
in using pipelined commands when each query takes many multiples of the client/server
round-trip time to execute.  A 100-statement operation run on a server
300 ms round-trip-time away would take 30 seconds in network latency alone
without pipelining; with pipelining it may spend as little as 0.3 s waiting for
results from the server.

Use pipelined commands when your application does lots of small
`INSERT`, `UPDATE` and
`DELETE` operations that can't easily be transformed
into operations on sets, or into a `COPY` operation.

Pipeline mode is not useful when information from one operation is required by
the client to produce the next operation. In such cases, the client
would have to introduce a synchronization point and wait for a full client/server
round-trip to get the results it needs. However, it's often possible to
adjust the client design to exchange the required information server-side.
Read-modify-write cycles are especially good candidates; for example:

```
BEGIN;
SELECT x FROM mytable WHERE id = 42 FOR UPDATE;
-- result: x=2
-- client adds 1 to x:
UPDATE mytable SET x = 3 WHERE id = 42;
COMMIT;
```

could be much more efficiently done with:

```
UPDATE mytable SET x = x + 1 WHERE id = 42;
```

Pipelining is less useful, and more complex, when a single pipeline contains
multiple transactions (see [libpq-pipeline-errors](#libpq-pipeline-errors)).

## Functions Associated with the `COPY` Command

The `COPY` command in
PostgreSQL has options to read from or write
to the network connection used by libpq.
The functions described in this section allow applications to take
advantage of this capability by supplying or consuming copied data.

The overall process is that the application first issues the SQL
`COPY` command via [libpq-PQexec](#libpq-PQexec) or one
of the equivalent functions.  The response to this (if there is no
error in the command) will be a `PGresult` object bearing
a status code of `PGRES_COPY_OUT` or
`PGRES_COPY_IN` (depending on the specified copy
direction).  The application should then use the functions of this
section to receive or transmit data rows.  When the data transfer is
complete, another `PGresult` object is returned to indicate
success or failure of the transfer.  Its status will be
`PGRES_COMMAND_OK` for success or
`PGRES_FATAL_ERROR` if some problem was encountered.
At this point further SQL commands can be issued via
[libpq-PQexec](#libpq-PQexec).  (It is not possible to execute other SQL
commands using the same connection while the `COPY`
operation is in progress.)

If a `COPY` command is issued via
[libpq-PQexec](#libpq-PQexec) in a string that could contain additional
commands, the application must continue fetching results via
[libpq-PQgetResult](#libpq-PQgetResult) after completing the `COPY`
sequence.  Only when [libpq-PQgetResult](#libpq-PQgetResult) returns
`NULL` is it certain that the [libpq-PQexec](#libpq-PQexec)
command string is done and it is safe to issue more commands.

The functions of this section should be executed only after obtaining
a result status of `PGRES_COPY_OUT` or
`PGRES_COPY_IN` from [libpq-PQexec](#libpq-PQexec) or
[libpq-PQgetResult](#libpq-PQgetResult).

A `PGresult` object bearing one of these status values
carries some additional data about the `COPY` operation
that is starting.  This additional data is available using functions
that are also used in connection with query results:

**`PQnfields`**
: Returns the number of columns (fields) to be copied.

**`PQbinaryTuples`**
: 0 indicates the overall copy format is textual (rows separated by
newlines, columns separated by separator characters, etc.).  1
indicates the overall copy format is binary.  See [sql-copy](#sql-copy) for more information.

**`PQfformat`**
: Returns the format code (0 for text, 1 for binary) associated with
each column of the copy operation.  The per-column format codes
will always be zero when the overall copy format is textual, but
the binary format can support both text and binary columns.
(However, as of the current implementation of `COPY`,
only binary columns appear in a binary copy; so the per-column
formats always match the overall format at present.)

### Functions for Sending `COPY` Data

These functions are used to send data during `COPY FROM
STDIN`.  They will fail if called when the connection is not in
`COPY_IN` state.

**`PQputCopyData`**
: Sends data to the server during `COPY_IN` state.

```
int PQputCopyData(PGconn *conn,
const char *buffer,
int nbytes);
```

Transmits the `COPY` data in the specified
buffer, of length nbytes, to the server.
The result is 1 if the data was queued, zero if it was not queued
because of full buffers (this will only happen in nonblocking mode),
or -1 if an error occurred.
(Use [libpq-PQerrorMessage](#libpq-PQerrorMessage) to retrieve details if
the return value is -1.  If the value is zero, wait for write-ready
and try again.)

The application can divide the `COPY` data stream
into buffer loads of any convenient size.  Buffer-load boundaries
have no semantic significance when sending.  The contents of the
data stream must match the data format expected by the
`COPY` command; see [sql-copy](#sql-copy) for details.

**`PQputCopyEnd`**
: Sends end-of-data indication to the server during `COPY_IN` state.

```
int PQputCopyEnd(PGconn *conn,
const char *errormsg);
```

Ends the `COPY_IN` operation successfully if
errormsg is `NULL`.  If
errormsg is not `NULL` then the
`COPY` is forced to fail, with the string pointed to by
errormsg used as the error message.  (One should not
assume that this exact error message will come back from the server,
however, as the server might have already failed the
`COPY` for its own reasons.)

The result is 1 if the termination message was sent; or in
nonblocking mode, this may only indicate that the termination
message was successfully queued.  (In nonblocking mode, to be
certain that the data has been sent, you should next wait for
write-ready and call [libpq-PQflush](#libpq-PQflush), repeating until it
returns zero.)  Zero indicates that the function could not queue
the termination message because of full buffers; this will only
happen in nonblocking mode.  (In this case, wait for
write-ready and try the [libpq-PQputCopyEnd](#libpq-PQputCopyEnd) call
again.)  If a hard error occurs, -1 is returned; you can use
[libpq-PQerrorMessage](#libpq-PQerrorMessage) to retrieve details.

After successfully calling [libpq-PQputCopyEnd](#libpq-PQputCopyEnd), call
[libpq-PQgetResult](#libpq-PQgetResult) to obtain the final result status of the
`COPY` command.  One can wait for this result to be
available in the usual way.  Then return to normal operation.

### Functions for Receiving `COPY` Data

These functions are used to receive data during `COPY TO
STDOUT`.  They will fail if called when the connection is not in
`COPY_OUT` state.

**`PQgetCopyData`**
: Receives data from the server during `COPY_OUT` state.

```
int PQgetCopyData(PGconn *conn,
char **buffer,
int async);
```

Attempts to obtain another row of data from the server during a
`COPY`.  Data is always returned one data row at
a time; if only a partial row is available, it is not returned.
Successful return of a data row involves allocating a chunk of
memory to hold the data.  The buffer parameter must
be non-`NULL`.  *buffer is set to
point to the allocated memory, or to `NULL` in cases
where no buffer is returned.  A non-`NULL` result
buffer should be freed using [libpq-PQfreemem](#libpq-PQfreemem) when no longer
needed.

When a row is successfully returned, the return value is the number
of data bytes in the row (this will always be greater than zero).
The returned string is always null-terminated, though this is
probably only useful for textual `COPY`.  A result
of zero indicates that the `COPY` is still in
progress, but no row is yet available (this is only possible when
async is true).  A result of -1 indicates that the
`COPY` is done.  A result of -2 indicates that an
error occurred (consult [libpq-PQerrorMessage](#libpq-PQerrorMessage) for the reason).

When async is true (not zero),
[libpq-PQgetCopyData](#libpq-PQgetCopyData) will not block waiting for input; it
will return zero if the `COPY` is still in progress
but no complete row is available.  (In this case wait for read-ready
and then call [libpq-PQconsumeInput](#libpq-PQconsumeInput) before calling
[libpq-PQgetCopyData](#libpq-PQgetCopyData) again.)  When async is
false (zero), [libpq-PQgetCopyData](#libpq-PQgetCopyData) will block until data is
available or the operation completes.

After [libpq-PQgetCopyData](#libpq-PQgetCopyData) returns -1, call
[libpq-PQgetResult](#libpq-PQgetResult) to obtain the final result status of the
`COPY` command.  One can wait for this result to be
available in the usual way.  Then return to normal operation.

### Obsolete Functions for `COPY`

These functions represent older methods of handling `COPY`.
Although they still work, they are deprecated due to poor error handling,
inconvenient methods of detecting end-of-data, and lack of support for binary
or nonblocking transfers.

**`PQgetline`**
: Reads  a  newline-terminated  line  of  characters (transmitted
by the server) into a buffer string of size length.

```
int PQgetline(PGconn *conn,
char *buffer,
int length);
```

This function copies up to length-1 characters into
the buffer and converts the terminating newline into a zero byte.
[libpq-PQgetline](#libpq-PQgetline) returns `EOF` at the
end of input, 0 if the entire line has been read, and 1 if the
buffer is full but the terminating newline has not yet been read.

Note that the application must check to see if a new line consists
of  the  two characters  `\.`, which  indicates
that the server has finished sending the results  of  the
`COPY` command.  If  the  application might receive
lines that are more than length-1  characters  long,
care is needed to be sure it recognizes the `\.`
line correctly (and does not, for example, mistake the end of a
long data line for a terminator line).

**`PQgetlineAsync`**
: Reads a row of `COPY` data (transmitted  by the
server) into a buffer without blocking.

```
int PQgetlineAsync(PGconn *conn,
char *buffer,
int bufsize);
```

This function is similar to [libpq-PQgetline](#libpq-PQgetline), but it can be used
by applications
that must read `COPY` data asynchronously, that is, without blocking.
Having issued the `COPY` command and gotten a `PGRES_COPY_OUT`
response, the
application should call [libpq-PQconsumeInput](#libpq-PQconsumeInput) and
[libpq-PQgetlineAsync](#libpq-PQgetlineAsync) until the
end-of-data signal is detected.

Unlike [libpq-PQgetline](#libpq-PQgetline), this function takes
responsibility for detecting end-of-data.

On each call, [libpq-PQgetlineAsync](#libpq-PQgetlineAsync) will return data if a
complete data row is available in libpq's input buffer.
Otherwise, no data is returned until the rest of the row arrives.
The function returns -1 if the end-of-copy-data marker has been recognized,
or 0 if no data is available, or a positive number giving the number of
bytes of data returned.  If -1 is returned, the caller must next call
[libpq-PQendcopy](#libpq-PQendcopy), and then return to normal processing.

The data returned will not extend beyond a data-row boundary.  If possible
a whole row will be returned at one time.  But if the buffer offered by
the caller is too small to hold a row sent by the server, then a partial
data row will be returned.  With textual data this can be detected by testing
whether the last returned byte is `\n` or not.  (In a binary
`COPY`, actual parsing of the `COPY` data format will be needed to make the
equivalent determination.)
The returned string is not null-terminated.  (If you want to add a
terminating null, be sure to pass a bufsize one smaller
than the room actually available.)

**`PQputline`**
: Sends  a  null-terminated  string  to  the server.  Returns 0 if
OK and `EOF` if unable to send the string.

```
int PQputline(PGconn *conn,
const char *string);
```

The `COPY` data stream sent by a series of calls
to [libpq-PQputline](#libpq-PQputline) has the same format as that
returned by [libpq-PQgetlineAsync](#libpq-PQgetlineAsync), except that
applications are not obliged to send exactly one data row per
[libpq-PQputline](#libpq-PQputline) call; it is okay to send a partial
line or multiple lines per call.

> **Note:**
> Before PostgreSQL protocol 3.0, it was necessary
> for the application to explicitly send the two characters
> `\.` as a final line to indicate to the server that it had
> finished sending `COPY` data.  While this still works, it is deprecated and the
> special meaning of `\.` can be expected to be removed in a
> future release.  It is sufficient to call [libpq-PQendcopy](#libpq-PQendcopy) after
> having sent the actual data.
>

**`PQputnbytes`**
: Sends  a  non-null-terminated  string  to  the server.  Returns
0 if OK and `EOF` if unable to send the string.

```
int PQputnbytes(PGconn *conn,
const char *buffer,
int nbytes);
```

This is exactly like [libpq-PQputline](#libpq-PQputline), except that the data
buffer need not be null-terminated since the number of bytes to send is
specified directly.  Use this procedure when sending binary data.

**`PQendcopy`**
: Synchronizes with the server.

```
int PQendcopy(PGconn *conn);
```

This function waits until the  server  has  finished  the copying.
It should either be issued when the  last  string  has  been sent
to  the  server using [libpq-PQputline](#libpq-PQputline) or when the
last string has been  received  from  the  server using
`PQgetline`.  It must be issued or the server
will get "out of sync" with  the client.   Upon return
from this function, the server is ready to receive the next SQL
command.  The return value is 0  on  successful  completion,
nonzero otherwise.  (Use [libpq-PQerrorMessage](#libpq-PQerrorMessage) to
retrieve details if the return value is nonzero.)

When using [libpq-PQgetResult](#libpq-PQgetResult), the application should
respond to a `PGRES_COPY_OUT` result by executing
[libpq-PQgetline](#libpq-PQgetline) repeatedly, followed by
[libpq-PQendcopy](#libpq-PQendcopy) after the terminator line is seen.
It should then return to the [libpq-PQgetResult](#libpq-PQgetResult) loop
until [libpq-PQgetResult](#libpq-PQgetResult) returns a null pointer.
Similarly a `PGRES_COPY_IN` result is processed
by a series of [libpq-PQputline](#libpq-PQputline) calls followed by
[libpq-PQendcopy](#libpq-PQendcopy), then return to the
[libpq-PQgetResult](#libpq-PQgetResult) loop.  This arrangement will
ensure that a `COPY` command embedded in a series
of SQL commands will be executed correctly.

Older applications are likely to submit a `COPY`
via [libpq-PQexec](#libpq-PQexec) and assume that the transaction
is done after [libpq-PQendcopy](#libpq-PQendcopy).  This will work
correctly only if the `COPY` is the only
SQL command in the command string.

## Control Functions

These functions control miscellaneous details of libpq's
behavior.

**`PQclientEncoding`**
: Returns the client encoding.

```
int PQclientEncoding(const PGconn *`conn`);
```

Note that it returns the encoding ID, not a symbolic string
such as `EUC_JP`. If unsuccessful, it returns -1.
To convert an encoding ID to an encoding name, you
can use:

```
char *pg_encoding_to_char(int `encoding_id`);
```

**`PQsetClientEncoding`**
: Sets the client encoding.

```
int PQsetClientEncoding(PGconn *`conn`, const char *`encoding`);
```

`conn` is a connection to the server,
and `encoding` is the encoding you want to
use. If the function successfully sets the encoding, it returns 0,
otherwise -1. The current encoding for this connection can be
determined by using [libpq-PQclientEncoding](#libpq-PQclientEncoding).

**`PQsetErrorVerbosity`**
: Determines the verbosity of messages returned by
[libpq-PQerrorMessage](#libpq-PQerrorMessage) and [libpq-PQresultErrorMessage](#libpq-PQresultErrorMessage).

```
typedef enum
{
PQERRORS_TERSE,
PQERRORS_DEFAULT,
PQERRORS_VERBOSE,
PQERRORS_SQLSTATE
} PGVerbosity;

PGVerbosity PQsetErrorVerbosity(PGconn *conn, PGVerbosity verbosity);
```

[libpq-PQsetErrorVerbosity](#libpq-PQsetErrorVerbosity) sets the verbosity mode,
returning the connection's previous setting.
In *TERSE* mode, returned messages include
severity, primary text, and position only; this will normally fit on a
single line.  The *DEFAULT* mode produces messages
that include the above plus any detail, hint, or context fields (these
might span multiple lines).  The *VERBOSE* mode
includes all available fields.  The *SQLSTATE*
mode includes only the error severity and the `SQLSTATE`
error code, if one is available (if not, the output is like
*TERSE* mode).

Changing the verbosity setting does not affect the messages available
from already-existing `PGresult` objects, only
subsequently-created ones.
(But see [libpq-PQresultVerboseErrorMessage](#libpq-PQresultVerboseErrorMessage) if you
want to print a previous error with a different verbosity.)

**`PQsetErrorContextVisibility`**
: Determines the handling of `CONTEXT` fields in messages
returned by [libpq-PQerrorMessage](#libpq-PQerrorMessage)
and [libpq-PQresultErrorMessage](#libpq-PQresultErrorMessage).

```
typedef enum
{
PQSHOW_CONTEXT_NEVER,
PQSHOW_CONTEXT_ERRORS,
PQSHOW_CONTEXT_ALWAYS
} PGContextVisibility;

PGContextVisibility PQsetErrorContextVisibility(PGconn *conn, PGContextVisibility show_context);
```

[libpq-PQsetErrorContextVisibility](#libpq-PQsetErrorContextVisibility) sets the context display mode,
returning the connection's previous setting.  This mode controls
whether the `CONTEXT` field is included in messages.
The *NEVER* mode
never includes `CONTEXT`, while *ALWAYS* always
includes it if available.  In *ERRORS* mode (the
default), `CONTEXT` fields are included only in error
messages, not in notices and warnings.
(However, if the verbosity setting is *TERSE*
or *SQLSTATE*, `CONTEXT` fields
are omitted regardless of the context display mode.)

Changing this mode does not
affect the messages available from
already-existing `PGresult` objects, only
subsequently-created ones.
(But see [libpq-PQresultVerboseErrorMessage](#libpq-PQresultVerboseErrorMessage) if you
want to print a previous error with a different display mode.)

**`PQtrace`**
: Enables tracing of the client/server communication to a debugging file
stream.

```
void PQtrace(PGconn *conn, FILE *stream);
```

Each line consists of: an optional timestamp, a direction indicator
(`F` for messages from client to server
or `B` for messages from server to client),
message length, message type, and message contents.
Non-message contents fields (timestamp, direction, length and message type)
are separated by a tab. Message contents are separated by a space.
Protocol strings are enclosed in double quotes, while strings used as data
values are enclosed in single quotes.  Non-printable chars are printed as
hexadecimal escapes.
Further message-type-specific detail can be found in
[protocol-message-formats](#protocol-message-formats).

> **Note:**
> On Windows, if the libpq library and an application are
> compiled with different flags, this function call will crash the
> application because the internal representation of the `FILE`
> pointers differ.  Specifically, multithreaded/single-threaded,
> release/debug, and static/dynamic flags should be the same for the
> library and all applications using that library.
>

**`PQsetTraceFlags`**
: Controls the tracing behavior of client/server communication.

```
void PQsetTraceFlags(PGconn *conn, int flags);
```

`flags` contains flag bits describing the operating mode
of tracing.
If `flags` contains `PQTRACE_SUPPRESS_TIMESTAMPS`,
then the timestamp is not included when printing each message.
If `flags` contains `PQTRACE_REGRESS_MODE`,
then some fields are redacted when printing each message, such as object
OIDs, to make the output more convenient to use in testing frameworks.
This function must be called after calling `PQtrace`.

**`PQuntrace`**
: Disables tracing started by [libpq-PQtrace](#libpq-PQtrace).

```
void PQuntrace(PGconn *conn);
```

## Miscellaneous Functions

As always, there are some functions that just don't fit anywhere.

**`PQfreemem`**
: Frees memory allocated by libpq.

```
void PQfreemem(void *ptr);
```

Frees memory allocated by libpq, particularly
[libpq-PQescapeByteaConn](#libpq-PQescapeByteaConn),
[libpq-PQescapeBytea](#libpq-PQescapeBytea),
[libpq-PQunescapeBytea](#libpq-PQunescapeBytea),
and `PQnotifies`.
It is particularly important that this function, rather than
`free()`, be used on Microsoft Windows.  This is because
allocating memory in a DLL and releasing it in the application works
only if multithreaded/single-threaded, release/debug, and static/dynamic
flags are the same for the DLL and the application.  On non-Microsoft
Windows platforms, this function is the same as the standard library
function `free()`.

**`PQconninfoFree`**
: Frees the data structures allocated by
[libpq-PQconndefaults](#libpq-PQconndefaults) or [libpq-PQconninfoParse](#libpq-PQconninfoParse).

```
void PQconninfoFree(PQconninfoOption *connOptions);
```

If the argument is a `NULL` pointer, no operation is
performed.

A simple [libpq-PQfreemem](#libpq-PQfreemem) will not do for this, since
the array contains references to subsidiary strings.

**`PQencryptPasswordConn`**
: Prepares the encrypted form of a PostgreSQL password.

```
char *PQencryptPasswordConn(PGconn *conn, const char *passwd, const char *user, const char *algorithm);
```

This function is intended to be used by client applications that
wish to send commands like `ALTER USER joe PASSWORD
'pwd'`.  It is good practice not to send the original cleartext
password in such a command, because it might be exposed in command
logs, activity displays, and so on.  Instead, use this function to
convert the password to encrypted form before it is sent.

The passwd and user arguments
are the cleartext password, and the SQL name of the user it is for.
algorithm specifies the encryption algorithm
to use to encrypt the password. Currently supported algorithms are
`md5` and `scram-sha-256` (`on` and
`off` are also accepted as aliases for `md5`, for
compatibility with older server versions). Note that support for
`scram-sha-256` was introduced in PostgreSQL
version 10, and will not work correctly with older server versions. If
algorithm is `NULL`, this function will query
the server for the current value of the
[guc-password-encryption](#guc-password-encryption) setting. That can block, and
will fail if the current transaction is aborted, or if the connection
is busy executing another query. If you wish to use the default
algorithm for the server but want to avoid blocking, query
`password_encryption` yourself before calling
[libpq-PQencryptPasswordConn](#libpq-PQencryptPasswordConn), and pass that value as the
algorithm.

The return value is a string allocated by `malloc`.
The caller can assume the string doesn't contain any special characters
that would require escaping.  Use [libpq-PQfreemem](#libpq-PQfreemem) to free the
result when done with it. On error, returns `NULL`, and
a suitable message is stored in the connection object.

**`PQencryptPassword`**
: Prepares the md5-encrypted form of a PostgreSQL password.

```
char *PQencryptPassword(const char *passwd, const char *user);
```

[libpq-PQencryptPassword](#libpq-PQencryptPassword) is an older, deprecated version of
[libpq-PQencryptPasswordConn](#libpq-PQencryptPasswordConn). The difference is that
[libpq-PQencryptPassword](#libpq-PQencryptPassword) does not
require a connection object, and `md5` is always used as the
encryption algorithm.

**`PQmakeEmptyPGresult`**
: Constructs an empty `PGresult` object with the given status.

```
PGresult *PQmakeEmptyPGresult(PGconn *conn, ExecStatusType status);
```

This is libpq's internal function to allocate and
initialize an empty `PGresult` object.  This
function returns `NULL` if memory could not be allocated. It is
exported because some applications find it useful to generate result
objects (particularly objects with error status) themselves.  If
conn is not null and status
indicates an error, the current error message of the specified
connection is copied into the `PGresult`.
Also, if conn is not null, any event procedures
registered in the connection are copied into the
`PGresult`.  (They do not get
`PGEVT_RESULTCREATE` calls, but see
[libpq-PQfireResultCreateEvents](#libpq-PQfireResultCreateEvents).)
Note that [libpq-PQclear](#libpq-PQclear) should eventually be called
on the object, just as with a `PGresult`
returned by libpq itself.

**`PQfireResultCreateEvents`**
: Fires a `PGEVT_RESULTCREATE` event (see [libpq-events](#libpq-events)) for each event procedure registered in the
`PGresult` object.  Returns non-zero for success,
zero if any event procedure fails.

```
int PQfireResultCreateEvents(PGconn *conn, PGresult *res);
```

The `conn` argument is passed through to event procedures
but not used directly.  It can be `NULL` if the event
procedures won't use it.

Event procedures that have already received a
`PGEVT_RESULTCREATE` or `PGEVT_RESULTCOPY` event
for this object are not fired again.

The main reason that this function is separate from
[libpq-PQmakeEmptyPGresult](#libpq-PQmakeEmptyPGresult) is that it is often appropriate
to create a `PGresult` and fill it with data
before invoking the event procedures.

**`PQcopyResult`**
: Makes a copy of a `PGresult` object.  The copy is
not linked to the source result in any way and
[libpq-PQclear](#libpq-PQclear) must be called when the copy is no longer
needed.  If the function fails, `NULL` is returned.

```
PGresult *PQcopyResult(const PGresult *src, int flags);
```

This is not intended to make an exact copy.  The returned result is
always put into `PGRES_TUPLES_OK` status, and does not
copy any error message in the source.  (It does copy the command status
string, however.)  The flags argument determines
what else is copied.  It is a bitwise OR of several flags.
`PG_COPYRES_ATTRS` specifies copying the source
result's attributes (column definitions).
`PG_COPYRES_TUPLES` specifies copying the source
result's tuples.  (This implies copying the attributes, too.)
`PG_COPYRES_NOTICEHOOKS` specifies
copying the source result's notify hooks.
`PG_COPYRES_EVENTS` specifies copying the source
result's events.  (But any instance data associated with the source
is not copied.)
The event procedures receive `PGEVT_RESULTCOPY` events.

**`PQsetResultAttrs`**
: Sets the attributes of a `PGresult` object.

```
int PQsetResultAttrs(PGresult *res, int numAttributes, PGresAttDesc *attDescs);
```

The provided attDescs are copied into the result.
If the attDescs pointer is `NULL` or
numAttributes is less than one, the request is
ignored and the function succeeds.  If res
already contains attributes, the function will fail.  If the function
fails, the return value is zero.  If the function succeeds, the return
value is non-zero.

**`PQsetvalue`**
: Sets a tuple field value of a `PGresult` object.

```
int PQsetvalue(PGresult *res, int tup_num, int field_num, char *value, int len);
```

The function will automatically grow the result's internal tuples array
as needed.  However, the tup_num argument must be
less than or equal to [libpq-PQntuples](#libpq-PQntuples), meaning this
function can only grow the tuples array one tuple at a time.  But any
field of any existing tuple can be modified in any order.  If a value at
field_num already exists, it will be overwritten.
If len is -1 or
value is `NULL`, the field value
will be set to an SQL null value.  The
value is copied into the result's private storage,
thus is no longer needed after the function
returns.  If the function fails, the return value is zero.  If the
function succeeds, the return value is non-zero.

**`PQresultAlloc`**
: Allocate subsidiary storage for a `PGresult` object.

```
void *PQresultAlloc(PGresult *res, size_t nBytes);
```

Any memory allocated with this function will be freed when
res is cleared.  If the function fails,
the return value is `NULL`.  The result is
guaranteed to be adequately aligned for any type of data,
just as for `malloc`.

**`PQresultMemorySize`**
: Retrieves the number of bytes allocated for
a `PGresult` object.

```
size_t PQresultMemorySize(const PGresult *res);
```

This value is the sum of all `malloc` requests
associated with the `PGresult` object, that is,
all the space that will be freed by [libpq-PQclear](#libpq-PQclear).
This information can be useful for managing memory consumption.

**`PQlibVersion`**
: Return the version of libpq that is being used.

```
int PQlibVersion(void);
```

The result of this function can be used to determine, at
run time, whether specific functionality is available in the currently
loaded version of libpq. The function can be used, for example,
to determine which connection options are available in
[libpq-PQconnectdb](#libpq-PQconnectdb).

The result is formed by multiplying the library's major version
number by 10000 and adding the minor version number.  For example,
version 10.1 will be returned as 100001, and version 11.0 will be
returned as 110000.

Prior to major version 10, PostgreSQL used
three-part version numbers in which the first two parts together
represented the major version.  For those
versions, [libpq-PQlibVersion](#libpq-PQlibVersion) uses two digits for each
part; for example version 9.1.5 will be returned as 90105, and
version 9.2.0 will be returned as 90200.

Therefore, for purposes of determining feature compatibility,
applications should divide the result of [libpq-PQlibVersion](#libpq-PQlibVersion)
by 100 not 10000 to determine a logical major version number.
In all release series, only the last two digits differ between
minor releases (bug-fix releases).

> **Note:**
> This function appeared in PostgreSQL version 9.1, so
> it cannot be used to detect required functionality in earlier
> versions, since calling it will create a link dependency
> on version 9.1 or later.
>
