# Choose Driver or ORM overview and Java drivers

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-choose-driver-or-orm.md`
- Source Title: `Choose Driver or ORM`
- Source Heading Path: `Choose Driver or ORM | Choose Driver or ORM > Java | Choose Driver or ORM > Java > Java drivers`
- Source Line Ranges: `5-87`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `ticdc`
- Topic Tags: `driver-selection`, `compatibility-levels`, `mysql-compatibility`, `java`, `jdbc`, `sm3-authentication`, `dependency-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0084_511d2afabb`
- Source ID: `tidb-docs-8.1:develop/dev-guide-choose-driver-or-orm.md#choose-driver-or-orm`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0bc8346f0c137e4aa0f44d10475a57b8b0d64a6b50e885a4ff0c322a0d5d7525`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-choose-driver-or-orm#choose-driver-or-orm
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-choose-driver-or-orm.md

## Retrieval Guidance

- Use When: Use this chunk when selecting a Java JDBC driver for TiDB or checking support levels, MySQL Connector/J compatibility notes, TiDB-JDBC features, and Java dependency coordinates.
- Retrieval Keywords: Choose Driver or ORM, Java drivers, MySQL Connector/J, MySQL-JDBC, TiDB-JDBC, Support level: Full, MySQL Compatibility, Third-party tools supported by TiDB, bug 106252, threads hang, 8.0.31, v6.3.0, automatic TiCDC snapshot maintenance, SM3 authentication plugin, io.github.lastincisor, mysql-connector-java, 8.0.29-tidb-1.0.0, org.bouncycastle, bcprov-jdk15on, bcpkix-jdk15on, Build a simple CRUD app with TiDB and JDBC
- Follow-up Guidance: The chunk also points to the JDBC sample application and the MySQL Compatibility and Third-Party Tools Supported by TiDB pages for related details.
- Classification Note: This is reference content because it summarizes Java driver options, stated support levels, compatibility caveats, and exact Maven and Gradle dependency identifiers from the official documentation.

## Official Source Content

# Choose Driver or ORM

> **Note:**
>
> TiDB provides the following two support levels for drivers and ORMs:
>
> - **Full**: indicates that TiDB is compatible with most features of the tool and maintains compatibility with its newer versions. PingCAP will periodically conduct compatibility tests with the latest version of [Third-party tools supported by TiDB](https://docs.pingcap.com/tidb/stable/develop/dev-guide-third-party-support).
> - **Compatible**: indicates that because the corresponding third-party tool is adapted to MySQL and TiDB is highly compatible with the MySQL protocol, so TiDB can use most features of the tool. However, PingCAP has not completed a full test on all features of the tool, which might lead to some unexpected behaviors.
>
> For more information, refer to [Third-Party Tools Supported by TiDB](https://docs.pingcap.com/tidb/stable/develop/dev-guide-third-party-support).

TiDB is highly compatible with the MySQL protocol but some features are incompatible with MySQL. For a full list of compatibility differences, see [MySQL Compatibility](https://docs.pingcap.com/tidb/stable/mysql-compatibility).
## Java

This section describes how to use drivers and ORM frameworks in Java.
### Java drivers

<div label="MySQL-JDBC">

Support level: **Full**

You can follow the [MySQL documentation](https://dev.mysql.com/doc/connector-j/en/) to download and configure a Java JDBC driver. It is recommended to use the latest GA version of MySQL Connector/J with TiDB v6.3.0 or later.

> **Warning:**
>
> There is a [bug](https://bugs.mysql.com/bug.php?id=106252) in the MySQL Connector/J 8.0 versions before 8.0.31 (see [MySQL JDBC bugs](https://docs.pingcap.com/tidb/stable/develop/dev-guide-third-party-tools-compatibility#mysql-jdbc-bugs) for details), which might cause threads to hang when using TiDB versions earlier than v6.3.0. To avoid this issue, do **NOT** use MySQL Connector/J 8.0.31 or an earlier version.

For an example of how to build a complete application, see [Build a simple CRUD app with TiDB and JDBC](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-jdbc).

</div>
<div label="TiDB-JDBC">

Support level: **Full**

[TiDB-JDBC](https://github.com/pingcap/mysql-connector-j) is a customized Java driver based on MySQL 8.0.29. Compiled based on MySQL official version 8.0.29, TiDB-JDBC fixes the bug of multi-parameter and multi-field EOF in the prepare mode in the original JDBC, and adds features such as automatic TiCDC snapshot maintenance and the SM3 authentication plugin.

The authentication based on SM3 is only supported in TiDB's TiDB-JDBC.

If you are using Maven, add the following content to the `<dependencies></dependencies>` section in the `pom.xml` file:

```xml
<dependency>
  <groupId>io.github.lastincisor</groupId>
  <artifactId>mysql-connector-java</artifactId>
  <version>8.0.29-tidb-1.0.0</version>
</dependency>
```

If you need to enable SM3 authentication, add the following content to the `<dependencies></dependencies>` section in the `pom.xml` file:

```xml
<dependency>
  <groupId>io.github.lastincisor</groupId>
  <artifactId>mysql-connector-java</artifactId>
  <version>8.0.29-tidb-1.0.0</version>
</dependency>
<dependency>
    <groupId>org.bouncycastle</groupId>
    <artifactId>bcprov-jdk15on</artifactId>
    <version>1.67</version>
</dependency>
<dependency>
    <groupId>org.bouncycastle</groupId>
    <artifactId>bcpkix-jdk15on</artifactId>
    <version>1.67</version>
</dependency>
```

If you use Gradle, add the following content to `dependencies`:

```gradle
implementation group: 'io.github.lastincisor', name: 'mysql-connector-java', version: '8.0.29-tidb-1.0.0'
implementation group: 'org.bouncycastle', name: 'bcprov-jdk15on', version: '1.67'
implementation group: 'org.bouncycastle', name: 'bcpkix-jdk15on', version: '1.67'
```

</div>
