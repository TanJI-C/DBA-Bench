# Event System; Behavior in Threaded Programs; Building libpq Programs; Example Programs

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIV_client_interfaces/01_libpq_-_c_library.md`
- Source Title: `libpq — C Library`
- Source Heading Path: `libpq - C Library > Event System; Behavior in Threaded Programs; Building libpq Programs; Example Programs`
- Source Line Ranges: `4956-5404, 5958-6006, 6007-6126, 6127-6132`
- Chunk ID: `pg16_fact_0076_d250426e54`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1a099fa2eca125461f62e4b9329f892e8fdd009559ddf31b4eba08c6924d4299`

## Retrieval Guidance

- Use When: Implement or compile libpq applications and understand callback/threading behavior.
- Retrieval Keywords: libpq event system, PGEventProc, thread-safe libpq, PQisthreadsafe, pg_config --libdir, libpq example
- Follow-up Guidance: Consult diagnostic records for runtime connection or query failures.
- Classification Note: These sections are programming reference for event callbacks, thread-safety rules, build/link flags, and example programs rather than operational configuration or repair steps.

## Official Source Content

## Event System

libpq's event system is designed to notify
registered event handlers about interesting
libpq events, such as the creation or
destruction of `PGconn` and
`PGresult` objects.  A principal use case is that
this allows applications to associate their own data with a
`PGconn` or `PGresult`
and ensure that that data is freed at an appropriate time.

