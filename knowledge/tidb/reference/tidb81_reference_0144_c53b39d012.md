# JDBC sample code for connect insert and query

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-java-jdbc.md`
- Source Title: `Connect to TiDB with JDBC`
- Source Heading Path: `Connect to TiDB with JDBC > Sample code snippets | Connect to TiDB with JDBC > Sample code snippets > Connect to TiDB | Connect to TiDB with JDBC > Sample code snippets > Insert data | Connect to TiDB with JDBC > Sample code snippets > Query data`
- Source Line Ranges: `199-265`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`
- Topic Tags: `sample-code`, `jdbc`, `datasource`, `connection`, `ssl-mode`, `insert`, `query`, `prepared-statement`, `crud`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0144_c53b39d012`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-java-jdbc.md#sample-code-snippets`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `846207f4838763412d0c7a2cf270f24ac5c08f87b0e51abd4d782a742d7bfea8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-jdbc#sample-code-snippets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-java-jdbc.md

## Retrieval Guidance

- Use When: Use this chunk when the user is looking for JDBC Java sample code to create a MysqlDataSource, enable SSL with VERIFY_IDENTITY and TLSv1.2/TLSv1.3, insert into the player table, or query a player by id with PreparedStatement.
- Retrieval Keywords: Sample code snippets, MysqlDataSource, getMysqlDataSource, setServerName, setPortNumber, setUser, setPassword, setDatabaseName, PropertyDefinitions.SslMode.VERIFY_IDENTITY, setEnabledTLSProtocols, TLSv1.2,TLSv1.3, INSERT INTO player (id, coins, goods) VALUES (?, ?, ?), SELECT * FROM player WHERE id = ?, PreparedStatement, ResultSet, PlayerBean, createPlayer, getPlayer
- Follow-up Guidance: The source links to the complete repository tidb-samples/tidb-java-jdbc-quickstart and to the Insert data and Query data documentation pages.
- Classification Note: This is reference content because it supplies code snippets and exact JDBC and SQL identifiers for common connect, insert, and query patterns.

## Official Source Content

## Sample code snippets

You can refer to the following sample code snippets to complete your own application development.

For complete sample code and how to run it, check out the [tidb-samples/tidb-java-jdbc-quickstart](https://github.com/tidb-samples/tidb-java-jdbc-quickstart) repository.
### Connect to TiDB

```java
public MysqlDataSource getMysqlDataSource() throws SQLException {
    MysqlDataSource mysqlDataSource = new MysqlDataSource();

    mysqlDataSource.setServerName(${tidb_host});
    mysqlDataSource.setPortNumber(${tidb_port});
    mysqlDataSource.setUser(${tidb_user});
    mysqlDataSource.setPassword(${tidb_password});
    mysqlDataSource.setDatabaseName(${tidb_db_name});
    if (${tidb_use_ssl}) {
        mysqlDataSource.setSslMode(PropertyDefinitions.SslMode.VERIFY_IDENTITY.name());
        mysqlDataSource.setEnabledTLSProtocols("TLSv1.2,TLSv1.3");
    }

    return mysqlDataSource;
}
```

When using this function, you need to replace `${tidb_host}`, `${tidb_port}`, `${tidb_user}`, `${tidb_password}`, and `${tidb_db_name}` with the actual values of your TiDB cluster.
### Insert data

```java
public void createPlayer(PlayerBean player) throws SQLException {
    MysqlDataSource mysqlDataSource = getMysqlDataSource();
    try (Connection connection = mysqlDataSource.getConnection()) {
        PreparedStatement preparedStatement = connection.prepareStatement("INSERT INTO player (id, coins, goods) VALUES (?, ?, ?)");
        preparedStatement.setString(1, player.getId());
        preparedStatement.setInt(2, player.getCoins());
        preparedStatement.setInt(3, player.getGoods());

        preparedStatement.execute();
    }
}
```

For more information, refer to [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data).
### Query data

```java
public void getPlayer(String id) throws SQLException {
    MysqlDataSource mysqlDataSource = getMysqlDataSourceByEnv();
    try (Connection connection = mysqlDataSource.getConnection()) {
        PreparedStatement preparedStatement = connection.prepareStatement("SELECT * FROM player WHERE id = ?");
        preparedStatement.setString(1, id);
        preparedStatement.execute();

        ResultSet res = preparedStatement.executeQuery();
        if(res.next()) {
            PlayerBean player = new PlayerBean(res.getString("id"), res.getInt("coins"), res.getInt("goods"));
            System.out.println(player);
        }
    }
}
```

For more information, refer to [Query data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table).
