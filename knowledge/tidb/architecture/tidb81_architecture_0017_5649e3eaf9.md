# Java application components interacting with TiDB

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/java-app-best-practices.md`
- Source Title: `Best Practices for Developing Java Applications with TiDB`
- Source Heading Path: `Best Practices for Developing Java Applications with TiDB | Best Practices for Developing Java Applications with TiDB > Database-related components in Java applications`
- Source Line Ranges: `5-30`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`
- Topic Tags: `java`, `application-components`, `jdbc`, `connection-pool`, `data-access-framework`, `spring-transaction`, `mysql-protocol`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0017_5649e3eaf9`
- Source ID: `tidb-docs-8.1:develop/java-app-best-practices.md#best-practices-for-developing-java-applications-with-tidb`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `55c99b6f3fdb59971b48dbe6dfc1218e2e36b7aba1da19ee68b4a7d8590175ec`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/java-app-best-practices#best-practices-for-developing-java-applications-with-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/java-app-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when identifying the Java-side components that interact with TiDB and how JDBC, connection pools, data access frameworks, and Spring Transaction fit together.
- Retrieval Keywords: MySQL protocol, JDBC API, MySQL Connector/J, MariaDB Connector/J, DataSource, connection pool, MyBatis, Hibernate, Spring Transaction, Java application components interacting with TiDB
- Follow-up Guidance: The document continues with issues and solutions for developing Java applications using these components.
- Classification Note: This is classified as architecture because it outlines the database-related Java application components and their interaction path with TiDB.

## Official Source Content

# Best Practices for Developing Java Applications with TiDB

This document introduces the best practice for developing Java applications to better use TiDB. Based on some common Java application components that interact with the backend TiDB database, this document also provides the solutions to commonly encountered issues during development.
## Database-related components in Java applications

Common components that interact with the TiDB database in Java applications include:

- Network protocol: A client interacts with a TiDB server via the standard [MySQL protocol](https://dev.mysql.com/doc/dev/mysql-server/latest/PAGE_PROTOCOL.html).
- JDBC API and JDBC drivers: Java applications usually use the standard [JDBC (Java Database Connectivity)](https://docs.oracle.com/javase/8/docs/technotes/guides/jdbc/) API to access a database. To connect to TiDB, you can use a JDBC driver that implements the MySQL protocol via the JDBC API. Such common JDBC drivers for MySQL include [MySQL Connector/J](https://github.com/mysql/mysql-connector-j) and [MariaDB Connector/J](https://mariadb.com/docs/connectors/mariadb-connector-j/about-mariadb-connector-j#about-mariadb-connectorj).
- Database connection pool: To reduce the overhead of creating a connection each time it is requested, applications usually use a connection pool to cache and reuse connections. JDBC [DataSource](https://docs.oracle.com/javase/8/docs/api/javax/sql/DataSource.html) defines a connection pool API. You can choose from different open-source connection pool implementations as needed.
- Data access framework: Applications usually use a data access framework such as [MyBatis](https://mybatis.org/mybatis-3/index.html) and [Hibernate](https://hibernate.org/) to further simplify and manage the database access operations.
- Application implementation: The application logic controls when to send what commands to the database. Some applications use [Spring Transaction](https://docs.spring.io/spring/docs/4.2.x/spring-framework-reference/html/transaction.html) aspects to manage transactions' start and commit logics.

![Java application components](/media/best-practices/java-practice-1.png)

From the above diagram, you can see that a Java application might do the following things:

- Implement the MySQL protocol via the JDBC API to interact with TiDB.
- Get a persistent connection from the connection pool.
- Use a data access framework such as MyBatis to generate and execute SQL statements.
- Use Spring Transaction to automatically start or stop a transaction.

The rest of this document describes the issues and their solutions when you develop a Java application using the above components.
