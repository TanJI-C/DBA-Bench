# TPC-C v5.4.0 vs v5.3.0 benchmark setup and results

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/v5.4-performance-benchmarking-with-tpcc.md`
- Source Title: `TiDB TPC-C Performance Test Report -- v5.4.0 vs. v5.3.0`
- Source Heading Path: `TiDB TPC-C Performance Test Report -- v5.4.0 vs. v5.3.0 | TiDB TPC-C Performance Test Report -- v5.4.0 vs. v5.3.0 > Test overview | TiDB TPC-C Performance Test Report -- v5.4.0 vs. v5.3.0 > Test environment (AWS EC2） | TiDB TPC-C Performance Test Report -- v5.4.0 vs. v5.3.0 > Test environment (AWS EC2） > Hardware configuration | TiDB TPC-C Performance Test Report -- v5.4.0 vs. v5.3.0 > Test environment (AWS EC2） > Software version | TiDB TPC-C Performance Test Report -- v5.4.0 vs. v5.3.0 > Test environment (AWS EC2） > Parameter configuration | TiDB TPC-C Performance Test Report -- v5.4.0 vs. v5.3.0 > Test environment (AWS EC2） > Parameter configuration > TiDB parameter configuration | TiDB TPC-C Performance Test Report -- v5.4.0 vs. v5.3.0 > Test environment (AWS EC2） > Parameter configuration > TiKV parameter configuration | TiDB TPC-C Performance Test Report -- v5.4.0 vs. v5.3.0 > Test environment (AWS EC2） > Parameter configuration > TiDB global variable configuration | TiDB TPC-C Performance Test Report -- v5.4.0 vs. v5.3.0 > Test environment (AWS EC2） > Parameter configuration > HAProxy configuration - haproxy.cfg | TiDB TPC-C Performance Test Report -- v5.4.0 vs. v5.3.0 > Test environment (AWS EC2） > Prepare test data | TiDB TPC-C Performance Test Report -- v5.4.0 vs. v5.3.0 > Test result`
- Source Line Ranges: `5-129`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `tiup`, `shared`
- Topic Tags: `tpcc`, `benchmarksql`, `oltp`, `aws-ec2`, `hardware-configuration`, `software-version`, `parameter-configuration`, `global-variables`, `haproxy`, `test-data`, `stress-test`, `tpmc`, `performance-results`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0050_0ef33d0d39`
- Source ID: `tidb-docs-8.1:benchmark/v5.4-performance-benchmarking-with-tpcc.md#tidb-tpc-c-performance-test-report-v5-4-0-vs-v5-3-0`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7b1d31e113d78f89ed96ffbbfbde442c7a22ecb87e81690bf8dce1929fd405da`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/v5.4-performance-benchmarking-with-tpcc#tidb-tpc-c-performance-test-report-v5-4-0-vs-v5-3-0
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/v5.4-performance-benchmarking-with-tpcc.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the official TPC-C benchmark setup and result comparison between TiDB v5.4.0 and v5.3.0, including environment, parameters, BenchmarkSQL commands, HAProxy configuration, and tpmC improvement.
- Retrieval Keywords: TiDB TPC-C Performance Test Report -- v5.4.0 vs. v5.3.0, v5.4.0 vs v5.3.0 TPC-C, 3.16% improved, AWS EC2, BenchmarkSQL, tiup bench tpcc prepare --warehouses 5000 --db tpcc -H 127.0.0.1 -P 4000, tiup bench tpcc run -U root --db tpcc --host 127.0.0.1 --port 4000 --time 1800s --warehouses 5000 --threads, create database tpcc;, tpmC, New Order, PD m5.xlarge, TiKV i3.4xlarge, TiDB c5.4xlarge, TPC-C c5.9xlarge, prepared-plan-cache.enabled, tikv-client.max-batch-wait-time, pessimistic-txn.pipelined, raftstore.apply-max-batch-size, server.grpc-concurrency, tidb_hashagg_final_concurrency, tidb_hashagg_partial_concurrency, tidb_enable_async_commit, tidb_enable_1pc, tidb_guarantee_linearizability, tidb_enable_clustered_index, haproxy.cfg, listen tidb-cluster, bind 0.0.0.0:3390, balance roundrobin, Best Practices for Using HAProxy in TiDB
- Follow-up Guidance: The source also points to Best Practices for Using HAProxy in TiDB for more details about using HAProxy on TiDB.
- Classification Note: This chunk is classified as performance because it reports OLTP TPC-C benchmarking results for TiDB v5.4.0 and v5.3.0 with the full test environment and parameter configuration.

## Official Source Content

# TiDB TPC-C Performance Test Report -- v5.4.0 vs. v5.3.0
## Test overview

This test aims at comparing the TPC-C performance of TiDB v5.4.0 and v5.3.0 in the Online Transactional Processing (OLTP) scenario. The results show that compared with v5.3.0, the TPC-C performance of v5.4.0 is improved by 3.16%.
## Test environment (AWS EC2）
### Hardware configuration

| Service type | EC2 type | Instance count |
|:----------|:----------|:----------|
| PD        | m5.xlarge |     3     |
| TiKV      | i3.4xlarge|     3     |
| TiDB      | c5.4xlarge|     3     |
| TPC-C  | c5.9xlarge|     1     |
### Software version

| Service type | Software version |
|:----------|:-----------|
| PD        | v5.3.0 and v5.4.0   |
| TiDB      | v5.3.0 and v5.4.0   |
| TiKV      | v5.3.0 and v5.4.0   |
| TiUP  | 1.5.1     |
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
pessimistic-txn.pipelined: true
raftdb.allow-concurrent-memtable-write: true
raftdb.max-background-jobs: 4
raftstore.apply-max-batch-size: 2048
raftstore.apply-pool-size: 3
raftstore.store-max-batch-size: 2048
raftstore.store-pool-size: 3
readpool.storage.normal-concurrency: 10
readpool.unified.max-thread-count: 20
readpool.unified.min-thread-count: 5
rocksdb.max-background-jobs: 8
server.grpc-concurrency: 6
storage.scheduler-worker-pool-size: 20
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
### Prepare test data

1. Deploy TiDB v5.4.0 and v5.3.0 using TiUP.
2. Create a database named `tpcc`: `create database tpcc;`.
3. Use BenchmarkSQL to import the TPC-C 5000 Warehouse data: `tiup bench tpcc prepare --warehouses 5000 --db tpcc -H 127.0.0.1 -P 4000`.
4. Run the `tiup bench tpcc run -U root --db tpcc --host 127.0.0.1 --port 4000 --time 1800s --warehouses 5000 --threads {{thread}}` command to perform stress tests on TiDB via HAProxy. For each concurrency, the test takes 30 minutes.
5. Extract the tpmC data of New Order from the result.
## Test result

Compared with v5.3.0, the TPC-C performance of v5.4.0 is **improved by 3.16%**.

| Threads | v5.3.0 tpmC | v5.4.0 tpmC | tpmC improvement (%) |
|:----------|:----------|:----------|:----------|
|50|43002.4|44204.4|2.80|
|100|50162.7|52305|4.27|
|200|55768.2|57690.7|3.45|
|400|56836.8|58034.6|2.11|

![TPC-C](/media/tpcc_v530_vs_v540.png)
