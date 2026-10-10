# Error Handling; sqlca; WHENEVER; SQLSTATE; SQL Descriptor Area diagnostics

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIV_client_interfaces/03_ecpg_-_embedded_sql_in_c.md`
- Source Title: `ECPG — Embedded SQL in C`
- Source Heading Path: `ECPG - Embedded SQL in C > Error Handling; sqlca; WHENEVER; SQLSTATE; SQL Descriptor Area diagnostics`
- Source Line Ranges: `1-5318`
- Chunk ID: `pg16_guide_0046_8170497982`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `4d9fc39454824765a54d9214d4dd746f82ab7f8c90147a4be7b2d22a24ac9077`

## Retrieval Guidance

- Use When: Determine whether an ECPG statement failed, reached no rows, or produced a warning, and decide which error path was taken.
- Retrieval Keywords: ECPG error handling, sqlca, sqlcode, sqlstate, WHENEVER SQLERROR, WHENEVER NOT FOUND, ECPG diagnostics
- Follow-up Guidance: Map SQLSTATE values to the appendix error-code record when a database-side condition is involved.
- Classification Note: These sections define the status variables, SQLSTATE values, SQLCA fields, and WHENEVER behavior used to detect and confirm embedded-SQL runtime failures.

## Official Source Content

# ECPG — Embedded SQL in C

This chapter describes the embedded SQL package
for PostgreSQL. It was written by
Linus Tolke (linus@epact.se) and Michael Meskes
(meskes@postgresql.org). Originally it was written to work with
C. It also works with C++, but
it does not recognize all C++ constructs yet.

This documentation is quite incomplete.  But since this
interface is standardized, additional information can be found in
many resources about SQL.

## The Concept

An embedded SQL program consists of code written in an ordinary
programming language, in this case C, mixed with SQL commands in
specially marked sections.  To build the program, the source code (`*.pgc`)
is first passed through the embedded SQL preprocessor, which converts it
to an ordinary C program (`*.c`), and afterwards it can be processed by a C
compiler.  (For details about the compiling and linking see [ecpg-process](#ecpg-process).)
Converted ECPG applications call functions in the libpq library
through the embedded SQL library (ecpglib), and communicate with
the PostgreSQL server using the normal frontend-backend protocol.

Embedded SQL has advantages over other methods
for handling SQL commands from C code. First, it
takes care of the tedious passing of information to and from
variables in your C program.  Second, the SQL
code in the program is checked at build time for syntactical
correctness.  Third, embedded SQL in C is
specified in the SQL standard and supported by
many other SQL database systems.  The
PostgreSQL implementation is designed to match this
standard as much as possible, and it is usually possible to port
embedded SQL programs written for other SQL
databases to PostgreSQL with relative
ease.

As already stated, programs written for the embedded
SQL interface are normal C programs with special
code inserted to perform database-related actions.  This special
code always has the form:

```
EXEC SQL ...;
```

These statements syntactically take the place of a C statement.
Depending on the particular statement, they can appear at the
global level or within a function.

Embedded
SQL statements follow the case-sensitivity rules of
normal SQL code, and not those of C. Also they allow nested
C-style comments as per the SQL standard. The C part of the
program, however, follows the C standard of not accepting nested comments.
Embedded SQL statements likewise use SQL rules, not
C rules, for parsing quoted strings and identifiers.
(See [sql-syntax-strings](#sql-syntax-strings) and
[sql-syntax-identifiers](#sql-syntax-identifiers) respectively.  Note that
ECPG assumes that `standard_conforming_strings`
is `on`.)
Of course, the C part of the program follows C quoting rules.

The following sections explain all the embedded SQL statements.

## Managing Database Connections

This section describes how to open, close, and switch database
connections.

### Connecting to the Database Server

One connects to a database using the following statement:

```
EXEC SQL CONNECT TO `target` `AS `connection-name` USER `user-name`;
```

The `target` can be specified in the
following ways:

The connection target `DEFAULT` initiates a connection
to the default database under the default user name.  No separate
user name or connection name can be specified in that case.

If you specify the connection target directly (that is, not as a string
literal or variable reference), then the components of the target are
passed through normal SQL parsing; this means that, for example,
the `hostname` must look like one or more SQL
identifiers separated by dots, and those identifiers will be
case-folded unless double-quoted.  Values of
any `options` must be SQL identifiers,
integers, or variable references.  Of course, you can put nearly
anything into an SQL identifier by double-quoting it.
In practice, it is probably less error-prone to use a (single-quoted)
string literal or a variable reference than to write the connection
target directly.

There are also different ways to specify the user name:

As above, the parameters `username` and
`password` can be an SQL identifier, an
SQL string literal, or a reference to a character variable.

