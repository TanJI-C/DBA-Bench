# Part VII: Internals

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVII_internals/README.md`
- Source Title: `Part VII: Internals`
- Source Heading Path: `Part VII: Internals`
- Source Line Ranges: `1-27`
- Chunk ID: `pg16_fact_0095_81f62899a6`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `3d6bc0ea5c107c8acecbb0654c9e9cc9c106b535ea8b28de4b1935ea2219052d`

## Retrieval Guidance

- Use When: Route retrieval to internal PostgreSQL implementation documentation.
- Retrieval Keywords: PostgreSQL internals, system catalogs, system views, planner statistics, storage, WAL
- Follow-up Guidance: Use chapter-specific records for planner, catalog, storage, or access-method details.
- Classification Note: This part-level index lists internals chapters and contains no direct configuration, diagnostic, or remediation content.

## Official Source Content

# Part VII: Internals

- [Overview of PostgreSQL Internals](01_overview_of_postgresql_internals.md)
- [System Catalogs](02_system_catalogs.md)
- [System Views](03_system_views.md)
- [Frontend/Backend Protocol](04_frontendbackend_protocol.md)
- [PostgreSQL Coding Conventions](05_postgresql_coding_conventions.md)
- [Native Language Support](06_native_language_support.md)
- [Writing a Procedural Language Handler](07_writing_a_procedural_language_handler.md)
- [Writing a Foreign Data Wrapper](08_writing_a_foreign_data_wrapper.md)
- [Writing a Table Sampling Method](09_writing_a_table_sampling_method.md)
- [Writing a Custom Scan Provider](10_writing_a_custom_scan_provider.md)
- [Genetic Query Optimizer](11_genetic_query_optimizer.md)
- [Table Access Method Interface Definition](12_table_access_method_interface_definition.md)
- [Index Access Method Interface Definition](13_index_access_method_interface_definition.md)
- [Generic WAL Records](14_generic_wal_records.md)
- [Custom WAL Resource Managers](15_custom_wal_resource_managers.md)
- [B-Tree Indexes](16_b-tree_indexes.md)
- [GiST Indexes](17_gist_indexes.md)
- [SP-GiST Indexes](18_sp-gist_indexes.md)
- [GIN Indexes](19_gin_indexes.md)
- [BRIN Indexes](20_brin_indexes.md)
- [Hash Indexes](21_hash_indexes.md)
- [Database Physical Storage](22_database_physical_storage.md)
- [System Catalog Declarations and Initial Contents](24_system_catalog_declarations_and_initial_contents.md)
- [How the Planner Uses Statistics](25_how_the_planner_uses_statistics.md)
- [Backup Manifest Format](26_backup_manifest_format.md)
