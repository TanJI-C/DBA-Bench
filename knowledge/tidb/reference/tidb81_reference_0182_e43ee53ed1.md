# Access control, schema change guidance, and limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-schema-design-overview.md`
- Source Title: `TiDB Database Schema Design Overview`
- Source Heading Path: `TiDB Database Schema Design Overview > Access Control | TiDB Database Schema Design Overview > Database schema changes | TiDB Database Schema Design Overview > Object limitations | TiDB Database Schema Design Overview > Need help?`
- Source Line Ranges: `70-104`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `access-control`, `users`, `roles`, `privileges`, `schema-changes`, `best-practices`, `limitations`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0182_e43ee53ed1`
- Source ID: `tidb-docs-8.1:develop/dev-guide-schema-design-overview.md#access-control`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9a6db2a3b10b378faba1a603dcc07eba749c10e306c0349d3341890a189dd583`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-schema-design-overview#access-control
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-schema-design-overview.md

## Retrieval Guidance

- Use When: Use this chunk when someone asks about TiDB access control options, guidance for executing database schema changes, object limitations, or where to get help.
- Retrieval Keywords: Access Control, user-based access control, role-based access control, privileges, users, roles, privilege management, user account management, role-based access control, Database schema changes, MySQL client, GUI client, driver or ORM, Object limitations, TiDB Limitations, Need help, Discord, Slack, support ticket
- Follow-up Guidance: It links to privilege management, user account management, role-based access control, TiDB Limitations, and support channels including Discord, Slack, and support ticket submission.
- Classification Note: This is reference content because it summarizes supported access control models, a best-practice note for schema changes, and pointers to limitations and support resources.

## Official Source Content

## Access Control

TiDB supports both user-based and role-based access control. To allow users to view, modify, or delete data objects and data schemas, you can either grant [privileges](https://docs.pingcap.com/tidb/stable/privilege-management) to [users](https://docs.pingcap.com/tidb/stable/user-account-management) directly or grant [privileges](https://docs.pingcap.com/tidb/stable/privilege-management) to users through [roles](https://docs.pingcap.com/tidb/stable/role-based-access-control).

TiDB supports both user-based and role-based access control. To allow users to view, modify, or delete data objects and data schemas, you can either grant [privileges](https://docs.pingcap.com/tidb/stable/privilege-management) to [users](https://docs.pingcap.com/tidb/stable/user-account-management) directly or grant [privileges](https://docs.pingcap.com/tidb/stable/privilege-management) to users through [roles](https://docs.pingcap.com/tidb/stable/role-based-access-control).
## Database schema changes

As a best practice, it is recommended that you use a [MySQL client](https://dev.mysql.com/doc/refman/8.0/en/mysql.html) or a GUI client instead of a driver or ORM to execute database schema changes.
## Object limitations

For more information, see [TiDB Limitations](https://docs.pingcap.com/tidb/stable/tidb-limitations).
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
