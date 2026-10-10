# OS parameter tuning verification and sysctl limits

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/check-before-deployment.md`
- Source Title: `TiDB Environment and System Configuration Check`
- Source Heading Path: `TiDB Environment and System Configuration Check > Check and configure the optimal parameters of the operating system`
- Source Line Ranges: `627-789`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiup`
- Topic Tags: `kernel`, `thp`, `io-scheduler`, `cpupower`, `sysctl`, `limits`, `numa`, `linux`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0020_b153e9c150`
- Source ID: `tidb-docs-8.1:check-before-deployment.md#check-and-configure-the-optimal-parameters-of-the-operating-system`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `aa476441607d1e71f285e74ddf8d69b0715e1104fd1feea91037774120aabbed`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/check-before-deployment#check-and-configure-the-optimal-parameters-of-the-operating-system
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/check-before-deployment.md

## Retrieval Guidance

- Use When: Use this chunk when checking or configuring Linux OS parameters before TiDB deployment, including THP, I/O Scheduler, cpupower policy, sysctl settings, and limits.conf for the tidb user.
- Retrieval Keywords: transparent_hugepage=never, grubby --info, echo never > /sys/kernel/mm/transparent_hugepage/enabled, echo never > /sys/kernel/mm/transparent_hugepage/defrag, /etc/udev/rules.d/60-tidb-schedulers.rules, ATTR{queue/scheduler}="noop", udevadm control --reload-rules, udevadm trigger --type=devices --action=change, cpupower.service, cpupower frequency-set --governor performance, cpupower frequency-info --policy, cat /sys/kernel/mm/transparent_hugepage/enabled, cat /sys/block/sd[bc]/queue/scheduler, fs.file-max = 1000000, net.core.somaxconn = 32768, net.ipv4.tcp_syncookies = 0, vm.overcommit_memory = 1, vm.min_free_kbytes = 1048576, sysctl -p, /etc/security/limits.conf, tidb soft nofile 1000000, tidb hard nofile 1000000, tidb soft stack 32768, tidb hard stack 32768, net.ipv4.tcp_tw_recycle = 0
- Follow-up Guidance: The chunk also includes verification commands and outputs for THP status, disk scheduler, and cpufreq governor, plus notes about vm.min_free_kbytes sizing and skipping udev rules when the device already uses noop or none.
- Classification Note: This is classified as configuration because the content consists of concrete kernel, udev, cpupower, sysctl, and limits.conf parameter settings and verification commands.

## Official Source Content

> **Note:**
            >
            > You can also specify the actual version number after `--update-kernel`, for example, `--update-kernel /boot/vmlinuz-3.10.0-957.el7.x86_64`.

        3. Execute `grubby --info` to see the modified default kernel configuration:

            ```bash
            grubby --info /boot/vmlinuz-3.10.0-957.el7.x86_64
            ```

            > **Note:**
            >
            > `--info` is followed by the actual default kernel version.

            ```
            index=0
            kernel=/boot/vmlinuz-3.10.0-957.el7.x86_64
            args="ro crashkernel=auto rd.lvm.lv=centos/root rd.lvm.lv=centos/swap rhgb quiet LANG=en_US.UTF-8 transparent_hugepage=never"
            root=/dev/mapper/centos-root
            initrd=/boot/initramfs-3.10.0-957.el7.x86_64.img
            title=CentOS Linux (3.10.0-957.el7.x86_64) 7 (Core)
            ```

        4. Modify the current kernel configuration to immediately disable THP:

            ```bash
            echo never > /sys/kernel/mm/transparent_hugepage/enabled
            echo never > /sys/kernel/mm/transparent_hugepage/defrag
            ```

        5. Configure the I/O Scheduler in the udev script:

            ```bash
            vi /etc/udev/rules.d/60-tidb-schedulers.rules
            ```

            ```
            ACTION=="add|change", SUBSYSTEM=="block", ENV{ID_SERIAL}=="36d0946606d79f90025f3e09a0c1fc035", ATTR{queue/scheduler}="noop"
            ACTION=="add|change", SUBSYSTEM=="block", ENV{ID_SERIAL}=="36d0946606d79f90025f3e09a0c1f9e81", ATTR{queue/scheduler}="noop"

            ```

        6. Apply the udev script:

            > **Note:**
            >
            > If your device uses the `noop` or `none` I/O Scheduler, skip this step. No udev rules configuration is needed.

            ```bash
            udevadm control --reload-rules
            udevadm trigger --type=devices --action=change
            ```

        7. Create a service to configure the CPU power policy:

            ```bash
            cat  >> /etc/systemd/system/cpupower.service << EOF
            [Unit]
            Description=CPU performance
            [Service]
            Type=oneshot
            ExecStart=/usr/bin/cpupower frequency-set --governor performance
            [Install]
            WantedBy=multi-user.target
            EOF
            ```

        8. Apply the CPU power policy configuration service:

            ```bash
            systemctl daemon-reload
            systemctl enable cpupower.service
            systemctl start cpupower.service
            ```

6. Execute the following command to verify the THP status:

    ```bash
    cat /sys/kernel/mm/transparent_hugepage/enabled
    ```

    ```
    always madvise [never]
    ```

7. Execute the following command to verify the I/O Scheduler of the disk where the data directory is located:

    ```bash
    cat /sys/block/sd[bc]/queue/scheduler
    ```

    ```
    [noop] deadline cfq
    [noop] deadline cfq
    ```

8. Execute the following command to see the power policy of the cpufreq module:

    ```bash
    cpupower frequency-info --policy
      ```

    ```
    analyzing CPU 0:
    current policy: frequency should be within 1.20 GHz and 3.10 GHz.
                  The governor "performance" may decide which speed to use within this range.
    ```

9. Execute the following commands to modify the `sysctl` parameters:

    {{< copyable "shell-regular" >}}

    ```bash
    echo "fs.file-max = 1000000">> /etc/sysctl.conf
    echo "net.core.somaxconn = 32768">> /etc/sysctl.conf
    echo "net.ipv4.tcp_syncookies = 0">> /etc/sysctl.conf
    echo "vm.overcommit_memory = 1">> /etc/sysctl.conf
    echo "vm.min_free_kbytes = 1048576">> /etc/sysctl.conf
    sysctl -p
    ```

    > **Warning:**
    >
    > It is not recommended to increase the value of `vm.min_free_kbytes` on systems with less than 16 GiB of memory, because it might cause instability and boot failures.

    > **Note:**
    >
    > - `vm.min_free_kbytes` is a Linux kernel parameter that controls the minimum amount of free memory reserved by the system, measured in KiB.
    > - The setting of `vm.min_free_kbytes` affects the memory reclaim mechanism. Setting it too large reduces the available memory, while setting it too small might cause memory request speeds to exceed background reclaim speeds, leading to memory reclamation and consequent delays in memory allocation.
    > - It is recommended to set `vm.min_free_kbytes` to `1048576` KiB (1 GiB) at least. If [NUMA is installed](https://docs.pingcap.com/tidb/stable/check-before-deployment#install-the-numactl-tool), it is recommended to set it to `number of NUMA nodes * 1048576` KiB.
    > - For systems running Linux kernel 4.11 or earlier, it is recommended to set `net.ipv4.tcp_tw_recycle = 0`.

10. Execute the following command to configure the user's `limits.conf` file:

    ```bash
    cat << EOF >>/etc/security/limits.conf
    tidb           soft    nofile          1000000
    tidb           hard    nofile          1000000
    tidb           soft    stack          32768
    tidb           hard    stack          32768
    EOF
    ```
