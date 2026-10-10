# Golang drivers and ORM frameworks, plus Python section intro

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-choose-driver-or-orm.md`
- Source Title: `Choose Driver or ORM`
- Source Heading Path: `Choose Driver or ORM > Golang | Choose Driver or ORM > Golang > Golang drivers | Choose Driver or ORM > Golang > Golang ORM frameworks | Choose Driver or ORM > Python`
- Source Line Ranges: `208-240`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`
- Topic Tags: `golang`, `sql-driver`, `gorm`, `orm`, `python`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0086_5cd141d9d4`
- Source ID: `tidb-docs-8.1:develop/dev-guide-choose-driver-or-orm.md#golang`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c58e504c9aee9c06dd44acdc33bf0113e8d84b7ef4be9f5ebbbabe72a068e9c5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-choose-driver-or-orm#golang
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-choose-driver-or-orm.md

## Retrieval Guidance

- Use When: Use this chunk when identifying supported Golang drivers or ORM frameworks for TiDB, or when looking for the start of the Python driver and ORM section.
- Retrieval Keywords: Golang drivers, go-sql-driver/mysql, Connect to TiDB with Go-MySQL-Driver, Golang ORM frameworks, GORM, gorm.io/gorm, gorm.io/driver/mysql, go get -u, Connect to TiDB with GORM, Python, This section describes how to use drivers and ORM frameworks in Python
- Follow-up Guidance: The chunk points to sample applications for go-sql-driver/mysql and GORM and introduces the Python section without further details in this excerpt.
- Classification Note: This is reference content because it names the supported Golang driver and ORM framework, gives exact package install commands, and marks the beginning of the Python section in the official documentation.

## Official Source Content

## Golang

This section describes how to use drivers and ORM frameworks in Golang.
### Golang drivers

**go-sql-driver/mysql**

Support level: **Full**

To download and configure a Golang driver, refer to the [go-sql-driver/mysql documentation](https://github.com/go-sql-driver/mysql).

For an example of how to build a complete application, see [Connect to TiDB with Go-MySQL-Driver](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-golang-sql-driver).
### Golang ORM frameworks

**GORM**

Support level: **Full**

GORM is a popular ORM framework for Golang. To get all dependencies in your application, you can use the `go get` command.

```shell
go get -u gorm.io/gorm
go get -u gorm.io/driver/mysql
```

For an example of using GORM to build a TiDB application, see [Connect to TiDB with GORM](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-golang-gorm).
## Python

This section describes how to use drivers and ORM frameworks in Python.
