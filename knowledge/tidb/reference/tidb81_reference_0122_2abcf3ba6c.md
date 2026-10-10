# TiDB Cloud developer overview and language/client guides

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-overview.md`
- Source Title: `Developer Guide Overview`
- Source Heading Path: `Developer Guide Overview | Developer Guide Overview > Guides by language and framework | Developer Guide Overview > Use MySQL client software | Developer Guide Overview > Additional resources`
- Source Line Ranges: `5-190`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`, `sql`
- Topic Tags: `developer-guide`, `language-guides`, `frameworks`, `client-tools`, `cli`, `integrations`, `resources`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0122_2abcf3ba6c`
- Source ID: `tidb-docs-8.1:develop/dev-guide-overview.md#developer-guide-overview`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `937f11734d6feef6c2989f1d76e6060b67200f085f2e4c2afc66ed48ca1d603e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-overview#developer-guide-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-overview.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Cloud developer overview page that lists language and framework guides, MySQL client software options, CLI, integrations, and additional learning resources.
- Retrieval Keywords: Developer Guide Overview, TiDB Cloud, Serverless Driver (beta), Next.js, Prisma, TypeORM, Sequelize, mysql.js, node-mysql2, AWS Lambda, Django, MySQL Connector/Python, PyMySQL, mysqlclient, SQLAlchemy, peewee, JDBC, MyBatis, Hibernate, Spring Boot, Go-MySQL-Driver, GORM, Ruby on Rails, mysql2, MySQL Workbench, Visual Studio Code, SQLTools extension in VSCode, DBeaver, DataGrip, TiDB Cloud CLI, services integrations, TiDB database development reference, Introduction to TiDB, TiDB Kernel Development Guide, MySQL-compatible database
- Follow-up Guidance: The page also points to TiDB Cloud CLI, services integrations, the TiDB database development reference, the Introduction to TiDB course, the TiDB Kernel Development Guide, and the Quick Start Guide for the TiDB Database Platform.
- Classification Note: This is reference content because it is an overview index of TiDB Cloud developer guides, client tools, and related resources rather than a task-specific procedure.

## Official Source Content

# Developer Guide Overview

Learn TiDB Cloud basics
TiDB Cloud is the fully-managed service built on top of TiDB, which is highly compatible with the MySQL protocol and supports most MySQL syntax and features.
## Guides by language and framework

Build your application with the language you use by following the guides with sample codes.

JavaScript
[Serverless Driver (beta)](/tidbcloud/serverless-driver)

Connect to TiDB Cloud over HTTPS in Edge Function.

[Next.js](/tidbcloud/dev-guide-sample-application-nextjs)

Connect Next.js with mysql2 to TiDB Cloud.

[Prisma](/tidbcloud/dev-guide-sample-application-nodejs-prisma)

Connect to TiDB Cloud with Prisma ORM.

[TypeORM](/tidbcloud/dev-guide-sample-application-nodejs-typeorm)

Connect to TiDB Cloud with TypeORM.

[Sequelize](/tidbcloud/dev-guide-sample-application-nodejs-sequelize)

Connect to TiDB Cloud with Sequelize ORM.

[mysql.js](/tidbcloud/dev-guide-sample-application-nodejs-mysqljs)

Connect Node.js with mysql.js module to TiDB Cloud.

[node-mysql2](/tidbcloud/dev-guide-sample-application-nodejs-mysql2)

Connect Node.js with node-mysql2 module to TiDB Cloud.

[AWS Lambda](/tidbcloud/dev-guide-sample-application-aws-lambda)

Connect AWS Lambda Function with mysql2 to TiDB Cloud.

Python
[Django](/tidbcloud/dev-guide-sample-application-python-django)

Connect Django application with django-tidb to TiDB Cloud.

[MySQL Connector/Python](/tidbcloud/dev-guide-sample-application-python-mysql-connector)

Connect to TiDB Cloud with MySQL official package.

[PyMySQL](/tidbcloud/dev-guide-sample-application-python-pymysql)

