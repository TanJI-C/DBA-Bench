# Pre-deployment host storage, swap, and temporary space preparation

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/check-before-deployment.md`
- Source Title: `TiDB Environment and System Configuration Check`
- Source Heading Path: `TiDB Environment and System Configuration Check | TiDB Environment and System Configuration Check > Mount the data disk ext4 filesystem with options on the target machines that deploy TiKV | TiDB Environment and System Configuration Check > Check and disable system swap | TiDB Environment and System Configuration Check > Set temporary spaces for TiDB instances (Recommended)`
- Source Line Ranges: `5-171`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiup`
- Topic Tags: `precheck`, `filesystem`, `ext4`, `mount-options`, `swap`, `memory`, `oom`, `temporary-storage`, `permissions`, `fast-online-ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0017_8a0a74611c`
- Source ID: `tidb-docs-8.1:check-before-deployment.md#tidb-environment-and-system-configuration-check`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d95a05dad73d03c1cbf78151ad15aebec26bf1327fcfebfd69d3ac09f7b0464d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/check-before-deployment#tidb-environment-and-system-configuration-check
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/check-before-deployment.md

## Retrieval Guidance

- Use When: Use this chunk when preparing self-managed TiDB hosts and you need the documented pre-deployment checks for TiKV ext4 mount options, swap handling, and TiDB temporary directories and permissions.
- Retrieval Keywords: nodelalloc, noatime, ext4, NVMe SSD, TiKV data disk, TiUP deployment cannot pass the precheck, /etc/fstab, mount -t ext4, Check and disable system swap, vm.swappiness = 0, swapoff -a && swapon -a, OOM issues, tmp-storage-path, temp-dir, tidb_ddl_enable_fast_reorg, Fast Online DDL, /tmp/tidb, temporary files, read and write permissions
- Follow-up Guidance: The content includes example commands for partitioning and formatting `/dev/nvme0n1`, editing `/etc/fstab`, adjusting `vm.swappiness`, and creating or granting permissions on `/data/tidb-deploy/tempdir`.
- Classification Note: This is classified as configuration because the official content describes required and recommended host filesystem, swap, and temporary directory settings before deployment.

## Official Source Content

# TiDB Environment and System Configuration Check

This document describes the environment check operations before deploying TiDB. The following steps are ordered by priorities.
## Mount the data disk ext4 filesystem with options on the target machines that deploy TiKV

For production deployments, it is recommended to use NVMe SSD of EXT4 filesystem to store TiKV data. This configuration is the best practice, whose reliability, security, and stability have been proven in a large number of online scenarios.

Log in to the target machines using the `root` user account.

Format your data disks to the ext4 filesystem and add the `nodelalloc` and `noatime` mount options to the filesystem. It is required to add the `nodelalloc` option, or else the TiUP deployment cannot pass the precheck. The `noatime` option is optional.

> **Note:**
>
> If your data disks have been formatted to ext4 and have added the mount options, you can uninstall it by running the `umount /dev/nvme0n1p1` command, skip directly to the fifth step below to edit the `/etc/fstab` file, and add the options again to the filesystem.

Take the `/dev/nvme0n1` data disk as an example:

1. View the data disk.

    ```bash
    fdisk -l
    ```

    ```
    Disk /dev/nvme0n1: 1000 GB
    ```

2. Create the partition.

    ```bash
    parted -s -a optimal /dev/nvme0n1 mklabel gpt -- mkpart primary ext4 1 -1
    ```

    For large NVMe devices, you can create multiple partitions:

    ```bash
    parted -s -a optimal /dev/nvme0n1 mklabel gpt -- mkpart primary ext4 1 2000GB
    parted -s -a optimal /dev/nvme0n1 -- mkpart primary ext4 2000GB -1
    ```

    > **Note:**
    >
    > Use the `lsblk` command to view the device number of the partition: for a NVMe disk, the generated device number is usually `nvme0n1p1`; for a regular disk (for example, `/dev/sdb`), the generated device number is usually `sdb1`.

3. Format the data disk to the ext4 filesystem.

    ```bash
    mkfs.ext4 /dev/nvme0n1p1
    ```

