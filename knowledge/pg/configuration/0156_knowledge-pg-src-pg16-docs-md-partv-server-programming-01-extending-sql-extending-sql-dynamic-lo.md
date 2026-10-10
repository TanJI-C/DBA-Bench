# Dynamic Loading; Function Optimization Information; Operator Optimization Information; Extension Building Infrastructure

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partV_server_programming/01_extending_sql.md`
- Source Title: `Extending SQL`
- Source Heading Path: `Extending SQL > Dynamic Loading; Function Optimization Information; Operator Optimization Information; Extension Building Infrastructure`
- Source Line Ranges: `1764-1849, 3107-3202, 4118-4418, 5069-5329`
- Chunk ID: `pg16_configuration_0156_9c83546a80`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cdb266a358fc84c9df42a764e410950c73dcdeff02b47989661e1b89030dd30f`

## Retrieval Guidance

- Use When: Set extension metadata that affects loading, planner choices, upgrade behavior, or extension installation semantics.
- Retrieval Keywords: dynamic_library_path, function cost, function rows, volatility, support function, operator selectivity, extension control file, relocatable extension
- Follow-up Guidance: Validate planner-facing settings with workload-specific plans because incorrect cost/selectivity metadata can mislead the optimizer.
- Classification Note: These sections define tunable metadata and declarative attributes such as dynamic library lookup, function volatility/cost/rows/support behavior, operator selectivity hooks, and extension control-file properties.

## Official Source Content

### Dynamic Loading

The first time a user-defined function in a particular
loadable object file is called in a session,
the dynamic loader loads that object file into memory so that the
function can be called.  The `CREATE FUNCTION`
for a user-defined C function must therefore specify two pieces of
information for the function: the name of the loadable
object file, and the C name (link symbol) of the specific function to call
within that object file.  If the C name is not explicitly specified then
it is assumed to be the same as the SQL function name.

The following algorithm is used to locate the shared object file
based on the name given in the `CREATE FUNCTION`
command:

