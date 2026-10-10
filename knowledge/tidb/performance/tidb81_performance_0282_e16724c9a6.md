# Network tuning bottlenecks and kernel or NIC adjustments

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tune-operating-system.md`
- Source Title: `Tune Operating System Performance`
- Source Heading Path: `Tune Operating System Performance > Performance tuning > Network tuning`
- Source Line Ranges: `103-127`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `network`, `nic`, `packet-loss`, `rss`, `rps`, `rfs`, `interrupts`, `softirq`, `socket-queue`, `flow-control`, `interrupt-coalescing`, `backlog`, `tx-queue`, `driver-tuning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0282_e16724c9a6`
- Source ID: `tidb-docs-8.1:tune-operating-system.md#network-tuning`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0abc0262b5bf417cdc413dcf60ba21565f77b23e62e5ff34eae290118a36f7e4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tune-operating-system#network-tuning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tune-operating-system.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing network-related performance bottlenecks or packet loss in a self-managed TiDB environment and you need the documented kernel, NIC, interrupt, queue, and socket indicators mentioned in the operating system tuning guide.
- Retrieval Keywords: Network tuning, ethtool -S ${NIC_DEV_NAME}, drops, ethtool -g ${NIC_DEV_NAME}, ethtool -G ${NIC_DEV_NAME}, /proc/interrupts, Receive-Side Scaling, RSS, Receive Packet Steering, RPS, Receive Flow Steering, RFS, /proc/net/softnet_stat, net.core.netdev_budget, net.core.dev_weight, softirq, ss -nmp, Recv-q, Ethernet flow control, interrupt coalescing, ethtool -c ${NIC_DEV_NAME}, ethtool -C ${NIC_DEV_NAME}, adaptive mode, net.core.netdev_max_backlog, ip -s link, TX errors, ip link set dev ${NIC_DEV_NAME} txqueuelen 2000, driver tuning
- Follow-up Guidance: The content points to related CPU topics for uneven NIC interrupts and references the kernel scaling document and NIC manuals for detailed RPS, RFS, and driver-specific settings.
- Classification Note: The official content is classified as performance for shared TiDB, TiKV, and PD components in self-managed deployments because it describes operating system network tuning factors such as NIC buffers, interrupts, softirq, socket queues, backlog, send queues, and driver parameters that can affect overall system performance.

## Official Source Content

### Network tuning

The network subsystem consists of many different parts with sensitive connections. The CentOS 7 network subsystem is designed to provide the best performance for most workloads and automatically optimizes the performance of these workloads. Therefore, usually you do not need to manually adjust network performance.

Network issues are usually caused by issues of hardware or related devices. So before tuning the protocol stack, rule out hardware issues.

Although the network stack is largely self-optimizing, the following aspects in the network packet processing might become the bottleneck and affect performance:

- NIC hardware cache: To correctly observe the packet loss at the hardware level, use the `ethtool -S ${NIC_DEV_NAME}` command to observe the `drops` field. When packet loss occurs, it might be that the processing speed of the hard/soft interrupts cannot catch up with the receiving speed of NIC. If the received buffer size is less than the upper limit, you can also try to increase the RX buffer to avoid packet loss. The query command is: `ethtool -g ${NIC_DEV_NAME}`, and the modification command is `ethtool -G ${NIC_DEV_NAME}`.

- Hardware interrupts: If the NIC supports the Receive-Side Scaling (RSS, also called multi-NIC receiving) feature, observe the `/proc/interrupts` NIC interrupts. If the interrupts are uneven, see [CPU—frequency scaling](#cpufrequency-scaling), [CPU—interrupt affinity](#cpuinterrupt-affinity), and [NUMA CPU binding](#numa-cpu-binding). If the NIC does not support RSS or the number of RSS is much smaller than the number of physical CPU cores, configure Receive Packet Steering (RPS, which can be regarded as the software implementation of RSS), and the RPS extension Receive Flow Steering (RFS). For detailed configuration, see the [kernel document](https://www.kernel.org/doc/Documentation/networking/scaling.txt).

- Software interrupts: Observe the monitoring of `/proc/net/softnet_stat`. If the values of the other columns except the third column are increasing, properly adjust the value of `net.core.netdev_budget` or `net.core.dev_weight` for `softirq` to get more CPU time. In addition, you also need to check the CPU usage to determine which tasks are frequently using the CPU and whether they can be optimized.

- Receive queue of application sockets: Monitor the `Resv-q` column of `ss -nmp`. If the queue is full, consider increasing the size of the application socket cache or use the automatic cache adjustment method. In addition, consider whether you can optimize the architecture of the application layer and reduce the interval between reading sockets.

- Ethernet flow control: If the NIC and switch support the flow control feature, you can use this feature to leave some time for the kernel to process the data in the NIC queue, to avoid the issue of NIC buffer overflow.

- Interrupts coalescing: Too frequent hardware interrupts reduces system performance, and too late hardware interrupts causes packet loss. Newer NICs support the interrupt coalescing feature and allow the driver to automatically adjust the number of hardware interrupts. You can execute `ethtool -c ${NIC_DEV_NAME}` to check and `ethtool -C ${NIC_DEV_NAME}` to enable this feature. The adaptive mode allows the NIC to automatically adjust the interrupt coalescing. In this mode, the driver checks the traffic mode and kernel receiving mode, and evaluates the coalescing settings in real time to prevent packet loss. NICs of different brands have different features and default configurations. For details, see the NIC manuals.

- Adapter queue: Before processing the protocol stack, the kernel uses this queue to buffer the data received by the NIC, and each CPU has its own backlog queue. The maximum number of packets that can be cached in this queue is `netdev_max_backlog`. Observe the second column of `/proc/net/softnet_stat`. When the second column of a row continues to increase, it means that the CPU [row-1] queue is full and the data packet is lost. To resolve this problem, continue to double the `net.core.netdev_max_backlog` value.

- Send queue: The length value of a send queue determines the number of packets that can be queued before sending. The default value is `1000`, which is sufficient for 10 Gbps. But if you have observed the value of TX errors from the output of `ip -s link`, you can try to double it: `ip link set dev ${NIC_DEV_NAME} txqueuelen 2000`.

- Driver: NIC drivers usually provide tuning parameters. See the device hardware manual and its driver documentation.
