# Functions and Arguments; Data Values; Built-in Functions; Global Values; Database Access; Triggers; Event Triggers

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partV_server_programming/08_plperl_-_perl_procedural_language.md`
- Source Title: `PL/Perl — Perl Procedural Language`
- Source Heading Path: `PL/Perl - Perl Procedural Language > Functions and Arguments; Data Values; Built-in Functions; Global Values; Database Access; Triggers; Event Triggers`
- Source Line Ranges: `29-39, 351-364, 365-686, 687-752, 845-928, 929-957`
- Chunk ID: `pg16_fact_0088_e92dda8dc3`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `df441e1b9c6576ffcec786b26d3ae354f9ceb97615d09790e1d02fdaa17d14e6`

## Retrieval Guidance

- Use When: Write or interpret PL/Perl database functions and triggers.
- Retrieval Keywords: PL/Perl, plperl, spi_exec_query, spi_prepare, trigger function, quote_literal, return_next
- Follow-up Guidance: Use configuration and error-handling records for interpreter initialization or failure handling.
- Classification Note: These sections document PL/Perl syntax, data mapping, built-in helpers, SPI access, and trigger/event-trigger behavior.

## Official Source Content

## PL/Perl Functions and Arguments

To create a function in the PL/Perl language, use the standard
[sql-createfunction](#sql-createfunction)
syntax:

```
CREATE FUNCTION `funcname` (`argument-types`)
RETURNS `return-type`
-- function attributes can go here
AS $$

## Data Values in PL/Perl

The argument values supplied to a PL/Perl function's code are
simply the input arguments converted to text form (just as if they
had been displayed by a `SELECT` statement).
Conversely, the `return` and `return_next`
commands will accept any string that is acceptable input format
for the function's declared return type.

If this behavior is inconvenient for a particular case, it can be
improved by using a transform, as already illustrated
for `bool` values.  Several examples of transform modules
are included in the PostgreSQL distribution.

## Built-in Functions

### Database Access from PL/Perl

Access to the database itself from your Perl function can be done
via the following functions:

**``spi_exec_query`(`query` [, `limit`])`**
: `spi_exec_query` executes an SQL command and
returns the entire row set as a reference to an array of hash references.
If `limit` is specified and is greater than zero,
then `spi_exec_query` retrieves at
most `limit` rows, much as if the query included
a `LIMIT` clause.  Omitting `limit`
or specifying it as zero results in no row limit.

*You should only use this command when you know
that the result set will be relatively small.*  Here is an
example of a query (`SELECT` command) with the
optional maximum number of rows:

```
$rv = spi_exec_query('SELECT * FROM my_table', 5);
```

This returns up to 5 rows from the table
`my_table`.  If `my_table`
has a column `my_column`, you can get that
value from row `$i` of the result like this:

```
$foo = $rv->{rows}[$i]->{my_column};
```

The total number of rows returned from a `SELECT`
query can be accessed like this:

```
$nrows = $rv->{processed}
```

Here is an example using a different command type:

```
$query = "INSERT INTO my_table VALUES (1, 'test')";
$rv = spi_exec_query($query);
```

You can then access the command status (e.g.,
`SPI_OK_INSERT`) like this:

```
$res = $rv->{status};
```

To get the number of rows affected, do:

```
$nrows = $rv->{processed};
```

Here is a complete example:

```
CREATE TABLE test (
i int,
v varchar
);

INSERT INTO test (i, v) VALUES (1, 'first line');
INSERT INTO test (i, v) VALUES (2, 'second line');
INSERT INTO test (i, v) VALUES (3, 'third line');
INSERT INTO test (i, v) VALUES (4, 'immortal');

CREATE OR REPLACE FUNCTION test_munge() RETURNS SETOF test AS $$
my $rv = spi_exec_query('select i, v from test;');
my $status = $rv->{status};
my $nrows = $rv->{processed};
foreach my $rn (0 .. $nrows - 1) {
my $row = $rv->{rows}[$rn];
$row->{i} += 200 if defined($row->{i});
$row->{v} =~ tr/A-Za-z/a-zA-Z/ if (defined($row->{v}));
return_next($row);
}
return undef;
$$ LANGUAGE plperl;

SELECT * FROM test_munge();
```

**``spi_query(`command`)``**
: `spi_query` and `spi_fetchrow`
work together as a pair for row sets which might be large, or for cases
where you wish to return rows as they arrive.
`spi_fetchrow` works *only* with
`spi_query`. The following example illustrates how
you use them together:

