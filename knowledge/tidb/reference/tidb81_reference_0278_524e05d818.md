# Restore compatibility checks for collation and placement rules

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/backup-and-restore-faq.md`
- Source Title: `Backup & Restore FAQs`
- Source Heading Path: `Backup & Restore FAQs > Feature compatibility issues > Why is `new_collation_enabled` mismatch reported during restore? | Backup & Restore FAQs > Feature compatibility issues > Why does an error occur when I restore placement rules to a cluster?`
- Source Line Ranges: `120-132`
- Source Scope: `all`
- Primary Component: `br`
- Related Components: `tidb`
- Topic Tags: `restore`, `compatibility`, `collation`, `placement-rules`, `version-checks`, `requirements-check`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0278_524e05d818`
- Source ID: `tidb-docs-8.1:faq/backup-and-restore-faq.md#why-is-new-collation-enabled-mismatch-reported-during-restore`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `284e795335453ce0a6c0926221f99ad965ef9a0463f021ad037031cfb04f07e6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/backup-and-restore-faq#why-is-new-collation-enabled-mismatch-reported-during-restore
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/backup-and-restore-faq.md

## Retrieval Guidance

- Use When: You need restore compatibility details for `new_collation_enabled` mismatch checks or placement rule restore behavior in BR.
- Retrieval Keywords: new_collation_enabled, new_collations_enabled_on_first_bootstrap, --check-requirements=false, placement rules, --with-tidb-placement-mode=strict/ignore, strict, ignore, mysql.tidb
- Follow-up Guidance: If the configuration values are consistent, BR can skip the requirements check with `--check-requirements=false`; for placement rules, BR uses `--with-tidb-placement-mode=strict/ignore`.
- Classification Note: This chunk is a reference FAQ entry about restore compatibility checks and placement rule restore options.

## Official Source Content

### Why is `new_collation_enabled` mismatch reported during restore?

Since TiDB v6.0.0, the default value of [`new_collations_enabled_on_first_bootstrap`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#new_collations_enabled_on_first_bootstrap) has changed from `false` to `true`. BR backs up the `new_collation_enabled` configuration in the `mysql.tidb` table of the upstream cluster and then checks whether the value of this configuration is consistent between the upstream and downstream clusters. If the value is consistent, BR safely restores the data backed up in the upstream cluster to the downstream cluster. If the value is inconsistent, BR does not perform the data restore and reports an error.

Suppose that you have backed up the data in a TiDB cluster of an earlier version of v6.0.0, and you want to restore this data to a TiDB cluster of v6.0.0 or later versions. In this situation, you need to manually check whether the value of `new_collations_enabled_on_first_bootstrap` is consistent between the upstream and downstream clusters:

- If the value is consistent, you can add `--check-requirements=false` to the restore command to skip this configuration check.
- If the value is inconsistent, and you forcibly perform the restore, BR reports a data validation error.
### Why does an error occur when I restore placement rules to a cluster?

Before v6.0.0, BR does not support [placement rules](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql). Starting from v6.0.0, BR supports placement rules and introduces a command-line option `--with-tidb-placement-mode=strict/ignore` to control the backup and restore mode of placement rules. With the default value `strict`, BR imports and validates placement rules, but ignores all placement rules when the value is `ignore`.
