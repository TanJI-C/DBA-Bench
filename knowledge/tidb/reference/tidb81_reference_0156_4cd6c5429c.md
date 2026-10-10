# Prisma relation mode and TiDB foreign key notes

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-nodejs-prisma.md`
- Source Title: `Connect to TiDB with Prisma`
- Source Heading Path: `Connect to TiDB with Prisma > Useful notes > Foreign key constraints vs Prisma relation mode`
- Source Line Ranges: `355-366`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`
- Topic Tags: `prisma`, `foreign-key`, `referential-integrity`, `relation-mode`, `performance-warning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0156_4cd6c5429c`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-nodejs-prisma.md#foreign-key-constraints-vs-prisma-relation-mode`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f017c861c1a49d63fe3dea723c75b499de6fff6fc8481e548b446554849f0c74`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-nodejs-prisma#foreign-key-constraints-vs-prisma-relation-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-nodejs-prisma.md

## Retrieval Guidance

- Use When: Use this chunk when comparing foreign key constraints with Prisma relation mode for referential integrity in a TiDB application using Prisma.
- Retrieval Keywords: Foreign key constraints vs Prisma relation mode, referential integrity, Prisma relation mode, foreign key, TiDB v6.6.0, experimental feature, cross-table referencing, data consistency, performance implications, additional database queries, large data volumes, serious performance issues
- Follow-up Guidance: The source notes that foreign keys are suitable for small and medium-volumes data scenarios and that Prisma relation mode requires additional database queries to maintain referential integrity.
- Classification Note: This is reference content because it summarizes the characteristics and cautions of foreign key constraints and Prisma relation mode rather than providing a step-by-step procedure.

## Official Source Content

### Foreign key constraints vs Prisma relation mode

To check [referential integrity](https://en.wikipedia.org/wiki/Referential_integrity?useskin=vector), you can use foreign key constraints or Prisma relation mode:

- [Foreign key](https://docs.pingcap.com/tidb/stable/foreign-key) is an experimental feature supported starting from TiDB v6.6.0, which allows cross-table referencing of related data, and foreign key constraints to maintain data consistency.

    > **Warning:**
    >
    > **Foreign keys are suitable for small and medium-volumes data scenarios.** Using foreign keys in large data volumes might lead to serious performance issues and could have unpredictable effects on the system. If you plan to use foreign keys, conduct thorough validation first and use them with caution.

- [Prisma relation mode](https://www.prisma.io/docs/concepts/components/prisma-schema/relations/relation-mode) is the emulation of referential integrity in Prisma Client side. However, it should be noted that there are performance implications, as it requires additional database queries to maintain referential integrity.