Connect to TiDB Cloud with PyMySQL package.

[mysqlclient](/tidbcloud/dev-guide-sample-application-python-mysqlclient)

Connect to TiDB Cloud with mysqlclient package.

[SQLAlchemy](/tidbcloud/dev-guide-sample-application-python-sqlalchemy)

Connect to TiDB Cloud with SQLAlchemy ORM.

[peewee](/tidbcloud/dev-guide-sample-application-python-peewee)

Connect to TiDB Cloud with Peewee ORM.

Java
[JDBC](/tidbcloud/dev-guide-sample-application-java-jdbc)

Connect to TiDB Cloud with JDBC (MySQL Connector/J).

[MyBatis](/tidbcloud/dev-guide-sample-application-java-mybatis)

Connect to TiDB Cloud with MyBatis ORM.

[Hibernate](/tidbcloud/dev-guide-sample-application-java-hibernate)

Connect to TiDB Cloud with Hibernate ORM.

[Spring Boot](/tidbcloud/dev-guide-sample-application-java-spring-boot)

Connect Spring based application with Spring Data JPA to TiDB Cloud.

Go
[Go-MySQL-Driver](/tidbcloud/dev-guide-sample-application-golang-sql-driver)

Connect to TiDB Cloud with MySQL driver for Go.

[GORM](/tidbcloud/dev-guide-sample-application-golang-gorm)

Connect to TiDB Cloud with GORM.

Ruby
[Ruby on Rails](/tidbcloud/dev-guide-sample-application-ruby-rails)

Connect Ruby on Rails application with Active Record ORM to TiDB Cloud.

[mysql2](/tidbcloud/dev-guide-sample-application-ruby-mysql2)

Connect to TiDB Cloud with mysql2 driver.

In addition to these guides, PingCAP works with the community to [support the third-party MySQL driver, ORMs and tools](https://docs.pingcap.com/tidb/stable/develop/dev-guide-third-party-support).
## Use MySQL client software

As TiDB is a MySQL-compatible database, you can use many client software tools to connect to TiDB Cloud and manage the databases just like you did before. Or, use our <a href="/tidbcloud/get-started-with-cli">command line tool</a> to connect and manage your databases.

[MySQL Workbench](/tidbcloud/dev-guide-gui-mysql-workbench)

Connect and manage TiDB Cloud databases with MySQL Workbench.

[Visual Studio Code](/tidbcloud/dev-guide-gui-vscode-sqltools)

Connect and manage TiDB Cloud databases with SQLTools extension in VSCode.

[DBeaver](/tidbcloud/dev-guide-gui-dbeaver)

Connect and manage TiDB Cloud databases with DBeaver.

[DataGrip](/tidbcloud/dev-guide-gui-datagrip)

Connect and manage TiDB Cloud databases with DataGrip by JetBrains.
## Additional resources

Learn other topics about developing with TiDB Cloud.

- Use <a href="/tidbcloud/get-started-with-cli">TiDB Cloud CLI</a> to develop, manage and deploy your applications.
- Explore popular <a href="/tidbcloud/integrate-tidbcloud-with-airbyte">services integrations</a> with TiDB Cloud.
- Use [TiDB database development reference](https://docs.pingcap.com/tidb/stable/develop/dev-guide-schema-design-overview) to design, interact, optimize and troubleshoot with your data and schema.
- Follow the free online course [Introduction to TiDB](https://eng.edu.pingcap.com/catalog/info/id:203/?utm_source=docs-dev-guide).

This guide is written for application developers, but if you are interested in the inner workings of TiDB or want to get involved in TiDB development, read the [TiDB Kernel Development Guide](https://pingcap.github.io/tidb-dev-guide/) for more information about TiDB.

This tutorial shows how to quickly build an application using TiDB, the possible use cases of TiDB and how to handle common problems.

Before reading this page, it is recommended that you read the [Quick Start Guide for the TiDB Database Platform](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb).
