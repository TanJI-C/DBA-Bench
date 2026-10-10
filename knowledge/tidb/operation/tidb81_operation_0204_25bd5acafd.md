# TiUP deployment and maintenance improvements

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.0-rc.md`
- Source Title: `TiDB 5.0 RC Release Notes`
- Source Heading Path: `TiDB 5.0 RC Release Notes > Deployment and maintenance`
- Source Line Ranges: `184-189`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `deployment`, `maintenance`, `ansible-import`, `edit-config`, `mirror`, `merge`, `local-mirror`, `installation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0204_25bd5acafd`
- Source ID: `tidb-docs-8.1:releases/release-5.0.0-rc.md#deployment-and-maintenance`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `031246acc34c3fa7ba62b97492222c7513fd8215abda1595a7a111d89ac05bc5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.0-rc#deployment-and-maintenance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.0-rc.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiUP deployment or maintenance changes involving TiDB Ansible import visibility in `tiup cluster edit-config`, `ansible-imported-configs`, or local mirror and `merge` command enhancements.
- Retrieval Keywords: Deployment and maintenance, TiUP, TiDB Ansible, ansible-imported-configs, tiup cluster edit-config, imported configuration, editor interface, mirror command, merge multiple mirrors into one, publishing components in the local mirror, adding component owners in the local mirror, merge command, multiple installation packages into one, tiup-server, self-built mirror, tiup mirror set, local mirror
- Follow-up Guidance: The source explains that imported TiDB Ansible configuration is now placed both in `ansible-imported-configs` and in the editor interface, and that `tiup mirror set` can publish the self-built mirror by setting the current mirror to the local mirror.
- Classification Note: This is classified as operation because the content describes deployment and maintenance workflow improvements in TiUP.

## Official Source Content

## Deployment and maintenance

+ Previously, when the configuration information of TiDB Ansible was imported to TiUP, TiUP put the user configuration in the `ansible-imported-configs` directory. When users later needed to edit the configuration using `tiup cluster edit-config`, the imported configuration was not displayed in the editor interface, which could be confusing for users. In TiDB v5.0, when TiDB Ansible configuration is imported, TiUP puts the configuration information both in `ansible-imported-configs` and in the editor interface. With this improvement, users can see the imported configuration when they are editing the cluster configuration.
+ Enhanced `mirror` command that supports merging multiple mirrors into one, publishing components in the local mirror, and adding component owners in the local mirror. [#814](https://github.com/pingcap/tiup/issues/814)
    + For a large enterprise, especially for the financial industry, any change in the production environment is given careful consideration. It can be troublesome if each version requires users to use a CD for installation. In TiDB v5.0, the `merge` command of TiUP supports merging multiple installation packages into one, which makes the installation easier.
    + In v4.0, users had to start tiup-server to publish the self-built mirror, which was not convenient enough. In v5.0, users can publish the self-built mirror simply by using `tiup mirror set` to set the current mirror to the local mirror.
