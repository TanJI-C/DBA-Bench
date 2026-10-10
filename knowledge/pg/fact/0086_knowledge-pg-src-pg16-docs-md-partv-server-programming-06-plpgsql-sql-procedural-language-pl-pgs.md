# Structure; Declarations; Expressions; Statements; Cursors; Trigger Functions; Implementation Details; Porting

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partV_server_programming/06_plpgsql_-_sql_procedural_language.md`
- Source Title: `PL/pgSQL — SQL Procedural Language`
- Source Heading Path: `PL/pgSQL - SQL Procedural Language > Structure; Declarations; Expressions; Statements; Cursors; Trigger Functions; Implementation Details; Porting`
- Source Line Ranges: `108-224, 225-672, 673-1025, 1269-2016, 2173-2647, 2735-2875, 2910-3036, 3793-3852, 3853-3912, 3913-4006, 4007-4106, 4107-4348`
- Chunk ID: `pg16_fact_0086_5330e14a17`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `01218afd336d81e2ab99e35c0840fb7d31e8f4a01d28edc1270d532c3d97df44`

## Retrieval Guidance

- Use When: Write or interpret PL/pgSQL functions, procedures, triggers, and control flow.
- Retrieval Keywords: PL/pgSQL, DECLARE, BEGIN END, RETURN QUERY, cursor, trigger function, record variable, FOUND
- Follow-up Guidance: Use the diagnostic/configuration records for failures, warnings, and compile-time checking behavior.
- Classification Note: These sections document PL/pgSQL language syntax, execution semantics, variables, statements, cursors, triggers, and implementation details.

## Official Source Content

## Structure of PL/pgSQL

Functions written in PL/pgSQL are defined
to the server by executing [sql-createfunction](#sql-createfunction) commands.
Such a command would normally look like, say,

```
CREATE FUNCTION somefunc(integer, text) RETURNS integer
AS '`function body text`'
LANGUAGE plpgsql;
```

The function body is simply a string literal so far as `CREATE
FUNCTION` is concerned.  It is often helpful to use dollar quoting
(see [sql-syntax-dollar-quoting](#sql-syntax-dollar-quoting)) to write the function
body, rather than the normal single quote syntax.  Without dollar quoting,
any single quotes or backslashes in the function body must be escaped by
doubling them.  Almost all the examples in this chapter use dollar-quoted
literals for their function bodies.

PL/pgSQL is a block-structured language.
The complete text of a function body must be a
*block*. A block is defined as:

```
>
DECLARE
`declarations`
BEGIN
`statements`
END  `label` ;
```

Each declaration and each statement within a block is terminated
by a semicolon.  A block that appears within another block must
have a semicolon after `END`, as shown above;
however the final `END` that
concludes a function body does not require a semicolon.

> **Tip:**

> A common mistake is to write a semicolon immediately after
> `BEGIN`.  This is incorrect and will result in a syntax error.
>

A `label` is only needed if you want to
identify the block for use
in an `EXIT` statement, or to qualify the names of the
variables declared in the block.  If a label is given after
`END`, it must match the label at the block's beginning.

All key words are case-insensitive.
Identifiers are implicitly converted to lower case
unless double-quoted, just as they are in ordinary SQL commands.

Comments work the same way in PL/pgSQL code as in
ordinary SQL.  A double dash (`--`) starts a comment
that extends to the end of the line. A `/*` starts a
block comment that extends to the matching occurrence of
`*/`.  Block comments nest.

Any statement in the statement section of a block
can be a *subblock*.  Subblocks can be used for
logical grouping or to localize variables to a small group
of statements.  Variables declared in a subblock mask any
similarly-named variables of outer blocks for the duration
of the subblock; but you can access the outer variables anyway
if you qualify their names with their block's label. For example:

```
CREATE FUNCTION somefunc() RETURNS integer AS $$
>
DECLARE
quantity integer := 30;
BEGIN
RAISE NOTICE 'Quantity here is %', quantity;  -- Prints 30
quantity := 50;
--
-- Create a subblock
--
DECLARE
quantity integer := 80;
BEGIN
RAISE NOTICE 'Quantity here is %', quantity;  -- Prints 80
RAISE NOTICE 'Outer quantity here is %', outerblock.quantity;  -- Prints 50
END;

RAISE NOTICE 'Quantity here is %', quantity;  -- Prints 50

RETURN quantity;
END;
$$ LANGUAGE plpgsql;
```

> **Note:**

> There is actually a hidden "outer block" surrounding the body
> of any PL/pgSQL function.  This block provides the
> declarations of the function's parameters (if any), as well as some
> special variables such as `FOUND` (see
> [plpgsql-statements-diagnostics](#plpgsql-statements-diagnostics)).  The outer block is
> labeled with the function's name, meaning that parameters and special
> variables can be qualified with the function's name.
>

It is important not to confuse the use of
`BEGIN`/`END` for grouping statements in
PL/pgSQL with the similarly-named SQL commands
for transaction
control.  PL/pgSQL's `BEGIN`/`END`
are only for grouping; they do not start or end a transaction.
See [plpgsql-transactions](#plpgsql-transactions) for information on managing
transactions in PL/pgSQL.
Also, a block containing an `EXCEPTION` clause effectively
forms a subtransaction that can be rolled back without affecting the
outer transaction.  For more about that see [plpgsql-error-trapping](#plpgsql-error-trapping).

## Declarations

All variables used in a block must be declared in the
declarations section of the block.
(The only exceptions are that the loop variable of a `FOR` loop
iterating over a range of integer values is automatically declared as an
integer variable, and likewise the loop variable of a `FOR` loop
iterating over a cursor's result is automatically declared as a
record variable.)

PL/pgSQL variables can have any SQL data type, such as
`integer`, `varchar`, and
`char`.

Here are some examples of variable declarations:

```
user_id integer;
quantity numeric(5);
url varchar;
myrow tablename%ROWTYPE;
myfield tablename.columnname%TYPE;
arow RECORD;
```

The general syntax of a variable declaration is:

```
`name`  CONSTANT  `type`  COLLATE `collation_name`   NOT NULL   { DEFAULT | := | = } `expression` ;
```

The `DEFAULT` clause, if given, specifies the initial value assigned
to the variable when the block is entered.  If the `DEFAULT` clause
is not given then the variable is initialized to the
SQL null value.
The `CONSTANT` option prevents the variable from being
assigned to after initialization, so that its value will remain constant
for the duration of the block.
The `COLLATE` option specifies a collation to use for the
variable (see [plpgsql-declaration-collation](#plpgsql-declaration-collation)).
If `NOT NULL`
is specified, an assignment of a null value results in a run-time
error. All variables declared as `NOT NULL`
must have a nonnull default value specified.
Equal (`=`) can be used instead of PL/SQL-compliant
`:=`.

A variable's default value is evaluated and assigned to the variable
each time the block is entered (not just once per function call).
So, for example, assigning `now()` to a variable of type
`timestamp` causes the variable to have the
time of the current function call, not the time when the function was
precompiled.

Examples:

```
quantity integer DEFAULT 32;
url varchar := 'http://mysite.com';
transaction_time CONSTANT timestamp with time zone := now();
```

Once declared, a variable's value can be used in later initialization
expressions in the same block, for example:

```
DECLARE
x integer := 1;
y integer := x + 1;
```

### Declaring Function Parameters

Parameters passed to functions are named with the identifiers
`$1`, `$2`,
etc.  Optionally, aliases can be declared for
`$`n``
parameter names for increased readability.  Either the alias or the
numeric identifier can then be used to refer to the parameter value.

There are two ways to create an alias.  The preferred way is to give a
name to the parameter in the `CREATE FUNCTION` command,
for example:

```
CREATE FUNCTION sales_tax(subtotal real) RETURNS real AS $$
BEGIN
RETURN subtotal * 0.06;
END;
$$ LANGUAGE plpgsql;
```

The other way is to explicitly declare an alias, using the
declaration syntax

```
`name` ALIAS FOR $`n`;
```

The same example in this style looks like:

```
CREATE FUNCTION sales_tax(real) RETURNS real AS $$
DECLARE
subtotal ALIAS FOR $1;
BEGIN
RETURN subtotal * 0.06;
END;
$$ LANGUAGE plpgsql;
```

> **Note:**

> These two examples are not perfectly equivalent.  In the first case,
> `subtotal` could be referenced as
> `sales_tax.subtotal`, but in the second case it could not.
> (Had we attached a label to the inner block, `subtotal` could
> be qualified with that label, instead.)
>

Some more examples:

```
CREATE FUNCTION instr(varchar, integer) RETURNS integer AS $$
DECLARE
v_string ALIAS FOR $1;
index ALIAS FOR $2;
BEGIN
-- some computations using v_string and index here
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION concat_selected_fields(in_t sometablename) RETURNS text AS $$
BEGIN
RETURN in_t.f1 || in_t.f3 || in_t.f5 || in_t.f7;
END;
$$ LANGUAGE plpgsql;
```

When a PL/pgSQL function is declared
with output parameters, the output parameters are given
`$`n`` names and optional
aliases in just the same way as the normal input parameters.  An
output parameter is effectively a variable that starts out NULL;
it should be assigned to during the execution of the function.
The final value of the parameter is what is returned.  For instance,
the sales-tax example could also be done this way:

```
CREATE FUNCTION sales_tax(subtotal real, OUT tax real) AS $$
BEGIN
tax := subtotal * 0.06;
END;
$$ LANGUAGE plpgsql;
```

Notice that we omitted `RETURNS real` — we could have
included it, but it would be redundant.

To call a function with `OUT` parameters, omit the
output parameter(s) in the function call:

```
SELECT sales_tax(100.00);
```

Output parameters are most useful when returning multiple values.
A trivial example is:

```
CREATE FUNCTION sum_n_product(x int, y int, OUT sum int, OUT prod int) AS $$
BEGIN
sum := x + y;
prod := x * y;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM sum_n_product(2, 4);
sum | prod
-----+------
6 |    8
```

As discussed in [xfunc-output-parameters](#xfunc-output-parameters), this
effectively creates an anonymous record type for the function's
results.  If a `RETURNS` clause is given, it must say
`RETURNS record`.

This also works with procedures, for example:

```
CREATE PROCEDURE sum_n_product(x int, y int, OUT sum int, OUT prod int) AS $$
BEGIN
sum := x + y;
prod := x * y;
END;
$$ LANGUAGE plpgsql;
```

In a call to a procedure, all the parameters must be specified.  For
output parameters, `NULL` may be specified when
calling the procedure from plain SQL:

```
CALL sum_n_product(2, 4, NULL, NULL);
sum | prod
-----+------
6 |    8
```

However, when calling a procedure
from PL/pgSQL, you should instead write a
variable for any output parameter; the variable will receive the result
of the call.  See [plpgsql-statements-calling-procedure](#plpgsql-statements-calling-procedure)
for details.

Another way to declare a PL/pgSQL function
is with `RETURNS TABLE`, for example:

```
CREATE FUNCTION extended_sales(p_itemno int)
RETURNS TABLE(quantity int, total numeric) AS $$
BEGIN
RETURN QUERY SELECT s.quantity, s.quantity * s.price FROM sales AS s
WHERE s.itemno = p_itemno;
END;
$$ LANGUAGE plpgsql;
```

This is exactly equivalent to declaring one or more `OUT`
parameters and specifying `RETURNS SETOF
`sometype``.

When the return type of a PL/pgSQL function
is declared as a polymorphic type (see
[extend-types-polymorphic](#extend-types-polymorphic)), a special
parameter `$0` is created.  Its data type is the actual
return type of the function, as deduced from the actual input types.
This allows the function to access its actual return type
as shown in [plpgsql-declaration-type](#plpgsql-declaration-type).
`$0` is initialized to null and can be modified by
the function, so it can be used to hold the return value if desired,
though that is not required.  `$0` can also be
given an alias.  For example, this function works on any data type
that has a `+` operator:

```
CREATE FUNCTION add_three_values(v1 anyelement, v2 anyelement, v3 anyelement)
RETURNS anyelement AS $$
DECLARE
result ALIAS FOR $0;
BEGIN
result := v1 + v2 + v3;
RETURN result;
END;
$$ LANGUAGE plpgsql;
```

The same effect can be obtained by declaring one or more output parameters as
polymorphic types.  In this case the
special `$0` parameter is not used; the output
parameters themselves serve the same purpose.  For example:

```
CREATE FUNCTION add_three_values(v1 anyelement, v2 anyelement, v3 anyelement,
OUT sum anyelement)
AS $$
BEGIN
sum := v1 + v2 + v3;
END;
$$ LANGUAGE plpgsql;
```

In practice it might be more useful to declare a polymorphic function
using the `anycompatible` family of types, so that automatic
promotion of the input arguments to a common type will occur.
For example:

```
CREATE FUNCTION add_three_values(v1 anycompatible, v2 anycompatible, v3 anycompatible)
RETURNS anycompatible AS $$
BEGIN
RETURN v1 + v2 + v3;
END;
$$ LANGUAGE plpgsql;
```

With this example, a call such as

```
SELECT add_three_values(1, 2, 4.7);
```

will work, automatically promoting the integer inputs to numeric.
The function using `anyelement` would require you to
cast the three inputs to the same type manually.

### `ALIAS`

```
`newname` ALIAS FOR `oldname`;
```

The `ALIAS` syntax is more general than is suggested in the
previous section: you can declare an alias for any variable, not just
function parameters.  The main practical use for this is to assign
a different name for variables with predetermined names, such as
`NEW` or `OLD` within
a trigger function.

Examples:

```
DECLARE
prior ALIAS FOR old;
updated ALIAS FOR new;
```

Since `ALIAS` creates two different ways to name the same
object, unrestricted use can be confusing.  It's best to use it only
for the purpose of overriding predetermined names.

### Copying Types

```
`variable`%TYPE
```

`%TYPE` provides the data type of a variable or
table column. You can use this to declare variables that will hold
database values. For example, let's say you have a column named
`user_id` in your `users`
table. To declare a variable with the same data type as
`users.user_id` you write:

```
user_id users.user_id%TYPE;
```

By using `%TYPE` you don't need to know the data
type of the structure you are referencing, and most importantly,
if the data type of the referenced item changes in the future (for
instance: you change the type of `user_id`
from `integer` to `real`), you might not need
to change your function definition.

`%TYPE` is particularly valuable in polymorphic
functions, since the data types needed for internal variables can
change from one call to the next.  Appropriate variables can be
created by applying `%TYPE` to the function's
arguments or result placeholders.

### Row Types

```
`name` `table_name``%ROWTYPE`;
`name` `composite_type_name`;
```

A variable of a composite type is called a *row*
variable (or *row-type* variable).  Such a variable
can hold a whole row of a `SELECT` or `FOR`
query result, so long as that query's column set matches the
declared type of the variable.
The individual fields of the row value
are accessed using the usual dot notation, for example
`rowvar.field`.

A row variable can be declared to have the same type as the rows of
an existing table or view, by using the
`table_name``%ROWTYPE`
notation; or it can be declared by giving a composite type's name.
(Since every table has an associated composite type of the same name,
it actually does not matter in PostgreSQL whether you
write `%ROWTYPE` or not.  But the form with
`%ROWTYPE` is more portable.)

Parameters to a function can be
composite types (complete table rows). In that case, the
corresponding identifier `$`n`` will be a row variable, and fields can
be selected from it, for example `$1.user_id`.

Here is an example of using composite types.  `table1`
and `table2` are existing tables having at least the
mentioned fields:

```
CREATE FUNCTION merge_fields(t_row table1) RETURNS text AS $$
DECLARE
t2_row table2%ROWTYPE;
BEGIN
SELECT * INTO t2_row FROM table2 WHERE ... ;
RETURN t_row.f1 || t2_row.f3 || t_row.f5 || t2_row.f7;
END;
$$ LANGUAGE plpgsql;

