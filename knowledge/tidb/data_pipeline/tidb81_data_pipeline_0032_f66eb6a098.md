# CSV import prerequisites, file layout, and target schema preparation

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-from-csv-files-to-tidb.md`
- Source Title: `Migrate Data from CSV Files to TiDB`
- Source Heading Path: `Migrate Data from CSV Files to TiDB | Migrate Data from CSV Files to TiDB > Prerequisites | Migrate Data from CSV Files to TiDB > Step 1. Prepare the CSV files | Migrate Data from CSV Files to TiDB > Step 2. Create the target table schema`
- Source Line Ranges: `5-38`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`
- Topic Tags: `csv`, `prerequisites`, `file-naming`, `schema`, `ddl`, `data-source`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0032_f66eb6a098`
- Source ID: `tidb-docs-8.1:migrate-from-csv-files-to-tidb.md#migrate-data-from-csv-files-to-tidb`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `50af789825cf2a42a4e7fbf4b7e2abfadd1dc5a51d26ccc85a31f592522858d0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-from-csv-files-to-tidb#migrate-data-from-csv-files-to-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-from-csv-files-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented prerequisites, CSV file naming rules, recursive source directory behavior, or the required target schema files before importing CSV data with TiDB Lightning.
- Retrieval Keywords: Install TiDB Lightning, privileges of the target database, ${db_name}.${table_name}.csv, ${db_name}.${table_name}.003.csv, recursively searches for all .csv files, ${db_name}-schema-create.sql, ${db_name}.${table_name}-schema.sql, CREATE DATABASE, CREATE TABLE, create the target table schema manually
- Follow-up Guidance: The source continues with creating a `tidb-lightning.toml` configuration file for the import.
- Classification Note: This is classified as data_pipeline because the content covers prerequisites, data source file layout, and target schema preparation for migrating CSV data into TiDB.

## Official Source Content

# Migrate Data from CSV Files to TiDB

This document describes how to migrate data from CSV files to TiDB.

TiDB Lightning can read data from CSV files and other delimiter formats, such as tab-separated values (TSV). For other flat file data sources, you can also refer to this document and migrate data to TiDB.
## Prerequisites

- [Install TiDB Lightning](https://docs.pingcap.com/tidb/stable/migration-tools).
- [Get the target database privileges required for TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-requirements#privileges-of-the-target-database).
## Step 1. Prepare the CSV files

Put all the CSV files in the same directory. If you need TiDB Lightning to recognize all CSV files, the file names should meet the following requirements:

- If a CSV file contains the data for an entire table, name the file `${db_name}.${table_name}.csv`.
- If the data of one table is separated into multiple CSV files, append a numeric suffix to these CSV files. For example, `${db_name}.${table_name}.003.csv`. The numeric suffixes can be inconsecutive but must be in ascending order. You also need to add extra zeros before the number to ensure all the suffixes are in the same length.

TiDB Lightning recursively searches for all `.csv` files in this directory and its subdirectories.
## Step 2. Create the target table schema

Because CSV files do not contain schema information, before importing data from CSV files into TiDB, you need to create the target table schema. You can create the target table schema by either of the following two methods:

* **Method 1**: create the target table schema using TiDB Lightning.

    Create SQL files that contain the required DDL statements:

    - Add `CREATE DATABASE` statements in the `${db_name}-schema-create.sql` files.
    - Add `CREATE TABLE` statements in the `${db_name}.${table_name}-schema.sql` files.

* **Method 2**: create the target table schema manually.
