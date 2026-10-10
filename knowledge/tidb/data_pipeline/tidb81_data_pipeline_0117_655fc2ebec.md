# Copy a schema using Dumpling and TiDB Lightning

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-faq.md`
- Source Title: `TiDB Lightning FAQs`
- Source Heading Path: `TiDB Lightning FAQs > How can I use TiDB Lightning and Dumpling to copy a schema?`
- Source Line Ranges: `177-220`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `dumpling`, `tiup`, `tidb`
- Topic Tags: `schema-copy`, `backup-and-import`, `mydumper-files`, `schema-remap`, `table-patterns`, `configuration-file`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0117_655fc2ebec`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-faq.md#how-can-i-use-tidb-lightning-and-dumpling-to-copy-a-schema`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2d5c3dda262ebf533c65ec57fcf7a73e56036ee07ffd67b8b579adc3947742ee`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-faq#how-can-i-use-tidb-lightning-and-dumpling-to-copy-a-schema
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-faq.md

## Retrieval Guidance

- Use When: Use this chunk when the question is how to copy one schema to a new schema by exporting with Dumpling and remapping schema names during TiDB Lightning import.
- Retrieval Keywords: How can I use TiDB Lightning and Dumpling to copy a schema, copy the `test` schema into `test2`, tiup dumpling -B test -o /tmp/bck1, /tmp/tidb-lightning.toml, backend = "tidb", data-source-dir = "/tmp/bck1", [[mydumper.files]], pattern = '^[a-z]*\.(.*)\.[0-9]*\.sql$', pattern = '^[a-z]*\.(.*)\-schema\.sql$', schema = 'test2', table = '$1', type = 'sql', type = 'table-schema', filename is used to determine the name of the table, tiup tidb-lightning -config /tmp/tidb-lightning.toml
- Follow-up Guidance: The chunk provides the exact Dumpling command, the full `tidb-lightning.toml` example with `[[mydumper.files]]` remapping rules, and the final `tiup tidb-lightning` import command.
- Classification Note: This is classified as data_pipeline because it describes an end-to-end export and import workflow for copying schema definition and table data between schemas.

## Official Source Content

## How can I use TiDB Lightning and Dumpling to copy a schema?

If you want to copy both the schema definition and table data from one schema to a new schema, follow the steps in this section. In this example, you'll learn how to make a copy of the `test` schema into a new schema called `test2`.

1. Create a backup of the original schema with `-B test` to select only the schema that you need.

    ```
    tiup dumpling -B test -o /tmp/bck1
    ```

2. Create a `/tmp/tidb-lightning.toml` file with the following content:

    ```toml
    [tidb]
    host = "127.0.0.1"
    port = 4000
    user = "root"
    
    [tikv-importer]
    backend = "tidb"
    
    [mydumper]
    data-source-dir = "/tmp/bck1"
    
    [[mydumper.files]]
    pattern = '^[a-z]*\.(.*)\.[0-9]*\.sql$'
    schema = 'test2'
    table = '$1'
    type = 'sql'
    
    [[mydumper.files]]
    pattern = '^[a-z]*\.(.*)\-schema\.sql$'
    schema = 'test2'
    table = '$1'
    type = 'table-schema'
    ```

    In this configuration file, set `schema = 'test2'` as you want to use a different schema name than the one used in the original dump. The filename is used to determine the name of the table.

3. Use this configuration file to run the import.

    ```
    tiup tidb-lightning -config /tmp/tidb-lightning.toml
    ```