4. View the partition UUID of the data disk.

    In this example, the UUID of nvme0n1p1 is `c51eb23b-195c-4061-92a9-3fad812cc12f`.

    ```bash
    lsblk -f
    ```

    ```
    NAME    FSTYPE LABEL UUID                                 MOUNTPOINT
    sda
    ├─sda1  ext4         237b634b-a565-477b-8371-6dff0c41f5ab /boot
    ├─sda2  swap         f414c5c0-f823-4bb1-8fdf-e531173a72ed
    └─sda3  ext4         547909c1-398d-4696-94c6-03e43e317b60 /
    sr0
    nvme0n1
    └─nvme0n1p1 ext4         c51eb23b-195c-4061-92a9-3fad812cc12f
    ```

5. Edit the `/etc/fstab` file and add the `nodelalloc` mount options.

    ```bash
    vi /etc/fstab
    ```

    ```
    UUID=c51eb23b-195c-4061-92a9-3fad812cc12f /data1 ext4 defaults,nodelalloc,noatime 0 2
    ```

6. Mount the data disk.

    ```bash
    mkdir /data1 && \
    systemctl daemon-reload && \
    mount -a
    ```

7. Check using the following command.

    ```bash
    mount -t ext4
    ```

    ```
    /dev/nvme0n1p1 on /data1 type ext4 (rw,noatime,nodelalloc,data=ordered)
    ```

    If the filesystem is ext4 and `nodelalloc` is included in the mount options, you have successfully mount the data disk ext4 filesystem with options on the target machines.
## Check and disable system swap

TiDB needs a sufficient amount of memory for operation. If the memory that TiDB uses gets swapped out and later gets swapped back in, this can cause latency spikes. If you want to maintain stable performance, it is recommended that you permanently disable the system swap, but it might trigger OOM issues when there is insufficient memory. If you want to avoid such OOM issues, you can just decrease the swap priority, instead of permanently disabling it.

- Enabling and using swap might introduce performance jitter issues. It is recommended that you permanently disable the operating system tier swap for low-latency and stability-critical database services. To permanently disable swap, you can use the following method:

    - During the initialization phase of the operating system, do not partition the swap partition disk separately.
    - If you have already partitioned a separate swap partition disk during the initialization phase of the operating system and enabled swap, run the following command to disable it:

        ```bash
        echo "vm.swappiness = 0">> /etc/sysctl.conf
        sysctl -p
        swapoff -a && swapon -a
        ```

- If the host memory is insufficient, disabling the system swap might be more likely to trigger OOM issues. You can run the following command to decrease the swap priority instead of disabling it permanently:

    ```bash
    echo "vm.swappiness = 0">> /etc/sysctl.conf
    sysctl -p
    ```
## Set temporary spaces for TiDB instances (Recommended)

Some operations in TiDB require writing temporary files to the server, so it is necessary to ensure that the operating system user that runs TiDB has sufficient permissions to read and write to the target directory. If you do not start the TiDB instance with the `root` privilege, you need to check the directory permissions and set them correctly.

- TiDB work area

    Operations that consume a significant amount of memory, such as hash table construction and sorting, might write temporary data to disk to reduce memory consumption and improve stability. The disk location for writing is defined by the configuration item [`tmp-storage-path`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tmp-storage-path). With the default configuration, make sure that the user that runs TiDB has read and write permissions to the temporary folder (usually `/tmp`) of the operating system.

- `Fast Online DDL` work area

    When the variable [`tidb_ddl_enable_fast_reorg`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_enable_fast_reorg-new-in-v630) is set to `ON` (the default value in v6.5.0 and later versions), `Fast Online DDL` is enabled, and some DDL operations need to read and write temporary files in filesystems. The location is defined by the configuration item [`temp-dir`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#temp-dir-new-in-v630). You need to ensure that the user that runs TiDB has read and write permissions for that directory of the operating system. The default directory `/tmp/tidb` uses tmpfs (temporary file system). It is recommended to explicitly specify a disk directory. The following uses `/data/tidb-deploy/tempdir` as an example:

    > **Note:**
    > 
    > If DDL operations on large objects exist in your application, it is highly recommended to configure an independent large file system for [`temp-dir`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#temp-dir-new-in-v630).

    ```shell
    sudo mkdir -p /data/tidb-deploy/tempdir
    ```

    If the `/data/tidb-deploy/tempdir` directory already exists, make sure the write permission is granted.

    ```shell
    sudo chmod -R 777 /data/tidb-deploy/tempdir
    ```

    > **Note:**
    >
    > If the directory does not exist, TiDB will automatically create it upon startup. If the directory creation fails or TiDB does not have the read and write permissions for that directory, [`Fast Online DDL`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_enable_fast_reorg-new-in-v630) will be disabled during runtime.
