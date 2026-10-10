# Connect to TiDB with MySQL, JDBC, and Hibernate

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-connect-to-tidb.md`
- Source Title: `Connect to TiDB`
- Source Heading Path: `Connect to TiDB | Connect to TiDB > MySQL | Connect to TiDB > JDBC | Connect to TiDB > JDBC > Connection parameters | Connect to TiDB > Hibernate | Connect to TiDB > Hibernate > Connection parameters | Connect to TiDB > Need help?`
- Source Line Ranges: `5-139`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `connectivity`, `mysql-protocol`, `mysql-client`, `mysql-shell`, `jdbc`, `datasource`, `connection-string`, `connection-parameters`, `hibernate`, `orm`, `sql-users`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0089_bef902c753`
- Source ID: `tidb-docs-8.1:develop/dev-guide-connect-to-tidb.md#connect-to-tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d94c519ade25380f20835510a39be84b10fd1fd637f3e31e7427794a1e14bff9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-connect-to-tidb#connect-to-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-connect-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs the official TiDB connection examples and parameters for MySQL Client, MySQL Shell, JDBC, or Hibernate over the MySQL protocol.
- Retrieval Keywords: Connect to TiDB, MySQL Client/Server Protocol, MySQL Client, MySQL Shell, mysql --host <tidb_server_host> --port 4000 -u root -p --comments, mysqlsh --sql mysql://root@<tidb_server_host>:4000, JDBC, MysqlDataSource, MysqlConnectionPoolDataSource, setURL, jdbc:mysql://{host}:{port}/{database}?user={username}&password={password}, Hibernate ORM, hibernate.connection.url, com.mysql.cj.jdbc.Driver, org.hibernate.dialect.TiDBDialect, hibernate.cfg.xml, SessionFactory, Configuration().configure("hibernate.cfg.xml").buildSessionFactory(), &amp;, {username}, {password}, {host}, {port}, {database}
- Follow-up Guidance: If more detail is needed, the source points to MySQL Client Options, JDBC documentation, Hibernate documentation, TiDB User Account Management, and community or support channels.
- Classification Note: This is classified as a reference chunk because it provides supported connection methods, exact command examples, connection strings, parameter definitions, and related identifiers for connecting to TiDB.

## Official Source Content

# Connect to TiDB

TiDB is highly compatible with the MySQL protocol. For a full list of client link parameters, see [MySQL Client Options](https://dev.mysql.com/doc/refman/8.0/en/mysql-command-options.html).

TiDB supports the [MySQL Client/Server Protocol](https://dev.mysql.com/doc/dev/mysql-server/latest/PAGE_PROTOCOL.html), which allows most client drivers and ORM frameworks to connect to TiDB just as they connect to MySQL.
## MySQL

You can choose to use MySQL Client or MySQL Shell based on your personal preferences.

<div label="MySQL Client">

You can connect to TiDB using MySQL Client, which can be used as a command-line tool for TiDB. To install MySQL Client, follow the instructions below for YUM based Linux distributions.

```shell
sudo yum install mysql
```

After the installation, you can connect to TiDB using the following command:

```shell
mysql --host <tidb_server_host> --port 4000 -u root -p --comments
```

</div>

<div label="MySQL Shell">

You can connect to TiDB using MySQL Shell, which can be used as a command-line tool for TiDB. To install MySQL Shell, follow the instructions in the [MySQL Shell documentation](https://dev.mysql.com/doc/mysql-shell/8.0/en/mysql-shell-install.html). After the installation, you can connect to TiDB using the following command:

```shell
mysqlsh --sql mysql://root@<tidb_server_host>:4000
```

</div>
## JDBC

You can connect to TiDB using the [JDBC](https://dev.mysql.com/doc/connector-j/en/) driver. To do that, you need to create a `MysqlDataSource` or `MysqlConnectionPoolDataSource` object (both objects support the `DataSource` interface), and then set the connection string using the `setURL` function.

For example:

```java
MysqlDataSource mysqlDataSource = new MysqlDataSource();
mysqlDataSource.setURL("jdbc:mysql://{host}:{port}/{database}?user={username}&password={password}");
```

For more information on JDBC connections, see the [JDBC documentation](https://dev.mysql.com/doc/connector-j/en/)
### Connection parameters

| Parameter name | Description |
| :---: | :----------------------------: |
| `{username}` | A SQL user to connect to the TiDB cluster |
| `{password}` | The password of the SQL user |
| `{host}` | [Host](https://en.wikipedia.org/wiki/Host_(network)) of a TiDB node |
| `{port}` | Port that the TiDB node is listening on |
| `{database}` | Name of an existing database |

For more information about TiDB SQL users, see [TiDB User Account Management](https://docs.pingcap.com/tidb/stable/user-account-management).

For more information about TiDB SQL users, see [TiDB User Account Management](https://docs.pingcap.com/tidb/stable/user-account-management).
## Hibernate

You can connect to TiDB using the [Hibernate ORM](https://hibernate.org/orm/). To do that, you need to set `hibernate.connection.url` in the Hibernate configuration file to a legal TiDB connection string.

For example, if you use a `hibernate.cfg.xml` configuration file, set `hibernate.connection.url` as follows:

```xml
<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE hibernate-configuration PUBLIC
        "-//Hibernate/Hibernate Configuration DTD 3.0//EN"
        "http://www.hibernate.org/dtd/hibernate-configuration-3.0.dtd">
<hibernate-configuration>
    <session-factory>
        <property name="hibernate.connection.driver_class">com.mysql.cj.jdbc.Driver</property>
        <property name="hibernate.dialect">org.hibernate.dialect.TiDBDialect</property>
        <property name="hibernate.connection.url">jdbc:mysql://{host}:{port}/{database}?user={user}&amp;password={password}</property>
    </session-factory>
</hibernate-configuration>
```

After the configuration is done, you can use the following command to read the configuration file and get the `SessionFactory` object:

```java
SessionFactory sessionFactory = new Configuration().configure("hibernate.cfg.xml").buildSessionFactory();
```

Note the following:

- Because the `hibernate.cfg.xml` configuration file is in the XML format and `&` is a special character in XML, you need to change `&` to `&amp;` when configuring the file. For example, you need to change the connection string `hibernate.connection.url` from `jdbc:mysql://{host}:{port}/{database}?user={user}&password={password}` to `jdbc:mysql://{host}:{ port}/{database}?user={user}&amp;password={password}`.
- It is recommended that you use the `TiDB` dialect by setting `hibernate.dialect` to `org.hibernate.dialect.TiDBDialect`.
- Hibernate supports TiDB dialects starting from `6.0.0.Beta2`, so it is recommended that you use Hibernate `6.0.0.Beta2` or a later version to connect to TiDB.

For more information about Hibernate connection parameters, see [Hibernate documentation](https://hibernate.org/orm/documentation).
### Connection parameters

| Parameter name | Description |
| :---: | :----------------------------: |
| `{username}` |  A SQL user to connect to the TiDB cluster  |
| `{password}` | The password of the SQL user |
| `{host}` | [Host](https://en.wikipedia.org/wiki/Host_(network)) of a TiDB node |
| `{port}` | Port that the TiDB node is listening on |
| `{database}` |  Name of an existing database |

For more information about TiDB SQL users, see [TiDB User Account Management](https://docs.pingcap.com/tidb/stable/user-account-management).

For more information about TiDB SQL users, see [TiDB User Account Management](https://docs.pingcap.com/tidb/stable/user-account-management).
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).
