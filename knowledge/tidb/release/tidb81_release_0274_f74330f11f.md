# Data migration features in Lightning and DM

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.4.0.md`
- Source Title: `TiDB 5.4 Release Notes`
- Source Heading Path: `TiDB 5.4 Release Notes > New features > Data migration`
- Source Line Ranges: `273-323`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `lightning`
- Topic Tags: `data-migration`, `lightning`, `parallel-import`, `duplicate-resolution`, `relay-log`, `collation`, `openapi`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0274_f74330f11f`
- Source ID: `tidb-docs-8.1:releases/release-5.4.0.md#data-migration`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `05413505b32ea8eb79637a82045fe663e7ea093d7291cc6810293fff3b519b9c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.4.0#data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.4 data migration release details about TiDB Lightning parallel import settings, duplicate resolution, DM relay log behavior, collation handling, transfer source, or DM OpenAPI.
- Retrieval Keywords: incremental-import, meta-schema-name, parallel import mode, tables with data, lightning_metadata, duplicate resolution, Local-backend mode, duplicated data, enable-relay, start-relay, stop-relay, relay log, source configuration, collation_compatible, loose, strict, transfer source, DM OpenAPI, adding data sources, managing tasks
- Follow-up Guidance: The source links to user documents for TiDB Lightning task configuration, TiDB Lightning error resolution, DM relay log, DM task configuration file advanced options, and DM OpenAPI.
- Classification Note: This is a release-note chunk for the data migration area, centered on DM and related Lightning features introduced or optimized in TiDB 5.4.0.

## Official Source Content

### Data migration

- **TiDB Lightning introduces a new feature to determine whether to allow importing data to tables with data**

    TiDB Lightning introduces a configuration item`incremental-import`. It determines whether to allow importing data to tables with data. The default value is `false`. When using the parallel import mode, you must set the configuration to `true`.

    [User document](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task)

- **TiDB Lightning introduces the schema name that stores the meta information for parallel import**

    TiDB Lightning introduces the `meta-schema-name` configuration item. In parallel import mode, this parameter specifies the schema name that stores the meta information for each TiDB Lightning instance in the target cluster. By default, the value is "lightning_metadata". The value set for this parameter must be the same for each TiDB Lightning instance that participates in the same parallel import; otherwise, the correctness of the imported data cannot be ensured.

  [User document](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task)

- **TiDB Lightning introduces duplicate resolution**

    In Local-backend mode, TiDB Lightning outputs duplicated data before the data import is completed, and then removes that duplicated data from the database. You can resolve the duplicated data after the import is completed and select suitable data to insert according to application rules. It is recommended to clean upstream data sources based on duplicated data to avoid data inconsistency caused by duplicated data encountered in the subsequent incremental data migration phase.

    [User document](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-error-resolution)

- **Optimize the usage of relay log in TiDB Data Migration (DM)**

    - Recover the `enable-relay` switch in the `source` configuration.

    - Support dynamically enabling and disabling relay log using the `start-relay` and `stop-relay` commands.

    - Bind the status of relay log to `source`. `source` keeps its original status of being enabled or disabled after it is migrated to any DM-worker.

    - Move the storage path of relay log to the DM-worker configuration file.

    [User document](https://docs.pingcap.com/tidb/stable/dm/relay-log)

- **Optimize the processing of [collation](https://docs.pingcap.com/tidb/stable/character-set-and-collation) in DM**

    Add the `collation_compatible` configuration item. The value options are `loose` (default) and `strict`:

    - If your application does not have strict requirements on collation, and the collation of query results can be different between the upstream and downstream, you can use the default `loose` mode to avoid reporting errors.
    - If your application has strict requirements on collation, and the collation must be consistent between the upstream and downstream, you can use the `strict` mode. However, if the downstream does not support the upstream's default collation, the data replication might report errors.

   [User document](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full#task-configuration-file-template-advanced)

- **Optimize `transfer source` in DM to support running replication tasks smoothly**

    When the DM-worker nodes have an unbalanced load, the `transfer source` command can be used to manually transfer the configuration of a `source` to another load. After the optimization, the `transfer source` command simplifies the manual operation. You can smoothly transfer the source instead of pausing all related tasks, because DM completes other operations internally.

- **DM OpenAPI becomes generally available (GA)**

    DM supports daily management via API, including adding data sources and managing tasks. In v5.4.0, DM OpenAPI becomes GA.

    [User document](https://docs.pingcap.com/tidb/stable/dm/dm-open-api)
