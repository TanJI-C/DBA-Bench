# Java ORM frameworks and client load balancing

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-choose-driver-or-orm.md`
- Source Title: `Choose Driver or ORM`
- Source Heading Path: `Choose Driver or ORM > Java > Java ORM frameworks | Choose Driver or ORM > Java > Java client load balancing`
- Source Line Ranges: `88-207`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`
- Topic Tags: `java`, `orm`, `hibernate`, `mybatis`, `savepoint`, `nested-transactions`, `dialect-configuration`, `load-balancing`, `jdbc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0085_42ca23dd46`
- Source ID: `tidb-docs-8.1:develop/dev-guide-choose-driver-or-orm.md#java-orm-frameworks`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `97b363aa5b084c083cffad62e0f5157f5ae34c6593e8913c39a56c09b451be0a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-choose-driver-or-orm#java-orm-frameworks
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-choose-driver-or-orm.md

## Retrieval Guidance

- Use When: Use this chunk when configuring Java ORM frameworks or application-side JDBC load balancing for TiDB, especially Hibernate dialect settings, savepoint-related nested transaction notes, MyBatis dependencies, and tidb-loadbalance requirements.
- Retrieval Keywords: Java ORM frameworks, Hibernate, MyBatis, Java client load balancing, tidb-loadbalance, org.hibernate.dialect.TiDBDialect, org.hibernate.dialect.MySQL57Dialect, Hibernate 6.0.0.Beta2, 6.2.3.Final, 3.5.13, mysql-connector-java 8.0.33, Propagation.NESTED, @Transactional, savepoint, sql-statement-savepoint, sequences, sql-statement-create-sequence, roundrobin, random, weight, io.github.lastincisor, tidb-loadbalance 0.0.5, must be used with mysql-connector-j, Spring Boot, Build a simple CRUD app with TiDB and Hibernate, Build a simple CRUD app with TiDB and MyBatis
- Follow-up Guidance: The chunk also links to sample applications for Hibernate, Spring Boot, and MyBatis, and notes that tidb-loadbalance uses mysql-connector-j.
- Classification Note: This is reference content because it lists Java ORM and client load balancing support information, version thresholds, dialect identifiers, policy names, and dependency snippets from the official content.

## Official Source Content

### Java ORM frameworks

<div label="Hibernate">

> **Note:**
>
> - Currently, Hibernate does [not support nested transactions](https://stackoverflow.com/questions/37927208/nested-transaction-in-spring-app-with-jpa-postgres).
>
> - Since v6.2.0, TiDB supports [savepoint](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-savepoint). To use the `Propagation.NESTED` transaction propagation option in `@Transactional`, that is, to set `@Transactional(propagation = Propagation.NESTED)`, make sure that your TiDB is v6.2.0 or later.

Support level: **Full**

To avoid manually managing complex relationships between different dependencies of an application, you can use [Gradle](https://gradle.org/install) or [Maven](https://maven.apache.org/install.html) to get all dependencies of your application, including those indirect ones. Note that only Hibernate `6.0.0.Beta2` or above supports the TiDB dialect.

If you are using Maven, add the following to your `<dependencies></dependencies>`:

```xml
<dependency>
    <groupId>org.hibernate.orm</groupId>
    <artifactId>hibernate-core</artifactId>
    <version>6.2.3.Final</version>
</dependency>

<dependency>
    <groupId>mysql</groupId>
    <artifactId>mysql-connector-java</artifactId>
    <version>8.0.33</version>
</dependency>
```

If you are using Gradle, add the following to your `dependencies`:

```gradle
implementation 'org.hibernate:hibernate-core:6.2.3.Final'
implementation 'mysql:mysql-connector-java:8.0.33'
```

- For an example of using Hibernate to build a TiDB application by native Java, see [Build a simple CRUD app with TiDB and Hibernate](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-hibernate).
- For an example of using Spring Data JPA or Hibernate to build a TiDB application by Spring, see [Build a TiDB app using Spring Boot](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-spring-boot).

In addition, you need to specify the TiDB dialect in your [Hibernate configuration file](https://www.tutorialspoint.com/hibernate/hibernate_configuration.htm): `org.hibernate.dialect.TiDBDialect`, which is only supported by Hibernate `6.0.0.Beta2` or above. If your `Hibernate` version is earlier than `6.0.0.Beta2`, upgrade it first.

> **Note:**
>
> If you are unable to upgrade your `Hibernate` version, use the MySQL 5.7 dialect `org.hibernate.dialect.MySQL57Dialect` instead. However, this setting might cause unpredictable results and the absence of some TiDB-specific features, such as [sequences](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-sequence).

</div>

<div label="MyBatis">

Support level: **Full**

To avoid manually managing complex relationships between different dependencies of an application, you can use [Gradle](https://gradle.org/install) or [Maven](https://maven.apache.org/install.html) to get all dependencies of your application, including those indirect dependencies.

If you are using Maven, add the following to your `<dependencies></dependencies>`:

```xml
<dependency>
    <groupId>org.mybatis</groupId>
    <artifactId>mybatis</artifactId>
    <version>3.5.13</version>
</dependency>

<dependency>
    <groupId>mysql</groupId>
    <artifactId>mysql-connector-java</artifactId>
    <version>8.0.33</version>
</dependency>
```

If you are using Gradle, add the following to your `dependencies`:

```gradle
implementation 'org.mybatis:mybatis:3.5.13'
implementation 'mysql:mysql-connector-java:8.0.33'
```

For an example of using MyBatis to build a TiDB application, see [Build a simple CRUD app with TiDB and MyBatis](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-mybatis).

</div>
### Java client load balancing

**tidb-loadbalance**

Support level: **Full**

[tidb-loadbalance](https://github.com/pingcap/tidb-loadbalance) is a load balancing component on the application side. With tidb-loadbalance, you can automatically maintain the node information of TiDB server and distribute JDBC connections on the client using the tidb-loadbalance policies. Using a direct JDBC connection between the client application and TiDB server has higher performance than using the load balancing component.

Currently, tidb-loadbalance supports the following policies: roundrobin, random, and weight.

> **Note:**
>
> tidb-loadbalance must be used with [mysql-connector-j](https://github.com/pingcap/mysql-connector-j).

If you are using Maven, add the following content to the element body of `<dependencies></dependencies>` in the `pom.xml` file:

```xml
<dependency>
  <groupId>io.github.lastincisor</groupId>
  <artifactId>mysql-connector-java</artifactId>
  <version>8.0.29-tidb-1.0.0</version>
</dependency>
<dependency>
  <groupId>io.github.lastincisor</groupId>
  <artifactId>tidb-loadbalance</artifactId>
  <version>0.0.5</version>
</dependency>
```

If you are using Gradle, add the following content to `dependencies`:

```gradle
implementation group: 'io.github.lastincisor', name: 'mysql-connector-java', version: '8.0.29-tidb-1.0.0'
implementation group: 'io.github.lastincisor', name: 'tidb-loadbalance', version: '0.0.5'
```
