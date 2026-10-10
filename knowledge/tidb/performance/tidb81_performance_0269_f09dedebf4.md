# TiProxy performance report overview and test environment

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiproxy/tiproxy-performance-test.md`
- Source Title: `TiProxy Performance Test Report`
- Source Heading Path: `TiProxy Performance Test Report | TiProxy Performance Test Report > Test environment | TiProxy Performance Test Report > Test environment > Hardware configuration | TiProxy Performance Test Report > Test environment > Software | TiProxy Performance Test Report > Test environment > Configuration | TiProxy Performance Test Report > Test environment > Configuration > TiProxy configuration | TiProxy Performance Test Report > Test environment > Configuration > HAProxy configuration - `haproxy.cfg` file`
- Source Line Ranges: `5-80`
- Source Scope: `self_managed`
- Primary Component: `tiproxy`
- Related Components: `tidb`, `pd`
- Topic Tags: `performance-testing`, `test-environment`, `hardware`, `software-versions`, `proxy-configuration`, `haproxy-comparison`, `cpu-usage`, `sysbench`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0269_f09dedebf4`
- Source ID: `tidb-docs-8.1:tiproxy/tiproxy-performance-test.md#tiproxy-performance-test-report`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `737c8357a0ffe243fe58f61001e8f9f935e185404d45edc24dcd2e7f8155a263`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-performance-test#tiproxy-performance-test-report
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiproxy/tiproxy-performance-test.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiProxy performance report summary, the Sysbench OLTP test environment, or the exact TiProxy and HAProxy configurations used for comparison.
- Retrieval Keywords: TiProxy Performance Test Report, Sysbench OLTP scenario, QPS upper limit less than 5% lower than HAProxy, TiProxy CPU usage about 25% higher than HAProxy, 5 to 12 TiDB server instances, performance increases almost linearly with the number of vCPUs, proxy.conn-buffer-size: 131072, TLS is not enabled, HAProxy 2.9.0, haproxy.cfg, balance leastconn, bind 0.0.0.0:3390, nbthread 4, maxconn 4096, Intel(R) Xeon(R) Silver 4214R CPU @ 2.40GHz, TiProxy v1.0.0, TiDB v8.0.0, PD v8.0.0, Sysbench 1.0.17
- Follow-up Guidance: The same report also contains basic workload test results and a result set test plan for comparing QPS, latency, and CPU usage between TiProxy and HAProxy.
- Classification Note: This chunk is classified as performance because it summarizes TiProxy benchmark findings and documents the hardware, software, and proxy configuration used in the tests.

## Official Source Content

# TiProxy Performance Test Report

This report tests the performance of TiProxy in the OLTP scenario of Sysbench and compares it with [HAProxy](https://www.haproxy.org/).

The results are as follows:

- The QPS upper limit of TiProxy is affected by the type of workload. When client concurrency is the same and the TiProxy CPU usage is below 80%, the QPS is less than 5% lower than that of HAProxy. In such cases, you can often increase the client concurrency to improve QPS. Under the same QPS, TiProxy's CPU usage is about 25% higher than HAProxy's. Therefore, you need to reserve more CPU resources.
- The number of TiDB server instances that TiProxy can hold varies according to the type of workload. Under the basic workloads of Sysbench, a TiProxy can hold 5 to 12 TiDB server instances of the same model.
- The row number of the query result set has a significant impact on the QPS of TiProxy, and the impact is the same as that of HAProxy.
- The performance of TiProxy increases almost linearly with the number of vCPUs. Therefore, increasing the number of vCPUs can effectively improve the QPS upper limit.
- The number of long connections and the frequency of creating short connections have minimal impact on the QPS of TiProxy.
## Test environment
### Hardware configuration

| Service | Machine type | CPU model | Instance count |
| --- | --- | --- | --- |
| TiProxy | 4C8G | Intel(R) Xeon(R) Silver 4214R CPU @ 2.40GHz | 1 |
| HAProxy | 4C8G | Intel(R) Xeon(R) Silver 4214R CPU @ 2.40GHz | 1 |
| PD | 4C8G | Intel(R) Xeon(R) Silver 4214R CPU @ 2.40GHz | 3 |
| TiDB | 8C16G | Intel(R) Xeon(R) Silver 4214R CPU @ 2.40GHz | 8 |
| TiKV | 8C16G | Intel(R) Xeon(R) Silver 4214R CPU @ 2.40GHz | 8 |
| Sysbench | 8C16G | Intel(R) Xeon(R) Silver 4214R CPU @ 2.40GHz | 1 |
### Software

| Service | Software version |
| --- | --- |
| TiProxy | v1.0.0 |
| HAProxy | 2.9.0 |
| PD | v8.0.0 |
| TiDB | v8.0.0 |
| TiKV | v8.0.0 |
| Sysbench | 1.0.17 |
### Configuration
#### TiProxy configuration

In the test, TLS is not enabled between the client and TiProxy, or between TiProxy and TiDB server.

```yaml
proxy.conn-buffer-size: 131072
```
#### HAProxy configuration - `haproxy.cfg` file

```yaml
global                                      # Global configuration.
    log         127.0.0.1 local2            # Specifies the global syslog server. You can define up to two.
    pidfile     /var/run/haproxy.pid        # Write the PID of the HAProxy process to pidfile.
    maxconn     4096                        # The maximum number of concurrent connections that a single HAProxy process can accept, equivalent to the command line parameter "-n".
    nbthread    4                           # The maximum number of threads. The upper limit of the number of threads is the same as the number of CPUs.
    user        haproxy                     # Same as UID parameter.
    group       haproxy                     # Same as GID parameter. A dedicated user group is recommended.
    daemon                                  # Run HAProxy as a daemon in the background, which is equivalent to the command line parameter "-D". You can also disable it with the "-db" parameter on the command line.
    stats socket /var/lib/haproxy/stats     # The location where the statistics are saved.

defaults                                    # Default configuration.
    log global                              # Inherit the settings of the global configuration section.
    retries 2                               # The maximum number of times to try to connect to the upstream server. If the number of retries exceeds this value, the backend server is considered unavailable.
    timeout connect  2s                     # The timeout period for HAProxy to connect to the backend server. If the server is located on the same LAN as HAProxy, set it to a shorter time.
    timeout client 30000s                   # The timeout period for the client to be inactive after the data transmission is completed.
    timeout server 30000s                   # The timeout period for the server to be inactive.

listen tidb-cluster                         # Configure database load balancing.
    bind 0.0.0.0:3390                       # Floating IP address and listening port.
    mode tcp                                # HAProxy uses layer 4, the transport layer.
    balance leastconn                      # The server with the least number of connections receives the connection first. `leastconn` is recommended for long session services, such as LDAP, SQL, and TSE, rather than short session protocols, such as HTTP. This algorithm is dynamic, and the server weight is adjusted during operation for slow-start servers.
    server tidb-1 10.9.18.229:4000 check inter 2000 rise 2 fall 3      # Detects port 4000 at a frequency of once every 2000 milliseconds. If it is detected as successful twice, the server is considered available; if it is detected as failed three times, the server is considered unavailable.
    server tidb-2 10.9.39.208:4000 check inter 2000 rise 2 fall 3
    server tidb-3 10.9.64.166:4000 check inter 2000 rise 2 fall 3
```
