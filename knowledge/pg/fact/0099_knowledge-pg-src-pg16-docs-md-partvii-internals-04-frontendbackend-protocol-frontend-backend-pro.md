# Overview; Message Flow; Message Formats; Authentication; Query; COPY; Extended Query; Replication Protocol

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVII_internals/04_frontendbackend_protocol.md`
- Source Title: `Frontend/Backend Protocol`
- Source Heading Path: `Frontend/Backend Protocol > Overview; Message Flow; Message Formats; Authentication; Query; COPY; Extended Query; Replication Protocol`
- Source Line Ranges: `95-128, 154-1193, 1194-1202, 1203-1276, 1304-1916, 1917-2039, 2080-3053, 3174-3641`
- Chunk ID: `pg16_fact_0099_6c057e794e`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `327a3fe9ef7bdd15bb674f983f35d97f9f15bcd7342d4369547632124e568be3`

## Retrieval Guidance

- Use When: Implement or debug protocol-level clients and understand PostgreSQL wire messages.
- Retrieval Keywords: frontend backend protocol, PostgreSQL protocol, StartupMessage, Query message, Bind, Execute, CopyData, replication protocol
- Follow-up Guidance: Use the diagnostic record for ErrorResponse and NoticeResponse fields.
- Classification Note: The chapter is a protocol reference for frontend/backend messages, authentication exchanges, query flow, COPY, extended query, and replication messages.

## Official Source Content

### Extended Query Overview

In the extended-query protocol, execution of SQL commands is divided
into multiple steps.  The state retained between steps is represented
by two types of objects: *prepared statements* and
*portals*.  A prepared statement represents the result of
parsing and semantic analysis of a textual query string.
A prepared statement is not in itself ready to execute, because it might
lack specific values for *parameters*.  A portal represents
a ready-to-execute or already-partially-executed statement, with any
missing parameter values filled in.  (For `SELECT` statements,
a portal is equivalent to an open cursor, but we choose to use a different
term since cursors don't handle non-`SELECT` statements.)

The overall execution cycle consists of a *parse* step,
which creates a prepared statement from a textual query string; a
*bind* step, which creates a portal given a prepared
statement and values for any needed parameters; and an
*execute* step that runs a portal's query.  In the case of
a query that returns rows (`SELECT`, `SHOW`, etc.),
the execute step can be told to fetch only
a limited number of rows, so that multiple execute steps might be needed
to complete the operation.

The backend can keep track of multiple prepared statements and portals
(but note that these exist only within a session, and are never shared
across sessions).  Existing prepared statements and portals are
referenced by names assigned when they were created.  In addition,
an "unnamed" prepared statement and portal exist.  Although these
behave largely the same as named objects, operations on them are optimized
for the case of executing a query only once and then discarding it,
whereas operations on named objects are optimized on the expectation
of multiple uses.

## Message Flow

This section describes the message flow and the semantics of each
message type.  (Details of the exact representation of each message
appear in [protocol-message-formats](#protocol-message-formats).)  There are
several different sub-protocols depending on the state of the
connection: start-up, query, function call,
`COPY`, and termination.  There are also special
provisions for asynchronous operations (including notification
responses and command cancellation), which can occur at any time
after the start-up phase.

### Start-up

To begin a session, a frontend opens a connection to the server and sends
a startup message.  This message includes the names of the user and of the
database the user wants to connect to; it also identifies the particular
protocol version to be used.  (Optionally, the startup message can include
additional settings for run-time parameters.)
The server then uses this information and
the contents of its configuration files (such as
`pg_hba.conf`) to determine
whether the connection is provisionally acceptable, and what additional
authentication is required (if any).

The server then sends an appropriate authentication request message,
to which the frontend must reply with an appropriate authentication
response message (such as a password).
For all authentication methods except GSSAPI, SSPI and SASL, there is at
most one request and one response. In some methods, no response
at all is needed from the frontend, and so no authentication request
occurs. For GSSAPI, SSPI and SASL, multiple exchanges of packets may be
needed to complete the authentication.

The authentication cycle ends with the server either rejecting the
connection attempt (ErrorResponse), or sending AuthenticationOk.

The possible messages from the server in this phase are:

**ErrorResponse**
: The connection attempt has been rejected.
The server then immediately closes the connection.

**AuthenticationOk**
: The authentication exchange is successfully completed.

**AuthenticationKerberosV5**
: The frontend must now take part in a Kerberos V5
authentication dialog (not described here, part of the
Kerberos specification) with the server.  If this is
successful, the server responds with an AuthenticationOk,
otherwise it responds with an ErrorResponse. This is no
longer supported.

**AuthenticationCleartextPassword**
: The frontend must now send a PasswordMessage containing the
password in clear-text form.  If
this is the correct password, the server responds with an
AuthenticationOk, otherwise it responds with an ErrorResponse.

**AuthenticationMD5Password**
: The frontend must now send a PasswordMessage containing the
password (with user name) encrypted via MD5, then encrypted
again using the 4-byte random salt specified in the
AuthenticationMD5Password message.  If this is the correct
password, the server responds with an AuthenticationOk,
otherwise it responds with an ErrorResponse.  The actual
PasswordMessage can be computed in SQL as `concat('md5',
md5(concat(md5(concat(password, username)), random-salt)))`.
(Keep in mind the `md5()` function returns its
result as a hex string.)

**AuthenticationGSS**
: The frontend must now initiate a GSSAPI negotiation. The frontend
will send a GSSResponse message with the first part of the GSSAPI
data stream in response to this. If further messages are needed,
the server will respond with AuthenticationGSSContinue.

**AuthenticationSSPI**
: The frontend must now initiate an SSPI negotiation. The frontend
will send a GSSResponse with the first part of the SSPI
data stream in response to this. If further messages are needed,
the server will respond with AuthenticationGSSContinue.

**AuthenticationGSSContinue**
: This message contains the response data from the previous step
of GSSAPI or SSPI negotiation (AuthenticationGSS, AuthenticationSSPI
or a previous AuthenticationGSSContinue). If the GSSAPI
or SSPI data in this message
indicates more data is needed to complete the authentication,
the frontend must send that data as another GSSResponse message. If
GSSAPI or SSPI authentication is completed by this message, the server
will next send AuthenticationOk to indicate successful authentication
or ErrorResponse to indicate failure.

**AuthenticationSASL**
: The frontend must now initiate a SASL negotiation, using one of the
SASL mechanisms listed in the message. The frontend will send a
SASLInitialResponse with the name of the selected mechanism, and the
first part of the SASL data stream in response to this. If further
messages are needed, the server will respond with
AuthenticationSASLContinue. See [sasl-authentication](#sasl-authentication)
for details.

**AuthenticationSASLContinue**
: This message contains challenge data from the previous step of SASL
negotiation (AuthenticationSASL, or a previous
AuthenticationSASLContinue). The frontend must respond with a
SASLResponse message.

**AuthenticationSASLFinal**
: SASL authentication has completed with additional mechanism-specific
data for the client. The server will next send AuthenticationOk to
indicate successful authentication, or an ErrorResponse to indicate
failure. This message is sent only if the SASL mechanism specifies
additional data to be sent from server to client at completion.

**NegotiateProtocolVersion**
: The server does not support the minor protocol version requested
by the client, but does support an earlier version of the protocol;
this message indicates the highest supported minor version.  This
message will also be sent if the client requested unsupported protocol
options (i.e., beginning with `_pq_.`) in the
startup packet.  This message will be followed by an ErrorResponse or
a message indicating the success or failure of authentication.

If the frontend does not support the authentication method
requested by the server, then it should immediately close the
connection.

After having received AuthenticationOk, the frontend must wait
for further messages from the server.  In this phase a backend process
is being started, and the frontend is just an interested bystander.
It is still possible for the startup attempt
to fail (ErrorResponse) or the server to decline support for the requested
minor protocol version (NegotiateProtocolVersion), but in the normal case
the backend will send some ParameterStatus messages, BackendKeyData, and
finally ReadyForQuery.

During this phase the backend will attempt to apply any additional
run-time parameter settings that were given in the startup message.
If successful, these values become session defaults.  An error causes
ErrorResponse and exit.

The possible messages from the backend in this phase are:

**BackendKeyData**
: This message provides secret-key data that the frontend must
save if it wants to be able to issue cancel requests later.
The frontend should not respond to this message, but should
continue listening for a ReadyForQuery message.

**ParameterStatus**
: This message informs the frontend about the current (initial)
setting of backend parameters, such as [guc-client-encoding](#guc-client-encoding) or [guc-datestyle](#guc-datestyle).
The frontend can ignore this message, or record the settings
for its future use; see [protocol-async](#protocol-async) for
more details.  The frontend should not respond to this
message, but should continue listening for a ReadyForQuery
message.

**ReadyForQuery**
: Start-up is completed.  The frontend can now issue commands.

**ErrorResponse**
: Start-up failed.  The connection is closed after sending this
message.

**NoticeResponse**
: A warning message has been issued.  The frontend should
display the message but continue listening for ReadyForQuery
or ErrorResponse.

The ReadyForQuery message is the same one that the backend will
issue after each command cycle.  Depending on the coding needs of
the frontend, it is reasonable to consider ReadyForQuery as
starting a command cycle, or to consider ReadyForQuery as ending the
start-up phase and each subsequent command cycle.

### Simple Query

A simple query cycle is initiated by the frontend sending a Query message
to the backend.  The message includes an SQL command (or commands)
expressed as a text string.
The backend then sends one or more response
messages depending on the contents of the query command string,
and finally a ReadyForQuery response message.  ReadyForQuery
informs the frontend that it can safely send a new command.
(It is not actually necessary for the frontend to wait for
ReadyForQuery before issuing another command, but the frontend must
then take responsibility for figuring out what happens if the earlier
command fails and already-issued later commands succeed.)

The possible response messages from the backend are:

**CommandComplete**
: An SQL command completed normally.

**CopyInResponse**
: The backend is ready to copy data from the frontend to a
table; see [protocol-copy](#protocol-copy).

**CopyOutResponse**
: The backend is ready to copy data from a table to the
frontend; see [protocol-copy](#protocol-copy).

**RowDescription**
: Indicates that rows are about to be returned in response to
a `SELECT`, `FETCH`, etc. query.
The contents of this message describe the column layout of the rows.
This will be followed by a DataRow message for each row being returned
to the frontend.

**DataRow**
: One of the set of rows returned by
a `SELECT`, `FETCH`, etc. query.

**EmptyQueryResponse**
: An empty query string was recognized.

**ErrorResponse**
: An error has occurred.

**ReadyForQuery**
: Processing of the query string is complete.  A separate
message is sent to indicate this because the query string might
contain multiple SQL commands.  (CommandComplete marks the
end of processing one SQL command, not the whole string.)
ReadyForQuery will always be sent, whether processing
terminates successfully or with an error.

**NoticeResponse**
: A warning message has been issued in relation to the query.
Notices are in addition to other responses, i.e., the backend
will continue processing the command.

The response to a `SELECT` query (or other queries that
return row sets, such as `EXPLAIN` or `SHOW`)
normally consists of RowDescription, zero or more
DataRow messages, and then CommandComplete.
`COPY` to or from the frontend invokes special protocol
as described in [protocol-copy](#protocol-copy).
All other query types normally produce only
a CommandComplete message.

Since a query string could contain several queries (separated by
semicolons), there might be several such response sequences before the
backend finishes processing the query string.  ReadyForQuery is issued
when the entire string has been processed and the backend is ready to
accept a new query string.

If a completely empty (no contents other than whitespace) query string
is received, the response is EmptyQueryResponse followed by ReadyForQuery.

In the event of an error, ErrorResponse is issued followed by
ReadyForQuery.  All further processing of the query string is aborted by
ErrorResponse (even if more queries remained in it).  Note that this
might occur partway through the sequence of messages generated by an
individual query.

In simple Query mode, the format of retrieved values is always text,
except when the given command is a `FETCH` from a cursor
declared with the `BINARY` option.  In that case, the
retrieved values are in binary format.  The format codes given in
the RowDescription message tell which format is being used.

A frontend must be prepared to accept ErrorResponse and
NoticeResponse messages whenever it is expecting any other type of
message.  See also [protocol-async](#protocol-async) concerning messages
that the backend might generate due to outside events.

Recommended practice is to code frontends in a state-machine style
that will accept any message type at any time that it could make sense,
rather than wiring in assumptions about the exact sequence of messages.

#### Multiple Statements in a Simple Query

When a simple Query message contains more than one SQL statement
(separated by semicolons), those statements are executed as a single
transaction, unless explicit transaction control commands are included
to force a different behavior.  For example, if the message contains

```
INSERT INTO mytable VALUES(1);
SELECT 1/0;
INSERT INTO mytable VALUES(2);
```

then the divide-by-zero failure in the `SELECT` will force
rollback of the first `INSERT`.  Furthermore, because
execution of the message is abandoned at the first error, the second
`INSERT` is never attempted at all.

If instead the message contains

```
BEGIN;
INSERT INTO mytable VALUES(1);
COMMIT;
INSERT INTO mytable VALUES(2);
SELECT 1/0;
```

then the first `INSERT` is committed by the
explicit `COMMIT` command.  The second `INSERT`
and the `SELECT` are still treated as a single transaction,
so that the divide-by-zero failure will roll back the
second `INSERT`, but not the first one.

This behavior is implemented by running the statements in a
multi-statement Query message in an *implicit transaction
block* unless there is some explicit transaction block for them to
run in.  The main difference between an implicit transaction block and
a regular one is that an implicit block is closed automatically at the
end of the Query message, either by an implicit commit if there was no
error, or an implicit rollback if there was an error.  This is similar
to the implicit commit or rollback that happens for a statement
executed by itself (when not in a transaction block).

If the session is already in a transaction block, as a result of
a `BEGIN` in some previous message, then the Query message
simply continues that transaction block, whether the message contains
one statement or several.  However, if the Query message contains
a `COMMIT` or `ROLLBACK` closing the existing
transaction block, then any following statements are executed in an
implicit transaction block.
Conversely, if a `BEGIN` appears in a multi-statement Query
message, then it starts a regular transaction block that will only be
terminated by an explicit `COMMIT` or `ROLLBACK`,
whether that appears in this Query message or a later one.
If the `BEGIN` follows some statements that were executed as
an implicit transaction block, those statements are not immediately
committed; in effect, they are retroactively included into the new
regular transaction block.

A `COMMIT` or `ROLLBACK` appearing in an implicit
transaction block is executed as normal, closing the implicit block;
however, a warning will be issued since a `COMMIT`
or `ROLLBACK` without a previous `BEGIN` might
represent a mistake.  If more statements follow, a new implicit
transaction block will be started for them.

Savepoints are not allowed in an implicit transaction block, since
they would conflict with the behavior of automatically closing the
block upon any error.

Remember that, regardless of any transaction control commands that may
be present, execution of the Query message stops at the first error.
Thus for example given

```
BEGIN;
SELECT 1/0;
ROLLBACK;
```

in a single Query message, the session will be left inside a failed
regular transaction block, since the `ROLLBACK` is not
reached after the divide-by-zero error.  Another `ROLLBACK`
will be needed to restore the session to a usable state.

Another behavior of note is that initial lexical and syntactic
analysis is done on the entire query string before any of it is
executed.  Thus simple errors (such as a misspelled keyword) in later
statements can prevent execution of any of the statements.  This
is normally invisible to users since the statements would all roll
back anyway when done as an implicit transaction block.  However,
it can be visible when attempting to do multiple transactions within a
multi-statement Query.  For instance, if a typo turned our previous
example into

```
BEGIN;
INSERT INTO mytable VALUES(1);
COMMIT;
INSERT INTO mytable VALUES(2);
SELCT 1/0;
```

then none of the statements would get run, resulting in the visible
difference that the first `INSERT` is not committed.
Errors detected at semantic analysis or later, such as a misspelled
table or column name, do not have this effect.

Lastly, note that all the statements within the Query message will
observe the same value of `statement_timestamp()`,
since that timestamp is updated only upon receipt of the Query
message.  This will result in them all observing the same
value of `transaction_timestamp()` as well,
except in cases where the query string ends a previously-started
transaction and begins a new one.

### Extended Query

The extended query protocol breaks down the above-described simple
query protocol into multiple steps.  The results of preparatory
steps can be re-used multiple times for improved efficiency.
Furthermore, additional features are available, such as the possibility
of supplying data values as separate parameters instead of having to
insert them directly into a query string.

In the extended protocol, the frontend first sends a Parse message,
which contains a textual query string, optionally some information
about data types of parameter placeholders, and the
name of a destination prepared-statement object (an empty string
selects the unnamed prepared statement).  The response is
either ParseComplete or ErrorResponse.  Parameter data types can be
specified by OID; if not given, the parser attempts to infer the
data types in the same way as it would do for untyped literal string
constants.

> **Note:**

> A parameter data type can be left unspecified by setting it to zero,
> or by making the array of parameter type OIDs shorter than the
> number of parameter symbols (`$``n`)
> used in the query string.  Another special case is that a parameter's
> type can be specified as `void` (that is, the OID of the
> `void` pseudo-type).  This is meant to allow parameter symbols
> to be used for function parameters that are actually OUT parameters.
> Ordinarily there is no context in which a `void` parameter
> could be used, but if such a parameter symbol appears in a function's
> parameter list, it is effectively ignored.  For example, a function
> call such as `foo($1,$2,$3,$4)` could match a function with
> two IN and two OUT arguments, if `$3` and `$4`
> are specified as having type `void`.
>

> **Note:**

> The query string contained in a Parse message cannot include more
> than one SQL statement; else a syntax error is reported.  This
> restriction does not exist in the simple-query protocol, but it
> does exist in the extended protocol, because allowing prepared
> statements or portals to contain multiple commands would complicate
> the protocol unduly.
>

If successfully created, a named prepared-statement object lasts till
the end of the current session, unless explicitly destroyed.  An unnamed
prepared statement lasts only until the next Parse statement specifying
the unnamed statement as destination is issued.  (Note that a simple
Query message also destroys the unnamed statement.)  Named prepared
statements must be explicitly closed before they can be redefined by
another Parse message, but this is not required for the unnamed statement.
Named prepared statements can also be created and accessed at the SQL
command level, using `PREPARE` and `EXECUTE`.

Once a prepared statement exists, it can be readied for execution using a
Bind message.  The Bind message gives the name of the source prepared
statement (empty string denotes the unnamed prepared statement), the name
of the destination portal (empty string denotes the unnamed portal), and
the values to use for any parameter placeholders present in the prepared
statement.  The
supplied parameter set must match those needed by the prepared statement.
(If you declared any `void` parameters in the Parse message,
pass NULL values for them in the Bind message.)
Bind also specifies the format to use for any data returned
by the query; the format can be specified overall, or per-column.
The response is either BindComplete or ErrorResponse.

> **Note:**

> The choice between text and binary output is determined by the format
> codes given in Bind, regardless of the SQL command involved.  The
> `BINARY` attribute in cursor declarations is irrelevant when
> using extended query protocol.
>

Query planning typically occurs when the Bind message is processed.
If the prepared statement has no parameters, or is executed repeatedly,
the server might save the created plan and re-use it during subsequent
Bind messages for the same prepared statement.  However, it will do so
only if it finds that a generic plan can be created that is not much
less efficient than a plan that depends on the specific parameter values
supplied.  This happens transparently so far as the protocol is concerned.

If successfully created, a named portal object lasts till the end of the
current transaction, unless explicitly destroyed.  An unnamed portal is
destroyed at the end of the transaction, or as soon as the next Bind
statement specifying the unnamed portal as destination is issued.  (Note
that a simple Query message also destroys the unnamed portal.)  Named
portals must be explicitly closed before they can be redefined by another
Bind message, but this is not required for the unnamed portal.
Named portals can also be created and accessed at the SQL
command level, using `DECLARE CURSOR` and `FETCH`.

Once a portal exists, it can be executed using an Execute message.
The Execute message specifies the portal name (empty string denotes the
unnamed portal) and
a maximum result-row count (zero meaning "fetch all rows").
The result-row count is only meaningful for portals
containing commands that return row sets; in other cases the command is
always executed to completion, and the row count is ignored.
The possible
responses to Execute are the same as those described above for queries
issued via simple query protocol, except that Execute doesn't cause
ReadyForQuery or RowDescription to be issued.

If Execute terminates before completing the execution of a portal
(due to reaching a nonzero result-row count), it will send a
PortalSuspended message; the appearance of this message tells the frontend
that another Execute should be issued against the same portal to
complete the operation.  The CommandComplete message indicating
completion of the source SQL command is not sent until
the portal's execution is completed.  Therefore, an Execute phase is
always terminated by the appearance of exactly one of these messages:
CommandComplete, EmptyQueryResponse (if the portal was created from
an empty query string), ErrorResponse, or PortalSuspended.

At completion of each series of extended-query messages, the frontend
should issue a Sync message.  This parameterless message causes the
backend to close the current transaction if it's not inside a
`BEGIN`/`COMMIT` transaction block ("close"
meaning to commit if no error, or roll back if error).  Then a
ReadyForQuery response is issued.  The purpose of Sync is to provide
a resynchronization point for error recovery.  When an error is detected
while processing any extended-query message, the backend issues
ErrorResponse, then reads and discards messages until a Sync is reached,
then issues ReadyForQuery and returns to normal message processing.
(But note that no skipping occurs if an error is detected
*while* processing Sync — this ensures that there is one
and only one ReadyForQuery sent for each Sync.)

> **Note:**

> Sync does not cause a transaction block opened with `BEGIN`
> to be closed.  It is possible to detect this situation since the
> ReadyForQuery message includes transaction status information.
>

In addition to these fundamental, required operations, there are several
optional operations that can be used with extended-query protocol.

The Describe message (portal variant) specifies the name of an existing
portal (or an empty string for the unnamed portal).  The response is a
RowDescription message describing the rows that will be returned by
executing the portal; or a NoData message if the portal does not contain a
query that will return rows; or ErrorResponse if there is no such portal.

The Describe message (statement variant) specifies the name of an existing
prepared statement (or an empty string for the unnamed prepared
statement).  The response is a ParameterDescription message describing the
parameters needed by the statement, followed by a RowDescription message
describing the rows that will be returned when the statement is eventually
executed (or a NoData message if the statement will not return rows).
ErrorResponse is issued if there is no such prepared statement.  Note that
since Bind has not yet been issued, the formats to be used for returned
columns are not yet known to the backend; the format code fields in the
RowDescription message will be zeroes in this case.

> **Tip:**

> In most scenarios the frontend should issue one or the other variant
> of Describe before issuing Execute, to ensure that it knows how to
> interpret the results it will get back.
>

The Close message closes an existing prepared statement or portal
and releases resources.  It is not an error to issue Close against
a nonexistent statement or portal name.  The response is normally
CloseComplete, but could be ErrorResponse if some difficulty is
encountered while releasing resources.  Note that closing a prepared
statement implicitly closes any open portals that were constructed
from that statement.

The Flush message does not cause any specific output to be generated,
but forces the backend to deliver any data pending in its output
buffers.  A Flush must be sent after any extended-query command except
Sync, if the frontend wishes to examine the results of that command before
issuing more commands.  Without Flush, messages returned by the backend
will be combined into the minimum possible number of packets to minimize
network overhead.

> **Note:**

> The simple Query message is approximately equivalent to the series Parse,
> Bind, portal Describe, Execute, Close, Sync, using the unnamed prepared
> statement and portal objects and no parameters.  One difference is that
> it will accept multiple SQL statements in the query string, automatically
> performing the bind/describe/execute sequence for each one in succession.
> Another difference is that it will not return ParseComplete, BindComplete,
> CloseComplete, or NoData messages.
>

### Pipelining

Use of the extended query protocol
allows *pipelining*, which means sending a series
of queries without waiting for earlier ones to complete.  This reduces
the number of network round trips needed to complete a given series of
operations.  However, the user must carefully consider the required
behavior if one of the steps fails, since later queries will already
be in flight to the server.

One way to deal with that is to make the whole query series be a
single transaction, that is wrap it in `BEGIN` ...
`COMMIT`.  However, this does not help if one wishes
for some of the commands to commit independently of others.

The extended query protocol provides another way to manage this
concern, which is to omit sending Sync messages between steps that
are dependent.  Since, after an error, the backend will skip command
messages until it finds Sync, this allows later commands in a pipeline
to be skipped automatically when an earlier one fails, without the
client having to manage that explicitly with `BEGIN`
and `COMMIT`.  Independently-committable segments
of the pipeline can be separated by Sync messages.

If the client has not issued an explicit `BEGIN`,
then each Sync ordinarily causes an implicit `COMMIT`
if the preceding step(s) succeeded, or an
implicit `ROLLBACK` if they failed.  However, there
are a few DDL commands (such as `CREATE DATABASE`)
that cannot be executed inside a transaction block.  If one of
these is executed in a pipeline, it will fail unless it is the first
command in the pipeline.  Furthermore, upon success it will force an
immediate commit to preserve database consistency.  Thus a Sync
immediately following one of these commands has no effect except to
respond with ReadyForQuery.

When using this method, completion of the pipeline must be determined
by counting ReadyForQuery messages and waiting for that to reach the
number of Syncs sent.  Counting command completion responses is
unreliable, since some of the commands may be skipped and thus not
produce a completion message.

### Function Call

The Function Call sub-protocol allows the client to request a direct
call of any function that exists in the database's
`pg_proc` system catalog.  The client must have
execute permission for the function.

> **Note:**

> The Function Call sub-protocol is a legacy feature that is probably best
> avoided in new code.  Similar results can be accomplished by setting up
> a prepared statement that does `SELECT function($1, ...)`.
> The Function Call cycle can then be replaced with Bind/Execute.
>

A Function Call cycle is initiated by the frontend sending a
FunctionCall message to the backend.  The backend then sends one
or more response messages depending on the results of the function
call, and finally a ReadyForQuery response message.  ReadyForQuery
informs the frontend that it can safely send a new query or
function call.

The possible response messages from the backend are:

**ErrorResponse**
: An error has occurred.

**FunctionCallResponse**
: The function call was completed and returned the result given
in the message.
(Note that the Function Call protocol can only handle a single
scalar result, not a row type or set of results.)

**ReadyForQuery**
: Processing of the function call is complete.  ReadyForQuery
will always be sent, whether processing terminates
successfully or with an error.

**NoticeResponse**
: A warning message has been issued in relation to the function
call.  Notices are in addition to other responses, i.e., the
backend will continue processing the command.

### COPY Operations

The `COPY` command allows high-speed bulk data transfer
to or from the server.  Copy-in and copy-out operations each switch
the connection into a distinct sub-protocol, which lasts until the
operation is completed.

Copy-in mode (data transfer to the server) is initiated when the
backend executes a `COPY FROM STDIN` SQL statement.  The backend
sends a CopyInResponse message to the frontend.  The frontend should
then send zero or more CopyData messages, forming a stream of input
data.  (The message boundaries are not required to have anything to do
with row boundaries, although that is often a reasonable choice.)
The frontend can terminate the copy-in mode by sending either a CopyDone
message (allowing successful termination) or a CopyFail message (which
will cause the `COPY` SQL statement to fail with an
error).  The backend then reverts to the command-processing mode it was
in before the `COPY` started, which will be either simple or
extended query protocol.  It will next send either CommandComplete
(if successful) or ErrorResponse (if not).

In the event of a backend-detected error during copy-in mode (including
receipt of a CopyFail message), the backend will issue an ErrorResponse
message.  If the `COPY` command was issued via an extended-query
message, the backend will now discard frontend messages until a Sync
message is received, then it will issue ReadyForQuery and return to normal
processing.  If the `COPY` command was issued in a simple
Query message, the rest of that message is discarded and ReadyForQuery
is issued.  In either case, any subsequent CopyData, CopyDone, or CopyFail
messages issued by the frontend will simply be dropped.

The backend will ignore Flush and Sync messages received during copy-in
mode.  Receipt of any other non-copy message type constitutes an error
that will abort the copy-in state as described above.  (The exception for
Flush and Sync is for the convenience of client libraries that always
send Flush or Sync after an Execute message, without checking whether
the command to be executed is a `COPY FROM STDIN`.)

Copy-out mode (data transfer from the server) is initiated when the
backend executes a `COPY TO STDOUT` SQL statement.  The backend
sends a CopyOutResponse message to the frontend, followed by
zero or more CopyData messages (always one per row), followed by CopyDone.
The backend then reverts to the command-processing mode it was
in before the `COPY` started, and sends CommandComplete.
The frontend cannot abort the transfer (except by closing the connection
or issuing a Cancel request),
but it can discard unwanted CopyData and CopyDone messages.

In the event of a backend-detected error during copy-out mode,
the backend will issue an ErrorResponse message and revert to normal
processing.  The frontend should treat receipt of ErrorResponse as
terminating the copy-out mode.

It is possible for NoticeResponse and ParameterStatus messages to be
interspersed between CopyData messages; frontends must handle these cases,
and should be prepared for other asynchronous message types as well (see
[protocol-async](#protocol-async)).  Otherwise, any message type other than
CopyData or CopyDone may be treated as terminating copy-out mode.

There is another Copy-related mode called copy-both, which allows
high-speed bulk data transfer to *and* from the server.
Copy-both mode is initiated when a backend in walsender mode
executes a `START_REPLICATION` statement.  The
backend sends a CopyBothResponse message to the frontend.  Both
the backend and the frontend may then send CopyData messages
until either end sends a CopyDone message. After the client
sends a CopyDone message, the connection goes from copy-both mode to
copy-out mode, and the client may not send any more CopyData messages.
Similarly, when the server sends a CopyDone message, the connection
goes into copy-in mode, and the server may not send any more CopyData
messages. After both sides have sent a CopyDone message, the copy mode
is terminated, and the backend reverts to the command-processing mode.
In the event of a backend-detected error during copy-both mode,
the backend will issue an ErrorResponse message, discard frontend messages
until a Sync message is received, and then issue ReadyForQuery and return
to normal processing.  The frontend should treat receipt of ErrorResponse
as terminating the copy in both directions; no CopyDone should be sent
in this case.  See [protocol-replication](#protocol-replication) for more
information on the subprotocol transmitted over copy-both mode.

The CopyInResponse, CopyOutResponse and CopyBothResponse messages
include fields that inform the frontend of the number of columns
per row and the format codes being used for each column.  (As of
the present implementation, all columns in a given `COPY`
operation will use the same format, but the message design does not
assume this.)

### Asynchronous Operations

There are several cases in which the backend will send messages that
are not specifically prompted by the frontend's command stream.
Frontends must be prepared to deal with these messages at any time,
even when not engaged in a query.
At minimum, one should check for these cases before beginning to
read a query response.

It is possible for NoticeResponse messages to be generated due to
outside activity; for example, if the database administrator commands
a "fast" database shutdown, the backend will send a NoticeResponse
indicating this fact before closing the connection.  Accordingly,
frontends should always be prepared to accept and display NoticeResponse
messages, even when the connection is nominally idle.

ParameterStatus messages will be generated whenever the active
value changes for any of the parameters the backend believes the
frontend should know about.  Most commonly this occurs in response
to a `SET` SQL command executed by the frontend, and
this case is effectively synchronous — but it is also possible
for parameter status changes to occur because the administrator
changed a configuration file and then sent the
SIGHUP signal to the server.  Also,
if a `SET` command is rolled back, an appropriate
ParameterStatus message will be generated to report the current
effective value.

At present there is a hard-wired set of parameters for which
ParameterStatus will be generated.  They are:

(`server_encoding`, `TimeZone`, and
`integer_datetimes` were not reported by releases before 8.0;
`standard_conforming_strings` was not reported by releases
before 8.1;
`IntervalStyle` was not reported by releases before 8.4;
`application_name` was not reported by releases before
9.0;
`default_transaction_read_only` and
`in_hot_standby` were not reported by releases before
14; `scram_iterations` was not reported by releases
before 16.)
Note that
`server_version`,
`server_encoding` and
`integer_datetimes`
are pseudo-parameters that cannot change after startup.
This set might change in the future, or even become configurable.
Accordingly, a frontend should simply ignore ParameterStatus for
parameters that it does not understand or care about.

If a frontend issues a `LISTEN` command, then the
backend will send a NotificationResponse message (not to be
confused with NoticeResponse!)  whenever a
`NOTIFY` command is executed for the same
channel name.

> **Note:**

> At present, NotificationResponse can only be sent outside a
> transaction, and thus it will not occur in the middle of a
> command-response series, though it might occur just before ReadyForQuery.
> It is unwise to design frontend logic that assumes that, however.
> Good practice is to be able to accept NotificationResponse at any
> point in the protocol.
>

### Canceling Requests in Progress

During the processing of a query, the frontend might request
cancellation of the query.  The cancel request is not sent
directly on the open connection to the backend for reasons of
implementation efficiency: we don't want to have the backend
constantly checking for new input from the frontend during query
processing.  Cancel requests should be relatively infrequent, so
we make them slightly cumbersome in order to avoid a penalty in
the normal case.

To issue a cancel request, the frontend opens a new connection to
the server and sends a CancelRequest message, rather than the
StartupMessage message that would ordinarily be sent across a new
connection.  The server will process this request and then close
the connection.  For security reasons, no direct reply is made to
the cancel request message.

A CancelRequest message will be ignored unless it contains the
same key data (PID and secret key) passed to the frontend during
connection start-up.  If the request matches the PID and secret
key for a currently executing backend, the processing of the
current query is aborted.  (In the existing implementation, this is
done by sending a special signal to the backend process that is
processing the query.)

The cancellation signal might or might not have any effect — for
example, if it arrives after the backend has finished processing
the query, then it will have no effect.  If the cancellation is
effective, it results in the current command being terminated
early with an error message.

The upshot of all this is that for reasons of both security and
efficiency, the frontend has no direct way to tell whether a
cancel request has succeeded.  It must continue to wait for the
backend to respond to the query.  Issuing a cancel simply improves
the odds that the current query will finish soon, and improves the
odds that it will fail with an error message instead of
succeeding.

Since the cancel request is sent across a new connection to the
server and not across the regular frontend/backend communication
link, it is possible for the cancel request to be issued by any
process, not just the frontend whose query is to be canceled.
This might provide additional flexibility when building
multiple-process applications.  It also introduces a security
risk, in that unauthorized persons might try to cancel queries.
The security risk is addressed by requiring a dynamically
generated secret key to be supplied in cancel requests.

### Termination

The normal, graceful termination procedure is that the frontend
sends a Terminate message and immediately closes the connection.
On receipt of this message, the backend closes the connection and
terminates.

In rare cases (such as an administrator-commanded database shutdown)
the backend might disconnect without any frontend request to do so.
In such cases the backend will attempt to send an error or notice message
giving the reason for the disconnection before it closes the connection.

Other termination scenarios arise from various failure cases, such as core
dump at one end or the other, loss of the communications link, loss of
message-boundary synchronization, etc.  If either frontend or backend sees
an unexpected closure of the connection, it should clean
up and terminate.  The frontend has the option of launching a new backend
by recontacting the server if it doesn't want to terminate itself.
Closing the connection is also advisable if an unrecognizable message type
is received, since this probably indicates loss of message-boundary sync.

For either normal or abnormal termination, any open transaction is
rolled back, not committed.  One should note however that if a
frontend disconnects while a non-`SELECT` query
is being processed, the backend will probably finish the query
before noticing the disconnection.  If the query is outside any
transaction block (`BEGIN` ... `COMMIT`
sequence) then its results might be committed before the
disconnection is recognized.

### SSL Session Encryption

If PostgreSQL was built with
SSL support, frontend/backend communications
can be encrypted using SSL.  This provides
communication security in environments where attackers might be
able to capture the session traffic. For more information on
encrypting PostgreSQL sessions with
SSL, see [ssl-tcp](#ssl-tcp).

To initiate an SSL-encrypted connection, the
frontend initially sends an SSLRequest message rather than a
StartupMessage.  The server then responds with a single byte
containing `S` or `N`, indicating that it is
willing or unwilling to perform SSL,
respectively.  The frontend might close the connection at this point
if it is dissatisfied with the response.  To continue after
`S`, perform an SSL startup handshake
(not described here, part of the SSL
specification) with the server.  If this is successful, continue
with sending the usual StartupMessage.  In this case the
StartupMessage and all subsequent data will be
SSL-encrypted.  To continue after
`N`, send the usual StartupMessage and proceed without
encryption.
(Alternatively, it is permissible to issue a GSSENCRequest message
after an `N` response to try to
use GSSAPI encryption instead
of SSL.)

The frontend should also be prepared to handle an ErrorMessage
response to SSLRequest from the server. The frontend should not display
this error message to the user/application, since the server has not been
authenticated
([CVE-2024-10977](https://www.postgresql.org/support/security/CVE-2024-10977/)).
In this case the connection must
be closed, but the frontend might choose to open a fresh connection
and proceed without requesting SSL.

When SSL encryption can be performed, the server
is expected to send only the single `S` byte and then
wait for the frontend to initiate an SSL handshake.
If additional bytes are available to read at this point, it likely
means that a man-in-the-middle is attempting to perform a
buffer-stuffing attack
([CVE-2021-23222](https://www.postgresql.org/support/security/CVE-2021-23222/)).
Frontends should be coded either to read exactly one byte from the
socket before turning the socket over to their SSL library, or to
treat it as a protocol violation if they find they have read additional
bytes.

An initial SSLRequest can also be used in a connection that is being
opened to send a CancelRequest message.

While the protocol itself does not provide a way for the server to
force SSL encryption, the administrator can
configure the server to reject unencrypted sessions as a byproduct
of authentication checking.

### GSSAPI Session Encryption

If PostgreSQL was built with
GSSAPI support, frontend/backend communications
can be encrypted using GSSAPI.  This provides
communication security in environments where attackers might be
able to capture the session traffic. For more information on
encrypting PostgreSQL sessions with
GSSAPI, see [gssapi-enc](#gssapi-enc).

To initiate a GSSAPI-encrypted connection, the
frontend initially sends a GSSENCRequest message rather than a
StartupMessage.  The server then responds with a single byte
containing `G` or `N`, indicating that it
is willing or unwilling to perform GSSAPI encryption,
respectively.  The frontend might close the connection at this point
if it is dissatisfied with the response.  To continue after
`G`, using the GSSAPI C bindings as discussed in
[RFC 2744](https://datatracker.ietf.org/doc/html/rfc2744)
or equivalent, perform a GSSAPI initialization by
calling `gss_init_sec_context()` in a loop and sending
the result to the server, starting with an empty input and then with each
result from the server, until it returns no output.  When sending the
results of `gss_init_sec_context()` to the server,
prepend the length of the message as a four byte integer in network byte
order.
To continue after
`N`, send the usual StartupMessage and proceed without
encryption.
(Alternatively, it is permissible to issue an SSLRequest message
after an `N` response to try to
use SSL encryption instead
of GSSAPI.)

The frontend should also be prepared to handle an ErrorMessage
response to GSSENCRequest from the server.  The frontend should not display
this error message to the user/application, since the server has not been
authenticated
([CVE-2024-10977](https://www.postgresql.org/support/security/CVE-2024-10977/)).
In this case the connection must be closed, but the frontend might choose
to open a fresh connection and proceed without requesting
GSSAPI encryption.

When GSSAPI encryption can be performed, the server
is expected to send only the single `G` byte and then
wait for the frontend to initiate a GSSAPI handshake.
If additional bytes are available to read at this point, it likely
means that a man-in-the-middle is attempting to perform a
buffer-stuffing attack
([CVE-2021-23222](https://www.postgresql.org/support/security/CVE-2021-23222/)).
Frontends should be coded either to read exactly one byte from the
socket before turning the socket over to their GSSAPI library, or to
treat it as a protocol violation if they find they have read additional
bytes.

An initial GSSENCRequest can also be used in a connection that is being
opened to send a CancelRequest message.

Once GSSAPI encryption has been successfully
established, use `gss_wrap()` to
encrypt the usual StartupMessage and all subsequent data, prepending the
length of the result from `gss_wrap()` as a four byte
integer in network byte order to the actual encrypted payload.  Note that
the server will only accept encrypted packets from the client which are less
than 16kB; `gss_wrap_size_limit()` should be used by the
client to determine the size of the unencrypted message which will fit
within this limit and larger messages should be broken up into multiple
`gss_wrap()` calls.  Typical segments are 8kB of
unencrypted data, resulting in encrypted packets of slightly larger than 8kB
but well within the 16kB maximum.  The server can be expected to not send
encrypted packets of larger than 16kB to the client.

While the protocol itself does not provide a way for the server to
force GSSAPI encryption, the administrator can
configure the server to reject unencrypted sessions as a byproduct
of authentication checking.

## SASL Authentication

*SASL* is a framework for authentication in connection-oriented
protocols. At the moment, PostgreSQL implements two SASL
authentication mechanisms, SCRAM-SHA-256 and SCRAM-SHA-256-PLUS. More
might be added in the future. The below steps illustrate how SASL
authentication is performed in general, while the next subsection gives
more details on SCRAM-SHA-256 and SCRAM-SHA-256-PLUS.

## SASL Authentication Message Flow

To begin a SASL authentication exchange, the server sends an
AuthenticationSASL message. It includes a list of SASL authentication
mechanisms that the server can accept, in the server's preferred order.

The client selects one of the supported mechanisms from the list, and sends
a SASLInitialResponse message to the server. The message includes the name
of the selected mechanism, and an optional Initial Client Response, if the
selected mechanism uses that.

One or more server-challenge and client-response message will follow. Each
server-challenge is sent in an AuthenticationSASLContinue message, followed
by a response from client in a SASLResponse message. The particulars of
the messages are mechanism specific.

Finally, when the authentication exchange is completed successfully, the
server sends an AuthenticationSASLFinal message, followed
immediately by an AuthenticationOk message. The AuthenticationSASLFinal
contains additional server-to-client data, whose content is particular to the
selected authentication mechanism. If the authentication mechanism doesn't
use additional data that's sent at completion, the AuthenticationSASLFinal
message is not sent.

On error, the server can abort the authentication at any stage, and send an
ErrorMessage.

### SCRAM-SHA-256 Authentication

The implemented SASL mechanisms at the moment
are `SCRAM-SHA-256` and its variant with channel
binding `SCRAM-SHA-256-PLUS`. They are described in
detail in [RFC 7677](https://datatracker.ietf.org/doc/html/rfc7677)
and [RFC 5802](https://datatracker.ietf.org/doc/html/rfc5802).

When SCRAM-SHA-256 is used in PostgreSQL, the server will ignore the user name
that the client sends in the `client-first-message`. The user name
that was already sent in the startup message is used instead.
PostgreSQL supports multiple character encodings, while SCRAM
dictates UTF-8 to be used for the user name, so it might be impossible to
represent the PostgreSQL user name in UTF-8.

The SCRAM specification dictates that the password is also in UTF-8, and is
processed with the *SASLprep* algorithm.
PostgreSQL, however, does not require UTF-8 to be used for
the password. When a user's password is set, it is processed with SASLprep
as if it was in UTF-8, regardless of the actual encoding used. However, if
it is not a legal UTF-8 byte sequence, or it contains UTF-8 byte sequences
that are prohibited by the SASLprep algorithm, the raw password will be used
without SASLprep processing, instead of throwing an error. This allows the
password to be normalized when it is in UTF-8, but still allows a non-UTF-8
password to be used, and doesn't require the system to know which encoding
the password is in.

*Channel binding* is supported in PostgreSQL builds with
SSL support. The SASL mechanism name for SCRAM with channel binding is
`SCRAM-SHA-256-PLUS`.  The channel binding type used by
PostgreSQL is `tls-server-end-point`.

In SCRAM without channel binding, the server chooses
a random number that is transmitted to the client to be mixed with the
user-supplied password in the transmitted password hash.  While this
prevents the password hash from being successfully retransmitted in
a later session, it does not prevent a fake server between the real
server and client from passing through the server's random value
and successfully authenticating.

SCRAM with channel binding prevents such
man-in-the-middle attacks by mixing the signature of the server's
certificate into the transmitted password hash. While a fake server can
retransmit the real server's certificate, it doesn't have access to the
private key matching that certificate, and therefore cannot prove it is
the owner, causing SSL connection failure.

## Streaming Replication Protocol

To initiate streaming replication, the frontend sends the
`replication` parameter in the startup message. A Boolean
value of `true` (or `on`,
`yes`, `1`) tells the backend to go into
physical replication walsender mode, wherein a small set of replication
commands, shown below, can be issued instead of SQL statements.

Passing `database` as the value for the
`replication` parameter instructs the backend to go into
logical replication walsender mode, connecting to the database specified in
the `dbname` parameter.  In logical replication walsender
mode, the replication commands shown below as well as normal SQL commands can
be issued.

In either physical replication or logical replication walsender mode, only the
simple query protocol can be used.

For the purpose of testing replication commands, you can make a replication
connection via psql or any other
libpq-using tool with a connection string including
the `replication` option,
e.g.:

```
psql "dbname=postgres replication=database" -c "IDENTIFY_SYSTEM;"
```

However, it is often more useful to use
[app-pgreceivewal](#app-pgreceivewal) (for physical replication) or
[app-pgrecvlogical](#app-pgrecvlogical) (for logical replication).

Replication commands are logged in the server log when
[guc-log-replication-commands](#guc-log-replication-commands) is enabled.

The commands accepted in replication mode are:

**`IDENTIFY_SYSTEM`**
: Requests the server to identify itself. Server replies with a result
set of a single row, containing four fields:

`systemid` (`text`)

The unique system identifier identifying the cluster. This
can be used to check that the base backup used to initialize the
standby came from the same cluster.

**`timeline` (`int8`)**
: Current timeline ID. Also useful to check that the standby is
consistent with the primary.

**`xlogpos` (`text`)**
: Current WAL flush location. Useful to get a known location in the
write-ahead log where streaming can start.

**`dbname` (`text`)**
: Database connected to or null.

`SHOW` `name`

Requests the server to send the current setting of a run-time parameter.
This is similar to the SQL command [sql-show](#sql-show).

**`name`**
: The name of a run-time parameter. Available parameters are documented
in [runtime-config](#runtime-config).

`TIMELINE_HISTORY` `tli`

Requests the server to send over the timeline history file for timeline
`tli`.  Server replies with a
result set of a single row, containing two fields.  While the fields
are labeled as `text`, they effectively return raw bytes,
with no encoding conversion:

**`filename` (`text`)**
: File name of the timeline history file, e.g., `00000002.history`.

**`content` (`text`)**
: Contents of the timeline history file.

`CREATE_REPLICATION_SLOT` `slot_name` [ `TEMPORARY` ] { `PHYSICAL` | `LOGICAL` `output_plugin` } [ ( `option` [, ...] ) ]

Create a physical or logical replication
slot. See [streaming-replication-slots](#streaming-replication-slots) for more about
replication slots.

**`slot_name`**
: The name of the slot to create. Must be a valid replication slot
name (see [streaming-replication-slots-manipulation](#streaming-replication-slots-manipulation)).

**`output_plugin`**
: The name of the output plugin used for logical decoding
(see [logicaldecoding-output-plugin](#logicaldecoding-output-plugin)).

**`TEMPORARY`**
: Specify that this replication slot is a temporary one. Temporary
slots are not saved to disk and are automatically dropped on error
or when the session has finished.

The following options are supported:

**`TWO_PHASE [ `boolean` ]`**
: If true, this logical replication slot supports decoding of two-phase
commit. With this option, commands related to two-phase commit such as
`PREPARE TRANSACTION`, `COMMIT PREPARED`
and `ROLLBACK PREPARED` are decoded and transmitted.
The transaction will be decoded and transmitted at
`PREPARE TRANSACTION` time.
The default is false.

**`RESERVE_WAL [ `boolean` ]`**
: If true, this physical replication slot reserves WAL
immediately.  Otherwise, WAL is only reserved upon
connection from a streaming replication client.
The default is false.

**`SNAPSHOT { 'export' | 'use' | 'nothing' }`**
: Decides what to do with the snapshot created during logical slot
initialization. `'export'`, which is the default,
will export the snapshot for use in other sessions. This option can't
be used inside a transaction.  `'use'` will use the
snapshot for the current transaction executing the command. This
option must be used in a transaction, and
`CREATE_REPLICATION_SLOT` must be the first command
run in that transaction.  Finally, `'nothing'` will
just use the snapshot for logical decoding as normal but won't do
anything else with it.

In response to this command, the server will send a one-row result set
containing the following fields:

**`slot_name` (`text`)**
: The name of the newly-created replication slot.

**`consistent_point` (`text`)**
: The WAL location at which the slot became consistent.  This is the
earliest location from which streaming can start on this replication
slot.

**`snapshot_name` (`text`)**
: The identifier of the snapshot exported by the command.  The
snapshot is valid until a new command is executed on this connection
or the replication connection is closed.  Null if the created slot
is physical.

**`output_plugin` (`text`)**
: The name of the output plugin used by the newly-created replication
slot.  Null if the created slot is physical.

`CREATE_REPLICATION_SLOT` `slot_name` [ `TEMPORARY` ] { `PHYSICAL` [ `RESERVE_WAL` ] | `LOGICAL` `output_plugin` [ `EXPORT_SNAPSHOT` | `NOEXPORT_SNAPSHOT` | `USE_SNAPSHOT` | `TWO_PHASE` ] }

For compatibility with older releases, this alternative syntax for
the `CREATE_REPLICATION_SLOT` command is still supported.

`READ_REPLICATION_SLOT` `slot_name`

Read some information associated with a replication slot. Returns a tuple
with `NULL` values if the replication slot does not
exist. This command is currently only supported for physical replication
slots.

In response to this command, the server will return a one-row result set,
containing the following fields:

**`slot_type` (`text`)**
: The replication slot's type, either `physical` or
`NULL`.

**`restart_lsn` (`text`)**
: The replication slot's `restart_lsn`.

**`restart_tli` (`int8`)**
: The timeline ID associated with `restart_lsn`,
following the current timeline history.

`START_REPLICATION` [ `SLOT` `slot_name` ] [ `PHYSICAL` ] `XXX/XXX` [ `TIMELINE` `tli` ]

Instructs server to start streaming WAL, starting at
WAL location `XXX/XXX`.
If `TIMELINE` option is specified,
streaming starts on timeline `tli`;
otherwise, the server's current timeline is selected. The server can
reply with an error, for example if the requested section of WAL has already
been recycled. On success, the server responds with a CopyBothResponse
message, and then starts to stream WAL to the frontend.

If a slot's name is provided
via `slot_name`, it will be updated
as replication progresses so that the server knows which WAL segments,
and if `hot_standby_feedback` is on which transactions,
are still needed by the standby.

If the client requests a timeline that's not the latest but is part of
the history of the server, the server will stream all the WAL on that
timeline starting from the requested start point up to the point where
the server switched to another timeline. If the client requests
streaming at exactly the end of an old timeline, the server skips COPY
mode entirely.

After streaming all the WAL on a timeline that is not the latest one,
the server will end streaming by exiting the COPY mode. When the client
acknowledges this by also exiting COPY mode, the server sends a result
set with one row and two columns, indicating the next timeline in this
server's history. The first column is the next timeline's ID (type `int8`), and the
second column is the WAL location where the switch happened (type `text`). Usually,
the switch position is the end of the WAL that was streamed, but there
are corner cases where the server can send some WAL from the old
timeline that it has not itself replayed before promoting. Finally, the
server sends two CommandComplete messages (one that ends the CopyData
and the other ends the `START_REPLICATION` itself), and
is ready to accept a new command.

WAL data is sent as a series of CopyData messages.  (This allows
other information to be intermixed; in particular the server can send
an ErrorResponse message if it encounters a failure after beginning
to stream.)  The payload of each CopyData message from server to the
client contains a message of one of the following formats:

**XLogData (B)**
: Byte1('w')

Identifies the message as WAL data.

**Int64**
: The starting point of the WAL data in this message.

**Int64**
: The current end of WAL on the server.

**Int64**
: The server's system clock at the time of transmission, as
microseconds since midnight on 2000-01-01.

**Byte`n`**
: A section of the WAL data stream.

A single WAL record is never split across two XLogData messages.
When a WAL record crosses a WAL page boundary, and is therefore
already split using continuation records, it can be split at the page
boundary. In other words, the first main WAL record and its
continuation records can be sent in different XLogData messages.

Primary keepalive message (B)

**Byte1('k')**
: Identifies the message as a sender keepalive.

**Int64**
: The current end of WAL on the server.

**Int64**
: The server's system clock at the time of transmission, as
microseconds since midnight on 2000-01-01.

**Byte1**
: 1 means that the client should reply to this message as soon as
possible, to avoid a timeout disconnect. 0 otherwise.

The receiving process can send replies back to the sender at any time,
using one of the following message formats (also in the payload of a
CopyData message):

**Standby status update (F)**
: Byte1('r')

Identifies the message as a receiver status update.

**Int64**
: The location of the last WAL byte + 1 received and written to disk
in the standby.

**Int64**
: The location of the last WAL byte + 1 flushed to disk in
the standby.

**Int64**
: The location of the last WAL byte + 1 applied in the standby.

**Int64**
: The client's system clock at the time of transmission, as
microseconds since midnight on 2000-01-01.

**Byte1**
: If 1, the client requests the server to reply to this message
immediately. This can be used to ping the server, to test if
the connection is still healthy.

Hot standby feedback message (F)

**Byte1('h')**
: Identifies the message as a hot standby feedback message.

**Int64**
: The client's system clock at the time of transmission, as
microseconds since midnight on 2000-01-01.

**Int32**
: The standby's current global xmin, excluding the catalog_xmin from any
replication slots. If both this value and the following
catalog_xmin are 0 this is treated as a notification that hot standby
feedback will no longer be sent on this connection. Later non-zero
messages may reinitiate the feedback mechanism.

**Int32**
: The epoch of the global xmin xid on the standby.

**Int32**
: The lowest catalog_xmin of any replication slots on the standby. Set to 0
if no catalog_xmin exists on the standby or if hot standby feedback is being
disabled.

**Int32**
: The epoch of the catalog_xmin xid on the standby.

`START_REPLICATION` `SLOT` `slot_name` `LOGICAL` `XXX/XXX` [ ( `option_name` [ `option_value` ] [, ...] ) ]

Instructs server to start streaming WAL for logical replication,
starting at either WAL location `XXX/XXX` or the slot's
`confirmed_flush_lsn` (see [view-pg-replication-slots](#view-pg-replication-slots)), whichever is greater. This
behavior makes it easier for clients to avoid updating their local LSN
status when there is no data to process. However, starting at a
different LSN than requested might not catch certain kinds of client
errors; so the client may wish to check that
`confirmed_flush_lsn` matches its expectations before
issuing `START_REPLICATION`.

The server can reply with an error, for example if the
slot does not exist. On success, the server responds with a CopyBothResponse
message, and then starts to stream WAL to the frontend.

The messages inside the CopyBothResponse messages are of the same format
documented for `START_REPLICATION ... PHYSICAL`, including
two CommandComplete messages.

The output plugin associated with the selected slot is used
to process the output for streaming.

**`SLOT` `slot_name`**
: The name of the slot to stream changes from. This parameter is required,
and must correspond to an existing logical replication slot created
with `CREATE_REPLICATION_SLOT` in
`LOGICAL` mode.

**`XXX/XXX`**
: The WAL location to begin streaming at.

**`option_name`**
: The name of an option passed to the slot's logical decoding output
plugin.  See [protocol-logical-replication](#protocol-logical-replication) for
options that are accepted by the standard (`pgoutput`)
plugin.

**`option_value`**
: Optional value, in the form of a string constant, associated with the
specified option.

`DROP_REPLICATION_SLOT` `slot_name`  `WAIT`

Drops a replication slot, freeing any reserved server-side resources.

**`slot_name`**
: The name of the slot to drop.

**`WAIT`**
: This option causes the command to wait if the slot is active until
it becomes inactive, instead of the default behavior of raising an
error.

`BASE_BACKUP` [ ( `option` [, ...] ) ]

Instructs the server to start streaming a base backup.
The system will automatically be put in backup mode before the backup
is started, and taken out of it when the backup is complete. The
following options are accepted:

**`LABEL` `'label'`**
: Sets the label of the backup. If none is specified, a backup label
of `base backup` will be used. The quoting rules
for the label are the same as a standard SQL string with
[guc-standard-conforming-strings](#guc-standard-conforming-strings) turned on.

**`TARGET` `'target'`**
: Tells the server where to send the backup.  If the target is
`client`, which is the default, the backup data is
sent to the client. If it is `server`, the backup
data is written to the server at the pathname specified by the
`TARGET_DETAIL` option. If it is
`blackhole`, the backup data is not sent
anywhere; it is simply discarded.

The `server` target requires superuser privilege or
being granted the `pg_write_server_files` role.

**`TARGET_DETAIL` `'detail'`**
: Provides additional information about the backup target.

Currently, this option can only be used when the backup target is
`server`. It specifies the server directory
to which the backup should be written.

**`PROGRESS [ `boolean` ]`**
: If set to true, request information required to generate a progress
report. This will send back an approximate size in the header of each
tablespace, which can be used to calculate how far along the stream
is done. This is calculated by enumerating all the file sizes once
before the transfer is even started, and might as such have a
negative impact on the performance.  In particular, it might take
longer before the first data
is streamed. Since the database files can change during the backup,
the size is only approximate and might both grow and shrink between
the time of approximation and the sending of the actual files.
The default is false.

**`CHECKPOINT { 'fast' | 'spread' }`**
: Sets the type of checkpoint to be performed at the beginning of the
base backup. The default is `spread`.

**`WAL [ `boolean` ]`**
: If set to true, include the necessary WAL segments in the backup.
This will include all the files between start and stop backup in the
`pg_wal` directory of the base directory tar
file. The default is false.

**`WAIT [ `boolean` ]`**
: If set to true, the backup will wait until the last required WAL
segment has been archived, or emit a warning if WAL archiving is
not enabled. If false, the backup will neither wait nor warn,
leaving the client responsible for ensuring the required log is
available. The default is true.

**`COMPRESSION` `'method'`**
: Instructs the server to compress the backup using the specified
method. Currently, the supported methods are `gzip`,
`lz4`, and `zstd`.

**`COMPRESSION_DETAIL` `detail`**
: Specifies details for the chosen compression method. This should only
be used in conjunction with the `COMPRESSION`
option.  If the value is an integer, it specifies the compression
level.  Otherwise, it should be a comma-separated list of items,
each of the form `keyword` or
`keyword=value`. Currently, the supported
keywords are `level`, `long` and
`workers`.

The `level` keyword sets the compression level.
For `gzip` the compression level should be an
integer between `1` and `9`
(default `Z_DEFAULT_COMPRESSION` or
`-1`), for `lz4` an integer
between 1 and 12 (default `0` for fast compression
mode), and for `zstd` an integer between
`ZSTD_minCLevel()` (usually `-131072`)
and `ZSTD_maxCLevel()` (usually `22`),
(default `ZSTD_CLEVEL_DEFAULT` or
`3`).

The `long` keyword enables long-distance matching
mode, for improved compression ratio, at the expense of higher memory
use.  Long-distance mode is supported only for
`zstd`.

The `workers` keyword sets the number of threads
that should be used for parallel compression. Parallel compression
is supported only for `zstd`.

**`MAX_RATE` `rate`**
: Limit (throttle) the maximum amount of data transferred from server
to client per unit of time.  The expected unit is kilobytes per second.
If this option is specified, the value must either be equal to zero
or it must fall within the range from 32 kB through 1 GB (inclusive).
If zero is passed or the option is not specified, no restriction is
imposed on the transfer.

**`TABLESPACE_MAP [ `boolean` ]`**
: If true, include information about symbolic links present in the
directory `pg_tblspc` in a file named
`tablespace_map`. The tablespace map file includes
each symbolic link name as it exists in the directory
`pg_tblspc/` and the full path of that symbolic link.
The default is false.

**`VERIFY_CHECKSUMS [ `boolean` ]`**
: If true, checksums are verified during a base backup if they are
enabled. If false, this is skipped. The default is true.

**`MANIFEST` `manifest_option`**
: When this option is specified with a value of `yes`
or `force-encode`, a backup manifest is created
and sent along with the backup.  The manifest is a list of every
file present in the backup with the exception of any WAL files that
may be included. It also stores the size, last modification time, and
optionally a checksum for each file.
A value of `force-encode` forces all filenames
to be hex-encoded; otherwise, this type of encoding is performed only
for files whose names are non-UTF8 octet sequences.
`force-encode` is intended primarily for testing
purposes, to be sure that clients which read the backup manifest
can handle this case. For compatibility with previous releases,
the default is `MANIFEST 'no'`.

**`MANIFEST_CHECKSUMS` `checksum_algorithm`**
: Specifies the checksum algorithm that should be applied to each file included
in the backup manifest. Currently, the available
algorithms are `NONE`, `CRC32C`,
`SHA224`, `SHA256`,
`SHA384`, and `SHA512`.
The default is `CRC32C`.

When the backup is started, the server will first send two
ordinary result sets, followed by one or more CopyOutResponse
results.

The first ordinary result set contains the starting position of the
backup, in a single row with two columns. The first column contains
the start position given in XLogRecPtr format, and the second column
contains the corresponding timeline ID.

The second ordinary result set has one row for each tablespace.
The fields in this row are:

**`spcoid` (`oid`)**
: The OID of the tablespace, or null if it's the base
directory.

**`spclocation` (`text`)**
: The full path of the tablespace directory, or null
if it's the base directory.

**`size` (`int8`)**
: The approximate size of the tablespace, in kilobytes (1024 bytes),
if progress report has been requested; otherwise it's null.

After the second regular result set, a CopyOutResponse will be sent.
The payload of each CopyData message will contain a message in one of
the following formats:

**new archive (B)**
: Byte1('n')

Identifies the message as indicating the start of a new archive.
There will be one archive for the main data directory and one
for each additional tablespace; each will use tar format
(following the "ustar interchange format" specified
in the POSIX 1003.1-2008 standard).

**String**
: The file name for this archive.

**String**
: For the main data directory, an empty string. For other
tablespaces, the full path to the directory from which this
archive was created.

manifest (B)

**Byte1('m')**
: Identifies the message as indicating the start of the backup
manifest.

archive or manifest data (B)

**Byte1('d')**
: Identifies the message as containing archive or manifest data.

**Byte`n`**
: Data bytes.

progress report (B)

**Byte1('p')**
: Identifies the message as a progress report.

**Int64**
: The number of bytes from the current tablespace for which
processing has been completed.

After the CopyOutResponse, or all such responses, have been sent, a
final ordinary result set will be sent, containing the WAL end position
of the backup, in the same format as the start position.

The tar archive for the data directory and each tablespace will contain
all files in the directories, regardless of whether they are
PostgreSQL files or other files added to the same
directory. The only excluded files are:

- `postmaster.pid`
- `postmaster.opts`
- `pg_internal.init` (found in multiple directories)
- Various temporary files and directories created during the operation
of the PostgreSQL server, such as any file or directory beginning
with `pgsql_tmp` and temporary relations.
- Unlogged relations, except for the init fork which is required to
recreate the (empty) unlogged relation on recovery.
- `pg_wal`, including subdirectories. If the backup is run
with WAL files included, a synthesized version of `pg_wal` will be
included, but it will only contain the files necessary for the
backup to work, not the rest of the contents.
- `pg_dynshmem`, `pg_notify`,
`pg_replslot`, `pg_serial`,
`pg_snapshots`, `pg_stat_tmp`, and
`pg_subtrans` are copied as empty directories (even if
they are symbolic links).
- Files other than regular files and directories, such as symbolic
links (other than for the directories listed above) and special
device and operating system files, are skipped.  (Symbolic links
in `pg_tblspc` are maintained.)

Owner, group, and file mode are set if the underlying file system on
the server supports it.

## Logical Streaming Replication Protocol

This section describes the logical replication protocol, which is the message
flow started by the `START_REPLICATION`
`SLOT` `slot_name`
`LOGICAL` replication command.

The logical streaming replication protocol builds on the primitives of
the physical streaming replication protocol.

PostgreSQL logical decoding supports output
plugins.  `pgoutput` is the standard one used for
the built-in logical replication.

### Logical Streaming Replication Parameters

Using the `START_REPLICATION` command,
`pgoutput` accepts the following options:

**proto_version**
: Protocol version. Currently versions `1`, `2`,
`3`, and `4` are supported.  A valid
version is required.

Version `2` is supported only for server version 14
and above, and it allows streaming of large in-progress transactions.

Version `3` is supported only for server version 15
and above, and it allows streaming of two-phase commits.

Version `4` is supported only for server version 16
and above, and it allows streams of large in-progress transactions to
be applied in parallel.

**publication_names**
: Comma separated list of publication names for which to subscribe
(receive changes). The individual publication names are treated
as standard objects names and can be quoted the same as needed.
At least one publication name is required.

**binary**
: Boolean option to use binary transfer mode.  Binary mode is faster
than the text mode but slightly less robust.

**messages**
: Boolean option to enable sending the messages that are written
by `pg_logical_emit_message`.

**streaming**
: Option to enable streaming of in-progress transactions. Valid values are
`off` (the default), `on` and
`parallel`. The setting `parallel`
enables sending extra information with some messages to be used for
parallelization. Minimum protocol version 2 is required to turn it
`on`.  Minimum protocol version 4 is required for the
`parallel` value.

**two_phase**
: Boolean option to enable two-phase transactions.   Minimum protocol
version 3 is required to turn it on.

**origin**
: Option to send changes by their origin.  Possible values are "none"
to only send the changes that have no origin associated, or "any"
to send the changes regardless of their origin.  This can be used
to avoid loops (infinite replication of the same data) among
replication nodes.

### Logical Replication Protocol Messages

The individual protocol messages are discussed in the following
subsections. Individual messages are described in
[protocol-logicalrep-message-formats](#protocol-logicalrep-message-formats).

All top-level protocol messages begin with a message type byte.
While represented in code as a character, this is a signed byte with no
associated encoding.

Since the streaming replication protocol supplies a message length there
is no need for top-level protocol messages to embed a length in their
header.

### Logical Replication Protocol Message Flow

With the exception of the `START_REPLICATION` command and
the replay progress messages, all information flows only from the backend
to the frontend.

The logical replication protocol sends individual transactions one by one.
This means that all messages between a pair of Begin and Commit messages
belong to the same transaction. Similarly, all messages between a pair of
Begin Prepare and Prepare messages belong to the same transaction.
It also sends changes of large in-progress transactions between a pair of
Stream Start and Stream Stop messages. The last stream of such a transaction
contains a Stream Commit or Stream Abort message.

Every sent transaction contains zero or more DML messages (Insert,
Update, Delete). In case of a cascaded setup it can also contain Origin
messages. The origin message indicates that the transaction originated on
different replication node. Since a replication node in the scope of logical
replication protocol can be pretty much anything, the only identifier
is the origin name. It's downstream's responsibility to handle this as
needed (if needed). The Origin message is always sent before any DML
messages in the transaction.

Every DML message contains a relation OID, identifying the publisher's
relation that was acted on.  Before the first DML message for a given
relation OID, a Relation message will be sent, describing the schema of
that relation.  Subsequently, a new Relation message will be sent if
the relation's definition has changed since the last Relation message
was sent for it.  (The protocol assumes that the client is capable of
remembering this metadata for as many relations as needed.)

Relation messages identify column types by their OIDs.  In the case
of a built-in type, it is assumed that the client can look up that
type OID locally, so no additional data is needed.  For a non-built-in
type OID, a Type message will be sent before the Relation message,
to provide the type name associated with that OID.  Thus, a client that
needs to specifically identify the types of relation columns should
cache the contents of Type messages, and first consult that cache to
see if the type OID is defined there.  If not, look up the type OID
locally.

## Message Formats

This section describes the detailed format of each message.  Each is marked to
indicate that it can be sent by a frontend (F), a backend (B), or both
(F & B).
Notice that although each message includes a byte count at the beginning,
the message format is defined so that the message end can be found without
reference to the byte count.  This aids validity checking.  (The CopyData
message is an exception, because it forms part of a data stream; the contents
of any individual CopyData message cannot be interpretable on their own.)

**AuthenticationOk (B)**
: Byte1('R')

Identifies the message as an authentication request.

**Int32(8)**
: Length of message contents in bytes, including self.

**Int32(0)**
: Specifies that the authentication was successful.

AuthenticationKerberosV5 (B)

**Byte1('R')**
: Identifies the message as an authentication request.

**Int32(8)**
: Length of message contents in bytes, including self.

**Int32(2)**
: Specifies that Kerberos V5 authentication is required.

AuthenticationCleartextPassword (B)

**Byte1('R')**
: Identifies the message as an authentication request.

**Int32(8)**
: Length of message contents in bytes, including self.

**Int32(3)**
: Specifies that a clear-text password is required.

AuthenticationMD5Password (B)

**Byte1('R')**
: Identifies the message as an authentication request.

**Int32(12)**
: Length of message contents in bytes, including self.

**Int32(5)**
: Specifies that an MD5-encrypted password is required.

**Byte4**
: The salt to use when encrypting the password.

AuthenticationGSS (B)

**Byte1('R')**
: Identifies the message as an authentication request.

**Int32(8)**
: Length of message contents in bytes, including self.

**Int32(7)**
: Specifies that GSSAPI authentication is required.

AuthenticationGSSContinue (B)

**Byte1('R')**
: Identifies the message as an authentication request.

**Int32**
: Length of message contents in bytes, including self.

**Int32(8)**
: Specifies that this message contains GSSAPI or SSPI data.

**Byte`n`**
: GSSAPI or SSPI authentication data.

AuthenticationSSPI (B)

**Byte1('R')**
: Identifies the message as an authentication request.

**Int32(8)**
: Length of message contents in bytes, including self.

**Int32(9)**
: Specifies that SSPI authentication is required.

AuthenticationSASL (B)

**Byte1('R')**
: Identifies the message as an authentication request.

**Int32**
: Length of message contents in bytes, including self.

**Int32(10)**
: Specifies that SASL authentication is required.

The message body is a list of SASL authentication mechanisms, in the
server's order of preference. A zero byte is required as terminator after
the last authentication mechanism name. For each mechanism, there is the
following:

**String**
: Name of a SASL authentication mechanism.

AuthenticationSASLContinue (B)

**Byte1('R')**
: Identifies the message as an authentication request.

**Int32**
: Length of message contents in bytes, including self.

**Int32(11)**
: Specifies that this message contains a SASL challenge.

**Byte`n`**
: SASL data, specific to the SASL mechanism being used.

AuthenticationSASLFinal (B)

**Byte1('R')**
: Identifies the message as an authentication request.

**Int32**
: Length of message contents in bytes, including self.

**Int32(12)**
: Specifies that SASL authentication has completed.

**Byte`n`**
: SASL outcome "additional data", specific to the SASL mechanism
being used.

BackendKeyData (B)

**Byte1('K')**
: Identifies the message as cancellation key data.
The frontend must save these values if it wishes to be
able to issue CancelRequest messages later.

**Int32(12)**
: Length of message contents in bytes, including self.

**Int32**
: The process ID of this backend.

**Int32**
: The secret key of this backend.

Bind (F)

**Byte1('B')**
: Identifies the message as a Bind command.

**Int32**
: Length of message contents in bytes, including self.

**String**
: The name of the destination portal
(an empty string selects the unnamed portal).

**String**
: The name of the source prepared statement
(an empty string selects the unnamed prepared statement).

**Int16**
: The number of parameter format codes that follow
(denoted `C` below).
This can be zero to indicate that there are no parameters
or that the parameters all use the default format (text);
or one, in which case the specified format code is applied
to all parameters; or it can equal the actual number of
parameters.

**Int16[`C`]**
: The parameter format codes.  Each must presently be
zero (text) or one (binary).

**Int16**
: The number of parameter values that follow (possibly zero).
This must match the number of parameters needed by the query.

Next, the following pair of fields appear for each parameter:

**Int32**
: The length of the parameter value, in bytes (this count
does not include itself).  Can be zero.
As a special case, -1 indicates a NULL parameter value.
No value bytes follow in the NULL case.

**Byte`n`**
: The value of the parameter, in the format indicated by the
associated format code.
`n` is the above length.

After the last parameter, the following fields appear:

**Int16**
: The number of result-column format codes that follow
(denoted `R` below).
This can be zero to indicate that there are no result columns
or that the result columns should all use the default format
(text);
or one, in which case the specified format code is applied
to all result columns (if any); or it can equal the actual
number of result columns of the query.

**Int16[`R`]**
: The result-column format codes.  Each must presently be
zero (text) or one (binary).

BindComplete (B)

**Byte1('2')**
: Identifies the message as a Bind-complete indicator.

**Int32(4)**
: Length of message contents in bytes, including self.

CancelRequest (F)

**Int32(16)**
: Length of message contents in bytes, including self.

**Int32(80877102)**
: The cancel request code.  The value is chosen to contain
`1234` in the most significant 16 bits, and `5678` in the
least significant 16 bits.  (To avoid confusion, this code
must not be the same as any protocol version number.)

**Int32**
: The process ID of the target backend.

**Int32**
: The secret key for the target backend.

Close (F)

**Byte1('C')**
: Identifies the message as a Close command.

**Int32**
: Length of message contents in bytes, including self.

**Byte1**
: '`S`' to close a prepared statement; or
'`P`' to close a portal.

**String**
: The name of the prepared statement or portal to close
(an empty string selects the unnamed prepared statement
or portal).

CloseComplete (B)

**Byte1('3')**
: Identifies the message as a Close-complete indicator.

**Int32(4)**
: Length of message contents in bytes, including self.

CommandComplete (B)

**Byte1('C')**
: Identifies the message as a command-completed response.

**Int32**
: Length of message contents in bytes, including self.

**String**
: The command tag.  This is usually a single
word that identifies which SQL command was completed.

For an `INSERT` command, the tag is
`INSERT `oid`
`rows``, where
`rows` is the number of rows
inserted. `oid` used to be the object ID
of the inserted row if `rows` was 1
and the target table had OIDs, but OIDs system columns are
not supported anymore; therefore `oid`
is always 0.

For a `DELETE` command, the tag is
`DELETE `rows`` where
`rows` is the number of rows deleted.

For an `UPDATE` command, the tag is
`UPDATE `rows`` where
`rows` is the number of rows updated.

For a `MERGE` command, the tag is
`MERGE `rows`` where
`rows` is the number of rows inserted,
updated, or deleted.

For a `SELECT` or `CREATE TABLE AS`
command, the tag is `SELECT `rows``
where `rows` is the number of rows retrieved.

For a `MOVE` command, the tag is
`MOVE `rows`` where
`rows` is the number of rows the
cursor's position has been changed by.

For a `FETCH` command, the tag is
`FETCH `rows`` where
`rows` is the number of rows that
have been retrieved from the cursor.

For a `COPY` command, the tag is
`COPY `rows`` where
`rows` is the number of rows copied.
(Note: the row count appears only in
PostgreSQL 8.2 and later.)

CopyData (F & B)

**Byte1('d')**
: Identifies the message as `COPY` data.

**Int32**
: Length of message contents in bytes, including self.

**Byte`n`**
: Data that forms part of a `COPY` data stream.  Messages sent
from the backend will always correspond to single data rows,
but messages sent by frontends might divide the data stream
arbitrarily.

CopyDone (F & B)

**Byte1('c')**
: Identifies the message as a `COPY`-complete indicator.

**Int32(4)**
: Length of message contents in bytes, including self.

CopyFail (F)

**Byte1('f')**
: Identifies the message as a `COPY`-failure indicator.

**Int32**
: Length of message contents in bytes, including self.

**String**
: An error message to report as the cause of failure.

CopyInResponse (B)

**Byte1('G')**
: Identifies the message as a Start Copy In response.
The frontend must now send copy-in data (if not
prepared to do so, send a CopyFail message).

**Int32**
: Length of message contents in bytes, including self.

**Int8**
: 0 indicates the overall `COPY` format is textual (rows
separated by newlines, columns separated by separator
characters, etc.).
1 indicates the overall copy format is binary (similar
to DataRow format).
See [sql-copy](#sql-copy)
for more information.

**Int16**
: The number of columns in the data to be copied
(denoted `N` below).

**Int16[`N`]**
: The format codes to be used for each column.
Each must presently be zero (text) or one (binary).
All must be zero if the overall copy format is textual.

CopyOutResponse (B)

**Byte1('H')**
: Identifies the message as a Start Copy Out response.
This message will be followed by copy-out data.

**Int32**
: Length of message contents in bytes, including self.

**Int8**
: 0 indicates the overall `COPY` format
is textual (rows separated by newlines, columns
separated by separator characters, etc.). 1 indicates
the overall copy format is binary (similar to DataRow
format). See [sql-copy](#sql-copy) for more information.

**Int16**
: The number of columns in the data to be copied
(denoted `N` below).

**Int16[`N`]**
: The format codes to be used for each column.
Each must presently be zero (text) or one (binary).
All must be zero if the overall copy format is textual.

CopyBothResponse (B)

**Byte1('W')**
: Identifies the message as a Start Copy Both response.
This message is used only for Streaming Replication.

**Int32**
: Length of message contents in bytes, including self.

**Int8**
: 0 indicates the overall `COPY` format
is textual (rows separated by newlines, columns
separated by separator characters, etc.). 1 indicates
the overall copy format is binary (similar to DataRow
format). See [sql-copy](#sql-copy) for more information.

**Int16**
: The number of columns in the data to be copied
(denoted `N` below).

**Int16[`N`]**
: The format codes to be used for each column.
Each must presently be zero (text) or one (binary).
All must be zero if the overall copy format is textual.

DataRow (B)

**Byte1('D')**
: Identifies the message as a data row.

**Int32**
: Length of message contents in bytes, including self.

**Int16**
: The number of column values that follow (possibly zero).

Next, the following pair of fields appear for each column:

**Int32**
: The length of the column value, in bytes (this count
does not include itself).  Can be zero.
As a special case, -1 indicates a NULL column value.
No value bytes follow in the NULL case.

**Byte`n`**
: The value of the column, in the format indicated by the
associated format code.
`n` is the above length.

Describe (F)

**Byte1('D')**
: Identifies the message as a Describe command.

**Int32**
: Length of message contents in bytes, including self.

**Byte1**
: '`S`' to describe a prepared statement; or
'`P`' to describe a portal.

**String**
: The name of the prepared statement or portal to describe
(an empty string selects the unnamed prepared statement
or portal).

EmptyQueryResponse (B)

**Byte1('I')**
: Identifies the message as a response to an empty query string.
(This substitutes for CommandComplete.)

**Int32(4)**
: Length of message contents in bytes, including self.

ErrorResponse (B)

**Byte1('E')**
: Identifies the message as an error.

**Int32**
: Length of message contents in bytes, including self.

The message body consists of one or more identified fields,
followed by a zero byte as a terminator.  Fields can appear in
any order.  For each field there is the following:

**Byte1**
: A code identifying the field type; if zero, this is
the message terminator and no string follows.
The presently defined field types are listed in
[protocol-error-fields](#protocol-error-fields).
Since more field types might be added in future,
frontends should silently ignore fields of unrecognized
type.

**String**
: The field value.

Execute (F)

**Byte1('E')**
: Identifies the message as an Execute command.

**Int32**
: Length of message contents in bytes, including self.

**String**
: The name of the portal to execute
(an empty string selects the unnamed portal).

**Int32**
: Maximum number of rows to return, if portal contains
a query that returns rows (ignored otherwise).  Zero
denotes "no limit".

Flush (F)

**Byte1('H')**
: Identifies the message as a Flush command.

**Int32(4)**
: Length of message contents in bytes, including self.

FunctionCall (F)

**Byte1('F')**
: Identifies the message as a function call.

**Int32**
: Length of message contents in bytes, including self.

**Int32**
: Specifies the object ID of the function to call.

**Int16**
: The number of argument format codes that follow
(denoted `C` below).
This can be zero to indicate that there are no arguments
or that the arguments all use the default format (text);
or one, in which case the specified format code is applied
to all arguments; or it can equal the actual number of
arguments.

**Int16[`C`]**
: The argument format codes.  Each must presently be
zero (text) or one (binary).

**Int16**
: Specifies the number of arguments being supplied to the
function.

Next, the following pair of fields appear for each argument:

**Int32**
: The length of the argument value, in bytes (this count
does not include itself).  Can be zero.
As a special case, -1 indicates a NULL argument value.
No value bytes follow in the NULL case.

**Byte`n`**
: The value of the argument, in the format indicated by the
associated format code.
`n` is the above length.

After the last argument, the following field appears:

**Int16**
: The format code for the function result. Must presently be
zero (text) or one (binary).

FunctionCallResponse (B)

**Byte1('V')**
: Identifies the message as a function call result.

**Int32**
: Length of message contents in bytes, including self.

**Int32**
: The length of the function result value, in bytes (this count
does not include itself).  Can be zero.
As a special case, -1 indicates a NULL function result.
No value bytes follow in the NULL case.

**Byte`n`**
: The value of the function result, in the format indicated by
the associated format code.
`n` is the above length.

GSSENCRequest (F)

**Int32(8)**
: Length of message contents in bytes, including self.

**Int32(80877104)**
: The GSSAPI Encryption request code.  The value is chosen to contain
`1234` in the most significant 16 bits, and `5680` in the
least significant 16 bits.  (To avoid confusion, this code
must not be the same as any protocol version number.)

GSSResponse (F)

**Byte1('p')**
: Identifies the message as a GSSAPI or SSPI response. Note that
this is also used for SASL and password response messages.
The exact message type can be deduced from the context.

**Int32**
: Length of message contents in bytes, including self.

**Byte`n`**
: GSSAPI/SSPI specific message data.

NegotiateProtocolVersion (B)

**Byte1('v')**
: Identifies the message as a protocol version negotiation
message.

**Int32**
: Length of message contents in bytes, including self.

**Int32**
: Newest minor protocol version supported by the server
for the major protocol version requested by the client.

**Int32**
: Number of protocol options not recognized by the server.

Then, for protocol option not recognized by the server, there
is the following:

**String**
: The option name.

NoData (B)

**Byte1('n')**
: Identifies the message as a no-data indicator.

**Int32(4)**
: Length of message contents in bytes, including self.

NoticeResponse (B)

**Byte1('N')**
: Identifies the message as a notice.

**Int32**
: Length of message contents in bytes, including self.

The message body consists of one or more identified fields,
followed by a zero byte as a terminator.  Fields can appear in
any order.  For each field there is the following:

**Byte1**
: A code identifying the field type; if zero, this is
the message terminator and no string follows.
The presently defined field types are listed in
[protocol-error-fields](#protocol-error-fields).
Since more field types might be added in future,
frontends should silently ignore fields of unrecognized
type.

**String**
: The field value.

NotificationResponse (B)

**Byte1('A')**
: Identifies the message as a notification response.

**Int32**
: Length of message contents in bytes, including self.

**Int32**
: The process ID of the notifying backend process.

**String**
: The name of the channel that the notify has been raised on.

**String**
: The "payload" string passed from the notifying process.

ParameterDescription (B)

**Byte1('t')**
: Identifies the message as a parameter description.

**Int32**
: Length of message contents in bytes, including self.

**Int16**
: The number of parameters used by the statement
(can be zero).

Then, for each parameter, there is the following:

**Int32**
: Specifies the object ID of the parameter data type.

ParameterStatus (B)

**Byte1('S')**
: Identifies the message as a run-time parameter status report.

**Int32**
: Length of message contents in bytes, including self.

**String**
: The name of the run-time parameter being reported.

**String**
: The current value of the parameter.

Parse (F)

**Byte1('P')**
: Identifies the message as a Parse command.

**Int32**
: Length of message contents in bytes, including self.

**String**
: The name of the destination prepared statement
(an empty string selects the unnamed prepared statement).

**String**
: The query string to be parsed.

**Int16**
: The number of parameter data types specified
(can be zero).  Note that this is not an indication of
the number of parameters that might appear in the
query string, only the number that the frontend wants to
prespecify types for.

Then, for each parameter, there is the following:

**Int32**
: Specifies the object ID of the parameter data type.
Placing a zero here is equivalent to leaving the type
unspecified.

ParseComplete (B)

**Byte1('1')**
: Identifies the message as a Parse-complete indicator.

**Int32(4)**
: Length of message contents in bytes, including self.

PasswordMessage (F)

**Byte1('p')**
: Identifies the message as a password response. Note that
this is also used for GSSAPI, SSPI and SASL response messages.
The exact message type can be deduced from the context.

**Int32**
: Length of message contents in bytes, including self.

**String**
: The password (encrypted, if requested).

PortalSuspended (B)

**Byte1('s')**
: Identifies the message as a portal-suspended indicator.
Note this only appears if an Execute message's row-count limit
was reached.

**Int32(4)**
: Length of message contents in bytes, including self.

Query (F)

**Byte1('Q')**
: Identifies the message as a simple query.

**Int32**
: Length of message contents in bytes, including self.

**String**
: The query string itself.

ReadyForQuery (B)

**Byte1('Z')**
: Identifies the message type.  ReadyForQuery is sent
whenever the backend is ready for a new query cycle.

**Int32(5)**
: Length of message contents in bytes, including self.

**Byte1**
: Current backend transaction status indicator.
Possible values are '`I`' if idle (not in
a transaction block); '`T`' if in a transaction
block; or '`E`' if in a failed transaction
block (queries will be rejected until block is ended).

RowDescription (B)

**Byte1('T')**
: Identifies the message as a row description.

**Int32**
: Length of message contents in bytes, including self.

**Int16**
: Specifies the number of fields in a row (can be zero).

Then, for each field, there is the following:

**String**
: The field name.

**Int32**
: If the field can be identified as a column of a specific
table, the object ID of the table; otherwise zero.

**Int16**
: If the field can be identified as a column of a specific
table, the attribute number of the column; otherwise zero.

**Int32**
: The object ID of the field's data type.

**Int16**
: The data type size (see `pg_type.typlen`).
Note that negative values denote variable-width types.

**Int32**
: The type modifier (see `pg_attribute.atttypmod`).
The meaning of the modifier is type-specific.

**Int16**
: The format code being used for the field.  Currently will
be zero (text) or one (binary).  In a RowDescription
returned from the statement variant of Describe, the
format code is not yet known and will always be zero.

SASLInitialResponse (F)

**Byte1('p')**
: Identifies the message as an initial SASL response. Note that
this is also used for GSSAPI, SSPI and password response messages.
The exact message type is deduced from the context.

**Int32**
: Length of message contents in bytes, including self.

**String**
: Name of the SASL authentication mechanism that the client
selected.

**Int32**
: Length of SASL mechanism specific "Initial Client Response" that
follows, or -1 if there is no Initial Response.

**Byte`n`**
: SASL mechanism specific "Initial Response".

SASLResponse (F)

**Byte1('p')**
: Identifies the message as a SASL response. Note that
this is also used for GSSAPI, SSPI and password response messages.
The exact message type can be deduced from the context.

**Int32**
: Length of message contents in bytes, including self.

**Byte`n`**
: SASL mechanism specific message data.

SSLRequest (F)

**Int32(8)**
: Length of message contents in bytes, including self.

**Int32(80877103)**
: The SSL request code.  The value is chosen to contain
`1234` in the most significant 16 bits, and `5679` in the
least significant 16 bits.  (To avoid confusion, this code
must not be the same as any protocol version number.)

StartupMessage (F)

**Int32**
: Length of message contents in bytes, including self.

**Int32(196608)**
: The protocol version number.  The most significant 16 bits are
the major version number (3 for the protocol described here).
The least significant 16 bits are the minor version number
(0 for the protocol described here).

The protocol version number is followed by one or more pairs of
parameter name and value strings.  A zero byte is required as a
terminator after the last name/value pair.
Parameters can appear in any
order.  `user` is required, others are optional.
Each parameter is specified as:

**String**
: The parameter name.  Currently recognized names are:

`user`

The database user name to connect as.  Required;
there is no default.

**`database`**
: The database to connect to.  Defaults to the user name.

**`options`**
: Command-line arguments for the backend.  (This is
deprecated in favor of setting individual run-time
parameters.)  Spaces within this string are
considered to separate arguments, unless escaped with
a backslash (`\`); write `\\` to
represent a literal backslash.

**`replication`**
: Used to connect in streaming replication mode, where
a small set of replication commands can be issued
instead of SQL statements. Value can be
`true`, `false`, or
`database`, and the default is
`false`. See
[protocol-replication](#protocol-replication) for details.

In addition to the above, other parameters may be listed.
Parameter names beginning with `_pq_.` are
reserved for use as protocol extensions, while others are
treated as run-time parameters to be set at backend start
time.  Such settings will be applied during backend start
(after parsing the command-line arguments if any) and will
act as session defaults.

String

The parameter value.

Sync (F)

**Byte1('S')**
: Identifies the message as a Sync command.

**Int32(4)**
: Length of message contents in bytes, including self.

Terminate (F)

**Byte1('X')**
: Identifies the message as a termination.

**Int32(4)**
: Length of message contents in bytes, including self.

## Logical Replication Message Formats

This section describes the detailed format of each logical replication
message.  These messages are either returned by the replication slot SQL
interface or are sent by a walsender.  In the case of a walsender, they are
encapsulated inside replication protocol WAL messages as described in
[protocol-replication](#protocol-replication), and generally obey the same message
flow as physical replication.

**Begin**
: Byte1('B')

Identifies the message as a begin message.

**Int64 (XLogRecPtr)**
: The final LSN of the transaction.

**Int64 (TimestampTz)**
: Commit timestamp of the transaction. The value is in number
of microseconds since PostgreSQL epoch (2000-01-01).

**Int32 (TransactionId)**
: Xid of the transaction.

Message

**Byte1('M')**
: Identifies the message as a logical decoding message.

**Int32 (TransactionId)**
: Xid of the transaction (only present for streamed transactions).
This field is available since protocol version 2.

**Int8**
: Flags; Either 0 for no flags or 1 if the logical decoding
message is transactional.

**Int64 (XLogRecPtr)**
: The LSN of the logical decoding message.

**String**
: The prefix of the logical decoding message.

**Int32**
: Length of the content.

**Byte`n`**
: The content of the logical decoding message.

Commit

**Byte1('C')**
: Identifies the message as a commit message.

**Int8(0)**
: Flags; currently unused.

**Int64 (XLogRecPtr)**
: The LSN of the commit.

**Int64 (XLogRecPtr)**
: The end LSN of the transaction.

**Int64 (TimestampTz)**
: Commit timestamp of the transaction. The value is in number
of microseconds since PostgreSQL epoch (2000-01-01).

Origin

**Byte1('O')**
: Identifies the message as an origin message.

**Int64 (XLogRecPtr)**
: The LSN of the commit on the origin server.

**String**
: Name of the origin.

Note that there can be multiple Origin messages inside a single transaction.

Relation

**Byte1('R')**
: Identifies the message as a relation message.

**Int32 (TransactionId)**
: Xid of the transaction (only present for streamed transactions).
This field is available since protocol version 2.

**Int32 (Oid)**
: OID of the relation.

**String**
: Namespace (empty string for `pg_catalog`).

**String**
: Relation name.

**Int8**
: Replica identity setting for the relation (same as
`relreplident` in `pg_class`).

**Int16**
: Number of columns.

Next, the following message part appears for each column included in
the publication (except generated columns):

**Int8**
: Flags for the column. Currently can be either 0 for no flags
or 1 which marks the column as part of the key.

**String**
: Name of the column.

**Int32 (Oid)**
: OID of the column's data type.

**Int32**
: Type modifier of the column (`atttypmod`).

Type

**Byte1('Y')**
: Identifies the message as a type message.

**Int32 (TransactionId)**
: Xid of the transaction (only present for streamed transactions).
This field is available since protocol version 2.

**Int32 (Oid)**
: OID of the data type.

**String**
: Namespace (empty string for `pg_catalog`).

**String**
: Name of the data type.

Insert

**Byte1('I')**
: Identifies the message as an insert message.

**Int32 (TransactionId)**
: Xid of the transaction (only present for streamed transactions).
This field is available since protocol version 2.

**Int32 (Oid)**
: OID of the relation corresponding to the ID in the relation
message.

**Byte1('N')**
: Identifies the following TupleData message as a new tuple.

**TupleData**
: TupleData message part representing the contents of new tuple.

Update

**Byte1('U')**
: Identifies the message as an update message.

**Int32 (TransactionId)**
: Xid of the transaction (only present for streamed transactions).
This field is available since protocol version 2.

**Int32 (Oid)**
: OID of the relation corresponding to the ID in the relation
message.

**Byte1('K')**
: Identifies the following TupleData submessage as a key.
This field is optional and is only present if
the update changed data in any of the column(s) that are
part of the REPLICA IDENTITY index.

**Byte1('O')**
: Identifies the following TupleData submessage as an old tuple.
This field is optional and is only present if table in which
the update happened has REPLICA IDENTITY set to FULL.

**TupleData**
: TupleData message part representing the contents of the old tuple
or primary key. Only present if the previous 'O' or 'K' part
is present.

**Byte1('N')**
: Identifies the following TupleData message as a new tuple.

**TupleData**
: TupleData message part representing the contents of a new tuple.

The Update message may contain either a 'K' message part or an 'O' message part
or neither of them, but never both of them.

Delete

**Byte1('D')**
: Identifies the message as a delete message.

**Int32 (TransactionId)**
: Xid of the transaction (only present for streamed transactions).
This field is available since protocol version 2.

**Int32 (Oid)**
: OID of the relation corresponding to the ID in the relation
message.

**Byte1('K')**
: Identifies the following TupleData submessage as a key.
This field is present if the table in which the delete has
happened uses an index as REPLICA IDENTITY.

**Byte1('O')**
: Identifies the following TupleData message as an old tuple.
This field is present if the table in which the delete
happened has REPLICA IDENTITY set to FULL.

**TupleData**
: TupleData message part representing the contents of the old tuple
or primary key, depending on the previous field.

The Delete message may contain either a 'K' message part or an 'O' message part,
but never both of them.

Truncate

**Byte1('T')**
: Identifies the message as a truncate message.

**Int32 (TransactionId)**
: Xid of the transaction (only present for streamed transactions).
This field is available since protocol version 2.

**Int32**
: Number of relations

**Int8**
: Option bits for `TRUNCATE`:
1 for `CASCADE`, 2 for `RESTART IDENTITY`

**Int32 (Oid)**
: OID of the relation corresponding to the ID in the relation
message.  This field is repeated for each relation.

The following messages (Stream Start, Stream Stop, Stream Commit, and
Stream Abort) are available since protocol version 2.

**Stream Start**
: Byte1('S')

Identifies the message as a stream start message.

**Int32 (TransactionId)**
: Xid of the transaction.

**Int8**
: A value of 1 indicates this is the first stream segment for
this XID, 0 for any other stream segment.

Stream Stop

**Byte1('E')**
: Identifies the message as a stream stop message.

Stream Commit

**Byte1('c')**
: Identifies the message as a stream commit message.

**Int32 (TransactionId)**
: Xid of the transaction.

**Int8(0)**
: Flags; currently unused.

**Int64 (XLogRecPtr)**
: The LSN of the commit.

**Int64 (XLogRecPtr)**
: The end LSN of the transaction.

**Int64 (TimestampTz)**
: Commit timestamp of the transaction. The value is in number
of microseconds since PostgreSQL epoch (2000-01-01).

Stream Abort

**Byte1('A')**
: Identifies the message as a stream abort message.

**Int32 (TransactionId)**
: Xid of the transaction.

**Int32 (TransactionId)**
: Xid of the subtransaction (will be same as xid of the transaction for top-level
transactions).

**Int64 (XLogRecPtr)**
: The LSN of the abort operation, present only when streaming is set to parallel.
This field is available since protocol version 4.

**Int64 (TimestampTz)**
: Abort timestamp of the transaction, present only when streaming is set to
parallel. The value is in number of microseconds since PostgreSQL epoch (2000-01-01).
This field is available since protocol version 4.

The following messages (Begin Prepare, Prepare, Commit Prepared, Rollback Prepared, Stream Prepare)
are available since protocol version 3.

**Begin Prepare**
: Byte1('b')

Identifies the message as the beginning of a prepared transaction message.

**Int64 (XLogRecPtr)**
: The LSN of the prepare.

**Int64 (XLogRecPtr)**
: The end LSN of the prepared transaction.

**Int64 (TimestampTz)**
: Prepare timestamp of the transaction. The value is in number
of microseconds since PostgreSQL epoch (2000-01-01).

**Int32 (TransactionId)**
: Xid of the transaction.

**String**
: The user defined GID of the prepared transaction.

Prepare

**Byte1('P')**
: Identifies the message as a prepared transaction message.

**Int8(0)**
: Flags; currently unused.

**Int64 (XLogRecPtr)**
: The LSN of the prepare.

**Int64 (XLogRecPtr)**
: The end LSN of the prepared transaction.

**Int64 (TimestampTz)**
: Prepare timestamp of the transaction. The value is in number
of microseconds since PostgreSQL epoch (2000-01-01).

**Int32 (TransactionId)**
: Xid of the transaction.

**String**
: The user defined GID of the prepared transaction.

Commit Prepared

**Byte1('K')**
: Identifies the message as the commit of a prepared transaction message.

**Int8(0)**
: Flags; currently unused.

**Int64 (XLogRecPtr)**
: The LSN of the commit of the prepared transaction.

**Int64 (XLogRecPtr)**
: The end LSN of the commit of the prepared transaction.

**Int64 (TimestampTz)**
: Commit timestamp of the transaction. The value is in number
of microseconds since PostgreSQL epoch (2000-01-01).

**Int32 (TransactionId)**
: Xid of the transaction.

**String**
: The user defined GID of the prepared transaction.

Rollback Prepared

**Byte1('r')**
: Identifies the message as the rollback of a prepared transaction message.

**Int8(0)**
: Flags; currently unused.

**Int64 (XLogRecPtr)**
: The end LSN of the prepared transaction.

**Int64 (XLogRecPtr)**
: The end LSN of the rollback of the prepared transaction.

**Int64 (TimestampTz)**
: Prepare timestamp of the transaction. The value is in number
of microseconds since PostgreSQL epoch (2000-01-01).

**Int64 (TimestampTz)**
: Rollback timestamp of the transaction. The value is in number
of microseconds since PostgreSQL epoch (2000-01-01).

**Int32 (TransactionId)**
: Xid of the transaction.

**String**
: The user defined GID of the prepared transaction.

Stream Prepare

**Byte1('p')**
: Identifies the message as a stream prepared transaction message.

**Int8(0)**
: Flags; currently unused.

**Int64 (XLogRecPtr)**
: The LSN of the prepare.

**Int64 (XLogRecPtr)**
: The end LSN of the prepared transaction.

**Int64 (TimestampTz)**
: Prepare timestamp of the transaction. The value is in number
of microseconds since PostgreSQL epoch (2000-01-01).

**Int32 (TransactionId)**
: Xid of the transaction.

**String**
: The user defined GID of the prepared transaction.

The following message parts are shared by the above messages.

**TupleData**
: Int16

Number of columns.

Next, one of the following submessages appears for each column (except generated columns):

**Byte1('n')**
: Identifies the data as NULL value.

Or

**Byte1('u')**
: Identifies unchanged TOASTed value (the actual value is not
sent).

Or

**Byte1('t')**
: Identifies the data as text formatted value.

Or

**Byte1('b')**
: Identifies the data as binary formatted value.

**Int32**
: Length of the column value.

**Byte`n`**
: The value of the column, either in binary or in text format.
(As specified in the preceding format byte).
`n` is the above length.
