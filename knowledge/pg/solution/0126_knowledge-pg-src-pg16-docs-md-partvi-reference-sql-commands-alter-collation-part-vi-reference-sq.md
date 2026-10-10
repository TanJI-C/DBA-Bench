# REFRESH VERSION / Notes

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_collation.md`
- Source Title: `alter collation`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER COLLATION > REFRESH VERSION / Notes`
- Source Line Ranges: `48-115`
- Chunk ID: `pg16_solution_0126_76989e62f1`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `633c271056d2eb55896de163cd7143f38b7e80520b12b5b7e26057e4bbcc0f75`

## Retrieval Guidance

- Use When: Use after collation mismatch warnings and dependency checks show objects must be rebuilt and catalog version refreshed.
- Retrieval Keywords: ALTER COLLATION REFRESH VERSION, collation version mismatch, rebuild affected objects, REINDEX collation
- Follow-up Guidance: Confirm affected objects with dependency query and rebuild indexes/objects before refreshing version.
- Classification Note: REFRESH VERSION is used after identifying collation version mismatch and rebuilding affected objects; it is a post-confirmation maintenance/remediation step.

## Official Source Content

## Notes

When a collation object is created, the provider-specific version of the
collation is recorded in the system catalog.  When the collation is used,
the current version is
checked against the recorded version, and a warning is issued when there is
a mismatch, for example:

```
WARNING:  collation "xx-x-icu" has version mismatch
DETAIL:  The collation in the database was created using version 1.2.3.4, but the operating system provides version 2.3.4.5.
HINT:  Rebuild all objects affected by this collation and run ALTER COLLATION pg_catalog."xx-x-icu" REFRESH VERSION, or build PostgreSQL with the right library version.
```

A change in collation definitions can lead to corrupt indexes and other
problems because the database system relies on stored objects having a
certain sort order.  Generally, this should be avoided, but it can happen
in legitimate circumstances, such as when upgrading the operating system
to a new major version or when
using `pg_upgrade` to upgrade to server binaries linked
with a newer version of ICU.  When this happens, all objects depending on
the collation should be rebuilt, for example,
using `REINDEX`.  When that is done, the collation version
can be refreshed using the command `ALTER COLLATION ... REFRESH
VERSION`.  This will update the system catalog to record the
current collation version and will make the warning go away.  Note that this
does not actually check whether all affected objects have been rebuilt
correctly.

When using collations provided by `libc`, version
information is recorded on systems using the GNU C library (most Linux
systems), FreeBSD and Windows.  When using collations provided by ICU, the
version information is provided by the ICU library and is available on all
platforms.

> **Note:**

> When using the GNU C library for collations, the C library's version
> is used as a proxy for the collation version.  Many Linux distributions
> change collation definitions only when upgrading the C library, but this
> approach is imperfect as maintainers are free to back-port newer
> collation definitions to older C library releases.
>

>

> When using Windows for collations, version information is only available
> for collations defined with BCP 47 language tags such as
> `en-US`.
>

For the database default collation, there is an analogous command
`ALTER DATABASE ... REFRESH COLLATION VERSION`.

The following query can be used to identify all collations in the current
database that need to be refreshed and the objects that depend on them:

```

SELECT pg_describe_object(refclassid, refobjid, refobjsubid) AS "Collation",
pg_describe_object(classid, objid, objsubid) AS "Object"
FROM pg_depend d JOIN pg_collation c
ON refclassid = 'pg_collation'::regclass AND refobjid = c.oid
WHERE c.collversion <> pg_collation_actual_version(c.oid)
ORDER BY 1, 2;

```
