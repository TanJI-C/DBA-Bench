# Sysbench benchmark overview and test environment

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v6.0.0-vs-v5.4.0.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0 | TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0 > Test overview | TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0 > Test environment (AWS EC2） | TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0 > Test environment (AWS EC2） > Hardware configuration | TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0 > Test environment (AWS EC2） > Software version | TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0 > Test environment (AWS EC2） > Parameter configuration | TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0 > Test environment (AWS EC2） > Parameter configuration > TiDB parameter configuration | TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0 > Test environment (AWS EC2） > Parameter configuration > TiKV parameter configuration | TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0 > Test environment (AWS EC2） > Parameter configuration > TiDB global variable configuration | TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0 > Test environment (AWS EC2） > Parameter configuration > HAProxy configuration - haproxy.cfg`
- Source Line Ranges: `5-103`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `tiup`, `shared`
- Topic Tags: `sysbench`, `benchmark`, `test-environment`, `hardware`, `software-version`, `parameter-configuration`, `haproxy`, `aws-ec2`, `oltp`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0021_52642b7431`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v6.0.0-vs-v5.4.0.md#tidb-sysbench-performance-test-report-v6-0-0-vs-v5-4-0`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `30509f49d1c21261a83a935fa73eae545732828ffdf9fc7954936fe0aa28adec`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v6.0.0-vs-v5.4.0#tidb-sysbench-performance-test-report-v6-0-0-vs-v5-4-0
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v6.0.0-vs-v5.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching for the Sysbench benchmark environment, cluster sizing, software versions, and exact TiDB, TiKV, global variable, or HAProxy settings used in the TiDB v6.0.0 vs. v5.4.0 OLTP comparison.
- Retrieval Keywords: TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0, AWS EC2 test environment, Hardware configuration, Software version, PD m5.xlarge 3, TiKV i3.4xlarge 3, TiDB c5.4xlarge 3, Sysbench c5.9xlarge 1, Sysbench 1.1.0-df89d34, prepared-plan-cache.enabled, tikv-client.max-batch-wait-time, storage.scheduler-worker-pool-size, pessimistic-txn.pipelined, server.grpc-concurrency, set global tidb_enable_async_commit = 1, set global tidb_enable_1pc = 1, set global tidb_guarantee_linearizability = 0, set global tidb_enable_clustered_index = 1, HAProxy configuration - haproxy.cfg, listen tidb-cluster, balance leastconn, bind 0.0.0.0:3390
- Follow-up Guidance: The source also points to Best Practices for Using HAProxy in TiDB for more details about how to use HAProxy on TiDB.
- Classification Note: This is classified as performance content because it defines the benchmark overview and the exact environment and parameter configuration used for the performance comparison.

## Official Source Content

# TiDB Sysbench Performance Test Report -- v6.0.0 vs. v5.4.0
## Test overview

This test aims at comparing the Sysbench performance of TiDB v6.0.0 and TiDB v5.4.0 in the Online Transactional Processing (OLTP) scenario. The results show that performance of v6.0.0 is significantly improved by 16.17% in the read-write workload. The performance of other workload is basically the same as in v5.4.0.
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
| PD        | v5.4.0 and v6.0.0 |
| TiDB      | v5.4.0 and v6.0.0 |
| TiKV      | v5.4.0 and v6.0.0 |
| Sysbench  | 1.1.0-df89d34   |
### Parameter configuration

TiDB v6.0.0 and TiDB v5.4.0 use the same configuration.
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
raftdb.max-background-jobs: 4
raftdb.allow-concurrent-memtable-write: true
server.grpc-concurrency: 6
readpool.storage.normal-concurrency: 10
pessimistic-txn.pipelined: true
```
#### TiDB global variable configuration

```sql
set global tidb_hashagg_final_concurrency=1;
set global tidb_hashagg_partial_concurrency=1;
set global tidb_enable_async_commit = 1;
set global tidb_enable_1pc = 1;
set global tidb_guarantee_linearizability = 0;
set global tidb_enable_clustered_index = 1;
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