```
CREATE TYPE foo_type AS (the_num INTEGER, the_text TEXT);

CREATE OR REPLACE FUNCTION lotsa_md5 (INTEGER) RETURNS SETOF foo_type AS $$
use Digest::MD5 qw(md5_hex);
my $file = '/usr/share/dict/words';
my $t = localtime;
elog(NOTICE, "opening file $file at $t" );
open my $fh, ';
close $fh;
$t = localtime;
elog(NOTICE, "closed file $file at $t");
chomp(@words);
my $row;
my $sth = spi_query("SELECT * FROM generate_series(1,$_[0]) AS b(a)");
while (defined ($row = spi_fetchrow($sth))) {
return_next({
the_num => $row->{a},
the_text => md5_hex($words[rand @words])
});
}
return;
$$ LANGUAGE plperlu;

SELECT * from lotsa_md5(500);
```

Normally, `spi_fetchrow` should be repeated until it
returns `undef`, indicating that there are no more
rows to read.  The cursor returned by `spi_query`
is automatically freed when
`spi_fetchrow` returns `undef`.
If you do not wish to read all the rows, instead call
`spi_cursor_close` to free the cursor.
Failure to do so will result in memory leaks.

**``spi_prepare(`command`, `argument types`)``**
: `spi_prepare`, `spi_query_prepared`, `spi_exec_prepared`,
and `spi_freeplan` implement the same functionality but for prepared queries.
`spi_prepare` accepts a query string with numbered argument placeholders ($1, $2, etc.)
and a string list of argument types:

```
$plan = spi_prepare('SELECT * FROM test WHERE id > $1 AND name = $2',
'INTEGER', 'TEXT');
```

Once a query plan is prepared by a call to `spi_prepare`, the plan can be used instead
of the string query, either in `spi_exec_prepared`, where the result is the same as returned
by `spi_exec_query`, or in `spi_query_prepared` which returns a cursor
exactly as `spi_query` does, which can be later passed to `spi_fetchrow`.
The optional second parameter to `spi_exec_prepared` is a hash reference of attributes;
the only attribute currently supported is `limit`, which
sets the maximum number of rows returned from the query.
Omitting `limit` or specifying it as zero results in no
row limit.

The advantage of prepared queries is that is it possible to use one prepared plan for more
than one query execution. After the plan is not needed anymore, it can be freed with
`spi_freeplan`:

```
CREATE OR REPLACE FUNCTION init() RETURNS VOID AS $$
$_SHARED{my_plan} = spi_prepare('SELECT (now() + $1)::date AS now',
'INTERVAL');
$$ LANGUAGE plperl;

CREATE OR REPLACE FUNCTION add_time( INTERVAL ) RETURNS TEXT AS $$
return spi_exec_prepared(
$_SHARED{my_plan},
$_[0]
)->{rows}->[0]->{now};
$$ LANGUAGE plperl;

CREATE OR REPLACE FUNCTION done() RETURNS VOID AS $$
spi_freeplan( $_SHARED{my_plan});
undef $_SHARED{my_plan};
$$ LANGUAGE plperl;

SELECT init();
SELECT add_time('1 day'), add_time('2 days'), add_time('3 days');
SELECT done();

add_time  |  add_time  |  add_time
------------+------------+------------
2005-12-10 | 2005-12-11 | 2005-12-12
```

Note that the parameter subscript in `spi_prepare` is defined via
$1, $2, $3, etc., so avoid declaring query strings in double quotes that might easily
lead to hard-to-catch bugs.

Another example illustrates usage of an optional parameter in `spi_exec_prepared`:

```
CREATE TABLE hosts AS SELECT id, ('192.168.1.'||id)::inet AS address
FROM generate_series(1,3) AS id;

CREATE OR REPLACE FUNCTION init_hosts_query() RETURNS VOID AS $$
$_SHARED{plan} = spi_prepare('SELECT * FROM hosts
WHERE address  2},
$_[0]
)->{rows};
$$ LANGUAGE plperl;

CREATE OR REPLACE FUNCTION release_hosts_query() RETURNS VOID AS $$
spi_freeplan($_SHARED{plan});
undef $_SHARED{plan};
$$ LANGUAGE plperl;

SELECT init_hosts_query();
SELECT query_hosts('192.168.1.0/30');
SELECT release_hosts_query();

query_hosts
-----------------
(1,192.168.1.1)
(2,192.168.1.2)
(2 rows)
```

**``spi_commit()``**
: Commit or roll back the current transaction.  This can only be called
in a procedure or anonymous code block (`DO` command)
called from the top level.  (Note that it is not possible to run the
SQL commands `COMMIT` or `ROLLBACK`
via `spi_exec_query` or similar.  It has to be done
using these functions.)  After a transaction is ended, a new
transaction is automatically started, so there is no separate function
for that.

