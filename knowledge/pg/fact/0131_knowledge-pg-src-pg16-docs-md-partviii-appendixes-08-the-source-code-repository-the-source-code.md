# Getting the Source via Git; Git

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/08_the_source_code_repository.md`
- Source Title: `08 the source code repository`
- Source Heading Path: `The Source Code Repository > Getting the Source via Git; Git`
- Source Line Ranges: `19-25, 26-53`
- Chunk ID: `pg16_fact_0131_eb622e7288`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `135bafc4dc7f8d01425d2bcaeebbc6053714a87d870cd7fd47de7a0b56f96991`

## Retrieval Guidance

- Use When: Locate or retrieve PostgreSQL source code.
- Retrieval Keywords: PostgreSQL source repository, git.postgresql.org, Git, source code
- Follow-up Guidance: Use current upstream project pages if exact repository URLs or branch names must be verified.
- Classification Note: The appendix describes where and how PostgreSQL source code is hosted and accessed.

## Official Source Content

## Getting the Source via Git

With Git you will make a copy of the entire code repository
on your local machine, so you will have access to all history and branches
offline. This is the fastest and most flexible way to develop or test
patches.

## Git

You will need an installed version of Git, which you can
get from [](https://git-scm.com). Many systems already
have a recent version of Git installed by default, or
available in their package distribution system.

To begin using the Git repository, make a clone of the official mirror:

```
git clone https://git.postgresql.org/git/postgresql.git
```

This will copy the full repository to your local machine, so it may take
a while to complete, especially if you have a slow Internet connection.
The files will be placed in a new subdirectory `postgresql` of
your current directory.

Whenever you want to get the latest updates in the system, `cd`
into the repository, and run:

```
git fetch
```

Git can do a lot more things than just fetch the source. For
more information, consult the Git man pages, or see the
website at [](https://git-scm.com).
