# dbt-tidb profile fields and supported functions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/integrate-tidbcloud-with-dbt.md`
- Source Title: `Integrate TiDB Cloud with dbt`
- Source Heading Path: `Integrate TiDB Cloud with dbt > Description of profile fields | Integrate TiDB Cloud with dbt > Supported functions`
- Source Line Ranges: `320-355`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`
- Topic Tags: `dbt`, `profiles`, `connection-fields`, `adapter`, `functions`, `sql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0804_8bd71d27ed`
- Source ID: `tidb-docs-8.1:tidb-cloud/integrate-tidbcloud-with-dbt.md#description-of-profile-fields`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bb916e8259505f6a8ad9a8a0ddb9b65cd16e51689dfd07228f2334eb439bc987`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-dbt#description-of-profile-fields
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/integrate-tidbcloud-with-dbt.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the dbt-tidb profile connection fields for TiDB Cloud or the list of functions supported directly in dbt-tidb.
- Retrieval Keywords: Description of profile fields, dbt-tidb, type, server, port, schema, username, password, retries, gateway01.ap-southeast-1.prod.aws.tidbcloud.com, 4000, analytics, supported functions, bool_or, cast_bool_to_text, dateadd, datediff, date_trunc, hash, safe_cast, split_part, last_day, concat, escape_single_quotes, except, intersect, length, position, replace, right
- Follow-up Guidance: The chunk notes that datediff is a little different from dbt-util because it rounds down rather than rounds up.
- Classification Note: This is classified as reference because the content is a lookup-style description of profile options and a supported function list for dbt-tidb.

## Official Source Content

## Description of profile fields

| Option           | Description                                                             | Required? | Example                                           |
|------------------|-------------------------------------------------------------------------|-----------|---------------------------------------------------|
| `type`             | The specific adapter to use                                             | Required  | `tidb`                                            |
| `server`           | The TiDB Cloud clusters' endpoint to connect to                         | Required  | `gateway01.ap-southeast-1.prod.aws.tidbcloud.com` |
| `port`             | The port to use                                                         | Required  | `4000`                                            |
| `schema`           | The schema (database) to normalize data into                      | Required  | `analytics`                                       |
| `username`         | The username to use to connect to the TiDB Cloud clusters               | Required  | `xxxxxxxxxxx.root`                                |
| `password`         | The password to use for authenticating to the TiDB Cloud clusters       | Required  | `"your_password"`                                 |
| `retries`          | The retry times for connection to TiDB Cloud clusters (1 by default)    | Optional  | `2`                                               |
## Supported functions

You can use the following functions directly in dbt-tidb. For information about how to use them, see [dbt-util](https://github.com/dbt-labs/dbt-utils).

The following functions are supported:

- `bool_or`
- `cast_bool_to_text`
- `dateadd`
- `datediff`. Note that `datediff` is a little different from dbt-util. It rounds down rather than rounds up.
- `date_trunc`
- `hash`
- `safe_cast`
- `split_part`
- `last_day`
- `cast_bool_to_text`
- `concat`
- `escape_single_quotes`
- `except`
- `intersect`
- `length`
- `position`
- `replace`
- `right`
