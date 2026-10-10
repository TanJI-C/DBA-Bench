# Spring Boot TiDB code snippets and next steps

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-java-spring-boot.md`
- Source Title: `Connect to TiDB with Spring Boot`
- Source Heading Path: `Connect to TiDB with Spring Boot > Sample code snippets | Connect to TiDB with Spring Boot > Sample code snippets > Connect to TiDB | Connect to TiDB with Spring Boot > Sample code snippets > Data management: `@Repository` | Connect to TiDB with Spring Boot > Sample code snippets > Insert or update data | Connect to TiDB with Spring Boot > Sample code snippets > Query data | Connect to TiDB with Spring Boot > Sample code snippets > Delete data | Connect to TiDB with Spring Boot > Next steps`
- Source Line Ranges: `187-270`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `shared`
- Topic Tags: `spring-boot`, `java`, `application-yml`, `jdbc`, `environment-variables`, `repository`, `jparepository`, `crud`, `insert`, `update`, `query`, `delete`, `next-steps`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0148_a1a5367033`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-java-spring-boot.md#sample-code-snippets`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1651de696c7743bb9c89dcf93eac1b6084ea7f2d64f117df3e9ac600c3dd99a9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-spring-boot#sample-code-snippets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-java-spring-boot.md

## Retrieval Guidance

- Use When: Use this chunk when you need Spring Boot and Spring Data JPA sample code for connecting to TiDB, configuring application.yml, or performing CRUD operations with JpaRepository.
- Retrieval Keywords: Sample code snippets, application.yml, spring.datasource.url, TIDB_JDBC_URL, jdbc:mysql://localhost:4000/test, TIDB_USER, TIDB_PASSWORD, com.mysql.cj.jdbc.Driver, org.hibernate.dialect.TiDBDialect, ddl-auto: create-drop, @Repository, JpaRepository, PlayerRepository, @Autowired, playerRepository.save(player), playerRepository.findById(id).orElse(null), playerRepository.deleteById(id), Connect to TiDB, Insert or update data, Query data, Delete data, Next steps
- Follow-up Guidance: The source points to next-step references including the Spring Framework, Spring Boot, Spring Data JPA, Hibernate documentation, and TiDB Developer guide chapters such as Insert data, Update data, Delete data, Single table reading, Transactions, and SQL performance optimization.
- Classification Note: This chunk is classified as reference because it supplies example configuration and code snippets plus linked documentation for further development details.

## Official Source Content

## Sample code snippets

You can refer to the following sample code snippets to complete your own application development.

For complete sample code and how to run it, check out the [tidb-samples/tidb-java-springboot-jpa-quickstart](https://github.com/tidb-samples/tidb-java-springboot-jpa-quickstart) repository.
### Connect to TiDB

Edit the configuration file `application.yml`:

```yaml
spring:
  datasource:
    url: ${TIDB_JDBC_URL:jdbc:mysql://localhost:4000/test}
    username: ${TIDB_USER:root}
    password: ${TIDB_PASSWORD:}
    driver-class-name: com.mysql.cj.jdbc.Driver
  jpa:
    show-sql: true
    database-platform: org.hibernate.dialect.TiDBDialect
    hibernate:
      ddl-auto: create-drop
```

After configuration, set the environment variables `TIDB_JDBC_URL`, `TIDB_USER`, and `TIDB_PASSWORD` to the actual values of your TiDB cluster. The configuration file provides default settings for these environment variables. If you do not configure the environment variables, the default values are as follows:

- `TIDB_JDBC_URL`: `"jdbc:mysql://localhost:4000/test"`
- `TIDB_USER`: `"root"`
- `TIDB_PASSWORD`: `""`
### Data management: `@Repository`

Spring Data JPA manages data through the `@Repository` interface. To use the CRUD operations provided by `JpaRepository`, you need to extend the `JpaRepository` interface:

```java
@Repository
public interface PlayerRepository extends JpaRepository<PlayerBean, Long> {
}
```

Then, you can use `@Autowired` for automatic dependency injection in any class that requires the `PlayerRepository`. This enables you to directly use CRUD functions. The following is an example:

```java
@Autowired
private PlayerRepository playerRepository;
```
### Insert or update data

```java
playerRepository.save(player);
```

For more information, refer to [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data) and [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data).
### Query data

```java
PlayerBean player = playerRepository.findById(id).orElse(null);
```

For more information, refer to [Query data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table).
### Delete data

```java
playerRepository.deleteById(id);
```

For more information, refer to [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data).
## Next steps

- Learn more usage about the third-party libraries and frameworks used in this document, refer to their official documentation:

    - [The documentation of Spring Framework](https://spring.io/projects/spring-framework)
    - [The documentation of Spring Boot](https://spring.io/projects/spring-boot)
    - [The documentation of Spring Data JPA](https://spring.io/projects/spring-data-jpa)
    - [The documentation of Hibernate](https://hibernate.org/orm/documentation)

- Learn the best practices for TiDB application development with the chapters in the [Developer guide](https://docs.pingcap.com/tidb/stable/develop/dev-guide-overview), such as [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data), [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data), [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data), [Single table reading](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table), [Transactions](https://docs.pingcap.com/tidb/stable/develop/dev-guide-transaction-overview), and [SQL performance optimization](https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql-overview).
- Learn through the professional [TiDB developer courses](https://www.pingcap.com/education/) and earn [TiDB certifications](https://www.pingcap.com/education/certification/) after passing the exam.
- Learn through the course for Java developers: [Working with TiDB from Java](https://eng.edu.pingcap.com/catalog/info/id:212).
