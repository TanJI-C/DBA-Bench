# Get TiSpark packages, dependencies, versions, and artifact IDs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tispark-overview.md`
- Source Title: `TiSpark User Guide`
- Source Heading Path: `TiSpark User Guide > Get TiSpark | TiSpark User Guide > Get TiSpark > Get mysql-connector-j | TiSpark User Guide > Get TiSpark > Choose TiSpark version | TiSpark User Guide > Get TiSpark > Get TiSpark jar | TiSpark User Guide > Get TiSpark > TiSpark jar's artifact ID`
- Source Line Ranges: `71-144`
- Source Scope: `shared`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `installation`, `jar`, `dependency`, `mysql-connector-java`, `version-matrix`, `artifact-id`, `build-from-source`, `compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0966_647efcfd89`
- Source ID: `tidb-docs-8.1:tispark-overview.md#get-tispark`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `70cd37e3ffa31a21ec486b1a92af2ef035a72c783053d896170c2e4e7c8348b4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tispark-overview#get-tispark
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tispark-overview.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs TiSpark package acquisition details, mysql-connector-java dependency notes, version compatibility tables, build commands, or artifact ID naming by TiSpark version.
- Retrieval Keywords: Get TiSpark, Get mysql-connector-j, mysql-connector-java, TiSpark needs mysql-connector-java for writing and authentication, spark-submit --jars, Choose TiSpark version, TiDB TiKV PD version, Spark version, Scala version, TiSpark 3.1.x, TiSpark 3.2.x, latest stable versions, Get TiSpark jar, maven central, TiSpark releases, git clone https://github.com/pingcap/tispark.git, mvn clean install -Dmaven.test.skip=true, -Pspark3.2.1, TiSpark jar's artifact ID, tispark-assembly, tispark-assembly-${spark_version}, tispark-assembly-${spark_version}-${scala_version}
- Follow-up Guidance: The source includes example build commands and a table mapping TiSpark versions to Artifact ID patterns.
- Classification Note: This is classified as reference because the content is primarily version matrices, dependency notes, download sources, and artifact naming details.

## Official Source Content

## Get TiSpark

TiSpark is a third-party jar package for Spark that provides the ability to read and write TiKV.
### Get mysql-connector-j

The `mysql-connector-java` dependency is no longer provided because of the limit of the GPL license.

The following versions of TiSpark's jar will no longer include `mysql-connector-java`.

- TiSpark > 3.0.1
- TiSpark > 2.5.1 for TiSpark 2.5.x
- TiSpark > 2.4.3 for TiSpark 2.4.x

However, TiSpark needs `mysql-connector-java` for writing and authentication. In such cases, you need to import `mysql-connector-java` manually using either of the following methods:

- Put `mysql-connector-java` into spark jars file.

- Import `mysql-connector-java` when you submit a spark job. See the following example:

```
spark-submit --jars tispark-assembly-3.0_2.12-3.1.0-SNAPSHOT.jar,mysql-connector-java-8.0.29.jar
```
### Choose TiSpark version

You can choose TiSpark version according to your TiDB and Spark version.

| TiSpark version | TiDB, TiKV, PD version | Spark version | Scala version |
| ---------------  |------------------------| ------------- | ------------- |
| 2.4.x-scala_2.11 | 5.x, 4.x               | 2.3.x, 2.4.x   | 2.11          |
| 2.4.x-scala_2.12 | 5.x, 4.x               | 2.4.x         | 2.12          |
| 2.5.x            | 5.x, 4.x               | 3.0.x, 3.1.x   | 2.12          |
| 3.0.x            | 5.x, 4.x               | 3.0.x, 3.1.x, 3.2.x|2.12|
| 3.1.x            | 6.x, 5.x, 4.x          | 3.0.x, 3.1.x, 3.2.x, 3.3.x|2.12|
| 3.2.x            | 6.x, 5.x, 4.x          | 3.0.x, 3.1.x, 3.2.x, 3.3.x|2.12|

TiSpark 2.4.4, 2.5.3, 3.0.3, 3.1.7, and 3.2.3 are the latest stable versions and are highly recommended.
### Get TiSpark jar

You can get the TiSpark jar using one of the following methods:

- Get from [maven central](https://search.maven.org/) and search for [`pingcap`](http://search.maven.org/#search%7Cga%7C1%7Cpingcap)
- Get from [TiSpark releases](https://github.com/pingcap/tispark/releases)
- Build from source with the steps below

> **Note:**
>
> Currently, java8 is the only choice to build TiSpark, run mvn -version to check.

```
git clone https://github.com/pingcap/tispark.git
```

Run the following command under the TiSpark root directory.

```
// add -Dmaven.test.skip=true to skip the tests
mvn clean install -Dmaven.test.skip=true
// or you can add properties to specify spark version
mvn clean install -Dmaven.test.skip=true -Pspark3.2.1
```
### TiSpark jar's artifact ID

The Artifact ID of TiSpark varies with TiSpark versions.

| TiSpark version                | Artifact ID                                        |
|--------------------------------| -------------------------------------------------- |
| 2.4.x-\${scala_version}, 2.5.0 | tispark-assembly                                   |
| 2.5.1                          | tispark-assembly-\${spark_version}                  |
| 3.0.x, 3.1.x, 3.2.x            | tispark-assembly-\${spark_version}-\${scala_version} |
