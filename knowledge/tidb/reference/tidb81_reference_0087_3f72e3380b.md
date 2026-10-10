# Python drivers and ORM frameworks for TiDB

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-choose-driver-or-orm.md`
- Source Title: `Choose Driver or ORM`
- Source Heading Path: `Choose Driver or ORM > Python > Python drivers | Choose Driver or ORM > Python > Python ORM frameworks`
- Source Line Ranges: `241-310`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `cloud`
- Topic Tags: `python`, `drivers`, `orm`, `compatibility`, `support-level`, `versions`, `installation`, `application-connection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0087_3f72e3380b`
- Source ID: `tidb-docs-8.1:develop/dev-guide-choose-driver-or-orm.md#python-drivers`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2fb1df3d1f4d75ca2a596048ecf5c10e10c8674f20c8d4caad6fb53efc62fdd9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-choose-driver-or-orm#python-drivers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-choose-driver-or-orm.md

## Retrieval Guidance

- Use When: Use this chunk when identifying supported Python drivers or ORM frameworks for TiDB, including support level, recommended versions, installation phrases, and example connection guides.
- Retrieval Keywords: PyMySQL, PyMySQL 1.0.2 or later, mysqlclient, mysqlclient 2.1.1 or later, MySQL Connector/Python, Connector/Python 8.0.31 or later, Django, django-tidb, SQLAlchemy, pip install SQLAlchemy==1.4.44, SQLAlchemy 1.4.44 or later, peewee, pip install peewee==3.15.4, peewee 3.15.4 or later, Support level: Compatible, Support level: Full, Connect to TiDB with PyMySQL, Connect to TiDB with mysqlclient, Connect to TiDB with MySQL Connector/Python, Connect to TiDB with Django, Connect to TiDB with SQLAlchemy, Connect to TiDB with peewee, connect to your TiDB cluster
- Follow-up Guidance: After determining the driver or ORM, the source points to connecting to your TiDB cluster and to example application guides for each listed Python option.
- Classification Note: This is reference content because it lists Python drivers and ORM frameworks for TiDB with their support levels, recommended versions, installation identifiers, and related example guides from the official content.

## Official Source Content

### Python drivers

<div label="PyMySQL">

Support level: **Compatible**

You can follow the [PyMySQL documentation](https://pypi.org/project/PyMySQL/) to download and configure the driver. It is recommended to use PyMySQL 1.0.2 or later versions.

For an example of using PyMySQL to build a TiDB application, see [Connect to TiDB with PyMySQL](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-python-pymysql).

</div>
<div label="mysqlclient">

Support level: **Compatible**

You can follow the [mysqlclient documentation](https://pypi.org/project/mysqlclient/) to download and configure the driver. It is recommended to use mysqlclient 2.1.1 or later versions.

For an example of using mysqlclient to build a TiDB application, see [Connect to TiDB with mysqlclient](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-python-mysqlclient).

</div>
<div label="MySQL Connector/Python">

Support level: **Compatible**

You can follow the [MySQL Connector/Python documentation](https://dev.mysql.com/doc/connector-python/en/connector-python-installation-binary.html) to download and configure the driver. It is recommended to use Connector/Python 8.0.31 or later versions.

For an example of using MySQL Connector/Python to build a TiDB application, see [Connect to TiDB with MySQL Connector/Python](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-python-mysql-connector).

</div>
### Python ORM frameworks

<div label="Django">

Support level: **Full**

[Django](https://docs.djangoproject.com/) is a popular Python web framework. To solve the compatibility issue between TiDB and Django, PingCAP provides a TiDB dialect `django-tidb`. To install it, you can see the [`django-tidb` documentation](https://github.com/pingcap/django-tidb#installation-guide).

For an example of using Django to build a TiDB application, see [Connect to TiDB with Django](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-python-django).

</div>
<div label="SQLAlchemy">

Support level: **Full**

[SQLAlchemy](https://www.sqlalchemy.org/) is a popular ORM framework for Python. To get all dependencies in your application, you can use the `pip install SQLAlchemy==1.4.44` command. It is recommended to use SQLAlchemy 1.4.44 or later versions.

For an example of using SQLAlchemy to build a TiDB application, see [Connect to TiDB with SQLAlchemy](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-python-sqlalchemy).

</div>
<div label="peewee">

Support level: **Compatible**

[peewee](http://docs.peewee-orm.com/en/latest/) is a popular ORM framework for Python. To get all dependencies in your application, you can use the `pip install peewee==3.15.4` command. It is recommended to use peewee 3.15.4 or later versions.

For an example of using peewee to build a TiDB application, see [Connect to TiDB with peewee](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-python-peewee).

</div>

After you have determined the driver or ORM, you can [connect to your TiDB cluster](https://docs.pingcap.com/tidbcloud/connect-to-tidb-cluster).
