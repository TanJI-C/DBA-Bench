# Compatibility changes for placement, SPM, and DM behavior

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.0.0-dmr.md`
- Source Title: `TiDB 6.0.0 Release Notes`
- Source Heading Path: `TiDB 6.0.0 Release Notes > Compatibility changes > Others`
- Source Line Ranges: `539-560`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `dm`, `ticdc`, `br`, `tiflash`
- Topic Tags: `compatibility`, `placement-policy`, `spm-binding`, `openapi`, `full-import`, `on-duplicate`, `upgrade`, `system-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0290_9f26a8a914`
- Source ID: `tidb-docs-8.1:releases/release-6.0.0-dmr.md#others`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a44f217c6625f8986e92b1a9e632f9611c7c7f2775fde7f9060dd7ba3d4342ca`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.0.0-dmr#others
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.0.0-dmr.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about TiDB 6.0.0 compatibility changes involving placement policies, SPM binding status values, DM OpenAPI or full import conflict handling, dmctl version matching, or stricter validation of noop system variable values.
- Retrieval Keywords: TiDB 6.0.0 compatibility changes, CREATE PLACEMENT POLICY, ALTER PLACEMENT POLICY, VOTERS, VOTER_CONSTRAINTS, information_schema.placement_rules, information_schema.placement_policies, placement_checks, tidb_placement_mode, TIDB_DIRECT_PLACEMENT, TiFlash replicas, SPM binding status using enabled disabled, DM OpenAPI task management, loader.<name>.on-duplicate, full import phase, dmctl v6.0.0, incorrect values for system variables, noop system variables
- Follow-up Guidance: The chunk also points to the new DM OpenAPI documentation for adapting task management interfaces and states that after upgrading DM to v6.0.0, `dmctl` should also be upgraded to v6.0.0.
- Classification Note: This is a release compatibility chunk because it lists behavior changes and renamed or replaced identifiers across placement policy syntax, SPM binding status values, DM interfaces and parameters, and system variable validation in TiDB 6.0.0.

## Official Source Content

### Others

- The data placement policy has the following compatibility changes:
    - Binding is not supported. The direct placement option is removed from the syntax.
    - The `CREATE PLACEMENT POLICY` and `ALTER PLACEMENT POLICY` statements no longer support the `VOTERS` and `VOTER_CONSTRAINTS` placement options.
    - TiDB migration tools (TiDB Binlog, TiCDC, and BR) are now compatible with placement rules. The placement option is moved to a special comment in TiDB Binlog.
    - The `information_schema.placement_rules` system table is renamed to `information_schema.placement_policies`. This table now only displays information about placement policies.
    - The `placement_checks` system variable is replaced by `tidb_placement_mode`.
    - It is prohibited to add partitions with placement rules to tables that have TiFlash replicas.
    - Remove the `TIDB_DIRECT_PLACEMENT` column from the `INFORMATION_SCHEMA` table.
- The `status` value of SQL plan management (SPM) binding is modified:
    - Remove `using`.
    - Add `enabled` (available) to replace `using`.
    - Add `disabled` (unavailable).
- DM modifies the OpenAPI interface
    - Because of internal mechanism changes, the interface related to task management cannot be compatible with the previous experimental version. You need to refer to the new [DM OpenAPI documentation](https://docs.pingcap.com/tidb/stable/dm/dm-open-api) for adaptation.
- DM changes the methods to resolve conflicts during the full import phase
    - A `loader.<name>.on-duplicate` parameter is added. The default value is `replace`, which means using the new data to replace the existing data. If you want to keep the previous behavior, you can set the value to `error`. This parameter only controls the behavior during the full import phase.
- To use DM, you should use the corresponding version of `dmctl`
    - Due to internal mechanism changes, after upgrading DM to v6.0.0, you should also upgrade `dmctl` to v6.0.0.
- For v5.4 and earlier versions, TiDB allows incorrect values for some noop system variables. Starting from v6.0.0, TiDB disallows setting incorrect values for system variables. [#31538](https://github.com/pingcap/tidb/issues/31538)
