# Installation; GUC Parameters; Features; Sepgsql Functions; Limitations

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/06_additional_supplied_modules_and_extensions.md`
- Source Title: `postgresql.conf`
- Source Heading Path: `Additional Supplied Modules and Extensions > sepgsql > Installation; GUC Parameters; Features; Sepgsql Functions; Limitations`
- Source Line Ranges: `1055-1066, 1256-1303, 4279-4294, 5954-5964, 6072-6089, 7305-7320, 7321-7443, 7444-7483, 7484-7491, 7492-7503, 8756-9298, 9299-9387`
- Chunk ID: `pg16_configuration_0176_7aba25c6d4`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b108e9ae3c450b3f20cee6caa10150b99e2b65864915d7ac25a8e15a7cd7d623`

## Retrieval Guidance

- Use When: Configure SELinux-backed security policy integration for PostgreSQL.
- Retrieval Keywords: sepgsql, SELinux, sepgsql.permissive, sepgsql.debug_audit, security label, mandatory access control
- Follow-up Guidance: Human security review is recommended before enabling or changing SELinux database policy.
- Classification Note: The module defines SELinux integration, installation prerequisites, GUCs, and controlled-object behavior that configure mandatory access control.

## Official Source Content

### Limitations

- Only operator classes for `int4` and `text` are
included with the module.
- Only the `=` operator is supported for search.  But
it is possible to add support for arrays with union and intersection
operations in the future.
- `bloom` access method doesn't support
`UNIQUE` indexes.
- `bloom` access method doesn't support searching for
`NULL` values.

### Limitations

- `citext`'s case-folding behavior depends on
the `LC_CTYPE` setting of your database. How it compares
values is therefore determined when the database is created.
It is not truly
case-insensitive in the terms defined by the Unicode standard.
Effectively, what this means is that, as long as you're happy with your
collation, you should be happy with `citext`'s comparisons. But
if you have data in different languages stored in your database, users
of one language may find their query results are not as expected if the
collation is for another language.
- As of PostgreSQL 9.1, you can attach a
`COLLATE` specification to `citext` columns or data
values.  Currently, `citext` operators will honor a non-default
`COLLATE` specification while comparing case-folded strings,
but the initial folding to lower case is always done according to the
database's `LC_CTYPE` setting (that is, as though
`COLLATE "default"` were given).  This may be changed in a
future release so that both steps follow the input `COLLATE`
specification.
- `citext` is not as efficient as `text` because the
operator functions and the B-tree comparison functions must make copies
of the data and convert it to lower case for comparisons.  Also, only
`text` can support B-Tree deduplication.  However,
`citext` is slightly more efficient than using
`lower` to get case-insensitive matching.
- `citext` doesn't help much if you need data to compare
case-sensitively in some contexts and case-insensitively in other
contexts.  The standard answer is to use the `text` type and
manually use the `lower` function when you need to compare
case-insensitively; this works all right if case-insensitive comparison
is needed only infrequently.  If you need case-insensitive behavior most
of the time and case-sensitive infrequently, consider storing the data
as `citext` and explicitly casting the column to `text`
when you want case-sensitive comparison.  In either situation, you will
need two indexes if you want both types of searches to be fast.
- The schema containing the `citext` operators must be
in the current `search_path` (typically `public`);
if it is not, the normal case-sensitive `text` operators
will be invoked instead.
- The approach of lower-casing strings for comparison does not handle some
Unicode special cases correctly, for example when one upper-case letter
has two lower-case letter equivalents.  Unicode distinguishes between
*case mapping* and *case
folding* for this reason.  Use nondeterministic collations
instead of `citext` to handle that correctly.

### Limitations

- Dropping a table will still orphan any objects it contains, as the trigger
is not executed.  You can avoid this by preceding the `DROP
TABLE` with `DELETE FROM `table``.

`TRUNCATE` has the same hazard.

