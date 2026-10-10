# Check and configure operating system optimal parameters

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/check-before-deployment.md`
- Source Title: `TiDB Environment and System Configuration Check`
- Source Heading Path: `TiDB Environment and System Configuration Check > Check and configure the optimal parameters of the operating system`
- Source Line Ranges: `436-626`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`
- Topic Tags: `operating-system`, `thp`, `io-scheduler`, `nvme`, `ssd`, `cpufreq`, `performance-mode`, `tuned`, `udev`, `kernel-parameters`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0019_2dd6be1d03`
- Source ID: `tidb-docs-8.1:check-before-deployment.md#check-and-configure-the-optimal-parameters-of-the-operating-system`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ddae8648678acb8efc28e1b7c21d301ed7d53de4e6aade97b2814ab9688c87e8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/check-before-deployment#check-and-configure-the-optimal-parameters-of-the-operating-system
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/check-before-deployment.md

## Retrieval Guidance

- Use When: Use this chunk when checking or tuning self-managed TiDB production operating system settings such as THP, disk I/O Scheduler, cpufreq governor, tuned profiles, or kernel parameters.
- Retrieval Keywords: Transparent Huge Pages, THP, cat /sys/kernel/mm/transparent_hugepage/enabled, [always] madvise never, I/O Scheduler, noop, none, deadline, cat /sys/block/sd[bc]/queue/scheduler, cat /sys/block/nvme[01]*/queue/scheduler, NVMe, SSD, ID_SERIAL, udevadm info --name=/dev/sdb | grep ID_SERIAL, cpufreq, cpupower frequency-info --policy, The governor "powersave", performance, tuned-adm list, Current active profile: balanced, balanced-tidb-optimal, /etc/tuned/balanced-tidb-optimal/tuned.conf, transparent_hugepages=never, devices_udev_regex, elevator=noop, tuned-adm profile balanced-tidb-optimal, grubby --default-kernel, grubby --args="transparent_hugepage=never" --update-kernel `grubby --default-kernel`
- Follow-up Guidance: The content includes two grounded configuration methods: creating and applying a tuned profile such as `balanced-tidb-optimal`, or modifying the kernel parameter with `grubby --args="transparent_hugepage=never" --update-kernel`.
- Classification Note: This chunk is classified as configuration because it provides operating system parameter checks and concrete settings for THP, I/O Scheduler, cpufreq, tuned, udev-based disk matching, and kernel configuration.

## Official Source Content

## Check and configure the optimal parameters of the operating system

For TiDB in the production environment, it is recommended to optimize the operating system configuration in the following ways:

1. Disable THP (Transparent Huge Pages). The memory access pattern of databases tends to be sparse rather than consecutive. If the high-level memory fragmentation is serious, higher latency will occur when THP pages are allocated.
2. Set the I/O Scheduler of the storage media.

    - For the high-speed SSD storage, the kernel's default I/O scheduling operations might cause performance loss. It is recommended to set the I/O Scheduler to first-in-first-out (FIFO), such as `noop` or `none`. This configuration allows the kernel to pass I/O requests directly to hardware without scheduling, thus improving performance.
    - For NVMe storage, the default I/O Scheduler is `none`, so no adjustment is needed.

3. Choose the `performance` mode for the cpufrequ module which controls the CPU frequency. The performance is maximized when the CPU frequency is fixed at its highest supported operating frequency without dynamic adjustment.

Take the following steps to check the current operating system configuration and configure optimal parameters:

1. Execute the following command to see whether THP is enabled or disabled:

    ```bash
    cat /sys/kernel/mm/transparent_hugepage/enabled
    ```

    ```
    [always] madvise never
    ```

    > **Note:**
    >
    > If `[always] madvise never` is output, THP is enabled. You need to disable it.

2. Execute the following command to see the I/O Scheduler of the disk where the data directory is located.

    If your data directory uses an SD or VD device, run the following command to check the I/O Scheduler:

    ```bash
    cat /sys/block/sd[bc]/queue/scheduler
    ```

    ```
    noop [deadline] cfq
    noop [deadline] cfq
    ```

    > **Note:**
    >
    > If `noop [deadline] cfq` is output, the I/O Scheduler for the disk is in the `deadline` mode. You need to change it to `noop`.

    If your data directory uses an NVMe device, run the following command to check the I/O Scheduler:

    ```bash
    cat /sys/block/nvme[01]*/queue/scheduler
    ```

    ```
    [none] mq-deadline kyber bfq
    [none] mq-deadline kyber bfq
    ```

    > **Note:**
    >
    > `[none] mq-deadline kyber bfq` indicates that the NVMe device uses the `none` I/O Scheduler, and no changes are needed.

