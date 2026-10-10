# TPC-C v5.3.0 vs v5.2.2 benchmark environment, plan, and results

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/v5.3-performance-benchmarking-with-tpcc.md`
- Source Title: `TiDB TPC-C Performance Test Report -- v5.3.0 vs. v5.2.2`
- Source Heading Path: `TiDB TPC-C Performance Test Report -- v5.3.0 vs. v5.2.2 | TiDB TPC-C Performance Test Report -- v5.3.0 vs. v5.2.2 > Test overview | TiDB TPC-C Performance Test Report -- v5.3.0 vs. v5.2.2 > Test environment (AWS EC2) | TiDB TPC-C Performance Test Report -- v5.3.0 vs. v5.2.2 > Hardware configuration | TiDB TPC-C Performance Test Report -- v5.3.0 vs. v5.2.2 > Hardware configuration > Software version | TiDB TPC-C Performance Test Report -- v5.3.0 vs. v5.2.2 > Hardware configuration > Parameter configuration | TiDB TPC-C Performance Test Report -- v5.3.0 vs. v5.2.2 > Hardware configuration > Parameter configuration > TiDB parameter configuration | TiDB TPC-C Performance Test Report -- v5.3.0 vs. v5.2.2 > Hardware configuration > Parameter configuration > TiKV parameter configuration | TiDB TPC-C Performance Test Report -- v5.3.0 vs. v5.2.2 > Hardware configuration > Parameter configuration > TiDB global variable configuration | TiDB TPC-C Performance Test Report -- v5.3.0 vs. v5.2.2 > Hardware configuration > Parameter configuration > HAProxy configuration - haproxy.cfg | TiDB TPC-C Performance Test Report -- v5.3.0 vs. v5.2.2 > Test plan | TiDB TPC-C Performance Test Report -- v5.3.0 vs. v5.2.2 > Test result`
- Source Line Ranges: `5-129`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `tiup`, `shared`
- Topic Tags: `tpcc`, `benchmarking`, `oltp`, `aws-ec2`, `hardware-configuration`, `software-version`, `parameter-configuration`, `global-variables`, `haproxy`, `tiup`, `stress-test`, `tpmc`, `performance-regression`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0049_af9c568be2`
- Source ID: `tidb-docs-8.1:benchmark/v5.3-performance-benchmarking-with-tpcc.md#tidb-tpc-c-performance-test-report-v5-3-0-vs-v5-2-2`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5942cbda3b6b8ac679340000003213c0b201c4d7eceaee3ef820ad45f65a3dc1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/v5.3-performance-benchmarking-with-tpcc#tidb-tpc-c-performance-test-report-v5-3-0-vs-v5-2-2
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/v5.3-performance-benchmarking-with-tpcc.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB v5.3.0 versus v5.2.2 TPC-C benchmark setup and results, including AWS EC2 environment, TiUP and BenchmarkSQL test plan, configuration parameters, HAProxy settings, and tpmC comparison.
- Retrieval Keywords: TiDB TPC-C Performance Test Report -- v5.3.0 vs. v5.2.2, v5.3.0 vs v5.2.2, TPC-C, OLTP, AWS EC2, m5.xlarge, i3.4xlarge, c5.4xlarge, c5.9xlarge, TiUP 1.5.1, BenchmarkSQL, tiup bench tpcc prepare --warehouses 5000 --db tpcc -H 127.0.0.1 -p 4000, tiup bench tpcc run -U root --db tpcc --host 127.0.0.1 --port 4000 --time 1800s --warehouses 5000 --threads, create database tpcc;, tpmC, New Order, performance reduced by 2.99%, prepared-plan-cache.enabled, tikv-client.max-batch-wait-time, pessimistic-txn.pipelined, tidb_enable_async_commit, tidb_enable_1pc, tidb_guarantee_linearizability, tidb_enable_clustered_index, haproxy.cfg, listen tidb-cluster, bind 0.0.0.0:3390, balance roundrobin
- Follow-up Guidance: The source includes a link to Best Practices for Using HAProxy in TiDB for more details about how to use HAProxy on TiDB.
- Classification Note: This chunk is classified as performance content because it reports a controlled TPC-C benchmarking comparison between TiDB v5.3.0 and v5.2.2 with test environment, parameter configuration, test plan, and measured tpmC results.

## Official Source Content

# TiDB TPC-C Performance Test Report -- v5.3.0 vs. v5.2.2
## Test overview

This test aims at comparing the TPC-C performance of TiDB v5.3.0 and TiDB v5.2.2 in the online transactional processing (OLTP) scenario. The result shows that compared with v5.2.2, the TPC-C performance of v5.3.0 is reduced by 2.99%.
## Test environment (AWS EC2)
## Hardware configuration

| Service type         | EC2 type     | Instance count |
|:----------|:----------|:----------|
| PD        | m5.xlarge |     3     |
| TiKV      | i3.4xlarge|     3     |
| TiDB      | c5.4xlarge|     3     |
| TPC-C  | c5.9xlarge|     1     |
### Software version

| Service type   | Software version    |
|:----------|:-----------|
| PD        | v5.2.2 and v5.3.0   |
| TiDB      | v5.2.2 and v5.3.0   |
| TiKV      | v5.2.2 and v5.3.0   |
| TiUP  | 1.5.1     |
### Parameter configuration

TiDB v5.3.0 and TiDB v5.2.2 use the same configuration.
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
   user        haproxy                     # Same with the UID parameter.
   group       haproxy                     # Same with the GID parameter. A dedicated user group is recommended.
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
## Test plan

1. Deploy TiDB v5.3.0 and v5.2.2 using TiUP.
2. Create a database named `tpcc`: `create database tpcc;`.
3. Use BenchmarkSQL to import the TPC-C 5000 Warehouse data: `tiup bench tpcc prepare --warehouses 5000 --db tpcc -H 127.0.0.1 -p 4000`.
4. Run the `tiup bench tpcc run -U root --db tpcc --host 127.0.0.1 --port 4000 --time 1800s --warehouses 5000 --threads {{thread}}` command to perform stress tests on TiDB via HAProxy. For each concurrency, the test takes 30 minutes.
5. Extract the tpmC data of New Order from the result.
## Test result

Compared with v5.2.2, the TPC-C performance of v5.3.0 is **reduced slightly by 2.99%**.

| Threads | v5.2.2 tpmC | v5.3.0 tpmC | tpmC improvement (%) |
|:----------|:----------|:----------|:----------|
|50|42228.8|41580|-1.54|
|100|49400|48248.2|-2.33|
|200|54436.6|52809.4|-2.99|
|400|57026.7|54117.1|-5.10|

![TPC-C](/media/tpcc_v522_vs_v530.png)