Here is an example:

```
CREATE PROCEDURE transaction_test1()
LANGUAGE plperl
AS $$
foreach my $i (0..9) {
spi_exec_query("INSERT INTO test1 (a) VALUES ($i)");
if ($i % 2 == 0) {
spi_commit();
} else {
spi_rollback();
}
}
$$;

CALL transaction_test1();
```

### Utility Functions in PL/Perl

**``elog(`level`, `msg`)``**
: Emit a log or error message. Possible levels are
`DEBUG`, `LOG`, `INFO`,
`NOTICE`, `WARNING`, and `ERROR`.
`ERROR`
raises an error condition; if this is not trapped by the surrounding
Perl code, the error propagates out to the calling query, causing
the current transaction or subtransaction to be aborted.  This
is effectively the same as the Perl `die` command.
The other levels only generate messages of different
priority levels.
Whether messages of a particular priority are reported to the client,
written to the server log, or both is controlled by the
[guc-log-min-messages](#guc-log-min-messages) and
[guc-client-min-messages](#guc-client-min-messages) configuration
variables. See [runtime-config](#runtime-config) for more
information.

**``quote_literal(`string`)``**
: Return the given string suitably quoted to be used as a string literal in an SQL
statement string. Embedded single-quotes and backslashes are properly doubled.
Note that `quote_literal` returns undef on undef input; if the argument
might be undef, `quote_nullable` is often more suitable.

**``quote_nullable(`string`)``**
: Return the given string suitably quoted to be used as a string literal in an SQL
statement string; or, if the argument is undef, return the unquoted string "NULL".
Embedded single-quotes and backslashes are properly doubled.

**``quote_ident(`string`)``**
: Return the given string suitably quoted to be used as an identifier in
an SQL statement string. Quotes are added only if necessary (i.e., if
the string contains non-identifier characters or would be case-folded).
Embedded quotes are properly doubled.

**``decode_bytea(`string`)``**
: Return the unescaped binary data represented by the contents of the given string,
which should be `bytea` encoded.

**``encode_bytea(`string`)``**
: Return the `bytea` encoded form of the binary data contents of the given string.

**``encode_array_literal(`array`)``**
: Returns the contents of the referenced array as a string in array literal format
(see [arrays-input](#arrays-input)).
Returns the argument value unaltered if it's not a reference to an array.
The delimiter used between elements of the array literal defaults to "`, `"
if a delimiter is not specified or is undef.

**``encode_typed_literal(`value`, `typename`)``**
: Converts a Perl variable to the value of the data type passed as a
second argument and returns a string representation of this value.
Correctly handles nested arrays and values of composite types.

**``encode_array_constructor(`array`)``**
: Returns the contents of the referenced array as a string in array constructor format
(see [sql-syntax-array-constructors](#sql-syntax-array-constructors)).
Individual values are quoted using `quote_nullable`.
Returns the argument value, quoted using `quote_nullable`,
if it's not a reference to an array.

**``looks_like_number(`string`)``**
: Returns a true value if the content of the given string looks like a
number, according to Perl, returns false otherwise.
Returns undef if the argument is undef.  Leading and trailing space is
ignored. `Inf` and `Infinity` are regarded as numbers.

**``is_array_ref(`argument`)``**
: Returns a true value if the given argument may be treated as an
array reference, that is, if ref of the argument is `ARRAY` or
`PostgreSQL::InServer::ARRAY`.  Returns false otherwise.

## Global Values in PL/Perl

You can use the global hash `%_SHARED` to store
data, including code references, between function calls for the
lifetime of the current session.

Here is a simple example for shared data:

```
CREATE OR REPLACE FUNCTION set_var(name text, val text) RETURNS text AS $$
if ($_SHARED{$_[0]} = $_[1]) {
return 'ok';
} else {
return "cannot set shared variable $_[0] to $_[1]";
}
$$ LANGUAGE plperl;

CREATE OR REPLACE FUNCTION get_var(name text) RETURNS text AS $$
return $_SHARED{$_[0]};
$$ LANGUAGE plperl;

SELECT set_var('sample', 'Hello, PL/Perl!  How''s tricks?');
SELECT get_var('sample');
```

Here is a slightly more complicated example using a code reference:

```
CREATE OR REPLACE FUNCTION myfuncs() RETURNS void AS $$
$_SHARED{myquote} = sub {
my $arg = shift;
$arg =~ s/(['\\])/\\$1/g;
return "'$arg'";
};
$$ LANGUAGE plperl;

SELECT myfuncs(); /* initializes the function */

/* Set up a function that uses the quote function */

CREATE OR REPLACE FUNCTION use_quote(TEXT) RETURNS text AS $$
my $text_to_quote = shift;
my $qfunc = $_SHARED{myquote};
return &$qfunc($text_to_quote);
$$ LANGUAGE plperl;
```

(You could have replaced the above with the one-liner
`return $_SHARED{myquote}->($_[0]);`
at the expense of readability.)

For security reasons, PL/Perl executes functions called by any one SQL role
in a separate Perl interpreter for that role.  This prevents accidental or
malicious interference by one user with the behavior of another user's
PL/Perl functions.  Each such interpreter has its own value of the
`%_SHARED` variable and other global state.  Thus, two
PL/Perl functions will share the same value of `%_SHARED`
if and only if they are executed by the same SQL role.  In an application
wherein a single session executes code under multiple SQL roles (via
`SECURITY DEFINER` functions, use of `SET ROLE`, etc.)
you may need to take explicit steps to ensure that PL/Perl functions can
share data via `%_SHARED`.  To do that, make sure that
functions that should communicate are owned by the same user, and mark
them `SECURITY DEFINER`.  You must of course take care that
such functions can't be used to do anything unintended.

## PL/Perl Triggers

PL/Perl can be used to write trigger functions.  In a trigger function,
the hash reference `$_TD` contains information about the
current trigger event. `$_TD` is a global variable,
which gets a separate local value for each invocation of the trigger.
The fields of the `$_TD` hash reference are:

**`$_TD->{new}{foo}`**
: `NEW` value of column `foo`

**`$_TD->{old}{foo}`**
: `OLD` value of column `foo`

**`$_TD->{name}`**
: Name of the trigger being called

**`$_TD->{event}`**
: Trigger event: `INSERT`, `UPDATE`,
`DELETE`, `TRUNCATE`, or `UNKNOWN`

**`$_TD->{when}`**
: When the trigger was called: `BEFORE`,
`AFTER`, `INSTEAD OF`, or
`UNKNOWN`

**`$_TD->{level}`**
: The trigger level: `ROW`, `STATEMENT`, or `UNKNOWN`

**`$_TD->{relid}`**
: OID of the table on which the trigger fired

**`$_TD->{table_name}`**
: Name of the table on which the trigger fired

**`$_TD->{relname}`**
: Name of the table on which the trigger fired. This has been deprecated,
and could be removed in a future release.
Please use $_TD->{table_name} instead.

**`$_TD->{table_schema}`**
: Name of the schema in which the table on which the trigger fired, is

**`$_TD->{argc}`**
: Number of arguments of the trigger function

**`@{$_TD->{args}}`**
: Arguments of the trigger function.  Does not exist if `$_TD->{argc}` is 0.

Row-level triggers can return one of the following:

**`return;`**
: Execute the operation

**`"SKIP"`**
: Don't execute the operation

**`"MODIFY"`**
: Indicates that the `NEW` row was modified by
the trigger function

Here is an example of a trigger function, illustrating some of the
above:

```
CREATE TABLE test (
i int,
v varchar
);

CREATE OR REPLACE FUNCTION valid_id() RETURNS trigger AS $$
if (($_TD->{new}{i} >= 100) || ($_TD->{new}{i} {new}{v} ne "immortal") {
$_TD->{new}{v} .= "(modified by trigger)";
return "MODIFY";  # modify row and execute INSERT/UPDATE command
} else {
return;           # execute INSERT/UPDATE command
}
$$ LANGUAGE plperl;

CREATE TRIGGER test_valid_id_trig
BEFORE INSERT OR UPDATE ON test
FOR EACH ROW EXECUTE FUNCTION valid_id();
```

## PL/Perl Event Triggers

PL/Perl can be used to write event trigger functions.  In an event trigger
function, the hash reference `$_TD` contains information
about the current trigger event.  `$_TD` is a global variable,
which gets a separate local value for each invocation of the trigger.  The
fields of the `$_TD` hash reference are:

**`$_TD->{event}`**
: The name of the event the trigger is fired for.

**`$_TD->{tag}`**
: The command tag for which the trigger is fired.

The return value of the trigger function is ignored.

Here is an example of an event trigger function, illustrating some of the
above:

```
CREATE OR REPLACE FUNCTION perlsnitch() RETURNS event_trigger AS $$
elog(NOTICE, "perlsnitch: " . $_TD->{event} . " " . $_TD->{tag} . " ");
$$ LANGUAGE plperl;

CREATE EVENT TRIGGER perl_a_snitch
ON ddl_command_start
EXECUTE FUNCTION perlsnitch();
```
