# JDBC update and delete snippets, ORM note, and follow-up resources

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-java-jdbc.md`
- Source Title: `Connect to TiDB with JDBC`
- Source Heading Path: `Connect to TiDB with JDBC > Sample code snippets > Update data | Connect to TiDB with JDBC > Sample code snippets > Delete data | Connect to TiDB with JDBC > Useful notes | Connect to TiDB with JDBC > Useful notes > Using driver or ORM framework? | Connect to TiDB with JDBC > Next steps | Connect to TiDB with JDBC > Need help?`
- Source Line Ranges: `266-332`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`
- Topic Tags: `jdbc`, `java`, `sample-code`, `update`, `delete`, `orm`, `connector-j`, `developer-guide`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0145_c706f734d7`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-java-jdbc.md#update-data`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `46f6875d062db74e9013564a55e4ce807f20088f30af2986f77860eb276739f0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-jdbc#update-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-java-jdbc.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Java JDBC sample code for UPDATE or DELETE operations on the player table, or for guidance on choosing JDBC versus an ORM framework and related learning resources.
- Retrieval Keywords: updatePlayer, deletePlayer, PreparedStatement, UPDATE player SET goods = goods + ?, coins = coins + ? WHERE id=?, DELETE FROM player WHERE id=?, MysqlDataSource, getMysqlDataSourceByEnv, Connection connection = mysqlDataSource.getConnection(), MySQL Connector/J, Using driver or ORM framework?, Hibernate, MyBatis, Spring Data JPA, Developer guide, Update data, Delete data, Single table reading, Transactions, SQL performance optimization, Working with TiDB from Java, Discord, Slack, support ticket
- Follow-up Guidance: The source points to Update data, Delete data, MySQL Connector/J documentation, the TiDB Developer guide, Java developer course materials, and community or support channels.
- Classification Note: This is reference content because it provides Java JDBC code snippets, exact SQL statements, ORM notes, and links to related documentation and support resources from the official developer guide.

## Official Source Content

### Update data

```java
public void updatePlayer(String id, int amount, int price) throws SQLException {
    MysqlDataSource mysqlDataSource = getMysqlDataSourceByEnv();
    try (Connection connection = mysqlDataSource.getConnection()) {
        PreparedStatement transfer = connection.prepareStatement("UPDATE player SET goods = goods + ?, coins = coins + ? WHERE id=?");
        transfer.setInt(1, -amount);
        transfer.setInt(2, price);
        transfer.setString(3, id);
        transfer.execute();
    }
}
```

For more information, refer to [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data).
### Delete data

```java
public void deletePlayer(String id) throws SQLException {
    MysqlDataSource mysqlDataSource = getMysqlDataSourceByEnv();
    try (Connection connection = mysqlDataSource.getConnection()) {
        PreparedStatement deleteStatement = connection.prepareStatement("DELETE FROM player WHERE id=?");
        deleteStatement.setString(1, id);
        deleteStatement.execute();
    }
}
```

For more information, refer to [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data).
## Useful notes
### Using driver or ORM framework?

The Java driver provides low-level access to the database, but it requires the developers to:

- Manually establish and release database connections.
- Manually manage database transactions.
- Manually map data rows to data objects.

Unless you need to write complex SQL statements, it is recommended to use [ORM](https://en.wikipedia.org/w/index.php?title=Object-relational_mapping) framework for development, such as [Hibernate](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-hibernate), [MyBatis](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-mybatis), or [Spring Data JPA](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-spring-boot). It can help you:

- Reduce [boilerplate code](https://en.wikipedia.org/wiki/Boilerplate_code) for managing connections and transactions.
- Manipulate data with data objects instead of a number of SQL statements.
## Next steps

- Learn more usage of MySQL Connector/J from [the documentation of MySQL Connector/J](https://dev.mysql.com/doc/connector-j/en/).
- Learn the best practices for TiDB application development with the chapters in the [Developer guide](https://docs.pingcap.com/tidb/stable/develop/dev-guide-overview), such as [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data), [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data), [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data), [Single table reading](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table), [Transactions](https://docs.pingcap.com/tidb/stable/develop/dev-guide-transaction-overview), and [SQL performance optimization](https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql-overview).
- Learn through the professional [TiDB developer courses](https://www.pingcap.com/education/) and earn [TiDB certifications](https://www.pingcap.com/education/certification/) after passing the exam.
- Learn through the course for Java developers: [Working with TiDB from Java](https://eng.edu.pingcap.com/catalog/info/id:212).
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
