# Functions; Data Values; Sharing Data; Anonymous Code Blocks; Trigger Functions; Database Access; Utility Functions; Python 2 vs. Python 3

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partV_server_programming/09_plpython_-_python_procedural_language.md`
- Source Title: `PL/Python — Python Procedural Language`
- Source Heading Path: `PL/Python - Python Procedural Language > Functions; Data Values; Sharing Data; Anonymous Code Blocks; Trigger Functions; Database Access; Utility Functions; Python 2 vs. Python 3`
- Source Line Ranges: `35-43, 127-326, 397-417, 471-484, 485-491, 499-546, 547-675, 922-981, 982-988`
- Chunk ID: `pg16_fact_0089_2aa3d4bd29`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d9c792c7e0232fcf49f2eb7e4ccaa0a8f92c5d52c3279866b496bdc3446ffb2a`

## Retrieval Guidance

- Use When: Write or interpret PL/Python functions, procedures, and triggers.
- Retrieval Keywords: PL/Python, plpython3u, plpy.execute, plpy.prepare, plpy.cursor, trigger function, SD, GD
- Follow-up Guidance: Use error and subtransaction records when diagnosing or handling PL/Python failures.
- Classification Note: These sections document PL/Python syntax, type mapping, shared dictionaries, SPI access, triggers, utilities, and Python-version behavior.

## Official Source Content

## PL/Python Functions