SELECT merge_fields(t.*) FROM table1 t WHERE ... ;
```

### Record Types

```
`name` RECORD;
```

Record variables are similar to row-type variables, but they have no
predefined structure.  They take on the actual row structure of the
row they are assigned during a `SELECT` or `FOR` command.  The substructure
of a record variable can change each time it is assigned to.
A consequence of this is that until a record variable is first assigned
to, it has no substructure, and any attempt to access a
field in it will draw a run-time error.

Note that `RECORD` is not a true data type, only a placeholder.
One should also realize that when a PL/pgSQL
function is declared to return type `record`, this is not quite the
same concept as a record variable, even though such a function might
use a record variable to hold its result.  In both cases the actual row
structure is unknown when the function is written, but for a function
returning `record` the actual structure is determined when the
calling query is parsed, whereas a record variable can change its row
structure on-the-fly.

### Collation of PL/pgSQL Variables

When a PL/pgSQL function has one or more
parameters of collatable data types, a collation is identified for each
function call depending on the collations assigned to the actual
arguments, as described in [collation](#collation).  If a collation is
successfully identified (i.e., there are no conflicts of implicit
collations among the arguments) then all the collatable parameters are
treated as having that collation implicitly.  This will affect the
behavior of collation-sensitive operations within the function.
For example, consider

```
CREATE FUNCTION less_than(a text, b text) RETURNS boolean AS $$
BEGIN
RETURN a  0 FROM my_table THEN ...
```

since the `expression`
between `IF` and `THEN` is parsed as
though it were `SELECT count(*) > 0 FROM my_table`.
The `SELECT` must produce a single column, and not
more than one row.  (If it produces no rows, the result is taken as
NULL.)

## Basic Statements

In this section and the following ones, we describe all the statement
types that are explicitly understood by
PL/pgSQL.
Anything not recognized as one of these statement types is presumed
to be an SQL command and is sent to the main database engine to execute,
as described in [plpgsql-statements-general-sql](#plpgsql-statements-general-sql).

### Assignment

An assignment of a value to a PL/pgSQL
variable is written as:

```
`variable` { := | = } `expression`;
```

As explained previously, the expression in such a statement is evaluated
by means of an SQL `SELECT` command sent to the main
database engine.  The expression must yield a single value (possibly
a row value, if the variable is a row or record variable).  The target
variable can be a simple variable (optionally qualified with a block
name), a field of a row or record target, or an element or slice of
an array target.  Equal (`=`) can be
used instead of PL/SQL-compliant `:=`.

If the expression's result data type doesn't match the variable's
data type, the value will be coerced as though by an assignment cast
(see [typeconv-query](#typeconv-query)).  If no assignment cast is known
for the pair of data types involved, the PL/pgSQL
interpreter will attempt to convert the result value textually, that is
by applying the result type's output function followed by the variable
type's input function.  Note that this could result in run-time errors
generated by the input function, if the string form of the result value
is not acceptable to the input function.

Examples:

```
tax := subtotal * 0.06;
my_record.user_id := 20;
my_array[j] := 20;
my_array[1:3] := array[1,2,3];
complex_array[n].realpart = 12.3;
```

### Executing SQL Commands

In general, any SQL command that does not return rows can be executed
within a PL/pgSQL function just by writing
the command.  For example, you could create and fill a table by writing

```
CREATE TABLE mytable (id int primary key, data text);
INSERT INTO mytable VALUES (1,'one'), (2,'two');
```

If the command does return rows (for example `SELECT`,
or `INSERT`/`UPDATE`/`DELETE`
with `RETURNING`), there are two ways to proceed.
When the command will return at most one row, or you only care about
the first row of output, write the command as usual but add
an `INTO` clause to capture the output, as described
in [plpgsql-statements-sql-onerow](#plpgsql-statements-sql-onerow).
To process all of the output rows, write the command as the data
source for a `FOR` loop, as described in
[plpgsql-records-iterating](#plpgsql-records-iterating).

Usually it is not sufficient just to execute statically-defined SQL
commands.  Typically you'll want a command to use varying data values,
or even to vary in more fundamental ways such as by using different
table names at different times.  Again, there are two ways to proceed
depending on the situation.

PL/pgSQL variable values can be
automatically inserted into optimizable SQL commands, which
are `SELECT`, `INSERT`,
`UPDATE`, `DELETE`,
`MERGE`, and certain
utility commands that incorporate one of these, such
as `EXPLAIN` and `CREATE TABLE ... AS
SELECT`.  In these commands,
any PL/pgSQL variable name appearing
in the command text is replaced by a query parameter, and then the
current value of the variable is provided as the parameter value
at run time.  This is exactly like the processing described earlier
for expressions; for details see [plpgsql-var-subst](#plpgsql-var-subst).

When executing an optimizable SQL command in this way,
PL/pgSQL may cache and re-use the execution
plan for the command, as discussed in
[plpgsql-plan-caching](#plpgsql-plan-caching).

Non-optimizable SQL commands (also called utility commands) are not
capable of accepting query parameters.  So automatic substitution
of PL/pgSQL variables does not work in such
commands.  To include non-constant text in a utility command executed
from PL/pgSQL, you must build the utility
command as a string and then `EXECUTE` it, as
discussed in [plpgsql-statements-executing-dyn](#plpgsql-statements-executing-dyn).

`EXECUTE` must also be used if you want to modify
the command in some other way than supplying a data value, for example
by changing a table name.

Sometimes it is useful to evaluate an expression or `SELECT`
query but discard the result, for example when calling a function
that has side-effects but no useful result value.  To do
this in PL/pgSQL, use the
`PERFORM` statement:

```
PERFORM `query`;
```

This executes `query` and discards the
result.  Write the `query` the same
way you would write an SQL `SELECT` command, but replace the
initial keyword `SELECT` with `PERFORM`.
For `WITH` queries, use `PERFORM` and then
place the query in parentheses.  (In this case, the query can only
return one row.)
PL/pgSQL variables will be
substituted into the query just as described above,
and the plan is cached in the same way.  Also, the special variable
`FOUND` is set to true if the query produced at
least one row, or false if it produced no rows (see
[plpgsql-statements-diagnostics](#plpgsql-statements-diagnostics)).

> **Note:**

> One might expect that writing `SELECT` directly
> would accomplish this result, but at
> present the only accepted way to do it is
> `PERFORM`.  An SQL command that can return rows,
> such as `SELECT`, will be rejected as an error
> unless it has an `INTO` clause as discussed in the
> next section.
>

An example:

```
PERFORM create_mv('cs_session_page_requests_mv', my_query);
```

### Executing a Command with a Single-Row Result

The result of an SQL command yielding a single row (possibly of multiple
columns) can be assigned to a record variable, row-type variable, or list
of scalar variables.  This is done by writing the base SQL command and
adding an `INTO` clause.  For example,

```
SELECT `select_expressions` INTO STRICT `target` FROM ...;
INSERT ... RETURNING `expressions` INTO STRICT `target`;
UPDATE ... RETURNING `expressions` INTO STRICT `target`;
DELETE ... RETURNING `expressions` INTO STRICT `target`;
```

where `target` can be a record variable, a row
variable, or a comma-separated list of simple variables and
record/row fields.
PL/pgSQL variables will be
substituted into the rest of the command (that is, everything but the
`INTO` clause) just as described above,
and the plan is cached in the same way.
This works for `SELECT`,
`INSERT`/`UPDATE`/`DELETE` with
`RETURNING`, and certain utility commands
that return row sets, such as `EXPLAIN`.
Except for the `INTO` clause, the SQL command is the same
as it would be written outside PL/pgSQL.

> **Tip:**

> Note that this interpretation of `SELECT` with `INTO`
> is quite different from PostgreSQL's regular
> `SELECT INTO` command, wherein the `INTO`
> target is a newly created table.  If you want to create a table from a
> `SELECT` result inside a
> PL/pgSQL function, use the syntax
> `CREATE TABLE ... AS SELECT`.
>

If a row variable or a variable list is used as target,
the command's result columns
must exactly match the structure of the target as to number and data
types, or else a run-time error
occurs.  When a record variable is the target, it automatically
configures itself to the row type of the command's result columns.

The `INTO` clause can appear almost anywhere in the SQL
command.  Customarily it is written either just before or just after
the list of `select_expressions` in a
`SELECT` command, or at the end of the command for other
command types.  It is recommended that you follow this convention
in case the PL/pgSQL parser becomes
stricter in future versions.

If `STRICT` is not specified in the `INTO`
clause, then `target` will be set to the first
row returned by the command, or to nulls if the command returned no rows.
(Note that "the first row" is not
well-defined unless you've used `ORDER BY`.)  Any result rows
after the first row are discarded.
You can check the special `FOUND` variable (see
[plpgsql-statements-diagnostics](#plpgsql-statements-diagnostics)) to
determine whether a row was returned:

```
SELECT * INTO myrec FROM emp WHERE empname = myname;
IF NOT FOUND THEN
RAISE EXCEPTION 'employee % not found', myname;
END IF;
```

If the `STRICT` option is specified, the command must
return exactly one row or a run-time error will be reported, either
`NO_DATA_FOUND` (no rows) or `TOO_MANY_ROWS`
(more than one row). You can use an exception block if you wish
to catch the error, for example:

```
BEGIN
SELECT * INTO STRICT myrec FROM emp WHERE empname = myname;
EXCEPTION
WHEN NO_DATA_FOUND THEN
RAISE EXCEPTION 'employee % not found', myname;
WHEN TOO_MANY_ROWS THEN
RAISE EXCEPTION 'employee % not unique', myname;
END;
```

Successful execution of a command with `STRICT`
always sets `FOUND` to true.

For `INSERT`/`UPDATE`/`DELETE` with
`RETURNING`, PL/pgSQL reports
an error for more than one returned row, even when
`STRICT` is not specified.  This is because there
is no option such as `ORDER BY` with which to determine
which affected row should be returned.

If `print_strict_params` is enabled for the function,
then when an error is thrown because the requirements
of `STRICT` are not met, the `DETAIL` part of
the error message will include information about the parameters
passed to the command.
You can change the `print_strict_params`
setting for all functions by setting
`plpgsql.print_strict_params`, though only subsequent
function compilations will be affected.  You can also enable it
on a per-function basis by using a compiler option, for example:

```
CREATE FUNCTION get_userid(username text) RETURNS int
AS $$
#print_strict_params on
DECLARE
userid int;
BEGIN
SELECT users.userid INTO STRICT userid
FROM users WHERE users.username = get_userid.username;
RETURN userid;
END;
$$ LANGUAGE plpgsql;
```

On failure, this function might produce an error message such as

```
ERROR:  query returned no rows
DETAIL:  parameters: username = 'nosuchuser'
CONTEXT:  PL/pgSQL function get_userid(text) line 6 at SQL statement
```

> **Note:**

> The `STRICT` option matches the behavior of
> Oracle PL/SQL's `SELECT INTO` and related statements.
>

### Executing Dynamic Commands

Oftentimes you will want to generate dynamic commands inside your
PL/pgSQL functions, that is, commands
that will involve different tables or different data types each
time they are executed.  PL/pgSQL's
normal attempts to cache plans for commands (as discussed in
[plpgsql-plan-caching](#plpgsql-plan-caching)) will not work in such
scenarios.  To handle this sort of problem, the
`EXECUTE` statement is provided:

```
EXECUTE `command-string`  INTO STRICT `target`   USING `expression` , ...  ;
```

where `command-string` is an expression
yielding a string (of type `text`) containing the
command to be executed.  The optional `target`
is a record variable, a row variable, or a comma-separated list of
simple variables and record/row fields, into which the results of
the command will be stored.  The optional `USING` expressions
supply values to be inserted into the command.

No substitution of PL/pgSQL variables is done on the
computed command string.  Any required variable values must be inserted
in the command string as it is constructed; or you can use parameters
as described below.

Also, there is no plan caching for commands executed via
`EXECUTE`.  Instead, the command is always planned
each time the statement is run. Thus the command
string can be dynamically created within the function to perform
actions on different tables and columns.

The `INTO` clause specifies where the results of
an SQL command returning rows should be assigned. If a row variable
or variable list is provided, it must exactly match the structure
of the command's results; if a
record variable is provided, it will configure itself to match the
result structure automatically. If multiple rows are returned,
only the first will be assigned to the `INTO`
variable(s). If no rows are returned, NULL is assigned to the
`INTO` variable(s). If no `INTO`
clause is specified, the command results are discarded.

If the `STRICT` option is given, an error is reported
unless the command produces exactly one row.

The command string can use parameter values, which are referenced
in the command as `$1`, `$2`, etc.
These symbols refer to values supplied in the `USING`
clause.  This method is often preferable to inserting data values
into the command string as text: it avoids run-time overhead of
converting the values to text and back, and it is much less prone
to SQL-injection attacks since there is no need for quoting or escaping.
An example is:

```
EXECUTE 'SELECT count(*) FROM mytable WHERE inserted_by = $1 AND inserted  **Note:**

