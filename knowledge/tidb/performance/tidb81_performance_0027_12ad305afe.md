# Sysbench benchmark overview and test environment

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v6.2.0-vs-v6.1.0.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0 | TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0 > Test overview | TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0 > Test environment (AWS EC2） | TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0 > Test environment (AWS EC2） > Hardware configuration | TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0 > Test environment (AWS EC2） > Software version | TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0 > Test environment (AWS EC2） > Parameter configuration | TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0 > Test environment (AWS EC2） > Parameter configuration > TiDB parameter configuration | TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0 > Test environment (AWS EC2） > Parameter configuration > TiKV parameter configuration | TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0 > Test environment (AWS EC2） > Parameter configuration > TiDB global variable configuration | TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0 > Test environment (AWS EC2） > Parameter configuration > HAProxy configuration - haproxy.cfg`
- Source Line Ranges: `5-103`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiup`
- Topic Tags: `sysbench`, `benchmark`, `test-environment`, `hardware`, `software-version`, `parameter-configuration`, `haproxy`, `aws-ec2`, `oltp`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0027_12ad305afe`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v6.2.0-vs-v6.1.0.md#tidb-sysbench-performance-test-report-v6-2-0-vs-v6-1-0`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2629b79c2b88e0d79dd258c670972ed5dbeba370a43d3bb60f3e63096af9e27c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v6.2.0-vs-v6.1.0#tidb-sysbench-performance-test-report-v6-2-0-vs-v6-1-0
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v6.2.0-vs-v6.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks for the Sysbench benchmark overview, AWS EC2 test environment, or exact TiDB, TiKV, global variable, and HAProxy settings used to compare TiDB v6.2.0 and v6.1.0.
- Retrieval Keywords: TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0, AWS EC2 test environment, m5.xlarge, i3.4xlarge, c5.4xlarge, c5.9xlarge, Sysbench 1.1.0-df89d34, prepared-plan-cache.enabled, tikv-client.max-batch-wait-time, storage.scheduler-worker-pool-size, raftstore.store-pool-size, raftstore.apply-pool-size, rocksdb.max-background-jobs, server.grpc-concurrency, readpool.unified.max-thread-count, set global tidb_hashagg_final_concurrency=1, set global tidb_enable_async_commit = 1, set global tidb_enable_1pc = 1, set global tidb_guarantee_linearizability = 0, set global tidb_enable_clustered_index = 1, set global tidb_prepared_plan_cache_size=1000, HAProxy configuration - haproxy.cfg, listen tidb-cluster, balance leastconn, bind 0.0.0.0:3390
- Follow-up Guidance: The source also points to Best Practices for Using HAProxy in TiDB for more details about how to use HAProxy on TiDB.
- Classification Note: This chunk is classified as performance because it defines the benchmark goal, hardware and software environment, and parameter configuration used for the Sysbench comparison.

## Official Source Content

# TiDB Sysbench Performance Test Report -- v6.2.0 vs. v6.1.0
## Test overview

This test aims at comparing the Sysbench performance of TiDB v6.2.0 and TiDB v6.1.0 in the Online Transactional Processing (OLTP) scenario. The results show that performance of v6.2.0 is basically the same as that of v6.1.0. The performance of Point Select slightly drops by 3.58%.
## Test environment (AWS EC2）
### Hardware configuration

| Service type | EC2 type | Instance count |
|:----------|:----------|:----------|
| PD        | m5.xlarge |     3     |
| TiKV      | i3.4xlarge|     3     |
| TiDB      | c5.4xlarge|     3     |
| Sysbench  | c5.9xlarge|     1     |
### Software version

| Service type | Software version |
|:----------|:-----------|
| PD        | v6.1.0 and v6.2.0 |
| TiDB      | v6.1.0 and v6.2.0 |
| TiKV      | v6.1.0 and v6.2.0 |
| Sysbench  | 1.1.0-df89d34   |
### Parameter configuration

TiDB v6.2.0 and TiDB v6.1.0 use the same configuration.
#### TiDB parameter configuration

```yaml
log.level: "error"
prepared-plan-cache.enabled: true
tikv-client.max-batch-wait-time: 2000000
```
#### TiKV parameter configuration

```yaml
storage.scheduler-worker-pool-size: 5
raftstore.store-pool-size: 3
raftstore.apply-pool-size: 3
rocksdb.max-background-jobs: 8
server.grpc-concurrency: 6
readpool.unified.max-thread-count: 10
```
#### TiDB global variable configuration

```sql
set global tidb_hashagg_final_concurrency=1;
set global tidb_hashagg_partial_concurrency=1;
set global tidb_enable_async_commit = 1;
set global tidb_enable_1pc = 1;
set global tidb_guarantee_linearizability = 0;
set global tidb_enable_clustered_index = 1;
set global tidb_prepared_plan_cache_size=1000;
```
#### HAProxy configuration - haproxy.cfg

For more details about how to use HAProxy on TiDB, see [Best Practices for Using HAProxy in TiDB](https://docs.pingcap.com/tidb/stable/best-practices/haproxy-best-practices).

```yaml
global                                     # Global configuration.
   pidfile     /var/run/haproxy.pid        # Writes the PIDs of HAProxy processes into this file.
   maxconn     4000                        # The maximum number of concurrent connections for a single HAProxy process.
   user        haproxy                     # The same with the UID parameter.
   group       haproxy                     # The same with the GID parameter. A dedicated user group is recommended.
   nbproc      64                          # The number of processes created when going daemon. When starting multiple processes to forward requests, ensure that the value is large enough so that HAProxy does not block processes.
   daemon                                  # Makes the process fork into background. It is equivalent to the command line "-D" argument. It can be disabled by the command line "-db" argument.

defaults                                   # Default configuration.
   log global                              # Inherits the settings of the global configuration.
   retries 2                               # The maximum number of retries to connect to an upstream server. If the number of connection attempts exceeds the value, the backend server is considered unavailable.
   timeout connect  2s                     # The maximum time to wait for a connection attempt to a backend server to succeed. It should be set to a shorter time if the server is located on the same LAN as HAProxy.
   timeout client 30000s                   # The maximum inactivity time on the client side.
   timeout server 30000s                   # The maximum inactivity time on the server side.

listen tidb-cluster                        # Database load balancing.
   bind 0.0.0.0:3390                       # The Floating IP address and listening port.
   mode tcp                                # HAProxy uses layer 4, the transport layer.
   balance leastconn                      # The server with the fewest connections receives the connection. "leastconn" is recommended where long sessions are expected, such as LDAP, SQL and TSE, rather than protocols using short sessions, such as HTTP. The algorithm is dynamic, which means that server weights might be adjusted on the fly for slow starts for instance.
   server tidb-1 10.9.18.229:4000 check inter 2000 rise 2 fall 3       # Detects port 4000 at a frequency of once every 2000 milliseconds. If it is detected as successful twice, the server is considered available; if it is detected as failed three times, the server is considered unavailable.
   server tidb-2 10.9.39.208:4000 check inter 2000 rise 2 fall 3
   server tidb-3 10.9.64.166:4000 check inter 2000 rise 2 fall 3
```
