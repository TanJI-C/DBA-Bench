# Java connection pool selection, HikariCP settings, and keepalive probes

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/java-app-best-practices.md`
- Source Title: `Best Practices for Developing Java Applications with TiDB`
- Source Heading Path: `Best Practices for Developing Java Applications with TiDB > Connection pool | Best Practices for Developing Java Applications with TiDB > Connection pool > Typical connection pool configuration | Best Practices for Developing Java Applications with TiDB > Connection pool > Probe configuration`
- Source Line Ranges: `228-287`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `connection-pool`, `hikaricp`, `pool-sizing`, `keepalive`, `idle-timeout`, `probes`, `load-balancing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0066_d34be2f619`
- Source ID: `tidb-docs-8.1:develop/java-app-best-practices.md#connection-pool`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a80872212ddedc7323b620b309f34a4994995d3850d1c0368c41c377c726fce5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/java-app-best-practices#connection-pool
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/java-app-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when you need guidance from the TiDB Java best practices on connection pool choice, HikariCP parameters, idle connection keepalive, or diagnosing CommunicationsException after long idle periods.
- Retrieval Keywords: HikariCP, tomcat-jdbc, druid, c3p0, dbcp, maximumPoolSize, minimumIdle, connectionTimeout, maxLifetime, keepaliveTime, poolName: hikariCP, About Pool Sizing, graceful-wait-before-shutdown, wait_timeout, Probe configuration, CommunicationsException: Communications link failure, The last packet sent successfully to the server was 3600000 milliseconds ago, JDBC4 isValid(), LVS, HAProxy
- Follow-up Guidance: The source distinguishes small `n milliseconds ago` values from large idle-time values and points to checking TiDB stderr logs or proxy idle configuration depending on that observation.
- Classification Note: This is classified as configuration because the content focuses on selecting and tuning Java connection pool settings and keepalive or probe behavior for TiDB connections.

## Official Source Content

## Connection pool

Building TiDB (MySQL) connections is relatively expensive (for OLTP scenarios at least), because in addition to building a TCP connection, connection authentication is also required. Therefore, the client usually saves the TiDB (MySQL) connections to the connection pool for reuse.

TiDB supports the following Java connection pools:

- [HikariCP](https://github.com/brettwooldridge/HikariCP)
- [tomcat-jdbc](https://tomcat.apache.org/tomcat-10.1-doc/jdbc-pool)
- [druid](https://github.com/alibaba/druid)
- [c3p0](https://www.mchange.com/projects/c3p0/)
- [dbcp](https://commons.apache.org/proper/commons-dbcp/)

In practice, some connection pools might persistently use specific active sessions. Although the total number of connections appears evenly distributed across TiDB compute nodes, uneven distribution of active connections can lead to actual load imbalance. In distributed scenarios, it is recommended to use HikariCP, which manages connection lifecycles effectively and helps prevent active connections from being fixed on certain nodes, achieving balanced load distribution.
### Typical connection pool configuration

The following is an example configuration for HikariCP:

```yaml
hikari:
  maximumPoolSize: 20
  poolName: hikariCP
  connectionTimeout: 30000 
  maxLifetime: 1200000
  keepaliveTime: 120000
```

The parameter explanations are as follows. For more details, refer to the [official HikariCP documentation](https://github.com/brettwooldridge/HikariCP/blob/dev/README.md).

- `maximumPoolSize`: the maximum number of connections in the pool. The default value is `10`. In containerized environments, it is recommended to set this to 4–10 times the number of CPU cores available to the Java application. Setting this value too high can lead to resource wastage, while setting it too low can slow down connection acquisition. See [About Pool Sizing](https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing) for more details.
- `minimumIdle`: HikariCP recommends not setting this parameter. The default value is equal to the value of `maximumPoolSize`, which disables connection pool scaling. This ensures that connections are readily available during traffic spikes and avoids delays caused by connection creation.
- `connectionTimeout`: the maximum time (in milliseconds) that an application waits to acquire a connection from the pool. The default value is `30000` milliseconds (30 seconds). If no available connection is obtained within this time, a `SQLException` exception occurs.
- `maxLifetime`: the maximum lifetime (in milliseconds) of a connection in the pool. The default value is `1800000` milliseconds (30 minutes). Connections in use are not affected. After the connection is closed, it will be removed according to this setting. Setting this value too low can cause frequent reconnections. If you are using [`graceful-wait-before-shutdown`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#graceful-wait-before-shutdown-new-in-v50), ensure this value is less than the wait time.
- `keepaliveTime`: the interval (in milliseconds) between keepalive operations on connections in the pool. This setting helps prevent disconnections caused by database or network idle timeouts. The default value is `120000` milliseconds (2 minutes). The pool prefers using the JDBC4 `isValid()` method to keep idle connections alive.
### Probe configuration

The connection pool maintains persistent connections from clients to TiDB as follows:

- Before v5.4, TiDB does not proactively close client connections by default (unless an error is reported).
- Starting from v5.4, TiDB automatically closes client connections after `28800` seconds (this is, `8` hours) of inactivity by default. You can control this timeout setting using the TiDB and MySQL compatible `wait_timeout` variable. For more information, see [JDBC Query Timeout](https://docs.pingcap.com/tidb/stable/develop/dev-guide-timeouts-in-tidb#jdbc-query-timeout).

Moreover, there might be network proxies such as [LVS](https://en.wikipedia.org/wiki/Linux_Virtual_Server) or [HAProxy](https://en.wikipedia.org/wiki/HAProxy) between clients and TiDB. These proxies typically proactively clean up connections after a specific idle period (determined by the proxy's idle configuration). In addition to monitoring the proxy's idle configuration, connection pools also need to maintain or probe connections for keep-alive.

If you often see the following error in your Java application:

```
The last packet sent successfully to the server was 3600000 milliseconds ago. The driver has not received any packets from the server. com.mysql.jdbc.exceptions.jdbc4.CommunicationsException: Communications link failure
```

If `n` in `n milliseconds ago` is `0` or a very small value, it is usually because the executed SQL operation causes TiDB to exit abnormally. To find the cause, it is recommended to check the TiDB stderr log.

If `n` is a very large value (such as `3600000` in the above example), it is likely that this connection was idle for a long time and then closed by the intermediate proxy. The usual solution is to increase the value of the proxy's idle configuration and allow the connection pool to:

- Check whether the connection is available before using the connection every time
- Regularly check whether the connection is available using a separate thread.
- Send a test query regularly to keep alive connections

Different connection pool implementations might support one or more of the above methods. You can check your connection pool documentation to find the corresponding configuration.
