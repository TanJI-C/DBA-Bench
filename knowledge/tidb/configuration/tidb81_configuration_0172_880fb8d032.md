# Table filter usage in CLI and TOML configs

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/table-filter.md`
- Source Title: `Table Filter`
- Source Heading Path: `Table Filter | Table Filter > Usage | Table Filter > Usage > CLI | Table Filter > Usage > TOML configuration files`
- Source Line Ranges: `5-83`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `br`, `dumpling`, `lightning`, `ticdc`, `tiup`
- Topic Tags: `table-filter`, `cli`, `toml`, `filter-rules`, `migration-tools`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0172_880fb8d032`
- Source ID: `tidb-docs-8.1:table-filter.md#table-filter`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a92e899ca6a739fceecb0ef0b4d674c7d37ceef44957103ba47c0d9a56a4351f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/table-filter#table-filter
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/table-filter.md

## Retrieval Guidance

- Use When: Use this when looking for how to pass table filter rules in command line flags or TOML configuration for TiDB migration tools.
- Retrieval Keywords: table filter, -f, --filter, db.table, foo*.*, bar*.*, tiup br backup full, tiup br restore full, tiup dumpling, tiup tidb-lightning, [mydumper] filter, [filter] rules, [[sink.dispatchers]] matcher, TiCDC
- Follow-up Guidance: It also shows example CLI and TOML snippets for BR, Dumpling, TiDB Lightning, and TiCDC using the shared filter syntax.
- Classification Note: This is configuration content because it shows the exact CLI parameters and TOML keys used to configure table filters in supported tools.

## Official Source Content

# Table Filter

The TiDB migration tools operate on all the databases by default, but oftentimes only a subset is needed. For example, you only want to work with the schemas in the form of `foo*` and `bar*` and nothing else.

Since TiDB 4.0, all TiDB migration tools share a common filter syntax to define subsets. This document describes how to use the table filter feature.
## Usage
### CLI

Table filters can be applied to the tools using multiple `-f` or `--filter` command line parameters. Each filter is in the form of `db.table`, where each part can be a wildcard (further explained in the [next section](#wildcards)). The following lists the example usage.

* [BR](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview):

    ```shell
    tiup br backup full -f 'foo*.*' -f 'bar*.*' -s 'local:///tmp/backup'
    ```

    ```shell
    tiup br restore full -f 'foo*.*' -f 'bar*.*' -s 'local:///tmp/backup'
    ```

* [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview):

    ```shell
    tiup dumpling -f 'foo*.*' -f 'bar*.*' -P 3306 -o /tmp/data/
    ```

* [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview):

    ```shell
    tiup tidb-lightning -f 'foo*.*' -f 'bar*.*' -d /tmp/data/ --backend tidb
    ```

* [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning-overview):

    ```shell
    tiup tidb-lightning -f 'foo*.*' -f 'bar*.*' -d /tmp/data/ --backend tidb
    ```
### TOML configuration files

Table filters in TOML files are specified as [array of strings](https://toml.io/en/v1.0.0-rc.1#section-15). The following lists the example usage.

* TiDB Lightning:

    ```toml
    [mydumper]
    filter = ['foo*.*', 'bar*.*']
    ```

* [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview):

    ```toml
    [filter]
    rules = ['foo*.*', 'bar*.*']

    [[sink.dispatchers]]
    matcher = ['db1.*', 'db2.*', 'db3.*']
    dispatcher = 'ts'
    ```
