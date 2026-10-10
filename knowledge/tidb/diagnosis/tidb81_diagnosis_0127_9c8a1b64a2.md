# PD anomaly causes of latency

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/troubleshoot-cpu-issues.md`
- Source Title: `Troubleshoot Increased Read and Write Latency`
- Source Heading Path: `Troubleshoot Increased Read and Write Latency > Common causes > PD anomalies | Troubleshoot Increased Read and Write Latency > Common causes > PD anomalies > Phenomenon | Troubleshoot Increased Read and Write Latency > Common causes > PD anomalies > Possible reasons`
- Source Line Ranges: `39-68`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `dashboard`, `tidb`
- Topic Tags: `latency`, `tso`, `wait-duration`, `disk-io`, `network`, `leader-election`, `oom`, `panic`, `logs`, `grafana`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0127_9c8a1b64a2`
- Source ID: `tidb-docs-8.1:troubleshoot-cpu-issues.md#pd-anomalies`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7ef83f7ba01159c9a01a057abf78b89b9bc40068c1d9ed27e10c80ebc7d0654c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/troubleshoot-cpu-issues#pd-anomalies
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/troubleshoot-cpu-issues.md

## Retrieval Guidance

- Use When: Use this chunk when PD TSO wait duration increases abnormally and you need grounded causes involving disk, network, leader election, OOM, panic, or PD logs and Grafana metrics.
- Retrieval Keywords: PD anomalies, wait duration, PD TSO, lost the TCP streaming connection, server is likely overloaded, lease is not expired, regions cost, use-region-storage, Grafana disk performance latency load, Grafana PD etcd round trip, blackbox_exporter ping latency, range failed to find revision pair, /api/v1/regions, TCP InSegs, curl http://127.0.0.1:2379/debug/pprof/goroutine?debug=2
- Follow-up Guidance: The content says to verify causes through Grafana panels, PD logs, or goroutine output, and it includes bug-report follow-up for PD panics or other causes.
- Classification Note: This is classified as diagnosis content because it describes the PD symptom of increased wait duration and enumerates specific observable causes, logs, metrics, and checks.

## Official Source Content

### PD anomalies
#### Phenomenon

There is an abnormal increase of the `wait duration` metric for the PD TSO. This metric represents the duration of waiting for PD to return requests.
#### Possible reasons

* Disk issue. The disk where the PD node is located has full I/O load. Investigate whether PD is deployed with other components with high I/O demand and the health of the disk. You can verify the cause by viewing the monitor metrics in **Grafana** -> **disk performance** -> **latency**/**load**. You can also use the FIO tool to run a check on the disk if necessary.

* Network issues between PD peers. The PD log shows `lost the TCP streaming connection`. You need to check whether there is a problem with the network between PD nodes and verify the cause by viewing `round trip` in the monitor **Grafana** -> **PD** -> **etcd**.

* High server load. The log shows `server is likely overloaded`.

* PD cannot elect a Leader: The PD log shows `lease is not expired`. [This issue](https://github.com/etcd-io/etcd/issues/10355) has been fixed in v3.0.x and v2.1.19.

* The leader election is slow. The Region loading duration is long. You can check this issue by running `grep "regions cost"` in the PD log. If the result is in seconds, such as `load 460927 regions cost 11.77099s`, it means the Region loading is slow. You can enable the `region storage` feature in v3.0 by setting `use-region-storage` to `true`, which significantly reduce the Region loading duration.

* The network issue between TiDB and PD. Check whether the network from TiDB to PD Leader is running normally by accessing the monitor **Grafana** -> **blackbox_exporter** -> **ping latency**.

* PD reports the `FATAL` error, and the log shows `range failed to find revision pair`. This issue has been fixed in v3.0.8 ([#2040](https://github.com/pingcap/pd/pull/2040)).

* When the `/api/v1/regions` interface is used, too many Regions might cause PD OOM. This issue has been fixed in v3.0.8 ([#1986](https://github.com/pingcap/pd/pull/1986)).

* PD OOM during the rolling upgrade. The size of gRPC messages is not limited, and the monitor shows that `TCP InSegs` is relatively large. This issue has been fixed in v3.0.6 ([#1952](https://github.com/pingcap/pd/pull/1952)). 

* PD panics. [Report a bug](https://github.com/tikv/pd/issues/new?labels=kind/bug&template=bug-report.md).

* Other causes. Get goroutine by running `curl http://127.0.0.1:2379/debug/pprof/goroutine?debug=2` and [report a bug](https://github.com/pingcap/pd/issues/new?labels=kind%2Fbug&template=bug-report.md).
