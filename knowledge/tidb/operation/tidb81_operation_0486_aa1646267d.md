# TiProxy installation, configuration changes, upgrade, and cluster restart guidance

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiproxy/tiproxy-overview.md`
- Source Title: `TiProxy Overview`
- Source Heading Path: `TiProxy Overview > Installation and usage | TiProxy Overview > Installation and usage > Deploy TiProxy | TiProxy Overview > Installation and usage > Modify TiProxy configuration | TiProxy Overview > Installation and usage > Upgrade TiProxy | TiProxy Overview > Installation and usage > Restart the TiDB cluster`
- Source Line Ranges: `56-140`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tiup`
- Topic Tags: `deployment`, `configuration`, `tls`, `certificates`, `session-token`, `graceful-shutdown`, `high-availability`, `online-change`, `upgrade`, `restart`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0486_aa1646267d`
- Source ID: `tidb-docs-8.1:tiproxy/tiproxy-overview.md#installation-and-usage`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `337c72ff0b9d7d958722bfa17fd9a49d7b5ee2340ad3e56c30d007132de5b834`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-overview#installation-and-usage
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiproxy/tiproxy-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to deploy, configure, modify, upgrade, or restart TiProxy with TiUP while preserving client connections.
- Retrieval Keywords: Installation and usage, Deploy TiProxy, Modify TiProxy configuration, Upgrade TiProxy, Restart the TiDB cluster, TiUP, security.session-token-signing-cert, security.session-token-signing-key, graceful-wait-before-shutdown, security.server-tls.ca, security.server-tls.cert, security.server-tls.key, --skip-restart, --tiproxy-version, tiup cluster upgrade, tiup cluster reload, tiup cluster restart, self-signed certificate, session-token, rolling restarted, client should connect to the port of TiProxy
- Follow-up Guidance: The source includes exact command and configuration references such as tiup cluster upgrade <cluster-name> <version> --tiproxy-version <tiproxy-version> and the note that tiup cluster reload or tiup cluster upgrade uses rolling restart for TiDB servers.
- Classification Note: This is classified as operation because the content gives deployment prerequisites, configuration items, upgrade flags, online change behavior, and restart guidance for self-managed use with TiUP.

## Official Source Content

## Installation and usage

This section describes how to deploy and change TiProxy using TiUP. For how to deploy TiProxy using TiDB Operator in Kubernetes, see [TiDB Operator documentation](https://docs.pingcap.com/tidb-in-kubernetes/stable/deploy-tiproxy).
### Deploy TiProxy

1. Before TiUP v1.15.0, you need to manually generate a self-signed certificate.

    Generate a self-signed certificate for the TiDB instance and place the certificate on all TiDB instances to ensure that all TiDB instances have the same certificate. For detailed steps, see [Generate self-signed certificates](https://docs.pingcap.com/tidb/stable/generate-self-signed-certificates).

2. Configure the TiDB instances.

    When using TiProxy, you also need to configure the following items for the TiDB instances:

    - Before TiUP v1.15.0, configure the [`security.session-token-signing-cert`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#session-token-signing-cert-new-in-v640) and [`security.session-token-signing-key`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#session-token-signing-key-new-in-v640) of TiDB instances to the path of the certificate. Otherwise, the connection cannot be migrated.
    - Configure the [`graceful-wait-before-shutdown`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#graceful-wait-before-shutdown-new-in-v50) of TiDB instances to a value greater than the longest transaction duration of the application. Otherwise, the client might disconnect when the TiDB server is offline. You can view the transaction duration through the [Transaction metrics on the TiDB monitoring dashboard](https://docs.pingcap.com/tidb/stable/grafana-tidb-dashboard#transaction). For details, see [TiProxy usage limitations](#limitations).

    A configuration example is as follows:

    ```yaml
    server_configs:
      tidb:
        security.session-token-signing-cert: "/var/sess/cert.pem"
        security.session-token-signing-key: "/var/sess/key.pem"
        security.ssl-ca: "/var/ssl/ca.pem"
        security.ssl-cert: "/var/ssl/cert.pem"
        security.ssl-key: "/var/ssl/key.pem"
        graceful-wait-before-shutdown: 15
    ```

3. Configure the TiProxy instances.

    To ensure the high availability of TiProxy, it is recommended to deploy at least two TiProxy instances. You can use hardware load balancers to distribute traffic to each TiProxy instance, or configure virtual IP to route the traffic to the available TiProxy instance.

    When selecting the model and number of TiProxy instances, consider the following factors:

    - For the workload type and maximum QPS, see [TiProxy Performance Test Report](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-performance-test).
    - Because the number of TiProxy instances is less than that of TiDB servers, the network bandwidth of TiProxy is more likely to become a bottleneck than that of TiDB servers. Therefore, you also need to consider the network bandwidth. For example, in AWS, the baseline network bandwidth of the same series of EC2 is not proportional to the number of CPU cores. For details, see [Network performance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/compute-optimized-instances.html#compute-network-performance). In such cases, when the network bandwidth becomes a bottleneck, splitting the TiProxy instance into more and smaller instances can improve QPS.

    It is recommended to specify the version number of TiProxy in the topology configuration so that TiProxy will not be upgraded when you upgrade the TiDB cluster through [`tiup cluster upgrade`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-upgrade). Otherwise, the client connection might be disconnected during TiProxy upgrade.

    To configure TiProxy configuration items, see [TiProxy configuration](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-configuration).

    A configuration example is as follows:

    ```yaml
    component_versions:
      tiproxy: "v1.0.0"
    server_configs:
      tiproxy:
        security.server-tls.ca: "/var/ssl/ca.pem"
        security.server-tls.cert: "/var/ssl/cert.pem"
        security.server-tls.key: "/var/ssl/key.pem"
    ```

4. Start the cluster.

    To start the cluster using TiUP, see [TiUP documentation](https://docs.pingcap.com/tidb/stable/tiup/tiup-documentation-guide).

5. Connect to TiProxy.

    After the cluster is deployed, the cluster exposes the ports of TiDB server and TiProxy at the same time. The client should connect to the port of TiProxy instead of the port of TiDB server.
### Modify TiProxy configuration

To ensure that TiProxy keeps the client connection, do not restart TiProxy unless necessary. Therefore, most of the TiProxy configuration items can be modified online. For the list of configuration items that support online change, see [TiProxy configuration](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-configuration).

When using TiUP to change the TiProxy configuration, if the configuration item to be changed supports online change, you can use the [`--skip-restart`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-reload#--skip-restart) option to avoid restarting TiProxy.
### Upgrade TiProxy

When you deploy TiProxy, it is recommended to specify the version of TiProxy so that TiProxy will not be upgraded when you upgrade the TiDB cluster.

If you need to upgrade TiProxy, add [`--tiproxy-version`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-upgrade#--tiproxy-version) in the upgrade command to specify the version of TiProxy:

```shell
tiup cluster upgrade <cluster-name> <version> --tiproxy-version <tiproxy-version>
```
### Restart the TiDB cluster

When you restart the TiDB cluster using [`tiup cluster restart`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-restart), TiDB servers are not rolling restarted, which causes the client connection to be disconnected. Therefore, avoid using this command.

Instead, when you upgrade the cluster using [`tiup cluster upgrade`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-upgrade) or reload the configuration using [`tiup cluster reload`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-reload), TiDB servers are rolling restarted, so the client connection is not affected.
