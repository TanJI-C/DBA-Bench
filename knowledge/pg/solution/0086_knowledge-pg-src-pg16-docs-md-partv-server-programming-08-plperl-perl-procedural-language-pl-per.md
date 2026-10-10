# Error Handling; Explicit Subtransactions; Transaction Management

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partV_server_programming/08_plperl_-_perl_procedural_language.md`
- Source Title: `PL/Perl — Perl Procedural Language`
- Source Heading Path: `PL/Perl - Perl Procedural Language > Error Handling; Explicit Subtransactions; Transaction Management`
- Source Line Ranges: `1-1059`
- Chunk ID: `pg16_solution_0086_a1e3be6c2c`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `40ff9a2724e6829fc06ce3feae1fca6193847c0622deea6b4f9a47eb534de9b2`

## Retrieval Guidance

- Use When: Recover from or isolate a confirmed statement failure inside a PL/Perl function or procedure.
- Retrieval Keywords: PL/Perl error handling, eval, spi_commit, spi_rollback, subtransaction, trapped error
- Follow-up Guidance: Confirm function context because explicit transaction controls are only valid in supported procedure/top-level contexts.
- Classification Note: These sections describe trapping errors and using subtransactions or explicit transaction controls to contain known failures in PL/Perl code.

## Official Source Content

# PL/Perl — Perl Procedural Language

PL/Perl is a loadable procedural language that enables you to write
PostgreSQL functions and procedures in the
[Perl programming language](https://www.perl.org).

The main advantage to using PL/Perl is that this allows use,
within stored functions and procedures, of the manyfold "string
munging" operators and functions available for Perl.  Parsing
complex strings might be easier using Perl than it is with the
string functions and control structures provided in PL/pgSQL.

To install PL/Perl in a particular database, use
`CREATE EXTENSION plperl`.

> **Tip:**

> If a language is installed into `template1`, all subsequently
> created databases will have the language installed automatically.
>

> **Note:**

> Users of source packages must specially enable the build of
> PL/Perl during the installation process.  (Refer to  linkend="installation"/> for more information.)  Users of
> binary packages might find PL/Perl in a separate subpackage.
>

## PL/Perl Functions and Arguments

To create a function in the PL/Perl language, use the standard
[sql-createfunction](#sql-createfunction)
syntax:

```
CREATE FUNCTION `funcname` (`argument-types`)
RETURNS `return-type`
-- function attributes can go here
AS $$
# PL/Perl function body goes here
$$ LANGUAGE plperl;
```

The body of the function is ordinary Perl code. In fact, the PL/Perl
glue code wraps it inside a Perl subroutine.  A PL/Perl function is
called in a scalar context, so it can't return a list.  You can return
non-scalar values (arrays, records, and sets) by returning a reference,
as discussed below.

In a PL/Perl procedure, any return value from the Perl code is ignored.

PL/Perl also supports anonymous code blocks called with the
[sql-do](#sql-do) statement:

```
DO $$
# PL/Perl code
$$ LANGUAGE plperl;
```

An anonymous code block receives no arguments, and whatever value it
might return is discarded.  Otherwise it behaves just like a function.

> **Note:**

> The use of named nested subroutines is dangerous in Perl, especially if
> they refer to lexical variables in the enclosing scope. Because a PL/Perl
> function is wrapped in a subroutine, any named subroutine you place inside
> one will be nested. In general, it is far safer to create anonymous
> subroutines which you call via a coderef. For more information, see the
> entries for `Variable "%s" will not stay shared` and
> `Variable "%s" is not available` in the
> perldiag man page, or
> search the Internet for "perl nested named subroutine".
>

The syntax of the `CREATE FUNCTION` command requires
the function body to be written as a string constant.  It is usually
most convenient to use dollar quoting (see [sql-syntax-dollar-quoting](#sql-syntax-dollar-quoting)) for the string constant.
If you choose to use escape string syntax `E''`,
you must double any single quote marks (`'`) and backslashes
(`\`) used in the body of the function
(see [sql-syntax-strings](#sql-syntax-strings)).

Arguments and results are handled as in any other Perl subroutine:
arguments are passed in `@_`, and a result value
is returned with `return` or as the last expression
evaluated in the function.

For example, a function returning the greater of two integer values
could be defined as:

```
CREATE FUNCTION perl_max (integer, integer) RETURNS integer AS $$
if ($_[0] > $_[1]) { return $_[0]; }
return $_[1];
$$ LANGUAGE plperl;
```

> **Note:**

> Arguments will be converted from the database's encoding to UTF-8
> for use inside PL/Perl, and then converted from UTF-8 back to the
> database encoding upon return.
>

If an SQL null value is passed to a function,
the argument value will appear as "undefined" in Perl.  The
above function definition will not behave very nicely with null
inputs (in fact, it will act as though they are zeroes).  We could
add `STRICT` to the function definition to make
PostgreSQL do something more reasonable:
if a null value is passed, the function will not be called at all,
but will just return a null result automatically.  Alternatively,
we could check for undefined inputs in the function body.  For
example, suppose that we wanted `perl_max` with
one null and one nonnull argument to return the nonnull argument,
rather than a null value:

```
CREATE FUNCTION perl_max (integer, integer) RETURNS integer AS $$
my ($x, $y) = @_;
if (not defined $x) {
return undef if not defined $y;
return $y;
}
return $x if not defined $y;
return $x if $x > $y;
return $y;
$$ LANGUAGE plperl;
```

As shown above, to return an SQL null value from a PL/Perl
function, return an undefined value.  This can be done whether the
function is strict or not.

Anything in a function argument that is not a reference is
a string, which is in the standard PostgreSQL
external text representation for the relevant data type. In the case of
ordinary numeric or text types, Perl will just do the right thing and
the programmer will normally not have to worry about it. However, in
other cases the argument will need to be converted into a form that is
more usable in Perl. For example, the `decode_bytea`
function can be used to convert an argument of
type `bytea` into unescaped binary.

Similarly, values passed back to PostgreSQL
must be in the external text representation format. For example, the
`encode_bytea` function can be used to
escape binary data for a return value of type `bytea`.

One case that is particularly important is boolean values.  As just
stated, the default behavior for `bool` values is that they
are passed to Perl as text, thus either `'t'`
or `'f'`.  This is problematic, since Perl will not
treat `'f'` as false!  It is possible to improve matters
by using a "transform" (see
[sql-createtransform](#sql-createtransform)).  Suitable transforms are provided
by the `bool_plperl` extension.  To use it, install
the extension:

```
CREATE EXTENSION bool_plperl;  -- or bool_plperlu for PL/PerlU
```

Then use the `TRANSFORM` function attribute for a
PL/Perl function that takes or returns `bool`, for example:

```
CREATE FUNCTION perl_and(bool, bool) RETURNS bool
TRANSFORM FOR TYPE bool
AS $$
my ($a, $b) = @_;
return $a && $b;
$$ LANGUAGE plperl;
```

When this transform is applied, `bool` arguments will be seen
by Perl as being `1` or empty, thus properly true or
false.  If the function result is type `bool`, it will be true
or false according to whether Perl would evaluate the returned value as
true.
Similar transformations are also performed for boolean query arguments
and results of SPI queries performed inside the function
([plperl-database](#plperl-database)).

Perl can return PostgreSQL arrays as
references to Perl arrays.  Here is an example:

```
CREATE OR REPLACE function returns_array()
RETURNS text[][] AS $$
return [['a"b','c,d'],['e\\f','g']];
$$ LANGUAGE plperl;

select returns_array();
```

Perl passes PostgreSQL arrays as a blessed
`PostgreSQL::InServer::ARRAY` object. This object may be treated as an array
reference or a string, allowing for backward compatibility with Perl
code written for PostgreSQL versions below 9.1 to
run.  For example:

```
CREATE OR REPLACE FUNCTION concat_array_elements(text[]) RETURNS TEXT AS $$
my $arg = shift;
my $result = "";
return undef if (!defined $arg);

# as an array reference
for (@$arg) {
$result .= $_;
}

# also works as a string
$result .= $arg;

return $result;
$$ LANGUAGE plperl;

SELECT concat_array_elements(ARRAY['PL','/','Perl']);
```

> **Note:**

> Multidimensional arrays are represented as references to
> lower-dimensional arrays of references in a way common to every Perl
> programmer.
>

Composite-type arguments are passed to the function as references
to hashes.  The keys of the hash are the attribute names of the
composite type.  Here is an example:

```
CREATE TABLE employee (
name text,
basesalary integer,
bonus integer
);

CREATE FUNCTION empcomp(employee) RETURNS integer AS $$
my ($emp) = @_;
return $emp->{basesalary} + $emp->{bonus};
$$ LANGUAGE plperl;

SELECT name, empcomp(employee.*) FROM employee;
```

A PL/Perl function can return a composite-type result using the same
approach: return a reference to a hash that has the required attributes.
For example:

```
CREATE TYPE testrowperl AS (f1 integer, f2 text, f3 text);

CREATE OR REPLACE FUNCTION perl_row() RETURNS testrowperl AS $$
return {f2 => 'hello', f1 => 1, f3 => 'world'};
$$ LANGUAGE plperl;

SELECT * FROM perl_row();
```

Any columns in the declared result data type that are not present in the
hash will be returned as null values.

Similarly, output arguments of procedures can be returned as a hash
reference:

```
CREATE PROCEDURE perl_triple(INOUT a integer, INOUT b integer) AS $$
my ($a, $b) = @_;
return {a => $a * 3, b => $b * 3};
$$ LANGUAGE plperl;

CALL perl_triple(5, 10);
```

PL/Perl functions can also return sets of either scalar or
composite types.  Usually you'll want to return rows one at a
time, both to speed up startup time and to keep from queuing up
the entire result set in memory.  You can do this with
`return_next` as illustrated below.  Note that
after the last `return_next`, you must put
either `return` or (better) `return
undef`.

```
CREATE OR REPLACE FUNCTION perl_set_int(int)
RETURNS SETOF INTEGER AS $$
foreach (0..$_[0]) {
return_next($_);
}
return undef;
$$ LANGUAGE plperl;

SELECT * FROM perl_set_int(5);

CREATE OR REPLACE FUNCTION perl_set()
RETURNS SETOF testrowperl AS $$
return_next({ f1 => 1, f2 => 'Hello', f3 => 'World' });
return_next({ f1 => 2, f2 => 'Hello', f3 => 'PostgreSQL' });
return_next({ f1 => 3, f2 => 'Hello', f3 => 'PL/Perl' });
return undef;
$$ LANGUAGE plperl;
```

For small result sets, you can return a reference to an array that
contains either scalars, references to arrays, or references to
hashes for simple types, array types, and composite types,
respectively.  Here are some simple examples of returning the entire
result set as an array reference:

```
CREATE OR REPLACE FUNCTION perl_set_int(int) RETURNS SETOF INTEGER AS $$
return [0..$_[0]];
$$ LANGUAGE plperl;

SELECT * FROM perl_set_int(5);

CREATE OR REPLACE FUNCTION perl_set() RETURNS SETOF testrowperl AS $$
return [
{ f1 => 1, f2 => 'Hello', f3 => 'World' },
{ f1 => 2, f2 => 'Hello', f3 => 'PostgreSQL' },
{ f1 => 3, f2 => 'Hello', f3 => 'PL/Perl' }
];
$$ LANGUAGE plperl;

SELECT * FROM perl_set();
```

If you wish to use the `strict` pragma with your code you
have a few options. For temporary global use you can `SET`
`plperl.use_strict` to true.
This will affect subsequent compilations of PL/Perl
functions, but not functions already compiled in the current session.
For permanent global use you can set `plperl.use_strict`
to true in the `postgresql.conf` file.

For permanent use in specific functions you can simply put:

```
use strict;
```

at the top of the function body.

The `feature` pragma is also available to `use` if your Perl is version 5.10.0 or higher.

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

## Trusted and Untrusted PL/Perl

Normally, PL/Perl is installed as a "trusted" programming
language named `plperl`.  In this setup, certain Perl
operations are disabled to preserve security.  In general, the
operations that are restricted are those that interact with the
environment. This includes file handle operations,
`require`, and `use` (for
external modules).  There is no way to access internals of the
database server process or to gain OS-level access with the
permissions of the server process,
as a C function can do.  Thus, any unprivileged database user can
be permitted to use this language.

> **Warning:**

> Trusted PL/Perl relies on the Perl `Opcode` module to
> preserve security.
> Perl
> [documents](https://perldoc.perl.org/Opcode#WARNING)
> that the module is not effective for the trusted PL/Perl use case.  If
> your security needs are incompatible with the uncertainty in that warning,
> consider executing `REVOKE USAGE ON LANGUAGE plperl FROM
> PUBLIC`.
>

Here is an example of a function that will not work because file
system operations are not allowed for security reasons:

```
CREATE FUNCTION badfunc() RETURNS integer AS $$
my $tmpfile = "/tmp/badfile";
open my $fh, '>', $tmpfile
or elog(ERROR, qq{could not open the file "$tmpfile": $!});
print $fh "Testing writing to a file\n";
close $fh or elog(ERROR, qq{could not close the file "$tmpfile": $!});
return 1;
$$ LANGUAGE plperl;
```

The creation of this function will fail as its use of a forbidden
operation will be caught by the validator.

Sometimes it is desirable to write Perl functions that are not
restricted.  For example, one might want a Perl function that sends
mail.  To handle these cases, PL/Perl can also be installed as an
"untrusted" language (usually called
PL/PerlU).
In this case the full Perl language is available.  When installing the
language, the language name `plperlu` will select
the untrusted PL/Perl variant.

The writer of a PL/PerlU function must take care that the function
cannot be used to do anything unwanted, since it will be able to do
anything that could be done by a user logged in as the database
administrator.  Note that the database system allows only database
superusers to create functions in untrusted languages.

If the above function was created by a superuser using the language
`plperlu`, execution would succeed.

In the same way, anonymous code blocks written in Perl can use
restricted operations if the language is specified as
`plperlu` rather than `plperl`, but the caller
must be a superuser.

> **Note:**

> While PL/Perl functions run in a separate Perl
> interpreter for each SQL role, all PL/PerlU functions
> executed in a given session run in a single Perl interpreter (which is
> not any of the ones used for PL/Perl functions).
> This allows PL/PerlU functions to share data freely,
> but no communication can occur between PL/Perl and
> PL/PerlU functions.
>

> **Note:**

> Perl cannot support multiple interpreters within one process unless
> it was built with the appropriate flags, namely either
> `usemultiplicity` or `useithreads`.
> (`usemultiplicity` is preferred unless you actually need
> to use threads.  For more details, see the
> perlembed man page.)
> If PL/Perl is used with a copy of Perl that was not built
> this way, then it is only possible to have one Perl interpreter per
> session, and so any one session can only execute either
> PL/PerlU functions, or PL/Perl functions
> that are all called by the same SQL role.
>

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

## PL/Perl Under the Hood

### Configuration

This section lists configuration parameters that affect PL/Perl.

**`plperl.on_init` (`string`)**
: Specifies Perl code to be executed when a Perl interpreter is first
initialized, before it is specialized for use by `plperl` or
`plperlu`.
The SPI functions are not available when this code is executed.
If the code fails with an error it will abort the initialization of
the interpreter and propagate out to the calling query, causing the
current transaction or subtransaction to be aborted.

The Perl code is limited to a single string. Longer code can be placed
into a module and loaded by the `on_init` string.
Examples:

```
plperl.on_init = 'require "plperlinit.pl"'
plperl.on_init = 'use lib "/my/app"; use MyApp::PgInit;'
```

Any modules loaded by `plperl.on_init`, either directly or
indirectly, will be available for use by `plperl`.  This may
create a security risk. To see what modules have been loaded you can use:

```
DO 'elog(WARNING, join ", ", sort keys %INC)' LANGUAGE plperl;
```

Initialization will happen in the postmaster if the `plperl` library is
included in [guc-shared-preload-libraries](#guc-shared-preload-libraries), in which
case extra consideration should be given to the risk of destabilizing
the postmaster.  The principal reason for making use of this feature
is that Perl modules loaded by `plperl.on_init` need be
loaded only at postmaster start, and will be instantly available
without loading overhead in individual database sessions.  However,
keep in mind that the overhead is avoided only for the first Perl
interpreter used by a database session — either PL/PerlU, or
PL/Perl for the first SQL role that calls a PL/Perl function.  Any
additional Perl interpreters created in a database session will have
to execute `plperl.on_init` afresh.  Also, on Windows there
will be no savings whatsoever from preloading, since the Perl
interpreter created in the postmaster process does not propagate to
child processes.

This parameter can only be set in the `postgresql.conf` file or on the server command line.

**`plperl.on_plperl_init` (`string`)**
: These parameters specify Perl code to be executed when a Perl
interpreter is specialized for `plperl` or
`plperlu` respectively.  This will happen when a PL/Perl or
PL/PerlU function is first executed in a database session, or when
an additional interpreter has to be created because the other language
is called or a PL/Perl function is called by a new SQL role.  This
follows any initialization done by `plperl.on_init`.
The SPI functions are not available when this code is executed.
The Perl code in `plperl.on_plperl_init` is executed after
"locking down" the interpreter, and thus it can only perform
trusted operations.

If the code fails with an error it will abort the initialization and
propagate out to the calling query, causing the current transaction or
subtransaction to be aborted.  Any actions already done within Perl
won't be undone; however, that interpreter won't be used again.
If the language is used again the initialization will be attempted
again within a fresh Perl interpreter.

Only superusers can change these settings.  Although these settings
can be changed within a session, such changes will not affect Perl
interpreters that have already been used to execute functions.

**`plperl.use_strict` (`boolean`)**
: When set true subsequent compilations of PL/Perl functions will have
the `strict` pragma enabled.  This parameter does not affect
functions already compiled in the current session.

### Limitations and Missing Features

The following features are currently missing from PL/Perl, but they
would make welcome contributions.

- PL/Perl functions cannot call each other directly.
- SPI is not yet fully implemented.
- If you are fetching very large data sets using
`spi_exec_query`, you should be aware that
these will all go into memory.  You can avoid this by using
`spi_query`/`spi_fetchrow` as
illustrated earlier.

A similar problem occurs if a set-returning function passes a
large set of rows back to PostgreSQL via `return`. You
can avoid this problem too by instead using
`return_next` for each row returned, as shown
previously.
- When a session ends normally, not due to a fatal error, any
`END` blocks that have been defined are executed.
Currently no other actions are performed. Specifically,
file handles are not automatically flushed and objects are
not automatically destroyed.
