# all version release note sections

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/05_release_notes.md`
- Source Title: `05 release notes`
- Source Heading Path: `Release Notes > all version release note sections`
- Source Line Ranges: `1-5997`
- Chunk ID: `pg16_fact_0124_4f995c3b50`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `406c569aa80a7c7ee33f39a0878d52274325e2feabcbb0c8ca6c75959860c428`

## Retrieval Guidance

- Use When: Look up when a PostgreSQL behavior, feature, or fix appeared.
- Retrieval Keywords: release notes, PostgreSQL 16, major release, minor release, bug fix, incompatibility, migration
- Follow-up Guidance: Use the migration record when the question is about upgrade action or compatibility risk.
- Classification Note: The appendix records version changes, bug fixes, incompatibilities, and feature additions as historical reference.

## Official Source Content

## Release Notes

The release notes contain the significant changes in each
PostgreSQL release, with major features and migration
issues listed at the top.  The release notes do not contain changes
that affect only a few users or changes that are internal and therefore not
user-visible.  For example, the optimizer is improved in almost every
release, but the improvements are usually observed by users as simply
faster queries.

A complete list of changes for each release can be obtained by
viewing the [Git](#git) logs for each release.
The [`pgsql-committers`
email list](https://www.postgresql.org/list/pgsql-committers/) records all source code changes as well.  There is also
a [web
interface](https://git.postgresql.org/gitweb/?p=postgresql.git;a=summary) that shows changes to specific files.

The name appearing next to each item represents the major developer for
that item.  Of course all changes involve community discussion and patch
review, so each item is truly a community effort.

Section markers () in the release notes link to [gitweb](https://git.postgresql.org/gitweb/?p=postgresql.git)
pages which show the primary git commit
messages and source tree changes responsible for the release note item.
There might be additional git commits which
are not shown.

## Release 16.14

## Release date:

2026-05-14

This release contains a variety of fixes from 16.13.
For information about new features in major release 16, see
[release-16](#release-16).

### Migration to Version 16.14

A dump/restore is not required for those running 16.X.

However, if you are upgrading from a version earlier than 16.10,
see [release-16-10](#release-16-10).

### Changes

- Prevent unbounded recursion while processing startup packets
(Michael Paquier)
[](66cf26b9e)
[](c2e6ef863)

A malicious client could crash the connected backend by alternating
rejected SSL and GSS encryption requests indefinitely.

The PostgreSQL Project thanks Calif.io
(in collaboration with Claude and Anthropic Research) for reporting
this problem.
(CVE-2026-6479)
- Fix assorted integer overflows in memory-allocation calculations
(Tom Lane, Nathan Bossart, Heikki Linnakangas)
[](cfb610eaa)
[](aff71f87b)
[](a4f089c79)
[](c25973124)
[](32c525eb6)
[](e24fb3247)
[](f20b84081)
[](924b3e943)
[](47dae5e74)
[](e42598a41)

Various places were incautious about the possibility of integer
overflow in calculations of how much memory to allocate.  Overflow
would lead to allocating a too-small buffer which the caller would
then write past the end of.  This would at least trigger server
crashes, and probably could be exploited for arbitrary code
execution.  In many but by no means all cases, the hazard exists
only in 32-bit builds.

The PostgreSQL Project thanks Xint Code,
Bruce Dang, Sven Klemm, and Pavel Kohout for reporting these problems.
(CVE-2026-6473)
- Properly quote object names in logical replication origin checks
(Pavel Kohout)
[](248a433cd)

`ALTER SUBSCRIPTION ... REFRESH PUBLICATION`
interpolated schema and relation names into SQL commands without
quoting them, allowing execution of arbitrary SQL on the publisher.

The PostgreSQL Project thanks
Pavel Kohout for reporting this problem.
(CVE-2026-6638)
- Reject over-length options in `ts_headline()`
(Michael Paquier)
[](5919e0005)

The `StartSel`, `StopSel`
and `FragmentDelimiter` strings must not exceed
32Kb in length, but this was not checked for.  An over-length value
would typically crash the server.

The PostgreSQL Project thanks
Xint Code for reporting this problem.
(CVE-2026-6473)
- Guard against malicious time zone names
in `timeofday()`
and `pg_strftime()` (Tom Lane)
[](24e0e3254)
[](79b7847c7)

A crafted time zone setting could pass `%`
sequences to `snprintf()`, potentially causing
crashes or disclosure of server memory.  Another path to similar
results was to overflow the limited-size output buffer used
by `pg_strftime()`.

The PostgreSQL Project thanks
Xint Code for reporting this problem.
(CVE-2026-6474)
- When creating a multirange type, ensure the user
has `CREATE` privilege on the schema specified for
the multirange type (Jelte Fennema-Nio)
[](d92852d62)

The multirange type can be put into a different schema than its
parent range type, but we neglected to apply the required privilege
check when doing so.

The PostgreSQL Project thanks
Jelte Fennema-Nio for reporting this problem.
(CVE-2026-6472)
- Use timing-safe string comparisons in authentication code
(Michael Paquier)
[](00e27235e)
[](1604939b2)

Use `timingsafe_bcmp()` instead
of `memcmp()` or `strcmp()`
when checking passwords, hashes, etc.  It is not known whether the
data dependency of those functions is usefully exploitable in any of
these places, but in the interests of safety, replace them.

The PostgreSQL Project thanks
Joe Conway for reporting this problem.
(CVE-2026-6478)
- Mark `PQfn()` as unsafe, and avoid using it
within libpq (Nathan Bossart)
[](614474996)

For a non-integral result type, `PQfn()` is not
passed the size of the output buffer, so it cannot check that the
data returned by the server will fit.  A malicious server could
therefore overwrite client memory.  This is unfixable without an
API change, so mark the function as deprecated.  Internally
to libpq, use a variant version that can
apply the missing check.

The PostgreSQL Project thanks
Yu Kunpeng and Martin Heistermann for reporting this problem.
(CVE-2026-6477)
- Prevent path traversal in pg_basebackup
and pg_rewind (Michael Paquier)
[](6778af13e)

These applications failed to validate output file paths read from
their input, so that a malicious source could overwrite any file
writable by these applications.  Constrain where data can be written
by rejecting paths that are absolute or contain parent-directory
references.

The PostgreSQL Project thanks XlabAI Team
of Tencent Xuanwu Lab and Valery Gubanov for reporting this problem.
(CVE-2026-6475)
- Guard against field overflow
within `contrib/intarray`'s `query_int`
type and `contrib/ltree`'s `ltxtquery`
type (Tom Lane)
[](5c1069c35)
[](6f0bff33d)

Parsing of these query structures did not check for overflow of
16-bit fields, so that construction of an invalid query tree was
possible.  This can crash the server when executing the query.

The PostgreSQL Project thanks
Xint Code for reporting this problem.
(CVE-2026-6473)
- Guard against overly long values
of `contrib/ltree`'s `lquery` type
(Michael Paquier)
[](6b6b26fde)

Values with more than 64K items caused internal overflows,
potentially resulting in stack smashes or wrong answers.

The PostgreSQL Project thanks
Vergissmeinnicht, A1ex, and Jihe Wang
for reporting this problem.
(CVE-2026-6473)
- Prevent SQL injection and buffer overruns
in `contrib/spi` (Nathan Bossart)
[](710995782)

`check_foreign_key()` was insufficiently careful
about quoting key values, and also used fixed-length buffers for
constructing queries.  While this module is only meant as example
code, it still shouldn't contain such dangerous errors.

The PostgreSQL Project thanks
Nikolay Samokhvalov for reporting this problem.
(CVE-2026-6637)
- Check for nondeterministic collations before assuming that an
equality condition on a collatable type implies uniqueness
(Richard Guo)
[](748fe9e60)
[](5a24cef08)

Numerous planner optimizations assume that, for example, at most one
table row can satisfy `WHERE x = 'abc'` if there is
a unique index on `x`.  However this conclusion is
unsafe in general if the index and the `WHERE`
clause have different collations attached.  It is safe when both
collations are deterministic, because that property essentially
requires that equality of two strings means bitwise equality.  But
nondeterministic collations don't act that way, so that optimizing
on the assumption of unique matches can give wrong query answers if
either the `WHERE` clause or the index has a
nondeterministic collation.
- Fix incomplete removal of relation references
in `RestrictInfo` structs during join removal
(Tom Lane)
[](d509be4ac)
[](798dabe83)

This oversight has been shown to result in planner failures such as
unexpected "FULL JOIN is only supported with merge-joinable or
hash-joinable join conditions" errors.  It may also have
caused failure to consider valid plans in other cases.
- Fix incorrect handling of `NEW` generated columns
in rule actions and rule qualifications (Richard Guo, Dean Rasheed)
[](07b257189)

Previously, such column references would produce NULL
in `INSERT` cases, or be equivalent to
the `OLD` value in `UPDATE` cases.
- Fix spurious "generated columns are not supported in COPY FROM
WHERE conditions" errors (Tom Lane)
[](3c7a6bbe6)

Use of a system column in a `COPY FROM WHERE`
condition could sometimes incorrectly report this error.
- Correctly report a serialization failure
when `MERGE` encounters a concurrently-updated
tuple in repeatable-read or serializable mode (Tender Wang)
[](f6e63d4b8)

Previously, such cases behaved the same as in lower isolation
levels.
- Fix `CREATE TABLE ... LIKE ... INCLUDING
STATISTICS` for cases where the source table has dropped
column(s) (Julien Tachoires)
[](7bb519635)

In such cases, extended statistics objects could be copied
incorrectly, or the command could give an incorrect error.
- Allow `ALTER INDEX ... ATTACH PARTITION` to mark
the parent index valid if appropriate (Sami Imseih)
[](313355d68)

There are edge cases in which a partitioned index might remain
marked as invalid even when all its leaf indexes are valid.  This
change provides a mechanism whereby a user can correct such a
situation without resorting to manual catalog updates.
- Fix `ALTER FOREIGN DATA WRAPPER` to not drop the
wrapper object's dependency on its handler function (Jeff Davis)
[](a19edb66a)
- Disallow making a composite type be a member of itself via a
multirange (Heikki Linnakangas)
[](06e304524)

We already forbade such cases when the intermediate type is a
domain, array, composite type, or range; but multiranges were
overlooked.
- Fix datum-image comparisons to be insensitive to sign-extension
variations (David Rowley)
[](1bd90c887)

This fixes some situations that previously led to "could not
find memoization table entry" errors or wrong query results.
- Fix incorrect logic for hashed `IN`/`NOT
IN` with non-strict equality operator (Chengpeng Yan)
[](a2a0060d5)

The previous coding could crash or give wrong answers.  All built-in
data types have strict equality operators, so that this issue could
only arise with an extension data type.
- Truncate overly-long locale-specific numeric symbols
in `to_char()` (Tom Lane)
[](e1e60f148)

If a locale specified a currency symbol, thousands separator, or
decimal or sign symbol more than 8 bytes long, a buffer overrun was
possible.  No such locales exist in the real world, and it's
impractical for an unprivileged attacker to install a malicious
locale definition underneath a Postgres server; but for safety's
sake check for overlength symbols and truncate if needed.
- Prevent buffer overruns when parsing an affix file for
an `Ispell` dictionary (Tom Lane)
[](42383d32d)
[](17f72e037)

A corrupt or malicious affix file could crash the server.
This is not considered a security issue because text search
configuration files are presumed trustworthy, but it still seems
worth fixing.
- Guard against integer overflow in calculations of frame start and
end positions for window aggregates (Richard Guo)
[](0fe032e6a)

Very large user-specified offsets (close to INT64_MAX) could result
in errors or incorrect query results.
- Fix `array_agg_array_combine()` to combine the
arrays' null bitmaps correctly (Dmytro Astapov)
[](bb959269e)

This mistake resulted in sometimes-incorrect output from
parallelized `array_agg(anyarray)` calculations.
- Retry `sync_file_range()` if it returns error
code `EINTR` (DaeMyung Kang)
[](3b35c10a4)
- Fix incorrect behavior
of `pg_stat_reset_single_table_counters()` on a
shared catalog (Chao Li)
[](c7cdcbd3e)

Such cases had a side-effect of resetting the
current database's `stat_reset_timestamp`, which
was unintended.
- Update activity statistics when a parallel apply worker is idle
(Zhijie Hou)
[](d052f6c7d)

Previously, statistics from a recently-completed transaction might
go unreported for long intervals, particularly if the workload is
light.
- Fix buffer overread when `pglz_decompress()`
receives corrupt input (Andrew Dunstan)
[](e630f65d0)

It was possible to read a few bytes past the end of the input, which
in very unlucky cases might cause a crash.
- Ensure that tuplestore data structures are internally consistent
even after an error (Tom Lane)
[](59c139d53)

The code was previously careless about this, which is fine most of
the time but is problematic for the tuplestore backing
a `WITH HOLD` cursor.  In v15 and before this
leads to easily-reproducible crashes; later branches are not known
to be vulnerable, but it seems best to preserve consistency in all.
- Fix premature NULL lag reporting
in `pg_stat_replication` (Shinya Kato)
[](f42105001)

The lag columns frequently read as NULL even while replication
activity was happening.
- Avoid rare flush failure when working with non-WAL-logged GiST
indexes (Tomas Vondra)
[](4f4025eac)

A non-logged GiST index could nonetheless sometimes
produce "xlog flush request `n/nnnn`
is not satisfied" errors, due to incorrect selection of
a "fake LSN" to represent an insertion point.
- Fix underestimate of required size of DSA page maps for odd-size
segments (Paul Bunn)
[](0af5e64e9)

This miscalculation led to out-of-bounds accesses and hence server
crashes.
- Fix possible server crash when processing extended statistics on
expressions of extension data types (Michael Paquier)
[](04745ba9c)

NULL pointer dereferences were possible if the data type's
typanalyze function does not compute any useful statistics.
No in-core typanalyze function behaves that way, but extensions
could.
- Fix minor memory leaks in ICU-based string processing (Jeff Davis)
[](a4515c9b4)
- If the startup process fails, properly shut down other child
processes before exiting the postmaster (Ayush Tiwari)
[](2d347f2cd)

The handling of this situation relied on a long-obsolete assumption
that no other postmaster children exist while the startup process is
running, so that immediate postmaster exit is acceptable.
Orphaned children would eventually notice the postmaster's death and
exit on their own, but a cleaner shutdown procedure is desirable.
- Fix race condition between WAL replay of checkpoints and multixact
ID creations (Heikki Linnakangas)
[](77dff5d93)

A standby server following WAL from a primary of an older minor
version could get into a crash-and-restart loop complaining
about "could not access status of transaction".
- Prevent indefinite wait in shutdown of a walsender process
(Anthonin Bonnefoy)
[](82935467a)
[](da21ecf57)

At shutdown of a cluster that is publishing logical replication
data, the walsender waits for all pending WAL to be written out.
But it did not correctly request that to happen, so that in some
cases this could become an indefinite wait.
- Ensure that changes to tables' free space maps are persisted during
recovery (Alexey Makhmutov)
[](54537de35)

Previously, while WAL replay did update the free space map while
replaying operations that should change it, the map page buffer did
not get marked dirty if checksums are enabled, so that the changes
might never get written out.  On a standby server, over time this
would result in a map wildly at variance with the table's actual
contents.  While the map is only used as a hint, this condition
could cause significant performance degradation for some period of
time after the standby server is promoted to be active, until most
of the map has been repaired by updates.
- Fix crashes in some ecpg functions when
called without any established connection (Shruthi Gowda)
[](7e4c871f4)
- Fix assorted bugs in backup decompression and tar-parsing code
(Andrew Dunstan, Tom Lane, Chao Li)
[](1590723f0)
[](cce939c71)
[](415cc943f)

The decompression and tar-file reading code used
in pg_basebackup
and pg_verifybackup mishandled tar-file
padding data, could corrupt LZ4-compressed data in edge cases,
failed to check for some unusual error conditions, failed to exit
after compression/decompression errors (leading to cascading error
reports), and leaked memory.
- In pg_dumpall, don't skip
role `GRANT`s with dangling grantor OIDs
(Tom Lane)
[](a4649c50a)

Instead, handle such cases by emitting `GRANT`
without any `GRANTED BY` clause, as we did before
v16.  This avoids losing the grant in foreseeable cases, since
pre-v16 servers didn't prevent dropping the grantor role.  Continue
to emit a warning about the missing grantor, but only if the source
server is v16 or later.
- In pg_upgrade, take care to use the
correct protocol version when connecting to older source servers
(Jacob Champion)
[](a38ed212f)

This could be problematic when attempting to upgrade from a pre-2018
server.
- In `contrib/basic_archive`, allow the archive
directory to be missing at startup (Nathan Bossart)
[](28c2b7896)

Previously, the setting
of `basic_archive.archive_directory` was rejected
if it didn't point to an existing directory.  This is undesirable
because archiving will be stuck indefinitely, even if the directory
appears later.
- Fix `contrib/ltree` to cope when case-folding
changes a string's byte length (Jeff Davis)
[](3ed2c7ef7)

Previously, `lquery` patterns specifying case-insensitive
matching might fail to match labels they should match.
- In `contrib/pg_stat_statements`, don't leak
memory if an error occurs while parsing the
`pgss_query_texts.stat` file (Heikki Linnakangas)
[](52edaf9d9)
- In `contrib/postgres_fdw`, avoid crash due to
premature cleanup of a failed connection (Etsuro Fujita)
[](1352651c2)

If a remote connection fails abort cleanup, we can't use it any
longer.  But delay closing the connection object until end of
transaction, because there might still be references to it within
data structures such as open cursors.
- Update time zone data files to tzdata
release 2026b (Tom Lane)
[](0465c999e)

British Columbia (America/Vancouver) will be on year-round UTC-07
(effectively, permanent DST) beginning in November 2026.  This
release assumes that their TZ abbreviation will
be `MST` from that time forward.  That seems likely
to change, but it's unclear what new abbreviation will be used.
Also a historical correction for Moldova: they have followed EU DST
transition times since 2022.

## Release 16.13

## Release date:

2026-02-26

This release contains a small number of fixes from 16.12.
For information about new features in major release 16, see
[release-16](#release-16).

### Migration to Version 16.13

A dump/restore is not required for those running 16.X.

However, if you are upgrading from a version earlier than 16.10,
see [release-16-10](#release-16-10).

### Changes

- Fix failure after replaying a multixid truncation record from WAL
that was generated by an older minor version (Heikki Linnakangas)
[](23064542f)

Erroneous logic for coping with the way that previous versions
handled multixid wraparound led to replay failure, with messages
like "could not access status of transaction".
A typical scenario in which this could occur is a standby server of
the latest minor version consuming WAL from a primary server of an
older version.
- Avoid incorrect complaint of invalid encoding
when `substring()` is applied
to "toasted" data (Noah Misch)
[](bdfb37228)
[](2280ab354)
[](45eb47230)

The fix for CVE-2026-2006 was too aggressive and could raise an
error about an incomplete character in cases that are actually
valid.
- Fix computation of the set of potentially-nulling outer joins for
the output of a `LATERAL UNION ALL` subquery
(Richard Guo)
[](ec20a4552)

This error could lead to skipping `NOT NULL` tests
in the mistaken belief that they were unnecessary, resulting in
wrong query output.
- Fix `pg_stat_get_backend_wait_event()`
and `pg_stat_get_backend_wait_event_type()`
to report values for auxiliary processes (Heikki Linnakangas)
[](2332911ae)

Previously these functions returned NULL for auxiliary processes,
but that's inconsistent with
the `pg_stat_activity` view.
- Fix casting a composite-type variable to a domain type when
returning its value from a PL/pgSQL function (Tom Lane)
[](c66f4cff1)

If the variable's value is NULL, a "cache lookup failed for
type 0" error resulted.
- Fix potential null pointer dereference
in `contrib/hstore`'s binary input function
(Michael Paquier)
[](31d0b917d)

`hstore`'s receive function crashed on input containing
duplicate keys.  `hstore` values generated by Postgres
would never contain duplicate keys, so this mistake has gone
unnoticed.  The crash could be provoked by malicious or corrupted
data.

## Release 16.12

## Release date:

2026-02-12

This release contains a variety of fixes from 16.11.
For information about new features in major release 16, see
[release-16](#release-16).

### Migration to Version 16.12

A dump/restore is not required for those running 16.X.

However, if you are upgrading from a version earlier than 16.10,
see [release-16-10](#release-16-10).

### Changes

- Guard against unexpected dimensions
of `oidvector`/`int2vector` (Tom Lane)
[](595956fc7)

These data types are expected to be 1-dimensional arrays containing
no nulls, but there are cast pathways that permit violating those
expectations.  Add checks to some functions that were depending on
those expectations without verifying them, and could misbehave in
consequence.

The PostgreSQL Project thanks
Altan Birler for reporting this problem.
(CVE-2026-2003)
- Harden selectivity estimators against being attached to operators
that accept unexpected data types (Tom Lane)
[](91d7c0bfd)
[](c0887b39d)
[](d484bc260)

`contrib/intarray` contained a selectivity
estimation function that could be abused for arbitrary code
execution, because it did not check that its input was of the
expected data type.  Third-party extensions should check for similar
hazards and add defenses using the technique intarray now uses.
Since such extension fixes will take time, we now require superuser
privilege to attach a non-built-in selectivity estimator to an
operator.

The PostgreSQL Project thanks
Daniel Firer, as part of zeroday.cloud, for reporting this problem.
(CVE-2026-2004)
- Fix buffer overrun in `contrib/pgcrypto`'s
PGP decryption functions (Michael Paquier)
[](527b730f4)

Decrypting a crafted message with an overlength session key caused a
buffer overrun, with consequences as bad as arbitrary code
execution.

The PostgreSQL Project thanks
Team Xint Code, as part of zeroday.cloud, for reporting this problem.
(CVE-2026-2005)
- Fix inadequate validation of multibyte character lengths
(Thomas Munro, Noah Misch)
[](70ff9ede5)
[](b0e3f5cf9)
[](d837fb029)
[](4c08960d9)
[](0c33d5608)
[](763671b74)

Assorted bugs allowed an attacker able to issue crafted SQL to
overrun string buffers, with consequences as bad as arbitrary code
execution.  After these fixes, applications may
observe "invalid byte sequence for encoding" errors
when string functions process invalid text that has been stored in
the database.

The PostgreSQL Project thanks Paul Gerste
and Moritz Sanft, as part of zeroday.cloud, for reporting this
problem.
(CVE-2026-2006)
- Don't allow CTE references in sub-selects to determine semantic
levels of aggregate functions (Tom Lane)
[](1c8c3206f)

This change undoes a change made two minor releases ago, instead
throwing an error if a sub-select references a CTE that's below the
semantic level that standard SQL rules would assign to the aggregate
based on contained column references and aggregates.  The attempted
fix turned out to cause problems of its own, and it's unclear what
to do instead.  Since sub-selects within aggregates are disallowed
altogether by the SQL standard, treating such cases as errors seems
sufficient.
- Fix trigger transition table capture for `MERGE`
in CTE queries (Dean Rasheed)
[](e7391bbf1)

When executing a data-modifying CTE query containing both
a `MERGE` and another DML operation on a table with
statement-level `AFTER` triggers, the transition
tables passed to the triggers would not include the rows affected by
the `MERGE`, only those affected by the other
operation(s).
- Fix failure when all children of a partitioned target table
of an update or delete have been pruned (Amit Langote)
[](fab386f74)

In such cases, the executor could report "could not find junk
ctid column" errors, even though nothing needs to be done.
- Avoid possible planner failure when a query contains duplicate
window function calls (Meng Zhang, David Rowley)
[](4297a3519)

Confusion over de-duplication of such calls could result in errors
like "WindowFunc with winref 2 assigned to WindowAgg with
winref 1".
- Allow indexscans on partial hash indexes even when the index's
predicate implies the truth of the WHERE clause (Tom Lane)
[](b497766a8)

Normally we drop a WHERE clause that is implied by the predicate,
since it's pointless to test it; it must hold for every index
entry.  However that can prevent creation of an indexscan plan if
the index is one that requires a WHERE clause on the leading index
key, as hash indexes do.  Don't drop implied clauses when
considering such an index.
- Do not emit WAL for unlogged BRIN indexes (Kirill Reshke)
[](a5277700e)

One seldom-taken code path incorrectly emitted a WAL record
relating to a BRIN index even if the index was marked unlogged.
Crash recovery would then fail to replay that record, complaining
that the file already exists.
- Prevent truncation of CLOG that is still needed by
unread `NOTIFY` messages (Joel Jacobson, Heikki
Linnakangas)
[](053e1868b)
[](44e8c60be)
[](0e8eaa218)

This fix prevents "could not access status of
transaction" errors when a backend is slow to
absorb `NOTIFY` messages.
- Escalate errors occurring during `NOTIFY` message
processing to FATAL, i.e. close the connection (Heikki Linnakangas)
[](c1a5bde00)

Formerly, if a backend got an error while absorbing
a `NOTIFY` message, it would advance past that
message, report the error to the client, and move on.  That behavior
was fraught with problems though.  One big concern is that the
client has no good way to know that a notification was lost, and
certainly no way to know what was in it.  Depending on the
application logic, missing a notification could cause the
application to get stuck waiting, for example.  Also, any remaining
messages would not get processed until someone sent a
new `NOTIFY`.

Also, if the connection is idle at the time of receiving
a `NOTIFY` signal, any ERROR would be escalated to
FATAL anyway, due to unrelated concerns.  Therefore, we've chosen to
make that happen in all cases, for consistency and to provide a
clear signal to the application that it might have missed some
notifications.
- Fix bug in following update chain when locking a tuple (Jasper
Smit)
[](7efef18ff)

This code path neglected to check the xmin of the first new tuple in
the update chain, making it possible to lock an unrelated tuple if
the original updater aborted and the space was immediately reclaimed
by `VACUUM` and then re-used.
That could cause unexpected transaction delays or deadlocks.
Errors associated with having identified the wrong tuple have also
been observed.
- Fix issues around in-place catalog updates (Noah Misch)
[](1d7b02711)
[](720e9304f)
[](27e4fad98)

Send a nontransactional invalidation message for an in-place update,
since such an update will survive transaction rollback.  Also ensure
that the update is WAL-logged before other sessions can see it.
These fixes primarily prevent scenarios in which relations'
frozen-XID attributes become inconsistent, possibly allowing
premature CLOG truncation and subsequent "could not access
status of transaction" errors.
- Fix potential backend process crash at process exit due to trying to
release a lock in an already-unmapped shared memory segment
(Rahila Syed)
[](980b7c736)
- Guard against incorrect truncation of the multixact log after a
crash (Heikki Linnakangas)
[](c7946e6f3)
- Fix possibly mis-encoded result
of `pg_stat_get_backend_activity()` (Chao Li)
[](c48829ed8)

The shared-memory buffer holding a session's activity string can
end with an incomplete multibyte character.  Readers are supposed
to truncate off any such incomplete character, but this function
failed to do so.
- Guard against recursive memory context logging (Fujii Masao)
[](3853f6168)

A constant flow of signals requesting memory context logging could
cause recursive execution of the logging code, which in theory could
lead to stack overflow.
- Fix memory context usage when reinitializing a parallel execution
context (Jakub Wartak, Jeevan Chalke)
[](12c2f843c)

This error could result in a crash due to a subsidiary data
structure having a shorter lifespan than the parallel context.
The problem is not known to be reachable using only
core PostgreSQL, but we have reports of
trouble in extensions.
- Set next multixid's offset when creating a new multixid, to remove
the wait loop that was needed in corner cases (Andrey Borodin)
[](635166913)
[](4d689a176)

The previous logic could get stuck waiting for an update that would
never occur.
- Avoid rewriting data-modifying CTEs more than once (Bernice Southey,
Dean Rasheed)
[](4d288e33b)

Formerly, when updating an auto-updatable view or a relation with
rules, if the original query had any data-modifying CTEs, the rewriter
would rewrite those CTEs multiple times due to recursion.  This was
inefficient and could produce false errors if a CTE included an
update of an always-generated column.
- Fail recovery if WAL does not exist back to the redo point indicated
by the checkpoint record (Nitin Jadhav)
[](1aa57e9ed)

Add an explicit check for this before starting recovery, so that no
harm is done and a useful error message is provided.  Previously,
recovery might crash or corrupt the database in this situation.
- Avoid scribbling on the source query tree during `ALTER
PUBLICATION` (Sunil S)
[](0687a6eb0)

This error had the visible effect that an event trigger fired for
the query would see only the first `publish`
option, even if several had been specified.  If such a query were
set up as a prepared statement, re-executions would misbehave too.
- Pass connection options specified in `CREATE SUBSCRIPTION
... CONNECTION` to the publisher's walsender (Fujii Masao)
[](75f3428f2)

Before this fix, the `options` connection option
(if any) was ignored, thus for example preventing setting custom
server parameter values in the walsender session.  It was intended
for that to work, and it did work before refactoring
in PostgreSQL version 15 broke it, so
restore the previous behavior.
- Prevent invalidation of newly created or newly synced replication
slots (Zhijie Hou)
[](24cce33c3)

A race condition with a concurrent checkpoint could allow WAL to be
removed that is needed by the replication slot, causing the slot to
immediately get marked invalid.
- Fix race condition in computing a replication slot's required xmin
(Zhijie Hou)
[](821466722)

This could lead to the error "cannot build an initial slot
snapshot as oldest safe xid follows snapshot's xmin".
- During initial synchronization of a logical replication
subscription, commit the addition of
a `pg_replication_origin` entry before
starting to copy data (Zhijie Hou)
[](e22e9ab0c)

Previously, if the copy step failed, the
new `pg_replication_origin` entry would be
lost due to transaction rollback.  This led to inconsistent state in
shared memory.
- Don't advance logical replication progress after a parallel worker
apply failure (Zhijie Hou)
[](63a65adf4)

The previous behavior allowed transactions to be lost by a
subscriber.
- Fix possible failure with "unexpected data beyond EOF"
during restart of a streaming replica server (Anthonin Bonnefoy)
[](a2eeb04f3)
- Fix erroneous tracking of column position when parsing partition
range bounds (myzhen)
[](821c4d27b)

This could, for example, lead to the wrong column name being cited
in error messages about casting partition bound values to the
column's data type.
- Fix assorted minor errors in error messages (Man Zeng, Tianchen Zhang)
[](977a17a3e)
[](e8fd6c9fd)
[](a7bdbbada)

For example, an error report about mismatched timeline number in a
backup manifest showed the starting timeline number where it meant
to show the ending timeline number.
- Fix failure to perform function inlining when doing JIT compilation
with LLVM version 17 or later (Anthonin Bonnefoy)
[](7600dc79c)
- Adjust our JIT code to work with LLVM 21 (Holger Hoffstätte)
[](600acd34b)

The previous coding failed to compile on aarch64 machines.
- Add new server parameter [guc-file-extend-method](#guc-file-extend-method) to
control use of `posix_fallocate()` (Thomas Munro)
[](e37b59802)

PostgreSQL version 16 and later will
use `posix_fallocate()`, if the platform provides
it, to extend relation files.  However, this has been reported to
interact poorly with some file systems: BTRFS compression is
disabled by the use of `posix_fallocate()`, and
XFS could produce spurious `ENOSPC` errors in older
Linux kernel versions.  To provide a workaround, introduce this new
server parameter.  Setting `file_extend_method`
to `write_zeros` will cause the server to return to
the old method of extending files by writing blocks of zeroes.
- Honor `open()`'s `O_CLOEXEC`
flag on Windows (Bryan Green, Thomas Munro)
[](d62a258cd)
[](0666ccc16)
[](80e8ec772)

Make this flag work like it does on POSIX platforms, so that we
don't leak file handles into child processes such as `COPY
TO/FROM PROGRAM`.  While that leakage hasn't caused many
problems, it seems undesirable.
- Fix failure to parse long options on the server command line in
Solaris executables built with meson (Tom Lane)
[](7369656fa)
- Support process title changes on GNU/Hurd (Michael Banck)
[](a1407dade)
- Make pg_resetwal print the updated value
when changing OldestXID (Heikki Linnakangas)
[](890cc81b6)

It already did that for every other variable it can change.
- Make pg_resetwal allow setting next
multixact xid to 0 or next multixact offset to UINT32_MAX (Maxim
Orlov)
[](e039b09f8)

These are valid values, so rejecting them was incorrect.  In the
worst case, if a pg_upgrade is attempted when exactly at the point
of multixact wraparound, the upgrade would fail.
- In `contrib/amcheck`, use the correct snapshot
for btree index parent checks (Mihail Nikalayeu)
[](098a1fab8)

The previous coding caused spurious errors when examining indexes
created with `CREATE INDEX CONCURRENTLY`.
- Fix `contrib/amcheck` to
handle "half-dead" btree index pages correctly
(Heikki Linnakangas)
[](182901626)

`amcheck` expected such a page to have a parent
downlink, but it does not, leading to a false error report
about "mismatch between parent key and child high key".
- Fix `contrib/amcheck` to
handle incomplete btree root page splits correctly
(Heikki Linnakangas)
[](f2a6df9fd)

`amcheck` could report a false error
about "block is not true root".
- Fix edge-case integer overflow
in `contrib/intarray`'s selectivity estimator
for `@@` (Chao Li)
[](54f82c4aa)

This could cause poor selectivity estimates to be produced for cases
involving the maximum integer value.
- Fix multibyte-encoding issue in `contrib/ltree`
(Jeff Davis)
[](b80227c0a)

The previous coding could pass an incomplete multibyte character
to `lower()`, probably resulting in incorrect
behavior.
- Update time zone data files to tzdata
release 2025c (Tom Lane)
[](d852d105e)

The only change is in historical data for pre-1976 timestamps in
Baja California.

## Release 16.11

## Release date:

2025-11-13

This release contains a variety of fixes from 16.10.
For information about new features in major release 16, see
[release-16](#release-16).

### Migration to Version 16.11

A dump/restore is not required for those running 16.X.

However, if you are upgrading from a version earlier than 16.10,
see [release-16-10](#release-16-10).

### Changes

- Check for `CREATE` privileges on the schema
in `CREATE STATISTICS` (Jelte Fennema-Nio)
[](d20abb587)

This omission allowed table owners to create statistics in any
schema, potentially leading to unexpected naming conflicts.

The PostgreSQL Project thanks
Jelte Fennema-Nio for reporting this problem.
(CVE-2025-12817)
- Avoid integer overflow in allocation-size calculations
within libpq (Jacob Champion)
[](585fd9b3c)

Several places in libpq were not
sufficiently careful about computing the required size of a memory
allocation.  Sufficiently large inputs could cause integer overflow,
resulting in an undersized buffer, which would then lead to writing
past the end of the buffer.

The PostgreSQL Project thanks Aleksey
Solovev of Positive Technologies for reporting this problem.
(CVE-2025-12818)
- Correctly treat JSON constructor expressions, such
as `JSON_OBJECT()`, as non-strict (Tender Wang,
Richard Guo)
[](62397bb18)

In some cases these expressions can yield a non-null result despite
having one or more null inputs, making them non-strict.  The planner
incorrectly classified them as strict and could perform incorrect
query transformations as a result.
- Further fix processing of character classes within `SIMILAR
TO` regular expressions (Laurenz Albe)
[](281ad4ed1)

The previous fix for translating `SIMILAR TO`
pattern matching expressions to POSIX-style regular expressions
broke a corner case that formerly worked: if there is an escape
character right after the opening bracket and then a closing bracket
right after the escape sequence (for
example `[\w]`), the closing bracket was no longer
seen as terminating the character class.
- Fix parsing of aggregate functions whose arguments contain a
sub-select with a `FROM` reference to a CTE outside
the aggregate function (Tom Lane)
[](7df74e635)

Such a CTE reference must act like a outer-level column reference
when determining the aggregate's semantic level; but it was not
being accounted for, leading to obscure planner or executor errors.
- Fix "no relation entry for relid" errors in corner
cases while estimating SubPlan costs (Richard Guo)
[](79ade5873)
- Avoid unlikely use-after-free in planner's expansion of partitioned
tables (Bernd Reiß)
[](f0fe1da50)

There was a hazard only when the last live partition was
concurrently dropped.
- Remove faulty assertion in btree index cleanup (Peter Geoghegan)
[](c160fd469)
- Fix possible infinite loop in GIN index scans with multiple scan
conditions (Tom Lane)
[](d532069c3)

GIN can handle scan conditions that can reject non-matching entries
but are not useful for searching for relevant entries, for example
a `tsquery` clause like `!term`.  But
such a condition must not be first in the array of scan conditions.
The code failed to ensure that in all cases, with the result that a
query having a mix of such conditions with normal conditions might
work or not depending on the order in which the conditions were
given in the query.
- Ensure that GIN index scans can be canceled (Tom Lane)
[](25eadfd0f)

Some code paths were capable of running for a long time without
checking for interrupts.
- Ensure that BRIN autosummarization provides a snapshot for index
expressions that need one (Álvaro Herrera)
[](6ef33c805)
[](20442cf50)

Previously, autosummarization would fail for such indexes, and then
leave placeholder index tuples behind, causing the index to bloat
over time.
- Fix integer-overflow hazard in BRIN index scans when the table
contains close to 2^32 pages (Sunil S)
[](ef915bf93)

This oversight could result in an infinite loop or scanning of
unneeded table pages.
- Fix incorrect zero-extension of stored values in JIT-generated tuple
deforming code (David Rowley)
[](3398b0d02)

When not using JIT, the equivalent code does sign-extension not
zero-extension, leading to a different Datum representation of small
integer data types.  This inconsistency was masked in most cases,
but it is known to lead to "could not find memoization table
entry" errors when using Memoize plan nodes, and there might
be other symptoms.
- Fix incorrect logic for caching result-relation information for
triggers (David Rowley, Amit Langote)
[](a546964db)

In cases where partitions' column sets aren't physically identical
to their parent partitioned tables' column sets, this oversight
could lead to crashes.
- Add missing EvalPlanQual rechecks for TID Scan and TID Range Scan
plan nodes (Sophie Alpert, David Rowley)
[](ba0203880)
[](d6539f88b)

This omission led to possibly not rechecking a condition
on `ctid` during concurrent-update
situations, causing the update's behavior to vary depending on which
plan type had been selected.
- Fix EvalPlanQual handling of foreign or custom joins that do not
have an alternative local-join plan prepared for EPQ (Masahiko
Sawada, Etsuro Fujita)
[](5a9af4868)

In such cases the foreign or custom access method should be invoked
normally, but that did not happen, typically leading to a crash.
- Avoid duplicating hash partition constraints during `DETACH
CONCURRENTLY` (Haiyang Li)
[](b835759ec)

`ALTER TABLE DETACH PARTITION CONCURRENTLY` was
written to add a copy of the partitioning constraint to the
now-detached partition.  This was misguided, partially because
non-concurrent `DETACH` doesn't do that, but mostly
because in the case of hash partitioning the constraint expression
contains references to the parent table's OID.  That causes problems
during dump/restore, or if the parent table is dropped
after `DETACH`.  In v19 and later, we'll no longer
create any such copied constraints at all.  In released branches, to
minimize the risk of unforeseen consequences, only skip adding a
copied constraint if it is for hash partitioning.
- Disallow generated columns in partition keys
(Jian He, Ashutosh Bapat)
[](7180d56c5)

This was already not allowed, but the check missed some cases, such
as where the column reference is implicit in a whole-row reference.
- Disallow generated columns in `COPY ... FROM
... WHERE` clauses (Peter Eisentraut, Jian He)
[](26958f4d9)

Previously, incorrect behavior or an obscure error message resulted
from attempting to reference such a column, since generated columns
have not yet been computed at the point
where `WHERE` filtering is done.
- Fix visibility checking for statistics objects
in `pg_temp` (Noah Misch)
[](ab16418ee)

A statistics object located in a temporary schema cannot be named
without schema qualification,
but `pg_statistics_obj_is_visible()` missed that
memo and could return "true" regardless.  In turn,
functions such as `pg_describe_object()` could
fail to schema-qualify the object's name as expected.
- Fix `pg_event_trigger_dropped_objects()`'s
reporting of temporary status (Antoine Violin, Tom Lane)
[](8856f1acc)
[](f6c8e7824)

If a dropped column default, trigger, or RLS policy belongs to a
temporary table, report it with `is_temporary`
true.
- Fix memory leakage in hashed subplans (Haiyang Li)
[](e1da9c072)

Any memory consumed by the hash functions used for hashing tuples
constituted a query-lifespan memory leak.  One way that could happen
is if the values being hashed require de-toasting.
- Fix minor memory leak during WAL replay of database creation
(Nathan Bossart)
[](c72b5c536)
- Fix corruption of the shared statistics table after out-of-memory
failures (Mikhail Kot)
[](12f57681c)

Previously, an out-of-memory failure partway through creating a new
hash table entry left a broken entry behind, potentially causing
errors in other sessions later.
- Fix concurrent update issue in `MERGE`
(Yugo Nagata)
[](21a61b87f)

When executing a `MERGE UPDATE` action, if there is
more than one concurrent update of the target row, the
lock-and-retry code would sometimes incorrectly identify the latest
version of the target tuple, leading to incorrect results.
- Add missing replica identity checks in `MERGE` and
`INSERT ... ON CONFLICT DO UPDATE`
(Zhijie Hou)
[](421d7a157)
[](0c4d5a45d)
[](d37694b97)

If `MERGE` may require update or delete actions,
and the target table publishes updates or deletes, insist that it
have a `REPLICA IDENTITY` defined.  Failing to
require this can silently break replication.
Likewise, `INSERT` with
an `UPDATE` option must require `REPLICA
IDENTITY` if the target table publishes either inserts or
updates.
- Avoid deadlock during `DROP SUBSCRIPTION` when
publisher is on the same server as subscriber (Dilip Kumar)
[](7ece76129)
- Fix incorrect reporting of replication lag
in `pg_stat_replication` view (Fujii Masao)
[](2e55cf4ef)

If any standby server's replay LSN stopped advancing,
the `write_lag`
and `flush_lag` columns would eventually
stop updating.
- Avoid duplicative log messages about
invalid `primary_slot_name` settings (Fujii Masao)
[](4fd916eab)
- Remove the unfinished slot state file after failing to write a
replication slot's state to disk (Michael Paquier)
[](bfdd1a12d)

Previously, a failure such as out-of-disk-space resulted in leaving
a temporary `state.tmp` file behind.  That's
problematic because it would block all subsequent attempts to
write the state, requiring manual intervention to clean up.
- Fix mishandling of lock timeout signals in parallel apply workers
for logical replication (Hayato Kuroda)
[](a54c7a113)

The same signal number was being used for both worker shutdown and
lock timeout, leading to confusion.
- Avoid unwanted WAL receiver shutdown when switching from streaming
to archive WAL source (Xuneng Zhou)
[](9b6109607)

During a timeline change, a standby server's WAL receiver should
remain alive, waiting for a new WAL streaming start point.  Instead
it was repeatedly shutting down and immediately getting restarted,
which could confuse status monitoring code.
- Avoid failures in logical replication due to chance collisions of
file numbers between regular and temporary tables (Vignesh C)
[](ab874faaa)

This low-probability problem manifested as transient errors
like "unexpected duplicate for
tablespace `X`,
relfilenode `Y`".
`contrib/autoprewarm` was also affected.
A side-effect of the fix is that the SQL
function `pg_filenode_relation()` will now ignore
temporary tables.
- Fix use-after-free issue in the relation synchronization cache
maintained by the pgoutput logical
decoding plugin (Vignesh C, Masahiko Sawada)
[](b07682bce)

An error during logical decoding could result in crashes in
subsequent logical decoding attempts in the same session.
The case is only reachable when pgoutput
is invoked via SQL functions.
- Avoid unnecessary invalidation of logical replication slots
(Bertrand Drouvot)
[](e3714dc05)
- Avoid assertion failure when trying to release a replication slot in
single-user mode (Hayato Kuroda)
[](fea1cc3f7)
- Fix incorrect printing of messages about failures in checking
whether the user has Windows administrator privilege (Bryan Green)
[](9883e3cd1)

This code would have crashed or at least printed garbage.
No such cases have been reported though, indicating that failure of
these system calls is extremely rare.
- Avoid startup failure on macOS and BSD platforms when there is a
collision with a pre-existing semaphore set (Tom Lane)
[](e67d5f7ba)

If the pre-existing set has fewer semaphores than we asked for,
these platforms return EINVAL
not EEXIST as our code expected, resulting
in failure to start the database.
- Avoid crash when attempting to
test PostgreSQL with certain libsanitizer
options (Emmanuel Sibi, Jacob Champion)
[](c775bf048)
- Fix false memory-context-checking warnings in debug builds
on 64-bit Windows (David Rowley)
[](cdc04a6c3)
- Correctly handle `GROUP BY DISTINCT` in PL/pgSQL
assignment statements (Tom Lane)
[](b7f6798c0)

The parser failed to record the `DISTINCT` option
in this context, so that the command would act as if it were
plain `GROUP BY`.
- Avoid leaking memory when handling a SQL error within PL/Python
(Tom Lane)
[](cbfd4d0f8)

This fixes a session-lifespan memory leak introduced in our previous
minor releases.
- Fix libpq's trace output of characters
with the high bit set (Ran Benita)
[](701a0bd56)

On platforms where `char` is considered signed, the
output included unsightly `\xffffff` decoration.
- Fix libpq's handling of socket-related
errors on Windows within its GSSAPI logic (Ning Wu, Tom Lane)
[](46c4478db)

The code for encrypting/decrypting transmitted data using GSSAPI did
not correctly recognize error conditions on the connection socket,
since Windows reports those differently than other platforms.  This
led to failure to make such connections on Windows.
- In pg_dump, dump security labels on
subscriptions and event triggers (Jian He, Fujii Masao)
[](20b23784f)

Labels on these types of objects were previously missed.
- Fix pg_dump's sorting of default ACLs and
foreign key constraints (Kirill Reshke, Álvaro Herrera)
[](e68fa9a83)
[](412d29fd2)
[](06c1ee6b7)

Ensure consistent ordering of these database object types, as was
already done for other object types.
- In pg_dump, label comments for
separately-dumped domain constraints with the proper dependency
(Noah Misch)
[](3cf328eca)

This error could lead to
parallel pg_restore attempting to create
the comment before the constraint itself has been restored.
- In pg_restore, skip comments and security
labels for publications and subscriptions that are not being
restored (Jian He, Fujii Masao)
[](97527a5e6)
[](0870397cc)

Do not emit `COMMENT` or `SECURITY
LABEL` commands for these objects
when `--no-publications`
or `--no-subscriptions` is specified.
- Fix assorted errors in the data compression logic
in pg_dump
and pg_restore
(Daniel Gustafsson, Tom Lane)
[](ec017a305)
[](1518b7d76)
[](c865f5b9f)

Error checking was missing or incorrect in several places, and there
were also portability issues that would manifest on big-endian
hardware.  These problems had been missed because this code is only
used to read compressed TOC files within directory-format
dumps.   pg_dump never produces such a
dump; the case can be reached only by manually compressing the TOC
file after the fact, which is a supported thing to do but very
uncommon.
- Fix pgbench to error out cleanly if
a `COPY` operation is started (Anthonin Bonnefoy)
[](640590bb4)

pgbench doesn't intend to support this
case, but previously it went into an infinite loop.
- Fix pgbench's reporting of multiple
errors (Yugo Nagata)
[](36c4d30c8)

In cases where two successive `PQgetResult` calls
both fail, pgbench might report the wrong
error message.
- In pgbench, fix faulty assertion about
errors in pipeline mode (Yugo Nagata)
[](8b2e290bd)
- Ensure that `contrib/pg_buffercache` functions
can be canceled (Satyanarayana Narlapuram, Yuhang Qiu)
[](815fcfb20)

Some code paths were capable of running for a long time without
checking for interrupts.
- Fix `contrib/pg_prewarm`'s privilege checks for
indexes (Ayush Vatsa, Nathan Bossart)
[](fae0ce5e3)
[](c26a8eaf6)

`pg_prewarm()` requires `SELECT`
privilege on relations to be prewarmed.  However, since indexes have
no SQL privileges of their own, this resulted in non-superusers
being unable to prewarm indexes.  Instead, check
for `SELECT` privilege on the index's table.
- Make `contrib/pgstattuple` more robust about
empty or invalid index pages (Nitin Motiani)
[](c0f9fe877)

Count all-zero pages as free space, and ignore pages that are
invalid according to a check of the page's special-space size.
The code for btree indexes already counted all-zero pages as free,
but the hash and gist code would error out, which has been found to
be much less user-friendly.  Similarly, make all three cases agree
on ignoring corrupted pages rather than throwing errors.
- Harden our read and write barrier macros to satisfy Clang
(Thomas Munro)
[](2f76ffe5e)

We supposed that `__atomic_thread_fence()` is a
sufficient barrier to prevent the C compiler from re-ordering memory
accesses around it, but it appears that that's not true for Clang,
allowing it to generate incorrect code for at least RISC-V, MIPS,
and LoongArch machines.  Add explicit compiler barriers to fix that.
- Fix building with LLVM version 21 and later (Holger Hoffstätte)
[](2670881af)
- When building with meson, apply the same special optimization flags
for `numeric.c`
and `checksum.c` as the makefile build does
(Nathan Bossart, Jeff Davis)
[](509c77929)
[](2de24ca6c)

Use `-ftree-vectorize` for both files, as well
as `-funroll-loops`
for `checksum.c`, to match what the makefiles
have long done.
- Fix PGXS build infrastructure to support building
NLS `po` files for extensions (Ryo Matsumura)
[](a506b0c0a)

## Release 16.10

## Release date:

2025-08-14

This release contains a variety of fixes from 16.9.
For information about new features in major release 16, see
[release-16](#release-16).

### Migration to Version 16.10

A dump/restore is not required for those running 16.X.

However, if you have any
BRIN `numeric_minmax_multi_ops` indexes, it is
advisable to reindex them after updating.  See the fourth changelog
entry below.

Also, if you are upgrading from a version earlier than 16.9,
see [release-16-9](#release-16-9).

### Changes

- Tighten security checks in planner estimation functions
(Dean Rasheed)
[](7e86da539)

The fix for CVE-2017-7484, plus followup fixes, intended to prevent
leaky functions from being applied to statistics data for columns
that the calling user does not have permission to read.  Two gaps in
that protection have been found.  One gap applies to partitioning
and inheritance hierarchies where RLS policies on the tables should
restrict access to statistics data, but did not.

The other gap applies to cases where the query accesses a table via
a view, and the view owner has permissions to read the underlying
table but the calling user does not have permissions on the view.
The view owner's permissions satisfied the security checks, and the
leaky function would get applied to the underlying table's
statistics before we check the calling user's permissions on the
view.  This has been fixed by making security checks on views occur
at the start of planning.  That might cause permissions failures to
occur earlier than before.

The PostgreSQL Project thanks
Dean Rasheed for reporting this problem.
(CVE-2025-8713)
- Prevent pg_dump scripts from being used
to attack the user running the restore (Nathan Bossart)
[](7ad8e7909)

Since dump/restore operations typically involve running SQL commands
as superuser, the target database installation must trust the source
server.  However, it does not follow that the operating system user
who executes psql to perform the restore
should have to trust the source server.  The risk here is that an
attacker who has gained superuser-level control over the source
server might be able to cause it to emit text that would be
interpreted as psql meta-commands.
That would provide shell-level access to the restoring user's own
account, independently of access to the target database.

To provide a positive guarantee that this can't happen,
extend psql with
a `\restrict` command that prevents execution of
further meta-commands, and teach pg_dump
to issue that before any data coming from the source server.

The PostgreSQL Project thanks Martin Rakhmanov, Matthieu Denais, and
RyotaK for reporting this problem.
(CVE-2025-8714)
- Convert newlines to spaces in names included in comments
in pg_dump output
(Noah Misch)
[](850caae60)

Object names containing newlines offered the ability to inject
arbitrary SQL commands into the output script.  (Without the
preceding fix, injection of psql
meta-commands would also be possible this way.)
CVE-2012-0868 fixed this class of problem at the time, but later
work reintroduced several cases.

The PostgreSQL Project thanks
Noah Misch for reporting this problem.
(CVE-2025-8715)
- Fix incorrect distance calculation in
BRIN `numeric_minmax_multi_ops` support function
(Peter Eisentraut, Tom Lane)
[](b9279058a)

The results were sometimes wrong on 64-bit platforms, and wildly
wrong on 32-bit platforms.  This did not produce obvious failures
because the logic is only used to choose how to merge values into
ranges; at worst the index would become inefficient and bloated.
Nonetheless it's recommended to reindex any BRIN indexes that use
the `numeric_minmax_multi_ops` operator class.
- Avoid regression in the size of XML input that we will accept
(Michael Paquier, Erik Wienhold)
[](6d5e493b4)
[](762c6d8d2)

Our workaround for a bug in early 2.13.x releases
of libxml2 made use of a code path that
rejects text chunks exceeding 10MB, whereas the previous coding did
not.  Those early releases are presumably extinct in the wild by
now, so revert to the previous coding.
- Fix `MERGE` into a plain-inheritance parent table
(Dean Rasheed)
[](3611794af)

Insertions into such a target table could crash or produce incorrect
query results due to failing to handle `WITH CHECK
OPTION` and `RETURNING` actions.
- Allow tables with statement-level triggers to become partitions or
inheritance children (Etsuro Fujita)
[](3863c6fb6)

We do not allow partitions or inheritance child tables to have
row-level triggers with transition tables, because an operation on
the whole inheritance tree would need to maintain a separate
transition table for each such child table.  But that problem does
not apply for statement-level triggers, because only the parent's
statement-level triggers will be fired.  The code that checks
whether an existing table can become a partition or inheritance
child nonetheless rejected both kinds of trigger.
- Disallow collecting transition tuples from child foreign tables
(Etsuro Fujita)
[](9cca445df)

We do not support triggers with transition tables on foreign tables.
However, the case of a partition or inheritance child that is a
foreign table was overlooked.  If the parent has such a trigger,
incorrect transition tuples were collected from the foreign child.
Instead throw an error, reporting that the case is not supported.
- Allow resetting unknown custom parameters with reserved prefixes
(Nathan Bossart)
[](b998ce327)

Previously, if a parameter setting had been stored
using `ALTER DATABASE/ROLE/SYSTEM`, the stored
setting could not be removed if the parameter was unknown but had a
reserved prefix.  This case could arise if an extension used to have
a parameter, but that parameter had been removed in an upgrade.
- Fix a potential deadlock during `ALTER SUBSCRIPTION ... DROP
PUBLICATION` (Ajin Cherian)
[](adfd80219)

Ensure that server processes acquire catalog locks in a consistent
order during replication origin drops.
- Shorten the race condition window for creating indexes with
conflicting names (Tom Lane)
[](1e24ea160)

When choosing an auto-generated name for an index, avoid conflicting
with not-yet-committed `pg_class` rows as
well as fully-valid ones.  This avoids possibly choosing the same
name as some concurrent `CREATE INDEX` did,
when that command is still in process of filling its index, or is
done but is part of a not-yet-committed transaction.  There's still
a window for trouble, but it's only as long as the time needed to
validate a new index's parameters and insert
its `pg_class` row.
- Prevent usage of incorrect `VACUUM` options in some
cases where multiple tables are vacuumed in a single command (Nathan
Bossart, Michael Paquier)
[](d187cabdd)

The `TRUNCATE` and `INDEX_CLEANUP`
options of one table could be applied to others.
- Fix processing of character classes within `SIMILAR
TO` regular expressions (Laurenz Albe)
[](e9e535d61)
[](52d08620e)

The code that translates `SIMILAR TO` pattern
matching expressions to POSIX-style regular expressions did not
consider that square brackets can be nested.  For example, in a
pattern like `[[:alpha:]%_]`, the code treated
the `%` and `_` characters as
metacharacters when they should be literals.
- When deparsing queries, always add parentheses around the expression
in `FETCH FIRST `expression` ROWS
WITH TIES` clauses (Heikki Linnakangas)
[](92a9ba3b9)
[](558ea446a)

This avoids some cases where the deparsed result wasn't
syntactically valid.
- Limit the checkpointer process's fsync request queue size (Alexander
Korotkov, Xuneng Zhou)
[](f0cdc2afd)
[](2ac50f118)

With very large `shared_buffers` settings, it was
possible for the checkpointer to attempt to allocate more than 1GB
for fsync requests, leading to failure and an infinite loop.  Clamp
the queue size to prevent this scenario.
- Avoid infinite wait in logical decoding when reading a
partially-written WAL record (Vignesh C)
[](b485e1c89)

If the server crashes after writing the first part of a WAL record
that would span multiple pages, subsequent logical decoding of the
WAL stream would wait for data to arrive on the next WAL page.
That might never happen if the server is now idle.
- Fix inconsistent quoting of role names in ACL strings (Tom Lane)
[](53a936b61)

The previous quoting rule was locale-sensitive, which could lead to
portability problems when transferring `aclitem` values
across installations.  (pg_dump does not
do that, but other tools might.)  To ensure consistency, always quote
non-ASCII characters in `aclitem` output; but to preserve
backward compatibility, never require that they be quoted
during `aclitem` input.
- Reject equal signs (`=`) in the names of relation
options and foreign-data options (Tom Lane)
[](ab758ec4d)

There's no evident use-case for option names like this, and allowing
them creates ambiguity in the stored representation.
- Fix potentially-incorrect decompression of LZ4-compressed archive
data (Mikhail Gribkov)
[](5c639523f)

This error seems to manifest only with not-very-compressible input
data, which may explain why it escaped detection.
- Avoid a rare scenario where a btree index scan could mark the wrong
index entries as dead (Peter Geoghegan)
[](c7f25feb3)
- Avoid re-distributing cache invalidation messages from other
transactions during logical replication (vignesh C)
[](b2ae07720)

Our previous round of minor releases included a bug fix to ensure
that replication receiver processes would respond to cross-process
cache invalidation messages, preventing them from using stale
catalog data while performing replication updates.  However, the fix
unintentionally made them also redistribute those messages again,
leading to an exponential increase in the number of invalidation
messages, which would often end in a memory allocation failure.
Fix by not redistributing received messages.
- Avoid premature removal of old WAL during checkpoints (Vitaly Davydov)
[](cea8f2c3e)

If a replication slot's restart point is advanced while a checkpoint
is in progress, no-longer-needed WAL segments could get removed too
soon, leading to recovery failure if the database crashes
immediately afterwards.  Fix by keeping them for one additional
checkpoint cycle.
- Never move a replication slot's confirmed-flush position backwards
(Shveta Malik)
[](c0f51fde5)

In some cases a replication client could acknowledge an LSN that's
past what it has stored persistently, and then perhaps send an older
LSN after a restart.  We consider this not-a-bug so long as the
client did not have anything it needed to do for the WAL between the
two points.  However, we should not re-send that WAL for fear of
data duplication, so make sure we always believe the latest
confirmed LSN for a given slot.
- Prevent excessive delays before launching new logical replication
workers (Tom Lane)
[](87c8ed3db)

In some cases the logical replication launcher could sleep
considerably longer than the
configured `wal_retrieve_retry_interval` before
launching a new worker.
- Fix use-after-free during logical replication of `INSERT
... ON CONFLICT` (Ethan Mertz, Michael Paquier)
[](ec96e8812)

This could result in incorrect progress reporting, or with very bad
luck it could result in a crash of the WAL sender process.
- Allow waiting for a transaction on a standby server to be
interrupted (Kevin K Biju)
[](63fa7caa9)

Creation of a replication slot on a standby server may require waiting
for some active transaction(s) to finish on the primary and then be
replayed on the standby.  Since that could be an indefinite wait,
it's desirable to allow the operation to be cancelled, but there was
no check for query cancel in the loop.
- Do not let cascading logical WAL senders try to send data that's
beyond what has been replayed on their standby server (Alexey
Makhmutov)
[](5e6d561bc)

This avoids a situation where such WAL senders could get stuck at
standby server shutdown, waiting for replay work that will not
happen because the server's startup process is already shut down.
- Fix per-relation memory leakage in autovacuum (Tom Lane)
[](e087b5b79)
- Fix session-lifespan memory leaks
in `XMLSERIALIZE(... INDENT)`
(Dmitry Kovalenko, Tom Lane)
[](abb517d61)
[](ee58de100)
- Fix some places that might try to fetch toasted fields of system
catalogs without any snapshot (Nathan Bossart)
[](24135398f)

This could result in an assertion failure or "cannot fetch
toast data without an active snapshot" error.
- Avoid assertion failure during cross-table constraint updates
(Tom Lane, Jian He)
[](c15798cf9)
[](d36980b71)
- Remove faulty assertion that a command tag must have been determined
by the end of `PortalRunMulti()` (Álvaro Herrera)
[](4871c1e9c)

This failed in edge cases such as an empty prepared statement.
- Fix assertion failure in `XMLTABLE` parsing
(Richard Guo)
[](d3716d4b1)
- Restore the ability to run PL/pgSQL expressions in parallel
(Dipesh Dhameliya)
[](3bbc1c4a7)

PL/pgSQL's notion of an "expression" is very broad,
encompassing any SQL `SELECT` query that returns a
single column and no more than one row.  So there are cases, for
example evaluation of an aggregate function, where the query
involves significant work and it'd be useful to run it with parallel
workers.  This used to be possible, but a previous bug fix
unintentionally disabled it.
- Fix edge-case resource leaks in PL/Python error reporting (Tom Lane)
[](5c7fd5976)
[](ecc8fd2b7)

An out-of-memory failure while reporting an error from Python could
result in failure to drop reference counts on Python objects,
leading to session-lifespan memory leakage.
- Fix libpq's `PQport()`
function to never return NULL unless the passed connection is NULL
(Daniele Varrazzo)
[](009c20a3d)

This is the documented behavior, but
recent libpq versions would return NULL
in some cases where the user had not provided a port specification.
Revert to our historical behavior of returning an empty string in
such cases.  (v18 and later will return the compiled-in default port
number, typically `"5432"`, instead.)
- Avoid failure when GSSAPI authentication requires packets larger
than 16kB (Jacob Champion, Tom Lane)
[](ca70ee6ed)

Larger authentication packets are needed for Active Directory users
who belong to many AD groups.  This limitation manifested in
connection failures with unintelligible error messages,
typically "GSSAPI context establishment error: The routine
must be called again to complete its function: Unknown
error".
- Fix timing-dependent failures in SSL and GSSAPI data transmission
(Tom Lane)
[](3f37400cf)

When using SSL or GSSAPI encryption in non-blocking
mode, libpq sometimes failed
with "SSL error: bad length" or "GSSAPI caller
failed to retransmit all data needing to be retried".
- Avoid null-pointer dereference during connection lookup
in ecpg applications (Aleksander
Alekseev)
[](313d3102f)

The case could occur only if the application has some connections
that are named and some that are not.
- Improve psql's tab completion
for `COPY` and `\copy` options
(Atsushi Torikoshi)
[](d69836b13)

The same completions were offered for both `COPY
FROM` and `COPY TO`, although some options
are only valid for one case or the other.  Distinguish these cases
to provide more accurate suggestions.
- Avoid assertion failure in pgbench when
multiple pipeline sync messages are received (Fujii Masao)
[](1d3ded521)
- Ensure that pg_dump dumps comments on
domain constraints in a valid order (Jian He)
[](cef998ef8)

In some cases the comment command could appear before creation of
the constraint.
- Ensure stable sort ordering in pg_dump
for all types of database objects (Noah Misch, Andreas Karlsson)
[](0ac1581c3)
[](9affed263)
[](216683296)

pg_dump sorts objects by their logical
names before performing dependency-driven reordering.  This sort did
not account for the full unique key identifying certain object types
such as rules and constraints, and thus it could produce dissimilar
sort orders for logically-identical databases.  That made it
difficult to compare databases by
diff'ing pg_dump output, so improve the
logic to ensure stable sort ordering in all cases.
- In pg_upgrade, check for inconsistent
inherited not-null constraints (Ali Akbar)
[](f63e408e8)
[](f943e2339)
[](05b367bea)
[](06f444816)

PostgreSQL versions before 18 allow an
inherited column not-null constraint to be dropped.  However, this
results in a schema that cannot be restored, leading to failure
in pg_upgrade.  Detect such cases
during pg_upgrade's preflight checks to
allow users to fix them before initiating the upgrade.
- Avoid assertion failure if `track_commit_timestamp`
is enabled during initdb (Hayato Kuroda,
Andy Fan)
[](7e7059abf)
- Fix pg_waldump to show information about
dropped statistics in `PREPARE TRANSACTION` WAL
records (Daniil Davydov)
[](0d2063585)
- Avoid possible leak of the open connection
during `contrib/dblink` connection establishment
(Tom Lane)
[](8eef55db1)

In the rare scenario where we hit out-of-memory while inserting the
new connection object into dblink's hashtable, the open connection
would be leaked until end of session, leaving an idle session
sitting on the remote server.
- Make `contrib/pg_prewarm` cope with very
large `shared_buffers` settings (Daria Shanina)
[](169429264)

Autoprewarm failed with a memory allocation error
if `shared_buffers` was larger than about 50
million buffers (400GB).
- In `contrib/pg_stat_statements`, avoid leaving
gaps in the set of parameter numbers used in a normalized query
(Sami Imseih)
[](7e8b44f4e)
- Fix memory leakage in `contrib/postgres_fdw`'s
DirectModify methods (Tom Lane)
[](2b92dc4ee)

The `PGresult` holding the results of the
remote modify command would be leaked for the rest of the session if
the query fails between invocations of the DirectModify methods,
which could happen when there's `RETURNING` data to
process.
- Ensure that directories listed
in configure's
`--with-includes`
and `--with-libraries` options are searched before
system-supplied directories (Tom Lane)
[](bbc20c8a9)

A common reason for using these options is to allow a user-built
version of some library to override the system-supplied version.
However, that failed to work in some environments because of
careless ordering of switches in the commands issued by the makefiles.
- Fix configure's checks
for `__cpuid()`
and `__cpuidex()` (Lukas Fittl, Michael Paquier)
[](c1984be23)

configure failed to detect these
Windows-specific functions, so that they would not be used,
leading to slower-than-necessary CRC computations since the
availability of hardware instructions could not be verified.
The practical impact of this error was limited, because production
builds for Windows typically do not use the Autoconf toolchain.
- Fix build failure with `--with-pam` option on
Solaris-based platforms (Tom Lane)
[](e4d585455)

Solaris is inconsistent with other Unix platforms about the API for
PAM authentication.  This manifested as an "inconsistent
pointer" compiler warning, which we never did anything about.
But as of GCC 14 it's an error not warning by default, so fix it.
- Make our code portable to GNU Hurd (Michael Banck, Christoph Berg,
Samuel Thibault)
[](d25d392e8)
[](3a2617e4f)

Fix assumptions about `IOV_MAX`
and `O_RDONLY` that don't hold on Hurd.
- Make our usage of `memset_s()` conform strictly
to the C11 standard (Tom Lane)
[](253cf661c)
[](4b53cb493)

This avoids compile failures on some platforms.
- Silence compatibility warning when using Meson to build with MSVC
(Peter Eisentraut)
[](629cc1623)
- Prevent uninitialized-value compiler warnings in JSONB comparison
code (Tom Lane)
[](5db55e13f)
- Avoid deprecation warnings when building
with libxml2 2.14 and later
(Michael Paquier)
[](d24a96ce2)
- Avoid problems when compiling `pg_locale.h` under
C++ (John Naylor)
[](aae9aad19)

PostgreSQL header files generally need to
be wrapped in `extern "C" { ... }` in order to be
included in extensions written in C++.  This failed
for `pg_locale.h` because of its use
of libicu headers, but we can work around
that by suppressing C++-only declarations in those headers.  C++
extensions that want to use libicu's C++
APIs can do so by including the libicu
headers ahead of `pg_locale.h`.

## Release 16.9

## Release date:

2025-05-08

This release contains a variety of fixes from 16.8.
For information about new features in major release 16, see
[release-16](#release-16).

### Migration to Version 16.9

A dump/restore is not required for those running 16.X.

However, if you have any self-referential foreign key constraints on
partitioned tables, it may be necessary to recreate those constraints
to ensure that they are being enforced correctly.  See the second
changelog entry below.

Also, if you have any BRIN bloom indexes, it may be advisable to
reindex them after updating.  See the third changelog entry below.

Also, if you are upgrading from a version earlier than 16.5,
see [release-16-5](#release-16-5).

### Changes

- Avoid one-byte buffer overread when examining invalidly-encoded
strings that are claimed to be in GB18030 encoding
(Noah Misch, Andres Freund)
[](d1264948f)
[](f3bb0b2c4)

While unlikely, a SIGSEGV crash could occur if an incomplete
multibyte character appeared at the end of memory.  This was
possible both in the server and
in libpq-using applications.
(CVE-2025-4207)
- Handle self-referential foreign keys on partitioned tables correctly
(Álvaro Herrera)
[](1817d62ec)

Creating or attaching partitions failed to make the required catalog
entries for a foreign-key constraint, if the table referenced by the
constraint was the same partitioned table.  This resulted in failure
to enforce the constraint fully.

To fix this, you should drop and recreate any self-referential
foreign keys on partitioned tables, if partitions have been created
or attached since the constraint was created.  Bear in mind that
violating rows might already be present, in which case recreating
the constraint will fail, and you'll need to fix up those rows
before trying again.
- Avoid data loss when merging compressed BRIN summaries
in `brin_bloom_union()` (Tomas Vondra)
[](ebcc799a7)

The code failed to account for decompression results not being
identical to the input objects, which would result in failure to add
some of the data to the merged summary, leading to missed rows in
index searches.

This mistake was present back to v14 where BRIN bloom indexes were
introduced, but this code path was only rarely reached then.  It's
substantially more likely to be hit in v17 because parallel index
builds now use the code.
- Fix unexpected "attribute has wrong type" errors
in `UPDATE`, `DELETE`,
and `MERGE` queries that use whole-row table
references to views or functions in `FROM`
(Tom Lane)
[](fec43428c)
- Fix `MERGE` into a partitioned table
with `DO NOTHING` actions (Tender Wang)
[](8d4cd3b4a)

Some cases failed with "unknown action in MERGE WHEN
clause" errors.
- Prevent failure in `INSERT` commands when the table
has a `GENERATED` column of a domain data type and
the domain's constraints disallow null values (Jian He)
[](f04e0faa3)

Constraint failure was reported even if the generation expression
produced a perfectly okay result.
- Correctly process references to outer CTE names that appear within
a `WITH` clause attached to
an `INSERT`/`UPDATE`/`DELETE`/`MERGE`
command that's inside `WITH` (Tom Lane)
[](1980ec2bc)

The parser failed to detect disallowed recursion cases, nor did it
account for such references when sorting CTEs into a usable order.
- Don't try to parallelize `array_agg()` when the
argument is of an anonymous record type (Richard Guo, Tom Lane)
[](a7aa9f21f)

The protocol for communicating with parallel workers doesn't support
identifying the concrete record type that a worker is returning.
- Fix `ARRAY(`subquery`)`
and `ARRAY[`expression, ...`]`
constructs to produce sane results when the input is of
type `int2vector` or `oidvector` (Tom Lane)
[](0405982c7)

This patch restores the behavior that existed
before PostgreSQL 9.5: the result is of
type `int2vector[]` or `oidvector[]`.
- Fix possible erroneous reports of invalid affixes while parsing
Ispell dictionaries (Jacob Brazeal)
[](61513da08)
- Fix `ALTER TABLE ADD COLUMN` to correctly handle
the case of a domain type that has a default
(Jian He, Tom Lane, Tender Wang)
[](edc3bccd0)
[](053222a97)

If a domain type has a default, adding a column of that type (without
any explicit `DEFAULT`
clause) failed to install the domain's default
value in existing rows, instead leaving the new column null.
- Repair misbehavior when there are duplicate column names in a
foreign key constraint's `ON DELETE SET DEFAULT`
or `SET NULL` action (Tom Lane)
[](fb3a77fd9)
- Improve the error message for disallowed attempts to alter the
properties of a foreign key constraint (Álvaro Herrera)
[](9ea5fe5b6)
- Avoid error when resetting
the `relhassubclass` flag of a temporary
table that's marked `ON COMMIT DELETE ROWS`
(Noah Misch)
[](5905e9935)
- Add missing deparsing of the `INDENT` option
of `XMLSERIALIZE()` (Jim Jones)
[](0af3ae468)
[](514d47dfb)

Previously, views or rules
using `XMLSERIALIZE(... INDENT)` were dumped
without the `INDENT` clause, causing incorrect
results after restore.
- Avoid premature evaluation of the arguments of an aggregate function
that has both `FILTER` and `ORDER
BY` (or `DISTINCT`) options (David Rowley)
[](887a23237)

If there is `ORDER BY`
or `DISTINCT`, we consider pre-sorting the
aggregate input values rather than doing the sort within the Agg
plan node.  But this is problematic if the aggregate inputs include
expressions that could fail (for example, a division where some of
the input divisors could be zero) and there is
a `FILTER` clause that's meant to prevent such
failures.  Pre-sorting would push the expression evaluations to
before the `FILTER` test, allowing the failures to
happen anyway.  Avoid this by not pre-sorting if there's
a `FILTER` and the input expressions are anything
more complex than a simple Var or Const.
- Fix planner's failure to identify more than one hashable
ScalarArrayOpExpr subexpression within a top-level expression
(David Geier)
[](5a0840b76)

This resulted in unnecessarily-inefficient execution of any
additional subexpressions that could have been processed with a hash
table (that is, `IN`, `NOT IN`,
or `= ANY` clauses with all-constant right-hand
sides).
- Disable "skip fetch" optimization in bitmap heap scan
(Matthias van de Meent)
[](980727b84)

It turns out that this optimization can result in returning dead
tuples when a concurrent vacuum marks a page all-visible.
- Fix performance issues in GIN index search startup when there are
many search keys (Tom Lane, Vinod Sridharan)
[](d52221cf0)
[](4b65b085a)

An indexable clause with many keys (for example, `jsonbcol
?| array[...]` with tens of thousands of array elements)
took O(N^2) time to start up, and was
uncancelable for that interval too.
- Detect missing support procedures in a BRIN index operator class,
and report an error instead of crashing (Álvaro Herrera)
[](e0d8f49a3)
- Respond to interrupts (such as query cancel) while waiting for
asynchronous subplans of an Append plan node (Heikki Linnakangas)
[](004dbbd72)

Previously, nothing would happen until one of the subplans becomes
ready.
- Report the I/O statistics of active WAL senders more frequently
(Bertrand Drouvot)
[](e2a82cd23)

Previously, the `pg_stat_io` view failed to
accumulate I/O performed by a WAL sender until that process exited.
Now such I/O will be reported after at most one second's delay.
- Fix race condition in handling
of `synchronous_standby_names` immediately after
startup (Melnikov Maksim, Michael Paquier)
[](c922ae2c4)

For a short period after system startup, backends might fail to wait
for synchronous commit even
though `synchronous_standby_names` is enabled.
- Avoid infinite loop if `scram_iterations` is set to
INT_MAX (Kevin K Biju)
[](de1484736)
- Avoid possible crashes due to double transformation
of `json_array()`'s subquery (Tom Lane)
[](ca54f9b70)
- Fix `pg_strtof()` to not crash with null endptr
(Alexander Lakhin, Tom Lane)
[](5c64ece8a)
- Fix crash after out-of-memory in certain GUC assignments (Daniel
Gustafsson)
[](8d48e84c5)
- Avoid crash when a Snowball stemmer encounters an out-of-memory
condition (Maksim Korotkov)
[](c0c364fa1)
- Disallow copying of invalidated replication slots (Shlok Kyal)
[](87e8599e0)

This prevents trouble when the invalid slot points to WAL that's
already been removed.
- Disallow restoring logical replication slots on standby servers that
are not in hot-standby mode (Masahiko Sawada)
[](cc628f661)

This prevents a scenario where the slot could remain valid after
promotion even if `wal_level` is too low.
- Prevent over-advancement of catalog xmin in "fast
forward" mode of logical decoding (Zhijie Hou)
[](21a7caeeb)

This mistake could allow deleted catalog entries to be vacuumed away
even though they were still potentially needed by the WAL-reading
process.
- Avoid data loss when DDL operations that don't take a strong lock
affect tables that are being logically replicated (Shlok Kyal,
Hayato Kuroda)
[](9a2f8b4f0)
[](9987c9466)

The catalog changes caused by the DDL command were not reflected
into WAL-decoding processes, allowing them to decode subsequent
changes using stale catalog data, probably resulting in data
corruption.
- Prevent incorrect reset of replication origin when an apply worker
encounters an error but the error is caught and does not result in
worker exit (Hayato Kuroda)
[](0de091a4b)

This mistake could allow duplicate data to be applied.
- Avoid duplicate snapshot creation in logical replication index
lookups (Heikki Linnakangas)
[](8171d2dae)
[](324e0b656)
- Improve detection of mixed-origin subscriptions
(Hou Zhijie, Shlok Kyal)
[](1c2a2354c)

Subscription creation gives a warning if a subscribed-to table is
also being followed through other publications, since that could
cause duplicate data to be received.  This change improves that
logic to also detect cases where a partition parent or child table
is the one being followed through another publication.
- Fix wrong checkpoint details in error message about incorrect
recovery timeline choice (David Steele)
[](b4969a296)

If the requested recovery timeline is not reachable, the reported
checkpoint and timeline should be the values read from the
backup_label, if there is one.  This message previously reported
values from the control file, which is correct when recovering from
the control file without a backup_label, but not when there is a
backup_label.
- Remove incorrect assertion
in `pgstat_report_stat()` (Michael Paquier)
[](e9ab8677b)
- Fix overly-strict assertion
in `gistFindCorrectParent()` (Heikki Linnakangas)
[](419321398)
- Fix rare assertion failure in standby servers when the primary is
restarted (Heikki Linnakangas)
[](2f33de3cd)
- In PL/pgSQL, avoid "unexpected plan node type" error
when a scrollable cursor is defined on a
simple `SELECT `expression``
query (Andrei Lepikhov)
[](a28c1fb61)
- Don't try to drop individual index partitions
in pg_dump's `--clean`
mode (Jian He)
[](a25f21d99)

The server rejects such `DROP` commands.  That has
no real consequences, since the partitions will go away anyway in
the subsequent `DROP`s of either their parent
tables or their partitioned index.  However, the error reported for
the attempted drop causes problems when restoring
in `--single-transaction` mode.
- In pg_dumpall, avoid emitting invalid
role `GRANT` commands
if `pg_auth_members` contains invalid role
OIDs (Tom Lane)
[](d850a6600)

Instead, print a warning and skip the entry.  This copes better with
catalog corruption that has been seen to occur in back branches as a
result of race conditions between `GRANT`
and `DROP ROLE`.
- In pg_amcheck
and pg_upgrade, use the correct function
to free allocations made by libpq
(Michael Paquier, Ranier Vilela)
[](9ca2145b0)
[](57467ec7b)
[](816149dc6)

These oversights could result in crashes in certain Windows build
configurations, such as a debug build
of libpq used by a non-debug build of the
calling application.
- Allow `contrib/dblink` queries to be interrupted
by query cancel (Noah Misch)
[](82a8f0f46)

This change back-patches a v17-era fix.  It prevents possible hangs
in `CREATE DATABASE` and `DROP
DATABASE` due to failure to detect deadlocks.
- Avoid crashing with corrupt input data
in `contrib/pageinspect`'s
`heap_page_items()` (Dmitry Kovalenko)
[](2d33cf7b8)
- Prevent assertion failure
in `contrib/pg_freespacemap`'s
`pg_freespacemap()` (Tender Wang)
[](41ed749e4)

Applying `pg_freespacemap()` to a relation
lacking storage (such as a view) caused an assertion failure,
although there was no ill effect in non-assert builds.
Add an error check to reject that case.
- Fix build failure on macOS 15.4 (Tom Lane, Peter Eisentraut)
[](a39eb9c77)

This macOS update broke our configuration probe
for `strchrnul()`.
- Update time zone data files to tzdata
release 2025b for DST law changes in Chile, plus historical
corrections for Iran (Tom Lane)
[](e076120d9)

There is a new time zone America/Coyhaique for Chile's Aysén Region,
to account for it changing to UTC-03 year-round and thus diverging
from America/Santiago.

## Release 16.8

## Release date:

2025-02-20

This release contains a few fixes from 16.7.
For information about new features in major release 16, see
[release-16](#release-16).

### Migration to Version 16.8

A dump/restore is not required for those running 16.X.

However, if you are upgrading from a version earlier than 16.5,
see [release-16-5](#release-16-5).

### Changes

- Improve behavior of libpq's quoting
functions (Andres Freund, Tom Lane)
[](111f4dd27)
[](991a60a9f)
[](644b7d686)

The changes made for CVE-2025-1094 had one serious oversight:
`PQescapeLiteral()`
and `PQescapeIdentifier()` failed to honor their
string length parameter, instead always reading to the input
string's trailing null.  This resulted in including unwanted text in
the output, if the caller intended to truncate the string via the
length parameter.  With very bad luck it could cause a crash due to
reading off the end of memory.

In addition, modify all these quoting functions so that when invalid
encoding is detected, an invalid sequence is substituted for just
the first byte of the presumed character, not all of it.  This
reduces the risk of problems if a calling application performs
additional processing on the quoted string.
- Fix meson build system to correctly detect availability of
the `bsd_auth.h` system header
(Nazir Bilal Yavuz)
[](01cdb98e4)

## Release 16.7

## Release date:

2025-02-13

This release contains a variety of fixes from 16.6.
For information about new features in major release 16, see
[release-16](#release-16).

### Migration to Version 16.7

A dump/restore is not required for those running 16.X.

However, if you are upgrading from a version earlier than 16.5,
see [release-16-5](#release-16-5).

### Changes

- Harden `PQescapeString` and allied functions
against invalidly-encoded input strings (Andres Freund, Noah Misch)
[](92e4170f4)
[](6e05b195d)
[](56aa2dcdd)
[](01784793f)
[](41343f840)
[](0075a5c6c)

Data-quoting functions supplied by libpq
now fully check the encoding validity of their input.  If invalid
characters are detected, they report an error if possible.  For the
ones that lack an error return convention, the output string is
adjusted to ensure that the server will report invalid encoding and
no intervening processing will be fooled by bytes that might happen
to match single quote, backslash, etc.

The purpose of this change is to guard against SQL-injection attacks
that are possible if one of these functions is used to quote crafted
input.  There is no hazard when the resulting string is sent
directly to a PostgreSQL server (which
would check its encoding anyway), but there is a risk when it is
passed through psql or other client-side
code.  Historically such code has not carefully vetted encoding, and
in many cases it's not clear what it should do if it did detect such
a problem.

This fix is effective only if the data-quoting function, the server,
and any intermediate processing agree on the character encoding
that's being used.  Applications that insert untrusted input into
SQL commands should take special care to ensure that that's true.

Applications and drivers that quote untrusted input without using
these libpq functions may be at risk of
similar problems.  They should first confirm the data is valid in
the encoding expected by the server.

The PostgreSQL Project thanks
Stephen Fewer for reporting this problem.
(CVE-2025-1094)
- Exclude parallel workers from connection privilege checks and limits
(Tom Lane)
[](41a252c2c)

Do not
check `datallowconn`, `rolcanlogin`,
and `ACL_CONNECT` privileges when starting a
parallel worker, instead assuming that it's enough for the leader
process to have passed similar checks originally.  This avoids, for
example, unexpected failures of parallelized queries when the leader
is running as a role that lacks login privilege.  In the same vein,
enforce `ReservedConnections`,
`datconnlimit`, and `rolconnlimit`
limits only against regular backends, and count only regular
backends while checking if the limits were already reached.  Those
limits are meant to prevent excessive consumption of process slots
for regular backends --- but parallel workers and other special
processes have their own pools of process slots with their own limit
checks.
- Fix possible re-use of stale results in window aggregates (David
Rowley)
[](c1d6506ac)

A window aggregate with a "run condition" optimization
and a pass-by-reference result type might incorrectly return the
result from the previous partition instead of performing a fresh
calculation.
- Keep `TransactionXmin` in sync
with `MyProc->xmin` (Heikki Linnakangas)
[](9d8ab2c46)

This oversight could permit a process to try to access data that had
already been vacuumed away.  One known consequence is
transient "could not access status of transaction"
errors.
- Fix race condition that could cause failure to add a newly-inserted
catalog entry to a catalog cache list (Heikki Linnakangas)
[](91fc447c2)

This could result, for example, in failure to use a newly-created
function within an existing session.
- Prevent possible catalog corruption when a system catalog is
vacuumed concurrently with an update (Noah Misch)
[](9311fcb86)
- Fix data corruption when relation truncation fails (Thomas Munro)
[](ba02d24ba)
[](c957d7444)
[](9defaaa1d)

The filesystem calls needed to perform relation truncation could
fail, leaving inconsistent state on disk (for example, effectively
reviving deleted data).  We can't really prevent that, but we can
recover by dint of making such failures into PANICs, so that
consistency is restored by replaying from WAL up to just before the
attempted truncation.  This isn't a hugely desirable behavior, but
such failures are rare enough that it seems an acceptable solution.
- Prevent checkpoints from starting during relation truncation
(Robert Haas)
[](ad5aa7bfd)

This avoids a race condition wherein the modified file might not get
fsync'd before completing the checkpoint, creating a risk of data
corruption if the operating system crashes soon after.
- Avoid possibly losing an update of
`pg_database`.`datfrozenxid`
when `VACUUM` runs concurrently with
a `REASSIGN OWNED` that changes that database's
owner (Kirill Reshke)
[](5d94aa4dc)
- Fix incorrect `tg_updatedcols` values
passed to `AFTER UPDATE` triggers (Tom Lane)
[](8c57f5485)

In some cases the `tg_updatedcols` bitmap
could describe the set of columns updated by an earlier command in
the same transaction, fooling the trigger into doing the wrong
thing.

Also, prevent memory bloat caused by making too many copies of
the `tg_updatedcols` bitmap.
- Fix detach of a partition that has its own foreign-key constraint
referencing a partitioned table (Amul Sul)
[](ddab512eb)

In common cases, foreign keys are defined on a partitioned table's
top level; but if instead one is defined on a partition and
references a partitioned table, and the referencing partition is
detached, the relevant `pg_constraint`
entries were updated incorrectly.  This led to errors
like "could not find ON INSERT check triggers of foreign key
constraint".
- Fix mis-processing of `to_timestamp`'s
`FF`n`` format codes
(Tom Lane)
[](26c233b8b)

An integer format code immediately
preceding `FF`n`` would
consume all available digits, leaving none
for `FF`n``.
- When deparsing an `XMLTABLE()` expression, ensure
that XML namespace names are double-quoted when necessary (Dean
Rasheed)
[](77763f3be)
- Include the `ldapscheme` option
in `pg_hba_file_rules()` output (Laurenz Albe)
[](c35bbdfbc)
[](116036d81)
- Don't merge `UNION` operations if their column
collations aren't consistent (Tom Lane)
[](f286f64bc)

Previously we ignored collations when deciding if it's safe to
merge `UNION` steps into a single
N-way `UNION` operation.  This was arguably valid
before the introduction of nondeterministic collations, but it's not
anymore, since the collation in use can affect the definition of
uniqueness.
- Prevent "wrong varnullingrels" planner errors after
pulling up a subquery that's underneath an outer join (Tom Lane)
[](85990e2fd)
[](7b456f040)
- Ignore nulling-relation marker bits when looking up statistics
(Richard Guo)
[](a1a9120c7)

This oversight could lead to failure to use relevant statistics
about expressions, or to "corrupt MVNDistinct
entry" errors.
- Fix missed expression processing for partition pruning steps
(Tom Lane)
[](94c02bd33)

This oversight could lead to "unrecognized node type"
errors, and perhaps other problems, in queries accessing partitioned
tables.
- Allow dshash tables to grow past 1GB (Matthias van de Meent)
[](2a7402322)

This avoids errors like "invalid DSA memory alloc request
size".  The case can occur for example in transactions that
process several million tables.
- Avoid possible integer overflow
in `bringetbitmap()` (James Hunter, Evgeniy
Gorbanyov)
[](bfda7d8dd)

Since the result is only used for statistical purposes, the effects
of this error were mostly cosmetic.
- Ensure that an already-set process latch doesn't prevent the
postmaster from noticing socket events (Thomas Munro)
[](b4b52c911)

An extremely heavy workload of backends launching workers and
workers exiting could prevent the postmaster from responding to
incoming client connections in a timely fashion.
- Prevent streaming standby servers from looping infinitely when
reading a WAL record that crosses pages (Kyotaro Horiguchi,
Alexander Kukushkin)
[](2c2e1d4f4)

This would happen when the record's continuation is on a page that
needs to be read from a different WAL source.
- Fix unintended promotion of FATAL errors to PANIC during early
process startup (Noah Misch)
[](ac4a2b403)

This fixes some unlikely cases that would result in "PANIC:
proc_exit() called in child process".
- Fix cases where an operator family member operator or support
procedure could become a dangling reference (Tom Lane)
[](be5db08ed)
[](faad01835)

In some cases a data type could be dropped while references to its
OID still remain in `pg_amop`
or `pg_amproc`.  While that caused no
immediate issues, an attempt to drop the owning operator family
would fail, and pg_dump would produce
bogus output when dumping the operator family.  This fix causes
creation and modification of operator families/classes to add
needed dependency entries so that dropping a data type will also
drop any dependent operator family elements.  That does not help
vulnerable pre-existing operator families, though, so a band-aid has
also been added to `DROP OPERATOR FAMILY` to
prevent failure when dropping a family that has dangling members.
- Fix multiple memory leaks in logical decoding output (Vignesh C,
Masahiko Sawada, Boyu Yang)
[](e3a27fd06)
[](4d45e7490)
[](e749eaf46)
- Fix small memory leak when
updating the `application_name`
or `cluster_name` settings (Tofig Aliev)
[](be9dac9af)
- Avoid integer overflow while
testing `wal_skip_threshold` condition (Tom Lane)
[](f7a08b6e9)

A transaction that created a very large relation could mistakenly
decide to ensure durability by copying the relation into WAL instead
of fsync'ing it, thereby negating the point
of `wal_skip_threshold`.  (This only matters
when `wal_level` is set
to `minimal`, else a WAL copy is required anyway.)
- Fix unsafe order of operations during cache lookups (Noah Misch)
[](c1285bbeb)

The only known consequence was a usually-harmless "you don't
own a lock of type ExclusiveLock" warning
during `GRANT TABLESPACE`.
- Fix possible "failed to resolve name" failures when
using JIT on older ARM platforms (Thomas Munro)
[](6de14dbb3)

This could occur as a consequence of inconsistency about the default
setting of `-moutline-atomics` between gcc and clang.
At least Debian and Ubuntu are known to ship gcc and clang compilers
that target armv8-a but differ on the use of outline atomics by
default.
- Fix assertion failure in `WITH RECURSIVE ... UNION`
queries (David Rowley)
[](093fc156b)
- Avoid assertion failure in rule deparsing if a set operation leaf
query contains set operations (Man Zeng, Tom Lane)
[](fe084039e)
- Avoid edge-case assertion failure in parallel query startup (Tom Lane)
[](bb649b553)
- Fix assertion failure at shutdown when writing out the statistics
file (Michael Paquier)
[](ae77bcc3a)
- In `NULLIF()`, avoid passing a read-write
expanded object pointer to the data type's equality function
(Tom Lane)
[](4aba56adc)

The equality function could modify or delete the object if it's
given a read-write pointer, which would be bad if we decide to
return it as the `NULLIF()` result.  There is
probably no problem with any built-in equality function, but it's
easy to demonstrate a failure with one coded in PL/pgSQL.
- Ensure that expression preprocessing is applied to a default null
value in `INSERT` (Tom Lane)
[](6655d931c)

If the target column is of a domain type, the planner must insert a
coerce-to-domain step not just a null constant, and this expression
missed going through some required processing steps.  There is no
known consequence with domains based on core data types, but in
theory an error could occur with domains based on extension types.
- Repair memory leaks in PL/Python (Mat Arye, Tom Lane)
[](33a4e656d)

Repeated use of `PLyPlan.execute`
or `plpy.cursor` resulted in memory leakage for
the duration of the calling PL/Python function.
- Fix PL/Tcl to compile with Tcl 9 (Peter Eisentraut)
[](07c77803c)
- In the ecpg preprocessor, fix possible
misprocessing of cursors that reference out-of-scope variables
(Tom Lane)
[](cca34f68c)
- In ecpg, fix compile-time warnings about
unsupported use of `COPY ... FROM STDIN` (Ryo
Kanbayashi)
[](5c7c34db2)

Previously, the intended warning was not issued due to a typo.
- Fix psql to safely handle file path names
that are encoded in SJIS (Tom Lane)
[](998c4fc7c)

Some two-byte characters in SJIS have a second byte that is equal to
ASCII backslash (`\`).  These characters were
corrupted by path name normalization, preventing access to files
whose names include such characters.
- Fix use of wrong version of `pqsignal()`
in pgbench
and psql (Fujii Masao, Tom Lane)
[](b935691b8)

This error could lead to misbehavior when using
the `-T` option in pgbench
or the `\watch` command
in psql, due to interrupted system calls
not being resumed as expected.
- Fix misexecution of some nested `\if` constructs
in pgbench (Michail Nikolaev)
[](076b09123)

An `\if` command appearing within a false
(not-being-executed) `\if` branch was incorrectly
treated the same as `\elif`.
- In pgbench, fix possible misdisplay of
progress messages during table initialization (Yushi Ogiwara, Tatsuo
Ishii, Fujii Masao)
[](1cf646957)
[](21b815f92)
- Make pg_controldata more robust against
corrupted `pg_control` files (Ilyasov Ian, Anton
Voloshin)
[](d54d5668b)

Since pg_controldata will attempt to
print the contents of `pg_control` even if the
CRC check fails, it must take care not to misbehave for invalid
field values.  This patch fixes some issues triggered by invalid
timestamps and apparently-negative WAL segment sizes.
- Fix possible crash in pg_dump with
identity sequences attached to tables that are extension members
(Tom Lane)
[](782cc1aa3)
- Fix memory leak in pg_restore
with zstd-compressed data (Tom Lane)
[](8cfff087b)

The leak was per-decompression-operation, so would be most
noticeable with a dump containing many tables or large objects.
- Fix pg_basebackup to correctly
handle `pg_wal.tar` files exceeding 2GB on
Windows (Davinder Singh, Thomas Munro)
[](be7489662)
[](0bff6f1da)
- Use SQL-standard function bodies in the declarations
of `contrib/earthdistance`'s SQL-language
functions (Tom Lane, Ronan Dunklau)
[](31daa10fa)

This change allows their references
to `contrib/cube` to be resolved during extension
creation, reducing the risk of search-path-based failures and
possible attacks.

In particular, this restores their usability in contexts like
generated columns, for which PostgreSQL
v17 restricts the search path on security grounds.  We have received
reports of databases failing to be upgraded to v17 because of that.
This patch has been included in v16 to provide a workaround:
updating the `earthdistance` extension to this
version beforehand should allow an upgrade to succeed.
- Update configuration probes that determine the compiler switches
needed to access ARM CRC instructions (Tom Lane)
[](1f4aadec4)

On ARM platforms where the baseline CPU target lacks CRC
instructions, we need to supply a `-march` switch to
persuade the compiler to compile such instructions.  Recent versions
of gcc reject the value we were trying, leading to silently falling
back to software CRC.
- Fix meson build system to support old OpenSSL libraries on Windows
(Darek Slusarczyk)
[](60516fc8b)

Add support for the legacy library
names `ssleay32`
and `libeay32`.
- In Windows builds using meson, ensure all libcommon and libpgport
functions are exported (Vladlen Popolitov, Heikki Linnakangas)
[](4e0d71ff2)
[](643efb18b)

This fixes "unresolved external symbol" build errors
for extensions.
- Fix meson configuration process to correctly detect
OSSP's `uuid.h` header file under MSVC
(Andrew Dunstan)
[](1250adfdf)
- When building with meson, install `pgevent`
in `pkglibdir`
not `bindir` (Peter Eisentraut)
[](766b0b40a)

This matches the behavior of the make-based build system and the old
MSVC build system.
- When building with meson, install `sepgsql.sql`
under `share/contrib/`
not `share/extension/` (Peter Eisentraut)
[](155d6162e)

This matches what the make-based build system does.
- Update time zone data files to tzdata
release 2025a for DST law changes in Paraguay, plus historical
corrections for the Philippines (Tom Lane)
[](d62403c51)

## Release 16.6

## Release date:

2024-11-21

This release contains a few fixes from 16.5.
For information about new features in major release 16, see
[release-16](#release-16).

### Migration to Version 16.6

A dump/restore is not required for those running 16.X.

However, if you are upgrading from a version earlier than 16.5,
see [release-16-5](#release-16-5).

### Changes

- Repair ABI break for extensions that work with
struct `ResultRelInfo` (Tom Lane)
[](ee33d5847)

Last week's minor releases unintentionally broke binary
compatibility with timescaledb and
several other extensions.  Restore the affected structure to its
previous size, so that such extensions need not be rebuilt.
- Restore functionality of `ALTER {ROLE|DATABASE} SET
role` (Tom Lane, Noah Misch)
[](b0918c128)

The fix for CVE-2024-10978 accidentally caused settings
for `role` to not be applied if they come from
non-interactive sources, including previous `ALTER
{ROLE|DATABASE}` commands and
the `PGOPTIONS` environment variable.
- Fix cases where a logical replication
slot's `restart_lsn` could go backwards
(Masahiko Sawada)
[](f35391133)

Previously, restarting logical replication could sometimes cause the
slot's restart point to be recomputed as an older value than had
previously been advertised
in `pg_replication_slots`.  This is bad,
since for example WAL files might have been removed on the basis of
the later `restart_lsn` value, in which
case replication would fail to restart.
- Avoid deleting still-needed WAL files
during pg_rewind
(Polina Bungina, Alexander Kukushkin)
[](ea1649c35)

Previously, in unlucky cases, it was possible
for pg_rewind to remove important WAL
files from the rewound demoted primary.  In particular this happens
if those files have been marked for archival (i.e.,
their `.ready` files were created) but not yet
archived.  Then the newly promoted node no longer has such files
because of them having been recycled, but likely they are needed
for recovery in the demoted node.
If pg_rewind removes them, recovery is
not possible anymore.
- Fix race conditions associated with dropping shared statistics
entries (Kyotaro Horiguchi, Michael Paquier)
[](afa20845d)

These bugs could lead to loss of statistics data, assertion
failures, or "can only drop stats once" errors.
- Count index scans in `contrib/bloom` indexes in
the statistics views, such as the
`pg_stat_user_indexes`.`idx_scan`
counter (Masahiro Ikeda)
[](05aac2e83)
- Fix crash when checking to see if an index's opclass options have
changed (Alexander Korotkov)
[](b242aba02)

Some forms of `ALTER TABLE` would fail if the
table has an index with non-default operator class options.
- Avoid assertion failure caused by disconnected NFA sub-graphs in
regular expression parsing (Tom Lane)
[](b6312becc)

This bug does not appear to have any visible consequences in
non-assert builds.

## Release 16.5

## Release date:

2024-11-14

This release contains a variety of fixes from 16.4.
For information about new features in major release 16, see
[release-16](#release-16).

### Migration to Version 16.5

A dump/restore is not required for those running 16.X.

However, if you have ever detached a partition from a partitioned
table that has a foreign-key reference to another partitioned table,
and not dropped the former partition, then you may have catalog and/or
data corruption to repair, as detailed in the fifth changelog entry
below.

Also, if you are upgrading from a version earlier than 16.3,
see [release-16-3](#release-16-3).

### Changes

- Ensure cached plans are marked as dependent on the calling role when
RLS applies to a non-top-level table reference (Nathan Bossart)
[](562289460)

If a CTE, subquery, sublink, security invoker view, or coercion
projection in a query references a table with row-level security
policies, we neglected to mark the resulting plan as potentially
dependent on which role is executing it.  This could lead to later
query executions in the same session using the wrong plan, and then
returning or hiding rows that should have been hidden or returned
instead.

The PostgreSQL Project thanks
Wolfgang Walther for reporting this problem.
(CVE-2024-10976)
- Make libpq discard error messages
received during SSL or GSS protocol negotiation (Jacob Champion)
[](67d28bd02)

An error message received before encryption negotiation is completed
might have been injected by a man-in-the-middle, rather than being
real server output.  Reporting it opens the door to various security
hazards; for example, the message might spoof a query result that a
careless user could mistake for correct output.  The best answer
seems to be to discard such data and rely only
on libpq's own report of the connection
failure.

The PostgreSQL Project thanks
Jacob Champion for reporting this problem.
(CVE-2024-10977)
- Fix unintended interactions between `SET SESSION
AUTHORIZATION` and `SET ROLE` (Tom Lane)
[](ae340d031)
[](95f5a5237)

The SQL standard mandates that `SET SESSION
AUTHORIZATION` have a side-effect of doing `SET
ROLE NONE`.  Our implementation of that was flawed,
creating more interaction between the two settings than intended.
Notably, rolling back a transaction that had done `SET
SESSION AUTHORIZATION` would revert `ROLE`
to `NONE` even if that had not been the previous
state, so that the effective user ID might now be different from
what it had been before the transaction.  Transiently
setting `session_authorization` in a
function `SET` clause had a similar effect.
A related bug was that if a parallel worker
inspected `current_setting('role')`, it
saw `none` even when it should see something else.

The PostgreSQL Project thanks
Tom Lane for reporting this problem.
(CVE-2024-10978)
- Prevent trusted PL/Perl code from changing environment variables
(Andrew Dunstan, Noah Misch)
[](8fe3e697a)
[](88269df4d)
[](168579e23)
[](c335264c9)
[](64df88700)

The ability to manipulate process environment variables such
as `PATH` gives an attacker opportunities to
execute arbitrary code.  Therefore, "trusted" PLs must
not offer the ability to do that.  To fix `plperl`,
replace `%ENV` with a tied hash that rejects any
modification attempt with a warning.
Untrusted `plperlu` retains the ability to change
the environment.

The PostgreSQL Project thanks
Coby Abrams for reporting this problem.
(CVE-2024-10979)
- Fix updates of catalog state for foreign-key constraints when
attaching or detaching table partitions (Jehan-Guillaume de
Rorthais, Tender Wang, Álvaro Herrera)
[](2aaf2a28b)
[](f7d510a38)

If the referenced table is partitioned, then different catalog
entries are needed for a referencing table that is stand-alone
versus one that is a partition.  `ATTACH/DETACH
PARTITION` commands failed to perform this conversion
correctly.  In particular, after `DETACH` the now
stand-alone table would be missing foreign-key enforcement triggers,
which could result in the table later containing rows that fail the
foreign-key constraint.  A subsequent re-`ATTACH`
could fail with surprising errors, too.

The way to fix this is to do `ALTER TABLE DROP
CONSTRAINT` on the now stand-alone table for each faulty
constraint, and then re-add the constraint.  If re-adding the
constraint fails, then some erroneous data has crept in.  You will
need to manually re-establish consistency between the referencing
and referenced tables, then re-add the constraint.

This query can be used to identify broken constraints and construct
the commands needed to recreate them:

```
SELECT conrelid::pg_catalog.regclass AS "constrained table",
conname AS constraint,
confrelid::pg_catalog.regclass AS "references",
pg_catalog.format('ALTER TABLE %s DROP CONSTRAINT %I;',
conrelid::pg_catalog.regclass, conname) AS "drop",
pg_catalog.format('ALTER TABLE %s ADD CONSTRAINT %I %s;',
conrelid::pg_catalog.regclass, conname,
pg_catalog.pg_get_constraintdef(oid)) AS "add"
FROM pg_catalog.pg_constraint c
WHERE contype = 'f' AND conparentid = 0 AND
(SELECT count(*) FROM pg_catalog.pg_constraint c2
WHERE c2.conparentid = c.oid) <>
((SELECT count(*) FROM pg_catalog.pg_inherits i
WHERE (i.inhparent = c.conrelid OR i.inhparent = c.confrelid) AND
EXISTS (SELECT 1 FROM pg_catalog.pg_partitioned_table
WHERE partrelid = i.inhparent)) +
CASE WHEN pg_catalog.pg_partition_root(conrelid) = confrelid THEN
(SELECT count(*) FROM pg_catalog.pg_partition_tree(confrelid)
WHERE level = 1)
ELSE 0 END);
```

Since it is possible that one or more of the `ADD
CONSTRAINT` steps will fail, you should save the query's
output in a file and then attempt to perform each step.
- Avoid possible crashes and "could not open relation"
errors in queries on a partitioned table occurring concurrently with
a `DETACH CONCURRENTLY` and immediate drop of a
partition (Álvaro Herrera, Kuntal Gosh)
[](a6ff329e7)
[](1b9dd6b05)
- Disallow `ALTER TABLE ATTACH PARTITION` if the
table to be attached has a foreign key referencing the partitioned
table (Álvaro Herrera)
[](ada34d714)
[](57c8b8726)

This arrangement is not supported, and other ways of creating it
already fail.
- Don't use partitionwise joins or grouping if the query's collation
for the key column doesn't match the partition key's collation (Jian
He, Webbo Han)
[](f734b6b4d)
[](dd2f8ebee)

Such plans could produce incorrect results.
- Fix possible "could not find pathkey item to sort"
error when the output of a `UNION ALL` member query
needs to be sorted, and the sort column is an expression (Andrei
Lepikhov, Tom Lane)
[](64635c8af)
- Fix performance regressions involving flattening of subqueries
underneath outer joins that are later reduced to plain joins
(Tom Lane)
[](80d9c07a4)

v16 failed to optimize some queries as well as prior versions had,
because of overoptimistic simplification of query-pullup logic.
- Allow cancellation of the second stage of index build for large hash
indexes (Pavel Borisov)
[](d23109f4b)
- Fix assertion failure or confusing error message for `COPY
(`query`) TO ...`, when
the `query` is rewritten by a `DO
INSTEAD NOTIFY` rule (Tender Wang, Tom Lane)
[](6c3b2d204)
- Fix server crash when a `json_objectagg()` call
contains a volatile function (Amit Langote)
[](fa4f11854)
- Fix checking of key uniqueness in JSON object constructors
(Junwang Zhao, Tomas Vondra)
[](8e65d9ff9)

When building an object larger than a kilobyte, it was possible to
accept invalid input that includes duplicate object keys, or to
falsely report that duplicate keys are present.
- Fix detection of skewed data during parallel hash join (Thomas
Munro)
[](53edc9485)

After repartitioning the inner side of a hash join because one
partition has accumulated too many tuples, we check to see if all
the partition's tuples went into the same child partition, which
suggests that they all have the same hash value and further
repartitioning cannot improve matters.  This check malfunctioned in
some cases, allowing repeated futile repartitioning which would
eventually end in a resource-exhaustion error.
- Disallow locale names containing non-ASCII characters (Thomas Munro)
[](ce17de580)

This is only an issue on Windows, as such locale names are not used
elsewhere.  They are problematic because it's quite unclear what
encoding such names are represented in (since the locale itself
defines the encoding to use).  In
recent PostgreSQL releases, an abort in
the Windows runtime library could occur because of confusion about
that.

Anyone who encounters the new error message should either create a
new duplicated locale with an ASCII-only name using Windows Locale
Builder, or consider using BCP 47-compliant locale names
like `tr-TR`.
- Fix race condition in committing a serializable transaction (Heikki
Linnakangas)
[](22665f210)

Mis-processing of a recently committed transaction could lead to an
assertion failure or a "could not access status of
transaction" error.
- Fix race condition in `COMMIT PREPARED`
that resulted in orphaned 2PC files (wuchengwen)
[](7de9b64a5)

A concurrent `PREPARE TRANSACTION` could
cause `COMMIT PREPARED` to not remove the on-disk
two-phase state file for the completed transaction.  There was no
immediate ill effect, but a subsequent crash-and-recovery could fail
with "could not access status of transaction",
requiring manual removal of the orphaned file to restore service.
- Avoid invalid memory accesses after skipping an invalid toast index
during `VACUUM FULL` (Tender Wang)
[](afbd3dc7d)

A list tracking yet-to-be-rebuilt indexes was not properly updated
in this code path, risking assertion failures or crashes later on.
- Fix ways in which an "in place" catalog update could be
lost (Noah Misch)
[](63f019805)
[](51ff46de2)
[](4c922821e)
[](2d63c964f)
[](370bc7740)
[](6c837c237)
[](f8f9110b4)

Normal row updates write a new version of the row to preserve
rollback-ability of the transaction.  However, certain system
catalog updates are intentionally non-transactional and are done
with an in-place update of the row.  These patches fix race
conditions that could cause the effects of an in-place update to be
lost.  As an example, it was possible to forget having set
`pg_class`.`relhasindex`
to true, preventing updates of the new index and thus causing index
corruption.
- Reset catalog caches at end of recovery (Noah Misch)
[](d36b4d8ec)

This prevents scenarios wherein an in-place catalog update could be
lost due to using stale data from a catalog cache.
- Avoid using parallel query while holding off interrupts
(Francesco Degrassi, Noah Misch, Tom Lane)
[](6f6521de9)
[](06424e9a2)

This situation cannot arise normally, but it can be reached with
test scenarios such as using a SQL-language function as B-tree
support (which would be far too slow for production usage).  If it
did occur it would result in an indefinite wait.
- Report the active query ID for statistics purposes at the start of
processing of Bind and Execute protocol messages (Sami Imseih)
[](21aad4bea)

This allows more of the work done in extended query protocol to be
attributed to the correct query.
- Guard against stack overflow in libxml2
with too-deeply-nested XML input (Tom Lane, with hat tip to Nick
Wellnhofer)
[](4c9bf947a)

Use `xmlXPathCtxtCompile()` rather
than `xmlXPathCompile()`, because the latter
fails to protect itself against recursion-to-stack-overflow
in libxml2 releases before 2.13.4.
- Fix some whitespace issues in the result
of `XMLSERIALIZE(... INDENT)` (Jim Jones)
[](06c285018)

Fix failure to indent nodes separated by whitespace, and ensure that
a trailing newline is not added.
- Do not ignore a concurrent `REINDEX CONCURRENTLY`
that is working on an index with predicates or expressions (Michail
Nikolaev)
[](edb0f6e41)

Normally, `REINDEX CONCURRENTLY` does not need to
wait for other `REINDEX CONCURRENTLY` operations on
other tables.  However, this optimization is not applied if the
other `REINDEX CONCURRENTLY` is processing an index
with predicates or expressions, on the chance that such expressions
contain user-defined code that accesses other tables.  Careless
coding created a race condition such that that rule was not applied
uniformly, possibly allowing inconsistent behavior.
- Fix mis-deparsing of `ORDER BY` lists when there is
a name conflict (Tom Lane)
[](9fe6319dc)

If an `ORDER BY` item in `SELECT`
is a bare identifier, the parser first seeks it as an output column
name of the `SELECT`, for SQL92 compatibility.
However, ruleutils.c expects the SQL99 interpretation where such a
name is an input column name.  So it was possible to produce an
incorrect display of a view in the (rather ill-advised) case where
some other column is renamed in the `SELECT` output
list to match an input column used in `ORDER BY`.
Fix by table-qualifying such names in the dumped view text.
- Fix "failed to find plan for subquery/CTE" errors
in `EXPLAIN` (Richard Guo, Tom Lane)
[](9db6650a5)
[](03f679475)

This case arose while trying to print references to fields of a
RECORD-type output of a subquery when the subquery has been
optimized out of the plan altogether (which is possible at least in
the case that it has a constant-false `WHERE`
condition).  Nothing remains in the plan to identify the original
field names, so fall back to
printing `f`N`` for
the `N`'th record column.  (That's actually
the right thing anyway, if the record output arose from
a `ROW()` constructor.)
- Disallow a `USING` clause when altering the type of
a generated column (Peter Eisentraut)
[](5867ee005)

A generated column already has an expression specifying the column
contents, so including `USING` doesn't make sense.
- Ignore not-yet-defined Portals in
the `pg_cursors` view (Tom Lane)
[](5de77b609)

It is possible for user-defined code that inspects this view to be
called while a new cursor is being set up, and if that happens a
null pointer dereference would ensue.  Avoid the problem by defining
the view to exclude incompletely-set-up cursors.
- Fix incorrect output of the `pg_stat_io` view
on 32-bit machines (Bertrand Drouvot)
[](dd20f950d)

The `stats_reset` timestamp column
contained garbage on such hardware.
- Prevent mis-encoding of "trailing junk after numeric
literal" error messages (Karina Litskevich)
[](4fd4d7653)

We do not allow identifiers to appear immediately following numeric
literals (there must be some whitespace between).  If a multibyte
character immediately followed a numeric literal, the syntax error
message about it included only the first byte of that character,
causing bad-encoding problems both in the report to the client and
in the postmaster log file.
- Avoid "unexpected table_index_fetch_tuple call during logical
decoding" error while decoding a transaction involving
insertion of a column default value (Takeshi Ideriha, Hou Zhijie)
[](0f0e253db)
[](0c40d9019)
- Reduce memory consumption of logical decoding (Masahiko Sawada)
[](05e982cdc)

Use a smaller default block size to store tuple data received during
logical replication.  This reduces memory wastage, which has been
reported to be severe while processing long-running transactions,
even leading to out-of-memory failures.
- In a logical replication apply worker, ensure that origin progress
is not advanced during an error or apply worker shutdown (Hayato
Kuroda, Shveta Malik)
[](b39c5272c)

This avoids possible loss of a transaction, since once the origin
progress point is advanced the source server won't send that data
again.
- Re-disable sending of stateless (TLSv1.2) session tickets
(Daniel Gustafsson)
[](9333174af)

A previous change to prevent sending of stateful (TLSv1.3) session
tickets accidentally re-enabled sending of stateless ones.  Thus,
while we intended to prevent clients from thinking that TLS session
resumption is supported, some still did.
- Avoid "wrong tuple length" failure when dropping a
database with many ACL (permission) entries (Ayush Tiwari)
[](545794515)
[](f6991cafa)
- Allow adjusting the `session_authorization`
and `role` settings in parallel workers (Tom Lane)
[](f3ab5d3a2)

Our code intends to allow modifiable server settings to be set by
function `SET` clauses, but not otherwise within a
parallel worker.  `SET` clauses failed for these
two settings, though.
- Fix behavior of stable functions called from
a `CALL` statement's argument list, when
the `CALL` is within a
PL/pgSQL `EXCEPTION` block (Tom Lane)
[](25d639eea)

As with a similar fix in our previous quarterly releases, this case
allowed such functions to be passed the wrong snapshot, causing them
to see stale values of rows modified since the start of the outer
transaction.
- Fix "cache lookup failed for function" errors in edge
cases in PL/pgSQL's `CALL` (Tom Lane)
[](a073835c1)
- Fix thread safety of our fallback (non-OpenSSL) MD5 implementation
on big-endian hardware (Heikki Linnakangas)
[](0583863e9)

Thread safety is not currently a concern in the server, but it is
for libpq.
- Parse libpq's `keepalives`
connection option in the same way as other integer-valued options
(Yuto Sasaki)
[](65f431aff)

The coding used here rejected trailing whitespace in the option
value, unlike other cases.  This turns out to be problematic
in ecpg's usage, for example.
- Avoid use of `pnstrdup()`
in ecpglib (Jacob Champion)
[](ee2997c67)

That function will call `exit()` on
out-of-memory, which is undesirable in a library.  The calling code
already handles allocation failures properly.
- In ecpglib, fix out-of-bounds read when
parsing incorrect datetime input (Bruce Momjian, Pavel Nekrasov)
[](a1e613b81)

It was possible to try to read the location just before the start of
a constant array.  Real-world consequences seem minimal, though.
- Fix memory leak in psql during repeated
use of `\bind` (Michael Paquier)
[](c2fb2f9e2)
- Avoid hanging if an interval less than 1ms is specified
in psql's `\watch`
command (Andrey Borodin, Michael Paquier)
[](6331972c7)

Instead, treat this the same as an interval of zero (no wait between
executions).
- Fix pg_dump's handling of identity
sequences that have persistence different from their owning table's
persistence (Tom Lane)
[](b8b175a4c)

Since v15, it's been possible to set an identity sequence to be
LOGGED when its owning table is UNLOGGED or vice versa.
However, pg_dump's method for recreating
that situation failed in binary-upgrade mode,
causing pg_upgrade to fail when such
sequences are present.  Fix by introducing a new option
for `ADD/ALTER COLUMN GENERATED AS IDENTITY` to
allow the sequence's persistence to be set correctly at creation.
Note that this means a dump from a database containing such a
sequence will only load into a server of this minor version or
newer.
- Include the source timeline history
in pg_rewind's debug output
(Heikki Linnakangas)
[](e8240dbd8)

This was the intention to begin with, but a coding error caused the
source history to always print as empty.
- Avoid trying to reindex temporary tables and indexes
in vacuumdb and in
parallel reindexdb (VaibhaveS, Michael
Paquier, Fujii Masao, Nathan Bossart)
[](1ea4d9c00)
[](653ce5b8b)
[](eba8cc1af)

Reindexing other sessions' temporary tables cannot work, but the
check to skip them was missing in some code paths, leading to
unwanted failures.
- Allow inspection of sequence relations in relevant functions
of `contrib/pageinspect`
and `contrib/pgstattuple` (Nathan Bossart, Ayush
Vatsa)
[](2bd4c06bb)
[](0938a4ecd)

This had been allowed in the past, but it got broken during the
introduction of non-default access methods for tables.
- Fix incorrect LLVM-generated code on ARM64 platforms (Thomas
Munro, Anthonin Bonnefoy)
[](ee67b73f5)

When using JIT compilation on ARM platforms, the generated code
could not support relocation distances exceeding 32 bits, allowing
unlucky placement of generated code to cause server crashes on
large-memory systems.
- Fix a few places that assumed that process start time (represented
as a `time_t`) will fit into a `long` value
(Max Johnson, Nathan Bossart)
[](8aaf88b63)

On platforms where `long` is 32 bits (notably Windows),
this coding would fail after Y2038.  Most of the failures appear
only cosmetic, but notably `pg_ctl start` would
hang.
- Fix building with Strawberry Perl on Windows (Andrew Dunstan)
[](0a0db4631)
- Update time zone data files to tzdata
release 2024b (Tom Lane)
[](a0c8d600b)
[](2abc88958)

This tzdata release changes the old
System-V-compatibility zone names to duplicate the corresponding
geographic zones; for example `PST8PDT` is now an
alias for `America/Los_Angeles`.  The main visible
consequence is that for timestamps before the introduction of
standardized time zones, the zone is considered to represent local
mean solar time for the named location.  For example,
in `PST8PDT`, `timestamptz` input such
as `1801-01-01 00:00` would previously have been
rendered as `1801-01-01 00:00:00-08`, but now it is
rendered as `1801-01-01 00:00:00-07:52:58`.

Also, historical corrections for Mexico, Mongolia, and Portugal.
Notably, `Asia/Choibalsan` is now an alias
for `Asia/Ulaanbaatar` rather than being a separate
zone, mainly because the differences between those zones were found to
be based on untrustworthy data.

## Release 16.4

## Release date:

2024-08-08

This release contains a variety of fixes from 16.3.
For information about new features in major release 16, see
[release-16](#release-16).

### Migration to Version 16.4

A dump/restore is not required for those running 16.X.

However, if you are upgrading from a version earlier than 16.3,
see [release-16-3](#release-16-3).

### Changes

- Prevent unauthorized code execution
during pg_dump (Masahiko Sawada)
[](6aba85a4b)

An attacker able to create and drop non-temporary objects could
inject SQL code that would be executed by a
concurrent pg_dump session with the
privileges of the role running pg_dump
(which is often a superuser).  The attack involves replacing a
sequence or similar object with a view or foreign table that will
execute malicious code.  To prevent this, introduce a new server
parameter `restrict_nonsystem_relation_kind` that
can disable expansion of non-builtin views as well as access to
foreign tables, and teach pg_dump to set
it when available.  Note that the attack is prevented only if
both pg_dump and the server it is dumping
from are new enough to have this fix.

The PostgreSQL Project thanks
Noah Misch for reporting this problem.
(CVE-2024-7348)
- Avoid incorrect results from Merge Right Anti Join plans
(Richard Guo)
[](507f2347e)

If the inner relation is known to have unique join keys, the merge
could misbehave when there are duplicated join keys in the outer
relation.
- Prevent infinite loop in `VACUUM`
(Melanie Plageman)
[](06bf404cd)

After a disconnected standby server with an old running transaction
reconnected to the primary, it was possible
for `VACUUM` on the primary to get confused about
which tuples are removable, resulting in an infinite loop.
- Fix failure after attaching a table as a partition, if the
table had previously had inheritance children
(lvaro Herrera)
[](084814d88)
- Fix `ALTER TABLE DETACH PARTITION` for cases
involving inconsistent index-based constraints
(lvaro Herrera, Tender Wang)
[](00a40e33c)
[](34eb37f79)

When a partitioned table has an index that is not associated with a
constraint, but a partition has an equivalent index that is, then
detaching the partition would misbehave, leaving the ex-partition's
constraint with an incorrect `coninhcount`
value.  This would cause trouble during any further manipulations of
that constraint.
- Fix partition pruning setup during `ALTER TABLE DETACH
PARTITION CONCURRENTLY` (lvaro Herrera)
[](96105ebfe)
[](bf78abebf)

The executor assumed that no partition could be detached between
planning and execution of a query on a partitioned table.  This is
no longer true since the introduction of `DETACH
PARTITION`'s `CONCURRENTLY` option, making
it possible for query execution to fail transiently when that is
used.
- Correctly update a partitioned table's
`pg_class`.`reltuples`
field to zero after its last child partition is dropped (Noah Misch)
[](e81deeefc)

The first `ANALYZE` on such a partitioned table
must update `relhassubclass` as well, and
that caused the `reltuples` update to be
lost.
- Fix handling of polymorphic output arguments for procedures
(Tom Lane)
[](8e0e99972)
[](bb331af4a)

The SQL `CALL` statement did not resolve the
correct data types for such arguments, leading to errors such
as "cannot display a value of type anyelement", or even
outright crashes.  (But `CALL`
in PL/pgSQL worked correctly.)
- Fix behavior of stable functions called from
a `CALL` statement's argument list (Tom Lane)
[](0d18b8eb4)

If the `CALL` is within an atomic context
(e.g. there's an outer transaction block), such functions were
passed the wrong snapshot, causing them to see stale values of rows
modified since the start of the outer transaction.
- Fix input of ISO-8601 "extended" time format for
types `time` and `timetz` (Tom Lane)
[](019ea7675)

Re-allow cases such as `T12:34:56`.
- Detect integer overflow in `money` calculations
(Joseph Koshakow)
[](34e9dce69)

None of the arithmetic functions for the `money` type
checked for overflow before, so they would silently give wrong
answers for overflowing cases.
- Fix over-aggressive clamping of the scale argument
in `round(numeric)`
and `trunc(numeric)` (Dean Rasheed)
[](f7aec8c1d)

These functions clamped their scale argument to +/-2000, but there
are valid use-cases for it to be larger; the functions returned
incorrect results in such cases.  Instead clamp to the actual
allowed range of type `numeric`.
- Fix result for `pg_size_pretty()` when applied to
the smallest possible `bigint` value (Joseph Koshakow)
[](6f6b0f193)
- Prevent `pg_sequence_last_value()` from failing
on unlogged sequences on standby servers and on temporary sequences
of other sessions (Nathan Bossart)
[](c1664c8ee)

Make it return NULL in these cases instead of throwing an error.
- Fix parsing of ignored operators
in `websearch_to_tsquery()` (Tom Lane)
[](086ecd12b)

Per the manual, punctuation in the input
of `websearch_to_tsquery()` is ignored except for
the special cases of dashes and quotes.  However, parentheses and a
few other characters appearing immediately before
an `or` could cause `or` to be
treated as a data word, rather than as an `OR`
operator as expected.
- Detect another integer overflow case while computing new array
dimensions (Joseph Koshakow)
[](a57d16865)

Reject applying array
dimensions `[-2147483648:2147483647]` to an empty
array.  This is closely related to CVE-2023-5869, but appears
harmless since the array still ends up empty.
- Fix unportable usage of `strnxfrm()` (Jeff Davis)
[](403cbd210)

Some code paths for non-deterministic collations could fail with
errors like "pg_strnxfrm() returned unexpected result".
- Detect another case of a new catalog cache entry becoming stale
while detoasting its fields (Noah Misch)
[](e4afd7153)

An in-place update occurring while we expand out-of-line fields in a
catalog tuple could be missed, leading to a catalog cache entry that
lacks the in-place change but is not known to be stale.  This is
only possible in the `pg_database` catalog,
so the effects are narrow, but misbehavior is possible.
- Correctly check updatability of view columns targeted
by `INSERT` ... `DEFAULT`
(Tom Lane)
[](fd958bbbd)

If such a column is non-updatable, we should give an error reporting
that.  But the check was missed and then later code would report an
unhelpful error such as "attribute
number `N` not found in view
targetlist".
- Avoid reporting an unhelpful internal error for incorrect recursive
queries (Tom Lane)
[](8fc487614)

Rearrange the order of error checks so that we throw an on-point
error when a `WITH RECURSIVE` query does not have a
self-reference within the second arm of
the `UNION`, but does have one self-reference in
some other place such as `ORDER BY`.
- Lock owned sequences during `ALTER TABLE SET
LOGGED|UNLOGGED` (Noah Misch)
[](112d05570)

These commands change the persistence of a table's owned sequences
along with the table, but they failed to acquire lock on the
sequences while doing so.  This could result in losing the effects
of concurrent `nextval()` calls.
- Don't throw an error if a queued `AFTER` trigger no
longer exists (Tom Lane)
[](4f1966676)

It's possible for a transaction to execute an operation that queues
a deferred `AFTER` trigger for later execution, and
then to drop the trigger before that happens.  Formerly this led to
weird errors such as "could not find
trigger `NNNN`".  It seems better to
silently do nothing if the trigger no longer exists at the time when
it would have been executed.
- Fix failure to remove `pg_init_privs` entries
for column-level privileges when their table is dropped (Tom Lane)
[](9cf4beb9e)

If an extension grants some column-level privileges on a table it
creates, relevant catalog entries would remain behind after the
extension is dropped.  This was harmless until/unless the table's
OID was re-used for another relation, when it could interfere with
what pg_dump dumps for that relation.
- Fix selection of an arbiter index for `ON CONFLICT`
when the desired index has expressions or predicates (Tom Lane)
[](b188e1bf7)

If a query using `ON CONFLICT` accesses the target
table through an updatable view, it could fail with "there is
no unique or exclusion constraint matching the ON CONFLICT
specification", even though a matching index does exist.
- Refuse to modify a temporary table of another session
with `ALTER TABLE` (Tom Lane)
[](8397f161e)

Permissions checks normally would prevent this case from arising,
but it is possible to reach it by altering a parent table whose
child is another session's temporary table.  Throw an error if we
discover that such a child table belongs to another session.
- Fix handling of extended statistics on expressions
in `CREATE TABLE LIKE STATISTICS` (Tom Lane)
[](2aa90c02d)

The `CREATE` command failed to adjust column
references in statistics expressions to the possibly-different
column numbering of the new table.  This resulted in invalid
statistics objects that would cause problems later.  A typical
scenario where renumbering columns is needed is when the source
table contains some dropped columns.
- Fix failure to recalculate sub-queries generated
from `MIN()` or `MAX()`
aggregates (Tom Lane)
[](ce0d16544)

In some cases the aggregate result computed at one row of the outer
query could be re-used for later rows when it should not be.  This
has only been seen to happen when the outer query uses
`DISTINCT` that is implemented with hash
aggregation, but other cases may exist.
- Re-forbid underscore in positional parameters (Erik Wienhold)
[](315661eca)

As of v16 we allow integer literals to contain underscores.
This change caused input such as `$1_234`
to be taken as a single token, but it did not work correctly.
It seems better to revert to the original definition in which a
parameter symbol is only `$` followed by digits.
- Avoid crashing when a JIT-inlined backend function throws an error
(Tom Lane)
[](07d66d3cc)

The error state can include pointers into the dynamically loaded
module holding the JIT-compiled code (for error location strings).
In some code paths the module could get unloaded before the error
report is processed, leading to SIGSEGV when the location strings
are accessed.
- Cope with behavioral changes in libxml2
version 2.13.x (Erik Wienhold, Tom Lane)
[](f85c91a18)

Notably, we now suppress "chunk is not well balanced"
errors from libxml2, unless that is the
only reported error.  This is to make error reports consistent
between 2.13.x and earlier libxml2
versions.  In earlier versions, that message was almost always
redundant or outright incorrect, so 2.13.x substantially reduced the
number of cases in which it's reported.
- Fix handling of subtransactions of prepared transactions
when starting a hot standby server (Heikki Linnakangas)
[](b5b418b68)

When starting a standby's replay at a shutdown checkpoint WAL
record, transactions that had been prepared but not yet committed on
the primary are correctly understood as being still in progress.
But subtransactions of a prepared transaction (created by savepoints
or PL/pgSQL exception blocks) were not
accounted for and would be treated as aborted.  That led to
inconsistency if the prepared transaction was later committed.
- Prevent incorrect initialization of logical replication slots
(Masahiko Sawada)
[](2f3304ce1)

In some cases a replication slot's start point within the WAL stream
could be set to a point within a transaction, leading to assertion
failures or incorrect decoding results.
- Avoid "can only drop stats once" error during
replication slot creation and drop (Floris Van Nee)
[](f2c922ff2)
- Fix resource leakage in logical replication WAL sender (Hou Zhijie)
[](b8f953d8d)

The walsender process leaked memory when publishing changes to a
partitioned table whose partitions have row types physically
different from the partitioned table's.
- Avoid memory leakage after servicing a notify or sinval interrupt
(Tom Lane)
[](54a7b21b3)

The processing functions for these events could switch the current
memory context to TopMemoryContext, resulting in session-lifespan
leakage of any data allocated before the incorrect setting gets
replaced.  There were observable leaks associated with (at least)
encoding conversion of incoming queries and parameters attached to
Bind messages.
- Prevent leakage of reference counts for the shared memory block used
for statistics (Anthonin Bonnefoy)
[](6f61d0e7e)

A new backend process attaching to the statistics shared memory
incremented its reference count, but failed to decrement the count
when exiting.  After 2^32 sessions had
been created, the reference count would overflow to zero, causing
failures in all subsequent backend process starts.
- Prevent deadlocks and assertion failures during truncation of the
multixact SLRU log (Heikki Linnakangas)
[](e7cbe5a85)

A process trying to delete SLRU segments could deadlock with the
checkpointer process.
- Avoid possibly missing end-of-input events on Windows sockets
(Thomas Munro)
[](a622095bc)

Windows reports an FD_CLOSE event only once after the remote end of
the connection disconnects.  With unlucky timing, we could miss that
report and wait indefinitely, or at least until a timeout elapsed,
expecting more input.
- Fix buffer overread in JSON parse error reports for incomplete byte
sequences (Jacob Champion)
[](5396a2987)

It was possible to walk off the end of the input buffer by a few
bytes when the last bytes comprise an incomplete multi-byte
character.  While usually harmless, in principle this could cause a
crash.
- Disable creation of stateful TLS session tickets by OpenSSL
(Daniel Gustafsson)
[](cc606afce)
[](83b4a6358)
[](441eba34d)

This avoids possible failures with clients that think receipt of
a session ticket means that TLS session resumption is supported.
- When replanning a PL/pgSQL "simple
expression", check it's still simple (Tom Lane)
[](82a931d3d)

Certain fairly-artificial cases, such as dropping a referenced
function and recreating it as an aggregate, could lead to surprising
failures such as "unexpected plan node type".
- Fix PL/pgSQL's handling of integer ranges
containing underscores (Erik Wienhold)
[](b4e909082)

As of v16 we allow integer literals to contain underscores,
but PL/pgSQL failed to handle examples
such as `FOR i IN 1_001..1_003`.
- Fix recursive `RECORD`-returning
PL/Python functions (Tom Lane)
[](52ea653aa)

If we recurse to a new call of the same function that passes a
different column definition list (`AS` clause), it
would fail because the inner call would overwrite the outer call's
idea of what rowtype to return.
- Don't corrupt PL/Python's
`TD` dictionary during a recursive trigger call
(Tom Lane)
[](be18a12b6)

If a PL/Python-language trigger caused
another one to be invoked, the `TD` dictionary
created for the inner one would overwrite the outer
one's `TD` dictionary.
- Fix PL/Tcl's reporting of invalid list
syntax in the result of a function returning tuple (Erik Wienhold,
Tom Lane)
[](c236ecc82)

Such a case could result in a crash, or in emission of misleading
context information that actually refers to the previous Tcl error.
- Avoid non-thread-safe usage of `strerror()`
in libpq (Peter Eisentraut)
[](c53016860)

Certain error messages returned by OpenSSL could become garbled in
multi-threaded applications.
- Avoid memory leak within pg_dump during a
binary upgrade (Daniel Gustafsson)
[](0ae05c18e)
- Ensure that `pg_restore` `-l`
reports dependent TOC entries correctly (Tom Lane)
[](5dce8ce0a)

If `-l` was specified together with selective-restore
options such as `-n` or `-N`,
dependent TOC entries such as comments would be omitted from the
listing, even when an actual restore would have selected them.
- Allow `contrib/pg_stat_statements` to distinguish
among utility statements appearing within SQL-language functions
(Anthonin Bonnefoy)
[](9cd365f28)

The SQL-language function executor failed to pass along the query ID
that is computed for a utility
(non `SELECT`/`INSERT`/`UPDATE`/`DELETE`/`MERGE`)
statement.
- Avoid "cursor can only scan forward" error
in `contrib/postgres_fdw` (Etsuro Fujita)
[](d97f2ee50)

This error could occur if the remote server is v15 or later
and a foreign table is mapped to a non-trivial remote view.
- In `contrib/postgres_fdw`, do not
send `FETCH FIRST WITH TIES` clauses to the remote
server (Japin Li)
[](8405d5a37)

The remote server might not implement this clause, or might
interpret it differently than we would locally, so don't risk
attempting remote execution.
- Avoid clashing with
system-provided `` headers
(Thomas Munro)
[](31423bc44)

This fixes a compilation failure on macOS version 15 and up.
- Fix otherwise-harmless assertion failure in Memoize cost estimation
(David Rowley)
[](6143c9c03)
- Fix otherwise-harmless assertion failures in `REINDEX
CONCURRENTLY` applied to an SP-GiST index (Tom Lane)
[](06f81fed3)

## Release 16.3

## Release date:

2024-05-09

This release contains a variety of fixes from 16.2.
For information about new features in major release 16, see
[release-16](#release-16).

### Migration to Version 16.3

A dump/restore is not required for those running 16.X.

However, a security vulnerability was found in the system
views `pg_stats_ext`
and `pg_stats_ext_exprs`, potentially allowing
authenticated database users to see data they shouldn't.  If this is
of concern in your installation, follow the steps in the first
changelog entry below to rectify it.

Also, if you are upgrading from a version earlier than 16.2,
see [release-16-2](#release-16-2).

### Changes

- Restrict visibility of `pg_stats_ext` and
`pg_stats_ext_exprs` entries to the table
owner (Nathan Bossart)
[](2485a85e9)

These views failed to hide statistics for expressions that involve
columns the accessing user does not have permission to read.  View
columns such as `most_common_vals` might
expose security-relevant data.  The potential interactions here are
not fully clear, so in the interest of erring on the side of safety,
make rows in these views visible only to the owner of the associated
table.

The PostgreSQL Project thanks
Lukas Fittl for reporting this problem.
(CVE-2024-4317)

By itself, this fix will only fix the behavior in newly initdb'd
database clusters.  If you wish to apply this change in an existing
cluster, you will need to do the following:

Find the SQL script `fix-CVE-2024-4317.sql` in
the `share` directory of
the PostgreSQL installation (typically
located someplace like `/usr/share/postgresql/`).
Be sure to use the script appropriate to
your PostgreSQL major version.
If you do not see this file, either your version is not vulnerable
(only v14–v16 are affected) or your minor version is too
old to have the fix.

In *each* database of the cluster, run
the `fix-CVE-2024-4317.sql` script as superuser.
In psql this would look like

```
\i /usr/share/postgresql/fix-CVE-2024-4317.sql
```

(adjust the file path as appropriate).  Any error probably indicates
that you've used the wrong script version.  It will not hurt to run
the script more than once.

Do not forget to include the `template0`
and `template1` databases, or the vulnerability
will still exist in databases you create later.  To
fix `template0`, you'll need to temporarily make
it accept connections.  Do that with

```
ALTER DATABASE template0 WITH ALLOW_CONNECTIONS true;
```

and then after fixing `template0`, undo it with

```
ALTER DATABASE template0 WITH ALLOW_CONNECTIONS false;
```

Fix `INSERT` from
multiple `VALUES` rows into a target column that is
a domain over an array or composite type (Tom Lane)
[](52898c63e)

Such cases would either fail with surprising complaints about
mismatched datatypes, or insert unexpected coercions that could lead
to odd results.
- Require `SELECT` privilege on the target table
for `MERGE` with a `DO NOTHING`
clause (lvaro Herrera)
[](a3f5d2056)

`SELECT` privilege would be required in all
practical cases anyway, but require it even if the query reads no
columns of the target table.  This avoids an edge case in
which `MERGE` would require no privileges whatever,
which seems undesirable even when it's a do-nothing command.
- Fix handling of self-modified tuples in `MERGE`
(Dean Rasheed)
[](dd73d10ad)

Throw an error if a target row joins to more than one source row, as
required by the SQL standard.  (The previous coding could silently
ignore this condition if a concurrent update was involved.)  Also,
throw a non-misleading error if a target row is already updated by a
later command in the current transaction, thanks to
a `BEFORE` trigger or a volatile function used in
the query.
- Fix incorrect pruning of NULL partition when a table is partitioned
on a boolean column and the query has a boolean `IS
NOT` clause (David Rowley)
[](fb95cc72b)

A NULL value satisfies a clause such
as ``boolcol` IS NOT
FALSE`, so pruning away a partition containing NULLs
yielded incorrect answers.
- Make `ALTER FOREIGN TABLE SET SCHEMA` move any
owned sequences into the new schema (Tom Lane)
[](7445f0928)

Moving a regular table to a new schema causes any sequences owned by
the table to be moved to that schema too (along with indexes and
constraints).  This was overlooked for foreign tables, however.
- Make `ALTER TABLE ... ADD COLUMN` create
identity/serial sequences with the same persistence as their owning
tables (Peter Eisentraut)
[](86d2b434c)

`CREATE UNLOGGED TABLE` will make any owned
sequences be unlogged too.  `ALTER TABLE` missed
that consideration, so that an added identity column would have a
logged sequence, which seems pointless.
- Improve `ALTER TABLE ... ALTER COLUMN TYPE`'s error
message when there is a dependent function or publication (Tom Lane)
[](11d40a44b)
[](b19255ca6)
- In `CREATE DATABASE`, recognize strategy keywords
case-insensitively for consistency with other options (Tomas Vondra)
[](9e6faeb32)
- Fix `EXPLAIN`'s counting of heap pages accessed by
a bitmap heap scan (Melanie Plageman)
[](1f4eb7342)

Previously, heap pages that contain no visible tuples were not
counted; but it seems more consistent to count all pages returned by
the bitmap index scan.
- Fix `EXPLAIN`'s output for subplans
in `MERGE` (Dean Rasheed)
[](34c854b93)

`EXPLAIN` would sometimes fail to properly display
subplan Params referencing variables in other parts of the plan tree.
- Avoid deadlock during removal of orphaned temporary tables
(Mikhail Zhilin)
[](cbfbb14bd)

If the session that creates a temporary table crashes without
removing the table, autovacuum will eventually try to remove the
orphaned table.  However, an incoming session that's been assigned
the same temporary namespace will do that too.  If a temporary table
has a dependency (such as an owned sequence) then a deadlock could
result between these two cleanup attempts.
- Fix updating of visibility map state in `VACUUM`
with the `DISABLE_PAGE_SKIPPING` option (Heikki
Linnakangas)
[](407cb6c65)

Due to an oversight, this mode caused all heap pages to be dirtied,
resulting in excess I/O.  Also, visibility map bits that were
incorrectly set would not get cleared.
- Avoid race condition while examining per-relation frozen-XID values
(Noah Misch)
[](92685c389)

`VACUUM`'s computation of per-database frozen-XID
values from per-relation values could get confused by a concurrent
update of those values by another `VACUUM`.
- Fix buffer usage reporting for parallel vacuuming (Anthonin Bonnefoy)
[](f199436c1)

Buffer accesses performed by parallel workers were not getting
counted in the statistics reported in `VERBOSE`
mode.
- Ensure that join conditions generated from equivalence classes are
applied at the correct plan level (Tom Lane)
[](91800af13)

In versions before PostgreSQL 16, it was
possible for generated conditions to be evaluated below outer joins
when they should be evaluated above (after) the outer join, leading
to incorrect query results.  All versions have a similar hazard when
considering joins to `UNION ALL` trees that have
constant outputs for the join column in
some `SELECT ` arms.
- Fix "could not find pathkey item to sort" errors
occurring while planning aggregate functions with `ORDER
BY` or `DISTINCT` options (David Rowley)
[](4e1ff2aad)

This is similar to a fix applied in 16.1, but it solves the problem
for parallel plans.
- Prevent potentially-incorrect optimization of some window functions
(David Rowley)
[](9d36b883b)

Disable "run condition" optimization
of `ntile()` and `count()`
with non-constant arguments.  This avoids possible misbehavior with
sub-selects, typically leading to errors like "WindowFunc not
found in subplan target lists".
- Avoid unnecessary use of moving-aggregate mode with a non-moving
window frame (Vallimaharajan G)
[](a94f51a7b)

When a plain aggregate is used as a window function, and the window
frame start is specified as `UNBOUNDED PRECEDING`,
the frame's head cannot move so we do not need to use the special
(and more expensive) moving-aggregate mode.  This optimization was
intended all along, but due to a coding error it never triggered.
- Avoid use of already-freed data while planning partition-wise joins
under GEQO (Tom Lane)
[](ef0333e67)

This would typically end in a crash or unexpected error message.
- Avoid freeing still-in-use data in Memoize (Tender Wang, Andrei
Lepikhov)
[](348233cb1)

In production builds this error frequently didn't cause any
problems, as the freed data would most likely not get overwritten
before it was used.
- Fix incorrectly-reported statistics kind codes in "requested
statistics kind `X` is not yet
built" error messages (David Rowley)
[](ac7e6a01c)
- Use a hash table instead of linear search for "catcache
list" objects (Tom Lane)
[](14e991db8)

This change solves performance problems that were reported for
certain operations in installations with many thousands of roles.
- Be more careful with `RECORD`-returning functions
in `FROM` (Tom Lane)
[](cc1eb6a3c)
[](1b3029be5)

The output columns of such a function call must be defined by
an `AS` clause that specifies the column names and
data types.  If the actual function output value doesn't match that,
an error is supposed to be thrown at runtime.  However, some code
paths would examine the actual value prematurely, and potentially
issue strange errors or suffer assertion failures if it doesn't
match expectations.
- Fix confusion about the return rowtype of SQL-language procedures
(Tom Lane)
[](40d1bdeb7)

A procedure implemented in SQL language that returns a single
composite-type column would cause an assertion failure or core dump.
- Add protective stack depth checks to some recursive functions
(Egor Chindyaskin)
[](760767182)
- Fix mis-rounding and overflow hazards
in `date_bin()` (Moaaz Assali)
[](17db5436e)

In the case where the source timestamp is before the origin
timestamp and their difference is already an exact multiple of the
stride, the code incorrectly subtracted the stride anyway.  Also,
detect some integer-overflow cases that would have produced
incorrect results.
- Detect integer overflow when adding or subtracting
an `interval` to/from a `timestamp`
(Joseph Koshakow)
[](3752e3d21)

Some cases that should cause an out-of-range error produced an
incorrect result instead.
- Avoid race condition in `pg_get_expr()`
(Tom Lane)
[](4eb261165)

If the relation referenced by the argument is dropped concurrently,
the function's intention is to return NULL, but sometimes it failed
instead.
- Fix detection of old transaction IDs in XID status functions
(Karina Litskevich)
[](e3e05adde)

Transaction IDs more than 2^31
transactions in the past could be misidentified as recent,
leading to misbehavior of `pg_xact_status()`
or `txid_status()`.
- Ensure that a table's freespace map won't return a page that's past
the end of the table (Ronan Dunklau)
[](4e62ba21a)

Because the freespace map isn't WAL-logged, this was possible in
edge cases involving an OS crash, a replica promote, or a PITR
restore.  The result would be a "could not read block"
error.
- Fix file descriptor leakage when an error is thrown while waiting
in `WaitEventSetWait` (Etsuro Fujita)
[](e79ceafe9)
- Avoid corrupting exception stack if an FDW implements async append
but doesn't configure any wait conditions for the Append plan node
to wait for (Alexander Pyhalov)
[](f6f61a4bd)
- Throw an error if an index is accessed while it is being reindexed
(Tom Lane)
[](8c785d354)

Previously this was just an assertion check, but promote it into a
regular runtime error.  This will provide a more on-point error
message when reindexing a user-defined index expression that
attempts to access its own table.
- Ensure that index-only scans on `name` columns return a
fully-padded value (David Rowley)
[](68d358545)

The value physically stored in the index is truncated, and
previously a pointer to that value was returned to callers.  This
provoked complaints when testing under valgrind.  In theory it could
result in crashes, though none have been reported.
- Fix race condition that could lead to reporting an incorrect
conflict cause when invalidating a replication slot (Bertrand
Drouvot)
[](59cea09f0)
- Fix race condition in deciding whether a table sync operation is
needed in logical replication (Vignesh C)
[](a9155efc7)

An invalidation event arriving while a subscriber identifies which
tables need to be synced would be forgotten about, so that any
tables newly in need of syncing might not get processed in a timely
fashion.
- Fix crash with DSM allocations larger than 4GB (Heikki Linnakangas)
[](f2f09b825)
- Disconnect if a new server session's client socket cannot be put
into non-blocking mode (Heikki Linnakangas)
[](539e328b1)

It was once theoretically possible for us to operate with a socket
that's in blocking mode; but that hasn't worked fully in a long
time, so fail at connection start rather than misbehave later.
- Fix inadequate error reporting
with OpenSSL 3.0.0 and later (Heikki
Linnakangas, Tom Lane)
[](6a2c80e95)

System-reported errors passed through by OpenSSL were reported with
a numeric error code rather than anything readable.
- Fix thread-safety of error reporting
for `getaddrinfo()` on Windows (Thomas Munro)
[](0460e4ecc)

A multi-threaded libpq client program
could get an incorrect or corrupted error message after a network
lookup failure.
- Avoid concurrent calls to `bindtextdomain()`
in libpq
and ecpglib (Tom Lane)
[](52afe5632)
[](9440d23a0)

Although GNU gettext's implementation
seems to be fine with concurrent calls, the version available on
Windows is not.
- Fix crash in ecpg's preprocessor if
the program tries to redefine a macro that was defined on the
preprocessor command line (Tom Lane)
[](392e6e9e6)
[](0018f0af5)
[](dd3fddc85)
- In ecpg, avoid issuing
false "unsupported feature will be passed to server"
warnings (Tom Lane)
[](118558e6d)
- Ensure that the string result
of ecpg's `intoasc()`
function is correctly zero-terminated (Oleg Tselebrovskiy)
[](88e03d055)
- In initdb's `-c` option,
match parameter names case-insensitively (Tom Lane)
[](b78f4d22b)

The server treats parameter names case-insensitively, so this code
should too.  This avoids putting redundant entries into the
generated `postgresql.conf` file.
- In psql, avoid leaking a query result
after the query is cancelled (Tom Lane)
[](a85e3ba1c)

This happened only when cancelling a non-last query in a query
string made with `\;` separators.
- Fix pg_dumpall so that role comments, if
present, will be dumped regardless of the setting
of `--no-role-passwords` (Daniel Gustafsson,
lvaro Herrera)
[](5863bacb8)
- Skip files named `.DS_Store`
in pg_basebackup,
pg_checksums,
and pg_rewind (Daniel Gustafsson)
[](103235888)

This avoids problems on macOS, where the Finder may create such
files.
- Fix PL/pgSQL's parsing of single-line
comments (`--`-style comments) following
expressions (Erik Wienhold, Tom Lane)
[](48f216dc6)

This mistake caused parse errors if such a comment followed
a `WHEN` expression in
a PL/pgSQL `CASE`
statement.
- In `contrib/amcheck`, don't report false match
failures due to short- versus long-header values (Andrey Borodin,
Michael Zhilin)
[](3676b846b)
[](a6ddb8ad0)

A variable-length datum in a heap tuple or index tuple could have
either a short or a long header, depending on compression parameters
that applied when it was made.  Treat these cases as equivalent
rather than complaining if there's a difference.
- Fix bugs in BRIN output functions (Tomas Vondra)
[](8cea358b1)
[](ccd8f0fa1)

These output functions are only used for displaying index entries
in `contrib/pageinspect`, so the errors are of
limited practical concern.
- In `contrib/postgres_fdw`, avoid emitting
requests to sort by a constant (David Rowley)
[](6a9e2cb2b)

This could occur in cases involving `UNION ALL`
with constant-emitting subqueries.  Sorting by a constant is useless
of course, but it also risks being misinterpreted by the remote
server, leading to "ORDER BY
position `N` is not in select list"
errors.
- Make `contrib/postgres_fdw` set the remote
session's time zone to `GMT`
not `UTC` (Tom Lane)
[](75929b6cf)

This should have the same results for practical purposes.
However, `GMT` is recognized by hard-wired code in
the server, while `UTC` is looked up in the
timezone database.  So the old code could fail in the unlikely event
that the remote server's timezone database is missing entries.
- In `contrib/xml2`, avoid use of library functions
that have been deprecated in recent versions
of libxml2 (Dmitry Koval)
[](7c93f31de)
- Fix incompatibility with LLVM 18 (Thomas Munro, Dmitry Dolgov)
[](bf1cfe77e)
- Allow `make check` to work with
the musl C library (Thomas Munro, Bruce
Momjian, Tom Lane)
[](7651fd387)

## Release 16.2

## Release date:

2024-02-08

This release contains a variety of fixes from 16.1.
For information about new features in major release 16, see
[release-16](#release-16).

### Migration to Version 16.2

A dump/restore is not required for those running 16.X.

However, one bug was fixed that could have resulted in corruption of
GIN indexes during concurrent updates.  If you suspect such
corruption, reindex affected indexes after installing this update.

Also, if you are upgrading from a version earlier than 16.1,
see [release-16-1](#release-16-1).

### Changes

- Tighten security restrictions within `REFRESH MATERIALIZED
VIEW CONCURRENTLY` (Heikki Linnakangas)
[](d6a61cb3b)
[](fb3836855)

One step of a concurrent refresh command was run under weak security
restrictions.  If a materialized view's owner could persuade a
superuser or other high-privileged user to perform a concurrent
refresh on that view, the view's owner could control code executed
with the privileges of the user running `REFRESH`.
Fix things so that all user-determined code is run as the view's
owner, as expected.

The only known exploit for this error does not work
in PostgreSQL 16.0 and later, so it may
be that v16 is not vulnerable in practice.

The PostgreSQL Project thanks Pedro
Gallegos for reporting this problem.
(CVE-2024-0985)
- Fix memory leak when performing JIT inlining (Andres Freund,
Daniel Gustafsson)
[](2cf50585e)

There have been multiple reports of backend processes suffering
out-of-memory conditions after sufficiently many JIT compilations.
This fix should resolve that.
- Avoid generating incorrect partitioned-join plans (Richard Guo)
[](62f120203)

Some uncommon situations involving lateral references could create
incorrect plans.  Affected queries could produce wrong answers, or
odd failures such as "variable not found in subplan target
list", or executor crashes.
- Fix incorrect wrapping of subquery output expressions in
PlaceHolderVars (Tom Lane)
[](80bece312)

This fixes incorrect results when a subquery is underneath an outer
join and has an output column that laterally references something
outside the outer join's scope.  The output column might not appear
as NULL when it should do so due to the action of the outer join.
- Fix misprocessing of window function run conditions (Richard Guo)
[](ee9553218)

This oversight could lead to "WindowFunc not found in subplan
target lists" errors.
- Fix detection of inner-side uniqueness for Memoize plans
(Richard Guo)
[](74f770ef2)

This mistake could lead to "cache entry already
complete" errors.
- Fix computation of nullingrels when constant-folding field selection
(Richard Guo)
[](6bf2efb38)

Failure to do this led to errors like "wrong varnullingrels
(b) (expected (b 3)) for Var 2/2".
- Skip inappropriate actions when `MERGE` causes a
cross-partition update (Dean Rasheed)
[](06a546382)

When executing a `MERGE UPDATE` action on a
partitioned table, if the `UPDATE` is turned into
a `DELETE` and `INSERT` due to
changing a partition key column, skip firing `AFTER
UPDATE ROW` triggers, as well as other post-update actions
such as RLS checks.  These actions would typically fail, which is
why a regular `UPDATE` doesn't do them in such
cases; `MERGE` shouldn't either.
- Cope with `BEFORE ROW DELETE` triggers in
cross-partition `MERGE` updates (Dean Rasheed)
[](7f07384dc)

If such a trigger attempted to prevent the update by returning
NULL, `MERGE` would suffer an error or assertion
failure.
- Prevent access to a no-longer-pinned buffer in `BEFORE ROW
UPDATE` triggers (Alexander Lakhin, Tom Lane)
[](23e0ba59c)

If the tuple being updated had just been updated and moved to
another page by another session, there was a narrow window where
we would attempt to fetch data from the new tuple version without
any pin on its buffer.  In principle this could result in garbage
data appearing in non-updated columns of the proposed new tuple.
The odds of problems in practice seem rather low, however.
- Avoid requesting an oversize shared-memory area in parallel hash
join (Thomas Munro, Andrei Lepikhov, Alexander Korotkov)
[](714a987bc)
[](20a566cd4)

The limiting value was too large, allowing "invalid DSA memory
alloc request size" errors to occur with sufficiently large
expected hash table sizes.
- Fix corruption of local buffer state when an error occurs while
trying to extend a temporary table (Tender Wang)
[](37c551663)
- Fix use of wrong tuple slot while
evaluating `DISTINCT` aggregates that have multiple
arguments (David Rowley)
[](6298673f4)

This mistake could lead to errors such as "attribute 1 of type
record has wrong type".
- Avoid assertion failures in `heap_update()`
and `heap_delete()` when a tuple to be updated by
a foreign-key enforcement trigger fails the extra visibility
crosscheck (Alexander Lakhin)
[](9fee3232a)

This error had no impact in non-assert builds.
- Fix overly tight assertion
about `false_positive_rate` parameter of
BRIN bloom operator classes (Alexander Lakhin)
[](4dccf9575)

This error had no impact in non-assert builds, either.
- Fix possible failure during `ALTER TABLE ADD
COLUMN` on a complex inheritance tree (Tender Wang)
[](51193e7a7)

If a grandchild table would inherit the new column via multiple
intermediate parents, the command failed with "tuple already
updated by self".
- Fix problems with duplicate token names in `ALTER TEXT
SEARCH CONFIGURATION ... MAPPING` commands (Tender Wang,
Michael Paquier)
[](f33e83285)
- Fix `DROP ROLE` with duplicate role names
(Michael Paquier)
[](f57a580fd)

Previously this led to a "tuple already updated by
self" failure.  Instead, ignore the duplicate.
- Properly lock the associated table during `DROP
STATISTICS` (Tomas Vondra)
[](ee32b824d)

Failure to acquire the lock could result in "tuple
concurrently deleted" errors if the `DROP`
executes concurrently with `ANALYZE`.
- Fix function volatility checking for `GENERATED`
and `DEFAULT` expressions (Tom Lane)
[](f07a3039c)

These places could fail to detect insertion of a volatile function
default-argument expression, or decide that a polymorphic function
is volatile although it is actually immutable on the datatype of
interest.  This could lead to improperly rejecting or accepting
a `GENERATED` clause, or to mistakenly applying the
constant-default-value optimization in `ALTER TABLE ADD
COLUMN`.
- Detect that a new catalog cache entry became stale while detoasting
its fields (Tom Lane)
[](7e2561e1a)
[](56dcd71de)

We expand any out-of-line fields in a catalog tuple before inserting
it into the catalog caches.  That involves database access which
might cause invalidation of catalog cache entries — but the
new entry isn't in the cache yet, so we would miss noticing that it
should get invalidated.  The result is a race condition in which an
already-stale cache entry could get made, and then persist
indefinitely.  This would lead to hard-to-predict misbehavior.
Fix by rechecking the tuple's visibility after detoasting.
- Fix edge-case integer overflow detection bug on some platforms (Dean
Rasheed)
[](c396aca2b)

Computing `0 - INT64_MIN` should result in an
overflow error, and did on most platforms.  However, platforms with
neither integer overflow builtins nor 128-bit integers would fail to
spot the overflow, instead returning `INT64_MIN`.
- Detect Julian-date overflow when adding or subtracting
an `interval` to/from a `timestamp` (Tom Lane)
[](7204aea83)

Some cases that should cause an out-of-range error produced an
incorrect result instead.
- Add more checks for overflow in `interval_mul()`
and `interval_div()` (Dean Rasheed)
[](72d0c135b)

Some cases that should cause an out-of-range error produced an
incorrect result instead.
- Allow `scram_SaltedPassword()` to be interrupted
(Bowen Shi)
[](07cb7bc1c)

With large `scram_iterations` values, this function
could take a long time to run.  Allow it to be interrupted by query
cancel requests.
- Ensure cached statistics are discarded after a change
to `stats_fetch_consistency` (Shinya Kato)
[](781bc121d)

In some code paths, it was possible for stale statistics to be
returned.
- Make the `pg_file_settings` view check
validity of unapplied values for settings
with `backend`
or `superuser-backend` context (Tom Lane)
[](e87252ceb)

Invalid values were not noted in the view as intended.  This escaped
detection because there are very few settings in these groups.
- Match collation too when matching an existing index to a new
partitioned index (Peter Eisentraut)
[](267f33f68)

Previously we could accept an index that has a different collation
from the corresponding element of the partition key, possibly
leading to misbehavior.
- Avoid failure if a child index is dropped concurrently
with `REINDEX INDEX` on a partitioned index
(Fei Changhong)
[](c030e263e)
[](7ce65c6f7)
- Fix insufficient locking when cleaning up an incomplete split of
a GIN index's internal page (Fei Changhong, Heikki Linnakangas)
[](b899e00e7)

The code tried to do this with shared rather than exclusive lock on
the buffer.  This could lead to index corruption if two processes
attempted the cleanup concurrently.
- Avoid premature release of buffer pin in GIN index insertion
(Tom Lane)
[](f76b975d5)

If an index root page split occurs concurrently with our own
insertion, the code could fail with "buffer NNNN is not owned
by resource owner".
- Avoid failure with partitioned SP-GiST indexes (Tom Lane)
[](0977bd64e)

Trying to use an index of this kind could lead to "No such
file or directory" errors.
- Fix ownership tests for large objects (Tom Lane)
[](152bfc0af)

Operations on large objects that require ownership privilege failed
with "unrecognized class ID: 2613", unless run by a
superuser.
- Fix ownership change reporting for large objects (Tom Lane)
[](152bfc0af)

A no-op `ALTER LARGE OBJECT OWNER` command (that
is, one selecting the existing owner) passed the wrong class ID to
the `PostAlterHook`, probably confusing any
extension using that hook.
- Fix reporting of I/O timing data in `EXPLAIN
(BUFFERS)` (Michael Paquier)
[](db69101a1)

The numbers labeled as "shared/local" actually refer
only to shared buffers, so change that label
to "shared".
- Ensure durability of `CREATE DATABASE` (Noah Misch)
[](6d423e9ff)
[](48a6bf5c4)

If an operating system crash occurred during or shortly
after `CREATE DATABASE`, recovery could fail, or
subsequent connections to the new database could fail.  If a base
backup was taken in that window, similar problems could be observed
when trying to use the backup.  The symptom would be that the
database directory, `PG_VERSION` file, or
`pg_filenode.map` file was missing or empty.
- Add more `LOG` messages when starting and ending
recovery from a backup (Andres Freund)
[](edbd1b41a)

This change provides additional information in the postmaster log
that may be useful for diagnosing recovery problems.
- Prevent standby servers from incorrectly processing dead index
tuples during subtransactions (Fei Changhong)
[](0e2c05af9)

The `startedInRecovery` flag was not
correctly set for a subtransaction.  This affects only processing of
dead index tuples.  It could allow a query in a subtransaction to
ignore index entries that it should return (if they are already dead
on the primary server, but not dead to the standby transaction), or
to prematurely mark index entries as dead that are not yet dead on
the primary.  It is not clear that the latter case has any serious
consequences, but it's not the intended behavior.
- Fix signal handling in walreceiver processes (Heikki Linnakangas)
[](c5a6d5337)

Revert a change that made walreceivers non-responsive
to SIGTERM while waiting for the
replication connection to be established.
- Fix integer overflow hazard in checking whether a record will fit
into the WAL decoding buffer (Thomas Munro)
[](8ca56620c)

This bug appears to be only latent except when running a
32-bit PostgreSQL build on a 64-bit
platform.
- Fix deadlock between a logical replication apply worker, its
tablesync worker, and a session process trying to alter the
subscription (Shlok Kyal)
[](01cc92fa6)

One edge of the deadlock loop did not involve a lock wait, so the
deadlock went undetected and would persist until manual
intervention.
- Ensure that column default values are correctly transmitted by
the pgoutput logical replication plugin
(Nikhil Benesch)
[](d7ca9209c)

`ALTER TABLE ADD COLUMN` with a constant default
value for the new column avoids rewriting existing tuples, instead
expecting that reading code will insert the correct default into a
tuple that lacks that column.  If replication was subsequently
initiated on the table, pgoutput would
transmit NULL instead of the correct default for such a column,
causing incorrect replication on the subscriber.
- Fix failure of logical replication's initial sync for a table with
no columns (Vignesh C)
[](1b6da28e0)

This case generated an improperly-formatted `COPY`
command.
- Re-validate a subscription's connection string before use (Vignesh C)
[](4c03ac7e2)
[](5b5318c38)

This is meant to detect cases where a subscription was created
without a password (which is allowed to superusers) but then the
subscription owner is changed to a non-superuser.
- Return the correct status code when a new client disconnects without
responding to the server's password challenge (Liu Lang, Tom Lane)
[](fb464a1ae)

In some cases we'd treat this as a loggable error, which was not the
intention and tends to create log spam, since common clients
like psql frequently do this.  It may
also confuse extensions that
use `ClientAuthentication_hook`.
- Fix incompatibility with OpenSSL 3.2
(Tristan Partin, Bo Andreson)
[](efa8f6064)

Use the BIO "app_data" field for our private storage,
instead of assuming it's okay to use the "data" field.
This mistake didn't cause problems before, but with 3.2 it leads
to crashes and complaints about double frees.
- Be more wary about OpenSSL not
setting `errno` on error (Tom Lane)
[](ebbd499d4)

If `errno` isn't set, assume the cause of the
reported failure is read EOF.  This fixes rare cases of strange
error reports like "could not accept SSL connection:
Success".
- Fix file descriptor leakage when a foreign data
wrapper's `ForeignAsyncRequest` function fails
(Heikki Linnakangas)
[](501cfd07d)
- Fix minor memory leak in connection string validation
for `CREATE SUBSCRIPTION` (Jeff Davis)
[](41820e640)
- Report ENOMEM errors from file-related system
calls as `ERRCODE_OUT_OF_MEMORY`,
not `ERRCODE_INTERNAL_ERROR` (Alexander Kuzmenkov)
[](a15378100)
- In PL/pgSQL, support SQL commands that
are `CREATE FUNCTION`/`CREATE
PROCEDURE` with SQL-standard bodies (Tom Lane)
[](00f941356)

Previously, such cases failed with parsing errors due to the
semicolon(s) appearing in the function body.
- Fix libpq's
handling of errors in pipelines (lvaro Herrera)
[](878aa41f8)
[](39aab1108)

The pipeline state could get out of sync if an error is returned
for reasons other than a query problem (for example, if the
connection is lost).  Potentially this would lead to a busy-loop in
the calling application.
- Make libpq's
`PQsendFlushRequest()` function flush the client
output buffer under the same rules as
other `PQsend` functions (Jelte Fennema-Nio)
[](42f832685)

In pipeline mode, it may still be necessary to
call `PQflush()` as well; but this change removes
some inconsistency.
- Avoid race condition when libpq
initializes OpenSSL support concurrently in two different threads
(Willi Mann, Michael Paquier)
[](8984480b5)
- Fix timing-dependent failure in GSSAPI data transmission (Tom Lane)
[](85eb77185)

When using GSSAPI encryption in non-blocking
mode, libpq sometimes failed
with "GSSAPI caller failed to retransmit all data needing to
be retried".
- Change initdb to always un-comment
the `postgresql.conf` entries for
the `lc_`xxx`` parameters
(Kyotaro Horiguchi)
[](ba33775fd)

initdb used to work this way before v16,
and now it does again.  The change
caused initdb's `--no-locale`
option to not have the intended effect
on `lc_messages`.
- In pg_dump, don't dump RLS policies or
security labels for extension member objects (Tom Lane, Jacob
Champion)
[](64d2467fc)
[](f1674ac6b)

Previously, commands would be included in the dump to set these
properties, which is really incorrect since they should be
considered as internal affairs of the extension.  Moreover, the
restoring user might not have adequate privilege to set them, and
indeed the dumping user might not have enough privilege to dump them
(since dumping RLS policies requires acquiring lock on their table).
- In pg_dump, don't dump an extended
statistics object if its underlying table isn't being dumped
(Rian McGuire, Tom Lane)
[](b2c9936a7)

This conforms to the behavior for other dependent objects such as
indexes.
- Properly detect out-of-memory in one code path
in pg_dump (Daniel Gustafsson)
[](5b5db413d)
- Make it an error for a pgbench script to
end with an open pipeline (Anthonin Bonnefoy)
[](07b53de70)

Previously, pgbench would behave oddly if
a `\startpipeline` command lacked a
matching `\endpipeline`.  This seems like a
scripting mistake rather than a case
that pgbench needs to handle nicely, so
throw an error.
- Fix crash in `contrib/intarray` if an array with
an element equal to `INT_MAX` is inserted into
a `gist__int_ops` index
(Alexander Lakhin, Tom Lane)
[](cf6f802bf)
- Report a better error
when `contrib/pageinspect`'s
`hash_bitmap_info()` function is applied to a
partitioned hash index (Alexander Lakhin, Michael Paquier)
[](7f68b1462)
- Report a better error
when `contrib/pgstattuple`'s
`pgstathashindex()` function is applied to a
partitioned hash index (Alexander Lakhin)
[](b4948ed66)
- On Windows, suppress autorun options when launching subprocesses
in pg_ctl
and pg_regress (Kyotaro Horiguchi)
[](714bfb781)
[](506c77f9b)

When launching a child process via `cmd.exe`,
pass the `/D` flag to prevent executing any autorun
commands specified in the registry.  This avoids possibly-surprising
side effects.
- Move `is_valid_ascii()`
from `mb/pg_wchar.h`
to `utils/ascii.h` (Jubilee Young)
[](1b924a86e)

This change avoids the need to
include ``
in `pg_wchar.h`, which was causing problems for
some third-party code.
- Fix compilation failures with libxml2
version 2.12.0 and later (Tom Lane)
[](e02fea093)
- Fix compilation failure of `WAL_DEBUG` code on
Windows (Bharath Rupireddy)
[](6248a2bb9)
- Suppress compiler warnings from Python's header files
(Peter Eisentraut, Tom Lane)
[](b0115e7e2)
[](c72049dbc)

Our preferred compiler options provoke warnings about constructs
appearing in recent versions of Python's header files.  When using
gcc, we can suppress these warnings with
a pragma.
- Avoid deprecation warning when compiling with LLVM 18 (Thomas Munro)
[](60ba7cae7)
- Update time zone data files to tzdata
release 2024a for DST law changes in Greenland, Kazakhstan, and
Palestine, plus corrections for the Antarctic stations Casey and
Vostok.  Also historical corrections for Vietnam, Toronto, and
Miquelon. (Tom Lane)
[](b4fb76fb5)

## Release 16.1

## Release date:

2023-11-09

This release contains a variety of fixes from 16.0.
For information about new features in major release 16, see
[release-16](#release-16).

### Migration to Version 16.1

A dump/restore is not required for those running 16.X.

However, several mistakes have been discovered that could lead to
certain types of indexes yielding wrong search results or being
unnecessarily inefficient.  It is advisable
to `REINDEX` potentially-affected indexes after
installing this update.  See the fourth through seventh changelog
entries below.

### Changes

- Fix handling of unknown-type arguments
in `DISTINCT` `"any"` aggregate
functions (Tom Lane)
[](d3d1e2509)

This error led to a `text`-type value being interpreted
as an `unknown`-type value (that is, a zero-terminated
string) at runtime.  This could result in disclosure of server
memory following the `text` value.

The PostgreSQL Project thanks Jingzhou Fu
for reporting this problem.
(CVE-2023-5868)
- Detect integer overflow while computing new array dimensions
(Tom Lane)
[](e24daa94b)

When assigning new elements to array subscripts that are outside the
current array bounds, an undetected integer overflow could occur in
edge cases.  Memory stomps that are potentially exploitable for
arbitrary code execution are possible, and so is disclosure of
server memory.

The PostgreSQL Project thanks Pedro
Gallegos for reporting this problem.
(CVE-2023-5869)
- Prevent the `pg_signal_backend` role from
signalling background workers and autovacuum processes
(Noah Misch, Jelte Fennema-Nio)
[](785412731)
[](2c3c5ec49)

The documentation says that `pg_signal_backend`
cannot issue signals to superuser-owned processes.  It was able to
signal these background processes, though, because they advertise a
role OID of zero.  Treat that as indicating superuser ownership.
The security implications of cancelling one of these process types
are fairly small so far as the core code goes (we'll just start
another one), but extensions might add background workers that are
more vulnerable.

Also ensure that the `is_superuser` parameter is
set correctly in such processes.  No specific security consequences
are known for that oversight, but it might be significant for some
extensions.

The PostgreSQL Project thanks
Hemanth Sandrana and Mahendrakar Srinivasarao
for reporting this problem.
(CVE-2023-5870)
- Fix misbehavior during recursive page split in GiST index build
(Heikki Linnakangas)
[](d7f521325)

Fix a case where the location of a page downlink was incorrectly
tracked, and introduce some logic to allow recovering from such
situations rather than silently doing the wrong thing.  This error
could result in incorrect answers from subsequent index searches.
It may be advisable to reindex all GiST indexes after installing
this update.
- Prevent de-duplication of btree index entries
for `interval` columns (Noah Misch)
[](bf1c21c4f)

There are `interval` values that are distinguishable but
compare equal, for example `24:00:00`
and `1 day`.  This breaks assumptions made by btree
de-duplication, so `interval` columns need to be excluded
from de-duplication.  This oversight can cause incorrect results
from index-only scans.  Moreover, after
updating amcheck will report an error for
almost all such indexes.  Users should reindex any btree indexes
on `interval` columns.
- Process `date` values more sanely in
BRIN `datetime_minmax_multi_ops` indexes
(Tomas Vondra)
[](e7965226d)

The distance calculation for dates was backward, causing poor
decisions about which entries to merge.  The index still produces
correct results, but is much less efficient than it should be.
Reindexing BRIN `minmax_multi` indexes
on `date` columns is advisable.
- Process large `timestamp` and `timestamptz`
values more sanely in
BRIN `datetime_minmax_multi_ops` indexes
(Tomas Vondra)
[](497fc9208)
[](0635fe02b)

Infinities were mistakenly treated as having distance zero rather
than a large distance from other values, causing poor decisions
about which entries to merge.  Also, finite-but-very-large values
(near the endpoints of the representable timestamp range) could
result in internal overflows, again causing poor decisions.  The
index still produces correct results, but is much less efficient
than it should be.  Reindexing BRIN `minmax_multi`
indexes on `timestamp` and `timestamptz`
columns is advisable if the column contains, or has contained,
infinities or large finite values.
- Avoid calculation overflows in
BRIN `interval_minmax_multi_ops` indexes with
extreme interval values (Tomas Vondra)
[](924e0e2ee)

This bug might have caused unexpected failures while trying to
insert large interval values into such an index.
- Fix partition step generation and runtime partition pruning for
hash-partitioned tables with multiple partition keys (David Rowley)
[](595db9e9c)
[](6352f1627)

Some cases involving an `IS NULL` condition on one
of the partition keys could result in a crash.
- Fix inconsistent rechecking of concurrently-updated rows
during `MERGE` (Dean Rasheed)
[](6d2de076c)

In `READ COMMITTED` mode, an update that finds that
its target row was just updated by a concurrent transaction will
recheck the query's `WHERE` conditions on the
updated row.  `MERGE` failed to ensure that the
proper rows of other joined tables were used during this recheck,
possibly resulting in incorrect decisions about whether the
newly-updated row should be updated again
by `MERGE`.
- Correctly identify the target table in an
inherited `UPDATE`/`DELETE`/`MERGE`
even when the parent table is excluded by constraints (Amit Langote,
Tom Lane)
[](b1444a09d)
[](178ee1d85)
[](2bf99b48d)

If the initially-named table is excluded by constraints, but not all
its inheritance descendants are, the first non-excluded descendant
was identified as the primary target table.  This would lead to
firing statement-level triggers associated with that table, rather
than the initially-named table as should happen.  In v16, the same
oversight could also lead to "invalid perminfoindex 0 in RTE
with relid NNNN" errors.
- Fix edge case in btree mark/restore processing of ScalarArrayOpExpr
clauses (Peter Geoghegan)
[](3fa81b62e)

When restoring an indexscan to a previously marked position, the
code could miss required setup steps if the scan had advanced
exactly to the end of the matches for a ScalarArrayOpExpr (that is,
an `indexcol = ANY(ARRAY[])`) clause.  This could
result in missing some rows that should have been fetched.
- Fix intra-query memory leak in Memoize execution
(Orlov Aleksej, David Rowley)
[](31b2b2d72)
- Fix intra-query memory leak when a set-returning function repeatedly
returns zero rows (Tom Lane)
[](07494a0df)
- Don't crash if `cursor_to_xmlschema()` is applied
to a non-data-returning Portal (Boyu Yang)
[](ec693a3f3)
- Fix improper sharing of origin filter condition across
successive `pg_logical_slot_get_changes()` calls
(Hou Zhijie)
[](8d05be931)

The origin condition set by one call of this function would be
re-used by later calls that did not specify the origin argument.
This was not intended.
- Throw the intended error if `pgrowlocks()` is
applied to a partitioned table (David Rowley)
[](a98f01c93)

Previously, a not-on-point complaint "only heap AM is
supported" would be raised.
- Handle invalid indexes more cleanly in assorted SQL functions
(Noah Misch)
[](1a368dd3e)

Report an error if `pgstatindex()`,
`pgstatginindex()`,
`pgstathashindex()`,
or `pgstattuple()` is applied to an invalid
index.  If `brin_desummarize_range()`,
`brin_summarize_new_values()`,
`brin_summarize_range()`,
or `gin_clean_pending_list()` is applied to an
invalid index, do nothing except to report a debug-level message.
Formerly these functions attempted to process the index, and might
fail in strange ways depending on what the failed `CREATE
INDEX` had left behind.
- Avoid premature memory allocation failure with long inputs
to `to_tsvector()` (Tom Lane)
[](8465efc1a)
- Fix over-allocation of the constructed `tsvector`
in `tsvectorrecv()` (Denis Erokhin)
[](5c34a7374)

If the incoming vector includes position data, the binary receive
function left wasted space (roughly equal to the size of the
position data) in the finished `tsvector`.  In extreme
cases this could lead to "maximum total lexeme length
exceeded" failures for vectors that were under the length
limit when emitted.  In any case it could lead to wasted space
on-disk.
- Improve checks for corrupt PGLZ compressed data (Flavien Guedez)
[](cfa4eba02)
- Fix `ALTER SUBSCRIPTION` so that a commanded change
in the `run_as_owner` option is actually applied
(Hou Zhijie)
[](a81e5516f)
- Fix bulk table insertion into partitioned tables (Andres Freund)
[](0002feb82)

Improper sharing of insertion state across partitions could result
in failures during `COPY FROM`, typically
manifesting as "could not read block NNNN in file XXXX: read
only 0 of 8192 bytes" errors.
- In `COPY FROM`, avoid evaluating column default
values that will not be needed by the command (Laurenz Albe)
[](910eb61b2)

This avoids a possible error if the default value isn't actually
valid for the column, or if the default's expression would fail in
the current execution context.  Such edge cases sometimes arise
while restoring dumps, for example.  Previous releases did not fail
in this situation, so prevent v16 from doing so.
- In `COPY FROM`, fail cleanly when an unsupported
encoding conversion is needed (Tom Lane)
[](ea0e7cd6b)

Recent refactoring accidentally removed the intended error check for
this, such that it ended in "cache lookup failed for function
0" instead of a useful error message.
- Avoid crash in `EXPLAIN` if a parameter marked to
be displayed by `EXPLAIN` has a NULL boot-time
value (Xing Guo, Aleksander Alekseev, Tom Lane)
[](82063edd4)

No built-in parameter fits this description, but an extension could
define such a parameter.
- Ensure we have a snapshot while dropping `ON COMMIT
DROP` temp tables (Tom Lane)
[](57e6e861d)

This prevents possible misbehavior if any catalog entries for the
temp tables have fields wide enough to require toasting (such as a
very complex `CHECK` condition).
- Avoid improper response to shutdown signals in child processes
just forked by `system()` (Nathan Bossart)
[](ee06199fc)

This fix avoids a race condition in which a child process that has
been forked off by `system()`, but hasn't yet
exec'd the intended child program, might receive and act on a signal
intended for the parent server process.  That would lead to
duplicate cleanup actions being performed, which will not end well.
- Cope with torn reads of `pg_control` in frontend
programs (Thomas Munro)
[](5725e4ebe)

On some file systems, reading `pg_control` may
not be an atomic action when the server concurrently writes that
file.  This is detectable via a bad CRC.  Retry a few times to see
if the file becomes valid before we report error.
- Avoid torn reads of `pg_control` in relevant SQL
functions (Thomas Munro)
[](2371432cd)

Acquire the appropriate lock before
reading `pg_control`, to ensure we get a
consistent view of that file.
- Fix "could not find pathkey item to sort" errors
occurring while planning aggregate functions with `ORDER
BY` or `DISTINCT` options (David Rowley)
[](9154ededf)
- Avoid integer overflow when computing size of backend activity
string array (Jakub Wartak)
[](75f31a3f2)

On 64-bit machines we will allow values
of `track_activity_query_size` large enough to
cause 32-bit overflow when multiplied by the allowed number of
connections.  The code actually allocating the per-backend local
array was careless about this though, and allocated the array
incorrectly.
- Fix briefly showing inconsistent progress statistics
for `ANALYZE` on inherited tables
(Heikki Linnakangas)
[](992d2ca81)

The block-level counters should be reset to zero at the same time we
update the current-relation field.
- Fix the background writer to report any WAL writes it makes to the
statistics counters (Nazir Bilal Yavuz)
[](4a97a43a7)
- Fix confusion about forced-flush behavior
in `pgstat_report_wal()`
(Ryoga Yoshida, Michael Paquier)
[](280f70221)

This could result in some statistics about WAL I/O being forgotten
in a shutdown.
- Fix statistics tracking of temporary-table extensions (Karina
Litskevich, Andres Freund)
[](c4758649b)

These were counted as normal-table writes when they should be
counted as temp-table writes.
- When `track_io_timing` is enabled, include the
time taken by relation extension operations as write time
(Nazir Bilal Yavuz)
[](2308f18c0)
- Track the dependencies of cached `CALL` statements,
and re-plan them when needed (Tom Lane)
[](055f786ea)

DDL commands, such as replacement of a function that has been
inlined into a `CALL` argument, can create the need
to re-plan a `CALL` that has been cached by
PL/pgSQL.  That was not happening, leading to misbehavior or strange
errors such as "cache lookup failed".
- Avoid a possible pfree-a-NULL-pointer crash after an error in
OpenSSL connection setup (Sergey Shinderuk)
[](f720875a4)
- Track nesting depth correctly when
inspecting `RECORD`-type Vars from outer query levels
(Richard Guo)
[](53630f12d)

This oversight could lead to assertion failures, core dumps,
or "bogus varno" errors.
- Track hash function and negator function dependencies of
ScalarArrayOpExpr plan nodes (David Rowley)
[](1a6900e58)

In most cases this oversight was harmless, since these functions
would be unlikely to disappear while the node's original operator
remains present.
- Fix error-handling bug in `RECORD` type cache management
(Thomas Munro)
[](f899c7f1e)

An out-of-memory error occurring at just the wrong point could leave
behind inconsistent state that would lead to an infinite loop.
- Treat out-of-memory failures as fatal while reading WAL
(Michael Paquier)
[](a06efbc3a)

Previously this would be treated as a bogus-data condition, leading
to the conclusion that we'd reached the end of WAL, which is
incorrect and could lead to inconsistent WAL replay.
- Fix possible recovery failure due to trying to allocate memory based
on a bogus WAL record length field (Thomas Munro, Michael Paquier)
[](ce497f648)
[](10d0591ea)
- Fix "could not duplicate handle" error occurring on
Windows when `min_dynamic_shared_memory` is set
above zero (Thomas Munro)
[](174ccda5e)
- Fix order of operations in `GenericXLogFinish`
(Jeff Davis)
[](b8963e8a2)

This code violated the conditions required for crash safety by
writing WAL before marking changed buffers dirty.  No core code uses
this function, but extensions do (`contrib/bloom`
does, for example).
- Remove incorrect assertion in PL/Python exception handling
(Alexander Lakhin)
[](f171430f0)
- Fix pg_dump to dump the
new `run_as_owner` option of subscriptions
(Philip Warner)
[](67738dbf9)

Due to this oversight, subscriptions would always be restored
with `run_as_owner` set
to `false`, which is not equivalent to their
behavior in pre-v16 releases.
- Fix pg_restore so that selective restores
will include both table-level and column-level ACLs for selected
tables (Euler Taveira, Tom Lane)
[](aaaf8fbb6)

Formerly, only the table-level ACL would get restored if both types
were present.
- Add logic to pg_upgrade to check for use
of `abstime`, `reltime`,
and `tinterval` data types (lvaro Herrera)
[](fb9ddd0fa)

These obsolete data types were removed
in PostgreSQL version 12, so check to
make sure they aren't present in an older database before claiming
it can be upgraded.
- Avoid false "too many client connections" errors
in pgbench on Windows (Noah Misch)
[](06ff06484)
- Fix vacuumdb's handling of
multiple `-N` switches (Nathan Bossart, Kuwamura
Masaki)
[](2143d96dc)

Multiple `-N` switches should exclude tables
in multiple schemas, but in fact excluded nothing due to faulty
construction of a generated query.
- Fix vacuumdb to honor
its `--buffer-usage-limit` option in analyze-only
mode (Ryoga Yoshida, David Rowley)
[](f7dbdab05)
- In `contrib/amcheck`, do not report interrupted
page deletion as corruption (Noah Misch)
[](3c6a05b80)

This fix prevents false-positive reports of "the first child
of leftmost target page is not leftmost of its
level", "block NNNN is not leftmost"
or "left link/right link pair in index XXXX not in
agreement".  They appeared
if amcheck ran after an unfinished btree
index page deletion and before `VACUUM` had cleaned
things up.
- Fix failure of `contrib/btree_gin` indexes
on `interval` columns,
when an indexscan using the ``LogicalRepLauncherDSA`](#wait-event-lwlock-table)
and `LogicalRepLauncherHash`.

#### Utility Commands

- Add [`EXPLAIN`](#sql-explain)
option `GENERIC_PLAN` to display the generic plan
for a parameterized query (Laurenz Albe)
[](3c05284d8)
- Allow a [`COPY FROM`](#sql-copy)
value to map to a column's `DEFAULT` (Israel
Barth Rubio)
[](9f8377f7a)
- Allow [`COPY`](#sql-copy)
into foreign tables to add rows in batches (Andrey Lepikhov,
Etsuro Fujita)
[](97da48246)

This is controlled by the [postgres_fdw](#postgres-fdw)
option [`batch_size`](#postgres-fdw-options-cost-estimation).
- Allow the `STORAGE` type to be specified by [`CREATE TABLE`](#sql-createtable)
(Teodor Sigaev, Aleksander Alekseev)
[](784cedda0)
[](b9424d014)

Previously only [`ALTER
TABLE`](#sql-altertable) could control this.
- Allow [truncate triggers](#sql-createtrigger)
on foreign tables (Yugo Nagata)
[](3b00a944a)
- Allow [`VACUUM`](#sql-vacuum) and [vacuumdb](#app-vacuumdb)
to only process [`TOAST`](#storage-toast) tables
(Nathan Bossart)
[](4211fbd84)

This is accomplished by having [`VACUUM`](#sql-vacuum)
turn off `PROCESS_MAIN` or by [vacuumdb](#app-vacuumdb)
using the `--no-process-main` option.
- Add [`VACUUM`](#sql-vacuum)
options to skip or update all [frozen](#vacuum-for-wraparound) statistics (Tom Lane,
Nathan Bossart)
[](a46a7011b)

The options are `SKIP_DATABASE_STATS` and
`ONLY_DATABASE_STATS`.
- Change [`REINDEX
DATABASE`](#sql-reindex) and [`REINDEX SYSTEM`](#sql-reindex)
to no longer require an argument (Simon Riggs)
[](2cbc3c17a)
[](0a5f06b84)

Previously the database name had to be specified.
- Allow [`CREATE
STATISTICS`](#sql-createstatistics) to generate a statistics name if none
is specified (Simon Riggs)
[](624aa2a13)

#### Data Types

- Allow non-decimal [integer
literals](#sql-syntax-bit-strings) (Peter Eisentraut)
[](6fcda9aba)

For example, `0x42F`, `0o273`,
and `0b100101`.
- Allow [`NUMERIC`](#datatype-numeric)
to process hexadecimal, octal, and binary integers of any size
(Dean Rasheed)
[](6dfacbf72)

Previously only unquoted eight-byte integers were supported with
these non-decimal bases.
- Allow underscores in integer and numeric [constants](#sql-syntax-bit-strings) (Peter Eisentraut,
Dean Rasheed)
[](faff8f8e4)

This can improve readability for long strings of digits.
- Accept the spelling `+infinity` in datetime input
(Vik Fearing)
[](2ceea5adb)
- Prevent the specification of `epoch` and
`infinity` together with other fields in datetime
strings (Joseph Koshakow)
[](bcc704b52)
- Remove undocumented support for date input in the form
`Y`year`M`month`D`day``
(Joseph Koshakow)
[](5b3c59535)
- Add functions [`pg_input_is_valid()`](#functions-info-validity-table)
and `pg_input_error_info()` to check for type
conversion errors (Tom Lane)
[](1939d2628)
[](b8da37b3a)

#### General Queries

- Allow subqueries in the `FROM` clause to omit
aliases (Dean Rasheed)
[](bcedd8f5f)
- Add support for enhanced numeric literals in
SQL/JSON paths (Peter Eisentraut)
[](102a5c164)

For example, allow hexadecimal, octal, and binary integers and
underscores between digits.

#### Functions

- Add SQL/JSON constructors (Nikita Glukhov,
Teodor Sigaev, Oleg Bartunov, Alexander Korotkov, Amit Langote)
[](7081ac46a)

The new functions [`JSON_ARRAY()`](#functions-json-creation-table),
[`JSON_ARRAYAGG()`](#functions-aggregate-table),
`JSON_OBJECT()`, and
`JSON_OBJECTAGG()` are part of the
SQL standard.
- Add SQL/JSON object checks (Nikita Glukhov,
Teodor Sigaev, Oleg Bartunov, Alexander Korotkov, Amit Langote,
Andrew Dunstan)
[](6ee30209a)

The [`IS
JSON`](#functions-sqljson-misc) checks include checks for values, arrays,
objects, scalars, and unique keys.
- Allow JSON string parsing to use vector
operations (John Naylor)
[](0a8de93a4)
- Improve the handling of full text highlighting function [`ts_headline()`](#textsearch-functions-table)
for `OR` and `NOT` expressions
(Tom Lane)
[](5a617d75d)
- Add functions to add, subtract, and generate
`timestamptz` values in a specified time zone (Przemyslaw
Sztoch, Gurjeet Singh)
[](75bd846b6)

The functions are [`date_add()`](#functions-datetime-table),
`date_subtract()`, and [`generate_series()`](#functions-srf-series).
- Change [`date_trunc(unit,
timestamptz, time_zone)`](#functions-datetime-table) to be an immutable
function (Przemyslaw Sztoch)
[](533e02e92)

This allows the creation of expression indexes using this function.
- Add server variable [`SYSTEM_USER`](#functions-info-session-table)
(Bertrand Drouvot)
[](0823d061b)

This reports the authentication method and its authenticated user.
- Add functions [`array_sample()`](#array-functions-table)
and `array_shuffle()` (Martin Kalcher)
[](888f2ea0a)
- Add aggregate function [`ANY_VALUE()`](#functions-aggregate-table)
which returns any value from a set (Vik Fearing)
[](2ddab010c)
- Add function [`random_normal()`](#functions-math-random-table)
to supply normally-distributed random numbers (Paul Ramsey)
[](38d81760c)
- Add error function [`erf()`](#functions-math-func-table)
and its complement `erfc()` (Dean Rasheed)
[](d5d574146)
- Improve the accuracy of numeric [`power()`](#functions-math-func-table)
for integer exponents (Dean Rasheed)
[](40c7fcbbe)
- Add [`XMLSERIALIZE()`](#datatype-xml-creating)
option `INDENT` to pretty-print its output
(Jim Jones)
[](483bdb2af)
- Change [`pg_collation_actual_version()`](#functions-admin-collation)
to return a reasonable value for the default collation (Jeff Davis)
[](10932ed5e)

Previously it returned `NULL`.
- Allow [`pg_read_file()`](#functions-admin-genfile-table)
and `pg_read_binary_file()` to ignore missing
files (Kyotaro Horiguchi)
[](283129e32)
- Add byte specification (`B`) to [`pg_size_bytes()`](#functions-admin-dbsize)
(Peter Eisentraut)
[](ce1215d9b)
- Allow [`to_reg`](#functions-info-catalog-table)*
functions to accept numeric OIDs as input
(Tom Lane)
[](3ea7329c9)

#### [PL/pgSQL](#plpgsql)

- Add the ability to get the current function's OID
in PL/pgSQL (Pavel Stehule)
[](d3d53f955)

This is accomplished with [`GET DIAGNOSTICS
variable = PG_ROUTINE_OID`](#plpgsql-statements-diagnostics).

#### [libpq](#libpq)

- Add libpq connection option [`require_auth`](#libpq-connect-require-auth)
to specify a list of acceptable authentication methods (Jacob
Champion)
[](3a465cc67)

This can also be used to disallow certain authentication methods.
- Allow multiple libpq-specified hosts
to be randomly selected (Jelte Fennema)
[](7f5b19817)
[](0a16512d4)

This is enabled with [`load_balance_hosts=random`](#libpq-connect-load-balance-hosts)
and can be used for load balancing.
- Add libpq option [`sslcertmode`](#libpq-connect-sslcertmode)
to control transmission of the client certificate (Jacob Champion)
[](36f40ce2d)

The option values are `disable`,
`allow`, and `require`.
- Allow libpq to use the system certificate
pool for certificate verification (Jacob Champion, Thomas Habets)
[](8eda73146)

This is enabled with [`sslrootcert=system`](#libpq-connect-sslrootcert),
which also enables [`sslmode=verify-full`](#libpq-connect-sslmode).

#### Client Applications

- Allow [`ECPG`](#ecpg)
variable declarations to use typedef names that match unreserved
SQL keywords (Tom Lane)
[](83f1c7b74)

This change does prevent keywords which match C typedef names from
being processed as keywords in later `EXEC SQL`
blocks.

##### [app-psql](#app-psql)

- Allow psql to control the maximum
width of header lines in expanded format (Platon Pronko)
[](a45388d6e)

This is controlled by [`xheader_width`](#app-psql-meta-command-pset-xheader-width).
- Add psql command [`\drg`](#app-psql-meta-command-drg)
to show role membership details (Pavel Luzanov)
[](d913928c9)
[](d65ddaca9)

The `Member of` output column has been removed
from `\du` and `\dg` because
this new command displays this information in more detail.
- Allow psql's access privilege commands
to show system objects (Nathan Bossart)
[](d913928c9)
[](d65ddaca9)

The options are [`\dpS`](#app-psql-meta-command-dp-lc)
and [`\zS`](#app-psql-meta-command-z).
- Add `FOREIGN` designation
to psql [`\d+`](#app-psql-meta-command-d)
for foreign table children and partitions (Ian Lawrence Barwick)
[](bd95816f7)
- Prevent [`\df+`](#app-psql-meta-command-df-uc)
from showing function source code (Isaac Morland)
[](3dfae91f7)

Function bodies are more easily viewed with [`\sf`](#app-psql-meta-command-sf).
- Allow psql to submit queries using
the extended query protocol (Peter Eisentraut)
[](5b66de343)

Passing arguments to such queries is done
using the new psql [`\bind`](#app-psql-meta-command-bind)
command.
- Allow psql [`\watch`](#app-psql-meta-command-watch)
to limit the number of executions (Andrey Borodin)
[](00beecfe8)

The `\watch` options can now be named when
specified.
- Detect invalid values for psql [`\watch`](#app-psql-meta-command-watch),
and allow zero to specify no delay (Andrey Borodin)
[](6f9ee74d4)
- Allow psql scripts to obtain the exit
status of shell commands and queries
(Corey Huinker, Tom Lane)
[](b0d8f2d98)
[](31ae2aa9d)

The new psql control variables are [`SHELL_ERROR`](#app-psql-variables-shell-error)
and [`SHELL_EXIT_CODE`](#app-psql-variables-shell-exit-code).
- Various psql tab completion improvements
(Vignesh C, Aleksander Alekseev, Dagfinn Ilmari Mannsåker,
Shi Yu, Michael Paquier, Ken Kato, Peter Smith)
[](f6c750d31)
[](4cbe57974)
[](6afcab6ac)
[](9aa58d48f)
[](3cf2f7af7)
[](2ea5de296)
[](07f7237c2)
[](9d0cf5749)
[](a3bc631ea)
[](2ff5ca86e)
[](9e1e9d656)
[](96c498d2f)

##### [pg_dump](#app-pgdump)

- Add pg_dump control of dumping child
tables and partitions (Gilles Darold)
[](a563c24c9)

The new options are `--table-and-children`,
`--exclude-table-and-children`, and
`--exclude-table-data-and-children`.
- Add LZ4 and
Zstandard compression to
pg_dump (Georgios Kokolatos, Justin
Pryzby)
- Allow pg_dump and [pg_basebackup](#app-pgbasebackup)
to use `long` mode for compression (Justin Pryzby)
[](0da243fed)
[](0070b66fe)
[](84adc8e20)
[](2820adf77)
- Improve pg_dump to accept a more
consistent compression syntax (Georgios Kokolatos)
[](5e73a6048)

Options like `--compress=gzip:5`.

#### Server Applications

- Add [initdb](#app-initdb)
option to set server variables for the duration of
initdb and all future server starts
(Tom Lane)
[](3e51b278d)

The option is `-c name=value`.
- Add options to [createuser](#app-createuser)
to control more user options (Shinya Kato)
[](08951a7c9)
[](2dcd1578c)

Specifically, the new options control the valid-until date,
bypassing of row-level security, and role membership.
- Deprecate [createuser](#app-createuser)
option `--role` (Nathan Bossart)
[](2dcd1578c)
[](381d19b3e)

This option could be easily confused with new
createuser role membership options,
so option `--member-of` has been added with the
same functionality.  The `--role` option can still
be used.
- Allow control of [vacuumdb](#app-vacuumdb)
schema processing (Gilles Darold)
[](7781f4e3e)

These are controlled by options `--schema` and
`--exclude-schema`.
- Use new [`VACUUM`](#sql-vacuum)
options to improve the performance of [vacuumdb](#app-vacuumdb)
(Tom Lane, Nathan Bossart)
[](a46a7011b)
- Have [pg_upgrade](#pgupgrade)
set the new cluster's locale and encoding (Jeff Davis)
[](9637badd9)

This removes the requirement that the new cluster be created with
the same locale and encoding settings.
- Add [pg_upgrade](#pgupgrade)
option to specify the default transfer mode (Peter Eisentraut)
[](746915c68)

The option is `--copy`.
- Improve [pg_basebackup](#app-pgbasebackup)
to accept numeric compression options (Georgios Kokolatos,
Michael Paquier)
[](d18655cc0)

Options like `--compress=server-5` are now supported.
- Fix [pg_basebackup](#app-pgbasebackup)
to handle tablespaces stored in the `PGDATA` directory
(Robert Haas)
[](363e8f911)
- Add [pg_waldump](#pgwaldump)
option `--save-fullpage` to dump full page images
(David Christensen)
[](d497093cb)
- Allow [pg_waldump](#pgwaldump)
options `-t`/`--timeline` to accept
hexadecimal values (Peter Eisentraut)
[](4c8044c04)
- Add support for progress reporting to [pg_verifybackup](#app-pgverifybackup)
(Masahiko Sawada)
[](d07c2948b)
- Allow [pg_rewind](#app-pgrewind)
to properly track timeline changes (Heikki Linnakangas)
[](009eeee74)
[](0a0500207)

Previously if pg_rewind was run after
a timeline switch but before a checkpoint was issued, it might
incorrectly determine that a rewind was unnecessary.
- Have [pg_receivewal](#app-pgreceivewal)
and [pg_recvlogical](#app-pgrecvlogical)
cleanly exit on `SIGTERM` (Christoph Berg)
[](8b60db774)

This signal is often used by systemd.

#### Source Code

- Build ICU support by default (Jeff Davis)
[](fcb21b3ac)

This removes [build
flag](#installation) `--with-icu` and adds flag
`--without-icu`.
- Add support for SSE2 (Streaming SIMD Extensions
2) vector operations on x86-64 architectures (John Naylor)
[](56f2c7b58)
- Add support for Advanced SIMD (Single
Instruction Multiple Data) (NEON) instructions
on ARM architectures (Nathan Bossart)
[](82739d4a8)
- Have Windows
binaries built with MSVC use
`RandomizedBaseAddress` (ASLR)
(Michael Paquier)
[](36389a060)

This was already enabled on MinGW builds.
- Prevent extension libraries from exporting their symbols by default
(Andres Freund, Tom Lane)
[](089480c07)
[](8cf64d35e)

Functions that need to be called from the core backend
or other extensions must now be explicitly marked
`PGDLLEXPORT`.
- Require Windows 10 or
newer versions (Michael Paquier, Juan José Santamaría Flecha)
[](495ed0ef2)

Previously Windows Vista and
Windows XP were supported.
- Require Perl version 5.14 or later
(John Naylor)
[](4c1532763)
- Require Bison version 2.3 or later
(John Naylor)
[](b086a47a2)
- Require Flex version 2.5.35 or later
(John Naylor)
[](8b878bffa)
- Require MIT Kerberos for
GSSAPI support (Stephen Frost)
[](f7431bca8)
- Remove support for Visual Studio 2013
(Michael Paquier)
[](6203583b7)
- Remove support for HP-UX
(Thomas Munro)
[](9db300ce6)
- Remove support for HP/Intel Itanium
(Thomas Munro)
[](0ad5b48e5)
- Remove support for M68K,
M88K, M32R,
and SuperH CPU
architectures (Thomas Munro)
[](718aa43a4)
[](14168d3c6)
- Remove [libpq](#libpq)
support for SCM credential authentication
(Michael Paquier)
[](98ae2c84a)

Backend support for this authentication method was removed in
PostgresSQL 9.1.
- Add [meson](#install-meson)
build system (Andres Freund, Nazir Bilal Yavuz, Peter Eisentraut)
[](e6927270c)

This eventually will replace the Autoconf
and Windows-based
MSVC build systems.
- Allow control of the location of the
openssl binary used by the build system
(Peter Eisentraut)
[](c8e4030d1)

Make finding openssl
program a configure or
meson option
- Add build option to allow testing of small table segment sizes
(Andres Freund)
[](d3b111e32)

The build options are [`--with-segsize-blocks`](#configure-option-with-segsize)
and `-Dsegsize_blocks`.
- Add [pgindent](#source) options
(Andrew Dunstan)
[](b90f0b574)
[](62e1e28bf)
[](124937163)
[](a1c4cd6f2)
[](068a243b7)
[](dab07e8c6)
[](b16259b3c)

The new options are `--show-diff`,
`--silent-diff`, `--commit`,
and `--help`, and allow multiple
`--exclude` options.  Also require the typedef file
to be explicitly specified.  Options `--code-base`
and `--build` were also removed.
- Add [pg_bsd_indent](#source)
source code to the main tree (Tom Lane)
[](4e831f4ce)
- Improve make_ctags and
make_etags (Yugo Nagata)
[](d1e2a380c)
- Adjust [`pg_attribute`](#catalog-pg-attribute)
columns for efficiency (Peter Eisentraut)
[](90189eefc)

#### Additional Modules

- Improve use of extension-based indexes on boolean columns (Zongliang
Quan, Tom Lane)
[](ff720a597)
- Add support for Daitch-Mokotoff Soundex to [fuzzystrmatch](#fuzzystrmatch)
(Dag Lem)
[](a290378a3)
- Allow [auto_explain](#auto-explain)
to log values passed to parameterized statements (Dagfinn Ilmari
Mannsåker)
[](d4bfe4128)

This affects queries using server-side [`PREPARE`](#sql-prepare)/[`EXECUTE`](#sql-execute)
and client-side parse/bind.  Logging is controlled by [`auto_explain.log_parameter_max_length`](#auto-explain-configuration-parameters-log-parameter-max-length);
by default query parameters will be logged with no length
restriction.
- Have [auto_explain](#auto-explain)'s
`log_verbose` mode honor the value of [`compute_query_id`](#guc-compute-query-id)
(Atsushi Torikoshi)
[](9d2d9728b)

Previously even if
`compute_query_id` was enabled, [`log_verbose`](#auto-explain-configuration-parameters-log-verbose)
was not showing the query identifier.
- Change the maximum length of [ltree](#ltree) labels
from 256 to 1000 and allow hyphens (Garen Torikian)
[](b1665bf01)
- Have [`pg_stat_statements`](#pgstatstatements)
normalize constants used in utility commands (Michael Paquier)
[](daa8365a9)

Previously constants appeared instead of placeholders, e.g.,
`$1`.
- Add [pg_walinspect](#pgwalinspect)
function [`pg_get_wal_block_info()`](#pgwalinspect-funcs-pg-get-wal-block-info)
to report WAL block information (Michael Paquier,
Melanie Plageman, Bharath Rupireddy)
[](c31cf1c03)
[](9ecb134a9)
[](122376f02)
[](df4f3ab51)
- Change how [pg_walinspect](#pgwalinspect)
functions [`pg_get_wal_records_info()`](#pgwalinspect-funcs-pg-get-wal-records-info)
and [`pg_get_wal_stats()`](#pgwalinspect-funcs-pg-get-wal-stats)
interpret ending LSNs (Bharath Rupireddy)
[](5c1b66280)

Previously ending LSNs which represent
nonexistent WAL locations would generate
an error, while they will now be interpreted as the end of the
WAL.
- Add detailed descriptions of WAL records in [pg_walinspect](#pgwalinspect)
and [pg_waldump](#pgwaldump)
(Melanie Plageman, Peter Geoghegan)
[](7d8219a44)
[](1c453cfd8)
[](96149a180)
[](50547a3fa)
- Add [pageinspect](#pageinspect)
function [`bt_multi_page_stats()`](#pageinspect-b-tree-funcs)
to report statistics on multiple pages (Hamid Akhtar)
[](1fd3dd204)

This is similar to `bt_page_stats()` except it
can report on a range of pages.
- Add empty range output column to [pageinspect](#pageinspect)
function [`brin_page_items()`](#pageinspect-brin-funcs)
(Tomas Vondra)
[](1fd3dd204)
- Redesign archive modules to be more flexible (Nathan Bossart)
[](35739b87d)

Initialization changes will require modules written for older
versions of Postgres to be updated.
- Correct inaccurate [pg_stat_statements](#pgstatstatements)
row tracking extended query protocol statements (Sami Imseih)
[](1d477a907)
- Add [pg_buffercache](#pgbuffercache)
function `pg_buffercache_usage_counts()` to
report usage totals (Nathan Bossart)
[](f3fa31327)
- Add [pg_buffercache](#pgbuffercache)
function `pg_buffercache_summary()` to report
summarized buffer statistics (Melih Mutlu)
[](2589434ae)
- Allow the schemas of required extensions to be
referenced in extension scripts using the new syntax
`@extschema:referenced_extension_name@`
(Regina Obe)
[](72a5b1fc8)
- Allow required extensions to
be marked as non-relocatable using [`no_relocate`](#extend-extensions-files-no-relocate)
(Regina Obe)
[](72a5b1fc8)

This allows `@extschema:referenced_extension_name@`
to be treated as a constant for the lifetime of the extension.

##### [postgres_fdw](#postgres-fdw)

- Allow postgres_fdw to do aborts in
parallel (Etsuro Fujita)
[](983ec2300)

This is enabled with
postgres_fdw option [`parallel_abort`](#postgres-fdw-options-transaction-management).
- Make [`ANALYZE`](#sql-analyze)
on foreign postgres_fdw tables more
efficient (Tomas Vondra)
[](8ad51b5f4)

The postgres_fdw option [`analyze_sampling`](#postgres-fdw-options-cost-estimation)
controls the sampling method.
- Restrict shipment of [`reg`](#datatype-oid)* type constants
in postgres_fdw to those referencing
built-in objects or extensions marked as shippable (Tom Lane)
[](31e5b5029)
- Have postgres_fdw and [dblink](#dblink) handle
interrupts during connection establishment (Andres Freund)
[](e4602483e)

### Acknowledgments

The following individuals (in alphabetical order) have contributed
to this release as patch authors, committers, reviewers, testers,
or reporters of issues.

## Prior Releases

Release notes for prior release branches can be found at
[`https://www.postgresql.org/docs/release/`](https://www.postgresql.org/docs/release/)
