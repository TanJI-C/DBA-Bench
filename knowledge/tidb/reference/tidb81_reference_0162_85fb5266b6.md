# TypeORM foreign key constraint note

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-nodejs-typeorm.md`
- Source Title: `Connect to TiDB with TypeORM`
- Source Heading Path: `Connect to TiDB with TypeORM > Useful notes | Connect to TiDB with TypeORM > Useful notes > Foreign key constraints`
- Source Line Ranges: `343-365`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`
- Topic Tags: `typeorm`, `foreign-keys`, `referential-integrity`, `entity-relations`, `performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0162_85fb5266b6`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-nodejs-typeorm.md#useful-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7ce0139044b23ae4e923680bbb962b8e4d1d5948351662255c17547fe93d553e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-nodejs-typeorm#useful-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-nodejs-typeorm.md

## Retrieval Guidance

- Use When: Use this chunk when searching for the TypeORM option that controls foreign key constraint creation and the note about referential integrity and performance impact.
- Retrieval Keywords: createForeignKeyConstraints, foreign key constraints, referential integrity, TypeORM relations FAQ, ManyToOne createForeignKeyConstraints false, ActionLog, Person, experimental, performance issues, large data volumes
- Follow-up Guidance: The source links to the TypeORM FAQ entry about avoiding foreign key constraint creation and to the foreign key constraints documentation.
- Classification Note: This is reference content because it explains the documented behavior and default value of the TypeORM createForeignKeyConstraints option and its foreign key constraint note.

## Official Source Content

## Useful notes
### Foreign key constraints

Using [foreign key constraints](https://docs.pingcap.com/tidb/stable/foreign-key) (experimental) ensures the [referential integrity](https://en.wikipedia.org/wiki/Referential_integrity) of data by adding checks on the database side. However, this might lead to serious performance issues in scenarios with large data volumes.

You can control whether foreign key constraints are created when constructing relationships between entities by using the `createForeignKeyConstraints` option (default value is `true`).

```typescript
@Entity()
export class ActionLog {
    @PrimaryColumn()
    id: number

    @ManyToOne((type) => Person, {
        createForeignKeyConstraints: false,
    })
    person: Person
}
```

For more information, refer to the [TypeORM FAQ](https://typeorm.io/relations-faq#avoid-foreign-key-constraint-creation) and [Foreign key constraints](https://docs.pingcap.com/tidbcloud/foreign-key#foreign-key-constraints).
