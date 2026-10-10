# OS performance tuning for CPU memory and storage

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tune-operating-system.md`
- Source Title: `Tune Operating System Performance`
- Source Heading Path: `Tune Operating System Performance > Performance tuning | Tune Operating System Performance > Performance tuning > CPU—frequency scaling | Tune Operating System Performance > Performance tuning > CPU—interrupt affinity | Tune Operating System Performance > Performance tuning > NUMA CPU binding | Tune Operating System Performance > Performance tuning > Memory—transparent huge page (THP) | Tune Operating System Performance > Performance tuning > Memory—virtual memory parameters | Tune Operating System Performance > Performance tuning > Storage and file system | Tune Operating System Performance > Performance tuning > Storage and file system > I/O scheduler | Tune Operating System Performance > Performance tuning > Storage and file system > Formatting parameters—block size | Tune Operating System Performance > Performance tuning > Storage and file system > `mount` parameters`
- Source Line Ranges: `44-102`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: none
- Topic Tags: `linux`, `os-tuning`, `cpu-frequency`, `interrupt-affinity`, `numa`, `thp`, `virtual-memory`, `storage`, `io-scheduler`, `filesystem`, `mount-options`, `centos-7`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0281_25f0a29347`
- Source ID: `tidb-docs-8.1:tune-operating-system.md#performance-tuning`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4b0f7962c1db4c7ae461f797c2ad0053eeb2304ca51d436ef87c0ec94c713a9c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tune-operating-system#performance-tuning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tune-operating-system.md

## Retrieval Guidance

- Use When: Use this chunk when looking for CentOS 7 operating system tuning topics for CPU, NUMA, memory, storage, file system, and mount settings that affect performance.
- Retrieval Keywords: Performance tuning, CPU frequency scaling, cpufreq, cpupower frequency-set --governor performance, CPU interrupt affinity, irqbalance, smp_affinity, IRQ-affinity.txt, NUMA CPU binding, numactl, transparent huge page, THP, echo never > /sys/kernel/mm/transparent_hugepage/enabled, echo never > /sys/kernel/mm/transparent_hugepage/defrag, dirty_ratio, dirty_background_ratio, pdflush, NVMe, I/O scheduler, noop, echo noop > /sys/block/${SSD_DEV_NAME}/queue/scheduler, mkfs, man mkfs.ext4, mount parameters, noatime, nodiratime, CentOS 7.5
- Follow-up Guidance: The source includes exact commands for CPU governor, disabling THP, and setting the SSD I/O scheduler, and it points to kernel and Linux manual pages for interrupt affinity, numactl, and mkfs details.
- Classification Note: This is classified as performance for the shared component because it covers operating system subsystem tuning across CPU, memory, and storage rather than behavior of a specific TiDB service.

## Official Source Content

## Performance tuning

This section introduces performance tuning based on the classified kernel subsystems.
### CPU—frequency scaling

cpufreq is a module that dynamically adjusts the CPU frequency. It supports five modes. To ensure service performance, select the performance mode and fix the CPU frequency at the highest supported operating frequency without dynamic adjustment. The command for this operation is `cpupower frequency-set --governor performance`.
### CPU—interrupt affinity

- Automatic balance can be implemented through the `irqbalance` service.
- Manual balance:
    - Identify the devices that need to balance interrupts. Starting from CentOS 7.5, the system automatically configures the best interrupt affinity for certain devices and their drivers, such as devices that use the `be2iscsi` driver and NVMe settings. You can no longer manually configure interrupt affinity for such devices.
    - For other devices, check the chip manual to see whether these devices support distributing interrupts.
        - If they do not, all interrupts of these devices are routed to the same CPU and cannot be modified.
        - If they do, calculate the `smp_affinity` mask and set the corresponding configuration file. For details, see the [kernel document](https://www.kernel.org/doc/Documentation/IRQ-affinity.txt).
### NUMA CPU binding

To avoid accessing memory across Non-Uniform Memory Access (NUMA) nodes as much as possible, you can bind a thread/process to certain CPU cores by setting the CPU affinity of the thread. For ordinary programs, you can use the `numactl` command for the CPU binding. For detailed usage, see the Linux manual pages. For network interface card (NIC) interrupts, see [tune network](#network-tuning).
### Memory—transparent huge page (THP)

It is **NOT** recommended to use THP for database applications, because databases often have sparse rather than continuous memory access patterns. If high-level memory fragmentation is serious, a higher latency will occur when THP pages are allocated. If the direct compaction is enabled for THP, the CPU usage will surge. Therefore, it is recommended to disable THP.

```shell
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag
```
### Memory—virtual memory parameters

- `dirty_ratio` percentage ratio. When the total amount of dirty page caches reach this percentage ratio of the total system memory, the system starts to use the `pdflush` operation to write the dirty page caches to disk. The default value of `dirty_ratio` is 20% and usually does not need adjustment. For high-performance SSDs such as NVMe devices, lowering this value helps improve the efficiency of memory reclamation.
- `dirty_background_ratio` percentage ratio. When the total amount of dirty page caches reach this percentage ratio of the total system memory, the system starts to write the dirty page caches to the disk in the background. The default value of `dirty_background_ratio` is 10% and usually does not need adjustment. For high-performance SSDs such as NVMe devices, setting a lower value helps improve the efficiency of memory reclamation.
### Storage and file system

The core I/O stack link is long, including the file system layer, the block device layer, and the driver layer.
#### I/O scheduler

The I/O scheduler determines when and how long I/O operations run on the storage device. It is also called I/O elevator. For SSD devices, it is recommended to set the I/O scheduling policy to `noop`.

```shell
echo noop > /sys/block/${SSD_DEV_NAME}/queue/scheduler
```
#### Formatting parameters—block size

Blocks are the working units of the file system. The block size determines how much data can be stored in a single block, and thus determines the minimum amount of data to be written or read each time.

The default block size is suitable for most scenarios. However, if the block size (or the size of multiple blocks) is the same or slightly larger than the amount of data normally read or written each time, the file system performs better and the data storage efficiency is higher. Small files still use the entire block. Files can be distributed among multiple blocks, but this will increase runtime overhead.

When using the `mkfs` command to format a device, specify the block size as a part of the file system options. The parameters that specify the block size vary with the file system. For details, see the corresponding `mkfs` manual pages, such as using `man mkfs.ext4`.
#### `mount` parameters

If the `noatime` option is enabled in the `mount` command, the update of metadata is disabled when files are read. If the `nodiratime` behavior is enabled, the update of metadata is disabled when the directory is read.
