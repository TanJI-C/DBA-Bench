# Third-party tool support overview and drivers

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-third-party-support.md`
- Source Title: `Third-Party Tools Supported by TiDB`
- Source Heading Path: `Third-Party Tools Supported by TiDB | Third-Party Tools Supported by TiDB > Support Level | Third-Party Tools Supported by TiDB > Driver`
- Source Line Ranges: `5-64`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`
- Topic Tags: `third-party-tools`, `support-levels`, `drivers`, `mysql-compatibility`, `connectivity`, `adapters`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0184_334df01690`
- Source ID: `tidb-docs-8.1:develop/dev-guide-third-party-support.md#third-party-tools-supported-by-tidb`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7e5340f163c5059714c521684e323c2a4370b63f409621ecb8a59c14d6158527`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-third-party-support#third-party-tools-supported-by-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-third-party-support.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the TiDB support levels for third-party drivers or asks which MySQL-compatible drivers and TiDB adapters are listed for Go or Java.
- Retrieval Keywords: Third-Party Tools Supported by TiDB, Support Level, Driver, Full, Compatible, MySQL protocol, Application retry and error handling, Go-MySQL-Driver, v1.6.0, JDBC, 8.0, pingcap/mysql-connector-j, pingcap/tidb-loadbalance, Connect to TiDB with Go-MySQL-Driver, Connect to TiDB with JDBC
- Follow-up Guidance: If users encounter problems when connecting to TiDB using the listed tools, the content says to submit an issue on GitHub with details to promote support on this tool.
- Classification Note: This is reference content because it defines the documented support levels and lists tested third-party drivers, versions, adapters, and tutorial links.

## Official Source Content

# Third-Party Tools Supported by TiDB

> **Note:**
>
> This document only lists common [third-party tools](https://en.wikipedia.org/wiki/Third-party_source) supported by TiDB. Some other third-party tools are not listed, not because they are not supported, but because PingCAP is not sure whether they use features that are incompatible with TiDB.

TiDB is [highly compatible with the MySQL protocol](https://docs.pingcap.com/tidb/stable/mysql-compatibility), so most of the MySQL drivers, ORM frameworks, and other tools that adapt to MySQL are compatible with TiDB. This document focuses on these tools and their support levels for TiDB.
## Support Level

PingCAP works with the community and provides the following support levels for third-party tools:

- **_Full_**: Indicates that TiDB is already compatible with most functionalities of the corresponding third-party tool, and maintains compatibility with its newer versions. PingCAP will periodically conduct compatibility tests with the latest version of the tool.
- **_Compatible_**: Indicates that because the corresponding third-party tool is adapted to MySQL and TiDB is highly compatible with the MySQL protocol, so TiDB can use most features of the tool. However, PingCAP has not completed a full test on all features of the tool, which might lead to some unexpected behaviors.

> **Note:**
>
> Unless specified, support for [Application retry and error handling](https://docs.pingcap.com/tidb/stable/develop/dev-guide-transaction-troubleshoot#application-retry-and-error-handling) is not included for **Driver** or **ORM frameworks**.

If you encounter problems when connecting to TiDB using the tools listed in this document, please submit an [issue](https://github.com/pingcap/tidb/issues/new?assignees=&labels=type%2Fquestion&template=general-question.md) on GitHub with details to promote support on this tool.
## Driver

<table>
   <thead>
      <tr>
         <th>Language</th>
         <th>Driver</th>
         <th>Latest tested version</th>
         <th>Support level</th>
         <th>TiDB adapter</th>
         <th>Tutorial</th>
      </tr>
   </thead>
   <tbody>
      <tr>
         <td>Go</td>
         <td><a href="https://github.com/go-sql-driver/mysql" target="_blank" referrerpolicy="no-referrer-when-downgrade">Go-MySQL-Driver</a></td>
         <td>v1.6.0</td>
         <td>Full</td>
         <td>N/A</td>
         <td><a href="/tidb/v8.1/dev-guide-sample-application-golang-sql-driver">Connect to TiDB with Go-MySQL-Driver</a></td>
      </tr>
      <tr>
         <td>Java</td>
         <td><a href="https://dev.mysql.com/downloads/connector/j/" target="_blank" referrerpolicy="no-referrer-when-downgrade">JDBC</a></td>
         <td>8.0</td>
         <td>Full</td>
         <td>
            <ul>
               <li><a href="/tidb/v8.1/dev-guide-choose-driver-or-orm#java-drivers" data-href="/tidb/v8.1/dev-guide-choose-driver-or-orm#java-drivers">pingcap/mysql-connector-j</a></li>
               <li><a href="/tidb/v8.1/dev-guide-choose-driver-or-orm#tidb-loadbalance" data-href="/tidb/v8.1/dev-guide-choose-driver-or-orm#tidb-loadbalance">pingcap/tidb-loadbalance</a></li>
            </ul>
         </td>
         <td><a href="/tidb/v8.1/dev-guide-sample-application-java-jdbc">Connect to TiDB with JDBC</a></td>
      </tr>
   </tbody>
</table>
