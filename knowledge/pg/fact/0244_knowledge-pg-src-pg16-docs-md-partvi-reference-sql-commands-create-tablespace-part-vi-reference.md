# CREATE TABLESPACE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/create_tablespace.md`
- Source Title: `create tablespace`
- Source Heading Path: `Part VI Reference > SQL Commands > CREATE TABLESPACE`
- Source Line Ranges: `1-108`
- Chunk ID: `pg16_fact_0244_42102cb5e6`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `6f0a6b2d4c258e0b5fc0a8dd6705ba6f3be5ff4620f127043a7d7a849674f6a1`

## Retrieval Guidance

- Use When: Use for tablespace creation syntax and location constraints.
- Retrieval Keywords: CREATE TABLESPACE, tablespace location, OWNER, storage location
- Follow-up Guidance: No section split needed.
- Classification Note: Tablespace object creation reference.

## Official Source Content

CREATE TABLESPACE
7
SQL - Language Statements

CREATE TABLESPACE
define a new tablespace

```
CREATE TABLESPACE `tablespace_name`
[ OWNER { `new_owner` | CURRENT_ROLE | CURRENT_USER | SESSION_USER } ]
LOCATION '`directory`'
[ WITH ( `tablespace_option` = `value` [, ... ] ) ]
```

## Description

`CREATE TABLESPACE` registers a new cluster-wide
tablespace.  The tablespace name must be distinct from the name of any
existing tablespace in the database cluster.

A tablespace allows superusers to define an alternative location on
the file system where the data files containing database objects
(such as tables and indexes) can reside.

A user with appropriate privileges can pass
`tablespace_name` to
`CREATE DATABASE`, `CREATE TABLE`,
`CREATE INDEX` or `ADD CONSTRAINT` to have the data
files for these objects stored within the specified tablespace.

> **Warning:**

> A tablespace cannot be used independently of the cluster in which it
> is defined;  see [manage-ag-tablespaces](#manage-ag-tablespaces).
>

## Parameters

**`tablespace_name`**
: The name of a tablespace to be created.  The name cannot
begin with `pg_`, as such names
are reserved for system tablespaces.

**`user_name`**
: The name of the user who will own the tablespace.  If omitted,
defaults to the user executing the command.  Only superusers
can create tablespaces, but they can assign ownership of tablespaces
to non-superusers.

**`directory`**
: The directory that will be used for the tablespace. The directory
must exist (`CREATE TABLESPACE` will not create it),
should be empty, and must be owned by the
PostgreSQL system user.  The directory must be
specified by an absolute path name.

**`tablespace_option`**
: A tablespace parameter to be set or reset.  Currently, the only
available parameters are `seq_page_cost`,
`random_page_cost`, `effective_io_concurrency`
and `maintenance_io_concurrency`.
Setting these values for a particular tablespace will override the
planner's usual estimate of the cost of reading pages from tables in
that tablespace, and the executor's prefetching behavior, as established
by the configuration parameters of the
same name (see [guc-seq-page-cost](#guc-seq-page-cost),
[guc-random-page-cost](#guc-random-page-cost),
[guc-effective-io-concurrency](#guc-effective-io-concurrency),
[guc-maintenance-io-concurrency](#guc-maintenance-io-concurrency)).  This may be useful if
one tablespace is located on a disk which is faster or slower than the
remainder of the I/O subsystem.

## Notes

`CREATE TABLESPACE` cannot be executed inside a transaction
block.

## Examples

To create a tablespace `dbspace` at file system location
`/data/dbs`, first create the directory using operating
system facilities and set the correct ownership:

```
mkdir /data/dbs
chown postgres:postgres /data/dbs
```

Then issue the tablespace creation command inside
PostgreSQL:

```
CREATE TABLESPACE dbspace LOCATION '/data/dbs';
```

To create a tablespace owned by a different database user, use a command
like this:

```
CREATE TABLESPACE indexspace OWNER genevieve LOCATION '/data/indexes';
```

## Compatibility

`CREATE TABLESPACE` is a PostgreSQL
extension.

## See Also