Functions in PL/Python are declared via the
standard [sql-createfunction](#sql-createfunction) syntax:

```
CREATE FUNCTION `funcname` (`argument-list`)
RETURNS `return-type`
AS $$

## Data Values

Generally speaking, the aim of PL/Python is to provide
a "natural" mapping between the PostgreSQL and the
Python worlds.  This informs the data mapping rules described
below.

### Data Type Mapping

When a PL/Python function is called, its arguments are converted from
their PostgreSQL data type to a corresponding Python type:

- PostgreSQL `boolean` is converted to Python `bool`.
- PostgreSQL `smallint`, `int`, `bigint`
and `oid` are converted to Python `int`.
- PostgreSQL `real` and `double` are converted to
Python `float`.
- PostgreSQL `numeric` is converted to
Python `Decimal`.  This type is imported from
the `cdecimal` package if that is available.
Otherwise,
`decimal.Decimal` from the standard library will be
used.  `cdecimal` is significantly faster
than `decimal`.  In Python 3.3 and up,
however, `cdecimal` has been integrated into the
standard library under the name `decimal`, so there is
no longer any difference.
- PostgreSQL `bytea` is converted to Python `bytes`.
- All other data types, including the PostgreSQL character string types,
are converted to a Python `str` (in Unicode like all Python
strings).
- For nonscalar data types, see below.

When a PL/Python function returns, its return value is converted to the
function's declared PostgreSQL return data type as follows:

- When the PostgreSQL return type is `boolean`, the
return value will be evaluated for truth according to the
*Python* rules.  That is, 0 and empty string
are false, but notably `'f'` is true.
- When the PostgreSQL return type is `bytea`, the return value
will be converted to Python `bytes` using the respective
Python built-ins, with the result being converted to
`bytea`.
- For all other PostgreSQL return types, the return value is converted
to a string using the Python built-in `str`, and the
result is passed to the input function of the PostgreSQL data type.
(If the Python value is a `float`, it is converted using
the `repr` built-in instead of `str`, to
avoid loss of precision.)

Strings are automatically converted to the PostgreSQL server encoding
when they are passed to PostgreSQL.
- For nonscalar data types, see below.

Note that logical mismatches between the declared PostgreSQL
return type and the Python data type of the actual return object
are not flagged; the value will be converted in any case.

### Null, None

If an SQL null value is passed to a
function, the argument value will appear as `None` in
Python. For example, the function definition of `pymax`
shown in [plpython-funcs](#plpython-funcs) will return the wrong answer for null
inputs. We could add `STRICT` to the function definition
to make PostgreSQL do something more reasonable:
if a null value is passed, the function will not be called at all,
but will just return a null result automatically. Alternatively,
we could check for null inputs in the function body:

```
CREATE FUNCTION pymax (a integer, b integer)
RETURNS integer
AS $$
if (a is None) or (b is None):
return None
if a > b:
return a
return b
$$ LANGUAGE plpython3u;
```

As shown above, to return an SQL null value from a PL/Python
function, return the value `None`. This can be done whether the
function is strict or not.

### Arrays, Lists

SQL array values are passed into PL/Python as a Python list.  To
return an SQL array value out of a PL/Python function, return a
Python list:

```
CREATE FUNCTION return_arr()
RETURNS int[]
AS $$
return [1, 2, 3, 4, 5]
$$ LANGUAGE plpython3u;

SELECT return_arr();
return_arr
-------------
{1,2,3,4,5}
(1 row)
```

Multidimensional arrays are passed into PL/Python as nested Python lists.
A 2-dimensional array is a list of lists, for example. When returning
a multi-dimensional SQL array out of a PL/Python function, the inner
lists at each level must all be of the same size. For example:

```
CREATE FUNCTION test_type_conversion_array_int4(x int4[]) RETURNS int4[] AS $$
plpy.info(x, type(x))
return x
$$ LANGUAGE plpython3u;

SELECT * FROM test_type_conversion_array_int4(ARRAY[[1,2,3],[4,5,6]]);
INFO:  ([[1, 2, 3], [4, 5, 6]], )
test_type_conversion_array_int4
---------------------------------
{{1,2,3},{4,5,6}}
(1 row)
```

Other Python sequences, like tuples, are also accepted for
backwards-compatibility with PostgreSQL versions 9.6 and below, when
multi-dimensional arrays were not supported. However, they are always
treated as one-dimensional arrays, because they are ambiguous with
composite types. For the same reason, when a composite type is used in a
multi-dimensional array, it must be represented by a tuple, rather than a
list.

Note that in Python, strings are sequences, which can have
undesirable effects that might be familiar to Python programmers:

```
CREATE FUNCTION return_str_arr()
RETURNS varchar[]
AS $$
return "hello"
$$ LANGUAGE plpython3u;

SELECT return_str_arr();
return_str_arr
----------------
{h,e,l,l,o}
(1 row)
```

### Composite Types

Composite-type arguments are passed to the function as Python mappings. The
element names of the mapping are the attribute names of the composite type.
If an attribute in the passed row has the null value, it has the value
`None` in the mapping. Here is an example:

```
CREATE TABLE employee (
name text,
salary integer,
age integer
);

CREATE FUNCTION overpaid (e employee)
RETURNS boolean
AS $$
if e["salary"] > 200000:
return True
if (e["age"]  100000):
return True
return False
$$ LANGUAGE plpython3u;
```

There are multiple ways to return row or composite types from a Python
function. The following examples assume we have:

```
CREATE TYPE named_value AS (
name   text,
value  integer
);
```

A composite result can be returned as a:

**Sequence type (a tuple or list, but not a set because
it is not indexable)**
: Returned sequence objects must have the same number of items as the
composite result type has fields. The item with index 0 is assigned to
the first field of the composite type, 1 to the second and so on. For
example:

```
CREATE FUNCTION make_pair (name text, value integer)
RETURNS named_value
AS $$
return ( name, value )

### Set-Returning Functions

A PL/Python function can also return sets of
scalar or composite types. There are several ways to achieve this because
the returned object is internally turned into an iterator. The following
examples assume we have composite type:

```
CREATE TYPE greeting AS (
how text,
who text
);
```

A set result can be returned from a:

**Sequence type (tuple, list, set)**
: ```
CREATE FUNCTION greet (how text)
RETURNS SETOF greeting
AS $$

## Sharing Data

The global dictionary `SD` is available to store
private data between repeated calls to the same function.
The global dictionary `GD` is public data,
that is available to all Python functions within a session;  use with
care.

Each function gets its own execution environment in the
Python interpreter, so that global data and function arguments from
`myfunc` are not available to
`myfunc2`.  The exception is the data in the
`GD` dictionary, as mentioned above.

## Anonymous Code Blocks

PL/Python also supports anonymous code blocks called with the
[sql-do](#sql-do) statement:

```
DO $$

## Trigger Functions

When a function is used as a trigger, the dictionary
`TD` contains trigger-related values:

**`TD["event"]`**
: contains the event as a string:
`INSERT`, `UPDATE`,
`DELETE`, or `TRUNCATE`.

**`TD["when"]`**
: contains one of `BEFORE`, `AFTER`, or
`INSTEAD OF`.

**`TD["level"]`**
: contains `ROW` or `STATEMENT`.

**`TD["new"]`**
: For a row-level trigger, one or both of these fields contain
the respective trigger rows, depending on the trigger event.

**`TD["name"]`**
: contains the trigger name.

**`TD["table_name"]`**
: contains the name of the table on which the trigger occurred.

**`TD["table_schema"]`**
: contains the schema of the table on which the trigger occurred.

**`TD["relid"]`**
: contains the OID of the table on which the trigger occurred.

**`TD["args"]`**
: If the `CREATE TRIGGER` command
included arguments, they are available in `TD["args"][0]` to
`TD["args"][`n`-1]`.

If `TD["when"]` is `BEFORE` or
`INSTEAD OF` and
`TD["level"]` is `ROW`, you can
return `None` or `"OK"` from the
Python function to indicate the row is unmodified,
`"SKIP"` to abort the event, or if `TD["event"]`
is `INSERT` or `UPDATE` you can return
`"MODIFY"` to indicate you've modified the new row.
Otherwise the return value is ignored.

## Database Access

The PL/Python language module automatically imports a Python module
called `plpy`.  The functions and constants in
this module are available to you in the Python code as
`plpy.`foo``.

### Database Access Functions

The `plpy` module provides several functions to execute
database commands:

**`plpy.`execute`(`query` [, `limit`])`**
: Calling `plpy.execute` with a query string and an
optional row limit argument causes that query to be run and the result to
be returned in a result object.

If `limit` is specified and is greater than
zero, then `plpy.execute` retrieves at
most `limit` rows, much as if the query
included a `LIMIT`
clause.  Omitting `limit` or specifying it as
zero results in no row limit.

The result object emulates a list or dictionary object.  The result
object can be accessed by row number and column name.  For example:

```
rv = plpy.execute("SELECT * FROM my_table", 5)
```

returns up to 5 rows from `my_table`.  If
`my_table` has a column
`my_column`, it would be accessed as:

```
foo = rv[i]["my_column"]
```

The number of rows returned can be obtained using the built-in
`len` function.

The result object has these additional methods:

``nrows`()`

Returns the number of rows processed by the command.  Note that this
is not necessarily the same as the number of rows returned.  For
example, an `UPDATE` command will set this value but
won't return any rows (unless `RETURNING` is used).

**``status`()`**
: The `SPI_execute()` return value.

**``colnames`()`**
: Return a list of column names, list of column type OIDs, and list of
type-specific type modifiers for the columns, respectively.

These methods raise an exception when called on a result object from
a command that did not produce a result set, e.g.,
`UPDATE` without `RETURNING`, or
`DROP TABLE`.  But it is OK to use these methods on
a result set containing zero rows.

**``__str__`()`**
: The standard `__str__` method is defined so that it
is possible for example to debug query execution results
using `plpy.debug(rv)`.

The result object can be modified.

Note that calling `plpy.execute` will cause the entire
result set to be read into memory.  Only use that function when you are
sure that the result set will be relatively small.  If you don't want to
risk excessive memory usage when fetching large results,
use `plpy.cursor` rather
than `plpy.execute`.

`plpy.`prepare`(`query` [, `argtypes`])`
`plpy.`execute`(`plan` [, `arguments` [, `limit`]])`

`plpy.prepare` prepares the execution plan for a
query.  It is called with a query string and a list of parameter types,
if you have parameter references in the query.  For example:

```
plan = plpy.prepare("SELECT last_name FROM my_users WHERE first_name = $1", ["text"])
```

`text` is the type of the variable you will be passing
for `$1`.  The second argument is optional if you don't
want to pass any parameters to the query.

After preparing a statement, you use a variant of the
function `plpy.execute` to run it:

```
rv = plpy.execute(plan, ["name"], 5)
```

Pass the plan as the first argument (instead of the query string), and a
list of values to substitute into the query as the second argument.  The
second argument is optional if the query does not expect any parameters.
The third argument is the optional row limit as before.

Alternatively, you can call the `execute` method on
the plan object:

```
rv = plan.execute(["name"], 5)
```

Query parameters and result row fields are converted between PostgreSQL
and Python data types as described in [plpython-data](#plpython-data).

When you prepare a plan using the PL/Python module it is automatically
saved.  Read the SPI documentation ([spi](#spi)) for a
description of what this means.  In order to make effective use of this
across function calls one needs to use one of the persistent storage
dictionaries `SD` or `GD` (see
[plpython-sharing](#plpython-sharing)). For example:

```
CREATE FUNCTION usesavedplan() RETURNS trigger AS $$
if "plan" in SD:
plan = SD["plan"]
else:
plan = plpy.prepare("SELECT 1")
SD["plan"] = plan

## Utility Functions

The `plpy` module also provides the functions

`plpy.error` and `plpy.fatal`
actually raise a Python exception which, if uncaught, propagates out to
the calling query, causing the current transaction or subtransaction to
be aborted.  `raise plpy.Error(`msg`)` and
`raise plpy.Fatal(`msg`)` are
equivalent to calling `plpy.error(`msg`)` and
`plpy.fatal(`msg`)`, respectively but
the `raise` form does not allow passing keyword arguments.
The other functions only generate messages of different priority levels.
Whether messages of a particular priority are reported to the client,
written to the server log, or both is controlled by the
[guc-log-min-messages](#guc-log-min-messages) and
[guc-client-min-messages](#guc-client-min-messages) configuration
variables. See [runtime-config](#runtime-config) for more information.

The `msg` argument is given as a positional argument.  For
backward compatibility, more than one positional argument can be given. In
that case, the string representation of the tuple of positional arguments
becomes the message reported to the client.

The following keyword-only arguments are accepted:

The string representation of the objects passed as keyword-only arguments
is used to enrich the messages reported to the client. For example:

```
CREATE FUNCTION raise_custom_exception() RETURNS void AS $$
plpy.error("custom exception message",
detail="some info about exception",
hint="hint for users")
$$ LANGUAGE plpython3u;

=# SELECT raise_custom_exception();
ERROR:  plpy.Error: custom exception message
DETAIL:  some info about exception
HINT:  hint for users
CONTEXT:  Traceback (most recent call last):
PL/Python function "raise_custom_exception", line 4, in
hint="hint for users")
PL/Python function "raise_custom_exception"
```

Another set of utility functions are
`plpy.quote_literal(`string`)`,
`plpy.quote_nullable(`string`)`, and
`plpy.quote_ident(`string`)`.  They
are equivalent to the built-in quoting functions described in [functions-string](#functions-string).  They are useful when constructing
ad-hoc queries.  A PL/Python equivalent of dynamic SQL from [plpgsql-quote-literal-example](#plpgsql-quote-literal-example) would be:

```
plpy.execute("UPDATE tbl SET %s = %s WHERE key = %s" % (
plpy.quote_ident(colname),
plpy.quote_nullable(newvalue),
plpy.quote_literal(keyvalue)))
```

## Python 2 vs. Python 3

PL/Python supports only Python 3. Past versions of
PostgreSQL supported Python 2, using the
`plpythonu` and `plpython2u` language
names.
