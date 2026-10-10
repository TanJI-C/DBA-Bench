# Sequelize incompatibilities and support resources

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-third-party-tools-compatibility.md`
- Source Title: `Known Incompatibility Issues with Third-Party Tools`
- Source Heading Path: `Known Incompatibility Issues with Third-Party Tools > Compatibility with Sequelize > Modification of a column's `AUTO_INCREMENT` attribute is not allowed by default | Known Incompatibility Issues with Third-Party Tools > Compatibility with Sequelize > `FULLTEXT`, `HASH`, and `SPATIAL` indexes are not supported | Known Incompatibility Issues with Third-Party Tools > Need help?`
- Source Line Ranges: `217-247`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `sql`, `tidb`, `shared`
- Topic Tags: `sequelize`, `auto_increment`, `alter-table`, `indexes`, `fulltext`, `hash`, `spatial`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0190_104618bdd1`
- Source ID: `tidb-docs-8.1:develop/dev-guide-third-party-tools-compatibility.md#modification-of-a-column-s-auto-increment-attribute-is-not-allowed-by-default`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c9f158e941c90861fe218962406c7032565cc90480501914b857b6cdc9635fc6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-third-party-tools-compatibility#modification-of-a-column-s-auto-increment-attribute-is-not-allowed-by-default
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-third-party-tools-compatibility.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB compatibility notes for Sequelize migrations involving AUTO_INCREMENT column changes, unsupported index types, or official support resources.
- Retrieval Keywords: Sequelize, ALTER TABLE MODIFY, ALTER TABLE CHANGE, AUTO_INCREMENT, @@tidb_allow_remove_auto_inc, restrictions of AUTO_INCREMENT, FULLTEXT indexes are not supported, HASH indexes are not supported, SPATIAL indexes are not supported, Discord, Slack, submit a support ticket
- Follow-up Guidance: It points to the restrictions of AUTO_INCREMENT, notes that setting @@tidb_allow_remove_auto_inc to true allows removal of the AUTO_INCREMENT attribute, and lists Discord, Slack, and support ticket channels for help.
- Classification Note: This is reference content because it lists known Sequelize incompatibility issues and support resources from the official documentation.

## Official Source Content

### Modification of a column's `AUTO_INCREMENT` attribute is not allowed by default

**Description**

Adding or removing the `AUTO_INCREMENT` attribute of a column via `ALTER TABLE MODIFY` or `ALTER TABLE CHANGE` command is not allowed by default.

**Way to avoid**

Refer to the [restrictions of `AUTO_INCREMENT`](https://docs.pingcap.com/tidb/stable/auto-increment#restrictions).

To allow the removal of the `AUTO_INCREMENT` attribute, set `@@tidb_allow_remove_auto_inc` to `true`.
### `FULLTEXT`, `HASH`, and `SPATIAL` indexes are not supported

**Description**

`FULLTEXT`, `HASH`, and `SPATIAL` indexes are not supported.
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
