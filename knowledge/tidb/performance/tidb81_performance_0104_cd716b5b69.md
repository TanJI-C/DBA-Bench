# MyBatis data access and executor practices

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/java-app-best-practices.md`
- Source Title: `Best Practices for Developing Java Applications with TiDB`
- Source Heading Path: `Best Practices for Developing Java Applications with TiDB > Data access framework | Best Practices for Developing Java Applications with TiDB > Data access framework > MyBatis | Best Practices for Developing Java Applications with TiDB > Data access framework > MyBatis > Mapper parameters | Best Practices for Developing Java Applications with TiDB > Data access framework > MyBatis > Dynamic SQL Batch | Best Practices for Developing Java Applications with TiDB > Data access framework > MyBatis > Streaming result | Best Practices for Developing Java Applications with TiDB > Data access framework > `ExecutorType``
- Source Line Ranges: `288-362`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`
- Topic Tags: `java`, `mybatis`, `prepared-statements`, `batch`, `streaming-result`, `fetchsize`, `cursor`, `executortype`, `jdbc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0104_cd716b5b69`
- Source ID: `tidb-docs-8.1:develop/java-app-best-practices.md#data-access-framework`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f43aefe9f7530619b9f1c98e85d4fb7fe6b6eca9c07e6d3abab19f68722e84ee`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/java-app-best-practices#data-access-framework
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/java-app-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when you need MyBatis-specific TiDB best practices for mapper parameters, dynamic SQL batch inserts, streaming result reading, or `ExecutorType` behavior in Java applications.
- Retrieval Keywords: MyBatis, Mapper parameters, #{param1}, ${param2}, Prepared Statement, prepare, injection security risks, Dynamic SQL - foreach, rewriteBatchedStatements=true, rewriteBatchStatements=true, insert on duplicate key update, prepStmtCacheSqlLimit, Streaming result, fetchSize, setFetchSize, ResultHandler, Cursor, fetchSize="-2147483648", Integer.MIN_VALUE, @Options(fetchSize = Integer.MIN_VALUE), ExecutorType, Simple, Reuse, Batch, openSession, cachePrepStmts
- Follow-up Guidance: The chunk also notes that batch execution with `ExecutorType` `Batch` can make `UPDATE` or `INSERT` appear fast during a transaction but slower when reading data or committing, which is normal when troubleshooting slow SQL queries.
- Classification Note: This is classified as performance content because the official text focuses on Prepared Statement reuse, reduced communication overhead, streaming large result sets, and executor behaviors that affect execution efficiency.

## Official Source Content

## Data access framework

Applications often use some kind of data access framework to simplify database access.
### MyBatis

[MyBatis](http://www.mybatis.org/mybatis-3/) is a popular Java data access framework. It is mainly used to manage SQL queries and complete the mapping between result sets and Java objects. MyBatis is highly compatible with TiDB. MyBatis rarely has problems based on its historical issues.

Here this document mainly focuses on the following configurations.
#### Mapper parameters

MyBatis Mapper supports two parameters:

- `select 1 from t where id = #{param1}` will be converted to `select 1 from t where id =?` as a Prepared Statement and be "prepared", and the actual parameter will be used for reuse. You can get the best performance when using this parameter with the previously mentioned Prepare connection parameters.
- `select 1 from t where id = ${param2}` will be replaced with `select 1 from t where id = 1` as a text file and be executed. If this statement is replaced with different parameters and is executed, MyBatis will send different requests for "preparing" the statements to TiDB. This might cause TiDB to cache a large number of Prepared Statements, and executing SQL operations this way has injection security risks.
#### Dynamic SQL Batch

[Dynamic SQL - foreach](http://www.mybatis.org/mybatis-3/dynamic-sql.html#foreach)

To support the automatic rewriting of multiple `INSERT` statements into the form of `insert ... values(...), (...), ...`, in addition to configuring `rewriteBatchedStatements=true` in JDBC as mentioned before, MyBatis can also use dynamic SQL to semi-automatically generate batch inserts. Take the following mapper as an example:

```xml
<insert id="insertTestBatch" parameterType="java.util.List" fetchSize="1">
  insert into test
   (id, v1, v2)
  values
  <foreach item="item" index="index" collection="list" separator=",">
  (
   #{item.id}, #{item.v1}, #{item.v2}
  )
  </foreach>
  on duplicate key update v2 = v1 + values(v1)
</insert>
```

This mapper generates an `insert on duplicate key update` statement. The number of `(?,?,?)` following "values" is determined by the number of passed lists. Its final effect is similar to using `rewriteBatchStatements=true`, which also effectively reduces communication overhead between the client and TiDB.

As mentioned before, you also need to note that the Prepared Statements will not be cached after their maximum length exceeds the value of `prepStmtCacheSqlLimit`.
#### Streaming result

[A previous section](#use-streamingresult-to-get-the-execution-result) introduces how to stream read execution results in JDBC. In addition to the corresponding configurations of JDBC, if you want to read a super large result set in MyBatis, you also need to note that:

- You can set `fetchSize` for a single SQL statement in the mapper configuration (see the previous code block). Its effect is equivalent to calling `setFetchSize` in JDBC.
- You can use the query interface with `ResultHandler` to avoid getting the entire result set at once.
- You can use the `Cursor` class for stream reading.

If you configure mappings using XML, you can stream read results by configuring `fetchSize="-2147483648"`(`Integer.MIN_VALUE`) in the mapping's `<select>` section.

```xml
<select id="getAll" resultMap="postResultMap" fetchSize="-2147483648">
  select * from post;
</select>
```

If you configure mappings using code, you can add the `@Options(fetchSize = Integer.MIN_VALUE)` annotation and keep the type of results as `Cursor` so that the SQL results can be read in streaming.

```java
@Select("select * from post")
@Options(fetchSize = Integer.MIN_VALUE)
Cursor<Post> queryAllPost();
```
### `ExecutorType`

You can choose `ExecutorType` during `openSession`. MyBatis supports three types of executors:

- Simple: The Prepared Statements are called to JDBC for each execution (if the JDBC configuration item `cachePrepStmts` is enabled, repeated Prepared Statements will be reused)
- Reuse: The Prepared Statements are cached in `executor`, so that you can reduce duplicate calls for Prepared Statements without using the JDBC `cachePrepStmts`
- Batch: Each update operation (`INSERT`/`DELETE`/`UPDATE`) will first be added to the batch, and will be executed until the transaction commits or a `SELECT` query is performed. If `rewriteBatchStatements` is enabled in the JDBC layer, it will try to rewrite the statements. If not, the statements will be sent one by one.

Usually, the default value of `ExecutorType` is `Simple`. You need to change `ExecutorType` when calling `openSession`. If it is the batch execution, you might find that in a transaction the `UPDATE` or `INSERT` statements are executed pretty fast, but it is slower when reading data or committing the transaction. This is actually normal, so you need to note this when troubleshooting slow SQL queries.