3. Execute the following command to see the `ID_SERIAL` of the disk:

    ```bash
    udevadm info --name=/dev/sdb | grep ID_SERIAL
    ```

    ```
    E: ID_SERIAL=36d0946606d79f90025f3e09a0c1f9e81
    E: ID_SERIAL_SHORT=6d0946606d79f90025f3e09a0c1f9e81
    ```

    > **Note:**
    >
    > - If multiple disks are allocated with data directories, you need to execute the above command for each disk to record the `ID_SERIAL` of each disk.
    > - If your device uses the `noop` or `none` Scheduler, you do not need to record the `ID_SERIAL` or configure udev rules or the tuned profile.

4. Execute the following command to see the power policy of the cpufreq module:

    ```bash
    cpupower frequency-info --policy
    ```

    ```
    analyzing CPU 0:
    current policy: frequency should be within 1.20 GHz and 3.10 GHz.
                  The governor "powersave" may decide which speed to use within this range.
    ```

    > **Note:**
    >
    > If `The governor "powersave"` is output, the power policy of the cpufreq module is `powersave`. You need to modify it to `performance`. If you use a virtual machine or a cloud host, the output is usually `Unable to determine current policy`, and you do not need to change anything.

5. Configure optimal parameters of the operating system:

    + Method one: Use tuned (Recommended)

        1. Execute the `tuned-adm list` command to see the tuned profile of the current operating system:

            ```bash
            tuned-adm list
            ```

            ```
            Available profiles:
            - balanced                    - General non-specialized tuned profile
            - desktop                     - Optimize for the desktop use-case
            - hpc-compute                 - Optimize for HPC compute workloads
            - latency-performance         - Optimize for deterministic performance at the cost of increased power consumption
            - network-latency             - Optimize for deterministic performance at the cost of increased power consumption, focused on low latency network performance
            - network-throughput          - Optimize for streaming network throughput, generally only necessary on older CPUs or 40G+ networks
            - powersave                   - Optimize for low power consumption
            - throughput-performance      - Broadly applicable tuning that provides excellent performance across a variety of common server workloads
            - virtual-guest               - Optimize for running inside a virtual guest
            - virtual-host                - Optimize for running KVM guests
            Current active profile: balanced
            ```

            The output `Current active profile: balanced` means that the tuned profile of the current operating system is `balanced`. It is recommended to optimize the configuration of the operating system based on the current profile.

        2. Create a new tuned profile:

            ```bash
            mkdir /etc/tuned/balanced-tidb-optimal/
            vi /etc/tuned/balanced-tidb-optimal/tuned.conf
            ```

            ```
            [main]
            include=balanced

            [cpu]
            governor=performance

            [vm]
            transparent_hugepages=never

            [disk]
            devices_udev_regex=(ID_SERIAL=36d0946606d79f90025f3e09a0c1fc035)|(ID_SERIAL=36d0946606d79f90025f3e09a0c1f9e81)
            elevator=noop
            ```

            The output `include=balanced` means to add the optimization configuration of the operating system to the current `balanced` profile.

        3. Apply the new tuned profile:

            > **Note:**
            >
            > If your device uses the `noop` or `none` I/O Scheduler, skip this step. No Scheduler configuration is needed in the tuned profile.

            ```bash
            tuned-adm profile balanced-tidb-optimal
            ```

    + Method two: Configure using scripts. Skip this method if you already use method one.

        1. Execute the `grubby` command to see the default kernel version:

            > **Note:**
            >
            > Install the `grubby` package first before you execute `grubby`.

            ```bash
            grubby --default-kernel
            ```

            ```bash
            /boot/vmlinuz-3.10.0-957.el7.x86_64
            ```

        2. Execute `grubby --update-kernel` to modify the kernel configuration:

            ```bash
            grubby --args="transparent_hugepage=never" --update-kernel `grubby --default-kernel`
            ```
