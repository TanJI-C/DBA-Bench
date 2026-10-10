# Benchmark overview and test environment configuration

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-sysbench-v5.4.0-vs-v5.3.0.md`
- Source Title: `TiDB Sysbench Performance Test Report -- v5.4.0 vs. v5.3.0`
- Source Heading Path: `TiDB Sysbench Performance Test Report -- v5.4.0 vs. v5.3.0 | TiDB Sysbench Performance Test Report -- v5.4.0 vs. v5.3.0 > Test overview | TiDB Sysbench Performance Test Report -- v5.4.0 vs. v5.3.0 > Test environment (AWS EC2） | TiDB Sysbench Performance Test Report -- v5.4.0 vs. v5.3.0 > Test environment (AWS EC2） > Hardware configuration | TiDB Sysbench Performance Test Report -- v5.4.0 vs. v5.3.0 > Test environment (AWS EC2） > Software version | TiDB Sysbench Performance Test Report -- v5.4.0 vs. v5.3.0 > Test environment (AWS EC2） > Parameter configuration | TiDB Sysbench Performance Test Report -- v5.4.0 vs. v5.3.0 > Test environment (AWS EC2） > Parameter configuration > TiDB parameter configuration | TiDB Sysbench Performance Test Report -- v5.4.0 vs. v5.3.0 > Test environment (AWS EC2） > Parameter configuration > TiKV parameter configuration | TiDB Sysbench Performance Test Report -- v5.4.0 vs. v5.3.0 > Test environment (AWS EC2） > Parameter configuration > TiDB global variable configuration | TiDB Sysbench Performance Test Report -- v5.4.0 vs. v5.3.0 > Test environment (AWS EC2） > Parameter configuration > HAProxy configuration - haproxy.cfg`
- Source Line Ranges: `5-107`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `tiup`
- Topic Tags: `sysbench`, `benchmarking`, `oltp`, `aws-ec2`, `hardware-configuration`, `software-version`, `parameter-configuration`, `global-variables`, `haproxy`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0018_f57bf1b963`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-sysbench-v5.4.0-vs-v5.3.0.md#tidb-sysbench-performance-test-report-v5-4-0-vs-v5-3-0`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `50494819aaaa21fb6287b31b2dbc5fd5b9d16e48038f4afb6f74b42fa61f3538`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-sysbench-v5.4.0-vs-v5.3.0#tidb-sysbench-performance-test-report-v5-4-0-vs-v5-3-0
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-sysbench-v5.4.0-vs-v5.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the benchmark overview or exact AWS EC2, software version, TiDB, TiKV, global variable, or HAProxy settings used for the TiDB v5.4.0 vs. v5.3.0 Sysbench OLTP test.
- Retrieval Keywords: TiDB Sysbench Performance Test Report -- v5.4.0 vs. v5.3.0, AWS EC2 test environment, PD m5.xlarge 3, TiKV i3.4xlarge 3, TiDB c5.4xlarge 3, Sysbench c5.9xlarge 1, Sysbench 1.1.0-ead2689, performance.max-procs: 20, prepared-plan-cache.enabled: true, tikv-client.max-batch-wait-time: 2000000, storage.scheduler-worker-pool-size: 5, pessimistic-txn.pipelined: true, set global tidb_enable_async_commit = 1, set global tidb_enable_1pc = 1, set global tidb_guarantee_linearizability = 0, set global tidb_enable_clustered_index = 1, HAProxy configuration - haproxy.cfg, listen tidb-cluster, bind 0.0.0.0:3390, balance roundrobin
- Follow-up Guidance: The source also points to Best Practices for Using HAProxy in TiDB for more details about how to use HAProxy on TiDB.
- Classification Note: This is classified as performance because it defines the benchmark goal, hardware and software environment, and parameter configuration used for the Sysbench comparison.

## Official Source Content

# TiDB Sysbench Performance Test Report -- v5.4.0 vs. v5.3.0
## Test overview

This test aims at comparing the Sysbench performance of TiDB v5.4.0 and TiDB v5.3.0 in the Online Transactional Processing (OLTP) scenario. The results show that performance of v5.4.0 is improved by 2.59% ~ 4.85% in the write-heavy workload.
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
| PD        | v5.3.0 and v5.4.0   |
| TiDB      | v5.3.0 and v5.4.0   |
| TiKV      | v5.3.0 and v5.4.0   |
| Sysbench  | 1.1.0-ead2689   |
### Parameter configuration

TiDB v5.4.0 and TiDB v5.3.0 use the same configuration.
#### TiDB parameter configuration

```yaml
log.level: "error"
performance.max-procs: 20
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
readpool.unified.min-thread-count: 5
readpool.unified.max-thread-count: 20
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
   chroot      /var/lib/haproxy            # Changes the current directory and sets superuser privileges for the startup process to improve security.
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
   balance roundrobin                      # The server with the fewest connections receives the connection. "leastconn" is recommended where long sessions are expected, such as LDAP, SQL and TSE, rather than protocols using short sessions, such as HTTP. The algorithm is dynamic, which means that server weights might be adjusted on the fly for slow starts for instance.
   server tidb-1 10.9.18.229:4000 check inter 2000 rise 2 fall 3       # Detects port 4000 at a frequency of once every 2000 milliseconds. If it is detected as successful twice, the server is considered available; if it is detected as failed three times, the server is considered unavailable.
   server tidb-2 10.9.39.208:4000 check inter 2000 rise 2 fall 3
   server tidb-3 10.9.64.166:4000 check inter 2000 rise 2 fall 3
```
