# HTTP endpoint SQL file configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-app-config-files.md`
- Source Title: `Data App Configuration Files`
- Source Heading Path: `Data App Configuration Files > HTTP endpoint configuration > SQL file configuration`
- Source Line Ranges: `193-229`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `data-app`, `http-endpoints`, `sql-files`, `endpoint-parameters`, `database-selection`, `query-definition`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0221_bc377aed71`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-app-config-files.md#sql-file-configuration`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `35a6b4d2adb07996f70566f008999569aa1360f748cf271c8df74e17b860604b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-app-config-files#sql-file-configuration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-app-config-files.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how a Data App HTTP endpoint SQL file is named, where it is stored, how to select a database, and how to define endpoint parameters in SQL.
- Retrieval Keywords: HTTP endpoint SQL file configuration, http_endpoints/sql/, <method>-<endpoint-path>.sql, method, endpoint, http_endpoints/config.json, USE database_name;, USE sample_data;, ${variable-name}, ${country}, parameter name is case-sensitive, parameter cannot be a table name or column name
- Follow-up Guidance: The SQL file name must match the endpoint `method` and `endpoint` settings in `http_endpoints/config.json`, and parameter names in the SQL file must match the configured parameter names there.
- Classification Note: This is configuration content because it defines the required SQL file location, naming format, database selection statement, and parameter placeholder rules for Data App HTTP endpoints.

## Official Source Content

### SQL file configuration

The SQL file of an endpoint specifies the SQL statements to query data through the endpoint. You can find the endpoint SQL files of a Data App in the `http_endpoints/sql/` directory. For each endpoint, there should be a corresponding SQL file.

The name of a SQL file is in the `<method>-<endpoint-path>.sql` format, where `<method>` and `<endpoint-path>` must match the `method` and `endpoint` configuration in [`http_endpoints/config.json`](#endpoint-configuration).

In the SQL file, you can write statements such as table join queries, complex queries, and aggregate functions. The following is an example SQL file.

```sql
/* Getting Started:
Enter "USE {database};" before entering your SQL statements.
Type "--your question" + Enter to try out AI-generated SQL queries in the TiDB Cloud console.
Declare a parameter like "Where id = ${arg}".
*/
USE sample_data;
SELECT
  rank,
  company_name,
FROM
  global_fortune_500_2018_2022
WHERE
  country = ${country};
```

When writing a SQL file, pay attention to the following:

- At the beginning of the SQL file, you need to specify the database in the SQL statements. For example, `USE database_name;`.

- To define a parameter of the endpoint, you can insert it as a variable placeholder like `${variable-name}` to the SQL statement.

    In the preceding example, `${country}` is used as a parameter of the endpoint. With this parameter, you can specify a desired country to query in your endpoint curl command.

    > **Note:**
    >
    > - The parameter name is case-sensitive.
    > - The parameter cannot be a table name or column name.
    > - The parameter name in the SQL file match the parameter name configured in [`http_endpoints/config.json`](#endpoint-configuration).
