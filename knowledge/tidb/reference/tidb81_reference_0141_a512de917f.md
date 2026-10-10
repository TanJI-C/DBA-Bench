# Hibernate configuration and CRUD code snippets

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-java-hibernate.md`
- Source Title: `Connect to TiDB with Hibernate`
- Source Heading Path: `Connect to TiDB with Hibernate > Sample code snippets | Connect to TiDB with Hibernate > Sample code snippets > Connect to TiDB | Connect to TiDB with Hibernate > Sample code snippets > Insert or update data | Connect to TiDB with Hibernate > Sample code snippets > Query data | Connect to TiDB with Hibernate > Sample code snippets > Delete data`
- Source Line Ranges: `181-260`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`
- Topic Tags: `hibernate-config`, `jdbc`, `sessionfactory`, `crud`, `insert`, `update`, `query`, `delete`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0141_a512de917f`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-java-hibernate.md#sample-code-snippets`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1ca60dbcd9d81e7d9f1b2095272a314421d580b9b9ca934650a3bcd718913aee`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-hibernate#sample-code-snippets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-java-hibernate.md

## Retrieval Guidance

- Use When: Use this chunk when you need Hibernate configuration examples for TiDB or sample Java CRUD snippets using SessionFactory, Session, and PlayerBean.
- Retrieval Keywords: Sample code snippets, hibernate.cfg.xml, hibernate.connection.driver_class, com.mysql.cj.jdbc.Driver, hibernate.dialect, org.hibernate.dialect.TiDBDialect, hibernate.connection.url, hibernate.connection.username, hibernate.connection.password, hibernate.connection.autocommit, hibernate.hbm2ddl.auto, create-drop, hibernate.show_sql, hibernate.format_sql, SessionFactory, Configuration().configure("hibernate.cfg.xml"), addAnnotatedClass, session.persist, session.get, session.remove, PlayerBean
- Follow-up Guidance: The chunk links to the complete sample repository and to separate TiDB guides for insert data, update data, query data, and delete data.
- Classification Note: This is reference content because it supplies reusable configuration and CRUD code examples rather than a full run procedure.

## Official Source Content

## Sample code snippets

You can refer to the following sample code snippets to complete your own application development.

For complete sample code and how to run it, check out the [tidb-samples/tidb-java-hibernate-quickstart](https://github.com/tidb-samples/tidb-java-hibernate-quickstart) repository.
### Connect to TiDB

Edit the Hibernate configuration file `hibernate.cfg.xml`:

```xml
<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE hibernate-configuration PUBLIC
        "-//Hibernate/Hibernate Configuration DTD 3.0//EN"
        "http://www.hibernate.org/dtd/hibernate-configuration-3.0.dtd">
<hibernate-configuration>
    <session-factory>

        <!-- Database connection settings -->
        <property name="hibernate.connection.driver_class">com.mysql.cj.jdbc.Driver</property>
        <property name="hibernate.dialect">org.hibernate.dialect.TiDBDialect</property>
        <property name="hibernate.connection.url">${tidb_jdbc_url}</property>
        <property name="hibernate.connection.username">${tidb_user}</property>
        <property name="hibernate.connection.password">${tidb_password}</property>
        <property name="hibernate.connection.autocommit">false</property>

        <!-- Required so a table can be created from the 'PlayerDAO' class -->
        <property name="hibernate.hbm2ddl.auto">create-drop</property>

        <!-- Optional: Show SQL output for debugging -->
        <property name="hibernate.show_sql">true</property>
        <property name="hibernate.format_sql">true</property>
    </session-factory>
</hibernate-configuration>
```

Be sure to replace `${tidb_jdbc_url}`, `${tidb_user}`, and `${tidb_password}` with the actual values of your TiDB cluster. Then, define the following function:

```java
public SessionFactory getSessionFactory() {
    return new Configuration()
            .configure("hibernate.cfg.xml")
            .addAnnotatedClass(${your_entity_class})
            .buildSessionFactory();
}
```

When using this function, you need to replace `${your_entity_class}` with your own data entity class. For multiple entity classes, you need to add a `.addAnnotatedClass(${your_entity_class})` statement for each. The preceding function is just one way to configure Hibernate. If you encounter any issues in the configuration or want to learn more about Hibernate, refer to the [Hibernate official documentation](https://hibernate.org/orm/documentation).
### Insert or update data

```java
try (Session session = sessionFactory.openSession()) {
    session.persist(new PlayerBean("id", 1, 1));
}
```

For more information, refer to [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data) and [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data).
### Query data

```java
try (Session session = sessionFactory.openSession()) {
    PlayerBean player = session.get(PlayerBean.class, "id");
    System.out.println(player);
}
```

For more information, refer to [Query data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table).
### Delete data

```java
try (Session session = sessionFactory.openSession()) {
    session.remove(new PlayerBean("id", 1, 1));
}
```

For more information, refer to [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data).
