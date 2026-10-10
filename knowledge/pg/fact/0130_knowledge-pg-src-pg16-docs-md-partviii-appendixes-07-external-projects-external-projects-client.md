# Client Interfaces; Administration Tools; Procedural Languages; Extensions

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/07_external_projects.md`
- Source Title: `07 external projects`
- Source Heading Path: `External Projects > Client Interfaces; Administration Tools; Procedural Languages; Extensions`
- Source Line Ranges: `8-29, 30-36, 37-54, 55-67`
- Chunk ID: `pg16_fact_0130_d72d6314ad`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d710c3b2705120977bb6db3a38771d863a510e38d636284a657aeca95211d07b`

## Retrieval Guidance

- Use When: Find related PostgreSQL ecosystem projects and interfaces.
- Retrieval Keywords: external projects, client interfaces, administration tools, procedural languages, PostgreSQL extensions
- Follow-up Guidance: Consult each external project documentation for current behavior and support status.
- Classification Note: The appendix lists related external projects and does not provide PostgreSQL operational configuration or diagnostics.

## Official Source Content

## Client Interfaces

There are only two client interfaces included in the base
PostgreSQL distribution:

- [libpq](#libpq) is included because it is the
primary C language interface, and because many other client interfaces
are built on top of it.
- [ECPG](#ecpg) is included because it depends on the
server-side SQL grammar, and is therefore sensitive to changes in
PostgreSQL itself.

All other language interfaces are external projects and are distributed
separately. A
[list of language interfaces](https://wiki.postgresql.org/wiki/List_of_drivers)
is maintained on the PostgreSQL wiki. Note that some of these packages are
not released under the same license as PostgreSQL.
For more information on each language interface, including licensing terms,
refer to its website and documentation.

[](https://wiki.postgresql.org/wiki/List_of_drivers)

## Administration Tools

There are several administration tools available for
PostgreSQL. The most popular is
[pgAdmin](https://www.pgadmin.org/),
and there are several commercially available ones as well.

## Procedural Languages

PostgreSQL includes several procedural
languages with the base distribution: [PL/pgSQL](#plpgsql), [PL/Tcl](#pltcl),
[PL/Perl](#plperl), and [PL/Python](#plpython).

In addition, there are a number of procedural languages that are developed
and maintained outside the core PostgreSQL
distribution. A list of
[procedural languages](https://wiki.postgresql.org/wiki/PL_Matrix)
is maintained on the PostgreSQL wiki. Note that some of these projects are
not released under the same license as PostgreSQL.
For more information on each procedural language, including licensing
information, refer to its website
and documentation.

[](https://wiki.postgresql.org/wiki/PL_Matrix)

## Extensions

PostgreSQL is designed to be easily extensible. For
this reason, extensions loaded into the database can function
just like features that are built in. The
`contrib/` directory shipped with the source code
contains several extensions, which are described in
[contrib](#contrib).  Other extensions are developed
independently, like [PostGIS](https://postgis.net/).  Even
PostgreSQL replication solutions can be developed
externally. For example,  [Slony-I](https://www.slony.info) is a popular
primary/standby replication solution that is developed independently
from the core project.