If the connection target includes any `options`,
those consist of
``keyword`=`value``
specifications separated by ampersands (`&`).
The allowed key words are the same ones recognized
by libpq (see
[libpq-paramkeywords](#libpq-paramkeywords)).  Spaces are ignored before
any `keyword` or `value`,
though not within or after one.  Note that there is no way to
write `&` within a `value`.

Notice that when specifying a socket connection
(with the `unix:` prefix), the host name must be
exactly `localhost`.  To select a non-default
socket directory, write the directory's pathname as the value of
a `host` option in
the `options` part of the target.

The `connection-name` is used to handle
multiple connections in one program.  It can be omitted if a
program uses only one connection.  The most recently opened
connection becomes the current connection, which is used by default
when an SQL statement is to be executed (see later in this
chapter).

Here are some examples of `CONNECT` statements:

```
EXEC SQL CONNECT TO mydb@sql.mydomain.com;

EXEC SQL CONNECT TO tcp:postgresql://sql.mydomain.com/mydb AS myconnection USER john;

EXEC SQL BEGIN DECLARE SECTION;
const char *target = "mydb@sql.mydomain.com";
const char *user = "john";
const char *passwd = "secret";
EXEC SQL END DECLARE SECTION;
...
EXEC SQL CONNECT TO :target USER :user USING :passwd;
/* or EXEC SQL CONNECT TO :target USER :user/:passwd; */
```

The last example makes use of the feature referred to above as
character variable references.  You will see in later sections how C
variables can be used in SQL statements when you prefix them with a
colon.

Be advised that the format of the connection target is not
specified in the SQL standard.  So if you want to develop portable
applications, you might want to use something based on the last
example above to encapsulate the connection target string
somewhere.

If untrusted users have access to a database that has not adopted a
[secure schema usage pattern](#ddl-schemas-patterns),
begin each session by removing publicly-writable schemas
from `search_path`.  For example,
add `options=-c search_path=`
to ``options``, or
issue `EXEC SQL SELECT pg_catalog.set_config('search_path', '',
false);` after connecting.  This consideration is not specific to
ECPG; it applies to every interface for executing arbitrary SQL commands.

### Choosing a Connection

SQL statements in embedded SQL programs are by default executed on
the current connection, that is, the most recently opened one.  If
an application needs to manage multiple connections, then there are
three ways to handle this.

The first option is to explicitly choose a connection for each SQL
statement, for example:

```
EXEC SQL AT `connection-name` SELECT ...;
```

This option is particularly suitable if the application needs to
use several connections in mixed order.

If your application uses multiple threads of execution, they cannot share a
connection concurrently. You must either explicitly control access to the connection
(using mutexes) or use a connection for each thread.

The second option is to execute a statement to switch the current
connection.  That statement is:

```
EXEC SQL SET CONNECTION `connection-name`;
```

This option is particularly convenient if many statements are to be
executed on the same connection.

Here is an example program managing multiple database connections:

```

#include

EXEC SQL BEGIN DECLARE SECTION;
char dbname[1024];
EXEC SQL END DECLARE SECTION;

int
main()
{
EXEC SQL CONNECT TO testdb1 AS con1 USER testuser;
EXEC SQL SELECT pg_catalog.set_config('search_path', '', false); EXEC SQL COMMIT;
EXEC SQL CONNECT TO testdb2 AS con2 USER testuser;
EXEC SQL SELECT pg_catalog.set_config('search_path', '', false); EXEC SQL COMMIT;
EXEC SQL CONNECT TO testdb3 AS con3 USER testuser;
EXEC SQL SELECT pg_catalog.set_config('search_path', '', false); EXEC SQL COMMIT;

/* This query would be executed in the last opened database "testdb3". */
EXEC SQL SELECT current_database() INTO :dbname;
printf("current=%s (should be testdb3)\n", dbname);

/* Using "AT" to run a query in "testdb2" */
EXEC SQL AT con2 SELECT current_database() INTO :dbname;
printf("current=%s (should be testdb2)\n", dbname);

/* Switch the current connection to "testdb1". */
EXEC SQL SET CONNECTION con1;

EXEC SQL SELECT current_database() INTO :dbname;
printf("current=%s (should be testdb1)\n", dbname);

EXEC SQL DISCONNECT ALL;
return 0;
}

```

This example would produce this output:

```
current=testdb3 (should be testdb3)
current=testdb2 (should be testdb2)
current=testdb1 (should be testdb1)
```

The third option is to declare an SQL identifier linked to
the connection, for example:

```
EXEC SQL AT `connection-name` DECLARE `statement-name` STATEMENT;
EXEC SQL PREPARE `statement-name` FROM :`dyn-string`;
```

Once you link an SQL identifier to a connection, you execute dynamic SQL
without an AT clause. Note that this option behaves like preprocessor
directives, therefore the link is enabled only in the file.

Here is an example program using this option:

```

#include

EXEC SQL BEGIN DECLARE SECTION;
char dbname[128];
char *dyn_sql = "SELECT current_database()";
EXEC SQL END DECLARE SECTION;

int main(){
EXEC SQL CONNECT TO postgres AS con1;
EXEC SQL CONNECT TO testdb AS con2;
EXEC SQL AT con1 DECLARE stmt STATEMENT;
EXEC SQL PREPARE stmt FROM :dyn_sql;
EXEC SQL EXECUTE stmt INTO :dbname;
printf("%s\n", dbname);

EXEC SQL DISCONNECT ALL;
return 0;
}

```

This example would produce this output, even if the default connection is testdb:

```
postgres
```

### Closing a Connection

To close a connection, use the following statement:

```
EXEC SQL DISCONNECT `connection`;
```

The `connection` can be specified
in the following ways:

If no connection name is specified, the current connection is
closed.

It is good style that an application always explicitly disconnect
from every connection it opened.

## Running SQL Commands

Any SQL command can be run from within an embedded SQL application.
Below are some examples of how to do that.

### Executing SQL Statements

Creating a table:

```
EXEC SQL CREATE TABLE foo (number integer, ascii char(16));
EXEC SQL CREATE UNIQUE INDEX num1 ON foo(number);
EXEC SQL COMMIT;
```

Inserting rows:

```
EXEC SQL INSERT INTO foo (number, ascii) VALUES (9999, 'doodad');
EXEC SQL COMMIT;
```

Deleting rows:

```
EXEC SQL DELETE FROM foo WHERE number = 9999;
EXEC SQL COMMIT;
```

Updates:

```
EXEC SQL UPDATE foo
SET ascii = 'foobar'
WHERE number = 9999;
EXEC SQL COMMIT;
```

`SELECT` statements that return a single result
row can also be executed using
`EXEC SQL` directly.  To handle result sets with
multiple rows, an application has to use a cursor;
see [ecpg-cursors](#ecpg-cursors) below.  (As a special case, an
application can fetch multiple rows at once into an array host
variable; see [ecpg-variables-arrays](#ecpg-variables-arrays).)

Single-row select:

```
EXEC SQL SELECT foo INTO :FooBar FROM table1 WHERE ascii = 'doodad';
```

Also, a configuration parameter can be retrieved with the
`SHOW` command:

```
EXEC SQL SHOW search_path INTO :var;
```

The tokens of the form
`:`something`` are
*host variables*, that is, they refer to
variables in the C program.  They are explained in [ecpg-variables](#ecpg-variables).

### Using Cursors

To retrieve a result set holding multiple rows, an application has
to declare a cursor and fetch each row from the cursor.  The steps
to use a cursor are the following: declare a cursor, open it, fetch
a row from the cursor, repeat, and finally close it.

Select using cursors:

```
EXEC SQL DECLARE foo_bar CURSOR FOR
SELECT number, ascii FROM foo
ORDER BY ascii;
EXEC SQL OPEN foo_bar;
EXEC SQL FETCH foo_bar INTO :FooBar, DooDad;
...
EXEC SQL CLOSE foo_bar;
EXEC SQL COMMIT;
```

For more details about declaring a cursor, see [ecpg-sql-declare](#ecpg-sql-declare); for more details about fetching rows from a
cursor, see [sql-fetch](#sql-fetch).

> **Note:**

> The ECPG `DECLARE` command does not actually
> cause a statement to be sent to the PostgreSQL backend.  The
> cursor is opened in the backend (using the
> backend's `DECLARE` command) at the point when
> the `OPEN` command is executed.
>

### Managing Transactions

In the default mode, statements are committed only when
`EXEC SQL COMMIT` is issued. The embedded SQL
interface also supports autocommit of transactions (similar to
psql's default behavior) via the -t`
command-line option to `ecpg` (see [app-ecpg](#app-ecpg)) or via the `EXEC SQL SET AUTOCOMMIT TO
ON` statement. In autocommit mode, each command is
automatically committed unless it is inside an explicit transaction
block. This mode can be explicitly turned off using `EXEC
SQL SET AUTOCOMMIT TO OFF`.

The following transaction management commands are available:

**`EXEC SQL COMMIT`**
: Commit an in-progress transaction.

**`EXEC SQL ROLLBACK`**
: Roll back an in-progress transaction.

**`EXEC SQL PREPARE TRANSACTION ``transaction_id`**
: Prepare the current transaction for two-phase commit.

**`EXEC SQL COMMIT PREPARED ``transaction_id`**
: Commit a transaction that is in prepared state.

**`EXEC SQL ROLLBACK PREPARED ``transaction_id`**
: Roll back a transaction that is in prepared state.

**`EXEC SQL SET AUTOCOMMIT TO ON`**
: Enable autocommit mode.

**`EXEC SQL SET AUTOCOMMIT TO OFF`**
: Disable autocommit mode.  This is the default.

### Prepared Statements

When the values to be passed to an SQL statement are not known at
compile time, or the same statement is going to be used many
times, then prepared statements can be useful.

The statement is prepared using the
command `PREPARE`.  For the values that are not
known yet, use the
placeholder "`?`":

```
EXEC SQL PREPARE stmt1 FROM "SELECT oid, datname FROM pg_database WHERE oid = ?";
```

If a statement returns a single row, the application can
call `EXECUTE` after
`PREPARE` to execute the statement, supplying the
actual values for the placeholders with a `USING`
clause:

```
EXEC SQL EXECUTE stmt1 INTO :dboid, :dbname USING 1;
```

If a statement returns multiple rows, the application can use a
cursor declared based on the prepared statement.  To bind input
parameters, the cursor must be opened with
a `USING` clause:

```
EXEC SQL PREPARE stmt1 FROM "SELECT oid,datname FROM pg_database WHERE oid > ?";
EXEC SQL DECLARE foo_bar CURSOR FOR stmt1;

/* when end of result set reached, break out of while loop */
EXEC SQL WHENEVER NOT FOUND DO BREAK;

EXEC SQL OPEN foo_bar USING 100;
...
while (1)
{
EXEC SQL FETCH NEXT FROM foo_bar INTO :dboid, :dbname;
...
}
EXEC SQL CLOSE foo_bar;
```

When you don't need the prepared statement anymore, you should
deallocate it:

```
EXEC SQL DEALLOCATE PREPARE `name`;
```

For more details about `PREPARE`,
see [ecpg-sql-prepare](#ecpg-sql-prepare). Also
see [ecpg-dynamic](#ecpg-dynamic) for more details about using
placeholders and input parameters.

## Using Host Variables

In [ecpg-commands](#ecpg-commands) you saw how you can execute SQL
statements from an embedded SQL program.  Some of those statements
only used fixed values and did not provide a way to insert
user-supplied values into statements or have the program process
the values returned by the query.  Those kinds of statements are
not really useful in real applications.  This section explains in
detail how you can pass data between your C program and the
embedded SQL statements using a simple mechanism called
*host variables*. In an embedded SQL program we
consider the SQL statements to be *guests* in the C
program code which is the *host language*. Therefore
the variables of the C program are called *host
variables*.

Another way to exchange values between PostgreSQL backends and ECPG
applications is the use of SQL descriptors, described
in [ecpg-descriptors](#ecpg-descriptors).

### Overview

Passing data between the C program and the SQL statements is
particularly simple in embedded SQL.  Instead of having the
program paste the data into the statement, which entails various
complications, such as properly quoting the value, you can simply
write the name of a C variable into the SQL statement, prefixed by
a colon.  For example:

```
EXEC SQL INSERT INTO sometable VALUES (:v1, 'foo', :v2);
```

This statement refers to two C variables named
`v1` and `v2` and also uses a
regular SQL string literal, to illustrate that you are not
restricted to use one kind of data or the other.

This style of inserting C variables in SQL statements works
anywhere a value expression is expected in an SQL statement.

### Declare Sections

To pass data from the program to the database, for example as
parameters in a query, or to pass data from the database back to
the program, the C variables that are intended to contain this
data need to be declared in specially marked sections, so the
embedded SQL preprocessor is made aware of them.

This section starts with:

```
EXEC SQL BEGIN DECLARE SECTION;
```

and ends with:

```
EXEC SQL END DECLARE SECTION;
```

Between those lines, there must be normal C variable declarations,
such as:

```
int   x = 4;
char  foo[16], bar[16];
```

As you can see, you can optionally assign an initial value to the variable.
The variable's scope is determined by the location of its declaring
section within the program.
You can also declare variables with the following syntax which implicitly
creates a declare section:

```
EXEC SQL int i = 4;
```

You can have as many declare sections in a program as you like.

The declarations are also echoed to the output file as normal C
variables, so there's no need to declare them again.  Variables
that are not intended to be used in SQL commands can be declared
normally outside these special sections.

The definition of a structure or union also must be listed inside
a `DECLARE` section. Otherwise the preprocessor cannot
handle these types since it does not know the definition.

### Retrieving Query Results

Now you should be able to pass data generated by your program into
an SQL command.  But how do you retrieve the results of a query?
For that purpose, embedded SQL provides special variants of the
usual commands `SELECT` and
`FETCH`.  These commands have a special
`INTO` clause that specifies which host variables
the retrieved values are to be stored in.
`SELECT` is used for a query that returns only
single row, and `FETCH` is used for a query that
returns multiple rows, using a cursor.

Here is an example:

```
/*
* assume this table:
* CREATE TABLE test1 (a int, b varchar(50));
*/

EXEC SQL BEGIN DECLARE SECTION;
int v1;
VARCHAR v2;
EXEC SQL END DECLARE SECTION;

...

EXEC SQL SELECT a, b INTO :v1, :v2 FROM test;
```

So the `INTO` clause appears between the select
list and the `FROM` clause.  The number of
elements in the select list and the list after
`INTO` (also called the target list) must be
equal.

Here is an example using the command `FETCH`:

```
EXEC SQL BEGIN DECLARE SECTION;
int v1;
VARCHAR v2;
EXEC SQL END DECLARE SECTION;

...

EXEC SQL DECLARE foo CURSOR FOR SELECT a, b FROM test;

...

do
{
...
EXEC SQL FETCH NEXT FROM foo INTO :v1, :v2;
...
} while (...);
```

Here the `INTO` clause appears after all the
normal clauses.

### Type Mapping

When ECPG applications exchange values between the PostgreSQL
server and the C application, such as when retrieving query
results from the server or executing SQL statements with input
parameters, the values need to be converted between PostgreSQL
data types and host language variable types (C language data
types, concretely).  One of the main points of ECPG is that it
takes care of this automatically in most cases.

In this respect, there are two kinds of data types: Some simple
PostgreSQL data types, such as `integer`
and `text`, can be read and written by the application
directly.  Other PostgreSQL data types, such
as `timestamp` and `numeric` can only be
accessed through special library functions; see
[ecpg-special-types](#ecpg-special-types).

[ecpg-datatype-hostvars-table](#ecpg-datatype-hostvars-table) shows which PostgreSQL
data types correspond to which C data types.  When you wish to
send or receive a value of a given PostgreSQL data type, you
should declare a C variable of the corresponding C data type in
the declare section.

| PostgreSQL data type | Host variable type |
| --- | --- |
| `smallint` | `short` |
| `integer` | `int` |
| `bigint` | `long long int` |
| `decimal` | `decimal` (Note: This type can only be accessed through special library functions; see .) |
| `numeric` | `numeric` |
| `real` | `float` |
| `double precision` | `double` |
| `smallserial` | `short` |
| `serial` | `int` |
| `bigserial` | `long long int` |
| `oid` | `unsigned int` |
| `character(`n`)`, `varchar(`n`)`, `text` | `char[`n`+1]`, `VARCHAR[`n`+1]` |
| `name` | `char[NAMEDATALEN]` |
| `timestamp` | `timestamp` |
| `interval` | `interval` |
| `date` | `date` |
| `boolean` | `bool` (Note: declared in `ecpglib.h` if not native) |
| `bytea` | `char *`, `bytea[`n`]` |

#### Handling Character Strings

To handle SQL character string data types, such
as `varchar` and `text`, there are two
possible ways to declare the host variables.

One way is using `char[]`, an array
of `char`, which is the most common way to handle
character data in C.

```
EXEC SQL BEGIN DECLARE SECTION;
char str[50];
EXEC SQL END DECLARE SECTION;
```

Note that you have to take care of the length yourself.  If you
use this host variable as the target variable of a query which
returns a string with more than 49 characters, a buffer overflow
occurs.

The other way is using the `VARCHAR` type, which is a
special type provided by ECPG.  The definition on an array of
type `VARCHAR` is converted into a
named `struct` for every variable. A declaration like:

```
VARCHAR var[180];
```

is converted into:

```
struct varchar_var { int len; char arr[180]; } var;
```

The member `arr` hosts the string
including a terminating zero byte.  Thus, to store a string in
a `VARCHAR` host variable, the host variable has to be
declared with the length including the zero byte terminator.  The
member `len` holds the length of the
string stored in the `arr` without the
terminating zero byte.  When a host variable is used as input for
a query, if `strlen(arr)`
and `len` are different, the shorter one
is used.

`VARCHAR` can be written in upper or lower case, but
not in mixed case.

`char` and `VARCHAR` host variables can
also hold values of other SQL types, which will be stored in
their string forms.

#### Accessing Special Data Types

ECPG contains some special types that help you to interact easily
with some special data types from the PostgreSQL server. In
particular, it has implemented support for the
`numeric`, `decimal`, `date`, `timestamp`,
and `interval` types.  These data types cannot usefully be
mapped to primitive host variable types (such
as `int`, `long long int`,
or `char[]`), because they have a complex internal
structure.  Applications deal with these types by declaring host
variables in special types and accessing them using functions in
the pgtypes library.  The pgtypes library, described in detail
in [ecpg-pgtypes](#ecpg-pgtypes) contains basic functions to deal
with those types, such that you do not need to send a query to
the SQL server just for adding an interval to a time stamp for
example.

The follow subsections describe these special data types. For
more details about pgtypes library functions,
see [ecpg-pgtypes](#ecpg-pgtypes).

##### timestamp, date

Here is a pattern for handling `timestamp` variables
in the ECPG host application.

First, the program has to include the header file for the
`timestamp` type:

```
#include
```

Next, declare a host variable as type `timestamp` in
the declare section:

```
EXEC SQL BEGIN DECLARE SECTION;
timestamp ts;
EXEC SQL END DECLARE SECTION;
```

And after reading a value into the host variable, process it
using pgtypes library functions. In following example, the
`timestamp` value is converted into text (ASCII) form
with the `PGTYPEStimestamp_to_asc()`
function:

```
EXEC SQL SELECT now()::timestamp INTO :ts;

printf("ts = %s\n", PGTYPEStimestamp_to_asc(ts));
```

This example will show some result like following:

```
ts = 2010-06-27 18:03:56.949343
```

In addition, the DATE type can be handled in the same way. The
program has to include `pgtypes_date.h`, declare a host variable
as the date type and convert a DATE value into a text form using
`PGTYPESdate_to_asc()` function. For more details about the
pgtypes library functions, see [ecpg-pgtypes](#ecpg-pgtypes).

##### interval

The handling of the `interval` type is also similar
to the `timestamp` and `date` types.  It
is required, however, to allocate memory for
an `interval` type value explicitly.  In other words,
the memory space for the variable has to be allocated in the
heap memory, not in the stack memory.

Here is an example program:

```
#include
#include
#include

int
main(void)
{
EXEC SQL BEGIN DECLARE SECTION;
interval *in;
EXEC SQL END DECLARE SECTION;

EXEC SQL CONNECT TO testdb;
EXEC SQL SELECT pg_catalog.set_config('search_path', '', false); EXEC SQL COMMIT;

in = PGTYPESinterval_new();
EXEC SQL SELECT '1 min'::interval INTO :in;
printf("interval = %s\n", PGTYPESinterval_to_asc(in));
PGTYPESinterval_free(in);

EXEC SQL COMMIT;
EXEC SQL DISCONNECT ALL;
return 0;
}
```

##### numeric, decimal

The handling of the `numeric`
and `decimal` types is similar to the
`interval` type: It requires defining a pointer,
allocating some memory space on the heap, and accessing the
variable using the pgtypes library functions.  For more details
about the pgtypes library functions,
see [ecpg-pgtypes](#ecpg-pgtypes).

No functions are provided specifically for
the `decimal` type.  An application has to convert it
to a `numeric` variable using a pgtypes library
function to do further processing.

Here is an example program handling `numeric`
and `decimal` type variables.

```
#include
#include
#include

EXEC SQL WHENEVER SQLERROR STOP;

int
main(void)
{
EXEC SQL BEGIN DECLARE SECTION;
numeric *num;
numeric *num2;
decimal *dec;
EXEC SQL END DECLARE SECTION;

EXEC SQL CONNECT TO testdb;
EXEC SQL SELECT pg_catalog.set_config('search_path', '', false); EXEC SQL COMMIT;

num = PGTYPESnumeric_new();
dec = PGTYPESdecimal_new();

EXEC SQL SELECT 12.345::numeric(4,2), 23.456::decimal(4,2) INTO :num, :dec;

printf("numeric = %s\n", PGTYPESnumeric_to_asc(num, 0));
printf("numeric = %s\n", PGTYPESnumeric_to_asc(num, 1));
printf("numeric = %s\n", PGTYPESnumeric_to_asc(num, 2));

/* Convert decimal to numeric to show a decimal value. */
num2 = PGTYPESnumeric_new();
PGTYPESnumeric_from_decimal(dec, num2);

printf("decimal = %s\n", PGTYPESnumeric_to_asc(num2, 0));
printf("decimal = %s\n", PGTYPESnumeric_to_asc(num2, 1));
printf("decimal = %s\n", PGTYPESnumeric_to_asc(num2, 2));

PGTYPESnumeric_free(num2);
PGTYPESdecimal_free(dec);
PGTYPESnumeric_free(num);

EXEC SQL COMMIT;
EXEC SQL DISCONNECT ALL;
return 0;
}
```

##### bytea

The handling of the `bytea` type is similar to
that of `VARCHAR`. The definition on an array of type
`bytea` is converted into a named struct for every
variable. A declaration like:

```
bytea var[180];
```

is converted into:

```
struct bytea_var { int len; char arr[180]; } var;
```

The member `arr` hosts binary format
data. It can also handle `'\0'` as part of
data, unlike `VARCHAR`.
The data is converted from/to hex format and sent/received by
ecpglib.

> **Note:**

> `bytea` variable can be used only when
> [guc-bytea-output](#guc-bytea-output) is set to `hex`.
>

#### Host Variables with Nonprimitive Types

As a host variable you can also use arrays, typedefs, structs, and
pointers.

##### Arrays

There are two use cases for arrays as host variables.  The first
is a way to store some text string in `char[]`
or `VARCHAR[]`, as
explained in [ecpg-char](#ecpg-char).  The second use case is to
retrieve multiple rows from a query result without using a
cursor.  Without an array, to process a query result consisting
of multiple rows, it is required to use a cursor and
the `FETCH` command.  But with array host
variables, multiple rows can be received at once.  The length of
the array has to be defined to be able to accommodate all rows,
otherwise a buffer overflow will likely occur.

Following example scans the `pg_database`
system table and shows all OIDs and names of the available
databases:

```
int
main(void)
{
EXEC SQL BEGIN DECLARE SECTION;
int dbid[8];
char dbname[8][16];
int i;
EXEC SQL END DECLARE SECTION;

memset(dbname, 0, sizeof(char)* 16 * 8);
memset(dbid, 0, sizeof(int) * 8);

EXEC SQL CONNECT TO testdb;
EXEC SQL SELECT pg_catalog.set_config('search_path', '', false); EXEC SQL COMMIT;

/* Retrieve multiple rows into arrays at once. */
EXEC SQL SELECT oid,datname INTO :dbid, :dbname FROM pg_database;

for (i = 0; i  **Note:**

> In PostgreSQL releases before v16, use
> of SQL keywords as typedef names was likely to result in syntax
> errors associated with use of the typedef itself, rather than use
> of the name as an SQL keyword.  The new behavior is less likely to
> cause problems when an existing ECPG application is recompiled in
> a new PostgreSQL release with new
> keywords.
>

##### Pointers

You can declare pointers to the most common types. Note however
that you cannot use pointers as target variables of queries
without auto-allocation. See [ecpg-descriptors](#ecpg-descriptors)
for more information on auto-allocation.

```
EXEC SQL BEGIN DECLARE SECTION;
int   *intp;
char **charp;
EXEC SQL END DECLARE SECTION;
```

### Handling Nonprimitive SQL Data Types

This section contains information on how to handle nonscalar and
user-defined SQL-level data types in ECPG applications.  Note that
this is distinct from the handling of host variables of
nonprimitive types, described in the previous section.

#### Arrays

Multi-dimensional SQL-level arrays are not directly supported in ECPG.
One-dimensional SQL-level arrays can be mapped into C array host
variables and vice-versa.  However, when creating a statement ecpg does
not know the types of the columns, so that it cannot check if a C array
is input into a corresponding SQL-level array.  When processing the
output of an SQL statement, ecpg has the necessary information and thus
checks if both are arrays.

If a query accesses *elements* of an array
separately, then this avoids the use of arrays in ECPG.  Then, a
host variable with a type that can be mapped to the element type
should be used.  For example, if a column type is array of
`integer`, a host variable of type `int`
can be used.  Also if the element type is `varchar`
or `text`, a host variable of type `char[]`
or `VARCHAR[]` can be used.

Here is an example.  Assume the following table:

```
CREATE TABLE t3 (
ii integer[]
);

testdb=> SELECT * FROM t3;
ii
-------------
{1,2,3,4,5}
(1 row)
```

The following example program retrieves the 4th element of the
array and stores it into a host variable of
type `int`:

```
EXEC SQL BEGIN DECLARE SECTION;
int ii;
EXEC SQL END DECLARE SECTION;

EXEC SQL DECLARE cur1 CURSOR FOR SELECT ii[4] FROM t3;
EXEC SQL OPEN cur1;

EXEC SQL WHENEVER NOT FOUND DO BREAK;

while (1)
{
EXEC SQL FETCH FROM cur1 INTO :ii ;
printf("ii=%d\n", ii);
}

EXEC SQL CLOSE cur1;
```

This example shows the following result:

```
ii=4
```

To map multiple array elements to the multiple elements in an
array type host variables each element of array column and each
element of the host variable array have to be managed separately,
for example:

```
EXEC SQL BEGIN DECLARE SECTION;
int ii_a[8];
EXEC SQL END DECLARE SECTION;

EXEC SQL DECLARE cur1 CURSOR FOR SELECT ii[1], ii[2], ii[3], ii[4] FROM t3;
EXEC SQL OPEN cur1;

EXEC SQL WHENEVER NOT FOUND DO BREAK;

while (1)
{
EXEC SQL FETCH FROM cur1 INTO :ii_a[0], :ii_a[1], :ii_a[2], :ii_a[3];
...
}
```

Note again that

```
EXEC SQL BEGIN DECLARE SECTION;
int ii_a[8];
EXEC SQL END DECLARE SECTION;

EXEC SQL DECLARE cur1 CURSOR FOR SELECT ii FROM t3;
EXEC SQL OPEN cur1;

EXEC SQL WHENEVER NOT FOUND DO BREAK;

while (1)
{
/* WRONG */
EXEC SQL FETCH FROM cur1 INTO :ii_a;
...
}
```

would not work correctly in this case, because you cannot map an
array type column to an array host variable directly.

Another workaround is to store arrays in their external string
representation in host variables of type `char[]`
or `VARCHAR[]`.  For more details about this
representation, see [arrays-input](#arrays-input).  Note that
this means that the array cannot be accessed naturally as an
array in the host program (without further processing that parses
the text representation).

#### Composite Types

Composite types are not directly supported in ECPG, but an easy workaround is possible.
The
available workarounds are similar to the ones described for
arrays above: Either access each attribute separately or use the
external string representation.

For the following examples, assume the following type and table:

```
CREATE TYPE comp_t AS (intval integer, textval varchar(32));
CREATE TABLE t4 (compval comp_t);
INSERT INTO t4 VALUES ( (256, 'PostgreSQL') );
```

The most obvious solution is to access each attribute separately.
The following program retrieves data from the example table by
selecting each attribute of the type `comp_t`
separately:

```
EXEC SQL BEGIN DECLARE SECTION;
int intval;
varchar textval[33];
EXEC SQL END DECLARE SECTION;

/* Put each element of the composite type column in the SELECT list. */
EXEC SQL DECLARE cur1 CURSOR FOR SELECT (compval).intval, (compval).textval FROM t4;
EXEC SQL OPEN cur1;

EXEC SQL WHENEVER NOT FOUND DO BREAK;

while (1)
{
/* Fetch each element of the composite type column into host variables. */
EXEC SQL FETCH FROM cur1 INTO :intval, :textval;

printf("intval=%d, textval=%s\n", intval, textval.arr);
}

EXEC SQL CLOSE cur1;
```

To enhance this example, the host variables to store values in
the `FETCH` command can be gathered into one
structure.  For more details about the host variable in the
structure form, see [ecpg-variables-struct](#ecpg-variables-struct).
To switch to the structure, the example can be modified as below.
The two host variables, `intval`
and `textval`, become members of
the `comp_t` structure, and the structure
is specified on the `FETCH` command.

```
EXEC SQL BEGIN DECLARE SECTION;
typedef struct
{
int intval;
varchar textval[33];
} comp_t;

comp_t compval;
EXEC SQL END DECLARE SECTION;

/* Put each element of the composite type column in the SELECT list. */
EXEC SQL DECLARE cur1 CURSOR FOR SELECT (compval).intval, (compval).textval FROM t4;
EXEC SQL OPEN cur1;

EXEC SQL WHENEVER NOT FOUND DO BREAK;

while (1)
{
/* Put all values in the SELECT list into one structure. */
EXEC SQL FETCH FROM cur1 INTO :compval;

printf("intval=%d, textval=%s\n", compval.intval, compval.textval.arr);
}

EXEC SQL CLOSE cur1;
```

Although a structure is used in the `FETCH`
command, the attribute names in the `SELECT`
clause are specified one by one.  This can be enhanced by using
a `*` to ask for all attributes of the composite
type value.

```
...
EXEC SQL DECLARE cur1 CURSOR FOR SELECT (compval).* FROM t4;
EXEC SQL OPEN cur1;

EXEC SQL WHENEVER NOT FOUND DO BREAK;

while (1)
{
/* Put all values in the SELECT list into one structure. */
EXEC SQL FETCH FROM cur1 INTO :compval;

printf("intval=%d, textval=%s\n", compval.intval, compval.textval.arr);
}
...
```

This way, composite types can be mapped into structures almost
seamlessly, even though ECPG does not understand the composite
type itself.

Finally, it is also possible to store composite type values in
their external string representation in host variables of
type `char[]` or `VARCHAR[]`.  But that
way, it is not easily possible to access the fields of the value
from the host program.

#### User-Defined Base Types

New user-defined base types are not directly supported by ECPG.
You can use the external string representation and host variables
of type `char[]` or `VARCHAR[]`, and this
solution is indeed appropriate and sufficient for many types.

Here is an example using the data type `complex` from
the example in [xtypes](#xtypes).  The external string
representation of that type is `(%f,%f)`,
which is defined in the
functions `complex_in()`
and `complex_out()`
in [xtypes](#xtypes).  The following example inserts the
complex type values `(1,1)`
and `(3,3)` into the
columns `a` and `b`, and select
them from the table after that.

```
EXEC SQL BEGIN DECLARE SECTION;
varchar a[64];
varchar b[64];
EXEC SQL END DECLARE SECTION;

EXEC SQL INSERT INTO test_complex VALUES ('(1,1)', '(3,3)');

EXEC SQL DECLARE cur1 CURSOR FOR SELECT a, b FROM test_complex;
EXEC SQL OPEN cur1;

EXEC SQL WHENEVER NOT FOUND DO BREAK;

while (1)
{
EXEC SQL FETCH FROM cur1 INTO :a, :b;
printf("a=%s, b=%s\n", a.arr, b.arr);
}

EXEC SQL CLOSE cur1;
```

This example shows following result:

```
a=(1,1), b=(3,3)
```

Another workaround is avoiding the direct use of the user-defined
types in ECPG and instead create a function or cast that converts
between the user-defined type and a primitive type that ECPG can
handle.  Note, however, that type casts, especially implicit
ones, should be introduced into the type system very carefully.

For example,

```
CREATE FUNCTION create_complex(r double, i double) RETURNS complex
LANGUAGE SQL
IMMUTABLE
AS $$ SELECT $1 * complex '(1,0')' + $2 * complex '(0,1)' $$;
```

After this definition, the following

```
EXEC SQL BEGIN DECLARE SECTION;
double a, b, c, d;
EXEC SQL END DECLARE SECTION;

a = 1;
b = 2;
c = 3;
d = 4;

EXEC SQL INSERT INTO test_complex VALUES (create_complex(:a, :b), create_complex(:c, :d));
```

has the same effect as

```
EXEC SQL INSERT INTO test_complex VALUES ('(1,2)', '(3,4)');
```

### Indicators

The examples above do not handle null values.  In fact, the
retrieval examples will raise an error if they fetch a null value
from the database.  To be able to pass null values to the database
or retrieve null values from the database, you need to append a
second host variable specification to each host variable that
contains data.  This second host variable is called the
*indicator* and contains a flag that tells
whether the datum is null, in which case the value of the real
host variable is ignored.  Here is an example that handles the
retrieval of null values correctly:

```
EXEC SQL BEGIN DECLARE SECTION;
VARCHAR val;
int val_ind;
EXEC SQL END DECLARE SECTION:

...

EXEC SQL SELECT b INTO :val :val_ind FROM test1;
```

The indicator variable `val_ind` will be zero if
the value was not null, and it will be negative if the value was
null.  (See [ecpg-oracle-compat](#ecpg-oracle-compat) to enable
Oracle-specific behavior.)

The indicator has another function: if the indicator value is
positive, it means that the value is not null, but it was
truncated when it was stored in the host variable.

If the argument `-r no_indicator` is passed to
the preprocessor `ecpg`, it works in
"no-indicator" mode. In no-indicator mode, if no
indicator variable is specified, null values are signaled (on
input and output) for character string types as empty string and
for integer types as the lowest possible value for type (for
example, `INT_MIN` for `int`).

## Dynamic SQL

In many cases, the particular SQL statements that an application
has to execute are known at the time the application is written.
In some cases, however, the SQL statements are composed at run time
or provided by an external source.  In these cases you cannot embed
the SQL statements directly into the C source code, but there is a
facility that allows you to call arbitrary SQL statements that you
provide in a string variable.

### Executing Statements without a Result Set

The simplest way to execute an arbitrary SQL statement is to use
the command `EXECUTE IMMEDIATE`.  For example:

```
EXEC SQL BEGIN DECLARE SECTION;
const char *stmt = "CREATE TABLE test1 (...);";
EXEC SQL END DECLARE SECTION;

EXEC SQL EXECUTE IMMEDIATE :stmt;
```

`EXECUTE IMMEDIATE` can be used for SQL
statements that do not return a result set (e.g.,
DDL, `INSERT`, `UPDATE`,
`DELETE`).  You cannot execute statements that
retrieve data (e.g., `SELECT`) this way.  The
next section describes how to do that.

### Executing a Statement with Input Parameters

A more powerful way to execute arbitrary SQL statements is to
prepare them once and execute the prepared statement as often as
you like.  It is also possible to prepare a generalized version of
a statement and then execute specific versions of it by
substituting parameters.  When preparing the statement, write
question marks where you want to substitute parameters later.  For
example:

```
EXEC SQL BEGIN DECLARE SECTION;
const char *stmt = "INSERT INTO test1 VALUES(?, ?);";
EXEC SQL END DECLARE SECTION;

EXEC SQL PREPARE mystmt FROM :stmt;
...
EXEC SQL EXECUTE mystmt USING 42, 'foobar';
```

When you don't need the prepared statement anymore, you should
deallocate it:

```
EXEC SQL DEALLOCATE PREPARE `name`;
```

### Executing a Statement with a Result Set

To execute an SQL statement with a single result row,
`EXECUTE` can be used.  To save the result, add
an `INTO` clause.

```

EXEC SQL BEGIN DECLARE SECTION;
const char *stmt = "SELECT a, b, c FROM test1 WHERE a > ?";
int v1, v2;
VARCHAR v3[50];
EXEC SQL END DECLARE SECTION;

EXEC SQL PREPARE mystmt FROM :stmt;
...
EXEC SQL EXECUTE mystmt INTO :v1, :v2, :v3 USING 37;

```

An `EXECUTE` command can have an
`INTO` clause, a `USING` clause,
both, or neither.

If a query is expected to return more than one result row, a
cursor should be used, as in the following example.
(See [ecpg-cursors](#ecpg-cursors) for more details about the
cursor.)

```
EXEC SQL BEGIN DECLARE SECTION;
char dbaname[128];
char datname[128];
char *stmt = "SELECT u.usename as dbaname, d.datname "
"  FROM pg_database d, pg_user u "
"  WHERE d.datdba = u.usesysid";
EXEC SQL END DECLARE SECTION;

EXEC SQL CONNECT TO testdb AS con1 USER testuser;
EXEC SQL SELECT pg_catalog.set_config('search_path', '', false); EXEC SQL COMMIT;

EXEC SQL PREPARE stmt1 FROM :stmt;

EXEC SQL DECLARE cursor1 CURSOR FOR stmt1;
EXEC SQL OPEN cursor1;

EXEC SQL WHENEVER NOT FOUND DO BREAK;

while (1)
{
EXEC SQL FETCH cursor1 INTO :dbaname,:datname;
printf("dbaname=%s, datname=%s\n", dbaname, datname);
}

EXEC SQL CLOSE cursor1;

EXEC SQL COMMIT;
EXEC SQL DISCONNECT ALL;
```

## pgtypes Library

The pgtypes library maps PostgreSQL database
types to C equivalents that can be used in C programs. It also offers
functions to do basic calculations with those types within C, i.e., without
the help of the PostgreSQL server. See the
following example:

```

EXEC SQL BEGIN DECLARE SECTION;
date date1;
timestamp ts1, tsout;
interval iv1;
char *out;
EXEC SQL END DECLARE SECTION;

PGTYPESdate_today(&date1);
EXEC SQL SELECT started, duration INTO :ts1, :iv1 FROM datetbl WHERE d=:date1;
PGTYPEStimestamp_add_interval(&ts1, &iv1, &tsout);
out = PGTYPEStimestamp_to_asc(&tsout);
printf("Started + duration: %s\n", out);
PGTYPESchar_free(out);

```

### Character Strings

Some functions such as `PGTYPESnumeric_to_asc` return
a pointer to a freshly allocated character string. These results should be
freed with `PGTYPESchar_free` instead of
`free`. (This is important only on Windows, where
memory allocation and release sometimes need to be done by the same
library.)

### The numeric Type

The numeric type offers to do calculations with arbitrary precision. See
[datatype-numeric](#datatype-numeric) for the equivalent type in the
PostgreSQL server. Because of the arbitrary precision this
variable needs to be able to expand and shrink dynamically. That's why you
can only create numeric variables on the heap, by means of the
`PGTYPESnumeric_new` and `PGTYPESnumeric_free`
functions. The decimal type, which is similar but limited in precision,
can be created on the stack as well as on the heap.

The following functions can be used to work with the numeric type:

**`PGTYPESnumeric_new`**
: Request a pointer to a newly allocated numeric variable.

```
numeric *PGTYPESnumeric_new(void);
```

**`PGTYPESnumeric_free`**
: Free a numeric type, release all of its memory.

```
void PGTYPESnumeric_free(numeric *var);
```

**`PGTYPESnumeric_from_asc`**
: Parse a numeric type from its string notation.

```
numeric *PGTYPESnumeric_from_asc(char *str, char **endptr);
```

Valid formats are for example:
`-2`,
`.794`,
`+3.44`,
`592.49E07` or
`-32.84e-4`.
If the value could be parsed successfully, a valid pointer is returned,
else the NULL pointer. At the moment ECPG always parses the complete
string and so it currently does not support to store the address of the
first invalid character in `*endptr`. You can safely
set `endptr` to NULL.

**`PGTYPESnumeric_to_asc`**
: Returns a pointer to a string allocated by `malloc` that contains the string
representation of the numeric type `num`.

```
char *PGTYPESnumeric_to_asc(numeric *num, int dscale);
```

The numeric value will be printed with `dscale` decimal
digits, with rounding applied if necessary.
The result must be freed with `PGTYPESchar_free()`.

**`PGTYPESnumeric_add`**
: Add two numeric variables into a third one.

```
int PGTYPESnumeric_add(numeric *var1, numeric *var2, numeric *result);
```

The function adds the variables `var1` and
`var2` into the result variable
`result`.
The function returns 0 on success and -1 in case of error.

**`PGTYPESnumeric_sub`**
: Subtract two numeric variables and return the result in a third one.

```
int PGTYPESnumeric_sub(numeric *var1, numeric *var2, numeric *result);
```

The function subtracts the variable `var2` from
the variable `var1`. The result of the operation is
stored in the variable `result`.
The function returns 0 on success and -1 in case of error.

**`PGTYPESnumeric_mul`**
: Multiply two numeric variables and return the result in a third one.

```
int PGTYPESnumeric_mul(numeric *var1, numeric *var2, numeric *result);
```

The function multiplies the variables `var1` and
`var2`. The result of the operation is stored in the
variable `result`.
The function returns 0 on success and -1 in case of error.

**`PGTYPESnumeric_div`**
: Divide two numeric variables and return the result in a third one.

```
int PGTYPESnumeric_div(numeric *var1, numeric *var2, numeric *result);
```

The function divides the variables `var1` by
`var2`. The result of the operation is stored in the
variable `result`.
The function returns 0 on success and -1 in case of error.

**`PGTYPESnumeric_cmp`**
: Compare two numeric variables.

```
int PGTYPESnumeric_cmp(numeric *var1, numeric *var2)
```

This function compares two numeric variables. In case of error,
`INT_MAX` is returned. On success, the function
returns one of three possible results:

- 1, if `var1` is bigger than `var2`
- -1, if `var1` is smaller than `var2`
- 0, if `var1` and `var2` are equal

**`PGTYPESnumeric_from_int`**
: Convert an int variable to a numeric variable.

```
int PGTYPESnumeric_from_int(signed int int_val, numeric *var);
```

This function accepts a variable of type signed int and stores it
in the numeric variable `var`. Upon success, 0 is returned and
-1 in case of a failure.

**`PGTYPESnumeric_from_long`**
: Convert a long int variable to a numeric variable.

```
int PGTYPESnumeric_from_long(signed long int long_val, numeric *var);
```

This function accepts a variable of type signed long int and stores it
in the numeric variable `var`. Upon success, 0 is returned and
-1 in case of a failure.

**`PGTYPESnumeric_copy`**
: Copy over one numeric variable into another one.

```
int PGTYPESnumeric_copy(numeric *src, numeric *dst);
```

This function copies over the value of the variable that
`src` points to into the variable that `dst`
points to. It returns 0 on success and -1 if an error occurs.

**`PGTYPESnumeric_from_double`**
: Convert a variable of type double to a numeric.

```
int  PGTYPESnumeric_from_double(double d, numeric *dst);
```

This function accepts a variable of type double and stores the result
in the variable that `dst` points to. It returns 0 on success
and -1 if an error occurs.

**`PGTYPESnumeric_to_double`**
: Convert a variable of type numeric to double.

```
int PGTYPESnumeric_to_double(numeric *nv, double *dp)
```

The function converts the numeric value from the variable that
`nv` points to into the double variable that `dp` points
to. It returns 0 on success and -1 if an error occurs, including
overflow. On overflow, the global variable `errno` will be set
to `PGTYPES_NUM_OVERFLOW` additionally.

**`PGTYPESnumeric_to_int`**
: Convert a variable of type numeric to int.

```
int PGTYPESnumeric_to_int(numeric *nv, int *ip);
```

The function converts the numeric value from the variable that
`nv` points to into the integer variable that `ip`
points to. It returns 0 on success and -1 if an error occurs, including
overflow. On overflow, the global variable `errno` will be set
to `PGTYPES_NUM_OVERFLOW` additionally.

**`PGTYPESnumeric_to_long`**
: Convert a variable of type numeric to long.

```
int PGTYPESnumeric_to_long(numeric *nv, long *lp);
```

The function converts the numeric value from the variable that
`nv` points to into the long integer variable that
`lp` points to. It returns 0 on success and -1 if an error
occurs, including overflow. On overflow, the global variable
`errno` will be set to `PGTYPES_NUM_OVERFLOW`
additionally.

**`PGTYPESnumeric_to_decimal`**
: Convert a variable of type numeric to decimal.

```
int PGTYPESnumeric_to_decimal(numeric *src, decimal *dst);
```

The function converts the numeric value from the variable that
`src` points to into the decimal variable that
`dst` points to. It returns 0 on success and -1 if an error
occurs, including overflow. On overflow, the global variable
`errno` will be set to `PGTYPES_NUM_OVERFLOW`
additionally.

**`PGTYPESnumeric_from_decimal`**
: Convert a variable of type decimal to numeric.

```
int PGTYPESnumeric_from_decimal(decimal *src, numeric *dst);
```

The function converts the decimal value from the variable that
`src` points to into the numeric variable that
`dst` points to. It returns 0 on success and -1 if an error
occurs. Since the decimal type is implemented as a limited version of
the numeric type, overflow cannot occur with this conversion.

### The date Type

The date type in C enables your programs to deal with data of the SQL type
date. See [datatype-datetime](#datatype-datetime) for the equivalent type in the
PostgreSQL server.

The following functions can be used to work with the date type:

**`PGTYPESdate_from_timestamp`**
: Extract the date part from a timestamp.

```
date PGTYPESdate_from_timestamp(timestamp dt);
```

The function receives a timestamp as its only argument and returns the
extracted date part from this timestamp.

**`PGTYPESdate_from_asc`**
: Parse a date from its textual representation.

```
date PGTYPESdate_from_asc(char *str, char **endptr);
```

The function receives a C char* string `str` and a pointer to
a C char* string `endptr`. At the moment ECPG always parses
the complete string and so it currently does not support to store the
address of the first invalid character in `*endptr`.
You can safely set `endptr` to NULL.

Note that the function always assumes MDY-formatted dates and there is
currently no variable to change that within ECPG.

[ecpg-pgtypesdate-from-asc-table](#ecpg-pgtypesdate-from-asc-table) shows the allowed input formats.

## Valid Input Formats for `PGTYPESdate_from_asc`

Input
Result

`January 8, 1999`
`January 8, 1999`

`1999-01-08`
`January 8, 1999`

`1/8/1999`
`January 8, 1999`

`1/18/1999`
`January 18, 1999`

`01/02/03`
`February 1, 2003`

`1999-Jan-08`
`January 8, 1999`

`Jan-08-1999`
`January 8, 1999`

`08-Jan-1999`
`January 8, 1999`

`99-Jan-08`
`January 8, 1999`

`08-Jan-99`
`January 8, 1999`

`08-Jan-06`
`January 8, 2006`

`Jan-08-99`
`January 8, 1999`

`19990108`
`ISO 8601; January 8, 1999`

`990108`
`ISO 8601; January 8, 1999`

`1999.008`
`year and day of year`

`J2451187`
`Julian day`

`January 8, 99 BC`
`year 99 before the Common Era`

**`PGTYPESdate_to_asc`**
: Return the textual representation of a date variable.

```
char *PGTYPESdate_to_asc(date dDate);
```

The function receives the date `dDate` as its only parameter.
It will output the date in the form `1999-01-18`, i.e., in the
`YYYY-MM-DD` format.
The result must be freed with `PGTYPESchar_free()`.

**`PGTYPESdate_julmdy`**
: Extract the values for the day, the month and the year from a variable
of type date.

```
void PGTYPESdate_julmdy(date d, int *mdy);
```

The function receives the date `d` and a pointer to an array
of 3 integer values `mdy`. The variable name indicates
the sequential order: `mdy[0]` will be set to contain the
number of the month, `mdy[1]` will be set to the value of the
day and `mdy[2]` will contain the year.

**`PGTYPESdate_mdyjul`**
: Create a date value from an array of 3 integers that specify the
day, the month and the year of the date.

```
void PGTYPESdate_mdyjul(int *mdy, date *jdate);
```

The function receives the array of the 3 integers (`mdy`) as
its first argument and as its second argument a pointer to a variable
of type date that should hold the result of the operation.

**`PGTYPESdate_dayofweek`**
: Return a number representing the day of the week for a date value.

```
int PGTYPESdate_dayofweek(date d);
```

The function receives the date variable `d` as its only
argument and returns an integer that indicates the day of the week for
this date.

- 0 - Sunday
- 1 - Monday
- 2 - Tuesday
- 3 - Wednesday
- 4 - Thursday
- 5 - Friday
- 6 - Saturday

**`PGTYPESdate_today`**
: Get the current date.

```
void PGTYPESdate_today(date *d);
```

The function receives a pointer to a date variable (`d`)
that it sets to the current date.

**`PGTYPESdate_fmt_asc`**
: Convert a variable of type date to its textual representation using a
format mask.

```
int PGTYPESdate_fmt_asc(date dDate, char *fmtstring, char *outbuf);
```

The function receives the date to convert (`dDate`), the
format mask (`fmtstring`) and the string that will hold the
textual representation of the date (`outbuf`).

On success, 0 is returned and a negative value if an error occurred.

The following literals are the field specifiers you can use:

- `dd` - The number of the day of the month.
- `mm` - The number of the month of the year.
- `yy` - The number of the year as a two digit number.
- `yyyy` - The number of the year as a four digit number.
- `ddd` - The name of the day (abbreviated).
- `mmm` - The name of the month (abbreviated).

All other characters are copied 1:1 to the output string.

[ecpg-pgtypesdate-fmt-asc-example-table](#ecpg-pgtypesdate-fmt-asc-example-table) indicates a few possible formats. This will give
you an idea of how to use this function. All output lines are based on
the same date: November 23, 1959.

## Valid Input Formats for `PGTYPESdate_fmt_asc`

Format
Result

`mmddyy`
`112359`

`ddmmyy`
`231159`

`yymmdd`
`591123`

`yy/mm/dd`
`59/11/23`

`yy mm dd`
`59 11 23`

`yy.mm.dd`
`59.11.23`

`.mm.yyyy.dd.`
`.11.1959.23.`

`mmm. dd, yyyy`
`Nov. 23, 1959`

`mmm dd yyyy`
`Nov 23 1959`

`yyyy dd mm`
`1959 23 11`

`ddd, mmm. dd, yyyy`
`Mon, Nov. 23, 1959`

`(ddd) mmm. dd, yyyy`
`(Mon) Nov. 23, 1959`

**`PGTYPESdate_defmt_asc`**
: Use a format mask to convert a C `char*` string to a value of type
date.

```
int PGTYPESdate_defmt_asc(date *d, char *fmt, char *str);
```

The function receives a pointer to the date value that should hold the
result of the operation (`d`), the format mask to use for
parsing the date (`fmt`) and the C char* string containing
the textual representation of the date (`str`). The textual
representation is expected to match the format mask. However you do not
need to have a 1:1 mapping of the string to the format mask. The
function only analyzes the sequential order and looks for the literals
`yy` or `yyyy` that indicate the
position of the year, `mm` to indicate the position of
the month and `dd` to indicate the position of the
day.

[ecpg-rdefmtdate-example-table](#ecpg-rdefmtdate-example-table) indicates a few possible formats. This will give
you an idea of how to use this function.

## Valid Input Formats for `rdefmtdate`

Format
String
Result

`ddmmyy`
`21-2-54`
`1954-02-21`

`ddmmyy`
`2-12-54`
`1954-12-02`

`ddmmyy`
`20111954`
`1954-11-20`

`ddmmyy`
`130464`
`1964-04-13`

`mmm.dd.yyyy`
`MAR-12-1967`
`1967-03-12`

`yy/mm/dd`
`1954, February 3rd`
`1954-02-03`

`mmm.dd.yyyy`
`041269`
`1969-04-12`

`yy/mm/dd`
`In the year 2525, in the month of July, mankind will be alive on the 28th day`
`2525-07-28`

`dd-mm-yy`
`I said on the 28th of July in the year 2525`
`2525-07-28`

`mmm.dd.yyyy`
`9/14/58`
`1958-09-14`

`yy/mm/dd`
`47/03/29`
`1947-03-29`

`mmm.dd.yyyy`
`oct 28 1975`
`1975-10-28`

`mmddyy`
`Nov 14th, 1985`
`1985-11-14`

### The timestamp Type

The timestamp type in C enables your programs to deal with data of the SQL
type timestamp. See [datatype-datetime](#datatype-datetime) for the equivalent
type in the PostgreSQL server.

The following functions can be used to work with the timestamp type:

**`PGTYPEStimestamp_from_asc`**
: Parse a timestamp from its textual representation into a timestamp
variable.

```
timestamp PGTYPEStimestamp_from_asc(char *str, char **endptr);
```

The function receives the string to parse (`str`) and a
pointer to a C char* (`endptr`).
At the moment ECPG always parses
the complete string and so it currently does not support to store the
address of the first invalid character in `*endptr`.
You can safely set `endptr` to NULL.

The function returns the parsed timestamp on success. On error,
`PGTYPESInvalidTimestamp` is returned and `errno` is
set to `PGTYPES_TS_BAD_TIMESTAMP`. See [pgtypesinvalidtimestamp](#pgtypesinvalidtimestamp) for important notes on this value.

In general, the input string can contain any combination of an allowed
date specification, a whitespace character and an allowed time
specification. Note that time zones are not supported by ECPG. It can
parse them but does not apply any calculation as the
PostgreSQL server does for example. Timezone
specifiers are silently discarded.

[ecpg-pgtypestimestamp-from-asc-example-table](#ecpg-pgtypestimestamp-from-asc-example-table) contains a few examples for input strings.

## Valid Input Formats for `PGTYPEStimestamp_from_asc`

Input
Result

`1999-01-08 04:05:06`
`1999-01-08 04:05:06`

`January 8 04:05:06 1999 PST`
`1999-01-08 04:05:06`

`1999-Jan-08 04:05:06.789-8`
`1999-01-08 04:05:06.789 (time zone specifier ignored)`

`J2451187 04:05-08:00`
`1999-01-08 04:05:00 (time zone specifier ignored)`

**`PGTYPEStimestamp_to_asc`**
: Converts a date to a C char* string.

```
char *PGTYPEStimestamp_to_asc(timestamp tstamp);
```

The function receives the timestamp `tstamp` as
its only argument and returns an allocated string that contains the
textual representation of the timestamp.
The result must be freed with `PGTYPESchar_free()`.

**`PGTYPEStimestamp_current`**
: Retrieve the current timestamp.

```
void PGTYPEStimestamp_current(timestamp *ts);
```

The function retrieves the current timestamp and saves it into the
timestamp variable that `ts` points to.

**`PGTYPEStimestamp_fmt_asc`**
: Convert a timestamp variable to a C char* using a format mask.

```
int PGTYPEStimestamp_fmt_asc(timestamp *ts, char *output, int str_len, char *fmtstr);
```

The function receives a pointer to the timestamp to convert as its
first argument (`ts`), a pointer to the output buffer
(`output`), the maximal length that has been allocated for
the output buffer (`str_len`) and the format mask to
use for the conversion (`fmtstr`).

Upon success, the function returns 0 and a negative value if an
error occurred.

You can use the following format specifiers for the format mask. The
format specifiers are the same ones that are used in the
`strftime` function in libc. Any
non-format specifier will be copied into the output buffer.

- `%A` - is replaced by national representation of
the full weekday name.
- `%a` - is replaced by national representation of
the abbreviated weekday name.
- `%B` - is replaced by national representation of
the full month name.
- `%b` - is replaced by national representation of
the abbreviated month name.
- `%C` - is replaced by (year / 100) as decimal
number; single digits are preceded by a zero.
- `%c` - is replaced by national representation of
time and date.
- `%D` - is equivalent to
`%m/%d/%y`.
- `%d` - is replaced by the day of the month as a
decimal number (01–31).
- `%E*` `%O*` -  POSIX locale
extensions. The sequences
`%Ec`
`%EC`
`%Ex`
`%EX`
`%Ey`
`%EY`
`%Od`
`%Oe`
`%OH`
`%OI`
`%Om`
`%OM`
`%OS`
`%Ou`
`%OU`
`%OV`
`%Ow`
`%OW`
`%Oy`
are supposed to provide alternative representations.

Additionally `%OB` implemented to represent
alternative months names (used standalone, without day mentioned).
- `%e` - is replaced by the day of month as a decimal
number (1–31); single digits are preceded by a blank.
- `%F` - is equivalent to `%Y-%m-%d`.
- `%G` - is replaced by a year as a decimal number
with century. This year is the one that contains the greater part of
the week (Monday as the first day of the week).
- `%g` - is replaced by the same year as in
`%G`, but as a decimal number without century
(00–99).
- `%H` - is replaced by the hour (24-hour clock) as a
decimal number (00–23).
- `%h` - the same as `%b`.
- `%I` - is replaced by the hour (12-hour clock) as a
decimal number (01–12).
- `%j` - is replaced by the day of the year as a
decimal number (001–366).
- `%k` - is replaced by the hour (24-hour clock) as a
decimal number (0–23); single digits are preceded by a blank.
- `%l` - is replaced by the hour (12-hour clock) as a
decimal number (1–12); single digits are preceded by a blank.
- `%M` - is replaced by the minute as a decimal
number (00–59).
- `%m` - is replaced by the month as a decimal number
(01–12).
- `%n` - is replaced by a newline.
- `%O*` - the same as `%E*`.
- `%p` - is replaced by national representation of
either "ante meridiem" or "post meridiem" as appropriate.
- `%R` - is equivalent to `%H:%M`.
- `%r` - is equivalent to `%I:%M:%S
%p`.
- `%S` - is replaced by the second as a decimal
number (00–60).
- `%s` - is replaced by the number of seconds since
the Epoch, UTC.
- `%T` - is equivalent to `%H:%M:%S`
- `%t` - is replaced by a tab.
- `%U` - is replaced by the week number of the year
(Sunday as the first day of the week) as a decimal number (00–53).
- `%u` - is replaced by the weekday (Monday as the
first day of the week) as a decimal number (1–7).
- `%V` - is replaced by the week number of the year
(Monday as the first day of the week) as a decimal number (01–53).
If the week containing January 1 has four or more days in the new
year, then it is week 1; otherwise it is the last week of the
previous year, and the next week is week 1.
- `%v` - is equivalent to
`%e-%b-%Y`.
- `%W` - is replaced by the week number of the year
(Monday as the first day of the week) as a decimal number (00–53).
- `%w` - is replaced by the weekday (Sunday as the
first day of the week) as a decimal number (0–6).
- `%X` - is replaced by national representation of
the time.
- `%x` - is replaced by national representation of
the date.
- `%Y` - is replaced by the year with century as a
decimal number.
- `%y` - is replaced by the year without century as a
decimal number (00–99).
- `%Z` - is replaced by the time zone name.
- `%z` - is replaced by the time zone offset from
UTC; a leading plus sign stands for east of UTC, a minus sign for
west of UTC, hours and minutes follow with two digits each and no
delimiter between them (common form for [RFC 822](https://datatracker.ietf.org/doc/html/rfc822) date headers).
- `%+` - is replaced by national representation of
the date and time.
- `%-*` - GNU libc extension. Do not do any padding
when performing numerical outputs.
- $_* - GNU libc extension.    Explicitly specify space for padding.
- `%0*` - GNU libc extension. Explicitly specify zero
for padding.
- `%%` - is replaced by `%`.

**`PGTYPEStimestamp_sub`**
: Subtract one timestamp from another one and save the result in a
variable of type interval.

```
int PGTYPEStimestamp_sub(timestamp *ts1, timestamp *ts2, interval *iv);
```

The function will subtract the timestamp variable that `ts2`
points to from the timestamp variable that `ts1` points to
and will store the result in the interval variable that `iv`
points to.

Upon success, the function returns 0 and a negative value if an
error occurred.

**`PGTYPEStimestamp_defmt_asc`**
: Parse a timestamp value from its textual representation using a
formatting mask.

```
int PGTYPEStimestamp_defmt_asc(char *str, char *fmt, timestamp *d);
```

The function receives the textual representation of a timestamp in the
variable `str` as well as the formatting mask to use in the
variable `fmt`. The result will be stored in the variable
that `d` points to.

If the formatting mask `fmt` is NULL, the function will fall
back to the default formatting mask which is `%Y-%m-%d
%H:%M:%S`.

This is the reverse function to [pgtypestimestampfmtasc](#pgtypestimestampfmtasc).  See the documentation there in
order to find out about the possible formatting mask entries.

**`PGTYPEStimestamp_add_interval`**
: Add an interval variable to a timestamp variable.

```
int PGTYPEStimestamp_add_interval(timestamp *tin, interval *span, timestamp *tout);
```

The function receives a pointer to a timestamp variable `tin`
and a pointer to an interval variable `span`. It adds the
interval to the timestamp and saves the resulting timestamp in the
variable that `tout` points to.

Upon success, the function returns 0 and a negative value if an
error occurred.

**`PGTYPEStimestamp_sub_interval`**
: Subtract an interval variable from a timestamp variable.

```
int PGTYPEStimestamp_sub_interval(timestamp *tin, interval *span, timestamp *tout);
```

The function subtracts the interval variable that `span`
points to from the timestamp variable that `tin` points to
and saves the result into the variable that `tout` points
to.

Upon success, the function returns 0 and a negative value if an
error occurred.

### The interval Type

The interval type in C enables your programs to deal with data of the SQL
type interval. See [datatype-datetime](#datatype-datetime) for the equivalent
type in the PostgreSQL server.

The following functions can be used to work with the interval type:

**`PGTYPESinterval_new`**
: Return a pointer to a newly allocated interval variable.

```
interval *PGTYPESinterval_new(void);
```

**`PGTYPESinterval_free`**
: Release the memory of a previously allocated interval variable.

```
void PGTYPESinterval_free(interval *intvl);
```

**`PGTYPESinterval_from_asc`**
: Parse an interval from its textual representation.

```
interval *PGTYPESinterval_from_asc(char *str, char **endptr);
```

The function parses the input string `str` and returns a
pointer to an allocated interval variable.
At the moment ECPG always parses
the complete string and so it currently does not support to store the
address of the first invalid character in `*endptr`.
You can safely set `endptr` to NULL.

**`PGTYPESinterval_to_asc`**
: Convert a variable of type interval to its textual representation.

```
char *PGTYPESinterval_to_asc(interval *span);
```

The function converts the interval variable that `span`
points to into a C char*. The output looks like this example:
`@ 1 day 12 hours 59 mins 10 secs`.
The result must be freed with `PGTYPESchar_free()`.

**`PGTYPESinterval_copy`**
: Copy a variable of type interval.

```
int PGTYPESinterval_copy(interval *intvlsrc, interval *intvldest);
```

The function copies the interval variable that `intvlsrc`
points to into the variable that `intvldest` points to. Note
that you need to allocate the memory for the destination variable
before.

### The decimal Type

The decimal type is similar to the numeric type. However it is limited to
a maximum precision of 30 significant digits. In contrast to the numeric
type which can be created on the heap only, the decimal type can be
created either on the stack or on the heap (by means of the functions
`PGTYPESdecimal_new` and
`PGTYPESdecimal_free`).
There are a lot of other functions that deal with the decimal type in the
Informix compatibility mode described in [ecpg-informix-compat](#ecpg-informix-compat).

The following functions can be used to work with the decimal type and are
not only contained in the `libcompat` library.

**`PGTYPESdecimal_new`**
: Request a pointer to a newly allocated decimal variable.

```
decimal *PGTYPESdecimal_new(void);
```

**`PGTYPESdecimal_free`**
: Free a decimal type, release all of its memory.

```
void PGTYPESdecimal_free(decimal *var);
```

### errno Values of pgtypeslib

**`PGTYPES_NUM_BAD_NUMERIC`**
: An argument should contain a numeric variable (or point to a numeric
variable) but in fact its in-memory representation was invalid.

**`PGTYPES_NUM_OVERFLOW`**
: An overflow occurred. Since the numeric type can deal with almost
arbitrary precision, converting a numeric variable into other types
might cause overflow.

**`PGTYPES_NUM_UNDERFLOW`**
: An underflow occurred. Since the numeric type can deal with almost
arbitrary precision, converting a numeric variable into other types
might cause underflow.

**`PGTYPES_NUM_DIVIDE_ZERO`**
: A division by zero has been attempted.

**`PGTYPES_DATE_BAD_DATE`**
: An invalid date string was passed to
the `PGTYPESdate_from_asc` function.

**`PGTYPES_DATE_ERR_EARGS`**
: Invalid arguments were passed to the
`PGTYPESdate_defmt_asc` function.

**`PGTYPES_DATE_ERR_ENOSHORTDATE`**
: An invalid token in the input string was found by the
`PGTYPESdate_defmt_asc` function.

**`PGTYPES_INTVL_BAD_INTERVAL`**
: An invalid interval string was passed to the
`PGTYPESinterval_from_asc` function, or an
invalid interval value was passed to the
`PGTYPESinterval_to_asc` function.

**`PGTYPES_DATE_ERR_ENOTDMY`**
: There was a mismatch in the day/month/year assignment in the
`PGTYPESdate_defmt_asc` function.

**`PGTYPES_DATE_BAD_DAY`**
: An invalid day of the month value was found by
the `PGTYPESdate_defmt_asc` function.

**`PGTYPES_DATE_BAD_MONTH`**
: An invalid month value was found by
the `PGTYPESdate_defmt_asc` function.

**`PGTYPES_TS_BAD_TIMESTAMP`**
: An invalid timestamp string pass passed to
the `PGTYPEStimestamp_from_asc` function,
or an invalid timestamp value was passed to
the `PGTYPEStimestamp_to_asc` function.

**`PGTYPES_TS_ERR_EINFTIME`**
: An infinite timestamp value was encountered in a context that
cannot handle it.

### Special Constants of pgtypeslib

**`PGTYPESInvalidTimestamp`**
: A value of type timestamp representing an invalid time stamp. This is
returned by the function `PGTYPEStimestamp_from_asc` on
parse error.
Note that due to the internal representation of the `timestamp` data type,
`PGTYPESInvalidTimestamp` is also a valid timestamp at
the same time. It is set to `1899-12-31 23:59:59`. In order
to detect errors, make sure that your application does not only test
for `PGTYPESInvalidTimestamp` but also for
`errno != 0` after each call to
`PGTYPEStimestamp_from_asc`.

## Using Descriptor Areas

An SQL descriptor area is a more sophisticated method for processing
the result of a `SELECT`, `FETCH` or
a `DESCRIBE` statement. An SQL descriptor area groups
the data of one row of data together with metadata items into one
data structure.  The metadata is particularly useful when executing
dynamic SQL statements, where the nature of the result columns might
not be known ahead of time. PostgreSQL provides two ways to use
Descriptor Areas: the named SQL Descriptor Areas and the C-structure
SQLDAs.

### Named SQL Descriptor Areas

A named SQL descriptor area consists of a header, which contains
information concerning the entire descriptor, and one or more item
descriptor areas, which basically each describe one column in the
result row.

Before you can use an SQL descriptor area, you need to allocate one:

```
EXEC SQL ALLOCATE DESCRIPTOR `identifier`;
```

The identifier serves as the "variable name" of the
descriptor area.
When you don't need the descriptor anymore, you should deallocate
it:

```
EXEC SQL DEALLOCATE DESCRIPTOR `identifier`;
```

To use a descriptor area, specify it as the storage target in an
`INTO` clause, instead of listing host variables:

```
EXEC SQL FETCH NEXT FROM mycursor INTO SQL DESCRIPTOR mydesc;
```

If the result set is empty, the Descriptor Area will still contain
the metadata from the query, i.e., the field names.

For not yet executed prepared queries, the `DESCRIBE`
statement can be used to get the metadata of the result set:

```
EXEC SQL BEGIN DECLARE SECTION;
char *sql_stmt = "SELECT * FROM table1";
EXEC SQL END DECLARE SECTION;

EXEC SQL PREPARE stmt1 FROM :sql_stmt;
EXEC SQL DESCRIBE stmt1 INTO SQL DESCRIPTOR mydesc;
```

Before PostgreSQL 9.0, the `SQL` keyword was optional,
so using `DESCRIPTOR` and `SQL DESCRIPTOR`
produced named SQL Descriptor Areas. Now it is mandatory, omitting
the `SQL` keyword produces SQLDA Descriptor Areas,
see [ecpg-sqlda-descriptors](#ecpg-sqlda-descriptors).

In `DESCRIBE` and `FETCH` statements,
the `INTO` and `USING` keywords can be
used to similarly: they produce the result set and the metadata in a
Descriptor Area.

Now how do you get the data out of the descriptor area?  You can
think of the descriptor area as a structure with named fields.  To
retrieve the value of a field from the header and store it into a
host variable, use the following command:

```
EXEC SQL GET DESCRIPTOR `name` :`hostvar` = `field`;
```

Currently, there is only one header field defined:
`COUNT`, which tells how many item
descriptor areas exist (that is, how many columns are contained in
the result).  The host variable needs to be of an integer type.  To
get a field from the item descriptor area, use the following
command:

```
EXEC SQL GET DESCRIPTOR `name` VALUE `num` :`hostvar` = `field`;
```

`num` can be a literal integer or a host
variable containing an integer. Possible fields are:

**`CARDINALITY` (integer)**
: number of rows in the result set

**`DATA`**
: actual data item (therefore, the data type of this field
depends on the query)

**`DATETIME_INTERVAL_CODE` (integer)**
: When `TYPE` is `9`,
`DATETIME_INTERVAL_CODE` will have a value of
`1` for `DATE`,
`2` for `TIME`,
`3` for `TIMESTAMP`,
`4` for `TIME WITH TIME ZONE`, or
`5` for `TIMESTAMP WITH TIME ZONE`.

**`DATETIME_INTERVAL_PRECISION` (integer)**
: not implemented

**`INDICATOR` (integer)**
: the indicator (indicating a null value or a value truncation)

**`KEY_MEMBER` (integer)**
: not implemented

**`LENGTH` (integer)**
: length of the datum in characters

**`NAME` (string)**
: name of the column

**`NULLABLE` (integer)**
: not implemented

**`OCTET_LENGTH` (integer)**
: length of the character representation of the datum in bytes

**`PRECISION` (integer)**
: precision (for type `numeric`)

**`RETURNED_LENGTH` (integer)**
: length of the datum in characters

**`RETURNED_OCTET_LENGTH` (integer)**
: length of the character representation of the datum in bytes

**`SCALE` (integer)**
: scale (for type `numeric`)

**`TYPE` (integer)**
: numeric code of the data type of the column

In `EXECUTE`, `DECLARE` and `OPEN`
statements, the effect of the `INTO` and `USING`
keywords are different. A Descriptor Area can also be manually built to
provide the input parameters for a query or a cursor and
`USING SQL DESCRIPTOR `name``
is the way to pass the input parameters into a parameterized query. The statement
to build a named SQL Descriptor Area is below:

```
EXEC SQL SET DESCRIPTOR `name` VALUE `num` `field` = :`hostvar`;
```

PostgreSQL supports retrieving more that one record in one `FETCH`
statement and storing the data in host variables in this case assumes that the
variable is an array. E.g.:

```
EXEC SQL BEGIN DECLARE SECTION;
int id[5];
EXEC SQL END DECLARE SECTION;

EXEC SQL FETCH 5 FROM mycursor INTO SQL DESCRIPTOR mydesc;

EXEC SQL GET DESCRIPTOR mydesc VALUE 1 :id = DATA;
```

### SQLDA Descriptor Areas

An SQLDA Descriptor Area is a C language structure which can be also used
to get the result set and the metadata of a query. One structure stores one
record from the result set.

```
EXEC SQL include sqlda.h;
sqlda_t         *mysqlda;

EXEC SQL FETCH 3 FROM mycursor INTO DESCRIPTOR mysqlda;
```

Note that the `SQL` keyword is omitted. The paragraphs about
the use cases of the `INTO` and `USING`
keywords in [ecpg-named-descriptors](#ecpg-named-descriptors) also apply here with an addition.
In a `DESCRIBE` statement the `DESCRIPTOR`
keyword can be completely omitted if the `INTO` keyword is used:

```
EXEC SQL DESCRIBE prepared_statement INTO mysqlda;
```

The general flow of a program that uses SQLDA is:

Prepare a query, and declare a cursor for it.
Declare an SQLDA for the result rows.
Declare an SQLDA for the input parameters, and initialize them (memory allocation, parameter settings).
Open a cursor with the input SQLDA.
Fetch rows from the cursor, and store them into an output SQLDA.
Read values from the output SQLDA into the host variables (with conversion if necessary).
Close the cursor.
Free the memory area allocated for the input SQLDA.

#### SQLDA Data Structure

SQLDA uses three data structure
types: `sqlda_t`, `sqlvar_t`,
and `struct sqlname`.

> **Tip:**

> PostgreSQL's SQLDA has a similar data structure to the one in
> IBM DB2 Universal Database, so some technical information on
> DB2's SQLDA could help understanding PostgreSQL's one better.
>

##### sqlda_t Structure

The structure type `sqlda_t` is the type of the
actual SQLDA.  It holds one record.  And two or
more `sqlda_t` structures can be connected in a
linked list with the pointer in
the `desc_next` field, thus
representing an ordered collection of rows.  So, when two or
more rows are fetched, the application can read them by
following the `desc_next` pointer in
each `sqlda_t` node.

The definition of `sqlda_t` is:

```
struct sqlda_struct
{
char            sqldaid[8];
long            sqldabc;
short           sqln;
short           sqld;
struct sqlda_struct *desc_next;
struct sqlvar_struct sqlvar[1];
};

typedef struct sqlda_struct sqlda_t;
```

The meaning of the fields is:

**`sqldaid`**
: It contains the literal string `"SQLDA  "`.

**`sqldabc`**
: It contains the size of the allocated space in bytes.

**`sqln`**
: It contains the number of input parameters for a parameterized query in
case it's passed into `OPEN`, `DECLARE` or
`EXECUTE` statements using the `USING`
keyword. In case it's used as output of `SELECT`,
`EXECUTE` or `FETCH` statements,
its value is the same as `sqld`
statement

**`sqld`**
: It contains the number of fields in a result set.

**`desc_next`**
: If the query returns more than one record, multiple linked
SQLDA structures are returned, and `desc_next` holds
a pointer to the next entry in the list.

**`sqlvar`**
: This is the array of the columns in the result set.

##### sqlvar_t Structure

The structure type `sqlvar_t` holds a column value
and metadata such as type and length. The definition of the type
is:

```
struct sqlvar_struct
{
short          sqltype;
short          sqllen;
char          *sqldata;
short         *sqlind;
struct sqlname sqlname;
};

typedef struct sqlvar_struct sqlvar_t;
```

The meaning of the fields is:

**`sqltype`**
: Contains the type identifier of the field. For values,
see `enum ECPGttype` in `ecpgtype.h`.

**`sqllen`**
: Contains the binary length of the field. e.g., 4 bytes for `ECPGt_int`.

**`sqldata`**
: Points to the data.  The format of the data is described
in [ecpg-variables-type-mapping](#ecpg-variables-type-mapping).

**`sqlind`**
: Points to the null indicator.  0 means not null, -1 means
null.

**`sqlname`**
: The name of the field.

##### struct sqlname Structure

A `struct sqlname` structure holds a column name.  It
is used as a member of the `sqlvar_t` structure.  The
definition of the structure is:

```
#define NAMEDATALEN 64

struct sqlname
{
short           length;
char            data[NAMEDATALEN];
};
```

The meaning of the fields is:

**`length`**
: Contains the length of the field name.

**`data`**
: Contains the actual field name.

#### Retrieving a Result Set Using an SQLDA

The general steps to retrieve a query result set through an
SQLDA are:

Declare an `sqlda_t` structure to receive the result set.
Execute `FETCH`/`EXECUTE`/`DESCRIBE` commands to process a query specifying the declared SQLDA.
Check the number of records in the result set by looking at `sqln`, a member of the `sqlda_t` structure.
Get the values of each column from `sqlvar[0]`, `sqlvar[1]`, etc., members of the `sqlda_t` structure.
Go to next row (`sqlda_t` structure) by following the `desc_next` pointer, a member of the `sqlda_t` structure.
Repeat above as you need.

Here is an example retrieving a result set through an SQLDA.

First, declare a `sqlda_t` structure to receive the result set.

```
sqlda_t *sqlda1;
```

Next, specify the SQLDA in a command.  This is
a `FETCH` command example.

```
EXEC SQL FETCH NEXT FROM cur1 INTO DESCRIPTOR sqlda1;
```

Run a loop following the linked list to retrieve the rows.

```
sqlda_t *cur_sqlda;

for (cur_sqlda = sqlda1;
cur_sqlda != NULL;
cur_sqlda = cur_sqlda->desc_next)
{
...
}
```

Inside the loop, run another loop to retrieve each column data
(`sqlvar_t` structure) of the row.

```
for (i = 0; i sqld; i++)
{
sqlvar_t v = cur_sqlda->sqlvar[i];
char *sqldata = v.sqldata;
short sqllen  = v.sqllen;
...
}
```

To get a column value, check the `sqltype` value,
a member of the `sqlvar_t` structure.  Then, switch
to an appropriate way, depending on the column type, to copy
data from the `sqlvar` field to a host variable.

```
char var_buf[1024];

switch (v.sqltype)
{
case ECPGt_char:
memset(&var_buf, 0, sizeof(var_buf));
memcpy(&var_buf, sqldata, (sizeof(var_buf) sqln = 2; /* number of input variables */
```

After memory allocation, store the parameter values into the
`sqlvar[]` array.  (This is same array used for
retrieving column values when the SQLDA is receiving a result
set.)  In this example, the input parameters
are `"postgres"`, having a string type,
and `1`, having an integer type.

```
sqlda2->sqlvar[0].sqltype = ECPGt_char;
sqlda2->sqlvar[0].sqldata = "postgres";
sqlda2->sqlvar[0].sqllen  = 8;

int intval = 1;
sqlda2->sqlvar[1].sqltype = ECPGt_int;
sqlda2->sqlvar[1].sqldata = (char *)
sqlda2->sqlvar[1].sqllen  = sizeof(intval);
```

By opening a cursor and specifying the SQLDA that was set up
beforehand, the input parameters are passed to the prepared
statement.

```
EXEC SQL OPEN cur1 USING DESCRIPTOR sqlda2;
```

Finally, after using input SQLDAs, the allocated memory space
must be freed explicitly, unlike SQLDAs used for receiving query
results.

```
free(sqlda2);
```

#### A Sample Application Using SQLDA

Here is an example program, which describes how to fetch access
statistics of the databases, specified by the input parameters,
from the system catalogs.

This application joins two system tables, pg_database and
pg_stat_database on the database OID, and also fetches and shows
the database statistics which are retrieved by two input
parameters (a database `postgres`, and OID `1`).

First, declare an SQLDA for input and an SQLDA for output.

```
EXEC SQL include sqlda.h;

sqlda_t *sqlda1; /* an output descriptor */
sqlda_t *sqlda2; /* an input descriptor  */
```

Next, connect to the database, prepare a statement, and declare a
cursor for the prepared statement.

```
int
main(void)
{
EXEC SQL BEGIN DECLARE SECTION;
char query[1024] = "SELECT d.oid,* FROM pg_database d, pg_stat_database s WHERE d.oid=s.datid AND ( d.datname=? OR d.oid=? )";
EXEC SQL END DECLARE SECTION;

EXEC SQL CONNECT TO testdb AS con1 USER testuser;
EXEC SQL SELECT pg_catalog.set_config('search_path', '', false); EXEC SQL COMMIT;

EXEC SQL PREPARE stmt1 FROM :query;
EXEC SQL DECLARE cur1 CURSOR FOR stmt1;
```

Next, put some values in the input SQLDA for the input
parameters.  Allocate memory for the input SQLDA, and set the
number of input parameters to `sqln`.  Store
type, value, and value length into `sqltype`,
`sqldata`, and `sqllen` in the
`sqlvar` structure.

```
/* Create SQLDA structure for input parameters. */
sqlda2 = (sqlda_t *) malloc(sizeof(sqlda_t) + sizeof(sqlvar_t));
memset(sqlda2, 0, sizeof(sqlda_t) + sizeof(sqlvar_t));
sqlda2->sqln = 2; /* number of input variables */

sqlda2->sqlvar[0].sqltype = ECPGt_char;
sqlda2->sqlvar[0].sqldata = "postgres";
sqlda2->sqlvar[0].sqllen  = 8;

intval = 1;
sqlda2->sqlvar[1].sqltype = ECPGt_int;
sqlda2->sqlvar[1].sqldata = (char *)
sqlda2->sqlvar[1].sqllen  = sizeof(intval);
```

After setting up the input SQLDA, open a cursor with the input
SQLDA.

```
/* Open a cursor with input parameters. */
EXEC SQL OPEN cur1 USING DESCRIPTOR sqlda2;
```

Fetch rows into the output SQLDA from the opened cursor.
(Generally, you have to call `FETCH` repeatedly
in the loop, to fetch all rows in the result set.)

```
while (1)
{
sqlda_t *cur_sqlda;

/* Assign descriptor to the cursor  */
EXEC SQL FETCH NEXT FROM cur1 INTO DESCRIPTOR sqlda1;
```

Next, retrieve the fetched records from the SQLDA, by following
the linked list of the `sqlda_t` structure.

```
for (cur_sqlda = sqlda1 ;
cur_sqlda != NULL ;
cur_sqlda = cur_sqlda->desc_next)
{
...
```

Read each columns in the first record.  The number of columns is
stored in `sqld`, the actual data of the first
column is stored in `sqlvar[0]`, both members of
the `sqlda_t` structure.

```
/* Print every column in a row. */
for (i = 0; i sqld; i++)
{
sqlvar_t v = sqlda1->sqlvar[i];
char *sqldata = v.sqldata;
short sqllen  = v.sqllen;

strncpy(name_buf, v.sqlname.data, v.sqlname.length);
name_buf[v.sqlname.length] = '\0';
```

Now, the column data is stored in the variable `v`.
Copy every datum into host variables, looking
at `v.sqltype` for the type of the column.

```
switch (v.sqltype) {
int intval;
double doubleval;
unsigned long long int longlongval;

case ECPGt_char:
memset(&var_buf, 0, sizeof(var_buf));
memcpy(&var_buf, sqldata, (sizeof(var_buf)
#include
#include
#include
#include

EXEC SQL include sqlda.h;

sqlda_t *sqlda1; /* descriptor for output */
sqlda_t *sqlda2; /* descriptor for input */

EXEC SQL WHENEVER NOT FOUND DO BREAK;
EXEC SQL WHENEVER SQLERROR STOP;

int
main(void)
{
EXEC SQL BEGIN DECLARE SECTION;
char query[1024] = "SELECT d.oid,* FROM pg_database d, pg_stat_database s WHERE d.oid=s.datid AND ( d.datname=? OR d.oid=? )";

int intval;
unsigned long long int longlongval;
EXEC SQL END DECLARE SECTION;

EXEC SQL CONNECT TO uptimedb AS con1 USER uptime;
EXEC SQL SELECT pg_catalog.set_config('search_path', '', false); EXEC SQL COMMIT;

EXEC SQL PREPARE stmt1 FROM :query;
EXEC SQL DECLARE cur1 CURSOR FOR stmt1;

/* Create an SQLDA structure for an input parameter */
sqlda2 = (sqlda_t *)malloc(sizeof(sqlda_t) + sizeof(sqlvar_t));
memset(sqlda2, 0, sizeof(sqlda_t) + sizeof(sqlvar_t));
sqlda2->sqln = 2; /* a number of input variables */

sqlda2->sqlvar[0].sqltype = ECPGt_char;
sqlda2->sqlvar[0].sqldata = "postgres";
sqlda2->sqlvar[0].sqllen  = 8;

intval = 1;
sqlda2->sqlvar[1].sqltype = ECPGt_int;
sqlda2->sqlvar[1].sqldata = (char *)
sqlda2->sqlvar[1].sqllen  = sizeof(intval);

/* Open a cursor with input parameters. */
EXEC SQL OPEN cur1 USING DESCRIPTOR sqlda2;

while (1)
{
sqlda_t *cur_sqlda;

/* Assign descriptor to the cursor  */
EXEC SQL FETCH NEXT FROM cur1 INTO DESCRIPTOR sqlda1;

for (cur_sqlda = sqlda1 ;
cur_sqlda != NULL ;
cur_sqlda = cur_sqlda->desc_next)
{
int i;
char name_buf[1024];
char var_buf[1024];

/* Print every column in a row. */
for (i=0 ; isqld ; i++)
{
sqlvar_t v = cur_sqlda->sqlvar[i];
char *sqldata = v.sqldata;
short sqllen  = v.sqllen;

strncpy(name_buf, v.sqlname.data, v.sqlname.length);
name_buf[v.sqlname.length] = '\0';

switch (v.sqltype)
{
case ECPGt_char:
memset(&var_buf, 0, sizeof(var_buf));
memcpy(&var_buf, sqldata, (sizeof(var_buf);
EXEC SQL INCLUDE "`filename`";
```

The embedded SQL preprocessor will look for a file named
``filename`.h`,
preprocess it, and include it in the resulting C output.  Thus,
embedded SQL statements in the included file are handled correctly.

The `ecpg` preprocessor will search a file at
several directories in following order:

But when `EXEC SQL INCLUDE
"`filename`"` is used, only the
current directory is searched.

In each directory, the preprocessor will first look for the file
name as given, and if not found will append `.h`
to the file name and try again (unless the specified file name
already has that suffix).

Note that `EXEC SQL INCLUDE` is *not* the same as:

```
#include
```

because this file would not be subject to SQL command preprocessing.
Naturally, you can continue to use the C
`#include` directive to include other header
files.

> **Note:**

> The include file name is case-sensitive, even though the rest of
> the `EXEC SQL INCLUDE` command follows the normal
> SQL case-sensitivity rules.
>

### The define and undef Directives

Similar to the directive `#define` that is known from C,
embedded SQL has a similar concept:

```
EXEC SQL DEFINE `name`;
EXEC SQL DEFINE `name` `value`;
```

So you can define a name:

```
EXEC SQL DEFINE HAVE_FEATURE;
```

And you can also define constants:

```
EXEC SQL DEFINE MYNUMBER 12;
EXEC SQL DEFINE MYSTRING 'abc';
```

Use `undef` to remove a previous definition:

```
EXEC SQL UNDEF MYNUMBER;
```

Of course you can continue to use the C versions `#define`
and `#undef` in your embedded SQL program. The difference
is where your defined values get evaluated. If you use `EXEC SQL
DEFINE` then the `ecpg` preprocessor evaluates the defines and substitutes
the values. For example if you write:

```
EXEC SQL DEFINE MYNUMBER 12;
...
EXEC SQL UPDATE Tbl SET col = MYNUMBER;
```

then `ecpg` will already do the substitution and your C compiler will never
see any name or identifier `MYNUMBER`. Note that you cannot use
`#define` for a constant that you are going to use in an
embedded SQL query because in this case the embedded SQL precompiler is not
able to see this declaration.

If multiple input files are named on the `ecpg`
preprocessor's command line, the effects of `EXEC SQL
DEFINE` and `EXEC SQL UNDEF` do not carry
across files: each file starts with only the symbols defined
by `-D` switches on the command line.

### ifdef, ifndef, elif, else, and endif Directives

You can use the following directives to compile code sections conditionally:

**`EXEC SQL ifdef `name`;`**
: Checks a `name` and processes subsequent lines if
`name` has been defined via `EXEC SQL define
`name``.

**`EXEC SQL ifndef `name`;`**
: Checks a `name` and processes subsequent lines if
`name` has *not* been defined via
`EXEC SQL define `name``.

**`EXEC SQL elif `name`;`**
: Begins an optional alternative section after an
`EXEC SQL ifdef `name`` or
`EXEC SQL ifndef `name``
directive.  Any number of `elif` sections can appear.
Lines following an `elif` will be processed
if `name` has been
defined *and* no previous section of the same
`ifdef`/`ifndef`...`endif`
construct has been processed.

**`EXEC SQL else;`**
: Begins an optional, final alternative section after an
`EXEC SQL ifdef `name`` or
`EXEC SQL ifndef `name``
directive.  Subsequent lines will be processed if no previous section
of the same
`ifdef`/`ifndef`...`endif`
construct has been processed.

**`EXEC SQL endif;`**
: Ends an
`ifdef`/`ifndef`...`endif`
construct.  Subsequent lines are processed normally.

`ifdef`/`ifndef`...`endif`
constructs can be nested, up to 127 levels deep.

This example will compile exactly one of the three `SET
TIMEZONE` commands:

```
EXEC SQL ifdef TZVAR;
EXEC SQL SET TIMEZONE TO TZVAR;
EXEC SQL elif TZNAME;
EXEC SQL SET TIMEZONE TO TZNAME;
EXEC SQL else;
EXEC SQL SET TIMEZONE TO 'GMT';
EXEC SQL endif;
```

## Processing Embedded SQL Programs

Now that you have an idea how to form embedded SQL C programs, you
probably want to know how to compile them.  Before compiling you
run the file through the embedded SQL
C preprocessor, which converts the
SQL statements you used to special function
calls.  After compiling, you must link with a special library that
contains the needed functions. These functions fetch information
from the arguments, perform the SQL command using
the libpq interface, and put the result
in the arguments specified for output.

The preprocessor program is called `ecpg` and is
included in a normal PostgreSQL installation.
Embedded SQL programs are typically named with an extension
`.pgc`.  If you have a program file called
`prog1.pgc`, you can preprocess it by simply
calling:

```
ecpg prog1.pgc
```

This will create a file called `prog1.c`.  If
your input files do not follow the suggested naming pattern, you
can specify the output file explicitly using the
`-o` option.

The preprocessed file can be compiled normally, for example:

```
cc -c prog1.c
```

The generated C source files include header files from the
PostgreSQL installation, so if you installed
PostgreSQL in a location that is not searched by
default, you have to add an option such as
`-I/usr/local/pgsql/include` to the compilation
command line.

To link an embedded SQL program, you need to include the
`libecpg` library, like so:

```
cc -o myprog prog1.o prog2.o ... -lecpg
```

Again, you might have to add an option like
`-L/usr/local/pgsql/lib` to that command line.

You can
use `pg_config`
or `pkg-config` with package name `libecpg` to
get the paths for your installation.

If you manage the build process of a larger project using
make, it might be convenient to include
the following implicit rule to your makefiles:

```
ECPG = ecpg

%.c: %.pgc
$(ECPG) $ **Note:**
> On Windows, if the ecpg libraries and an application are
> compiled with different flags, this function call will crash the
> application because the internal representation of the
> `FILE` pointers differ.  Specifically,
> multithreaded/single-threaded, release/debug, and static/dynamic
> flags should be the same for the library and all applications using
> that library.
>
- `ECPGget_PGconn(const char *`connection_name`)
` returns the library database connection handle identified by the given name.
If `connection_name` is set to `NULL`, the current
connection handle is returned. If no connection handle can be identified, the function returns
`NULL`. The returned connection handle can be used to call any other functions
from libpq, if necessary.

> **Note:**
> It is a bad idea to manipulate database connection handles made from ecpg directly
> with libpq routines.
>
- `ECPGtransactionStatus(const char *`connection_name`)`
returns the current transaction status of the given connection identified by `connection_name`.
See [libpq-status](#libpq-status) and libpq's [libpq-PQtransactionStatus](#libpq-PQtransactionStatus) for details about the returned status codes.
- `ECPGstatus(int `lineno`,
const char* `connection_name`)`
returns true if you are connected to a database and false if not.
`connection_name` can be `NULL`
if a single connection is being used.

## Large Objects

Large objects are not directly supported by ECPG, but ECPG
application can manipulate large objects through the libpq large
object functions, obtaining the necessary `PGconn`
object by calling the `ECPGget_PGconn()`
function.  (However, use of
the `ECPGget_PGconn()` function and touching
`PGconn` objects directly should be done very carefully
and ideally not mixed with other ECPG database access calls.)

For more details about the `ECPGget_PGconn()`, see
[ecpg-library](#ecpg-library).  For information about the large
object function interface, see [largeobjects](#largeobjects).

Large object functions have to be called in a transaction block, so
when autocommit is off, `BEGIN` commands have to
be issued explicitly.

[ecpg-lo-example](#ecpg-lo-example) shows an example program that
illustrates how to create, write, and read a large object in an
ECPG application.

## ECPG Program Accessing Large Objects

```

#include
#include
#include
#include

EXEC SQL WHENEVER SQLERROR STOP;

int
main(void)
{
PGconn     *conn;
Oid         loid;
int         fd;
char        buf[256];
int         buflen = 256;
char        buf2[256];
int         rc;

memset(buf, 1, buflen);

EXEC SQL CONNECT TO testdb AS con1;
EXEC SQL SELECT pg_catalog.set_config('search_path', '', false); EXEC SQL COMMIT;

conn = ECPGget_PGconn("con1");
printf("conn = %p\n", conn);

/* create */
loid = lo_create(conn, 0);
if (loid test();
return 0;
}
```

To build the application, proceed as follows.  Convert
`test_mod.pgc` into `test_mod.c` by
running `ecpg`, and generate
`test_mod.o` by compiling
`test_mod.c` with the C compiler:

```
ecpg -o test_mod.c test_mod.pgc
cc -c test_mod.c -o test_mod.o
```

Next, generate `test_cpp.o` by compiling
`test_cpp.cpp` with the C++ compiler:

```
c++ -c test_cpp.cpp -o test_cpp.o
```

Finally, link these object files, `test_cpp.o`
and `test_mod.o`, into one executable, using the C++
compiler driver:

```
c++ test_cpp.o test_mod.o -lecpg -o test_cpp
```

## Embedded SQL Commands

This section describes all SQL commands that are specific to
embedded SQL.  Also refer to the SQL commands listed
in [sql-commands](#sql-commands), which can also be used in
embedded SQL, unless stated otherwise.

ALLOCATE DESCRIPTOR
allocate an SQL descriptor area

```
ALLOCATE DESCRIPTOR `name`
```

## Description

`ALLOCATE DESCRIPTOR` allocates a new named SQL
descriptor area, which can be used to exchange data between the
PostgreSQL server and the host program.

Descriptor areas should be freed after use using
the `DEALLOCATE DESCRIPTOR` command.

## Parameters

**`name`**
: A name of SQL descriptor, case sensitive.  This can be an SQL
identifier or a host variable.

## Examples

```
EXEC SQL ALLOCATE DESCRIPTOR mydesc;
```

## Compatibility

`ALLOCATE DESCRIPTOR` is specified in the SQL
standard.

## See Also

CONNECT
establish a database connection

```
CONNECT TO `connection_target` [ AS `connection_name` ] [ USER `connection_user` ]
CONNECT TO DEFAULT
CONNECT `connection_user`
DATABASE `connection_target`
```

## Description

The `CONNECT` command establishes a connection
between the client and the PostgreSQL server.

## Parameters

**`connection_target`**
: `connection_target`
specifies the target server of the connection on one of
several forms.

[ `database_name` ] [ `@``host` ] [ `:``port` ]

Connect over TCP/IP

**`unix:postgresql://``host` [ `:``port` ] `/` [ `database_name` ] [ `?``connection_option` ]**
: Connect over Unix-domain sockets

**`tcp:postgresql://``host` [ `:``port` ] `/` [ `database_name` ] [ `?``connection_option` ]**
: Connect over TCP/IP

**SQL string constant**
: containing a value in one of the above forms

**host variable**
: host variable of type `char[]`
or `VARCHAR[]` containing a value in one of the
above forms

`connection_name`

An optional identifier for the connection, so that it can be
referred to in other commands.  This can be an SQL identifier
or a host variable.

`connection_user`

The user name for the database connection.

This parameter can also specify user name and password, using one the forms
``user_name`/`password``,
``user_name` IDENTIFIED BY `password``, or
``user_name` USING `password``.

User name and password can be SQL identifiers, string
constants, or host variables.

`DEFAULT`

Use all default connection parameters, as defined by libpq.

## Examples

Here a several variants for specifying connection parameters:

```
EXEC SQL CONNECT TO "connectdb" AS main;
EXEC SQL CONNECT TO "connectdb" AS second;
EXEC SQL CONNECT TO "unix:postgresql://200.46.204.71/connectdb" AS main USER connectuser;
EXEC SQL CONNECT TO "unix:postgresql://localhost/connectdb" AS main USER connectuser;
EXEC SQL CONNECT TO 'connectdb' AS main;
EXEC SQL CONNECT TO 'unix:postgresql://localhost/connectdb' AS main USER :user;
EXEC SQL CONNECT TO :db AS :id;
EXEC SQL CONNECT TO :db USER connectuser USING :pw;
EXEC SQL CONNECT TO @localhost AS main USER connectdb;
EXEC SQL CONNECT TO REGRESSDB1 as main;
EXEC SQL CONNECT TO AS main USER connectdb;
EXEC SQL CONNECT TO connectdb AS :id;
EXEC SQL CONNECT TO connectdb AS main USER connectuser/connectdb;
EXEC SQL CONNECT TO connectdb AS main;
EXEC SQL CONNECT TO connectdb@localhost AS main;
EXEC SQL CONNECT TO tcp:postgresql://localhost/ USER connectdb;
EXEC SQL CONNECT TO tcp:postgresql://localhost/connectdb USER connectuser IDENTIFIED BY connectpw;
EXEC SQL CONNECT TO tcp:postgresql://localhost:20/connectdb USER connectuser IDENTIFIED BY connectpw;
EXEC SQL CONNECT TO unix:postgresql://localhost/ AS main USER connectdb;
EXEC SQL CONNECT TO unix:postgresql://localhost/connectdb AS main USER connectuser;
EXEC SQL CONNECT TO unix:postgresql://localhost/connectdb USER connectuser IDENTIFIED BY "connectpw";
EXEC SQL CONNECT TO unix:postgresql://localhost/connectdb USER connectuser USING "connectpw";
EXEC SQL CONNECT TO unix:postgresql://localhost/connectdb?connect_timeout=14 USER connectuser;
```

Here is an example program that illustrates the use of host
variables to specify connection parameters:

```
int
main(void)
{
EXEC SQL BEGIN DECLARE SECTION;
char *dbname     = "testdb";    /* database name */
char *user       = "testuser";  /* connection user name */
char *connection = "tcp:postgresql://localhost:5432/testdb";
/* connection string */
char ver[256];                  /* buffer to store the version string */
EXEC SQL END DECLARE SECTION;

ECPGdebug(1, stderr);

EXEC SQL CONNECT TO :dbname USER :user;
EXEC SQL SELECT pg_catalog.set_config('search_path', '', false); EXEC SQL COMMIT;
EXEC SQL SELECT version() INTO :ver;
EXEC SQL DISCONNECT;

printf("version: %s\n", ver);

EXEC SQL CONNECT TO :connection USER :user;
EXEC SQL SELECT pg_catalog.set_config('search_path', '', false); EXEC SQL COMMIT;
EXEC SQL SELECT version() INTO :ver;
EXEC SQL DISCONNECT;

printf("version: %s\n", ver);

return 0;
}
```

## Compatibility

`CONNECT` is specified in the SQL standard, but
the format of the connection parameters is
implementation-specific.

## See Also

DEALLOCATE DESCRIPTOR
deallocate an SQL descriptor area

```
DEALLOCATE DESCRIPTOR `name`
```

## Description

`DEALLOCATE DESCRIPTOR` deallocates a named SQL
descriptor area.

## Parameters

**`name`**
: The name of the descriptor which is going to be deallocated.
It is case sensitive.  This can be an SQL identifier or a host
variable.

## Examples

```
EXEC SQL DEALLOCATE DESCRIPTOR mydesc;
```

## Compatibility

`DEALLOCATE DESCRIPTOR` is specified in the SQL
standard.

## See Also

DECLARE
define a cursor

```
DECLARE `cursor_name` [ BINARY ] [ ASENSITIVE | INSENSITIVE ] [ [ NO ] SCROLL ] CURSOR [ { WITH | WITHOUT } HOLD ] FOR `prepared_name`
DECLARE `cursor_name` [ BINARY ] [ ASENSITIVE | INSENSITIVE ] [ [ NO ] SCROLL ] CURSOR [ { WITH | WITHOUT } HOLD ] FOR `query`
```

## Description

`DECLARE` declares a cursor for iterating over
the result set of a prepared statement.  This command has
slightly different semantics from the direct SQL
command `DECLARE`: Whereas the latter executes a
query and prepares the result set for retrieval, this embedded
SQL command merely declares a name as a "loop
variable" for iterating over the result set of a query;
the actual execution happens when the cursor is opened with
the `OPEN` command.

## Parameters

**`cursor_name`**
: A cursor name, case sensitive.  This can be an SQL identifier
or a host variable.

**`prepared_name`**
: The name of a prepared query, either as an SQL identifier or a
host variable.

**`query`**
: A [sql-select](#sql-select) or
[sql-values](#sql-values) command which will provide the
rows to be returned by the cursor.

For the meaning of the cursor options,
see [sql-declare](#sql-declare).

## Examples

Examples declaring a cursor for a query:

```
EXEC SQL DECLARE C CURSOR FOR SELECT * FROM My_Table;
EXEC SQL DECLARE C CURSOR FOR SELECT Item1 FROM T;
EXEC SQL DECLARE cur1 CURSOR FOR SELECT version();
```

An example declaring a cursor for a prepared statement:

```
EXEC SQL PREPARE stmt1 AS SELECT version();
EXEC SQL DECLARE cur1 CURSOR FOR stmt1;
```

## Compatibility

`DECLARE` is specified in the SQL standard.

## See Also

DECLARE STATEMENT
declare SQL statement identifier

```
EXEC SQL [ AT `connection_name` ] DECLARE `statement_name` STATEMENT
```

## Description

`DECLARE STATEMENT` declares an SQL statement identifier.
SQL statement identifier can be associated with the connection.
When the identifier is used by dynamic SQL statements, the statements
are executed using the associated connection.
The namespace of the declaration is the precompile unit, and multiple
declarations to the same SQL statement identifier are not allowed.
Note that if the precompiler runs in Informix compatibility mode and
some SQL statement is declared, "database" can not be used as a cursor
name.

## Parameters

**`connection_name`**
: A database connection name established by the `CONNECT` command.

AT clause can be omitted, but such statement has no meaning.

**`statement_name`**
: The name of an SQL statement identifier, either as an SQL identifier or a host variable.

## Notes

This association is valid only if the declaration is physically placed on top of a dynamic statement.

## Examples

```
EXEC SQL CONNECT TO postgres AS con1;
EXEC SQL AT con1 DECLARE sql_stmt STATEMENT;
EXEC SQL DECLARE cursor_name CURSOR FOR sql_stmt;
EXEC SQL PREPARE sql_stmt FROM :dyn_string;
EXEC SQL OPEN cursor_name;
EXEC SQL FETCH cursor_name INTO :column1;
EXEC SQL CLOSE cursor_name;
```

## Compatibility

`DECLARE STATEMENT` is an extension of the SQL standard,
but can be used in famous DBMSs.

## See Also

DESCRIBE
obtain information about a prepared statement or result set

```
DESCRIBE [ OUTPUT ] `prepared_name` USING [ SQL ] DESCRIPTOR `descriptor_name`
DESCRIBE [ OUTPUT ] `prepared_name` INTO [ SQL ] DESCRIPTOR `descriptor_name`
DESCRIBE [ OUTPUT ] `prepared_name` INTO `sqlda_name`
```

## Description

`DESCRIBE` retrieves metadata information about
the result columns contained in a prepared statement, without
actually fetching a row.

## Parameters

**`prepared_name`**
: The name of a prepared statement.  This can be an SQL
identifier or a host variable.

**`descriptor_name`**
: A descriptor name. It is case sensitive.  It can be an SQL
identifier or a host variable.

**`sqlda_name`**
: The name of an SQLDA variable.

## Examples

```
EXEC SQL ALLOCATE DESCRIPTOR mydesc;
EXEC SQL PREPARE stmt1 FROM :sql_stmt;
EXEC SQL DESCRIBE stmt1 INTO SQL DESCRIPTOR mydesc;
EXEC SQL GET DESCRIPTOR mydesc VALUE 1 :charvar = NAME;
EXEC SQL DEALLOCATE DESCRIPTOR mydesc;
```

## Compatibility

`DESCRIBE` is specified in the SQL standard.

## See Also

DISCONNECT
terminate a database connection

```
DISCONNECT `connection_name`
DISCONNECT [ CURRENT ]
DISCONNECT ALL
```

## Description

`DISCONNECT` closes a connection (or all
connections) to the database.

## Parameters

**`connection_name`**
: A database connection name established by
the `CONNECT` command.

**`CURRENT`**
: Close the "current" connection, which is either
the most recently opened connection, or the connection set by
the `SET CONNECTION` command.  This is also
the default if no argument is given to
the `DISCONNECT` command.

**`ALL`**
: Close all open connections.

## Examples

```
int
main(void)
{
EXEC SQL CONNECT TO testdb AS con1 USER testuser;
EXEC SQL CONNECT TO testdb AS con2 USER testuser;
EXEC SQL CONNECT TO testdb AS con3 USER testuser;

EXEC SQL DISCONNECT CURRENT;  /* close con3          */
EXEC SQL DISCONNECT ALL;      /* close con2 and con1 */

return 0;
}
```

## Compatibility

`DISCONNECT` is specified in the SQL standard.

## See Also

EXECUTE IMMEDIATE
dynamically prepare and execute a statement

```
EXECUTE IMMEDIATE `string`
```

## Description

`EXECUTE IMMEDIATE` immediately prepares and
executes a dynamically specified SQL statement, without
retrieving result rows.

## Parameters

**`string`**
: A literal string or a host variable containing the SQL
statement to be executed.

## Notes

In typical usage, the `string` is a host
variable reference to a string containing a dynamically-constructed
SQL statement.  The case of a literal string is not very useful;
you might as well just write the SQL statement directly, without
the extra typing of `EXECUTE IMMEDIATE`.

If you do use a literal string, keep in mind that any double quotes
you might wish to include in the SQL statement must be written as
octal escapes (`\042`) not the usual C
idiom `\"`.  This is because the string is inside
an `EXEC SQL` section, so the ECPG lexer parses it
according to SQL rules not C rules.  Any embedded backslashes will
later be handled according to C rules; but `\"`
causes an immediate syntax error because it is seen as ending the
literal.

## Examples

Here is an example that executes an `INSERT`
statement using `EXECUTE IMMEDIATE` and a host
variable named `command`:

```
sprintf(command, "INSERT INTO test (name, amount, letter) VALUES ('db: ''r1''', 1, 'f')");
EXEC SQL EXECUTE IMMEDIATE :command;
```

## Compatibility

`EXECUTE IMMEDIATE` is specified in the SQL standard.

GET DESCRIPTOR
get information from an SQL descriptor area

```
GET DESCRIPTOR `descriptor_name` `:cvariable` = `descriptor_header_item` [, ... ]
GET DESCRIPTOR `descriptor_name` VALUE `column_number` `:cvariable` = `descriptor_item` [, ... ]
```

## Description

`GET DESCRIPTOR` retrieves information about a
query result set from an SQL descriptor area and stores it into
host variables.  A descriptor area is typically populated
using `FETCH` or `SELECT`
before using this command to transfer the information into host
language variables.

This command has two forms: The first form retrieves
descriptor "header" items, which apply to the result
set in its entirety.  One example is the row count.  The second
form, which requires the column number as additional parameter,
retrieves information about a particular column.  Examples are
the column name and the actual column value.

## Parameters

**`descriptor_name`**
: A descriptor name.

**`descriptor_header_item`**
: A token identifying which header information item to retrieve.
Only `COUNT`, to get the number of columns in the
result set, is currently supported.

**`column_number`**
: The number of the column about which information is to be
retrieved.  The count starts at 1.

**`descriptor_item`**
: A token identifying which item of information about a column
to retrieve.  See [ecpg-named-descriptors](#ecpg-named-descriptors) for
a list of supported items.

**`cvariable`**
: A host variable that will receive the data retrieved from the
descriptor area.

## Examples

An example to retrieve the number of columns in a result set:

```
EXEC SQL GET DESCRIPTOR d :d_count = COUNT;
```

An example to retrieve a data length in the first column:

```
EXEC SQL GET DESCRIPTOR d VALUE 1 :d_returned_octet_length = RETURNED_OCTET_LENGTH;
```

An example to retrieve the data body of the second column as a
string:

```
EXEC SQL GET DESCRIPTOR d VALUE 2 :d_data = DATA;
```

Here is an example for a whole procedure of
executing `SELECT current_database();` and showing the number of
columns, the column data length, and the column data:

```
int
main(void)
{
EXEC SQL BEGIN DECLARE SECTION;
int  d_count;
char d_data[1024];
int  d_returned_octet_length;
EXEC SQL END DECLARE SECTION;

EXEC SQL CONNECT TO testdb AS con1 USER testuser;
EXEC SQL SELECT pg_catalog.set_config('search_path', '', false); EXEC SQL COMMIT;
EXEC SQL ALLOCATE DESCRIPTOR d;

/* Declare, open a cursor, and assign a descriptor to the cursor  */
EXEC SQL DECLARE cur CURSOR FOR SELECT current_database();
EXEC SQL OPEN cur;
EXEC SQL FETCH NEXT FROM cur INTO SQL DESCRIPTOR d;

/* Get a number of total columns */
EXEC SQL GET DESCRIPTOR d :d_count = COUNT;
printf("d_count                 = %d\n", d_count);

/* Get length of a returned column */
EXEC SQL GET DESCRIPTOR d VALUE 1 :d_returned_octet_length = RETURNED_OCTET_LENGTH;
printf("d_returned_octet_length = %d\n", d_returned_octet_length);

/* Fetch the returned column as a string */
EXEC SQL GET DESCRIPTOR d VALUE 1 :d_data = DATA;
printf("d_data                  = %s\n", d_data);

/* Closing */
EXEC SQL CLOSE cur;
EXEC SQL COMMIT;

EXEC SQL DEALLOCATE DESCRIPTOR d;
EXEC SQL DISCONNECT ALL;

return 0;
}
```

When the example is executed, the result will look like this:

```
d_count                 = 1
d_returned_octet_length = 6
d_data                  = testdb
```

## Compatibility

`GET DESCRIPTOR` is specified in the SQL standard.

## See Also

OPEN
open a dynamic cursor

```
OPEN `cursor_name`
OPEN `cursor_name` USING `value` [, ... ]
OPEN `cursor_name` USING SQL DESCRIPTOR `descriptor_name`
```

## Description

`OPEN` opens a cursor and optionally binds
actual values to the placeholders in the cursor's declaration.
The cursor must previously have been declared with
the `DECLARE` command.  The execution
of `OPEN` causes the query to start executing on
the server.

## Parameters

**`cursor_name`**
: The name of the cursor to be opened.  This can be an SQL
identifier or a host variable.

**`value`**
: A value to be bound to a placeholder in the cursor.  This can
be an SQL constant, a host variable, or a host variable with
indicator.

**`descriptor_name`**
: The name of a descriptor containing values to be bound to the
placeholders in the cursor.  This can be an SQL identifier or
a host variable.

## Examples

```
EXEC SQL OPEN a;
EXEC SQL OPEN d USING 1, 'test';
EXEC SQL OPEN c1 USING SQL DESCRIPTOR mydesc;
EXEC SQL OPEN :curname1;
```

## Compatibility

`OPEN` is specified in the SQL standard.

## See Also

PREPARE
prepare a statement for execution

```
PREPARE `prepared_name` FROM `string`
```

## Description

`PREPARE` prepares a statement dynamically
specified as a string for execution.  This is different from the
direct SQL statement [sql-prepare](#sql-prepare), which can also
be used in embedded programs.  The [sql-execute](#sql-execute)
command is used to execute either kind of prepared statement.

## Parameters

**`prepared_name`**
: An identifier for the prepared query.

**`string`**
: A literal string or a host variable containing a preparable
SQL statement, one of SELECT, INSERT, UPDATE, or DELETE.
Use question marks (`?`) for parameter values
to be supplied at execution.

## Notes

In typical usage, the `string` is a host
variable reference to a string containing a dynamically-constructed
SQL statement.  The case of a literal string is not very useful;
you might as well just write a direct SQL `PREPARE`
statement.

If you do use a literal string, keep in mind that any double quotes
you might wish to include in the SQL statement must be written as
octal escapes (`\042`) not the usual C
idiom `\"`.  This is because the string is inside
an `EXEC SQL` section, so the ECPG lexer parses it
according to SQL rules not C rules.  Any embedded backslashes will
later be handled according to C rules; but `\"`
causes an immediate syntax error because it is seen as ending the
literal.

## Examples

```
char *stmt = "SELECT * FROM test1 WHERE a = ? AND b = ?";

EXEC SQL ALLOCATE DESCRIPTOR outdesc;
EXEC SQL PREPARE foo FROM :stmt;

EXEC SQL EXECUTE foo USING SQL DESCRIPTOR indesc INTO SQL DESCRIPTOR outdesc;
```

## Compatibility

`PREPARE` is specified in the SQL standard.

## See Also

SET AUTOCOMMIT
set the autocommit behavior of the current session

```
SET AUTOCOMMIT { = | TO } { ON | OFF }
```

## Description

`SET AUTOCOMMIT` sets the autocommit behavior of
the current database session.  By default, embedded SQL programs
are *not* in autocommit mode,
so `COMMIT` needs to be issued explicitly when
desired.  This command can change the session to autocommit mode,
where each individual statement is committed implicitly.

## Compatibility

`SET AUTOCOMMIT` is an extension of PostgreSQL ECPG.

SET CONNECTION
select a database connection

```
SET CONNECTION [ TO | = ] `connection_name`
```

## Description

`SET CONNECTION` sets the "current"
database connection, which is the one that all commands use
unless overridden.

## Parameters

**`connection_name`**
: A database connection name established by
the `CONNECT` command.

**`CURRENT`**
: Set the connection to the current connection (thus, nothing happens).

## Examples

```
EXEC SQL SET CONNECTION TO con2;
EXEC SQL SET CONNECTION = con1;
```

## Compatibility

`SET CONNECTION` is specified in the SQL standard.

## See Also

SET DESCRIPTOR
set information in an SQL descriptor area

```
SET DESCRIPTOR `descriptor_name` `descriptor_header_item` = `value` [, ... ]
SET DESCRIPTOR `descriptor_name` VALUE `number` `descriptor_item` = `value` [, ...]
```

## Description

`SET DESCRIPTOR` populates an SQL descriptor
area with values.  The descriptor area is then typically used to
bind parameters in a prepared query execution.

This command has two forms: The first form applies to the
descriptor "header", which is independent of a
particular datum.  The second form assigns values to particular
datums, identified by number.

## Parameters

**`descriptor_name`**
: A descriptor name.

**`descriptor_header_item`**
: A token identifying which header information item to set.
Only `COUNT`, to set the number of descriptor
items, is currently supported.

**`number`**
: The number of the descriptor item to set.  The count starts at
1.

**`descriptor_item`**
: A token identifying which item of information to set in the
descriptor.  See [ecpg-named-descriptors](#ecpg-named-descriptors) for a
list of supported items.

**`value`**
: A value to store into the descriptor item.  This can be an SQL
constant or a host variable.

## Examples

```
EXEC SQL SET DESCRIPTOR indesc COUNT = 1;
EXEC SQL SET DESCRIPTOR indesc VALUE 1 DATA = 2;
EXEC SQL SET DESCRIPTOR indesc VALUE 1 DATA = :val1;
EXEC SQL SET DESCRIPTOR indesc VALUE 2 INDICATOR = :val1, DATA = 'some string';
EXEC SQL SET DESCRIPTOR indesc VALUE 2 INDICATOR = :val2null, DATA = :val2;
```

## Compatibility

`SET DESCRIPTOR` is specified in the SQL standard.

## See Also

TYPE
define a new data type

```
TYPE `type_name` IS `ctype`
```

## Description

The `TYPE` command defines a new C type.  It is
equivalent to putting a `typedef` into a declare
section.

This command is only recognized when `ecpg` is
run with the `-c` option.

## Parameters

**`type_name`**
: The name for the new type.  It must be a valid C type name.

**`ctype`**
: A C type specification.

## Examples

```
EXEC SQL TYPE customer IS
struct
{
varchar name[50];
int     phone;
};

EXEC SQL TYPE cust_ind IS
struct ind
{
short   name_ind;
short   phone_ind;
};

EXEC SQL TYPE c IS char reference;
EXEC SQL TYPE ind IS union { int integer; short smallint; };
EXEC SQL TYPE intarray IS int[AMOUNT];
EXEC SQL TYPE str IS varchar[BUFFERSIZ];
EXEC SQL TYPE string IS char[11];
```

Here is an example program that uses `EXEC SQL
TYPE`:

```
EXEC SQL WHENEVER SQLERROR SQLPRINT;

EXEC SQL TYPE tt IS
struct
{
varchar v[256];
int     i;
};

EXEC SQL TYPE tt_ind IS
struct ind {
short   v_ind;
short   i_ind;
};

int
main(void)
{
EXEC SQL BEGIN DECLARE SECTION;
tt t;
tt_ind t_ind;
EXEC SQL END DECLARE SECTION;

EXEC SQL CONNECT TO testdb AS con1;
EXEC SQL SELECT pg_catalog.set_config('search_path', '', false); EXEC SQL COMMIT;

EXEC SQL SELECT current_database(), 256 INTO :t:t_ind LIMIT 1;

printf("t.v = %s\n", t.v.arr);
printf("t.i = %d\n", t.i);

printf("t_ind.v_ind = %d\n", t_ind.v_ind);
printf("t_ind.i_ind = %d\n", t_ind.i_ind);

EXEC SQL DISCONNECT con1;

return 0;
}
```

The output from this program looks like this:

```
t.v = testdb
t.i = 256
t_ind.v_ind = 0
t_ind.i_ind = 0
```

## Compatibility

The `TYPE` command is a PostgreSQL extension.

VAR
define a variable

```
VAR `varname` IS `ctype`
```

## Description

The `VAR` command assigns a new C data type
to a host variable.  The host variable must be previously
declared in a declare section.

## Parameters

**`varname`**
: A C variable name.

**`ctype`**
: A C type specification.

## Examples

```
Exec sql begin declare section;
short a;
exec sql end declare section;
EXEC SQL VAR a IS int;
```

## Compatibility

The `VAR` command is a PostgreSQL extension.

WHENEVER
specify the action to be taken when an SQL statement causes a specific class condition to be raised

```
WHENEVER { NOT FOUND | SQLERROR | SQLWARNING } `action`
```

## Description

Define a behavior which is called on the special cases (Rows not
found, SQL warnings or errors) in the result of SQL execution.

## Parameters

See [ecpg-whenever](#ecpg-whenever) for a description of the
parameters.

## Examples

```
EXEC SQL WHENEVER NOT FOUND CONTINUE;
EXEC SQL WHENEVER NOT FOUND DO BREAK;
EXEC SQL WHENEVER NOT FOUND DO CONTINUE;
EXEC SQL WHENEVER SQLWARNING SQLPRINT;
EXEC SQL WHENEVER SQLWARNING DO warn();
EXEC SQL WHENEVER SQLERROR sqlprint;
EXEC SQL WHENEVER SQLERROR CALL print2();
EXEC SQL WHENEVER SQLERROR DO handle_error("select");
EXEC SQL WHENEVER SQLERROR DO sqlnotice(NULL, NONO);
EXEC SQL WHENEVER SQLERROR DO sqlprint();
EXEC SQL WHENEVER SQLERROR GOTO error_label;
EXEC SQL WHENEVER SQLERROR STOP;
```

A typical application is the use of `WHENEVER NOT FOUND
BREAK` to handle looping through result sets:

```
int
main(void)
{
EXEC SQL CONNECT TO testdb AS con1;
EXEC SQL SELECT pg_catalog.set_config('search_path', '', false); EXEC SQL COMMIT;
EXEC SQL ALLOCATE DESCRIPTOR d;
EXEC SQL DECLARE cur CURSOR FOR SELECT current_database(), 'hoge', 256;
EXEC SQL OPEN cur;

/* when end of result set reached, break out of while loop */
EXEC SQL WHENEVER NOT FOUND DO BREAK;

while (1)
{
EXEC SQL FETCH NEXT FROM cur INTO SQL DESCRIPTOR d;
...
}

EXEC SQL CLOSE cur;
EXEC SQL COMMIT;

EXEC SQL DEALLOCATE DESCRIPTOR d;
EXEC SQL DISCONNECT ALL;

return 0;
}
```

## Compatibility

`WHENEVER` is specified in the SQL standard, but
most of the actions are PostgreSQL extensions.

## Informix Compatibility Mode

`ecpg` can be run in a so-called *Informix compatibility mode*. If
this mode is active, it tries to behave as if it were the Informix
precompiler for Informix E/SQL. Generally spoken this will allow you to use
the dollar sign instead of the `EXEC SQL` primitive to introduce
embedded SQL commands:

```
$int j = 3;
$CONNECT TO :dbname;
$CREATE TABLE test(i INT PRIMARY KEY, j INT);
$INSERT INTO test(i, j) VALUES (7, :j);
$COMMIT;
```

> **Note:**

> There must not be any white space between the `$`
> and a following preprocessor directive, that is,
> `include`, `define`, `ifdef`,
> etc.  Otherwise, the preprocessor will parse the token as a host
> variable.
>

There are two compatibility modes: `INFORMIX`, `INFORMIX_SE`

When linking programs that use this compatibility mode, remember to link
against `libcompat` that is shipped with ECPG.

Besides the previously explained syntactic sugar, the Informix compatibility
mode ports some functions for input, output and transformation of data as
well as embedded SQL statements known from E/SQL to ECPG.

Informix compatibility mode is closely connected to the pgtypeslib library
of ECPG. pgtypeslib maps SQL data types to data types within the C host
program and most of the additional functions of the Informix compatibility
mode allow you to operate on those C host program types. Note however that
the extent of the compatibility is limited. It does not try to copy Informix
behavior; it allows you to do more or less the same operations and gives
you functions that have the same name and the same basic behavior but it is
no drop-in replacement if you are using Informix at the moment. Moreover,
some of the data types are different. For example,
PostgreSQL's datetime and interval types do not
know about ranges like for example `YEAR TO MINUTE` so you won't
find support in ECPG for that either.

### Additional Types

The Informix-special "string" pseudo-type for storing right-trimmed character string data is now
supported in Informix-mode without using `typedef`. In fact, in Informix-mode,
ECPG refuses to process source files that contain `typedef sometype string;`

```
EXEC SQL BEGIN DECLARE SECTION;
string userid; /* this variable will contain trimmed data */
EXEC SQL END DECLARE SECTION;

EXEC SQL FETCH MYCUR INTO :userid;
```

### Additional/Missing Embedded SQL Statements

**`CLOSE DATABASE`**
: This statement closes the current connection. In fact, this is a
synonym for ECPG's `DISCONNECT CURRENT`:

```
$CLOSE DATABASE;                /* close the current connection */
EXEC SQL CLOSE DATABASE;
```

**`FREE cursor_name`**
: Due to differences in how ECPG works compared to Informix's ESQL/C (namely, which steps
are purely grammar transformations and which steps rely on the underlying run-time library)
there is no `FREE cursor_name` statement in ECPG. This is because in ECPG,
`DECLARE CURSOR` doesn't translate to a function call into
the run-time library that uses to the cursor name. This means that there's no run-time
bookkeeping of SQL cursors in the ECPG run-time library, only in the PostgreSQL server.

**`FREE statement_name`**
: `FREE statement_name` is a synonym for `DEALLOCATE PREPARE statement_name`.

### Informix-compatible SQLDA Descriptor Areas

Informix-compatible mode supports a different structure than the one described in
[ecpg-sqlda-descriptors](#ecpg-sqlda-descriptors). See below:

```
struct sqlvar_compat
{
short   sqltype;
int     sqllen;
char   *sqldata;
short  *sqlind;
char   *sqlname;
char   *sqlformat;
short   sqlitype;
short   sqlilen;
char   *sqlidata;
int     sqlxid;
char   *sqltypename;
short   sqltypelen;
short   sqlownerlen;
short   sqlsourcetype;
char   *sqlownername;
int     sqlsourceid;
char   *sqlilongdata;
int     sqlflags;
void   *sqlreserved;
};

struct sqlda_compat
{
short  sqld;
struct sqlvar_compat *sqlvar;
char   desc_name[19];
short  desc_occ;
struct sqlda_compat *desc_next;
void  *reserved;
};

typedef struct sqlvar_compat    sqlvar_t;
typedef struct sqlda_compat     sqlda_t;
```

The global properties are:

**`sqld`**
: The number of fields in the `SQLDA` descriptor.

**`sqlvar`**
: Pointer to the per-field properties.

**`desc_name`**
: Unused, filled with zero-bytes.

**`desc_occ`**
: Size of the allocated structure.

**`desc_next`**
: Pointer to the next SQLDA structure if the result set contains more than one record.

**`reserved`**
: Unused pointer, contains NULL. Kept for Informix-compatibility.

The per-field properties are below, they are stored in the `sqlvar` array:

**`sqltype`**
: Type of the field. Constants are in `sqltypes.h`

**`sqllen`**
: Length of the field data.

**`sqldata`**
: Pointer to the field data. The pointer is of `char *` type,
the data pointed by it is in a binary format. Example:

```
int intval;

switch (sqldata->sqlvar[i].sqltype)
{
case SQLINTEGER:
intval = *(int *)sqldata->sqlvar[i].sqldata;
break;
...
}
```

**`sqlind`**
: Pointer to the NULL indicator. If returned by DESCRIBE or FETCH then it's always a valid pointer.
If used as input for `EXECUTE ... USING sqlda;` then NULL-pointer value means
that the value for this field is non-NULL. Otherwise a valid pointer and `sqlitype`
has to be properly set. Example:

```
if (*(int2 *)sqldata->sqlvar[i].sqlind != 0)
printf("value is NULL\n");
```

**`sqlname`**
: Name of the field. 0-terminated string.

**`sqlformat`**
: Reserved in Informix, value of [libpq-PQfformat](#libpq-PQfformat) for the field.

**`sqlitype`**
: Type of the NULL indicator data. It's always SQLSMINT when returning data from the server.
When the `SQLDA` is used for a parameterized query, the data is treated
according to the set type.

**`sqlilen`**
: Length of the NULL indicator data.

**`sqlxid`**
: Extended type of the field, result of [libpq-PQftype](#libpq-PQftype).

**`sqltypename`**
: Unused.

**`sqlilongdata`**
: It equals to `sqldata` if `sqllen` is larger than 32kB.

Example:

```
EXEC SQL INCLUDE sqlda.h;

sqlda_t        *sqlda; /* This doesn't need to be under embedded DECLARE SECTION */

EXEC SQL BEGIN DECLARE SECTION;
char *prep_stmt = "select * from table1";
int i;
EXEC SQL END DECLARE SECTION;

...

EXEC SQL PREPARE mystmt FROM :prep_stmt;

EXEC SQL DESCRIBE mystmt INTO sqlda;

printf("# of fields: %d\n", sqlda->sqld);
for (i = 0; i sqld; i++)
printf("field %d: \"%s\"\n", sqlda->sqlvar[i]->sqlname);

EXEC SQL DECLARE mycursor CURSOR FOR mystmt;
EXEC SQL OPEN mycursor;
EXEC SQL WHENEVER NOT FOUND GOTO out;

while (1)
{
EXEC SQL FETCH mycursor USING sqlda;
}

EXEC SQL CLOSE mycursor;

free(sqlda); /* The main structure is all to be free(),
* sqlda and sqlda->sqlvar is in one allocated area */
```

For more information, see the `sqlda.h` header and the
`src/interfaces/ecpg/test/compat_informix/sqlda.pgc` regression test.

### Additional Functions

**`decadd`**
: Add two decimal type values.

```
int decadd(decimal *arg1, decimal *arg2, decimal *sum);
```

The function receives a pointer to the first operand of type decimal
(`arg1`), a pointer to the second operand of type decimal
(`arg2`) and a pointer to a value of type decimal that will
contain the sum (`sum`). On success, the function returns 0.
`ECPG_INFORMIX_NUM_OVERFLOW` is returned in case of overflow and
`ECPG_INFORMIX_NUM_UNDERFLOW` in case of underflow. -1 is returned for
other failures and `errno` is set to the respective `errno` number of the
pgtypeslib.

**`deccmp`**
: Compare two variables of type decimal.

```
int deccmp(decimal *arg1, decimal *arg2);
```

The function receives a pointer to the first decimal value
(`arg1`), a pointer to the second decimal value
(`arg2`) and returns an integer value that indicates which is
the bigger value.

- 1, if the value that `arg1` points to is bigger than the
value that `var2` points to
- -1, if the value that `arg1` points to is smaller than the
value that `arg2` points to
- 0, if the value that `arg1` points to and the value that
`arg2` points to are equal

**`deccopy`**
: Copy a decimal value.

```
void deccopy(decimal *src, decimal *target);
```

The function receives a pointer to the decimal value that should be
copied as the first argument (`src`) and a pointer to the
target structure of type decimal (`target`) as the second
argument.

**`deccvasc`**
: Convert a value from its ASCII representation into a decimal type.

```
int deccvasc(char *cp, int len, decimal *np);
```

The function receives a pointer to string that contains the string
representation of the number to be converted (`cp`) as well
as its length `len`. `np` is a pointer to the
decimal value that saves the result of the operation.

Valid formats are for example:
`-2`,
`.794`,
`+3.44`,
`592.49E07` or
`-32.84e-4`.

The function returns 0 on success. If overflow or underflow occurred,
`ECPG_INFORMIX_NUM_OVERFLOW` or
`ECPG_INFORMIX_NUM_UNDERFLOW` is returned. If the ASCII
representation could not be parsed,
`ECPG_INFORMIX_BAD_NUMERIC` is returned or
`ECPG_INFORMIX_BAD_EXPONENT` if this problem occurred while
parsing the exponent.

**`deccvdbl`**
: Convert a value of type double to a value of type decimal.

```
int deccvdbl(double dbl, decimal *np);
```

The function receives the variable of type double that should be
converted as its first argument (`dbl`). As the second
argument (`np`), the function receives a pointer to the
decimal variable that should hold the result of the operation.

The function returns 0 on success and a negative value if the
conversion failed.

**`deccvint`**
: Convert a value of type int to a value of type decimal.

```
int deccvint(int in, decimal *np);
```

The function receives the variable of type int that should be
converted as its first argument (`in`). As the second
argument (`np`), the function receives a pointer to the
decimal variable that should hold the result of the operation.

The function returns 0 on success and a negative value if the
conversion failed.

**`deccvlong`**
: Convert a value of type long to a value of type decimal.

```
int deccvlong(long lng, decimal *np);
```

The function receives the variable of type long that should be
converted as its first argument (`lng`). As the second
argument (`np`), the function receives a pointer to the
decimal variable that should hold the result of the operation.

The function returns 0 on success and a negative value if the
conversion failed.

**`decdiv`**
: Divide two variables of type decimal.

```
int decdiv(decimal *n1, decimal *n2, decimal *result);
```

The function receives pointers to the variables that are the first
(`n1`) and the second (`n2`) operands and
calculates `n1`/`n2`. `result` is a
pointer to the variable that should hold the result of the operation.

On success, 0 is returned and a negative value if the division fails.
If overflow or underflow occurred, the function returns
`ECPG_INFORMIX_NUM_OVERFLOW` or
`ECPG_INFORMIX_NUM_UNDERFLOW` respectively. If an attempt to
divide by zero is observed, the function returns
`ECPG_INFORMIX_DIVIDE_ZERO`.

**`decmul`**
: Multiply two decimal values.

```
int decmul(decimal *n1, decimal *n2, decimal *result);
```

The function receives pointers to the variables that are the first
(`n1`) and the second (`n2`) operands and
calculates `n1`*`n2`. `result` is a
pointer to the variable that should hold the result of the operation.

On success, 0 is returned and a negative value if the multiplication
fails. If overflow or underflow occurred, the function returns
`ECPG_INFORMIX_NUM_OVERFLOW` or
`ECPG_INFORMIX_NUM_UNDERFLOW` respectively.

**`decsub`**
: Subtract one decimal value from another.

```
int decsub(decimal *n1, decimal *n2, decimal *result);
```

The function receives pointers to the variables that are the first
(`n1`) and the second (`n2`) operands and
calculates `n1`-`n2`. `result` is a
pointer to the variable that should hold the result of the operation.

On success, 0 is returned and a negative value if the subtraction
fails. If overflow or underflow occurred, the function returns
`ECPG_INFORMIX_NUM_OVERFLOW` or
`ECPG_INFORMIX_NUM_UNDERFLOW` respectively.

**`dectoasc`**
: Convert a variable of type decimal to its ASCII representation in a C
char* string.

```
int dectoasc(decimal *np, char *cp, int len, int right)
```

The function receives a pointer to a variable of type decimal
(`np`) that it converts to its textual representation.
`cp` is the buffer that should hold the result of the
operation. The parameter `right` specifies, how many digits
right of the decimal point should be included in the output. The result
will be rounded to this number of decimal digits. Setting
`right` to -1 indicates that all available decimal digits
should be included in the output. If the length of the output buffer,
which is indicated by `len` is not sufficient to hold the
textual representation including the trailing zero byte, only a
single `*` character is stored in the result and -1 is
returned.

The function returns either -1 if the buffer `cp` was too
small or `ECPG_INFORMIX_OUT_OF_MEMORY` if memory was
exhausted.

**`dectodbl`**
: Convert a variable of type decimal to a double.

```
int dectodbl(decimal *np, double *dblp);
```

The function receives a pointer to the decimal value to convert
(`np`) and a pointer to the double variable that
should hold the result of the operation (`dblp`).

On success, 0 is returned and a negative value if the conversion
failed.

**`dectoint`**
: Convert a variable of type decimal to an integer.

```
int dectoint(decimal *np, int *ip);
```

The function receives a pointer to the decimal value to convert
(`np`) and a pointer to the integer variable that
should hold the result of the operation (`ip`).

On success, 0 is returned and a negative value if the conversion
failed. If an overflow occurred, `ECPG_INFORMIX_NUM_OVERFLOW`
is returned.

Note that the ECPG implementation differs from the Informix
implementation. Informix limits an integer to the range from -32767 to
32767, while the limits in the ECPG implementation depend on the
architecture (`INT_MIN .. INT_MAX`).

**`dectolong`**
: Convert a variable of type decimal to a long integer.

```
int dectolong(decimal *np, long *lngp);
```

The function receives a pointer to the decimal value to convert
(`np`) and a pointer to the long variable that
should hold the result of the operation (`lngp`).

On success, 0 is returned and a negative value if the conversion
failed. If an overflow occurred, `ECPG_INFORMIX_NUM_OVERFLOW`
is returned.

Note that the ECPG implementation differs from the Informix
implementation. Informix limits a long integer to the range from
-2,147,483,647 to 2,147,483,647, while the limits in the ECPG
implementation depend on the architecture (`-LONG_MAX ..
LONG_MAX`).

**`rdatestr`**
: Converts a date to a C char* string.

```
int rdatestr(date d, char *str);
```

The function receives two arguments, the first one is the date to
convert (`d`) and the second one is a pointer to the target
string. The output format is always `yyyy-mm-dd`, so you need
to allocate at least 11 bytes (including the zero-byte terminator) for the
string.

The function returns 0 on success and a negative value in case of
error.

Note that ECPG's implementation differs from the Informix
implementation. In Informix the format can be influenced by setting
environment variables. In ECPG however, you cannot change the output
format.

**`rstrdate`**
: Parse the textual representation of a date.

```
int rstrdate(char *str, date *d);
```

The function receives the textual representation of the date to convert
(`str`) and a pointer to a variable of type date
(`d`). This function does not allow you to specify a format
mask. It uses the default format mask of Informix which is
`mm/dd/yyyy`. Internally, this function is implemented by
means of `rdefmtdate`. Therefore, `rstrdate` is
not faster and if you have the choice you should opt for
`rdefmtdate` which allows you to specify the format mask
explicitly.

The function returns the same values as `rdefmtdate`.

**`rtoday`**
: Get the current date.

```
void rtoday(date *d);
```

The function receives a pointer to a date variable (`d`)
that it sets to the current date.

Internally this function uses the [pgtypesdatetoday](#pgtypesdatetoday)
function.

**`rjulmdy`**
: Extract the values for the day, the month and the year from a variable
of type date.

```
int rjulmdy(date d, short mdy[3]);
```

The function receives the date `d` and a pointer to an array
of 3 short integer values `mdy`. The variable name indicates
the sequential order: `mdy[0]` will be set to contain the
number of the month, `mdy[1]` will be set to the value of the
day and `mdy[2]` will contain the year.

The function always returns 0 at the moment.

Internally the function uses the [pgtypesdatejulmdy](#pgtypesdatejulmdy)
function.

**`rdefmtdate`**
: Use a format mask to convert a character string to a value of type
date.

```
int rdefmtdate(date *d, char *fmt, char *str);
```

The function receives a pointer to the date value that should hold the
result of the operation (`d`), the format mask to use for
parsing the date (`fmt`) and the C char* string containing
the textual representation of the date (`str`). The textual
representation is expected to match the format mask. However you do not
need to have a 1:1 mapping of the string to the format mask. The
function only analyzes the sequential order and looks for the literals
`yy` or `yyyy` that indicate the
position of the year, `mm` to indicate the position of
the month and `dd` to indicate the position of the
day.

The function returns the following values:

- 0 - The function terminated successfully.
- `ECPG_INFORMIX_ENOSHORTDATE` - The date does not contain
delimiters between day, month and year. In this case the input
string must be exactly 6 or 8 bytes long but isn't.
- `ECPG_INFORMIX_ENOTDMY` - The format string did not
correctly indicate the sequential order of year, month and day.
- `ECPG_INFORMIX_BAD_DAY` - The input string does not
contain a valid day.
- `ECPG_INFORMIX_BAD_MONTH` - The input string does not
contain a valid month.
- `ECPG_INFORMIX_BAD_YEAR` - The input string does not
contain a valid year.

Internally this function is implemented to use the [pgtypesdatedefmtasc](#pgtypesdatedefmtasc) function. See the reference there for a
table of example input.

**`rfmtdate`**
: Convert a variable of type date to its textual representation using a
format mask.

```
int rfmtdate(date d, char *fmt, char *str);
```

The function receives the date to convert (`d`), the format
mask (`fmt`) and the string that will hold the textual
representation of the date (`str`).

On success, 0 is returned and a negative value if an error occurred.

Internally this function uses the [pgtypesdatefmtasc](#pgtypesdatefmtasc)
function, see the reference there for examples.

**`rmdyjul`**
: Create a date value from an array of 3 short integers that specify the
day, the month and the year of the date.

```
int rmdyjul(short mdy[3], date *d);
```

The function receives the array of the 3 short integers
(`mdy`) and a pointer to a variable of type date that should
hold the result of the operation.

Currently the function returns always 0.

Internally the function is implemented to use the function [pgtypesdatemdyjul](#pgtypesdatemdyjul).

**`rdayofweek`**
: Return a number representing the day of the week for a date value.

```
int rdayofweek(date d);
```

The function receives the date variable `d` as its only
argument and returns an integer that indicates the day of the week for
this date.

- 0 - Sunday
- 1 - Monday
- 2 - Tuesday
- 3 - Wednesday
- 4 - Thursday
- 5 - Friday
- 6 - Saturday

Internally the function is implemented to use the function [pgtypesdatedayofweek](#pgtypesdatedayofweek).

**`dtcurrent`**
: Retrieve the current timestamp.

```
void dtcurrent(timestamp *ts);
```

The function retrieves the current timestamp and saves it into the
timestamp variable that `ts` points to.

**`dtcvasc`**
: Parses a timestamp from its textual representation
into a timestamp variable.

```
int dtcvasc(char *str, timestamp *ts);
```

The function receives the string to parse (`str`) and a
pointer to the timestamp variable that should hold the result of the
operation (`ts`).

The function returns 0 on success and a negative value in case of
error.

Internally this function uses the [pgtypestimestampfromasc](#pgtypestimestampfromasc) function. See the reference there
for a table with example inputs.

**`dtcvfmtasc`**
: Parses a timestamp from its textual representation
using a format mask into a timestamp variable.

```
dtcvfmtasc(char *inbuf, char *fmtstr, timestamp *dtvalue)
```

The function receives the string to parse (`inbuf`), the
format mask to use (`fmtstr`) and a pointer to the timestamp
variable that should hold the result of the operation
(`dtvalue`).

This function is implemented by means of the [pgtypestimestampdefmtasc](#pgtypestimestampdefmtasc) function. See the documentation
there for a list of format specifiers that can be used.

The function returns 0 on success and a negative value in case of
error.

**`dtsub`**
: Subtract one timestamp from another and return a variable of type
interval.

```
int dtsub(timestamp *ts1, timestamp *ts2, interval *iv);
```

The function will subtract the timestamp variable that `ts2`
points to from the timestamp variable that `ts1` points to
and will store the result in the interval variable that `iv`
points to.

Upon success, the function returns 0 and a negative value if an
error occurred.

**`dttoasc`**
: Convert a timestamp variable to a C char* string.

```
int dttoasc(timestamp *ts, char *output);
```

The function receives a pointer to the timestamp variable to convert
(`ts`) and the string that should hold the result of the
operation (`output`). It converts `ts` to its
textual representation according to the SQL standard, which is
be `YYYY-MM-DD HH:MM:SS`.

Upon success, the function returns 0 and a negative value if an
error occurred.

**`dttofmtasc`**
: Convert a timestamp variable to a C char* using a format mask.

```
int dttofmtasc(timestamp *ts, char *output, int str_len, char *fmtstr);
```

The function receives a pointer to the timestamp to convert as its
first argument (`ts`), a pointer to the output buffer
(`output`), the maximal length that has been allocated for
the output buffer (`str_len`) and the format mask to
use for the conversion (`fmtstr`).

Upon success, the function returns 0 and a negative value if an
error occurred.

Internally, this function uses the [pgtypestimestampfmtasc](#pgtypestimestampfmtasc) function. See the reference there for
information on what format mask specifiers can be used.

**`intoasc`**
: Convert an interval variable to a C char* string.

```
int intoasc(interval *i, char *str);
```

The function receives a pointer to the interval variable to convert
(`i`) and the string that should hold the result of the
operation (`str`). It converts `i` to its
textual representation according to the SQL standard, which is
be `YYYY-MM-DD HH:MM:SS`.

Upon success, the function returns 0 and a negative value if an
error occurred.

**`rfmtlong`**
: Convert a long integer value to its textual representation using a
format mask.

```
int rfmtlong(long lng_val, char *fmt, char *outbuf);
```

The function receives the long value `lng_val`, the format
mask `fmt` and a pointer to the output buffer
`outbuf`. It converts the long value according to the format
mask to its textual representation.

The format mask can be composed of the following format specifying
characters:

- `*` (asterisk) - if this position would be blank
otherwise, fill it with an asterisk.
- `&` (ampersand) - if this position would be
blank otherwise, fill it with a zero.
- `#` - turn leading zeroes into blanks.
- `;
#include ;

/* exec sql begin declare section */

#line 1 "foo.pgc"

int index;
int result;
/* exec sql end declare section */
...
ECPGdo(__LINE__, NULL, "SELECT res FROM mytable WHERE index = ?     ",
ECPGt_int,&(index),1L,1L,sizeof(int),
ECPGt_NO_INDICATOR, NULL , 0L, 0L, 0L, ECPGt_EOIT,
ECPGt_int,&(result),1L,1L,sizeof(int),
ECPGt_NO_INDICATOR, NULL , 0L, 0L, 0L, ECPGt_EORT);
#line 147 "foo.pgc"

```

(The indentation here is added for readability and not
something the preprocessor does.)
