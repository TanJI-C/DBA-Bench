# Upgrade TiUP components

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-management.md`
- Source Title: `Manage TiUP Components with TiUP Commands`
- Source Heading Path: `Manage TiUP Components with TiUP Commands > Upgrade components`
- Source Line Ranges: `82-114`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `tiup update`, `upgrade`, `nightly`, `self`, `force`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0515_14918fb239`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-management.md#upgrade-components`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d1263840fb7ea69847fd92b5ef94e5bf44409b70e60338d728c4efc848cfe90c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-management#upgrade-components
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-management.md

## Retrieval Guidance

- Use When: Use this chunk when you need to upgrade TiUP components, all components, nightly versions, or TiUP itself with `tiup update`.
- Retrieval Keywords: Upgrade components, tiup update, --all, --nightly, --self, --force, tiup update --all, tiup update --all --nightly, tiup update --self
- Follow-up Guidance: Examples cover upgrading all components to the latest versions, upgrading all components to the nightly version, and upgrading TiUP itself.
- Classification Note: This is operation content because it describes how to perform upgrades with `tiup update` and its flags.

## Official Source Content

## Upgrade components

After a new version of a component is published, you can use the `tiup update` command to upgrade this component. The usage of this command is basically the same as that of `tiup install`, except for the following flags:

- `--all`: Upgrades all components.
- `--nightly`: Upgrades to the nightly version.
- `--self`: Upgrades TiUP itself to the latest version.
- `--force`: Forcibly upgrades to the latest version.

Example 1: Upgrade all components to the latest versions.

```shell
tiup update --all
```

Example 2: Upgrade all components to the nightly version.

```shell
tiup update --all --nightly
```

Example 3: Upgrade TiUP to the latest version.

```shell
tiup update --self
```