1. If the name is an absolute path, the given file is loaded.
2. If the name starts with the string `$libdir`,
that part is replaced by the PostgreSQL package
library directory
name, which is determined at build time.
3. If the name does not contain a directory part, the file is
searched for in the path specified by the configuration variable
[guc-dynamic-library-path](#guc-dynamic-library-path).
4. Otherwise (the file was not found in the path, or it contains a
non-absolute directory part), the dynamic loader will try to
take the name as given, which will most likely fail.  (It is
unreliable to depend on the current working directory.)

If this sequence does not work, the platform-specific shared
library file name extension (often `.so`) is
appended to the given name and this sequence is tried again.  If
that fails as well, the load will fail.

It is recommended to locate shared libraries either relative to
`$libdir` or through the dynamic library path.
This simplifies version upgrades if the new installation is at a
different location.  The actual directory that
`$libdir` stands for can be found out with the
command `pg_config --pkglibdir`.

The user ID the PostgreSQL server runs
as must be able to traverse the path to the file you intend to
load.  Making the file or a higher-level directory not readable
and/or not executable by the postgres
user is a common mistake.

In any case, the file name that is given in the
`CREATE FUNCTION` command is recorded literally
in the system catalogs, so if the file needs to be loaded again
the same procedure is applied.

> **Note:**

> PostgreSQL will not compile a C function
> automatically.  The object file must be compiled before it is referenced
> in a `CREATE
> FUNCTION` command.  See [dfunc](#dfunc) for additional
> information.
>

To ensure that a dynamically loaded object file is not loaded into an
incompatible server, PostgreSQL checks that the
file contains a "magic block" with the appropriate contents.
This allows the server to detect obvious incompatibilities, such as code
compiled for a different major version of
PostgreSQL. To include a magic block,
write this in one (and only one) of the module source files, after having
included the header `fmgr.h`:

```
PG_MODULE_MAGIC;
```

After it is used for the first time, a dynamically loaded object
file is retained in memory.  Future calls in the same session to
the function(s) in that file will only incur the small overhead of
a symbol table lookup.  If you need to force a reload of an object
file, for example after recompiling it, begin a fresh session.

Optionally, a dynamically loaded file can contain an initialization
function.  If the file includes a function named
`_PG_init`, that function will be called immediately after
loading the file.  The function receives no parameters and should
return void.  There is presently no way to unload a dynamically loaded file.

## Function Optimization Information

By default, a function is just a "black box" that the
database system knows very little about the behavior of.  However,
that means that queries using the function may be executed much less
efficiently than they could be.  It is possible to supply additional
knowledge that helps the planner optimize function calls.

Some basic facts can be supplied by declarative annotations provided in
the [`CREATE FUNCTION`](#sql-createfunction) command.  Most important of
these is the function's [volatility
category](#xfunc-volatility) (`IMMUTABLE`, `STABLE`,
or `VOLATILE`); one should always be careful to
specify this correctly when defining a function.
The parallel safety property (`PARALLEL
UNSAFE`, `PARALLEL RESTRICTED`, or
`PARALLEL SAFE`) must also be specified if you hope
to use the function in parallelized queries.
It can also be useful to specify the function's estimated execution
cost, and/or the number of rows a set-returning function is estimated
to return.  However, the declarative way of specifying those two
facts only allows specifying a constant value, which is often
inadequate.

It is also possible to attach a *planner support
function* to an SQL-callable function (called
its *target function*), and thereby provide
knowledge about the target function that is too complex to be
represented declaratively.  Planner support functions have to be
written in C (although their target functions might not be), so this is
an advanced feature that relatively few people will use.

A planner support function must have the SQL signature

```
supportfn(internal) returns internal
```

It is attached to its target function by specifying
the `SUPPORT` clause when creating the target function.

The details of the API for planner support functions can be found in
file `src/include/nodes/supportnodes.h` in the
PostgreSQL source code.  Here we provide
just an overview of what planner support functions can do.
The set of possible requests to a support function is extensible,
so more things might be possible in future versions.

Some function calls can be simplified during planning based on
properties specific to the function.  For example,
`int4mul(n, 1)` could be simplified to
just `n`.  This type of transformation can be
performed by a planner support function, by having it implement
the `SupportRequestSimplify` request type.
The support function will be called for each instance of its target
function found in a query parse tree.  If it finds that the particular
call can be simplified into some other form, it can build and return a
parse tree representing that expression.  This will automatically work
for operators based on the function, too — in the example just
given, `n * 1` would also be simplified to
`n`.
(But note that this is just an example; this particular
optimization is not actually performed by
standard PostgreSQL.)
We make no guarantee that PostgreSQL will
never call the target function in cases that the support function could
simplify.  Ensure rigorous equivalence between the simplified
expression and an actual execution of the target function.

For target functions that return `boolean`, it is often useful to estimate
the fraction of rows that will be selected by a `WHERE` clause using that
function.  This can be done by a support function that implements
the `SupportRequestSelectivity` request type.

If the target function's run time is highly dependent on its inputs,
it may be useful to provide a non-constant cost estimate for it.
This can be done by a support function that implements
the `SupportRequestCost` request type.

For target functions that return sets, it is often useful to provide
a non-constant estimate for the number of rows that will be returned.
This can be done by a support function that implements
the `SupportRequestRows` request type.

For target functions that return `boolean`, it may be possible to
convert a function call appearing in `WHERE` into an indexable operator
clause or clauses.  The converted clauses might be exactly equivalent
to the function's condition, or they could be somewhat weaker (that is,
they might accept some values that the function condition does not).
In the latter case the index condition is said to
be *lossy*; it can still be used to scan an index,
but the function call will have to be executed for each row returned by
the index to see if it really passes the `WHERE` condition or not.
To create such conditions, the support function must implement
the `SupportRequestIndexCondition` request type.

## Operator Optimization Information

A PostgreSQL operator definition can include
several optional clauses that tell the system useful things about how
the operator behaves.  These clauses should be provided whenever
appropriate, because they can make for considerable speedups in execution
of queries that use the operator.  But if you provide them, you must be
sure that they are right!  Incorrect use of an optimization clause can
result in slow queries, subtly wrong output, or other Bad Things.
You can always leave out an optimization clause if you are not sure
about it; the only consequence is that queries might run slower than
they need to.

Additional optimization clauses might be added in future versions of
PostgreSQL.  The ones described here are all
the ones that release  understands.

It is also possible to attach a planner support function to the function
that underlies an operator, providing another way of telling the system
about the behavior of the operator.
See [xfunc-optimization](#xfunc-optimization) for more information.

### `COMMUTATOR`

The `COMMUTATOR` clause, if provided, names an operator that is the
commutator of the operator being defined.  We say that operator A is the
commutator of operator B if (x A y) equals (y B x) for all possible input
values x, y.  Notice that B is also the commutator of A.  For example,
operators `<` and `>` for a particular data type are usually each others'
commutators, and operator `+` is usually commutative with itself.
But operator `-` is usually not commutative with anything.

The left operand type of a commutable operator is the same as the
right operand type of its commutator, and vice versa.  So the name of
the commutator operator is all that PostgreSQL
needs to be given to look up the commutator, and that's all that needs to
be provided in the `COMMUTATOR` clause.

It's critical to provide commutator information for operators that
will be used in indexes and join clauses, because this allows the
query optimizer to "flip around" such a clause to the forms
needed for different plan types.  For example, consider a query with
a WHERE clause like `tab1.x = tab2.y`, where `tab1.x`
and `tab2.y` are of a user-defined type, and suppose that
`tab2.y` is indexed.  The optimizer cannot generate an
index scan unless it can determine how to flip the clause around to
`tab2.y = tab1.x`, because the index-scan machinery expects
to see the indexed column on the left of the operator it is given.
PostgreSQL will *not* simply
assume that this is a valid transformation — the creator of the
`=` operator must specify that it is valid, by marking the
operator with commutator information.

When you are defining a self-commutative operator, you just do it.
When you are defining a pair of commutative operators, things are
a little trickier: how can the first one to be defined refer to the
other one, which you haven't defined yet?  There are two solutions
to this problem:

- One way is to omit the `COMMUTATOR` clause in the first operator that
you define, and then provide one in the second operator's definition.
Since PostgreSQL knows that commutative
operators come in pairs, when it sees the second definition it will
automatically go back and fill in the missing `COMMUTATOR` clause in
the first definition.
- The other, more straightforward way is just to include `COMMUTATOR` clauses
in both definitions.  When PostgreSQL processes
the first definition and realizes that `COMMUTATOR` refers to a nonexistent
operator, the system will make a dummy entry for that operator in the
system catalog.  This dummy entry will have valid data only
for the operator name, left and right operand types, and result type,
since that's all that PostgreSQL can deduce
at this point.  The first operator's catalog entry will link to this
dummy entry.  Later, when you define the second operator, the system
updates the dummy entry with the additional information from the second
definition.  If you try to use the dummy operator before it's been filled
in, you'll just get an error message.

### `NEGATOR`

The `NEGATOR` clause, if provided, names an operator that is the
negator of the operator being defined.  We say that operator A
is the negator of operator B if both return Boolean results and
(x A y) equals NOT (x B y) for all possible inputs x, y.
Notice that B is also the negator of A.
For example, `<` and `>=` are a negator pair for most data types.
An operator can never validly be its own negator.

Unlike commutators, a pair of unary operators could validly be marked
as each other's negators; that would mean (A x) equals NOT (B x)
for all x.

An operator's negator must have the same left and/or right operand types
as the operator to be defined, so just as with `COMMUTATOR`, only the operator
name need be given in the `NEGATOR` clause.

Providing a negator is very helpful to the query optimizer since
it allows expressions like `NOT (x = y)` to be simplified into
`x <> y`.  This comes up more often than you might think, because
`NOT` operations can be inserted as a consequence of other rearrangements.

Pairs of negator operators can be defined using the same methods
explained above for commutator pairs.

### `RESTRICT`

The `RESTRICT` clause, if provided, names a restriction selectivity
estimation function for the operator.  (Note that this is a function
name, not an operator name.)  `RESTRICT` clauses only make sense for
binary operators that return `boolean`.  The idea behind a restriction
selectivity estimator is to guess what fraction of the rows in a
table will satisfy a `WHERE`-clause condition of the form:

```
column OP constant
```

for the current operator and a particular constant value.
This assists the optimizer by
giving it some idea of how many rows will be eliminated by `WHERE`
clauses that have this form.  (What happens if the constant is on
the left, you might be wondering?  Well, that's one of the things that
`COMMUTATOR` is for...)

Writing new restriction selectivity estimation functions is far beyond
the scope of this chapter, but fortunately you can usually just use
one of the system's standard estimators for many of your own operators.
These are the standard restriction estimators:

You can frequently get away with using either `eqsel` or `neqsel` for
operators that have very high or very low selectivity, even if they
aren't really equality or inequality.  For example, the
approximate-equality geometric operators use `eqsel` on the assumption that
they'll usually only match a small fraction of the entries in a table.

You can use `scalarltsel`, `scalarlesel`,
`scalargtsel` and `scalargesel` for comparisons on
data types that have some sensible means of being converted into numeric
scalars for range comparisons.  If possible, add the data type to those
understood by the function `convert_to_scalar()` in
`src/backend/utils/adt/selfuncs.c`.
(Eventually, this function should be replaced by per-data-type functions
identified through a column of the pg_type system catalog; but that hasn't happened
yet.)  If you do not do this, things will still work, but the optimizer's
estimates won't be as good as they could be.

Another useful built-in selectivity estimation function
is `matchingsel`, which will work for almost any
binary operator, if standard MCV and/or histogram statistics are
collected for the input data type(s).  Its default estimate is set to
twice the default estimate used in `eqsel`, making
it most suitable for comparison operators that are somewhat less
strict than equality.  (Or you could call the
underlying `generic_restriction_selectivity`
function, providing a different default estimate.)

There are additional selectivity estimation functions designed for geometric
operators in `src/backend/utils/adt/geo_selfuncs.c`: `areasel`, `positionsel`,
and `contsel`.  At this writing these are just stubs, but you might want
to use them (or even better, improve them) anyway.

### `JOIN`

The `JOIN` clause, if provided, names a join selectivity
estimation function for the operator.  (Note that this is a function
name, not an operator name.)  `JOIN` clauses only make sense for
binary operators that return `boolean`.  The idea behind a join
selectivity estimator is to guess what fraction of the rows in a
pair of tables will satisfy a `WHERE`-clause condition of the form:

```
table1.column1 OP table2.column2
```

for the current operator.  As with the `RESTRICT` clause, this helps
the optimizer very substantially by letting it figure out which
of several possible join sequences is likely to take the least work.

As before, this chapter will make no attempt to explain how to write
a join selectivity estimator function, but will just suggest that
you use one of the standard estimators if one is applicable:

### `HASHES`

The `HASHES` clause, if present, tells the system that
it is permissible to use the hash join method for a join based on this
operator.  `HASHES` only makes sense for a binary operator that
returns `boolean`, and in practice the operator must represent
equality for some data type or pair of data types.

The assumption underlying hash join is that the join operator can
only return true for pairs of left and right values that hash to the
same hash code.  If two values get put in different hash buckets, the
join will never compare them at all, implicitly assuming that the
result of the join operator must be false.  So it never makes sense
to specify `HASHES` for operators that do not represent
some form of equality.  In most cases it is only practical to support
hashing for operators that take the same data type on both sides.
However, sometimes it is possible to design compatible hash functions
for two or more data types; that is, functions that will generate the
same hash codes for "equal" values, even though the values
have different representations.  For example, it's fairly simple
to arrange this property when hashing integers of different widths.

To be marked `HASHES`, the join operator must appear
in a hash index operator family.  This is not enforced when you create
the operator, since of course the referencing operator family couldn't
exist yet.  But attempts to use the operator in hash joins will fail
at run time if no such operator family exists.  The system needs the
operator family to find the data-type-specific hash function(s) for the
operator's input data type(s).  Of course, you must also create suitable
hash functions before you can create the operator family.

Care should be exercised when preparing a hash function, because there
are machine-dependent ways in which it might fail to do the right thing.
For example, if your data type is a structure in which there might be
uninteresting pad bits, you cannot simply pass the whole structure to
`hash_any`.  (Unless you write your other operators and
functions to ensure that the unused bits are always zero, which is the
recommended strategy.)
Another example is that on machines that meet the IEEE
floating-point standard, negative zero and positive zero are different
values (different bit patterns) but they are defined to compare equal.
If a float value might contain negative zero then extra steps are needed
to ensure it generates the same hash value as positive zero.

A hash-joinable operator must have a commutator (itself if the two
operand data types are the same, or a related equality operator
if they are different) that appears in the same operator family.
If this is not the case, planner errors might occur when the operator
is used.  Also, it is a good idea (but not strictly required) for
a hash operator family that supports multiple data types to provide
equality operators for every combination of the data types; this
allows better optimization.

> **Note:**

> The function underlying a hash-joinable operator must be marked
> immutable or stable.  If it is volatile, the system will never
> attempt to use the operator for a hash join.
>

> **Note:**

> If a hash-joinable operator has an underlying function that is marked
> strict, the
> function must also be complete: that is, it should return true or
> false, never null, for any two nonnull inputs.  If this rule is
> not followed, hash-optimization of `IN` operations might
> generate wrong results.  (Specifically, `IN` might return
> false where the correct answer according to the standard would be null;
> or it might yield an error complaining that it wasn't prepared for a
> null result.)
>

### `MERGES`

The `MERGES` clause, if present, tells the system that
it is permissible to use the merge-join method for a join based on this
operator.  `MERGES` only makes sense for a binary operator that
returns `boolean`, and in practice the operator must represent
equality for some data type or pair of data types.

Merge join is based on the idea of sorting the left- and right-hand tables
into order and then scanning them in parallel.  So, both data types must
be capable of being fully ordered, and the join operator must be one
that can only succeed for pairs of values that fall at the
"same place"
in the sort order.  In practice this means that the join operator must
behave like equality.  But it is possible to merge-join two
distinct data types so long as they are logically compatible.  For
example, the `smallint`-versus-`integer`
equality operator is merge-joinable.
We only need sorting operators that will bring both data types into a
logically compatible sequence.

To be marked `MERGES`, the join operator must appear
as an equality member of a `btree` index operator family.
This is not enforced when you create
the operator, since of course the referencing operator family couldn't
exist yet.  But the operator will not actually be used for merge joins
unless a matching operator family can be found.  The
`MERGES` flag thus acts as a hint to the planner that
it's worth looking for a matching operator family.

A merge-joinable operator must have a commutator (itself if the two
operand data types are the same, or a related equality operator
if they are different) that appears in the same operator family.
If this is not the case, planner errors might occur when the operator
is used.  Also, it is a good idea (but not strictly required) for
a `btree` operator family that supports multiple data types to provide
equality operators for every combination of the data types; this
allows better optimization.

> **Note:**

> The function underlying a merge-joinable operator must be marked
> immutable or stable.  If it is volatile, the system will never
> attempt to use the operator for a merge join.
>

## Extension Building Infrastructure

If you are thinking about distributing your
PostgreSQL extension modules, setting up a
portable build system for them can be fairly difficult.  Therefore
the PostgreSQL installation provides a build
infrastructure for extensions, called PGXS, so
that simple extension modules can be built simply against an
already installed server.  PGXS is mainly intended
for extensions that include C code, although it can be used for
pure-SQL extensions too.  Note that PGXS is not
intended to be a universal build system framework that can be used
to build any software interfacing to PostgreSQL;
it simply automates common build rules for simple server extension
modules.  For more complicated packages, you might need to write your
own build system.

To use the PGXS infrastructure for your extension,
you must write a simple makefile.
In the makefile, you need to set some variables
and include the global PGXS makefile.
Here is an example that builds an extension module named
`isbn_issn`, consisting of a shared library containing
some C code, an extension control file, an SQL script, an include file
(only needed if other modules might need to access the extension functions
without going via SQL), and a documentation text file:

```
MODULES = isbn_issn
EXTENSION = isbn_issn
DATA = isbn_issn--1.0.sql
DOCS = README.isbn_issn
HEADERS_isbn_issn = isbn_issn.h

PG_CONFIG = pg_config
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)
```

The last three lines should always be the same.  Earlier in the
file, you assign variables or add custom
make rules.

Set one of these three variables to specify what is built:

**`MODULES`**
: list of shared-library objects to be built from source files with same
stem (do not include library suffixes in this list)

**`MODULE_big`**
: a shared library to build from multiple source files
(list object files in `OBJS`)

**`PROGRAM`**
: an executable program to build
(list object files in `OBJS`)

The following variables can also be set:

**`EXTENSION`**
: extension name(s); for each name you must provide an
``extension`.control` file,
which will be installed into
``prefix`/share/extension`

**`MODULEDIR`**
: subdirectory of ``prefix`/share`
into which DATA and DOCS files should be installed
(if not set, default is `extension` if
`EXTENSION` is set,
or `contrib` if not)

**`DATA`**
: random files to install into ``prefix`/share/$MODULEDIR`

**`DATA_built`**
: random files to install into
``prefix`/share/$MODULEDIR`,
which need to be built first

**`DATA_TSEARCH`**
: random files to install under
``prefix`/share/tsearch_data`

**`DOCS`**
: random files to install under
``prefix`/doc/$MODULEDIR`

**`HEADERS`**
: Files to (optionally build and) install under
``prefix`/include/server/$MODULEDIR/$MODULE_big`.

Unlike `DATA_built`, files in `HEADERS_built`
are not removed by the `clean` target; if you want them removed,
also add them to `EXTRA_CLEAN` or add your own rules to do it.

**`HEADERS_$MODULE`**
: Files to install (after building if specified) under
``prefix`/include/server/$MODULEDIR/$MODULE`,
where `$MODULE` must be a module name used
in `MODULES` or `MODULE_big`.

Unlike `DATA_built`, files in `HEADERS_built_$MODULE`
are not removed by the `clean` target; if you want them removed,
also add them to `EXTRA_CLEAN` or add your own rules to do it.

It is legal to use both variables for the same module, or any
combination, unless you have two module names in the
`MODULES` list that differ only by the presence of a
prefix `built_`, which would cause ambiguity. In
that (hopefully unlikely) case, you should use only the
`HEADERS_built_$MODULE` variables.

**`SCRIPTS`**
: script files (not binaries) to install into
``prefix`/bin`

**`SCRIPTS_built`**
: script files (not binaries) to install into
``prefix`/bin`,
which need to be built first

**`REGRESS`**
: list of regression test cases (without suffix), see below

**`REGRESS_OPTS`**
: additional switches to pass to pg_regress

**`ISOLATION`**
: list of isolation test cases, see below for more details

**`ISOLATION_OPTS`**
: additional switches to pass to
pg_isolation_regress

**`TAP_TESTS`**
: switch defining if TAP tests need to be run, see below

**`NO_INSTALL`**
: don't define an `install` target, useful for test
modules that don't need their build products to be installed

**`NO_INSTALLCHECK`**
: don't define an `installcheck` target, useful e.g., if tests require special configuration, or don't use pg_regress

**`EXTRA_CLEAN`**
: extra files to remove in `make clean`

**`PG_CPPFLAGS`**
: will be prepended to `CPPFLAGS`

**`PG_CFLAGS`**
: will be appended to `CFLAGS`

**`PG_CXXFLAGS`**
: will be appended to `CXXFLAGS`

**`PG_LDFLAGS`**
: will be prepended to `LDFLAGS`

**`PG_LIBS`**
: will be added to `PROGRAM` link line

**`SHLIB_LINK`**
: will be added to `MODULE_big` link line

**`PG_CONFIG`**
: path to pg_config program for the
PostgreSQL installation to build against
(typically just `pg_config` to use the first one in your
`PATH`)

Put this makefile as `Makefile` in the directory
which holds your extension. Then you can do
`make` to compile, and then `make
install` to install your module.  By default, the extension is
compiled and installed for the
PostgreSQL installation that
corresponds to the first `pg_config` program
found in your `PATH`.  You can use a different installation by
setting `PG_CONFIG` to point to its
`pg_config` program, either within the makefile
or on the `make` command line.

You can also run `make` in a directory outside the source
tree of your extension, if you want to keep the build directory separate.
This procedure is also called a
*VPATH*
build.  Here's how:

```
mkdir build_dir
cd build_dir
make -f /path/to/extension/source/tree/Makefile
make -f /path/to/extension/source/tree/Makefile install
```

Alternatively, you can set up a directory for a VPATH build in a similar
way to how it is done for the core code. One way to do this is using the
core script `config/prep_buildtree`. Once this has been done
you can build by setting the `make` variable
`VPATH` like this:

```
make VPATH=/path/to/extension/source/tree
make VPATH=/path/to/extension/source/tree install
```

This procedure can work with a greater variety of directory layouts.

The scripts listed in the `REGRESS` variable are used for
regression testing of your module, which can be invoked by `make
installcheck` after doing `make install`.  For this to
work you must have a running PostgreSQL server.
The script files listed in `REGRESS` must appear in a
subdirectory named `sql/` in your extension's directory.
These files must have extension `.sql`, which must not be
included in the `REGRESS` list in the makefile.  For each
test there should also be a file containing the expected output in a
subdirectory named `expected/`, with the same stem and
extension `.out`.  `make installcheck`
executes each test script with psql, and compares the
resulting output to the matching expected file.  Any differences will be
written to the file `regression.diffs` in `diff
-c` format.  Note that trying to run a test that is missing its
expected file will be reported as "trouble", so make sure you
have all expected files.

The scripts listed in the `ISOLATION` variable are used
for tests stressing behavior of concurrent session with your module, which
can be invoked by `make installcheck` after doing
`make install`.  For this to work you must have a
running PostgreSQL server.  The script files
listed in `ISOLATION` must appear in a subdirectory
named `specs/` in your extension's directory.  These files
must have extension `.spec`, which must not be included
in the `ISOLATION` list in the makefile.  For each test
there should also be a file containing the expected output in a
subdirectory named `expected/`, with the same stem and
extension `.out`.  `make installcheck`
executes each test script, and compares the resulting output to the
matching expected file.  Any differences will be written to the file
`output_iso/regression.diffs` in
`diff -c` format.  Note that trying to run a test that is
missing its expected file will be reported as "trouble", so
make sure you have all expected files.

`TAP_TESTS` enables the use of TAP tests.  Data from each
run is present in a subdirectory named `tmp_check/`.
See also [regress-tap](#regress-tap) for more details.

> **Tip:**

> The easiest way to create the expected files is to create empty files,
> then do a test run (which will of course report differences).  Inspect
> the actual result files found in the `results/`
> directory (for tests in `REGRESS`), or
> `output_iso/results/` directory (for tests in
> `ISOLATION`), then copy them to
> `expected/` if they match what you expect from the test.
>