> The PL/pgSQL
> `EXECUTE` statement is not related to the
> [`EXECUTE`](#sql-execute) SQL
> statement supported by the
> PostgreSQL server. The server's
> `EXECUTE` statement cannot be used directly within
> PL/pgSQL functions (and is not needed).
>

## Control Structures

Control structures are probably the most useful (and
important) part of PL/pgSQL. With
PL/pgSQL's control structures,
you can manipulate PostgreSQL data in a very
flexible and powerful way.

### Returning from a Function

There are two commands available that allow you to return data
from a function: `RETURN` and `RETURN
NEXT`.

#### `RETURN`

```
RETURN `expression`;
```

`RETURN` with an expression terminates the
function and returns the value of
`expression` to the caller.  This form
is used for PL/pgSQL functions that do
not return a set.

In a function that returns a scalar type, the expression's result will
automatically be cast into the function's return type as described for
assignments.  But to return a composite (row) value, you must write an
expression delivering exactly the requested column set.  This may
require use of explicit casting.

If you declared the function with output parameters, write just
`RETURN` with no expression.  The current values
of the output parameter variables will be returned.

If you declared the function to return `void`, a
`RETURN` statement can be used to exit the function
early; but do not write an expression following
`RETURN`.

The return value of a function cannot be left undefined. If
control reaches the end of the top-level block of the function
without hitting a `RETURN` statement, a run-time
error will occur.  This restriction does not apply to functions
with output parameters and functions returning `void`,
however.  In those cases a `RETURN` statement is
automatically executed if the top-level block finishes.

Some examples:

```
-- functions returning a scalar type
RETURN 1 + 2;
RETURN scalar_var;

-- functions returning a composite type
RETURN composite_type_var;
RETURN (1, 2, 'three'::text);  -- must cast columns to correct types
```

#### `RETURN NEXT` and `RETURN QUERY`

```
RETURN NEXT `expression`;
RETURN QUERY `query`;
RETURN QUERY EXECUTE `command-string`  USING `expression` , ...  ;
```

When a PL/pgSQL function is declared to return
`SETOF `sometype``, the procedure
to follow is slightly different.  In that case, the individual
items to return are specified by a sequence of `RETURN
NEXT` or `RETURN QUERY` commands, and
then a final `RETURN` command with no argument
is used to indicate that the function has finished executing.
`RETURN NEXT` can be used with both scalar and
composite data types; with a composite result type, an entire
"table" of results will be returned.
`RETURN QUERY` appends the results of executing
a query to the function's result set. `RETURN
NEXT` and `RETURN QUERY` can be freely
intermixed in a single set-returning function, in which case
their results will be concatenated.

`RETURN NEXT` and `RETURN
QUERY` do not actually return from the function —
they simply append zero or more rows to the function's result
set.  Execution then continues with the next statement in the
PL/pgSQL function.  As successive
`RETURN NEXT` or `RETURN
QUERY` commands are executed, the result set is built
up.  A final `RETURN`, which should have no
argument, causes control to exit the function (or you can just
let control reach the end of the function).

`RETURN QUERY` has a variant
`RETURN QUERY EXECUTE`, which specifies the
query to be executed dynamically.  Parameter expressions can
be inserted into the computed query string via `USING`,
in just the same way as in the `EXECUTE` command.

If you declared the function with output parameters, write just
`RETURN NEXT` with no expression.  On each
execution, the current values of the output parameter
variable(s) will be saved for eventual return as a row of the
result.  Note that you must declare the function as returning
`SETOF record` when there are multiple output
parameters, or `SETOF `sometype``
when there is just one output parameter of type
`sometype`, in order to create a set-returning
function with output parameters.

Here is an example of a function using `RETURN
NEXT`:

```
CREATE TABLE foo (fooid INT, foosubid INT, fooname TEXT);
INSERT INTO foo VALUES (1, 2, 'three');
INSERT INTO foo VALUES (4, 5, 'six');

CREATE OR REPLACE FUNCTION get_all_foo() RETURNS SETOF foo AS
$BODY$
DECLARE
r foo%rowtype;
BEGIN
FOR r IN
SELECT * FROM foo WHERE fooid > 0
LOOP
-- can do some processing here
RETURN NEXT r; -- return current row of SELECT
END LOOP;
RETURN;
END;
$BODY$
LANGUAGE plpgsql;

SELECT * FROM get_all_foo();
```

Here is an example of a function using `RETURN
QUERY`:

```
CREATE FUNCTION get_available_flightid(date) RETURNS SETOF integer AS
$BODY$
BEGIN
RETURN QUERY SELECT flightid
FROM flight
WHERE flightdate >= $1
AND flightdate  **Note:**

> The current implementation of `RETURN NEXT`
> and `RETURN QUERY` stores the entire result set
> before returning from the function, as discussed above.  That
> means that if a PL/pgSQL function produces a
> very large result set, performance might be poor: data will be
> written to disk to avoid memory exhaustion, but the function
> itself will not return until the entire result set has been
> generated.  A future version of PL/pgSQL might
> allow users to define set-returning functions
> that do not have this limitation.  Currently, the point at
> which data begins being written to disk is controlled by the
> [guc-work-mem](#guc-work-mem)
> configuration variable.  Administrators who have sufficient
> memory to store larger result sets in memory should consider
> increasing this parameter.
>

### Returning from a Procedure

A procedure does not have a return value.  A procedure can therefore end
without a `RETURN` statement.  If you wish to use
a `RETURN` statement to exit the code early, write
just `RETURN` with no expression.

If the procedure has output parameters, the final values of the output
parameter variables will be returned to the caller.

### Calling a Procedure

A PL/pgSQL function, procedure,
or `DO` block can call a procedure
using `CALL`.  Output parameters are handled
differently from the way that `CALL` works in plain
SQL.  Each `OUT` or `INOUT`
parameter of the procedure must
correspond to a variable in the `CALL` statement, and
whatever the procedure returns is assigned back to that variable after
it returns.  For example:

```
CREATE PROCEDURE triple(INOUT x int)
LANGUAGE plpgsql
AS $$
BEGIN
x := x * 3;
END;
$$;

DO $$
DECLARE myvar int := 5;
BEGIN
CALL triple(myvar);
RAISE NOTICE 'myvar = %', myvar;  -- prints 15
END;
$$;
```

The variable corresponding to an output parameter can be a simple
variable or a field of a composite-type variable.  Currently,
it cannot be an element of an array.

### Conditionals

`IF` and `CASE` statements let you execute
alternative commands based on certain conditions.
PL/pgSQL has three forms of `IF`:

- `IF ... THEN ... END IF`
- `IF ... THEN ... ELSE ... END IF`
- `IF ... THEN ... ELSIF ... THEN ... ELSE ... END IF`

and two forms of `CASE`:

- `CASE ... WHEN ... THEN ... ELSE ... END CASE`
- `CASE WHEN ... THEN ... ELSE ... END CASE`

#### `IF-THEN`

```
IF `boolean-expression` THEN
`statements`
END IF;
```

`IF-THEN` statements are the simplest form of
`IF`. The statements between
`THEN` and `END IF` will be
executed if the condition is true. Otherwise, they are
skipped.

Example:

```
IF v_user_id <> 0 THEN
UPDATE users SET email = v_email WHERE user_id = v_user_id;
END IF;
```

#### `IF-THEN-ELSE`

```
IF `boolean-expression` THEN
`statements`
ELSE
`statements`
END IF;
```

`IF-THEN-ELSE` statements add to
`IF-THEN` by letting you specify an
alternative set of statements that should be executed if the
condition is not true.  (Note this includes the case where the
condition evaluates to NULL.)

Examples:

```
IF parentid IS NULL OR parentid = ''
THEN
RETURN fullname;
ELSE
RETURN hp_true_filename(parentid) || '/' || fullname;
END IF;
```

```
IF v_count > 0 THEN
INSERT INTO users_count (count) VALUES (v_count);
RETURN 't';
ELSE
RETURN 'f';
END IF;
```

#### `IF-THEN-ELSIF`

```
IF `boolean-expression` THEN
`statements`
ELSIF `boolean-expression` THEN
`statements`
ELSIF `boolean-expression` THEN
`statements`
...

ELSE
`statements`
END IF;
```

Sometimes there are more than just two alternatives.
`IF-THEN-ELSIF` provides a convenient
method of checking several alternatives in turn.
The `IF` conditions are tested successively
until the first one that is true is found.  Then the
associated statement(s) are executed, after which control
passes to the next statement after `END IF`.
(Any subsequent `IF` conditions are *not*
tested.)  If none of the `IF` conditions is true,
then the `ELSE` block (if any) is executed.

Here is an example:

```
IF number = 0 THEN
result := 'zero';
ELSIF number > 0 THEN
result := 'positive';
ELSIF number >
LOOP
`statements`
END LOOP  `label` ;
```

`LOOP` defines an unconditional loop that is repeated
indefinitely until terminated by an `EXIT` or
`RETURN` statement.  The optional
`label` can be used by `EXIT`
and `CONTINUE` statements within nested loops to
specify which loop those statements refer to.

#### `EXIT`

```
EXIT  `label`   WHEN `boolean-expression` ;
```

If no `label` is given, the innermost
loop is terminated and the statement following `END
LOOP` is executed next.  If `label`
is given, it must be the label of the current or some outer
level of nested loop or block. Then the named loop or block is
terminated and control continues with the statement after the
loop's/block's corresponding `END`.

If `WHEN` is specified, the loop exit occurs only if
`boolean-expression` is true. Otherwise, control passes
to the statement after `EXIT`.

`EXIT` can be used with all types of loops; it is
not limited to use with unconditional loops.

When used with a
`BEGIN` block, `EXIT` passes
control to the next statement after the end of the block.
Note that a label must be used for this purpose; an unlabeled
`EXIT` is never considered to match a
`BEGIN` block.  (This is a change from
pre-8.4 releases of PostgreSQL, which
would allow an unlabeled `EXIT` to match
a `BEGIN` block.)

Examples:

```
LOOP
-- some computations
IF count > 0 THEN
EXIT;  -- exit loop
END IF;
END LOOP;

LOOP
-- some computations
EXIT WHEN count > 0;  -- same result as previous example
END LOOP;

>
BEGIN
-- some computations
IF stocks > 100000 THEN
EXIT ablock;  -- causes exit from the BEGIN block
END IF;
-- computations here will be skipped when stocks > 100000
END;
```

#### `CONTINUE`

```
CONTINUE  `label`   WHEN `boolean-expression` ;
```

If no `label` is given, the next iteration of
the innermost loop is begun. That is, all statements remaining
in the loop body are skipped, and control returns
to the loop control expression (if any) to determine whether
another loop iteration is needed.
If `label` is present, it
specifies the label of the loop whose execution will be
continued.

If `WHEN` is specified, the next iteration of the
loop is begun only if `boolean-expression` is
true. Otherwise, control passes to the statement after
`CONTINUE`.

`CONTINUE` can be used with all types of loops; it
is not limited to use with unconditional loops.

Examples:

```
LOOP
-- some computations
EXIT WHEN count > 100;
CONTINUE WHEN count >
WHILE `boolean-expression` LOOP
`statements`
END LOOP  `label` ;
```

The `WHILE` statement repeats a
sequence of statements so long as the
`boolean-expression`
evaluates to true.  The expression is checked just before
each entry to the loop body.

For example:

```
WHILE amount_owed > 0 AND gift_certificate_balance > 0 LOOP
-- some computations here
END LOOP;

WHILE NOT done LOOP
-- some computations here
END LOOP;
```

#### `FOR` (Integer Variant)

```
>
FOR `name` IN  REVERSE  `expression` .. `expression`  BY `expression`  LOOP
`statements`
END LOOP  `label` ;
```

This form of `FOR` creates a loop that iterates over a range
of integer values. The variable
`name` is automatically defined as type
`integer` and exists only inside the loop (any existing
definition of the variable name is ignored within the loop).
The two expressions giving
the lower and upper bound of the range are evaluated once when entering
the loop. If the `BY` clause isn't specified the iteration
step is 1, otherwise it's the value specified in the `BY`
clause, which again is evaluated once on loop entry.
If `REVERSE` is specified then the step value is
subtracted, rather than added, after each iteration.

Some examples of integer `FOR` loops:

```
FOR i IN 1..10 LOOP
-- i will take on the values 1,2,3,4,5,6,7,8,9,10 within the loop
END LOOP;

FOR i IN REVERSE 10..1 LOOP
-- i will take on the values 10,9,8,7,6,5,4,3,2,1 within the loop
END LOOP;

FOR i IN REVERSE 10..1 BY 2 LOOP
-- i will take on the values 10,8,6,4,2 within the loop
END LOOP;
```

If the lower bound is greater than the upper bound (or less than,
in the `REVERSE` case), the loop body is not
executed at all.  No error is raised.

If a `label` is attached to the
`FOR` loop then the integer loop variable can be
referenced with a qualified name, using that
`label`.

### Looping through Query Results

Using a different type of `FOR` loop, you can iterate through
the results of a query and manipulate that data
accordingly. The syntax is:

```
>
FOR `target` IN `query` LOOP
`statements`
END LOOP  `label` ;
```

The `target` is a record variable, row variable,
or comma-separated list of scalar variables.
The `target` is successively assigned each row
resulting from the `query` and the loop body is
executed for each row. Here is an example:

```
CREATE FUNCTION refresh_mviews() RETURNS integer AS $$
DECLARE
mviews RECORD;
BEGIN
RAISE NOTICE 'Refreshing all materialized views...';

FOR mviews IN
SELECT n.nspname AS mv_schema,
c.relname AS mv_name,
pg_catalog.pg_get_userbyid(c.relowner) AS owner
FROM pg_catalog.pg_class c
LEFT JOIN pg_catalog.pg_namespace n ON (n.oid = c.relnamespace)
WHERE c.relkind = 'm'
ORDER BY 1
LOOP

-- Now "mviews" has one record with information about the materialized view

RAISE NOTICE 'Refreshing materialized view %.% (owner: %)...',
quote_ident(mviews.mv_schema),
quote_ident(mviews.mv_name),
quote_ident(mviews.owner);
EXECUTE format('REFRESH MATERIALIZED VIEW %I.%I', mviews.mv_schema, mviews.mv_name);
END LOOP;

RAISE NOTICE 'Done refreshing materialized views.';
RETURN 1;
END;
$$ LANGUAGE plpgsql;
```

If the loop is terminated by an `EXIT` statement, the last
assigned row value is still accessible after the loop.

The `query` used in this type of `FOR`
statement can be any SQL command that returns rows to the caller:
`SELECT` is the most common case,
but you can also use `INSERT`, `UPDATE`, or
`DELETE` with a `RETURNING` clause.  Some utility
commands such as `EXPLAIN` will work too.

PL/pgSQL variables are replaced by query parameters,
and the query plan is cached for possible re-use, as discussed in
detail in [plpgsql-var-subst](#plpgsql-var-subst) and
[plpgsql-plan-caching](#plpgsql-plan-caching).

The `FOR-IN-EXECUTE` statement is another way to iterate over
rows:

```
>
FOR `target` IN EXECUTE `text_expression`  USING `expression` , ...   LOOP
`statements`
END LOOP  `label` ;
```

This is like the previous form, except that the source query
is specified as a string expression, which is evaluated and replanned
on each entry to the `FOR` loop.  This allows the programmer to
choose the speed of a preplanned query or the flexibility of a dynamic
query, just as with a plain `EXECUTE` statement.
As with `EXECUTE`, parameter values can be inserted
into the dynamic command via `USING`.

Another way to specify the query whose results should be iterated
through is to declare it as a cursor.  This is described in
[plpgsql-cursor-for-loop](#plpgsql-cursor-for-loop).

### Looping through Arrays

The `FOREACH` loop is much like a `FOR` loop,
but instead of iterating through the rows returned by an SQL query,
it iterates through the elements of an array value.
(In general, `FOREACH` is meant for looping through
components of a composite-valued expression; variants for looping
through composites besides arrays may be added in future.)
The `FOREACH` statement to loop over an array is:

```
>
FOREACH `target`  SLICE `number`  IN ARRAY `expression` LOOP
`statements`
END LOOP  `label` ;
```

Without `SLICE`, or if `SLICE 0` is specified,
the loop iterates through individual elements of the array produced
by evaluating the `expression`.
The `target` variable is assigned each
element value in sequence, and the loop body is executed for each element.
Here is an example of looping through the elements of an integer
array:

```
CREATE FUNCTION sum(int[]) RETURNS int8 AS $$
DECLARE
s int8 := 0;
x int;
BEGIN
FOREACH x IN ARRAY $1
LOOP
s := s + x;
END LOOP;
RETURN s;
END;
$$ LANGUAGE plpgsql;
```

The elements are visited in storage order, regardless of the number of
array dimensions.  Although the `target` is
usually just a single variable, it can be a list of variables when
looping through an array of composite values (records).  In that case,
for each array element, the variables are assigned from successive
columns of the composite value.

With a positive `SLICE` value, `FOREACH`
iterates through slices of the array rather than single elements.
The `SLICE` value must be an integer constant not larger
than the number of dimensions of the array.  The
`target` variable must be an array,
and it receives successive slices of the array value, where each slice
is of the number of dimensions specified by `SLICE`.
Here is an example of iterating through one-dimensional slices:

```
CREATE FUNCTION scan_rows(int[]) RETURNS void AS $$
DECLARE
x int[];
BEGIN
FOREACH x SLICE 1 IN ARRAY $1
LOOP
RAISE NOTICE 'row = %', x;
END LOOP;
END;
$$ LANGUAGE plpgsql;

SELECT scan_rows(ARRAY[[1,2,3],[4,5,6],[7,8,9],[10,11,12]]);

NOTICE:  row = {1,2,3}
NOTICE:  row = {4,5,6}
NOTICE:  row = {7,8,9}
NOTICE:  row = {10,11,12}
```

### Trapping Errors

By default, any error occurring in a PL/pgSQL
function aborts execution of the function and the
surrounding transaction.  You can trap errors and recover
from them by using a `BEGIN` block with an
`EXCEPTION` clause.  The syntax is an extension of the
normal syntax for a `BEGIN` block:

```
>
DECLARE
`declarations`
BEGIN
`statements`
EXCEPTION
WHEN `condition`  OR `condition` ...  THEN
`handler_statements`
WHEN `condition`  OR `condition` ...  THEN
`handler_statements`
...
END;
```

If no error occurs, this form of block simply executes all the
`statements`, and then control passes
to the next statement after `END`.  But if an error
occurs within the `statements`, further
processing of the `statements` is
abandoned, and control passes to the `EXCEPTION` list.
The list is searched for the first `condition`
matching the error that occurred.  If a match is found, the
corresponding `handler_statements` are
executed, and then control passes to the next statement after
`END`.  If no match is found, the error propagates out
as though the `EXCEPTION` clause were not there at all:
the error can be caught by an enclosing block with
`EXCEPTION`, or if there is none it aborts processing
of the function.

The `condition` names can be any of
those shown in [errcodes-appendix](#errcodes-appendix).  A category
name matches any error within its category.  The special
condition name `OTHERS` matches every error type except
`QUERY_CANCELED` and `ASSERT_FAILURE`.
(It is possible, but often unwise, to trap those two error types
by name.)  Condition names are
not case-sensitive.  Also, an error condition can be specified
by `SQLSTATE` code; for example these are equivalent:

```
WHEN division_by_zero THEN ...
WHEN SQLSTATE '22012' THEN ...
```

If a new error occurs within the selected
`handler_statements`, it cannot be caught
by this `EXCEPTION` clause, but is propagated out.
A surrounding `EXCEPTION` clause could catch it.

When an error is caught by an `EXCEPTION` clause,
the local variables of the PL/pgSQL function
remain as they were when the error occurred, but all changes
to persistent database state within the block are rolled back.
As an example, consider this fragment:

```
INSERT INTO mytab(firstname, lastname) VALUES('Tom', 'Jones');
BEGIN
UPDATE mytab SET firstname = 'Joe' WHERE lastname = 'Jones';
x := x + 1;
y := x / 0;
EXCEPTION
WHEN division_by_zero THEN
RAISE NOTICE 'caught division_by_zero';
RETURN x;
END;
```

When control reaches the assignment to `y`, it will
fail with a `division_by_zero` error.  This will be caught by
the `EXCEPTION` clause.  The value returned in the
`RETURN` statement will be the incremented value of
`x`, but the effects of the `UPDATE` command will
have been rolled back.  The `INSERT` command preceding the
block is not rolled back, however, so the end result is that the database
contains `Tom Jones` not `Joe Jones`.

> **Tip:**

> A block containing an `EXCEPTION` clause is significantly
> more expensive to enter and exit than a block without one.  Therefore,
> don't use `EXCEPTION` without need.
>

## Cursors

Rather than executing a whole query at once, it is possible to set
up a *cursor* that encapsulates the query, and then read
the query result a few rows at a time. One reason for doing this is
to avoid memory overrun when the result contains a large number of
rows. (However, PL/pgSQL users do not normally need
to worry about that, since `FOR` loops automatically use a cursor
internally to avoid memory problems.) A more interesting usage is to
return a reference to a cursor that a function has created, allowing the
caller to read the rows. This provides an efficient way to return
large row sets from functions.

### Declaring Cursor Variables

All access to cursors in PL/pgSQL goes through
cursor variables, which are always of the special data type
`refcursor`.  One way to create a cursor variable
is just to declare it as a variable of type `refcursor`.
Another way is to use the cursor declaration syntax,
which in general is:

```
`name`   NO  SCROLL  CURSOR  ( `arguments` )  FOR `query`;
```

(`FOR` can be replaced by `IS` for
Oracle compatibility.)
If `SCROLL` is specified, the cursor will be capable of
scrolling backward; if `NO SCROLL` is specified, backward
fetches will be rejected; if neither specification appears, it is
query-dependent whether backward fetches will be allowed.
`arguments`, if specified, is a
comma-separated list of pairs ``name`
`datatype`` that define names to be
replaced by parameter values in the given query.  The actual
values to substitute for these names will be specified later,
when the cursor is opened.

Some examples:

```
DECLARE
curs1 refcursor;
curs2 CURSOR FOR SELECT * FROM tenk1;
curs3 CURSOR (key integer) FOR SELECT * FROM tenk1 WHERE unique1 = key;
```

All three of these variables have the data type `refcursor`,
but the first can be used with any query, while the second has
a fully specified query already *bound* to it, and the last
has a parameterized query bound to it.  (`key` will be
replaced by an integer parameter value when the cursor is opened.)
The variable `curs1`
is said to be *unbound* since it is not bound to
any particular query.

The `SCROLL` option cannot be used when the cursor's
query uses `FOR UPDATE/SHARE`.  Also, it is
best to use `NO SCROLL` with a query that involves
volatile functions.  The implementation of `SCROLL`
assumes that re-reading the query's output will give consistent
results, which a volatile function might not do.

### Opening Cursors

Before a cursor can be used to retrieve rows, it must be
*opened*. (This is the equivalent action to the SQL
command [`DECLARE
CURSOR`](#sql-declare).)
PL/pgSQL has
three forms of the `OPEN` statement, two of which use unbound
cursor variables while the third uses a bound cursor variable.

> **Note:**

> Bound cursor variables can also be used without explicitly opening the cursor,
> via the `FOR` statement described in
> [plpgsql-cursor-for-loop](#plpgsql-cursor-for-loop).
> A `FOR` loop will open the cursor and then
> close it again when the loop completes.
>

Opening a cursor involves creating a server-internal data structure
called a *portal*, which holds the execution
state for the cursor's query.  A portal has a name, which must be
unique within the session for the duration of the portal's existence.
By default, PL/pgSQL will assign a unique
name to each portal it creates.  However, if you assign a non-null
string value to a cursor variable, that string will be used as its
portal name.  This feature can be used as described in
[plpgsql-cursor-returning](#plpgsql-cursor-returning).

#### `OPEN FOR` `query`

```
OPEN `unbound_cursorvar`   NO  SCROLL  FOR `query`;
```

The cursor variable is opened and given the specified query to
execute.  The cursor cannot be open already, and it must have been
declared as an unbound cursor variable (that is, as a simple
`refcursor` variable).  The query must be a
`SELECT`, or something else that returns rows
(such as `EXPLAIN`).  The query
is treated in the same way as other SQL commands in
PL/pgSQL: PL/pgSQL
variable names are substituted, and the query plan is cached for
possible reuse.  When a PL/pgSQL
variable is substituted into the cursor query, the value that is
substituted is the one it has at the time of the `OPEN`;
subsequent changes to the variable will not affect the cursor's
behavior.
The `SCROLL` and `NO SCROLL`
options have the same meanings as for a bound cursor.

An example:

```
OPEN curs1 FOR SELECT * FROM foo WHERE key = mykey;
```

#### `OPEN FOR EXECUTE`

```
OPEN `unbound_cursorvar`   NO  SCROLL  FOR EXECUTE `query_string`
USING `expression` , ...  ;
```

The cursor variable is opened and given the specified query to
execute.  The cursor cannot be open already, and it must have been
declared as an unbound cursor variable (that is, as a simple
`refcursor` variable).  The query is specified as a string
expression, in the same way as in the `EXECUTE`
command.  As usual, this gives flexibility so the query plan can vary
from one run to the next (see [plpgsql-plan-caching](#plpgsql-plan-caching)),
and it also means that variable substitution is not done on the
command string. As with `EXECUTE`, parameter values
can be inserted into the dynamic command via
`format()` and `USING`.
The `SCROLL` and
`NO SCROLL` options have the same meanings as for a bound
cursor.

An example:

```
OPEN curs1 FOR EXECUTE format('SELECT * FROM %I WHERE col1 = $1',tabname) USING keyvalue;
```

In this example, the table name is inserted into the query via
`format()`.  The comparison value for `col1`
is inserted via a `USING` parameter, so it needs
no quoting.

#### Opening a Bound Cursor

```
OPEN `bound_cursorvar`  (  `argument_name` :=  `argument_value` , ... ) ;
```

This form of `OPEN` is used to open a cursor
variable whose query was bound to it when it was declared.  The
cursor cannot be open already.  A list of actual argument value
expressions must appear if and only if the cursor was declared to
take arguments.  These values will be substituted in the query.

The query plan for a bound cursor is always considered cacheable;
there is no equivalent of `EXECUTE` in this case.
Notice that `SCROLL` and `NO SCROLL` cannot be
specified in `OPEN`, as the cursor's scrolling
behavior was already determined.

Argument values can be passed using either *positional*
or *named* notation.  In positional
notation, all arguments are specified in order.  In named notation,
each argument's name is specified using `:=` to
separate it from the argument expression. Similar to calling
functions, described in [sql-syntax-calling-funcs](#sql-syntax-calling-funcs), it
is also allowed to mix positional and named notation.

Examples (these use the cursor declaration examples above):

```
OPEN curs2;
OPEN curs3(42);
OPEN curs3(key := 42);
```

Because variable substitution is done on a bound cursor's query,
there are really two ways to pass values into the cursor: either
with an explicit argument to `OPEN`, or implicitly by
referencing a PL/pgSQL variable in the query.
However, only variables declared before the bound cursor was
declared will be substituted into it.  In either case the value to
be passed is determined at the time of the `OPEN`.
For example, another way to get the same effect as the
`curs3` example above is

```
DECLARE
key integer;
curs4 CURSOR FOR SELECT * FROM tenk1 WHERE unique1 = key;
BEGIN
key := 42;
OPEN curs4;
```

### Using Cursors

Once a cursor has been opened, it can be manipulated with the
statements described here.

These manipulations need not occur in the same function that
opened the cursor to begin with.  You can return a `refcursor`
value out of a function and let the caller operate on the cursor.
(Internally, a `refcursor` value is simply the string name
of the portal containing the active query for the cursor.  This name
can be passed around, assigned to other `refcursor` variables,
and so on, without disturbing the portal.)

All portals are implicitly closed at transaction end.  Therefore
a `refcursor` value is usable to reference an open cursor
only until the end of the transaction.

#### `FETCH`

```
FETCH  `direction` { FROM | IN }  `cursor` INTO `target`;
```

`FETCH` retrieves the next row (in the indicated
direction) from the
cursor into a target, which might be a row variable, a record
variable, or a comma-separated list of simple variables, just like
`SELECT INTO`.  If there is no suitable row, the
target is set to NULL(s).  As with `SELECT
INTO`, the special variable `FOUND` can
be checked to see whether a row was obtained or not.  If no row is
obtained, the cursor is positioned after the last row or before the
first row, depending on the movement direction.

The `direction` clause can be any of the
variants allowed in the SQL [sql-fetch](#sql-fetch)
command except the ones that can fetch
more than one row; namely, it can be
`NEXT`,
`PRIOR`,
`FIRST`,
`LAST`,
`ABSOLUTE` `count`,
`RELATIVE` `count`,
`FORWARD`, or
`BACKWARD`.
Omitting `direction` is the same
as specifying `NEXT`.
In the forms using a `count`,
the `count` can be any integer-valued
expression (unlike the SQL `FETCH` command,
which only allows an integer constant).
`direction` values that require moving
backward are likely to fail unless the cursor was declared or opened
with the `SCROLL` option.

`cursor` must be the name of a `refcursor`
variable that references an open cursor portal.

Examples:

```
FETCH curs1 INTO rowvar;
FETCH curs2 INTO foo, bar, baz;
FETCH LAST FROM curs3 INTO x, y;
FETCH RELATIVE -2 FROM curs4 INTO x;
```

#### `MOVE`

```
MOVE  `direction` { FROM | IN }  `cursor`;
```

`MOVE` repositions a cursor without retrieving
any data. `MOVE` works like the
`FETCH` command, except it only repositions the
cursor and does not return the row moved to.
The `direction` clause can be any of the
variants allowed in the SQL [sql-fetch](#sql-fetch)
command, including those that can fetch more than one row;
the cursor is positioned to the last such row.
(However, the case in which the `direction`
clause is simply a `count` expression with
no key word is deprecated in PL/pgSQL.
That syntax is ambiguous with the case where
the `direction` clause is omitted
altogether, and hence it may fail if
the `count` is not a constant.)
As with `SELECT
INTO`, the special variable `FOUND` can
be checked to see whether there was a row to move to.  If there is no
such row, the cursor is positioned after the last row or before the
first row, depending on the movement direction.

Examples:

```
MOVE curs1;
MOVE LAST FROM curs3;
MOVE RELATIVE -2 FROM curs4;
MOVE FORWARD 2 FROM curs4;
```

#### `UPDATE/DELETE WHERE CURRENT OF`

```
UPDATE `table` SET ... WHERE CURRENT OF `cursor`;
DELETE FROM `table` WHERE CURRENT OF `cursor`;
```

When a cursor is positioned on a table row, that row can be updated
or deleted using the cursor to identify the row.  There are
restrictions on what the cursor's query can be (in particular,
no grouping) and it's best to use `FOR UPDATE` in the
cursor.  For more information see the
[sql-declare](#sql-declare)
reference page.

An example:

```
UPDATE foo SET dataval = myval WHERE CURRENT OF curs1;
```

#### `CLOSE`

```
CLOSE `cursor`;
```

`CLOSE` closes the portal underlying an open
cursor.  This can be used to release resources earlier than end of
transaction, or to free up the cursor variable to be opened again.

An example:

```
CLOSE curs1;
```

#### Returning Cursors

PL/pgSQL functions can return cursors to the
caller. This is useful to return multiple rows or columns,
especially with very large result sets.  To do this, the function
opens the cursor and returns the cursor name to the caller (or simply
opens the cursor using a portal name specified by or otherwise known
to the caller).  The caller can then fetch rows from the cursor. The
cursor can be closed by the caller, or it will be closed automatically
when the transaction closes.

The portal name used for a cursor can be specified by the
programmer or automatically generated.  To specify a portal name,
simply assign a string to the `refcursor` variable before
opening it.  The string value of the `refcursor` variable
will be used by `OPEN` as the name of the underlying portal.
However, if the `refcursor` variable's value is null
(as it will be by default), then
`OPEN` automatically generates a name that does not
conflict with any existing portal, and assigns it to the
`refcursor` variable.

> **Note:**

> Prior to PostgreSQL 16, bound cursor
> variables were initialized to contain their own names, rather
> than being left as null, so that the underlying portal name would
> be the same as the cursor variable's name by default.  This was
> changed because it created too much risk of conflicts between
> similarly-named cursors in different functions.
>

The following example shows one way a cursor name can be supplied by
the caller:

```
CREATE TABLE test (col text);
INSERT INTO test VALUES ('123');

CREATE FUNCTION reffunc(refcursor) RETURNS refcursor AS '
BEGIN
OPEN $1 FOR SELECT col FROM test;
RETURN $1;
END;
' LANGUAGE plpgsql;

BEGIN;
SELECT reffunc('funccursor');
FETCH ALL IN funccursor;
COMMIT;
```

The following example uses automatic cursor name generation:

```
CREATE FUNCTION reffunc2() RETURNS refcursor AS '
DECLARE
ref refcursor;
BEGIN
OPEN ref FOR SELECT col FROM test;
RETURN ref;
END;
' LANGUAGE plpgsql;

-- need to be in a transaction to use cursors.
BEGIN;
SELECT reffunc2();

reffunc2
--------------------

(1 row)

FETCH ALL IN "";
COMMIT;
```

The following example shows one way to return multiple cursors
from a single function:

```
CREATE FUNCTION myfunc(refcursor, refcursor) RETURNS SETOF refcursor AS $$
BEGIN
OPEN $1 FOR SELECT * FROM table_1;
RETURN NEXT $1;
OPEN $2 FOR SELECT * FROM table_2;
RETURN NEXT $2;
END;
$$ LANGUAGE plpgsql;

-- need to be in a transaction to use cursors.
BEGIN;

SELECT * FROM myfunc('a', 'b');

FETCH ALL FROM a;
FETCH ALL FROM b;
COMMIT;
```

### Looping through a Cursor's Result

There is a variant of the `FOR` statement that allows
iterating through the rows returned by a cursor.  The syntax is:

```
>
FOR `recordvar` IN `bound_cursorvar`  (  `argument_name` :=  `argument_value` , ... )  LOOP
`statements`
END LOOP  `label` ;
```

The cursor variable must have been bound to some query when it was
declared, and it *cannot* be open already.  The
`FOR` statement automatically opens the cursor, and it closes
the cursor again when the loop exits.  A list of actual argument value
expressions must appear if and only if the cursor was declared to take
arguments.  These values will be substituted in the query, in just
the same way as during an `OPEN` (see [plpgsql-open-bound-cursor](#plpgsql-open-bound-cursor)).

The variable `recordvar` is automatically
defined as type `record` and exists only inside the loop (any
existing definition of the variable name is ignored within the loop).
Each row returned by the cursor is successively assigned to this
record variable and the loop body is executed.

### Reporting Errors and Messages

Use the `RAISE` statement to report messages and
raise errors.

```
RAISE  `level`  '`format`' , `expression` , ...   USING `option` = `expression` , ...  ;
RAISE  `level`  `condition_name`  USING `option` = `expression` , ...  ;
RAISE  `level`  SQLSTATE '`sqlstate`'  USING `option` = `expression` , ...  ;
RAISE  `level`  USING `option` = `expression` , ... ;
RAISE ;
```

The `level` option specifies
the error severity.  Allowed levels are `DEBUG`,
`LOG`, `INFO`,
`NOTICE`, `WARNING`,
and `EXCEPTION`, with `EXCEPTION`
being the default.
`EXCEPTION` raises an error (which normally aborts the
current transaction); the other levels only generate messages of different
priority levels.
Whether messages of a particular priority are reported to the client,
written to the server log, or both is controlled by the
[guc-log-min-messages](#guc-log-min-messages) and
[guc-client-min-messages](#guc-client-min-messages) configuration
variables. See [runtime-config](#runtime-config) for more
information.

After `level` if any,
you can specify a `format` string
(which must be a simple string literal, not an expression).  The
format string specifies the error message text to be reported.
The format string can be followed
by optional argument expressions to be inserted into the message.
Inside the format string, `%` is replaced by the
string representation of the next optional argument's value. Write
`%%` to emit a literal `%`.
The number of arguments must match the number of `%`
placeholders in the format string, or an error is raised during
the compilation of the function.

In this example, the value of `v_job_id` will replace the
`%` in the string:

```
RAISE NOTICE 'Calling cs_create_job(%)', v_job_id;
```

You can attach additional information to the error report by writing
`USING` followed by `option` = `expression` items.  Each
`expression` can be any
string-valued expression.  The allowed `option` key words are:

**`MESSAGE`**
: Sets the error message text.  This option can't be used in the
form of `RAISE` that includes a format string
before `USING`.

**`DETAIL`**
: Supplies an error detail message.

**`HINT`**
: Supplies a hint message.

**`ERRCODE`**
: Specifies the error code (SQLSTATE) to report, either by condition
name, as shown in [errcodes-appendix](#errcodes-appendix), or directly as a
five-character SQLSTATE code.

**`COLUMN`**
: Supplies the name of a related object.

This example will abort the transaction with the given error message
and hint:

```
RAISE EXCEPTION 'Nonexistent ID --> %', user_id
USING HINT = 'Please check your user ID';
```

These two examples show equivalent ways of setting the SQLSTATE:

```
RAISE 'Duplicate user ID: %', user_id USING ERRCODE = 'unique_violation';
RAISE 'Duplicate user ID: %', user_id USING ERRCODE = '23505';
```

There is a second `RAISE` syntax in which the main argument
is the condition name or SQLSTATE to be reported, for example:

```
RAISE division_by_zero;
RAISE SQLSTATE '22012';
```

In this syntax, `USING` can be used to supply a custom
error message, detail, or hint.  Another way to do the earlier
example is

```
RAISE unique_violation USING MESSAGE = 'Duplicate user ID: ' || user_id;
```

Still another variant is to write `RAISE USING` or `RAISE
`level` USING` and put
everything else into the `USING` list.

The last variant of `RAISE` has no parameters at all.
This form can only be used inside a `BEGIN` block's
`EXCEPTION` clause;
it causes the error currently being handled to be re-thrown.

> **Note:**

> Before PostgreSQL 9.1, `RAISE` without
> parameters was interpreted as re-throwing the error from the block
> containing the active exception handler.  Thus an `EXCEPTION`
> clause nested within that handler could not catch it, even if the
> `RAISE` was within the nested `EXCEPTION` clause's
> block. This was deemed surprising as well as being incompatible with
> Oracle's PL/SQL.
>

If no condition name nor SQLSTATE is specified in a
`RAISE EXCEPTION` command, the default is to use
`raise_exception` (`P0001`).
If no message text is specified, the default is to use the condition
name or SQLSTATE as message text.

> **Note:**

> When specifying an error code by SQLSTATE code, you are not
> limited to the predefined error codes, but can select any
> error code consisting of five digits and/or upper-case ASCII
> letters, other than `00000`.  It is recommended that
> you avoid throwing error codes that end in three zeroes, because
> these are category codes and can only be trapped by trapping
> the whole category.
>

## Trigger Functions

PL/pgSQL can be used to define trigger
functions on data changes or database events.
A trigger function is created with the `CREATE FUNCTION`
command, declaring it as a function with no arguments and a return type of
`trigger` (for data change triggers) or
`event_trigger` (for database event triggers).
Special local variables named `TG_`something`` are
automatically defined to describe the condition that triggered the call.

### Triggers on Data Changes

A [data change trigger](#triggers) is declared as a
function with no arguments and a return type of `trigger`.
Note that the function must be declared with no arguments even if it
expects to receive some arguments specified in `CREATE TRIGGER`
— such arguments are passed via `TG_ARGV`, as described
below.

When a PL/pgSQL function is called as a
trigger, several special variables are created automatically in the
top-level block. They are:

**`NEW` `record`**
: new database row for `INSERT`/`UPDATE` operations in row-level
triggers. This variable is null in statement-level triggers
and for `DELETE` operations.

**`OLD` `record`**
: old database row for `UPDATE`/`DELETE` operations in row-level
triggers. This variable is null in statement-level triggers
and for `INSERT` operations.

**`TG_NAME` `name`**
: name of the trigger which fired.

**`TG_WHEN` `text`**
: `BEFORE`, `AFTER`, or
`INSTEAD OF`, depending on the trigger's definition.

**`TG_LEVEL` `text`**
: `ROW` or `STATEMENT`,
depending on the trigger's definition.

**`TG_OP` `text`**
: operation for which the trigger was fired:
`INSERT`, `UPDATE`,
`DELETE`, or `TRUNCATE`.

**`TG_RELID` `oid` (references [`pg_class`](#catalog-pg-class).`oid`)**
: object ID of the table that caused the trigger invocation.

**`TG_RELNAME` `name`**
: table that caused the trigger
invocation. This is now deprecated, and could disappear in a future
release. Use `TG_TABLE_NAME` instead.

**`TG_TABLE_NAME` `name`**
: table that caused the trigger invocation.

**`TG_TABLE_SCHEMA` `name`**
: schema of the table that caused the trigger invocation.

**`TG_NARGS` `integer`**
: number of arguments given to the trigger
function in the `CREATE TRIGGER` statement.

**`TG_ARGV` `text[]`**
: arguments from
the `CREATE TRIGGER` statement.
The index counts from 0. Invalid
indexes (less than 0 or greater than or equal to `tg_nargs`)
result in a null value.

A trigger function must return either `NULL` or a
record/row value having exactly the structure of the table the
trigger was fired for.

Row-level triggers fired `BEFORE` can return null to signal the
trigger manager to skip the rest of the operation for this row
(i.e., subsequent triggers are not fired, and the
`INSERT`/`UPDATE`/`DELETE` does not occur
for this row).  If a nonnull
value is returned then the operation proceeds with that row value.
Returning a row value different from the original value
of `NEW` alters the row that will be inserted or
updated.  Thus, if the trigger function wants the triggering
action to succeed normally without altering the row
value, `NEW` (or a value equal thereto) has to be
returned.  To alter the row to be stored, it is possible to
replace single values directly in `NEW` and return the
modified `NEW`, or to build a complete new record/row to
return.  In the case of a before-trigger
on `DELETE`, the returned value has no direct
effect, but it has to be nonnull to allow the trigger action to
proceed.  Note that `NEW` is null
in `DELETE` triggers, so returning that is
usually not sensible.  The usual idiom in `DELETE`
triggers is to return `OLD`.

`INSTEAD OF` triggers (which are always row-level triggers,
and may only be used on views) can return null to signal that they did
not perform any updates, and that the rest of the operation for this
row should be skipped (i.e., subsequent triggers are not fired, and the
row is not counted in the rows-affected status for the surrounding
`INSERT`/`UPDATE`/`DELETE`).
Otherwise a nonnull value should be returned, to signal
that the trigger performed the requested operation. For
`INSERT` and `UPDATE` operations, the return value
should be `NEW`, which the trigger function may modify to
support `INSERT RETURNING` and `UPDATE RETURNING`
(this will also affect the row value passed to any subsequent triggers,
or passed to a special `EXCLUDED` alias reference within
an `INSERT` statement with an `ON CONFLICT DO
UPDATE` clause).  For `DELETE` operations, the return
value should be `OLD`.

The return value of a row-level trigger
fired `AFTER` or a statement-level trigger
fired `BEFORE` or `AFTER` is
always ignored; it might as well be null. However, any of these types of
triggers might still abort the entire operation by raising an error.

[plpgsql-trigger-example](#plpgsql-trigger-example) shows an example of a
trigger function in PL/pgSQL.

## Porting from Oracle PL/SQL

This section explains differences between
PostgreSQL's PL/pgSQL
language and Oracle's PL/SQL language,
to help developers who port applications from
Oracle to PostgreSQL.

PL/pgSQL is similar to PL/SQL in many
aspects. It is a block-structured, imperative language, and all
variables have to be declared.  Assignments, loops, and conditionals
are similar.  The main differences you should keep in mind when
porting from PL/SQL to
PL/pgSQL are:

- If a name used in an SQL command could be either a column name of a
table used in the command or a reference to a variable of the function,
PL/SQL treats it as a column name.
By default, PL/pgSQL will throw an error
complaining that the name is ambiguous.  You can specify
`plpgsql.variable_conflict` = `use_column`
to change this behavior to match PL/SQL,
as explained in [plpgsql-var-subst](#plpgsql-var-subst).
It's often best to avoid such ambiguities in the first place,
but if you have to port a large amount of code that depends on
this behavior, setting `variable_conflict` may be the
best solution.
- In PostgreSQL the function body must be written as
a string literal.  Therefore you need to use dollar quoting or escape
single quotes in the function body. (See [plpgsql-quote-tips](#plpgsql-quote-tips).)
- Data type names often need translation.  For example, in Oracle string
values are commonly declared as being of type `varchar2`, which
is a non-SQL-standard type.  In PostgreSQL,
use type `varchar` or `text` instead.  Similarly, replace
type `number` with `numeric`, or use some other numeric
data type if there's a more appropriate one.
- Instead of packages, use schemas to organize your functions
into groups.
- Since there are no packages, there are no package-level variables
either. This is somewhat annoying.  You can keep per-session state
in temporary tables instead.
- Integer `FOR` loops with `REVERSE` work
differently: PL/SQL counts down from the second
number to the first, while PL/pgSQL counts down
from the first number to the second, requiring the loop bounds
to be swapped when porting.  This incompatibility is unfortunate
but is unlikely to be changed. (See [plpgsql-integer-for](#plpgsql-integer-for).)
- `FOR` loops over queries (other than cursors) also work
differently: the target variable(s) must have been declared,
whereas PL/SQL always declares them implicitly.
An advantage of this is that the variable values are still accessible
after the loop exits.
- There are various notational differences for the use of cursor
variables.

### Porting Examples

[pgsql-porting-ex1](#pgsql-porting-ex1) shows how to port a simple
function from PL/SQL to PL/pgSQL.

## Porting a Simple Function from PL/SQL to PL/pgSQL

Here is an Oracle PL/SQL function:

```
CREATE OR REPLACE FUNCTION cs_fmt_browser_version(v_name varchar2,
v_version varchar2)
RETURN varchar2 IS
BEGIN
IF v_version IS NULL THEN
RETURN v_name;
END IF;
RETURN v_name || '/' || v_version;
END;
/
show errors;
```

Let's go through this function and see the differences compared to
PL/pgSQL:

- The type name `varchar2` has to be changed to `varchar`
or `text`.  In the examples in this section, we'll
use `varchar`, but `text` is often a better choice if
you do not need specific string length limits.
- The `RETURN` key word in the function
prototype (not the function body) becomes
`RETURNS` in
PostgreSQL.
Also, `IS` becomes `AS`, and you need to
add a `LANGUAGE` clause because PL/pgSQL
is not the only possible function language.
- In PostgreSQL, the function body is considered
to be a string literal, so you need to use quote marks or dollar
quotes around it.  This substitutes for the terminating `/`
in the Oracle approach.
- The `show errors` command does not exist in
PostgreSQL, and is not needed since errors are
reported automatically.

This is how this function would look when ported to
PostgreSQL:

```
CREATE OR REPLACE FUNCTION cs_fmt_browser_version(v_name varchar,
v_version varchar)
RETURNS varchar AS $$
BEGIN
IF v_version IS NULL THEN
RETURN v_name;
END IF;
RETURN v_name || '/' || v_version;
END;
$$ LANGUAGE plpgsql;
```

[plpgsql-porting-ex2](#plpgsql-porting-ex2) shows how to port a
function that creates another function and how to handle the
ensuing quoting problems.

## Porting a Function that Creates Another Function from PL/SQL to PL/pgSQL

The following procedure grabs rows from a
`SELECT` statement and builds a large function
with the results in `IF` statements, for the
sake of efficiency.

This is the Oracle version:

```
CREATE OR REPLACE PROCEDURE cs_update_referrer_type_proc IS
CURSOR referrer_keys IS
SELECT * FROM cs_referrer_keys
ORDER BY try_order;
func_cmd VARCHAR(4000);
BEGIN
func_cmd := 'CREATE OR REPLACE FUNCTION cs_find_referrer_type(v_host IN VARCHAR2,
v_domain IN VARCHAR2, v_url IN VARCHAR2) RETURN VARCHAR2 IS BEGIN';

FOR referrer_key IN referrer_keys LOOP
func_cmd := func_cmd ||
' IF v_' || referrer_key.kind
|| ' LIKE ''' || referrer_key.key_string
|| ''' THEN RETURN ''' || referrer_key.referrer_type
|| '''; END IF;';
END LOOP;

func_cmd := func_cmd || ' RETURN NULL; END;';

EXECUTE IMMEDIATE func_cmd;
END;
/
show errors;
```

Here is how this function would end up in PostgreSQL:

```
CREATE OR REPLACE PROCEDURE cs_update_referrer_type_proc() AS $func$
DECLARE
referrer_keys CURSOR IS
SELECT * FROM cs_referrer_keys
ORDER BY try_order;
func_body text;
func_cmd text;
BEGIN
func_body := 'BEGIN';

FOR referrer_key IN referrer_keys LOOP
func_body := func_body ||
' IF v_' || referrer_key.kind
|| ' LIKE ' || quote_literal(referrer_key.key_string)
|| ' THEN RETURN ' || quote_literal(referrer_key.referrer_type)
|| '; END IF;' ;
END LOOP;

func_body := func_body || ' RETURN NULL; END;';

func_cmd :=
'CREATE OR REPLACE FUNCTION cs_find_referrer_type(v_host varchar,
v_domain varchar,
v_url varchar)
RETURNS varchar AS '
|| quote_literal(func_body)
|| ' LANGUAGE plpgsql;' ;

EXECUTE func_cmd;
END;
$func$ LANGUAGE plpgsql;
```

Notice how the body of the function is built separately and passed
through `quote_literal` to double any quote marks in it.  This
technique is needed because we cannot safely use dollar quoting for
defining the new function: we do not know for sure what strings will
be interpolated from the `referrer_key.key_string` field.
(We are assuming here that `referrer_key.kind` can be
trusted to always be `host`, `domain`, or
`url`, but `referrer_key.key_string` might be
anything, in particular it might contain dollar signs.) This function
is actually an improvement on the Oracle original, because it will
not generate broken code when `referrer_key.key_string` or
`referrer_key.referrer_type` contain quote marks.

[plpgsql-porting-ex3](#plpgsql-porting-ex3) shows how to port a function
with `OUT` parameters and string manipulation.
PostgreSQL does not have a built-in
`instr` function, but you can create one
using a combination of other
functions. In [plpgsql-porting-appendix](#plpgsql-porting-appendix) there is a
PL/pgSQL implementation of
`instr` that you can use to make your porting
easier.

## Porting a Procedure With String Manipulation and
`OUT` Parameters from PL/SQL to
PL/pgSQL

The following Oracle PL/SQL procedure is used
to parse a URL and return several elements (host, path, and query).

This is the Oracle version:

```
CREATE OR REPLACE PROCEDURE cs_parse_url(
v_url IN VARCHAR2,
v_host OUT VARCHAR2,  -- This will be passed back
v_path OUT VARCHAR2,  -- This one too
v_query OUT VARCHAR2) -- And this one
IS
a_pos1 INTEGER;
a_pos2 INTEGER;
BEGIN
v_host := NULL;
v_path := NULL;
v_query := NULL;
a_pos1 := instr(v_url, '//');

IF a_pos1 = 0 THEN
RETURN;
END IF;
a_pos2 := instr(v_url, '/', a_pos1 + 2);
IF a_pos2 = 0 THEN
v_host := substr(v_url, a_pos1 + 2);
v_path := '/';
RETURN;
END IF;

v_host := substr(v_url, a_pos1 + 2, a_pos2 - a_pos1 - 2);
a_pos1 := instr(v_url, '?', a_pos2 + 1);

IF a_pos1 = 0 THEN
v_path := substr(v_url, a_pos2);
RETURN;
END IF;

v_path := substr(v_url, a_pos2, a_pos1 - a_pos2);
v_query := substr(v_url, a_pos1 + 1);
END;
/
show errors;
```

Here is a possible translation into PL/pgSQL:

```
CREATE OR REPLACE FUNCTION cs_parse_url(
v_url IN VARCHAR,
v_host OUT VARCHAR,  -- This will be passed back
v_path OUT VARCHAR,  -- This one too
v_query OUT VARCHAR) -- And this one
AS $$
DECLARE
a_pos1 INTEGER;
a_pos2 INTEGER;
BEGIN
v_host := NULL;
v_path := NULL;
v_query := NULL;
a_pos1 := instr(v_url, '//');

IF a_pos1 = 0 THEN
RETURN;
END IF;
a_pos2 := instr(v_url, '/', a_pos1 + 2);
IF a_pos2 = 0 THEN
v_host := substr(v_url, a_pos1 + 2);
v_path := '/';
RETURN;
END IF;

v_host := substr(v_url, a_pos1 + 2, a_pos2 - a_pos1 - 2);
a_pos1 := instr(v_url, '?', a_pos2 + 1);

IF a_pos1 = 0 THEN
v_path := substr(v_url, a_pos2);
RETURN;
END IF;

v_path := substr(v_url, a_pos2, a_pos1 - a_pos2);
v_query := substr(v_url, a_pos1 + 1);
END;
$$ LANGUAGE plpgsql;
```

This function could be used like this:

```
SELECT * FROM cs_parse_url('http://foobar.com/query.cgi?baz');
```

[plpgsql-porting-ex4](#plpgsql-porting-ex4) shows how to port a procedure
that uses numerous features that are specific to Oracle.

## Porting a Procedure from PL/SQL to PL/pgSQL

The Oracle version:

```
CREATE OR REPLACE PROCEDURE cs_create_job(v_job_id IN INTEGER) IS
a_running_job_count INTEGER;
BEGIN
LOCK TABLE cs_jobs IN EXCLUSIVE MODE;

SELECT count(*) INTO a_running_job_count FROM cs_jobs WHERE end_stamp IS NULL;

IF a_running_job_count > 0 THEN
COMMIT; -- free lock
raise_application_error(-20000,
'Unable to create a new job: a job is currently running.');
END IF;

DELETE FROM cs_active_job;
INSERT INTO cs_active_job(job_id) VALUES (v_job_id);

BEGIN
INSERT INTO cs_jobs (job_id, start_stamp) VALUES (v_job_id, now());
EXCEPTION
WHEN dup_val_on_index THEN NULL; -- don't worry if it already exists
END;
COMMIT;
END;
/
show errors
```

This is how we could port this procedure to PL/pgSQL:

```
CREATE OR REPLACE PROCEDURE cs_create_job(v_job_id integer) AS $$
DECLARE
a_running_job_count integer;
BEGIN
LOCK TABLE cs_jobs IN EXCLUSIVE MODE;

SELECT count(*) INTO a_running_job_count FROM cs_jobs WHERE end_stamp IS NULL;

IF a_running_job_count > 0 THEN
COMMIT; -- free lock
RAISE EXCEPTION 'Unable to create a new job: a job is currently running'; --
END IF;

DELETE FROM cs_active_job;
INSERT INTO cs_active_job(job_id) VALUES (v_job_id);

BEGIN
INSERT INTO cs_jobs (job_id, start_stamp) VALUES (v_job_id, now());
EXCEPTION
WHEN unique_violation THEN --
-- don't worry if it already exists
END;
COMMIT;
END;
$$ LANGUAGE plpgsql;
```

The syntax of `RAISE` is considerably different from
Oracle's statement, although the basic case `RAISE`
`exception_name` works
similarly.

The exception names supported by PL/pgSQL are
different from Oracle's.  The set of built-in exception names
is much larger (see [errcodes-appendix](#errcodes-appendix)).  There
is not currently a way to declare user-defined exception names,
although you can throw user-chosen SQLSTATE values instead.

### Other Things to Watch For

This section explains a few other things to watch for when porting
Oracle PL/SQL functions to
PostgreSQL.

#### Implicit Rollback after Exceptions

In PL/pgSQL, when an exception is caught by an
`EXCEPTION` clause, all database changes since the block's
`BEGIN` are automatically rolled back.  That is, the behavior
is equivalent to what you'd get in Oracle with:

```
BEGIN
SAVEPOINT s1;
... code here ...
EXCEPTION
WHEN ... THEN
ROLLBACK TO s1;
... code here ...
WHEN ... THEN
ROLLBACK TO s1;
... code here ...
END;
```

If you are translating an Oracle procedure that uses
`SAVEPOINT` and `ROLLBACK TO` in this style,
your task is easy: just omit the `SAVEPOINT` and
`ROLLBACK TO`.  If you have a procedure that uses
`SAVEPOINT` and `ROLLBACK TO` in a different way
then some actual thought will be required.

#### `EXECUTE`

The PL/pgSQL version of
`EXECUTE` works similarly to the
PL/SQL version, but you have to remember to use
`quote_literal` and
`quote_ident` as described in [plpgsql-statements-executing-dyn](#plpgsql-statements-executing-dyn).  Constructs of the
type `EXECUTE 'SELECT * FROM $1';` will not work
reliably unless you use these functions.

#### Optimizing PL/pgSQL Functions

PostgreSQL gives you two function creation
modifiers to optimize execution: "volatility" (whether
the function always returns the same result when given the same
arguments) and "strictness" (whether the function
returns null if any argument is null).  Consult the [sql-createfunction](#sql-createfunction)
reference page for details.

When making use of these optimization attributes, your
`CREATE FUNCTION` statement might look something
like this:

```
CREATE FUNCTION foo(...) RETURNS integer AS $$
...
$$ LANGUAGE plpgsql STRICT IMMUTABLE;
```

### Appendix

This section contains the code for a set of Oracle-compatible
`instr` functions that you can use to simplify
your porting efforts.

```

--
-- instr functions that mimic Oracle's counterpart
-- Syntax: instr(string1, string2 [, n [, m]])
-- where [] denotes optional parameters.
--
-- Search string1, beginning at the nth character, for the mth occurrence
-- of string2.  If n is negative, search backwards, starting at the abs(n)'th
-- character from the end of string1.
-- If n is not passed, assume 1 (search starts at first character).
-- If m is not passed, assume 1 (find first occurrence).
-- Returns starting index of string2 in string1, or 0 if string2 is not found.
--

CREATE FUNCTION instr(varchar, varchar) RETURNS integer AS $$
BEGIN
RETURN instr($1, $2, 1);
END;
$$ LANGUAGE plpgsql STRICT IMMUTABLE;

CREATE FUNCTION instr(string varchar, string_to_search_for varchar,
beg_index integer)
RETURNS integer AS $$
DECLARE
pos integer NOT NULL DEFAULT 0;
temp_str varchar;
beg integer;
length integer;
ss_length integer;
BEGIN
IF beg_index > 0 THEN
temp_str := substring(string FROM beg_index);
pos := position(string_to_search_for IN temp_str);

IF pos = 0 THEN
RETURN 0;
ELSE
RETURN pos + beg_index - 1;
END IF;
ELSIF beg_index  0 LOOP
temp_str := substring(string FROM beg FOR ss_length);
IF string_to_search_for = temp_str THEN
RETURN beg;
END IF;

beg := beg - 1;
END LOOP;

RETURN 0;
ELSE
RETURN 0;
END IF;
END;
$$ LANGUAGE plpgsql STRICT IMMUTABLE;

CREATE FUNCTION instr(string varchar, string_to_search_for varchar,
beg_index integer, occur_index integer)
RETURNS integer AS $$
DECLARE
pos integer NOT NULL DEFAULT 0;
occur_number integer NOT NULL DEFAULT 0;
temp_str varchar;
beg integer;
i integer;
length integer;
ss_length integer;
BEGIN
IF occur_index  0 THEN
beg := beg_index - 1;
FOR i IN 1..occur_index LOOP
temp_str := substring(string FROM beg + 1);
pos := position(string_to_search_for IN temp_str);
IF pos = 0 THEN
RETURN 0;
END IF;
beg := beg + pos;
END LOOP;

RETURN beg;
ELSIF beg_index  0 LOOP
temp_str := substring(string FROM beg FOR ss_length);
IF string_to_search_for = temp_str THEN
occur_number := occur_number + 1;
IF occur_number = occur_index THEN
RETURN beg;
END IF;
END IF;

beg := beg - 1;
END LOOP;

RETURN 0;
ELSE
RETURN 0;
END IF;
END;
$$ LANGUAGE plpgsql STRICT IMMUTABLE;

```
