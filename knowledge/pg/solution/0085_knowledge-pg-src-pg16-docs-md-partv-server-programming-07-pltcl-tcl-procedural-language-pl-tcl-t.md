# Error Handling; Explicit Subtransactions

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partV_server_programming/07_pltcl_-_tcl_procedural_language.md`
- Source Title: `PL/Tcl — Tcl Procedural Language`
- Source Heading Path: `PL/Tcl - Tcl Procedural Language > Error Handling; Explicit Subtransactions`
- Source Line Ranges: `215-265, 277-347`
- Chunk ID: `pg16_solution_0085_44e104b32c`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4a4d9d64bdc6371d9567ed411df8e4e724c243c07b2decc02bf9a905669cfd07`

## Retrieval Guidance

- Use When: Handle a known failing statement inside PL/Tcl without aborting all surrounding procedural work.
- Retrieval Keywords: PL/Tcl error handling, catch, subtransaction, spi_exec, rollback partial work
- Follow-up Guidance: Use diagnostics from the caught error before deciding whether retry, fallback, or abort is appropriate.
- Classification Note: These sections describe how PL/Tcl code traps errors and uses subtransactions to contain a confirmed failing database operation.

## Official Source Content

## Error Handling in PL/Tcl

Tcl code within or called from a PL/Tcl function can raise an error,
either by executing some invalid operation or by generating an error
using the Tcl `error` command or
PL/Tcl's `elog` command.  Such errors can be caught
within Tcl using the Tcl `catch` command.  If an
error is not caught but is allowed to propagate out to the top level of
execution of the PL/Tcl function, it is reported as an SQL error in the
function's calling query.

Conversely, SQL errors that occur within PL/Tcl's
`spi_exec`, `spi_prepare`,
and `spi_execp` commands are reported as Tcl errors,
so they are catchable by Tcl's `catch` command.
(Each of these PL/Tcl commands runs its SQL operation in a
subtransaction, which is rolled back on error, so that any
partially-completed operation is automatically cleaned up.)
Again, if an error propagates out to the top level without being caught,
it turns back into an SQL error.

Tcl provides an `errorCode` variable that can represent
additional information about an error in a form that is easy for Tcl
programs to interpret.  The contents are in Tcl list format, and the
first word identifies the subsystem or library reporting the error;
beyond that the contents are left to the individual subsystem or
library.  For database errors reported by PL/Tcl commands, the first
word is `POSTGRES`, the second word is the PostgreSQL
version number, and additional words are field name/value pairs
providing detailed information about the error.
Fields `SQLSTATE`, `condition`,
and `message` are always supplied
(the first two represent the error code and condition name as shown
in [errcodes-appendix](#errcodes-appendix)).
Fields that may be present include
`detail`, `hint`, `context`,
`schema`, `table`, `column`,
`datatype`, `constraint`,
`statement`, `cursor_position`,
`filename`, `lineno`, and
`funcname`.

A convenient way to work with PL/Tcl's `errorCode`
information is to load it into an array, so that the field names become
array subscripts.  Code for doing that might look like

```
if {[catch { spi_exec $sql_command }]} {
if {[lindex $::errorCode 0] == "POSTGRES"} {
array set errorArray $::errorCode
if {$errorArray(condition) == "undefined_table"} {

## Explicit Subtransactions in PL/Tcl

Recovering from errors caused by database access as described in
[pltcl-error-handling](#pltcl-error-handling) can lead to an undesirable
situation where some operations succeed before one of them fails,
and after recovering from that error the data is left in an
inconsistent state.  PL/Tcl offers a solution to this problem in
the form of explicit subtransactions.

Consider a function that implements a transfer between two accounts:

```
CREATE FUNCTION transfer_funds() RETURNS void AS $$
if [catch {
spi_exec "UPDATE accounts SET balance = balance - 100 WHERE account_name = 'joe'"
spi_exec "UPDATE accounts SET balance = balance + 100 WHERE account_name = 'mary'"
} errormsg] {
set result [format "error transferring funds: %s" $errormsg]
} else {
set result "funds transferred successfully"
}
spi_exec "INSERT INTO operations (result) VALUES ('[quote $result]')"
$$ LANGUAGE pltcl;
```

If the second `UPDATE` statement results in an
exception being raised, this function will log the failure, but
the result of the first `UPDATE` will
nevertheless be committed.  In other words, the funds will be
withdrawn from Joe's account, but will not be transferred to
Mary's account.  This happens because each `spi_exec`
is a separate subtransaction, and only one of those subtransactions
got rolled back.

To handle such cases, you can wrap multiple database operations in an
explicit subtransaction, which will succeed or roll back as a whole.
PL/Tcl provides a `subtransaction` command to manage
this.  We can rewrite our function as:

```
CREATE FUNCTION transfer_funds2() RETURNS void AS $$
if [catch {
subtransaction {
spi_exec "UPDATE accounts SET balance = balance - 100 WHERE account_name = 'joe'"
spi_exec "UPDATE accounts SET balance = balance + 100 WHERE account_name = 'mary'"
}
} errormsg] {
set result [format "error transferring funds: %s" $errormsg]
} else {
set result "funds transferred successfully"
}
spi_exec "INSERT INTO operations (result) VALUES ('[quote $result]')"
$$ LANGUAGE pltcl;
```

Note that use of `catch` is still required for this
purpose.  Otherwise the error would propagate to the top level of the
function, preventing the desired insertion into
the `operations` table.
The `subtransaction` command does not trap errors, it
only assures that all database operations executed inside its scope will
be rolled back together when an error is reported.

A rollback of an explicit subtransaction occurs on any error reported
by the contained Tcl code, not only errors originating from database
access.  Thus a regular Tcl exception raised inside
a `subtransaction` command will also cause the
subtransaction to be rolled back.  However, non-error exits out of the
contained Tcl code (for instance, due to `return`) do
not cause a rollback.
