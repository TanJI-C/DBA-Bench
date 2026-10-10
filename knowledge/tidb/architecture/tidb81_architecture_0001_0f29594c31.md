# Use a dedicated Raft Engine disk on public cloud

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/best-practices-on-public-cloud.md`
- Source Title: `TiDB Best Practices on Public Cloud`
- Source Heading Path: `TiDB Best Practices on Public Cloud > Use a dedicated disk for Raft Engine | TiDB Best Practices on Public Cloud > Use a dedicated disk for Raft Engine > Choose appropriate disks for Raft Engine on public clouds | TiDB Best Practices on Public Cloud > Use a dedicated disk for Raft Engine > Choose appropriate disks for Raft Engine on public clouds > Middle-range disk | TiDB Best Practices on Public Cloud > Use a dedicated disk for Raft Engine > Choose appropriate disks for Raft Engine on public clouds > High-end disk | TiDB Best Practices on Public Cloud > Use a dedicated disk for Raft Engine > Example 1: Run a social network workload on AWS | TiDB Best Practices on Public Cloud > Use a dedicated disk for Raft Engine > Example 2: Run TPC-C/Sysbench workload on Azure | TiDB Best Practices on Public Cloud > Use a dedicated disk for Raft Engine > Example 3: Attach a dedicated pd-ssd disk on Google Cloud for Raft Engine on TiKV manifest`
- Source Line Ranges: `45-132`
- Source Scope: `cloud`
- Primary Component: `tikv`
- Related Components: `cloud`, `operator`
- Topic Tags: `raft-engine`, `dedicated-disk`, `iostat`, `flush`, `fdatasync`, `iops`, `throughput`, `latency`, `aws`, `azure`, `google-cloud`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0001_0f29594c31`
- Source ID: `tidb-docs-8.1:best-practices/best-practices-on-public-cloud.md#use-a-dedicated-disk-for-raft-engine`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3a69951cc5c87b5384e9088f8d98fd450ed091922edf2099ef8484dd512c2d59`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/best-practices-on-public-cloud#use-a-dedicated-disk-for-raft-engine
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/best-practices-on-public-cloud.md

## Retrieval Guidance

- Use When: Use this chunk when looking for public cloud TiKV architecture guidance about placing Raft Engine on a dedicated disk, selecting disk types by cloud provider, or configuring `raft-engine.dir`.
- Retrieval Keywords: Use a dedicated disk for Raft Engine, Raft Engine, write-ahead log, iostat, f/s, fdatasync(), dedicated disk, write latency, IOPS, MBPS, AWS gp3, AWS io2, Google Cloud pd-ssd, Google Cloud pd-extreme, Azure Premium SSD v2, Azure ultra disk, raft-engine.dir, enable-log-recycle, TiDB Operator
- Follow-up Guidance: The content includes workload examples on AWS and Azure with QPS and latency improvements, and a Google Cloud TiKV manifest example that sets `[raft-engine] dir = "/var/lib/raft-pv-ssd/raft-engine"`.
- Classification Note: This is classified as architecture because the content centers on storage layout and disk provisioning for the TiKV Raft Engine, including dedicated-disk design and cloud-specific disk choices.

## Official Source Content

## Use a dedicated disk for Raft Engine

The [Raft Engine](https://docs.pingcap.com/tidb/stable/glossary#raft-engine) in TiKV plays a critical role similar to that of a write-ahead log (WAL) in traditional databases. To achieve optimal performance and stability, it is crucial to allocate a dedicated disk for the Raft Engine when you deploy TiDB on public cloud. The following `iostat` shows the I/O characteristics on a TiKV node with a write-heavy workload.

```
Device            r/s     rkB/s       w/s     wkB/s      f/s  aqu-sz  %util
sdb           1649.00 209030.67   1293.33 304644.00    13.33    5.09  48.37
sdd           1033.00   4132.00   1141.33  31685.33   571.00    0.94 100.00
```

The device `sdb` is used for KV RocksDB, while `sdd` is used to restore Raft Engine logs. Note that `sdd` has a significantly higher `f/s` value, which represents the number of flush requests completed per second for the device. In Raft Engine, when a write in a batch is marked synchronous, the batch leader will call `fdatasync()` after writing, guaranteeing that buffered data is flushed to the storage. By using a dedicated disk for Raft Engine, TiKV reduces the average queue length of requests, thereby ensuring optimal and stable write latency.

Different cloud providers offer various disk types with different performance characteristics, such as IOPS and MBPS. Therefore, it is important to choose an appropriate cloud provider, disk type, and disk size based on your workload.
### Choose appropriate disks for Raft Engine on public clouds

This section outlines best practices for choosing appropriate disks for Raft Engine on different public clouds. Depending on performance requirements, two types of recommended disks are available.
#### Middle-range disk

The following are recommended middle-range disks for different public clouds:

- On AWS, [gp3](https://aws.amazon.com/ebs/general-purpose/) is recommended. The gp3 volume offers a free allocation of 3000 IOPS and 125 MB/s throughput, regardless of the volume size, which is usually sufficient for the Raft Engine.

- On Google Cloud, [pd-ssd](https://cloud.google.com/compute/docs/disks#disk-types/) is recommended. The IOPS and MBPS vary depending on the allocated disk size. To meet performance requirements, it is recommended to allocate 200 GB for Raft Engine. Although Raft Engine does not require such a large space, it ensures optimal performance.

- On Azure, [Premium SSD v2](https://learn.microsoft.com/en-us/azure/virtual-machines/disks-types#premium-ssd-v2) is recommended. Similar to AWS gp3, Premium SSD v2 provides a free allocation of 3000 IOPS and 125 MB/s throughput, regardless of the volume size, which is usually sufficient for Raft Engine.
#### High-end disk

If you expect an even lower latency for Raft Engine, consider using high-end disks. The following are recommended high-end disks for different public clouds:

- On AWS, [io2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-volume-types.html) is recommended. Disk size and IOPS can be provisioned according to your specific requirements.

- On Google Cloud, [pd-extreme](https://cloud.google.com/compute/docs/disks#disk-types/) is recommended. Disk size, IOPS, and MBPS can be provisioned, but it is only available on instances with more than 64 CPU cores.

- On Azure, [ultra disk](https://learn.microsoft.com/en-us/azure/virtual-machines/disks-types#ultra-disks) is recommended. Disk size, IOPS, and MBPS can be provisioned according to your specific requirements.
### Example 1: Run a social network workload on AWS

AWS offers 3000 IOPS and 125 MBPS/s for a 20 GB [gp3](https://aws.amazon.com/ebs/general-purpose/) volume.

By using a dedicated 20 GB [gp3](https://aws.amazon.com/ebs/general-purpose/) Raft Engine disk on AWS for a write-intensive social network application workload, the following improvements are observed but the estimated cost only increases by 0.4%:

- a 17.5% increase in QPS (queries per second)
- an 18.7% decrease in average latency for insert statements
- a 45.6% decrease in p99 latency for insert statements.

| Metric | Shared Raft Engine disk | Dedicated Raft Engine disk | Difference (%) |
| ------------- | ------------- |------------- |------------- |
| QPS (K/s)| 8.0 | 9.4 | 17.5|
| AVG Insert Latency (ms)| 11.3 | 9.2 | -18.7 |
| P99 Insert Latency (ms)| 29.4 | 16.0 | -45.6|
### Example 2: Run TPC-C/Sysbench workload on Azure

By using a dedicated 32 GB [ultra disk](https://learn.microsoft.com/en-us/azure/virtual-machines/disks-types#ultra-disks) for Raft Engine on Azure, the following improvements are observed:

- Sysbench `oltp_read_write` workload: a 17.8% increase in QPS and a 15.6% decrease in average latency.
- TPC-C workload: a 27.6% increase in QPS and a 23.1% decrease in average latency.

| Metric | Workload | Shared Raft Engine disk | Dedicated Raft Engine disk | Difference (%) |
| ------------- | ------------- | ------------- |------------- |------------- |
| QPS (K/s) | Sysbench `oltp_read_write` | 60.7 | 71.5 | 17.8|
| QPS (K/s) | TPC-C | 23.9 | 30.5 | 27.6|
| AVG Latency (ms)| Sysbench `oltp_read_write` |  4.5 | 3.8 | -15.6 |
| AVG Latency (ms)| TPC-C |  3.9 | 3.0 | -23.1 |
### Example 3: Attach a dedicated pd-ssd disk on Google Cloud for Raft Engine on TiKV manifest

The following TiKV configuration example shows how to attach an additional 512 GB [pd-ssd](https://cloud.google.com/compute/docs/disks#disk-types/) disk to a cluster on Google Cloud deployed by [TiDB Operator](https://docs.pingcap.com/tidb-in-kubernetes/stable), with `raft-engine.dir` configured to store Raft Engine logs to this specific disk.

```
tikv:
    config: |
      [raft-engine]
        dir = "/var/lib/raft-pv-ssd/raft-engine"
        enable = true
        enable-log-recycle = true
    requests:
      storage: 4Ti
    storageClassName: pd-ssd
    storageVolumes:
    - mountPath: /var/lib/raft-pv-ssd
      name: raft-pv-ssd
      storageSize: 512Gi
```
