# TiProxy overview, features, and user scenarios

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiproxy/tiproxy-overview.md`
- Source Title: `TiProxy Overview`
- Source Heading Path: `TiProxy Overview | TiProxy Overview > Main features | TiProxy Overview > Main features > Connection migration | TiProxy Overview > Main features > Service discovery | TiProxy Overview > Main features > Quick deployment | TiProxy Overview > User scenarios`
- Source Line Ranges: `5-55`
- Source Scope: `shared`
- Primary Component: `shared`
- Related Components: `tidb`, `tiup`, `operator`, `dashboard`
- Topic Tags: `proxy`, `load-balancing`, `connection-migration`, `service-discovery`, `deployment`, `user-scenarios`, `performance-sensitivity`, `cost-sensitivity`, `failover-limitations`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0115_8b41db6db0`
- Source ID: `tidb-docs-8.1:tiproxy/tiproxy-overview.md#tiproxy-overview`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c4706004d8e9d4f9ad92a676be5a34480265907b498bc796036c4946856ee857`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-overview#tiproxy-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiproxy/tiproxy-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks what TiProxy is, what features it provides, or whether it fits scenarios involving connection persistence, service discovery, scaling, rolling upgrade, or rolling restart.
- Retrieval Keywords: TiProxy Overview, official proxy component of PingCAP, load balancing, connection persistence, service discovery, connection migration, quick deployment, scaling in, scaling out, rolling upgrade, rolling restart, client connection alive, TiUP, TiDB Operator, TiDB Dashboard, Grafana, sensitive to performance, sensitive to cost, TiDB server failover, HAProxy
- Follow-up Guidance: The source also points to installation and usage guidance, including deployment and configuration details for TiProxy.
- Classification Note: This is classified as architecture because the content defines TiProxy's role between the client and TiDB server, its main features, and the scenarios where it is suitable or not suitable.

## Official Source Content

# TiProxy Overview

TiProxy is the official proxy component of PingCAP. It is placed between the client and the TiDB server to provide load balancing, connection persistence, service discovery, and other features for TiDB.

TiProxy is an optional component. You can also use a third-party proxy component or connect directly to the TiDB server without using a proxy.

The following figure shows the architecture of TiProxy:

<img src="https://docs-download.pingcap.com/media/images/docs/tiproxy/tiproxy-architecture.png" alt="TiProxy architecture" width="500" />
## Main features

TiProxy provides connection migration, service discovery, and quick deployment.
### Connection migration

TiProxy can migrate connections from one TiDB server to another without breaking the client connection.

As shown in the following figure, the client originally connects to TiDB 1 through TiProxy. After the connection migration, the client actually connects to TiDB 2. When TiDB 1 is about to be offline or the ratio of connections on TiDB 1 to connections on TiDB 2 exceeds the set threshold, the connection migration is triggered. The client is unaware of the connection migration.

<img src="https://docs-download.pingcap.com/media/images/docs/tiproxy/tiproxy-session-migration.png" alt="TiProxy connection migration" width="400" />

Connection migration usually occurs in the following scenarios:

- When a TiDB server performs scaling in, rolling upgrade, or rolling restart, TiProxy can migrate connections from the TiDB server that is about to be offline to other TiDB servers to keep the client connection alive.
- When a TiDB server performs scaling out, TiProxy can migrate existing connections to the new TiDB server to achieve real-time load balancing without resetting the client connection pool.
### Service discovery

When a TiDB server performs scaling in or scaling out, if you use a common load balancer, you need to manually update the TiDB server list. However, TiProxy can automatically discover the TiDB server list without manual intervention.
### Quick deployment

TiProxy is integrated into [TiUP](https://github.com/pingcap/tiup), [TiDB Operator](https://github.com/pingcap/tidb-operator), [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro), and [Grafana](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-grafana), which reduces the deployment, operation, and management costs.
## User scenarios

TiProxy is suitable for the following scenarios:

- Connection persistence: When a TiDB server performs scaling in, rolling upgrade, or rolling restart, the client connection is broken, resulting in an error. If the client does not have an idempotent error retry mechanism, you need to manually check and fix the error, which greatly increases the labor cost. TiProxy can keep the client connection, so that the client does not report an error.
- Frequent scaling in and scaling out: The workload of an application might change periodically. To save costs, you can deploy TiDB on the cloud and automatically scale in and scale out TiDB servers according to the workload. However, scaling in might cause the client to disconnect, and scaling out might result in unbalanced load. TiProxy can keep the client connection and achieve load balancing.

TiProxy is not suitable for the following scenarios:

- Sensitive to performance: The performance of TiProxy is lower than that of HAProxy and other load balancers, so using TiProxy requires reserving more CPU resources to maintain similar performance levels. For details, refer to [TiProxy Performance Test Report](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-performance-test).
- Sensitive to cost: If the TiDB cluster uses hardware load balancers, virtual IP, or the load balancer provided by Kubernetes, adding TiProxy will increase the cost. In addition, if you deploy the TiDB cluster across availability zones on the cloud, adding TiProxy will also increase the traffic cost across availability zones.
- TiDB server failover: TiProxy can keep the client connection only when the TiDB server is offline or restarted as planned. If the TiDB server is offline unexpectedly, the connection is still broken.

It is recommended that you use TiProxy for the scenarios that TiProxy is suitable for and use HAProxy or other proxies when your application is sensitive to performance.
