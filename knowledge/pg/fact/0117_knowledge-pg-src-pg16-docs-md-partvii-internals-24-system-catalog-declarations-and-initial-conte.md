# System Catalog Declarations and Initial Contents

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVII_internals/24_system_catalog_declarations_and_initial_contents.md`
- Source Title: `System Catalog Declarations and Initial Contents`
- Source Heading Path: `System Catalog Declarations and Initial Contents`
- Source Line Ranges: `1-148`
- Chunk ID: `pg16_fact_0117_2ddc9a3e37`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2540d96deb25d068c565f32d31b3d296f027f203f752a705ce3d2743775b6004`

## Retrieval Guidance

- Use When: Work on PostgreSQL source-level catalog definitions or extension compatibility with catalog declarations.
- Retrieval Keywords: system catalog declarations, catalog header, BKI, genbki, initial contents, pg_proc.dat
- Follow-up Guidance: Use system catalog records for runtime catalog field meanings.
- Classification Note: The file describes how PostgreSQL source declares and initializes system catalogs.

## Official Source Content

# System Catalog Declarations and Initial Contents

PostgreSQL uses many different system catalogs
to keep track of the existence and properties of database objects, such as
tables and functions.  Physically there is no difference between a system
catalog and a plain user table, but the backend C code knows the structure
and properties of each catalog, and can manipulate it directly at a low
level.  Thus, for example, it is inadvisable to attempt to alter the
structure of a catalog on-the-fly; that would break assumptions built into
the C code about how rows of the catalog are laid out.  But the structure
of the catalogs can change between major versions.

The structures of the catalogs are declared in specially formatted C
header files in the `src/include/catalog/` directory of
the source tree.  For each catalog there is a header file
named after the catalog (e.g., `pg_class.h`
for `pg_class`), which defines the set of columns
the catalog has, as well as some other basic properties such as its OID.

Many of the catalogs have initial data that must be loaded into them
during the "bootstrap" phase
of initdb, to bring the system up to a point
where it is capable of executing SQL commands.  (For
example, `pg_class.h` must contain an entry for itself,
as well as one for each other system catalog and index.)  This
initial data is kept in editable form in data files that are also stored
in the `src/include/catalog/` directory.  For example,
`pg_proc.dat` describes all the initial rows that must
be inserted into the `pg_proc` catalog.

To create the catalog files and load this initial data into them, a
backend running in bootstrap mode reads a BKI
(Backend Interface) file containing commands and initial data.
The `postgres.bki` file used in this mode is prepared
from the aforementioned header and data files, while building
a PostgreSQL distribution, by a Perl script
named `genbki.pl`.
Although it's specific to a particular PostgreSQL
release, `postgres.bki` is platform-independent and is
installed in the `share` subdirectory of the
installation tree.

`genbki.pl` also produces a derived header file for
each catalog, for example `pg_class_d.h` for
the `pg_class` catalog.  This file contains
automatically-generated macro definitions, and may contain other macros,
enum declarations, and so on that can be useful for client C code that
reads a particular catalog.

Most PostgreSQL developers don't need to be directly concerned with
the BKI file, but almost any nontrivial feature
addition in the backend will require modifying the catalog header files
and/or initial data files.  The rest of this chapter gives some
information about that, and for completeness describes
the BKI file format.

## System Catalog Declaration Rules

The key part of a catalog header file is a C structure definition
describing the layout of each row of the catalog.  This begins with
a `CATALOG` macro, which so far as the C compiler is
concerned is just shorthand for `typedef struct
FormData_`catalogname``.
Each field in the struct gives rise to a catalog column.
Fields can be annotated using the BKI property macros described
in `genbki.h`, for example to define a default value
for a field or mark it as nullable or not nullable.
The `CATALOG` line can also be annotated, with some
other BKI property macros described in `genbki.h`, to
define other properties of the catalog as a whole, such as whether
it is a shared relation.

The system catalog cache code (and most catalog-munging code in general)
assumes that the fixed-length portions of all system catalog tuples are
in fact present, because it maps this C struct declaration onto them.
Thus, all variable-length fields and nullable fields must be placed at
the end, and they cannot be accessed as struct fields.
For example, if you tried to
set `pg_type`.`typrelid`
to be NULL, it would fail when some piece of code tried to reference
`typetup->typrelid` (or worse,
`typetup->typelem`, because that follows
`typrelid`).  This would result in
random errors or even segmentation violations.

As a partial guard against this type of error, variable-length or
nullable fields should not be made directly visible to the C compiler.
This is accomplished by wrapping them in `#ifdef
CATALOG_VARLEN` ... `#endif` (where
`CATALOG_VARLEN` is a symbol that is never defined).
This prevents C code from carelessly trying to access fields that might
not be there or might be at some other offset.
As an independent guard against creating incorrect rows, we
require all columns that should be non-nullable to be marked so
in `pg_attribute`.  The bootstrap code will
automatically mark catalog columns as `NOT NULL`
if they are fixed-width and are not preceded by any nullable or
variable-width column.
Where this rule is inadequate, you can force correct marking by using
`BKI_FORCE_NOT_NULL`
and `BKI_FORCE_NULL` annotations as needed.

Frontend code should not include any `pg_xxx.h`
catalog header file, as these files may contain C code that won't compile
outside the backend.  (Typically, that happens because these files also
contain declarations for functions
in `src/backend/catalog/` files.)
Instead, frontend code may include the corresponding
generated `pg_xxx_d.h` header, which will contain
OID `#define`s and any other data that might be of use
on the client side.  If you want macros or other code in a catalog header
to be visible to frontend code, write `#ifdef
EXPOSE_TO_CLIENT_CODE` ... `#endif` around that
section to instruct `genbki.pl` to copy that section
to the `pg_xxx_d.h` header.

A few of the catalogs are so fundamental that they can't even be created
by the BKI `create` command that's
used for most catalogs, because that command needs to write information
into these catalogs to describe the new catalog.  These are
called *bootstrap* catalogs, and defining one takes
a lot of extra work: you have to manually prepare appropriate entries for
them in the pre-loaded contents of `pg_class`
and `pg_type`, and those entries will need to be
updated for subsequent changes to the catalog's structure.
(Bootstrap catalogs also need pre-loaded entries
in `pg_attribute`, but
fortunately `genbki.pl` handles that chore nowadays.)
Avoid making new catalogs be bootstrap catalogs if at all possible.

## System Catalog Initial Data

Each catalog that has any manually-created initial data (some do not)
has a corresponding `.dat` file that contains its
initial data in an editable format.

### Data File Format

Each `.dat` file contains Perl data structure literals
that are simply eval'd to produce an in-memory data structure consisting
of an array of hash references, one per catalog row.
A slightly modified excerpt from `pg_database.dat`
will demonstrate the key features:

```

[
