# Interface Functions; Visibility; Memory Management; SPI Result Codes; Examples

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partV_server_programming/10_server_programming_interface.md`
- Source Title: `Server Programming Interface`
- Source Heading Path: `Server Programming Interface > Interface Functions; Visibility; Memory Management; SPI Result Codes; Examples`
- Source Line Ranges: `37-54, 2303-2357, 2789-2823, 2824-2994`
- Chunk ID: `pg16_fact_0090_447bd0ddd6`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ad2dbdc949d78900cbb084d13505f938da03b7f6569128b585147b5289be9d02`

## Retrieval Guidance

- Use When: Implement C-language server-side code that executes SQL through SPI.
- Retrieval Keywords: SPI, Server Programming Interface, SPI_connect, SPI_execute, SPI_finish, SPI_result_code_string, memory context
- Follow-up Guidance: Treat SPI result codes as API reference unless tied to a concrete runtime failure.
- Classification Note: The chapter is API reference for SPI calls, memory contexts, visibility, return codes, and examples used by server-side code.

## Official Source Content

## Interface Functions

SPI_connect
3

SPI_connect
SPI_connect_ext
connect a C function to the SPI manager

```
int SPI_connect(void)
```

```
int SPI_connect_ext(int
options)
```

## Memory Management

PostgreSQL allocates memory within
*memory contexts*, which provide a convenient method of
managing allocations made in many different places that need to
live for differing amounts of time.  Destroying a context releases
all the memory that was allocated in it.  Thus, it is not necessary
to keep track of individual objects to avoid memory leaks; instead
only a relatively small number of contexts have to be managed.
`palloc` and related functions allocate memory
from the "current" context.

`SPI_connect` creates a new memory context and
makes it current.  `SPI_finish` restores the
previous current memory context and destroys the context created by
`SPI_connect`.  These actions ensure that
transient memory allocations made inside your C function are
reclaimed at C function exit, avoiding memory leakage.

However, if your C function needs to return an object in allocated
memory (such as a value of a pass-by-reference data type), you
cannot allocate that memory using `palloc`, at
least not while you are connected to SPI.  If you try, the object
will be deallocated by `SPI_finish`, and your
C function will not work reliably.  To solve this problem, use
`SPI_palloc` to allocate memory for your return
object.  `SPI_palloc` allocates memory in the
"upper executor context", that is, the memory context
that was current when `SPI_connect` was called,
which is precisely the right context for a value returned from your
C function.  Several of the other utility functions described in
this section also return objects created in the upper executor context.

When `SPI_connect` is called, the private
context of the C function, which is created by
`SPI_connect`, is made the current context.  All
allocations made by `palloc`,
`repalloc`, or SPI utility functions (except as
described in this section) are made in this context.  When a
C function disconnects from the SPI manager (via
`SPI_finish`) the current context is restored to
the upper executor context, and all allocations made in the
C function memory context are freed and cannot be used any more.

SPI_palloc
3

SPI_palloc
allocate memory in the upper executor context

```
void * SPI_palloc(Size
size)
```

## Visibility of Data Changes

The following rules govern the visibility of data changes in
functions that use SPI (or any other C function):

- During the execution of an SQL command, any data changes made by
the command are invisible to the command itself.  For
example, in:

```
INSERT INTO a SELECT * FROM a;
```

the inserted rows are invisible to the `SELECT`
part.
- Changes made by a command C are visible to all commands that are
started after C, no matter whether they are started inside C
(during the execution of C) or after C is done.
- Commands executed via SPI inside a function called by an SQL command
(either an ordinary function or a trigger) follow one or the
other of the above rules depending on the read/write flag passed
to SPI.  Commands executed in read-only mode follow the first
rule: they cannot see changes of the calling command.  Commands executed
in read-write mode follow the second rule: they can see all changes made
so far.
- All standard procedural languages set the SPI read-write mode
depending on the volatility attribute of the function.  Commands of
`STABLE` and `IMMUTABLE` functions are done in
read-only mode, while commands of `VOLATILE` functions are
done in read-write mode.  While authors of C functions are able to
violate this convention, it's unlikely to be a good idea to do so.

The next section contains an example that illustrates the
application of these rules.

## Examples

