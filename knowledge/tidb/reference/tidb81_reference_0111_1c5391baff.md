# Object naming conventions for databases, tables, columns, and indexes

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-object-naming-guidelines.md`
- Source Title: `Object Naming Convention`
- Source Heading Path: `Object Naming Convention | Object Naming Convention > General rules | Object Naming Convention > Database naming convention | Object Naming Convention > Table naming convention | Object Naming Convention > Column naming convention | Object Naming Convention > Index naming convention | Object Naming Convention > Need help?`
- Source Line Ranges: `5-60`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `shared`, `tidb`
- Topic Tags: `naming`, `database-names`, `table-names`, `column-names`, `index-names`, `reserved-words`, `conventions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0111_1c5391baff`
- Source ID: `tidb-docs-8.1:develop/dev-guide-object-naming-guidelines.md#object-naming-convention`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `df7c584f970032dfb208beaa7688db40a433be70624f6ee5460bb329b3d929b8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-object-naming-guidelines#object-naming-convention
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-object-naming-guidelines.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiDB object naming guidelines for databases, tables, columns, or indexes, including reserved-word avoidance and recommended naming patterns.
- Retrieval Keywords: Object Naming Convention, General rules, Database naming convention, Table naming convention, Column naming convention, Index naming convention, meaningful English words separated by underscores, use only letters, numbers, and underscores, TiDB reserved words, group, order, from, desc, lowercase letters, tmp_crm, test_crm, tmp_t_crm_relation_0425, bak_t_crm_relation_20170425, tmp_st_{business code}_{creator abbreviation}_{date}, t_crm_ec_record_YYYY{MM}{dd}, is_{description}, is_enabled, pk_{table_name_abbreviation}_{field_name_abbreviation}, uk_{table_name_abbreviation}_{field_name_abbreviation}, idx_{table_name_abbreviation}_{field_name_abbreviation}, TiDB keywords
- Follow-up Guidance: The source also points to TiDB keywords for checking whether a keyword is reserved and lists Discord, Slack, and support ticket channels under Need help?.
- Classification Note: This is a reference chunk because it provides naming rules, examples, and identifier patterns for SQL objects rather than procedural steps.

## Official Source Content

# Object Naming Convention

This document introduces the rules to name database objects, such as database, table, index, and user.
## General rules

- It is recommended to use meaningful English words separated by underscores.
- Use only letters, numbers, and underscores in a name.
- Avoid using TiDB reserved words, such as `group` and `order`, as column names.
- It is recommended to use lowercase letters for all database objects.
## Database naming convention

It is recommended to differentiate database names by business, product, or other metrics and use no more than 20 characters in a database name. For example, you can name a temporary library as `tmp_crm` or a test library as `test_crm`.
## Table naming convention

- Use the same prefix for tables of the same business or module, and make sure that the table name is self-explanatory as much as possible.
- Separate words in a name by underscores. It is recommended to use no more than 32 characters in a table name.
- It is recommended to annotate the purpose of the table for a better understanding. For example:
    - Temporary table: `tmp_t_crm_relation_0425`
    - Backup table: `bak_t_crm_relation_20170425`
    - Temporary table of business operations: `tmp_st_{business code}_{creator abbreviation}_{date}`
    - Record table of accounts period: `t_crm_ec_record_YYYY{MM}{dd}`
- Create separate databases for tables of different business modules and add annotations accordingly.
## Column naming convention

- The column naming is the actual meaning or abbreviation of the column.
- It is recommended to use the same column name between tables with the same meaning.
- It is recommended to add annotations to columns and specify named values for enumerated types, such as "0: offline, 1: online".
- It is recommended to name the boolean column as `is_{description}`. For example, the column of a `member` table that indicates whether the member is enabled, can be named as `is_enabled`.
- It is not recommended to name a column with more than 30 characters, and the number of columns should be less than 60.
- Avoid using TiDB reserved words as column names, such as `order`, `from`, and `desc`. To check whether a keyword is reserved, see [TiDB keywords](https://docs.pingcap.com/tidb/stable/keywords).
## Index naming convention

- Primary key index: `pk_{table_name_abbreviation}_{field_name_abbreviation}`
- Unique index: `uk_{table_name_abbreviation}_{field_name_abbreviation}`
- Common index: `idx_{table_name_abbreviation}_{field_name_abbreviation}`
- Column name with multiple words: use meaningful abbreviations
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
