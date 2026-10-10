# Filter exported databases tables and rows

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dumpling-overview.md`
- Source Title: `Dumpling Overview`
- Source Heading Path: `Use Dumpling to Export Data > Export data from TiDB or MySQL > Filter the exported data | Use Dumpling to Export Data > Export data from TiDB or MySQL > Filter the exported data > Use the `--where` option to filter data | Use Dumpling to Export Data > Export data from TiDB or MySQL > Filter the exported data > Use the `--filter` option to filter data | Use Dumpling to Export Data > Export data from TiDB or MySQL > Filter the exported data > Use the `-B` or `-T` option to filter data`
- Source Line Ranges: `245-282`
- Source Scope: `shared`
- Primary Component: `dumpling`
- Related Components: `sql`
- Topic Tags: `filtering`, `where-clause`, `table-filter`, `database-selection`, `table-selection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0097_54b12422ea`
- Source ID: `tidb-docs-8.1:dumpling-overview.md#filter-the-exported-data`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `569c620e30ef3a46506fb5fe98a12ea86e40ed6c04e0c84f44676b2be24f99c7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dumpling-overview#filter-the-exported-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dumpling-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the documented Dumpling options for filtering exported databases, tables, or rows during export.
- Retrieval Keywords: --where, --filter, -B, -T, table filter, .gitignore, id < 100, employees.*, *.WorkOrder, employees.WorkOrder, system databases, cannot use the --where parameter together with --sql, The --filter option and the -T option cannot be used at the same time
- Follow-up Guidance: The source notes that --where cannot be used together with --sql, and that -T only accepts the complete form database-name.table-name.
- Classification Note: This is classified as configuration because the content focuses on Dumpling command options that control which rows, tables, and databases are exported.

## Official Source Content

### Filter the exported data
#### Use the `--where` option to filter data

By default, Dumpling exports all databases except system databases (including `mysql`, `sys`, `INFORMATION_SCHEMA`, `PERFORMANCE_SCHEMA`, `METRICS_SCHEMA`, and `INSPECTION_SCHEMA`). You can use `--where <SQL where expression>` to select the records to be exported.

```shell
tiup dumpling -u root -P 4000 -h 127.0.0.1 -o /tmp/test --where "id < 100"
```

The above command exports the data that matches `id < 100` from each table. Note that you cannot use the `--where` parameter together with `--sql`.
#### Use the `--filter` option to filter data

Dumpling can filter specific databases or tables by specifying the table filter with the `--filter` option. The syntax of table filters is similar to that of `.gitignore`. For details, see [Table Filter](https://docs.pingcap.com/tidb/stable/table-filter).

```shell
tiup dumpling -u root -P 4000 -h 127.0.0.1 -o /tmp/test -r 200000 --filter "employees.*" --filter "*.WorkOrder"
```

The above command exports all the tables in the `employees` database and the `WorkOrder` tables in all databases.
#### Use the `-B` or `-T` option to filter data

Dumpling can also export specific databases with the `-B` option or specific tables with the `-T` option.

> **Note:**
>
> - The `--filter` option and the `-T` option cannot be used at the same time.
> - The `-T` option can only accept a complete form of inputs like `database-name.table-name`, and inputs with only the table name are not accepted. Example: Dumpling cannot recognize `-T WorkOrder`.

Examples:

- `-B employees` exports the `employees` database.
- `-T employees.WorkOrder` exports the `employees.WorkOrder` table.