Each registered event handler is associated with two pieces of data,
known to libpq only as opaque `void *`
pointers.  There is a *pass-through* pointer that is provided
by the application when the event handler is registered with a
`PGconn`.  The pass-through pointer never changes for the
life of the `PGconn` and all `PGresult`s
generated from it; so if used, it must point to long-lived data.
In addition there is an *instance data* pointer, which starts
out `NULL` in every `PGconn` and `PGresult`.
This pointer can be manipulated using the
[libpq-PQinstanceData](#libpq-PQinstanceData),
[libpq-PQsetInstanceData](#libpq-PQsetInstanceData),
[libpq-PQresultInstanceData](#libpq-PQresultInstanceData) and
[libpq-PQresultSetInstanceData](#libpq-PQresultSetInstanceData) functions.  Note that
unlike the pass-through pointer, instance data of a `PGconn`
is not automatically inherited by `PGresult`s created from
it.  libpq does not know what pass-through
and instance data pointers point to (if anything) and will never attempt
to free them — that is the responsibility of the event handler.

### Event Types

The enum `PGEventId` names the types of events handled by
the event system.  All its values have names beginning with
`PGEVT`.  For each event type, there is a corresponding
event info structure that carries the parameters passed to the event
handlers.  The event types are:

**`PGEVT_REGISTER`**
: The register event occurs when [libpq-PQregisterEventProc](#libpq-PQregisterEventProc)
is called.  It is the ideal time to initialize any
`instanceData` an event procedure may need.  Only one
register event will be fired per event handler per connection.  If the
event procedure fails (returns zero), the registration is cancelled.

```
typedef struct
{
PGconn *conn;
} PGEventRegister;
```

When a `PGEVT_REGISTER` event is received, the
evtInfo pointer should be cast to a
`PGEventRegister *`.  This structure contains a
`PGconn` that should be in the
`CONNECTION_OK` status; guaranteed if one calls
[libpq-PQregisterEventProc](#libpq-PQregisterEventProc) right after obtaining a good
`PGconn`.  When returning a failure code, all
cleanup must be performed as no `PGEVT_CONNDESTROY`
event will be sent.

**`PGEVT_CONNRESET`**
: The connection reset event is fired on completion of
[libpq-PQreset](#libpq-PQreset) or `PQresetPoll`.  In
both cases, the event is only fired if the reset was successful.
The return value of the event procedure is ignored
in PostgreSQL v15 and later.
With earlier versions, however, it's important to return success
(nonzero) or the connection will be aborted.

```
typedef struct
{
PGconn *conn;
} PGEventConnReset;
```

When a `PGEVT_CONNRESET` event is received, the
evtInfo pointer should be cast to a
`PGEventConnReset *`.  Although the contained
`PGconn` was just reset, all event data remains
unchanged.  This event should be used to reset/reload/requery any
associated `instanceData`.  Note that even if the
event procedure fails to process `PGEVT_CONNRESET`, it will
still receive a `PGEVT_CONNDESTROY` event when the connection
is closed.

**`PGEVT_CONNDESTROY`**
: The connection destroy event is fired in response to
[libpq-PQfinish](#libpq-PQfinish).  It is the event procedure's
responsibility to properly clean up its event data as libpq has no
ability to manage this memory.  Failure to clean up will lead
to memory leaks.

```
typedef struct
{
PGconn *conn;
} PGEventConnDestroy;
```

When a `PGEVT_CONNDESTROY` event is received, the
evtInfo pointer should be cast to a
`PGEventConnDestroy *`.  This event is fired
prior to [libpq-PQfinish](#libpq-PQfinish) performing any other cleanup.
The return value of the event procedure is ignored since there is no
way of indicating a failure from [libpq-PQfinish](#libpq-PQfinish).  Also,
an event procedure failure should not abort the process of cleaning up
unwanted memory.

**`PGEVT_RESULTCREATE`**
: The result creation event is fired in response to any query execution
function that generates a result, including
[libpq-PQgetResult](#libpq-PQgetResult).  This event will only be fired after
the result has been created successfully.

```
typedef struct
{
PGconn *conn;
PGresult *result;
} PGEventResultCreate;
```

When a `PGEVT_RESULTCREATE` event is received, the
evtInfo pointer should be cast to a
`PGEventResultCreate *`.  The
conn is the connection used to generate the
result.  This is the ideal place to initialize any
`instanceData` that needs to be associated with the
result.  If an event procedure fails (returns zero), that event
procedure will be ignored for the remaining lifetime of the result;
that is, it will not receive `PGEVT_RESULTCOPY`
or `PGEVT_RESULTDESTROY` events for this result or
results copied from it.

**`PGEVT_RESULTCOPY`**
: The result copy event is fired in response to
[libpq-PQcopyResult](#libpq-PQcopyResult).  This event will only be fired after
the copy is complete.  Only event procedures that have
successfully handled the `PGEVT_RESULTCREATE`
or `PGEVT_RESULTCOPY` event for the source result
will receive `PGEVT_RESULTCOPY` events.

```
typedef struct
{
const PGresult *src;
PGresult *dest;
} PGEventResultCopy;
```

When a `PGEVT_RESULTCOPY` event is received, the
evtInfo pointer should be cast to a
`PGEventResultCopy *`.  The
src result is what was copied while the
dest result is the copy destination.  This event
can be used to provide a deep copy of `instanceData`,
since `PQcopyResult` cannot do that.  If an event
procedure fails (returns zero), that event procedure will be
ignored for the remaining lifetime of the new result; that is, it
will not receive `PGEVT_RESULTCOPY`
or `PGEVT_RESULTDESTROY` events for that result or
results copied from it.

**`PGEVT_RESULTDESTROY`**
: The result destroy event is fired in response to a
[libpq-PQclear](#libpq-PQclear).  It is the event procedure's
responsibility to properly clean up its event data as libpq has no
ability to manage this memory.  Failure to clean up will lead
to memory leaks.

```
typedef struct
{
PGresult *result;
} PGEventResultDestroy;
```

When a `PGEVT_RESULTDESTROY` event is received, the
evtInfo pointer should be cast to a
`PGEventResultDestroy *`.  This event is fired
prior to [libpq-PQclear](#libpq-PQclear) performing any other cleanup.
The return value of the event procedure is ignored since there is no
way of indicating a failure from [libpq-PQclear](#libpq-PQclear).  Also,
an event procedure failure should not abort the process of cleaning up
unwanted memory.

### Event Callback Procedure

**`PGEventProc`**
: `PGEventProc` is a typedef for a pointer to an
event procedure, that is, the user callback function that receives
events from libpq.  The signature of an event procedure must be

```
int eventproc(PGEventId evtId, void *evtInfo, void *passThrough)
```

The evtId parameter indicates which
`PGEVT` event occurred.  The
evtInfo pointer must be cast to the appropriate
structure type to obtain further information about the event.
The passThrough parameter is the pointer
provided to [libpq-PQregisterEventProc](#libpq-PQregisterEventProc) when the event
procedure was registered.  The function should return a non-zero value
if it succeeds and zero if it fails.

A particular event procedure can be registered only once in any
`PGconn`.  This is because the address of the procedure
is used as a lookup key to identify the associated instance data.

> **Caution:**
> On Windows, functions can have two different addresses: one visible
> from outside a DLL and another visible from inside the DLL.  One
> should be careful that only one of these addresses is used with
> libpq's event-procedure functions, else confusion will
> result.  The simplest rule for writing code that will work is to
> ensure that event procedures are declared `static`.  If the
> procedure's address must be available outside its own source file,
> expose a separate function to return the address.
>

### Event Support Functions

**`PQregisterEventProc`**
: Registers an event callback procedure with libpq.

```
int PQregisterEventProc(PGconn *conn, PGEventProc proc,
const char *name, void *passThrough);
```

An event procedure must be registered once on each
`PGconn` you want to receive events about.  There is no
limit, other than memory, on the number of event procedures that
can be registered with a connection.  The function returns a non-zero
value if it succeeds and zero if it fails.

The proc argument will be called when a libpq
event is fired.  Its memory address is also used to lookup
`instanceData`.  The name
argument is used to refer to the event procedure in error messages.
This value cannot be `NULL` or a zero-length string.  The name string is
copied into the `PGconn`, so what is passed need not be
long-lived.  The passThrough pointer is passed
to the proc whenever an event occurs. This
argument can be `NULL`.

**`PQsetInstanceData`**
: Sets the connection conn's `instanceData`
for procedure proc to data.  This
returns non-zero for success and zero for failure.  (Failure is
only possible if proc has not been properly
registered in conn.)

```
int PQsetInstanceData(PGconn *conn, PGEventProc proc, void *data);
```

**`PQinstanceData`**
: Returns the
connection conn's `instanceData`
associated with procedure proc,
or `NULL` if there is none.

```
void *PQinstanceData(const PGconn *conn, PGEventProc proc);
```

**`PQresultSetInstanceData`**
: Sets the result's `instanceData`
for proc to data.  This returns
non-zero for success and zero for failure.  (Failure is only
possible if proc has not been properly registered
in the result.)

```
int PQresultSetInstanceData(PGresult *res, PGEventProc proc, void *data);
```

Beware that any storage represented by data
will not be accounted for by [libpq-PQresultMemorySize](#libpq-PQresultMemorySize),
unless it is allocated using [libpq-PQresultAlloc](#libpq-PQresultAlloc).
(Doing so is recommendable because it eliminates the need to free
such storage explicitly when the result is destroyed.)

**`PQresultInstanceData`**
: Returns the result's `instanceData` associated with proc, or `NULL`
if there is none.

```
void *PQresultInstanceData(const PGresult *res, PGEventProc proc);
```

### Event Example

Here is a skeleton example of managing private data associated with
libpq connections and results.

```

/* required header for libpq events (note: includes libpq-fe.h) */
#include

/* The instanceData */
typedef struct
{
int n;
char *str;
} mydata;

/* PGEventProc */
static int myEventProc(PGEventId evtId, void *evtInfo, void *passThrough);

int
main(void)
{
mydata *data;
PGresult *res;
PGconn *conn =
PQconnectdb("dbname=postgres options=-csearch_path=");

if (PQstatus(conn) != CONNECTION_OK)
{
/* PQerrorMessage's result includes a trailing newline */
fprintf(stderr, "%s", PQerrorMessage(conn));
PQfinish(conn);
return 1;
}

/* called once on any connection that should receive events.
* Sends a PGEVT_REGISTER to myEventProc.
*/
if (!PQregisterEventProc(conn, myEventProc, "mydata_proc", NULL))
{
fprintf(stderr, "Cannot register PGEventProc\n");
PQfinish(conn);
return 1;
}

/* conn instanceData is available */
data = PQinstanceData(conn, myEventProc);

/* Sends a PGEVT_RESULTCREATE to myEventProc */
res = PQexec(conn, "SELECT 1 + 1");

/* result instanceData is available */
data = PQresultInstanceData(res, myEventProc);

/* If PG_COPYRES_EVENTS is used, sends a PGEVT_RESULTCOPY to myEventProc */
res_copy = PQcopyResult(res, PG_COPYRES_TUPLES | PG_COPYRES_EVENTS);

/* result instanceData is available if PG_COPYRES_EVENTS was
* used during the PQcopyResult call.
*/
data = PQresultInstanceData(res_copy, myEventProc);

/* Both clears send a PGEVT_RESULTDESTROY to myEventProc */
PQclear(res);
PQclear(res_copy);

/* Sends a PGEVT_CONNDESTROY to myEventProc */
PQfinish(conn);

return 0;
}

static int
myEventProc(PGEventId evtId, void *evtInfo, void *passThrough)
{
switch (evtId)
{
case PGEVT_REGISTER:
{
PGEventRegister *e = (PGEventRegister *)evtInfo;
mydata *data = get_mydata(e->conn);

/* associate app specific data with connection */
PQsetInstanceData(e->conn, myEventProc, data);
break;
}

case PGEVT_CONNRESET:
{
PGEventConnReset *e = (PGEventConnReset *)evtInfo;
mydata *data = PQinstanceData(e->conn, myEventProc);

if (data)
memset(data, 0, sizeof(mydata));
break;
}

case PGEVT_CONNDESTROY:
{
PGEventConnDestroy *e = (PGEventConnDestroy *)evtInfo;
mydata *data = PQinstanceData(e->conn, myEventProc);

/* free instance data because the conn is being destroyed */
if (data)
free_mydata(data);
break;
}

case PGEVT_RESULTCREATE:
{
PGEventResultCreate *e = (PGEventResultCreate *)evtInfo;
mydata *conn_data = PQinstanceData(e->conn, myEventProc);
mydata *res_data = dup_mydata(conn_data);

/* associate app specific data with result (copy it from conn) */
PQresultSetInstanceData(e->result, myEventProc, res_data);
break;
}

case PGEVT_RESULTCOPY:
{
PGEventResultCopy *e = (PGEventResultCopy *)evtInfo;
mydata *src_data = PQresultInstanceData(e->src, myEventProc);
mydata *dest_data = dup_mydata(src_data);

/* associate app specific data with result (copy it from a result) */
PQresultSetInstanceData(e->dest, myEventProc, dest_data);
break;
}

case PGEVT_RESULTDESTROY:
{
PGEventResultDestroy *e = (PGEventResultDestroy *)evtInfo;
mydata *data = PQresultInstanceData(e->result, myEventProc);

/* free instance data because the result is being destroyed */
if (data)
free_mydata(data);
break;
}

/* unknown event ID, just return true. */
default:
break;
}

return true; /* event processing succeeded */
}

```

## Behavior in Threaded Programs

libpq is reentrant and thread-safe by default.
You might need to use special compiler command-line
options when you compile your application code.  Refer to your
system's documentation for information about how to build
thread-enabled applications, or look in
`src/Makefile.global` for `PTHREAD_CFLAGS`
and `PTHREAD_LIBS`.  This function allows the querying of
libpq's thread-safe status:

**`PQisthreadsafe`**
: Returns the thread safety status of the
libpq library.

```
int PQisthreadsafe();
```

Returns 1 if the libpq is thread-safe
and 0 if it is not.

One thread restriction is that no two threads attempt to manipulate
the same `PGconn` object at the same time. In particular,
you cannot issue concurrent commands from different threads through
the same connection object. (If you need to run concurrent commands,
use multiple connections.)

`PGresult` objects are normally read-only after creation,
and so can be passed around freely between threads.  However, if you use
any of the `PGresult`-modifying functions described in
[libpq-misc](#libpq-misc) or [libpq-events](#libpq-events), it's up
to you to avoid concurrent operations on the same `PGresult`,
too.

The deprecated functions [libpq-PQrequestCancel](#libpq-PQrequestCancel) and
[libpq-PQoidStatus](#libpq-PQoidStatus) are not thread-safe and should not be
used in multithread programs.  [libpq-PQrequestCancel](#libpq-PQrequestCancel)
can be replaced by [libpq-PQcancel](#libpq-PQcancel).
[libpq-PQoidStatus](#libpq-PQoidStatus) can be replaced by
[libpq-PQoidValue](#libpq-PQoidValue).

If you are using Kerberos inside your application (in addition to inside
libpq), you will need to do locking around
Kerberos calls because Kerberos functions are not thread-safe.  See
function `PQregisterThreadLock` in the
libpq source code for a way to do cooperative
locking between libpq and your application.

## Building libpq Programs

To build (i.e., compile and link) a program using
libpq you need to do all of the following
things:

- Include the `libpq-fe.h` header file:

```
#include
```

If you failed to do that then you will normally get error messages
from your compiler similar to:

```
foo.c: In function `main':
foo.c:34: `PGconn' undeclared (first use in this function)
foo.c:35: `PGresult' undeclared (first use in this function)
foo.c:54: `CONNECTION_BAD' undeclared (first use in this function)
foo.c:68: `PGRES_COMMAND_OK' undeclared (first use in this function)
foo.c:95: `PGRES_TUPLES_OK' undeclared (first use in this function)
```
- Point your compiler to the directory where the PostgreSQL header
files were installed, by supplying the
`-I`directory`` option
to your compiler.  (In some cases the compiler will look into
the directory in question by default, so you can omit this
option.)  For instance, your compile command line could look
like:

```
cc -c -I/usr/local/pgsql/include testprog.c
```

If you are using makefiles then add the option to the
`CPPFLAGS` variable:

```
CPPFLAGS += -I/usr/local/pgsql/include
```

If there is any chance that your program might be compiled by
other users then you should not hardcode the directory location
like that.  Instead, you can run the utility
`pg_config` to find out where the header
files are on the local system:

```
$ pg_config --includedir
/usr/local/include
```

If you
have `pkg-config` installed, you can run instead:

```
$ pkg-config --cflags libpq
-I/usr/local/include
```

Note that this will already include the `-I` in front of
the path.

Failure to specify the correct option to the compiler will
result in an error message such as:

```
testlibpq.c:8:22: libpq-fe.h: No such file or directory
```
- When linking the final program, specify the option
`-lpq` so that the libpq
library gets pulled in, as well as the option
`-L`directory`` to point
the compiler to the directory where the
libpq library resides.  (Again, the
compiler will search some directories by default.)  For maximum
portability, put the `-L` option before the
`-lpq` option.  For example:

```
cc -o testprog testprog1.o testprog2.o -L/usr/local/pgsql/lib -lpq
```

You can find out the library directory using
`pg_config` as well:

```
$ pg_config --libdir
/usr/local/pgsql/lib
```

Or again use `pkg-config`:

```
$ pkg-config --libs libpq
-L/usr/local/pgsql/lib -lpq
```

Note again that this prints the full options, not only the path.

Error messages that point to problems in this area could look like
the following:

```
testlibpq.o: In function `main':
testlibpq.o(.text+0x60): undefined reference to `PQsetdbLogin'
testlibpq.o(.text+0x71): undefined reference to `PQstatus'
testlibpq.o(.text+0xa4): undefined reference to `PQerrorMessage'
```

This means you forgot `-lpq`.

```
/usr/bin/ld: cannot find -lpq
```

This means you forgot the `-L` option or did not
specify the right directory.

## Example Programs

These examples and others can be found in the
directory `src/test/examples` in the source code
distribution.
