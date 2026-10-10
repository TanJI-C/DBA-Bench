# Foreign key constraints, views, and sequences

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/database-schema-concepts.md`
- Source Title: `Database Schema`
- Source Heading Path: `Database Schema > Constraints > FOREIGN KEY constraints | Database Schema > Views | Database Schema > Sequence`
- Source Line Ranges: `154-176`
- Source Scope: `cloud`
- Primary Component: `sql`
- Related Components: `cloud`, `tidb`
- Topic Tags: `foreign-key`, `referential-integrity`, `experimental-feature`, `views`, `virtual-table`, `sequence`, `schema-objects`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0800_056b56286e`
- Source ID: `tidb-docs-8.1:tidb-cloud/database-schema-concepts.md#foreign-key-constraints`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fa6375aa172a03edee2dddc1648e3cdf047b72571880aa3480ec25f40161a34e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/database-schema-concepts#foreign-key-constraints
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/database-schema-concepts.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB Cloud schema concepts involving FOREIGN KEY constraints, views as virtual tables, or sequences for generating numbers.
- Retrieval Keywords: FOREIGN KEY constraints, referential integrity, child table, parent table, primary or unique key column, experimental feature, v6.6.0, Views, virtual table, SELECT statement that creates the view, safe fields, complex queries, Sequence, database object, generate a sequence of numbers, unique identifiers, primary keys
- Follow-up Guidance: The source points to the detailed pages FOREIGN KEY constraints, Views, and sql-statement-create-sequence for more information.
- Classification Note: This is reference content because it defines schema objects and constraint concepts in TiDB Cloud, including FOREIGN KEY constraints, views, and sequences.

## Official Source Content

### FOREIGN KEY constraints

A FOREIGN KEY is a database constraint that enforces referential integrity between two tables by linking a column in one table (the child table) to a column in another table (the parent table). This ensures that the values in the foreign key column of the child table match values in the primary or unique key column of the parent table. For example, a record in an `orders` table might have a foreign key linking to a customer in a `customers` table, which ensures that each order is associated with a valid customer.

Starting from v6.6.0, TiDB supports foreign key constraints as an experimental feature. This feature allows cross-table referencing of related data and helps maintain data consistency by enforcing referential integrity. However, it is important to note that this feature is experimental and not recommended for production environments due to potential performance issues, especially with large data volumes.

For more information, see [FOREIGN KEY constraints](https://docs.pingcap.com/tidb/stable/foreign-key).
## Views

A view acts as a virtual table, whose schema is defined by the `SELECT` statement that creates the view. Using views has the following benefits:

- Exposing only safe fields and data to users to ensure the security of sensitive fields and data stored in the underlying table.

- Defining complex queries that frequently appear as views to make complex queries easier and more convenient.

For more information, see [Views](https://docs.pingcap.com/tidb/stable/views).
## Sequence

A sequence is a database object designed to generate a sequence of numbers according to a specified set of rules. This feature is especially useful in scenarios where unique identifiers are required, such as in the creation of primary keys for database tables.

For more information, see [sequence](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-sequence).