This section contains a very simple example of SPI usage. The
C function `execq` takes an SQL command as its
first argument and a row count as its second, executes the command
using `SPI_exec` and returns the number of rows
that were processed by the command.  You can find more complex
examples for SPI in the source tree in
`src/test/regress/regress.c` and in the
[contrib-spi](#contrib-spi) module.

```
#include "postgres.h"

#include "executor/spi.h"
#include "utils/builtins.h"

PG_MODULE_MAGIC;

PG_FUNCTION_INFO_V1(execq);

Datum
execq(PG_FUNCTION_ARGS)
{
char *command;
int cnt;
int ret;
uint64 proc;

/* Convert given text object to a C string */
command = text_to_cstring(PG_GETARG_TEXT_PP(0));
cnt = PG_GETARG_INT32(1);

SPI_connect();

ret = SPI_exec(command, cnt);

proc = SPI_processed;

/*
* If some rows were fetched, print them via elog(INFO).
*/
if (ret > 0 && SPI_tuptable != NULL)
{
SPITupleTable *tuptable = SPI_tuptable;
TupleDesc tupdesc = tuptable->tupdesc;
char buf[8192];
uint64 j;

for (j = 0; j numvals; j++)
{
HeapTuple tuple = tuptable->vals[j];
int i;

for (i = 1, buf[0] = 0; i natts; i++)
snprintf(buf + strlen(buf), sizeof(buf) - strlen(buf), " %s%s",
SPI_getvalue(tuple, tupdesc, i),
(i == tupdesc->natts) ? " " : " |");
elog(INFO, "EXECQ: %s", buf);
}
}

SPI_finish();
pfree(command);

PG_RETURN_INT64(proc);
}
```

This is how you declare the function after having compiled it into
a shared library (details are in [dfunc](#dfunc).):

```
CREATE FUNCTION execq(text, integer) RETURNS int8
AS '`filename`'
LANGUAGE C STRICT;
```

Here is a sample session:

```
=> SELECT execq('CREATE TABLE a (x integer)', 0);
execq
-------
0
(1 row)

=> INSERT INTO a VALUES (execq('INSERT INTO a VALUES (0)', 0));
INSERT 0 1
=> SELECT execq('SELECT * FROM a', 0);
INFO:  EXECQ:  0    -- inserted by execq
INFO:  EXECQ:  1    -- returned by execq and inserted by upper INSERT

execq
-------
2
(1 row)

=> SELECT execq('INSERT INTO a SELECT x + 2 FROM a RETURNING *', 1);
INFO:  EXECQ:  2    -- 0 + 2, then execution was stopped by count
execq
-------
1
(1 row)

=> SELECT execq('SELECT * FROM a', 10);
INFO:  EXECQ:  0
INFO:  EXECQ:  1
INFO:  EXECQ:  2

execq
-------
3              -- 10 is the max value only, 3 is the real number of rows
(1 row)

=> SELECT execq('INSERT INTO a SELECT x + 10 FROM a', 1);
execq
-------
3              -- all rows processed; count does not stop it, because nothing is returned
(1 row)

=> SELECT * FROM a;
x
----
0
1
2
10
11
12
(6 rows)

=> DELETE FROM a;
DELETE 6
=> INSERT INTO a VALUES (execq('SELECT * FROM a', 0) + 1);
INSERT 0 1
=> SELECT * FROM a;
x
---
1                  -- 0 (no rows in a) + 1
(1 row)

=> INSERT INTO a VALUES (execq('SELECT * FROM a', 0) + 1);
INFO:  EXECQ:  1
INSERT 0 1
=> SELECT * FROM a;
x
---
1
2                  -- 1 (there was one row in a) + 1
(2 rows)

-- This demonstrates the data changes visibility rule.
-- execq is called twice and sees different numbers of rows each time:

=> INSERT INTO a SELECT execq('SELECT * FROM a', 0) * x FROM a;
INFO:  EXECQ:  1    -- results from first execq
INFO:  EXECQ:  2
INFO:  EXECQ:  1    -- results from second execq
INFO:  EXECQ:  2
INFO:  EXECQ:  2
INSERT 0 2
=> SELECT * FROM a;
x
---
1
2
2                  -- 2 rows * 1 (x in first row)
6                  -- 3 rows (2 + 1 just inserted) * 2 (x in second row)
(4 rows)
```
