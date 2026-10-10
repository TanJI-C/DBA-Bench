# MyBatis configuration and CRUD code snippets

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-java-mybatis.md`
- Source Title: `Connect to TiDB with MyBatis`
- Source Heading Path: `Connect to TiDB with MyBatis > Sample code snippets | Connect to TiDB with MyBatis > Sample code snippets > Connect to TiDB | Connect to TiDB with MyBatis > Sample code snippets > Insert data | Connect to TiDB with MyBatis > Sample code snippets > Query data`
- Source Line Ranges: `181-274`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `sql`, `tidb`
- Topic Tags: `java`, `mybatis`, `configuration-file`, `jdbc`, `session-factory`, `mapper-xml`, `insert`, `query`, `crud`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0146_5dba2fcb0d`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-java-mybatis.md#sample-code-snippets`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6a83fb3f51ff5067968a43501a0ced647fd764141c5aa134fb6cb9341a8d0e9f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-mybatis#sample-code-snippets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-java-mybatis.md

## Retrieval Guidance

- Use When: Use this chunk when you need MyBatis configuration examples and mapper XML snippets for connecting to TiDB and implementing basic insert and query operations in a Java application.
- Retrieval Keywords: Sample code snippets, mybatis-config.xml, SqlSessionFactory, SqlSessionFactoryBuilder, Resources.getResourceAsStream, com.mysql.cj.jdbc.Driver, tidb_jdbc_url, tidb_user, tidb_password, mapper_location, <mapper/>, mapper.namespace, com.pingcap.model.PlayerMapper, insert into player (id, coins, goods), selectByPrimaryKey, resultMap, BaseResultMap, select id, coins, goods from player
- Follow-up Guidance: The chunk points to the `tidb-samples/tidb-java-mybatis-quickstart` repository for complete sample code and links to separate documentation for Insert data and Query data.
- Classification Note: This is classified as reference because the content provides configuration and code examples for MyBatis XML and Java functions rather than a full procedural workflow.

## Official Source Content

## Sample code snippets

You can refer to the following sample code snippets to complete your own application development.

For complete sample code and how to run it, check out the [tidb-samples/tidb-java-mybatis-quickstart](https://github.com/tidb-samples/tidb-java-mybatis-quickstart) repository.
### Connect to TiDB

Edit the MyBatis configuration file `mybatis-config.xml`:

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE configuration
        PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-config.dtd">
<configuration>
    <settings>
        <setting name="cacheEnabled" value="true"/>
        <setting name="lazyLoadingEnabled" value="false"/>
        <setting name="aggressiveLazyLoading" value="true"/>
        <setting name="logImpl" value="LOG4J"/>
    </settings>

    <environments default="development">
        <environment id="development">
            <!-- JDBC transaction manager -->
            <transactionManager type="JDBC"/>
            <!-- Database pool -->
            <dataSource type="POOLED">
                <property name="driver" value="com.mysql.cj.jdbc.Driver"/>
                <property name="url" value="${tidb_jdbc_url}"/>
                <property name="username" value="${tidb_user}"/>
                <property name="password" value="${tidb_password}"/>
            </dataSource>
        </environment>
    </environments>
    <mappers>
        <mapper resource="${mapper_location}.xml"/>
    </mappers>
</configuration>
```

Be sure to replace `${tidb_jdbc_url}`, `${tidb_user}`, and `${tidb_password}` with the actual values of your TiDB cluster. Also, replace `${mapper_location}` with the path of your mapper XML configuration file. For multiple mapper XML configuration files, you need to add a `<mapper/>` tag for each. Then, define the following function:

```java
public SqlSessionFactory getSessionFactory() {
    InputStream inputStream = Resources.getResourceAsStream("mybatis-config.xml");
    SqlSessionFactory sessionFactory = new SqlSessionFactoryBuilder().build(inputStream);
}
```
### Insert data

Add a node in the mapper XML and add a function with the same name in the interface class configured in the `mapper.namespace` attribute of the XML configuration file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.pingcap.model.PlayerMapper">
    <insert id="insert" parameterType="com.pingcap.model.Player">
    insert into player (id, coins, goods)
    values (#{id,jdbcType=VARCHAR}, #{coins,jdbcType=INTEGER}, #{goods,jdbcType=INTEGER})
    </insert>
</mapper>
```

For more information, refer to [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data).
### Query data

Add a node in the mapper XML and add a function with the same name in the interface class configured in the `mapper.namespace` attribute of the XML configuration file. Specifically, if you use `resultMap` as the return type for MyBatis query functions, make sure that the `<resultMap/>` node is configured correctly.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.pingcap.model.PlayerMapper">
    <resultMap id="BaseResultMap" type="com.pingcap.model.Player">
        <constructor>
            <idArg column="id" javaType="java.lang.String" jdbcType="VARCHAR" />
            <arg column="coins" javaType="java.lang.Integer" jdbcType="INTEGER" />
            <arg column="goods" javaType="java.lang.Integer" jdbcType="INTEGER" />
        </constructor>
    </resultMap>

    <select id="selectByPrimaryKey" parameterType="java.lang.String" resultMap="BaseResultMap">
    select id, coins, goods
    from player
    where id = #{id,jdbcType=VARCHAR}
    </select>
</mapper>
```

For more information, refer to [Query data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table).
