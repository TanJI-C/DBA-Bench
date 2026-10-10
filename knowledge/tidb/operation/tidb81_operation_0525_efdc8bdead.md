# Deploy TiProxy with TiUP Playground

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-playground.md`
- Source Title: `Quickly Deploy a Local TiDB Cluster`
- Source Heading Path: `Quickly Deploy a Local TiDB Cluster > Deploy TiProxy`
- Source Line Ranges: `137-170`
- Source Scope: `developer`
- Primary Component: `tiproxy`
- Related Components: `tiup`, `tidb`
- Topic Tags: `tiproxy`, `deployment`, `flags`, `graceful-shutdown`, `proxy`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0525_efdc8bdead`
- Source ID: `tidb-docs-8.1:tiup/tiup-playground.md#deploy-tiproxy`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `25ba4f9cde24ab3bea118f553fdd5315f89cdfe5d1a2030117a4a31853215b0d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-playground#deploy-tiproxy
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-playground.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to deploy TiProxy with TiUP Playground, what TiProxy flags are available, or how `graceful-wait-before-shutdown=15` is used with TiDB during scaling-in.
- Retrieval Keywords: Deploy TiProxy, TiProxy, Starting from TiUP v1.15.0, graceful-wait-before-shutdown=15, tidb.toml, tiup playground v8.1.2 --tiproxy 1 --db.config tidb.toml, --tiproxy, --tiproxy.binpath, --tiproxy.config, --tiproxy.host, --tiproxy.port, --tiproxy.timeout, --tiproxy.version
- Follow-up Guidance: The source also links to TiProxy installation and usage for more information about deploying and using TiProxy.
- Classification Note: This is classified as an operation chunk because it explains the Playground-based deployment flow for TiProxy, the required example configuration, and the related command-line flags.

## Official Source Content

## Deploy TiProxy

[TiProxy](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-overview) is the official proxy component from PingCAP, placed between the client and the TiDB server to provide load balancing, connection persistence, service discovery, and other features for TiDB.

Starting from TiUP v1.15.0, you can deploy TiProxy for your cluster using TiUP Playground.

1. Create a `tidb.toml` file and add the following configuration:

    ```
    graceful-wait-before-shutdown=15
    ```

    This configuration item controls the duration (in seconds) that TiDB waits before shutting down the server, avoiding client disconnections during cluster scaling-in operations.

2. Start the TiDB cluster:

    ```shell
    tiup playground v8.1.2 --tiproxy 1 --db.config tidb.toml
    ```

    In the playground component, TiProxy-related command-line flags are as follows:

    ```bash
    Flags:
          --tiproxy int                  The number of TiProxy nodes in the cluster. If not specified, TiProxy is not deployed.
          --tiproxy.binpath string       TiProxy instance binary path.
          --tiproxy.config string        TiProxy instance configuration file.
          --tiproxy.host host            Playground TiProxy host. If not provided, TiProxy will still use host flag as its host.
          --tiproxy.port int             Playground TiProxy port. If not provided, TiProxy will use 6000 as its port.
          --tiproxy.timeout int          TiProxy maximum wait time in seconds for starting. 0 means no limit (default 60).
          --tiproxy.version string       The version of TiProxy. If not specified, the latest version of TiProxy is deployed.
    ```

For more information about deploying and using TiProxy, see [TiProxy installation and usage](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-overview#installation-and-usage).
