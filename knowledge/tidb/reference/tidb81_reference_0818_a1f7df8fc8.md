# Data import file and schema naming conventions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/naming-conventions-for-data-import.md`
- Source Title: `Naming Conventions for Data Import`
- Source Heading Path: `Naming Conventions for Data Import | Naming Conventions for Data Import > Naming conventions for schema files | Naming Conventions for Data Import > Naming conventions for data files | Naming Conventions for Data Import > Naming conventions for data files > CSV | Naming Conventions for Data Import > Naming conventions for data files > Parquet | Naming Conventions for Data Import > Naming conventions for data files > Aurora Snapshot | Naming Conventions for Data Import > Naming conventions for data files > SQL | Naming Conventions for Data Import > File pattern`
- Source Line Ranges: `5-125`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dumpling`, `shared`
- Topic Tags: `data-import`, `file-naming`, `schema-files`, `data-files`, `csv`, `parquet`, `aurora-snapshot`, `sql`, `compression`, `file-pattern`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0818_a1f7df8fc8`
- Source ID: `tidb-docs-8.1:tidb-cloud/naming-conventions-for-data-import.md#naming-conventions-for-data-import`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `801051ec268d9ade1ec00a0a193beadd6de85212deaae9ad9f0975ac8f7f5561`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/naming-conventions-for-data-import#naming-conventions-for-data-import
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/naming-conventions-for-data-import.md

## Retrieval Guidance

- Use When: Use this when you need the exact TiDB Cloud naming conventions for schema files or CSV, Parquet, Aurora Snapshot, and SQL data files used in data import, including when file pattern mapping applies.
- Retrieval Keywords: Naming Conventions for Data Import, schema file, database schema file, table schema file, ${db_name}-schema-create.sql, ${db_name}.${table_name}-schema.sql, CSV, ${db_name}.${table_name}${suffix}.csv.${compress}, Parquet, ${db_name}.${table_name}${suffix}.parquet, Aurora Snapshot, ${db_name}.${table_name}/, .parquet, SQL, ${db_name}.${table_name}${suffix}.sql.${compress}, file pattern, Mapping Settings, Advanced Settings, Snappy, official Snappy format, Dumpling
- Follow-up Guidance: If CSV or Parquet source files do not conform to the naming convention, the source says you can use the file pattern feature in Advanced Settings > Mapping Settings, while Aurora Snapshot and SQL data files do not support this feature.
- Classification Note: This is reference content because it enumerates the required file name patterns, optional suffix and compression formats, examples, and the scope of the file pattern feature for TiDB Cloud data import.

## Official Source Content

# Naming Conventions for Data Import

You can import data into TiDB Cloud in the following file formats: CSV, Parquet, Aurora Snapshot, and SQL. To make sure that your data is imported successfully, you need to prepare the following two types of files:

- **Schema file**. Prepare the database schema file (optional) and the table schema file, both in SQL format (`.sql`). If the table schema file is not provided, you need to create the corresponding table manually in the target database in advance.
- **Data file**. Prepare a data file that conforms to the naming conventions for importing data. If the data file name can not meet the requirements, it is recommended to use [**File Pattern**](#file-pattern) to perform the import task. Otherwise, the import task cannot scan the data files you want to import.
## Naming conventions for schema files

This section describes the naming conventions for database and table schema files. The naming conventions for schema files are the same for all the following types of source files: CSV, Parquet, Aurora Snapshot, and SQL.

The naming conventions for schema files are as follows:

- Database schema file (optional): `${db_name}-schema-create.sql`
- Table schema file: `${db_name}.${table_name}-schema.sql`

The following is an example of a database schema file:

- Name: `import_db-schema-create.sql`
- File content:

    ```sql
    CREATE DATABASE import_db;
    ```

The following is an example of a table schema file:

- Name: `import_db.test_table-schema.sql`
- File content:

    ```sql
    CREATE TABLE test_table (
        id INTEGER PRIMARY KEY,
        val VARCHAR(255)
    );
    ```
## Naming conventions for data files

This section describes the naming conventions for data files. Depending on the type of source files, the naming conventions for data files are different.
### CSV

When you import CSV files, name the data files as follows:

`${db_name}.${table_name}${suffix}.csv.${compress}`

`${suffix}` is optional and can be one of the following formats, where *`xxx`* can be any number:

- *`.xxx`*, such as `.01`
- *`._xxx_xxx_xxx`*, such as `._0_0_01`
- *`_xxx_xxx_xxx`*, such as `_0_0_01`

`${compress}` is the compression format and it is optional. TiDB Cloud supports the following formats: `.gzip`, `.gz`, `.zstd`, `.zst` and `.snappy`.

For example, the target database and table of all the following files are `import_db` and `test_table`:

- `import_db.test_table.csv`
- `import_db.test_table.01.csv`
- `import_db.test_table._0_0_01.csv`
- `import_db.test_table_0_0_01.csv`
- `import_db.test_table_0_0_01.csv.gz`

> **Note:**
>
> The Snappy compressed file must be in the [official Snappy format](https://github.com/google/snappy). Other variants of Snappy compression are not supported.
### Parquet

When you import Parquet files, name the data files as follows:

`${db_name}.${table_name}${suffix}.parquet` (`${suffix}` is optional)

For example:

- `import_db.test_table.parquet`
- `import_db.test_table.01.parquet`
### Aurora Snapshot

For Aurora Snapshot files, all files with the `.parquet` suffix in the `${db_name}.${table_name}/` folder conform to the naming convention. A data file name can contain any prefix consisting of "a-z, 0-9, - , _ , ." and suffix ".parquet".

For example:

- `import_db.test_table/mydata.parquet`
- `import_db.test_table/part001/mydata.parquet`
- `import_db.test_table/part002/mydata-part002.parquet`
### SQL

When you import SQL files, name the data files as follows:

`${db_name}.${table_name}${suffix}.sql.${compress}`

`${suffix}` is optional and can be one of the following formats, where *`xxx`* can be any number:

- *`.xxx`*, such as `.01`
- *`._xxx_xxx_xxx`*, such as `._0_0_01`
- *`_xxx_xxx_xxx`*, such as `_0_0_01`

`${compress}` is the compression format and it is optional. TiDB Cloud supports the following formats: `.gzip`, `.gz`, `.zstd`, `.zst` and `.snappy`.

For example:

- `import_db.test_table.sql`
- `import_db.test_table.01.sql`
- `import_db.test_table.01.sql.gz`

If the SQL file is exported through TiDB Dumpling with the default configuration, it conforms to the naming convention by default.

> **Note:**
>
> The Snappy compressed file must be in the [official Snappy format](https://github.com/google/snappy). Other variants of Snappy compression are not supported.
## File pattern

If the source data file of CSV or Parquet does not conform to the naming convention, you can use the file pattern feature to establish the name mapping relationship between the source data file and the target table. This feature does not support Aurora Snapshot and SQL data files.

- For CSV files, see **Advanced Settings** > **Mapping Settings** in [Step 4. Import CSV files to TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-csv-files#step-4-import-csv-files-to-tidb-cloud)
- For Parquet files, see **Advanced Settings** > **Mapping Settings** in [Step 4. Import Parquet files to TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/import-parquet-files#step-4-import-parquet-files-to-tidb-cloud)
