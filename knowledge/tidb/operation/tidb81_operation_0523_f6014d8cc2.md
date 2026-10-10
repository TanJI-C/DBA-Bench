# TiUP Playground startup examples for versions, configuration, binaries, scaling, and tags

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-playground.md`
- Source Title: `Quickly Deploy a Local TiDB Cluster`
- Source Heading Path: `Quickly Deploy a Local TiDB Cluster > Examples | Quickly Deploy a Local TiDB Cluster > Examples > Check available TiDB versions | Quickly Deploy a Local TiDB Cluster > Examples > Start a TiDB cluster of a specific version | Quickly Deploy a Local TiDB Cluster > Examples > Start a TiDB cluster of the nightly version | Quickly Deploy a Local TiDB Cluster > Examples > Override PD's default configuration | Quickly Deploy a Local TiDB Cluster > Examples > Replace the default binary files | Quickly Deploy a Local TiDB Cluster > Examples > Start multiple component instances | Quickly Deploy a Local TiDB Cluster > Examples > Specify a tag when starting the TiDB cluster to store the data`
- Source Line Ranges: `34-91`
- Source Scope: `developer`
- Primary Component: `tiup`
- Related Components: `pd`, `tidb`, `tikv`
- Topic Tags: `examples`, `version-check`, `nightly`, `pd-config`, `binpath`, `multi-instance`, `data-retention`, `tag`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0523_f6014d8cc2`
- Source ID: `tidb-docs-8.1:tiup/tiup-playground.md#examples`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `abdd1479f4d37ab016d6bc7032a78cfb9c6b14369e6c2d0e8b0e8958053c8aa2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-playground#examples
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-playground.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs example commands for checking TiDB versions, starting a specific or nightly version, overriding PD configuration, replacing binaries, changing instance counts, or retaining playground data with a tag.
- Retrieval Keywords: tiup list tidb, tiup playground ${version}, tiup playground nightly, nightly latest development version of TiDB, --pd.config ~/config/pd.toml, PD configuration template, --db.binpath /xx/tidb-server, --db 3 --pd 3 --kv 3, --tag ${tag_name}, ~/.tiup/data
- Follow-up Guidance: The source also notes that a cluster started with `--tag` retains its data files after the cluster is stopped and can be started next time with the same tag.
- Classification Note: This is classified as an operation chunk because it provides concrete TiUP Playground command examples for version selection, configuration override, binary replacement, topology sizing, and tagged data retention.

## Official Source Content

## Examples
### Check available TiDB versions

```shell
tiup list tidb
```
### Start a TiDB cluster of a specific version

```shell
tiup playground ${version}
```

Replace `${version}` with the target version number.
### Start a TiDB cluster of the nightly version

```shell
tiup playground nightly
```

In the command above, `nightly` indicates the latest development version of TiDB.
### Override PD's default configuration

First, you need to copy the [PD configuration template](https://github.com/pingcap/pd/blob/release-8.1/conf/config.toml). Assume you place the copied file to `~/config/pd.toml` and make some changes according to your need, then you can execute the following command to override PD's default configuration:

```shell
tiup playground --pd.config ~/config/pd.toml
```
### Replace the default binary files

By default, when playground is started, each component is started using the binary files from the official mirror. If you want to put a temporarily compiled local binary file into the cluster for testing, you can use the `--{comp}.binpath` flag for replacement. For example, execute the following command to replace the binary file of TiDB:

```shell
tiup playground --db.binpath /xx/tidb-server
```
### Start multiple component instances

By default, only one instance is started for each TiDB, TiKV, and PD component. To start multiple instances for each component, add the following flag:

```shell
tiup playground --db 3 --pd 3 --kv 3
```
### Specify a tag when starting the TiDB cluster to store the data

After you stop a TiDB cluster started using TiUP playground, all cluster data is cleaned up as well. To start a TiDB cluster using TiUP playground and ensure that the cluster data is not cleaned up automatically, you can specify a tag when starting the cluster. After specifying the tag, you can find the cluster data in the `~/.tiup/data` directory. Run the following command to specify a tag:

```shell
tiup playground --tag ${tag_name}
```

For a cluster started in this way, the data files are retained after the cluster is stopped. You can use this tag to start the cluster next time so that you can use the data kept since the cluster was stopped.
