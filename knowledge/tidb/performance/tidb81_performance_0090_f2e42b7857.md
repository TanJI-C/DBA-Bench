# Connection pool sizing, probes, and tuning

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-connection-parameters.md`
- Source Title: `Connection Pools and Connection Parameters`
- Source Heading Path: `Connection Pools and Connection Parameters | Connection Pools and Connection Parameters > Connection pool | Connection Pools and Connection Parameters > Connection pool > Configure the number of connections | Connection Pools and Connection Parameters > Connection pool > Probe configuration | Connection Pools and Connection Parameters > Connection pool > Formulas based on experience | Connection Pools and Connection Parameters > Connection pool > Tuning direction`
- Source Line Ranges: `5-112`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `ecosystem`, `shared`
- Topic Tags: `connection-pool`, `pool-sizing`, `idle-timeout`, `keepalive`, `jdbc`, `throughput-tuning`, `preparedness`, `proxy-idle`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0090_f2e42b7857`
- Source ID: `tidb-docs-8.1:develop/dev-guide-connection-parameters.md#connection-pools-and-connection-parameters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `36a8ab53a4460010f3d226d761b276a58da8d538e616c112903963c75bccd8ae`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-connection-parameters#connection-pools-and-connection-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-connection-parameters.md

## Retrieval Guidance

- Use When: Use this chunk when you need guidance on Java connection pool sizing, idle timeout behavior, keep-alive probes, or tuning around maximumPoolSize and minimumIdle for TiDB connections.
- Retrieval Keywords: maximumPoolSize, minimumIdle, metricRegistry, wait_timeout, 28800 seconds, 8 hours, CommunicationsException: Communications link failure, The last packet sent successfully to the server was 3600000 milliseconds ago, LVS, HAProxy, connection pool keep-alive, check whether the connection is available, test query regularly, connections = ((core_count * 2) + effective_spindle_count), connections = (number of cores * 4), effective_spindle_count, Hyper-Threading, pool sizing, tuning direction
- Follow-up Guidance: The content also points to JDBC Query Timeout and Java application best practices pages for related connection handling details.
- Classification Note: This is classified as performance content because the official text focuses on connection pool sizing formulas, throughput-oriented tuning direction, idle connection handling, and monitoring of pool behavior.

## Official Source Content

# Connection Pools and Connection Parameters

This document describes how to configure connection pools and connection parameters when you use a driver or ORM framework to connect to TiDB.

If you are interested in more tips about Java application development, see [Best Practices for Developing Java Applications with TiDB](https://docs.pingcap.com/tidb/stable/develop/java-app-best-practices#connection-pool)

If you are interested in more tips about Java application development, see [Best Practices for Developing Java Applications with TiDB](https://docs.pingcap.com/tidb/stable/java-app-best-practices)
## Connection pool

Building TiDB (MySQL) connections is relatively expensive (for OLTP scenarios at least). Because in addition to building a TCP connection, connection authentication is also required. Therefore, the client usually saves the TiDB (MySQL) connections to the connection pool for reuse.

Java has many connection pool implementations such as [HikariCP](https://github.com/brettwooldridge/HikariCP), [tomcat-jdbc](https://tomcat.apache.org/tomcat-10.1-doc/jdbc-pool.html), [druid](https://github.com/alibaba/druid), [c3p0](https://www.mchange.com/projects/c3p0/), and [dbcp](https://commons.apache.org/proper/commons-dbcp/). TiDB does not limit which connection pool you use, so you can choose whichever you like for your application.
### Configure the number of connections

It is a common practice that the connection pool size is well adjusted according to the application's own needs. Take HikariCP as an example:

- **maximumPoolSize**: The maximum number of connections in the connection pool. If this value is too large, TiDB consumes resources to maintain useless connections. If this value is too small, the application gets slow connections. Therefore, you need to configure this value according to your application characteristics. For details, see [About Pool Sizing](https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing).
- **minimumIdle**: The minimum number of idle connections in the connection pool. It is mainly used to reserve some connections to respond to sudden requests when the application is idle. You also need to configure it according to your application characteristics.

The application needs to return the connection after finishing using it. It is recommended that the application uses the corresponding connection pool monitoring (such as **metricRegistry**) to locate connection pool issues in time.
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

If `n` is a very large value (such as `3600000` in the above example), it is likely that this connection was idle for a long time and then closed by the proxy. The usual solution is to increase the value of the proxy's idle configuration and allow the connection pool to:

- Check whether the connection is available before using the connection every time.
- Regularly check whether the connection is available using a separate thread.
- Send a test query regularly to keep alive connections.

Different connection pool implementations might support one or more of the above methods. You can check your connection pool documentation to find the corresponding configuration.
### Formulas based on experience

According to the [About Pool Sizing](https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing) article of HikariCP, if you have no idea about how to set a proper size for the database connection pool, you can get started with a [formula based on experience](https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing#connections--core_count--2--effective_spindle_count). Then, based on the performance result of the pool size calculated from the formula, you can further adjust the size to achieve the best performance.

The formula based on experience is as follows:

```
connections = ((core_count * 2) + effective_spindle_count)
```

The description of each parameter in the formula is as follows:

- **connections**: the size of connections obtained.
- **core_count**: the number of CPU cores.
- **effective_spindle_count**: the number of hard drives (not [SSD](https://en.wikipedia.org/wiki/Solid-state_drive)). Because each spinning hard disk can be called a spindle. For example, if you are using a server with a RAID of 16 disks, the **effective_spindle_count** should be 16. Because **HDD** usually can handle only one request at a time, the formula here is actually measuring how many concurrent I/O requests your server can manage.

In particular, pay attention to the following note below the [formula](https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing#the-formula).

> ```
> A formula which has held up pretty well across a lot of benchmarks for years is
> that for optimal throughput the number of active connections should be somewhere
> near ((core_count * 2) + effective_spindle_count). Core count should not include
> HT threads, even if hyperthreading is enabled. Effective spindle count is zero if
> the active data set is fully cached, and approaches the actual number of spindles
> as the cache hit rate falls. ... There hasn't been any analysis so far regarding
> how well the formula works with SSDs.
> ```

This note indicates that:

- **core_count** is the number of physical cores, regardless of whether you enable [Hyper-Threading](https://en.wikipedia.org/wiki/Hyper-threading) or not.
- When data is fully cached, you need to set **effective_spindle_count** to `0`. As the hit rate of cache decreases, the count is closer to the actual number of `HDD`.
- **Whether the formula works for _SSD_ is not tested and unknown.**

When using SSDs, it is recommended that you use the following formula based on experience instead:

```
connections = (number of cores * 4)
```

Therefore, you can set the maximum connection size of the initial connection pool to `cores * 4` in the case of SSDs and further adjust the size to tune the performance.
### Tuning direction

As you can see, a size calculated from the [formulas based on experience](#formulas-based-on-experience) is just a recommended base value. To get the optimal size on a specific machine, you need to try other values around the base value and test the performance.

Here are some basic rules to help you get the optimal size:

- If your network or storage latency is high, increase your maximum number of connections to reduce the latency waiting time. Once a thread is blocked by latency, other threads can take over and continue processing.
- If you have multiple services deployed on your server and each service has a separate connection pool, consider the sum of the maximum number of connections to all connection pools.
