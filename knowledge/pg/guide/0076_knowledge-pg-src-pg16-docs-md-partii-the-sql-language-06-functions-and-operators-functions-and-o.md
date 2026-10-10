# Inspecting MCV Lists

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/06_functions_and_operators.md`
- Source Title: `Functions and Operators`
- Source Heading Path: `Functions and Operators > Statistics Information Functions > Inspecting MCV Lists`
- Source Line Ranges: `6773-6805`
- Chunk ID: `pg16_guide_0076_f1b056ed4c`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3c2b89df6369b880c5da004583e65ea1accab0439b03c9b71be56e7cfb487f4c`

## Retrieval Guidance

- Use When: Need to confirm whether multivariate MCV statistics explain planner selectivity estimates.
- Retrieval Keywords: pg_mcv_list_items, extended statistics, MCV list, pg_statistic_ext_data, selectivity estimate
- Follow-up Guidance: Create or refresh extended statistics if bad estimates are confirmed and the workload uses those column combinations.
- Classification Note: Shows pg_mcv_list_items for inspecting extended most-common-value statistics collected by CREATE STATISTICS.

## Official Source Content

## Statistics Information Functions

PostgreSQL provides a function to inspect complex
statistics defined using the `CREATE STATISTICS` command.

### Inspecting MCV Lists

```
`pg_mcv_list_items` ( `pg_mcv_list` ) setof record
```

`pg_mcv_list_items` returns a set of records describing
all items stored in a multi-column MCV list.  It
returns the following columns:

| Name | Type | Description |
| --- | --- | --- |
| `index` | `integer` | index of the item in the MCV list |
| `values` | `text[]` | values stored in the MCV item |
| `nulls` | `boolean[]` | flags identifying `NULL` values |
| `frequency` | `double precision` | frequency of this MCV item |
| `base_frequency` | `double precision` | base frequency of this MCV item |

The `pg_mcv_list_items` function can be used like this:

```
SELECT m.* FROM pg_statistic_ext join pg_statistic_ext_data on (oid = stxoid),
pg_mcv_list_items(stxdmcv) m WHERE stxname = 'stts';
```

Values of the `pg_mcv_list` type can be obtained only from the
`pg_statistic_ext_data`.`stxdmcv`
column.