If you already have, or suspect you have, orphaned large objects, see the
[vacuumlo](#vacuumlo) module to help
you clean them up.  It's a good idea to run vacuumlo
occasionally as a back-stop to the `lo_manage` trigger.
- Some frontends may create their own tables, and will not create the
associated trigger(s).  Also, users may not remember (or know) to create
the triggers.

#### Limitations of PGP Code

- No support for signing.  That also means that it is not checked
whether the encryption subkey belongs to the master key.
- No support for encryption key as master key.  As such practice
is generally discouraged, this should not be a problem.
- No support for several subkeys.  This may seem like a problem, as this
is common practice.  On the other hand, you should not use your regular
GPG/PGP keys with `pgcrypto`, but create new ones,
as the usage scenario is rather different.

#### Security Limitations

All `pgcrypto` functions run inside the database server.
That means that all
the data and passwords move between `pgcrypto` and client
applications in clear text.  Thus you must:

1. Connect locally or use SSL connections.
2. Trust both system and database administrator.

If you cannot, then better do crypto inside client application.

The implementation does not resist
[side-channel
attacks](https://en.wikipedia.org/wiki/Side-channel_attack).  For example, the time required for
a `pgcrypto` decryption function to complete varies among
ciphertexts of a given size.

### GUC Parameters

**`pg_trgm.similarity_threshold` (`real`)**
: Sets the current similarity threshold that is used by the `%`
operator.  The threshold must be between 0 and 1 (default is 0.3).

**`pg_trgm.word_similarity_threshold` (`real`)**
: Sets the current word similarity threshold that is used by the
`` operators.  The threshold
must be between 0 and 1 (default is 0.6).

**`pg_trgm.strict_word_similarity_threshold` (`real`)**
: Sets the current strict word similarity threshold that is used by the
`>` operators.  The threshold
must be between 0 and 1 (default is 0.5).

### Index Support

The `pg_trgm` module provides GiST and GIN index
operator classes that allow you to create an index over a text column for
the purpose of very fast similarity searches.  These index types support
the above-described similarity operators, and additionally support
trigram-based index searches for `LIKE`, `ILIKE`,
`~`, `~*` and `=` queries.
The similarity comparisons are case-insensitive in a default build of
`pg_trgm`.
Inequality operators are not supported.
Note that those indexes may not be as efficient as regular B-tree indexes
for equality operator.

Example:

```
CREATE TABLE test_trgm (t text);
CREATE INDEX trgm_idx ON test_trgm USING GIST (t gist_trgm_ops);
```

or

```
CREATE INDEX trgm_idx ON test_trgm USING GIN (t gin_trgm_ops);
```

`gist_trgm_ops` GiST opclass approximates a set of
trigrams as a bitmap signature.  Its optional integer parameter
`siglen` determines the
signature length in bytes.  The default length is 12 bytes.
Valid values of signature length are between 1 and 2024 bytes.  Longer
signatures lead to a more precise search (scanning a smaller fraction of the index and
fewer heap pages), at the cost of a larger index.

Example of creating such an index with a signature length of 32 bytes:

```
CREATE INDEX trgm_idx ON test_trgm USING GIST (t gist_trgm_ops(siglen=32));
```

At this point, you will have an index on the `t` column that
you can use for similarity searching.  A typical query is

```
SELECT t, similarity(t, '`word`') AS sml
FROM test_trgm
WHERE t % '`word`'
ORDER BY sml DESC, t;
```

This will return all values in the text column that are sufficiently
similar to `word`, sorted from best match to worst.  The
index will be used to make this a fast operation even over very large data
sets.

A variant of the above query is

```
SELECT t, t  '`word`' AS dist
FROM test_trgm
ORDER BY dist LIMIT 10;
```

This can be implemented quite efficiently by GiST indexes, but not
by GIN indexes.  It will usually beat the first formulation when only
a small number of the closest matches is wanted.

Also you can use an index on the `t` column for word
similarity or strict word similarity.  Typical queries are:

```
SELECT t, word_similarity('`word`', t) AS sml
FROM test_trgm
WHERE '`word`'  t AS dist
FROM test_trgm
ORDER BY dist LIMIT 10;
```

and

```
SELECT t, '`word`'  t AS dist
FROM test_trgm
ORDER BY dist LIMIT 10;
```

This can be implemented quite efficiently by GiST indexes, but not
by GIN indexes.

Beginning in PostgreSQL 9.1, these index types also support
index searches for `LIKE` and `ILIKE`, for example

```
SELECT * FROM test_trgm WHERE t LIKE '%foo%bar';
```

The index search works by extracting trigrams from the search string
and then looking these up in the index.  The more trigrams in the search
string, the more effective the index search is.  Unlike B-tree based
searches, the search string need not be left-anchored.

Beginning in PostgreSQL 9.3, these index types also support
index searches for regular-expression matches
(`~` and `~*` operators), for example

```
SELECT * FROM test_trgm WHERE t ~ '(foo|bar)';
```

The index search works by extracting trigrams from the regular expression
and then looking these up in the index.  The more trigrams that can be
extracted from the regular expression, the more effective the index search
is.  Unlike B-tree based searches, the search string need not be
left-anchored.

For both `LIKE` and regular-expression searches, keep in mind
that a pattern with no extractable trigrams will degenerate to a full-index
scan.

The choice between GiST and GIN indexing depends on the relative
performance characteristics of GiST and GIN, which are discussed elsewhere.

### Text Search Integration

Trigram matching is a very useful tool when used in conjunction
with a full text index.  In particular it can help to recognize
misspelled input words that will not be matched directly by the
full text search mechanism.

The first step is to generate an auxiliary table containing all
the unique words in the documents:

```
CREATE TABLE words AS SELECT word FROM
ts_stat('SELECT to_tsvector(''simple'', bodytext) FROM documents');
```

where `documents` is a table that has a text field
`bodytext` that we wish to search.  The reason for using
the `simple` configuration with the `to_tsvector`
function, instead of using a language-specific configuration,
is that we want a list of the original (unstemmed) words.

Next, create a trigram index on the word column:

```
CREATE INDEX words_idx ON words USING GIN (word gin_trgm_ops);
```

Now, a `SELECT` query similar to the previous example can
be used to suggest spellings for misspelled words in user search terms.
A useful extra test is to require that the selected words are also of
similar length to the misspelled word.

> **Note:**

> Since the `words` table has been generated as a separate,
> static table, it will need to be periodically regenerated so that
> it remains reasonably up-to-date with the document collection.
> Keeping it exactly current is usually unnecessary.
>

### References

GiST Development Site
[](http://www.sai.msu.su/~megera/postgres/gist/)

Tsearch2 Development Site
[](http://www.sai.msu.su/~megera/postgres/gist/tsearch/V2/)

### Authors

Oleg Bartunov oleg@sai.msu.su, Moscow, Moscow University, Russia

Teodor Sigaev teodor@sigaev.ru, Moscow, Delta-Soft Ltd.,Russia

Alexander Korotkov a.korotkov@postgrespro.ru, Moscow, Postgres Professional, Russia

Documentation: Christopher Kings-Lynne

This module is sponsored by Delta-Soft Ltd., Moscow, Russia.

## sepgsql —
SELinux-, label-based mandatory access control (MAC) security module

`sepgsql` is a loadable module that supports label-based
mandatory access control (MAC) based on SELinux security
policy.

> **Warning:**

> The current implementation has significant limitations, and does not
> enforce mandatory access control for all actions.  See
> [sepgsql-limitations](#sepgsql-limitations).
>

### Overview

This module integrates with SELinux to provide an
additional layer of security checking above and beyond what is normally
provided by PostgreSQL.  From the perspective of
SELinux, this module allows
PostgreSQL to function as a user-space object
manager.  Each table or function access initiated by a DML query will be
checked against the system security policy.  This check is in addition to
the usual SQL permissions checking performed by
PostgreSQL.

SELinux access control decisions are made using
security labels, which are represented by strings such as
`system_u:object_r:sepgsql_table_t:s0`.  Each access control
decision involves two labels: the label of the subject attempting to
perform the action, and the label of the object on which the operation is
to be performed.  Since these labels can be applied to any sort of object,
access control decisions for objects stored within the database can be
(and, with this module, are) subjected to the same general criteria used
for objects of any other type, such as files.  This design is intended to
allow a centralized security policy to protect information assets
independent of the particulars of how those assets are stored.

The [`SECURITY LABEL`](#sql-security-label) statement allows assignment of
a security label to a database object.

### Installation

`sepgsql` can only be used on Linux
2.6.28 or higher with SELinux enabled.
It is not available on any other platform.  You will also need
libselinux 2.1.10 or higher and
selinux-policy 3.9.13 or higher (although some
distributions may backport the necessary rules into older policy
versions).

The `sestatus` command allows you to check the status of
SELinux.  A typical display is:

```
$ sestatus
SELinux status:                 enabled
SELinuxfs mount:                /selinux
Current mode:                   enforcing
Mode from config file:          enforcing
Policy version:                 24
Policy from config file:        targeted
```

If SELinux is disabled or not installed, you must set
that product up first before installing this module.

To build this module, include the option `--with-selinux` in
your PostgreSQL `configure` command.  Be sure that the
`libselinux-devel` RPM is installed at build time.

To use this module, you must include `sepgsql`
in the [guc-shared-preload-libraries](#guc-shared-preload-libraries) parameter in
`postgresql.conf`.  The module will not function correctly
if loaded in any other manner.  Once the module is loaded, you
should execute `sepgsql.sql` in each database.
This will install functions needed for security label management, and
assign initial security labels.

Here is an example showing how to initialize a fresh database cluster
with `sepgsql` functions and security labels installed.
Adjust the paths shown as appropriate for your installation:

```
$ export PGDATA=/path/to/data/directory
$ initdb
$ vi $PGDATA/postgresql.conf
change
#shared_preload_libraries = ''                # (change requires restart)
to
shared_preload_libraries = 'sepgsql'          # (change requires restart)
$ for DBNAME in template0 template1 postgres; do
postgres --single -F -c exit_on_error=true $DBNAME \
/dev/null
done
```

Please note that you may see some or all of the following notifications
depending on the particular versions you have of
libselinux and selinux-policy:

```
/etc/selinux/targeted/contexts/sepgsql_contexts:  line 33 has invalid object type db_blobs
/etc/selinux/targeted/contexts/sepgsql_contexts:  line 36 has invalid object type db_language
/etc/selinux/targeted/contexts/sepgsql_contexts:  line 37 has invalid object type db_language
/etc/selinux/targeted/contexts/sepgsql_contexts:  line 38 has invalid object type db_language
/etc/selinux/targeted/contexts/sepgsql_contexts:  line 39 has invalid object type db_language
/etc/selinux/targeted/contexts/sepgsql_contexts:  line 40 has invalid object type db_language
```

These messages are harmless and should be ignored.

If the installation process completes without error, you can now start the
server normally.

### Regression Tests

Due to the nature of SELinux, running the
regression tests for `sepgsql` requires several extra
configuration steps, some of which must be done as root.
The regression tests will not be run by an ordinary
`make check` or `make installcheck` command; you must
set up the configuration and then invoke the test script manually.
The tests must be run in the `contrib/sepgsql` directory
of a configured PostgreSQL build tree.  Although they require a build tree,
the tests are designed to be executed against an installed server,
that is they are comparable to `make installcheck` not
`make check`.

First, set up `sepgsql` in a working database
according to the instructions in [sepgsql-installation](#sepgsql-installation).
Note that the current operating system user must be able to connect to the
database as superuser without password authentication.

Second, build and install the policy package for the regression test.
The `sepgsql-regtest` policy is a special purpose policy package
which provides a set of rules to be allowed during the regression tests.
It should be built from the policy source file
`sepgsql-regtest.te`, which is done using
`make` with a Makefile supplied by SELinux.
You will need to locate the appropriate
Makefile on your system; the path shown below is only an example.
(This Makefile is usually supplied by the
`selinux-policy-devel` or
`selinux-policy` RPM.)
Once built, install this policy package using the
`semodule` command, which loads supplied policy packages
into the kernel.  If the package is correctly installed,
``semodule` -l` should list `sepgsql-regtest` as an
available policy package:

```
$ cd .../contrib/sepgsql
$ make -f /usr/share/selinux/devel/Makefile
$ sudo semodule -u sepgsql-regtest.pp
$ sudo semodule -l | grep sepgsql
sepgsql-regtest 1.07
```

Third, turn on `sepgsql_regression_test_mode`.
For security reasons, the rules in `sepgsql-regtest`
are not enabled by default;
the `sepgsql_regression_test_mode` parameter enables
the rules needed to launch the regression tests.
It can be turned on using the `setsebool` command:

```
$ sudo setsebool sepgsql_regression_test_mode on
$ getsebool sepgsql_regression_test_mode
sepgsql_regression_test_mode --> on
```

Fourth, verify your shell is operating in the `unconfined_t`
domain:

```
$ id -Z
unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
```

See [sepgsql-resources](#sepgsql-resources) for details on adjusting your
working domain, if necessary.

Finally, run the regression test script:

```
$ ./test_sepgsql
```

This script will attempt to verify that you have done all the configuration
steps correctly, and then it will run the regression tests for the
`sepgsql` module.

After completing the tests, it's recommended you disable
the `sepgsql_regression_test_mode` parameter:

```
$ sudo setsebool sepgsql_regression_test_mode off
```

You might prefer to remove the `sepgsql-regtest` policy
entirely:

```
$ sudo semodule -r sepgsql-regtest
```

### GUC Parameters

**`sepgsql.permissive` (`boolean`)**
: This parameter enables `sepgsql` to function
in permissive mode, regardless of the system setting.
The default is off.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

When this parameter is on, `sepgsql` functions
in permissive mode, even if SELinux in general is working in enforcing
mode.  This parameter is primarily useful for testing purposes.

**`sepgsql.debug_audit` (`boolean`)**
: This parameter enables the printing of audit messages regardless of
the system policy settings.
The default is off, which means that messages will be printed according
to the system settings.

The security policy of SELinux also has rules to
control whether or not particular accesses are logged.
By default, access violations are logged, but allowed
accesses are not.

This parameter forces all possible logging to be turned on, regardless
of the system policy.

### Features

#### Controlled Object Classes

The security model of SELinux describes all the access
control rules as relationships between a subject entity (typically,
a client of the database) and an object entity (such as a database
object), each of which is
identified by a security label.  If access to an unlabeled object is
attempted, the object is treated as if it were assigned the label
`unlabeled_t`.

Currently, `sepgsql` allows security labels to be
assigned to schemas, tables, columns, sequences, views, and functions.
When `sepgsql` is in use, security labels are
automatically assigned to supported database objects at creation time.
This label is called a default security label, and is decided according
to the system security policy, which takes as input the creator's label,
the label assigned to the new object's parent object and optionally name
of the constructed object.

A new database object basically inherits the security label of the parent
object, except when the security policy has special rules known as
type-transition rules, in which case a different label may be applied.
For schemas, the parent object is the current database; for tables,
sequences, views, and functions, it is the containing schema; for columns,
it is the containing table.

#### DML Permissions

For tables, `db_table:select`, `db_table:insert`,
`db_table:update` or `db_table:delete` are
checked for all the referenced target tables depending on the kind of
statement; in addition, `db_table:select` is also checked for
all the tables that contain columns referenced in the
`WHERE` or `RETURNING` clause, as a data source
for `UPDATE`, and so on.

Column-level permissions will also be checked for each referenced column.
`db_column:select` is checked on not only the columns being
read using `SELECT`, but those being referenced in other DML
statements; `db_column:update` or `db_column:insert`
will also be checked for columns being modified by `UPDATE` or
`INSERT`.

For example, consider:

```
UPDATE t1 SET x = 2, y = func1(y) WHERE z = 100;
```

Here, `db_column:update` will be checked for
`t1.x`, since it is being updated,
`db_column:{select update}` will be checked for
`t1.y`, since it is both updated and referenced, and
`db_column:select` will be checked for `t1.z`, since
it is only referenced.
`db_table:{select update}` will also be checked
at the table level.

For sequences, `db_sequence:get_value` is checked when we
reference a sequence object using `SELECT`; however, note that we
do not currently check permissions on execution of corresponding functions
such as `lastval()`.

For views, `db_view:expand` will be checked, then any other
required permissions will be checked on the objects being
expanded from the view, individually.

For functions, `db_procedure:{execute}` will be checked when
user tries to execute a function as a part of query, or using fast-path
invocation. If this function is a trusted procedure, it also checks
`db_procedure:{entrypoint}` permission to check whether it
can perform as entry point of trusted procedure.

In order to access any schema object, `db_schema:search`
permission is required on the containing schema.  When an object is
referenced without schema qualification, schemas on which this
permission is not present will not be searched (just as if the user did
not have `USAGE` privilege on the schema).  If an explicit schema
qualification is present, an error will occur if the user does not have
the requisite permission on the named schema.

The client must be allowed to access all referenced tables and
columns, even if they originated from views which were then expanded,
so that we apply consistent access control rules independent of the manner
in which the table contents are referenced.

The default database privilege system allows database superusers to
modify system catalogs using DML commands, and reference or modify
toast tables.  These operations are prohibited when
`sepgsql` is enabled.

#### DDL Permissions

SELinux defines several permissions to control common
operations for each object type; such as creation, alter, drop and
relabel of security label. In addition, several object types have
special permissions to control their characteristic operations; such as
addition or deletion of name entries within a particular schema.

Creating a new database object requires `create` permission.
SELinux will grant or deny this permission based on the
client's security label and the proposed security label for the new
object.  In some cases, additional privileges are required:

- [`CREATE DATABASE`](#sql-createdatabase) additionally requires
`getattr` permission for the source or template database.
- Creating a schema object additionally requires `add_name`
permission on the parent schema.
- Creating a table additionally requires permission to create each
individual table column, just as if each table column were a
separate top-level object.
- Creating a function marked as `LEAKPROOF` additionally
requires `install` permission.  (This permission is also
checked when `LEAKPROOF` is set for an existing function.)

When `DROP` command is executed, `drop` will be
checked on the object being removed.  Permissions will be also checked for
objects dropped indirectly via `CASCADE`.  Deletion of objects
contained within a particular schema (tables, views, sequences and
procedures) additionally requires `remove_name` on the schema.

When `ALTER` command is executed, `setattr` will be
checked on the object being modified for each object types, except for
subsidiary objects such as the indexes or triggers of a table, where
permissions are instead checked on the parent object.  In some cases,
additional permissions are required:

- Moving an object to a new schema additionally requires
`remove_name` permission on the old schema and
`add_name` permission on the new one.
- Setting the `LEAKPROOF` attribute on a function requires
`install` permission.
- Using [`SECURITY LABEL`](#sql-security-label) on an object additionally
requires `relabelfrom` permission for the object in
conjunction with its old security label and `relabelto`
permission for the object in conjunction with its new security label.
(In cases where multiple label providers are installed and the user
tries to set a security label, but it is not managed by
SELinux, only `setattr` should be checked here.
This is currently not done due to implementation restrictions.)

#### Trusted Procedures

Trusted procedures are similar to security definer functions or setuid
commands. SELinux provides a feature to allow trusted
code to run using a security label different from that of the client,
generally for the purpose of providing highly controlled access to
sensitive data (e.g., rows might be omitted, or the precision of stored
values might be reduced).  Whether or not a function acts as a trusted
procedure is controlled by its security label and the operating system
security policy.  For example:

```
postgres=# CREATE TABLE customer (
cid     int primary key,
cname   text,
credit  text
);
CREATE TABLE
postgres=# SECURITY LABEL ON COLUMN customer.credit
IS 'system_u:object_r:sepgsql_secret_table_t:s0';
SECURITY LABEL
postgres=# CREATE FUNCTION show_credit(int) RETURNS text
AS 'SELECT regexp_replace(credit, ''-[0-9]+$'', ''-xxxx'', ''g'')
FROM customer WHERE cid = $1'
LANGUAGE sql;
CREATE FUNCTION
postgres=# SECURITY LABEL ON FUNCTION show_credit(int)
IS 'system_u:object_r:sepgsql_trusted_proc_exec_t:s0';
SECURITY LABEL
```

The above operations should be performed by an administrative user.

```
postgres=# SELECT * FROM customer;
ERROR:  SELinux: security policy violation
postgres=# SELECT cid, cname, show_credit(cid) FROM customer;
cid | cname  |     show_credit
-----+--------+---------------------
1 | taro   | 1111-2222-3333-xxxx
2 | hanako | 5555-6666-7777-xxxx
(2 rows)
```

In this case, a regular user cannot reference `customer.credit`
directly, but a trusted procedure `show_credit` allows the user
to print the credit card numbers of customers with some of the digits
masked out.

#### Dynamic Domain Transitions

It is possible to use SELinux's dynamic domain transition feature
to switch the security label of the client process, the client domain,
to a new context, if that is allowed by the security policy.
The client domain needs the `setcurrent` permission and also
`dyntransition` from the old to the new domain.

Dynamic domain transitions should be considered carefully, because they
allow users to switch their label, and therefore their privileges,
at their option, rather than (as in the case of a trusted procedure)
as mandated by the system.
Thus, the `dyntransition` permission is only considered
safe when used to switch to a domain with a smaller set of privileges than
the original one. For example:

```
regression=# select sepgsql_getcon();
sepgsql_getcon
-------------------------------------------------------
unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
(1 row)

regression=# SELECT sepgsql_setcon('unconfined_u:unconfined_r:unconfined_t:s0-s0:c1.c4');
sepgsql_setcon
----------------
t
(1 row)

regression=# SELECT sepgsql_setcon('unconfined_u:unconfined_r:unconfined_t:s0-s0:c1.c1023');
ERROR:  SELinux: security policy violation
```

In this example above we were allowed to switch from the larger MCS
range `c1.c1023` to the smaller range `c1.c4`, but
switching back was denied.

A combination of dynamic domain transition and trusted procedure
enables an interesting use case that fits the typical process life-cycle
of connection pooling software.
Even if your connection pooling software is not allowed to run most
of SQL commands, you can allow it to switch the security label
of the client using the `sepgsql_setcon()` function
from within a trusted procedure; that should take some
credential to authorize the request to switch the client label.
After that, this session will have the privileges of the target user,
rather than the connection pooler.
The connection pooler can later revert the security label change by
again using `sepgsql_setcon()` with
`NULL` argument, again invoked from within a trusted
procedure with appropriate permissions checks.
The point here is that only the trusted procedure actually has permission
to change the effective security label, and only does so when given proper
credentials.  Of course, for secure operation, the credential store
(table, procedure definition, or whatever) must be protected from
unauthorized access.

#### Miscellaneous

We reject the [`LOAD`](#sql-load) command across the board, because
any module loaded could easily circumvent security policy enforcement.

### Sepgsql Functions

[sepgsql-functions-table](#sepgsql-functions-table) shows the available functions.

| Function                         Description |
| --- |
| `sepgsql_getcon` ()         text                         Returns the client domain, the current security label of the client. |
| `sepgsql_setcon` ( `text` )         boolean                         Switches the client domain of the current session to the new domain,         if allowed by the security policy.         It also accepts `NULL` input as a request to transition         to the client's original domain. |
| `sepgsql_mcstrans_in` ( `text` )         text                         Translates the given qualified MLS/MCS range into raw format if         the mcstrans daemon is running. |
| `sepgsql_mcstrans_out` ( `text` )         text                         Translates the given raw MLS/MCS range into qualified format if         the mcstrans daemon is running. |
| `sepgsql_restorecon` ( `text` )         boolean                         Sets up initial security labels for all objects within the         current database. The argument may be `NULL`, or the         name of a specfile to be used as alternative of the system default. |

### Limitations

**Data Definition Language (DDL) Permissions**
: Due to implementation restrictions, some DDL operations do not
check permissions.

**Data Control Language (DCL) Permissions**
: Due to implementation restrictions, DCL operations do not check
permissions.

**Row-level access control**
: PostgreSQL supports row-level access, but
`sepgsql` does not.

**Covert channels**
: `sepgsql` does not try to hide the existence of
a certain object, even if the user is not allowed to reference it.
For example, we can infer the existence of an invisible object as
a result of primary key conflicts, foreign key violations, and so on,
even if we cannot obtain the contents of the object.  The existence
of a top secret table cannot be hidden; we only hope to conceal its
contents.

### External Resources

**[SE-PostgreSQL Introduction](https://wiki.postgresql.org/wiki/SEPostgreSQL)**
: This wiki page provides a brief overview, security design, architecture,
administration and upcoming features.

**[SELinux User's and Administrator's Guide](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/selinux_users_and_administrators_guide/index)**
: This document provides a wide spectrum of knowledge to administer
SELinux on your systems.
It focuses primarily on Red Hat operating systems, but is not limited to them.

**[Fedora SELinux FAQ](https://fedoraproject.org/wiki/SELinux_FAQ)**
: This document answers frequently asked questions about
SELinux.
It focuses primarily on Fedora, but is not limited to Fedora.

### Author

KaiGai Kohei kaigai@ak.jp.nec.com

## spi — Server Programming Interface features/examples

The spi module provides several workable examples
of using the [Server Programming Interface](#spi)
(SPI) and triggers.  While these functions are of
some value in
their own right, they are even more useful as examples to modify for
your own purposes.  The functions are general enough to be used
with any table, but you have to specify table and field names (as described
below) while creating a trigger.

Each of the groups of functions described below is provided as a
separately-installable extension.

### refint — Functions for Implementing Referential Integrity

`check_primary_key()` and
`check_foreign_key()` are used to check foreign key constraints.
(This functionality is long since superseded by the built-in foreign
key mechanism, of course, but the module is still useful as an example.)

`check_primary_key()` checks the referencing table.
To use, create a `BEFORE INSERT OR UPDATE` trigger using this
function on a table referencing another table. Specify as the trigger
arguments: the referencing table's column name(s) which form the foreign
key, the referenced table name, and the column names in the referenced table
which form the primary/unique key.  To handle multiple foreign
keys, create a trigger for each reference.

`check_foreign_key()` checks the referenced table.
To use, create a `BEFORE DELETE OR UPDATE` trigger using this
function on a table referenced by other table(s).  Specify as the trigger
arguments: the number of referencing tables for which the function has to
perform checking, the action if a referencing key is found
(`cascade` — to delete the referencing row,
`restrict` — to abort transaction if referencing keys
exist, `setnull` — to set referencing key fields to null),
the triggered table's column names which form the primary/unique key, then
the referencing table name and column names (repeated for as many
referencing tables as were specified by first argument).  Note that the
primary/unique key columns should be marked NOT NULL and should have a
unique index.

There are examples in `refint.example`.

### autoinc — Functions for Autoincrementing Fields

`autoinc()` is a trigger that stores the next value of
a sequence into an integer field.  This has some overlap with the
built-in "serial column" feature, but it is not the same:
`autoinc()` will override attempts to substitute a
different field value during inserts, and optionally it can be
used to increment the field during updates, too.

To use, create a `BEFORE INSERT` (or optionally `BEFORE
INSERT OR UPDATE`) trigger using this function.  Specify two
trigger arguments: the name of the integer column to be modified,
and the name of the sequence object that will supply values.
(Actually, you can specify any number of pairs of such names, if
you'd like to update more than one autoincrementing column.)

There is an example in `autoinc.example`.

### insert_username — Functions for Tracking Who Changed a Table

`insert_username()` is a trigger that stores the current
user's name into a text field.  This can be useful for tracking
who last modified a particular row within a table.

To use, create a `BEFORE INSERT` and/or `UPDATE`
trigger using this function.  Specify a single trigger
argument: the name of the text column to be modified.

There is an example in `insert_username.example`.

### moddatetime — Functions for Tracking Last Modification Time

`moddatetime()` is a trigger that stores the current
time into a `timestamp` field.  This can be useful for tracking
the last modification time of a particular row within a table.

To use, create a `BEFORE UPDATE`
trigger using this function.  Specify a single trigger
argument: the name of the column to be modified.
The column must be of type `timestamp` or `timestamp with
time zone`.

There is an example in `moddatetime.example`.
