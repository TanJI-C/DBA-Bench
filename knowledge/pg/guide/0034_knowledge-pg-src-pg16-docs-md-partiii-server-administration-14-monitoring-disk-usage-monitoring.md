# Determining Disk Usage

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/14_monitoring_disk_usage.md`
- Source Title: `Monitoring Disk Usage`
- Source Heading Path: `Monitoring Disk Usage > Determining Disk Usage`
- Source Line Ranges: `6-93`
- Chunk ID: `pg16_guide_0034_327747a752`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `714a1d85ec78b80148288d261f3c74dc7f6969a6a37460134ef9899ef20a58c3`

## Retrieval Guidance

- Use When: 诊断磁盘占用、找最大表/索引或解释 relpages 数据来源。
- Retrieval Keywords: disk usage, pg_relation_filepath, relpages, pg_class, TOAST size, index size, largest tables
- Follow-up Guidance: 优先使用 pg_size_* 函数；catalog relpages 需 VACUUM/ANALYZE 后更准。
- Classification Note: 提供用 SQL、oid2name 或 catalog 查询表/TOAST/索引大小的方法。

## Official Source Content

## Determining Disk Usage

Each table has a primary heap disk file where most of the data is
stored. If the table has any columns with potentially-wide values,
there also might be a TOAST file associated with the table,
which is used to store values too wide to fit comfortably in the main
table (see [storage-toast](#storage-toast)).  There will be one valid index
on the TOAST table, if present. There also might be indexes
associated with the base table.  Each table and index is stored in a
separate disk file — possibly more than one file, if the file would
exceed one gigabyte.  Naming conventions for these files are described
in [storage-file-layout](#storage-file-layout).

You can monitor disk space in three ways:
using the SQL functions listed in [functions-admin-dbsize](#functions-admin-dbsize),
using the [oid2name](#oid2name) module, or
using manual inspection of the system catalogs.
The SQL functions are the easiest to use and are generally recommended.
The remainder of this section shows how to do it by inspection of the
system catalogs.

Using psql on a recently vacuumed or analyzed database,
you can issue queries to see the disk usage of any table:

```
SELECT pg_relation_filepath(oid), relpages FROM pg_class WHERE relname = 'customer';

pg_relation_filepath | relpages
----------------------+----------
base/16384/16806     |       60
(1 row)
```

Each page is typically 8 kilobytes. (Remember, `relpages`
is only updated by `VACUUM`, `ANALYZE`, and
a few DDL commands such as `CREATE INDEX`.)  The file path name
is of interest if you want to examine the table's disk file directly.

To show the space used by TOAST tables, use a query
like the following:

```
SELECT relname, relpages
FROM pg_class,
(SELECT reltoastrelid
FROM pg_class
WHERE relname = 'customer') AS ss
WHERE oid = ss.reltoastrelid OR
oid = (SELECT indexrelid
FROM pg_index
WHERE indrelid = ss.reltoastrelid)
ORDER BY relname;

relname        | relpages
----------------------+----------
pg_toast_16806       |        0
pg_toast_16806_index |        1
```

You can easily display index sizes, too:

```
SELECT c2.relname, c2.relpages
FROM pg_class c, pg_class c2, pg_index i
WHERE c.relname = 'customer' AND
c.oid = i.indrelid AND
c2.oid = i.indexrelid
ORDER BY c2.relname;

relname      | relpages
-------------------+----------
customer_id_index |       26
```

It is easy to find your largest tables and indexes using this
information:

```
SELECT relname, relpages
FROM pg_class
ORDER BY relpages DESC;

relname        | relpages
----------------------+----------
bigtable             |     3290
customer             |     3144
```
