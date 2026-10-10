# Overview; The Concept; Preprocessor; Embedded SQL Commands; Dynamic SQL; Descriptor Areas; Type Handling; Informix Compatibility; Internals

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIV_client_interfaces/03_ecpg_-_embedded_sql_in_c.md`
- Source Title: `ECPG — Embedded SQL in C`
- Source Heading Path: `ECPG - Embedded SQL in C > Overview; The Concept; Preprocessor; Embedded SQL Commands; Dynamic SQL; Descriptor Areas; Type Handling; Informix Compatibility; Internals`
- Source Line Ranges: `14-67, 1375-1491, 2507-3287, 3468-3481, 4500-5318`
- Chunk ID: `pg16_fact_0078_c0d07164ff`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `917ab3f52c9c1d07839c694fc3eadbf5ad652b64e09c172c0b02b12ffcca11f4`

## Retrieval Guidance

- Use When: Implement embedded SQL in C or look up ECPG syntax and generated-code behavior.
- Retrieval Keywords: ECPG, embedded SQL C, ecpg preprocessor, EXEC SQL, descriptor area, dynamic SQL, Informix compatibility
- Follow-up Guidance: Use connection or error-handling records for runtime configuration and diagnostics.
- Classification Note: These sections document embedded SQL syntax, generated C behavior, descriptor APIs, dynamic SQL, type mapping, and compatibility details.

## Official Source Content

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
