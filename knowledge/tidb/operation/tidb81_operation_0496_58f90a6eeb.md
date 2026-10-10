# Check items for TiUP cluster environment validation

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-cluster-check.md`
- Source Title: `tiup cluster check`
- Source Heading Path: `tiup cluster check | tiup cluster check > List of check items | tiup cluster check > List of check items > Operating system version | tiup cluster check > List of check items > CPU EPOLLEXCLUSIVE | tiup cluster check > List of check items > numactl | tiup cluster check > List of check items > System time | tiup cluster check > List of check items > System time zone | tiup cluster check > List of check items > Time synchronization service | tiup cluster check > List of check items > Swap partitioning | tiup cluster check > List of check items > Kernel parameters | tiup cluster check > List of check items > Transparent Huge Pages (THP) | tiup cluster check > List of check items > System limits | tiup cluster check > List of check items > SELinux | tiup cluster check > List of check items > Firewall | tiup cluster check > List of check items > irqbalance | tiup cluster check > List of check items > Disk mount options | tiup cluster check > List of check items > Port usage | tiup cluster check > List of check items > CPU core number | tiup cluster check > List of check items > Memory size | tiup cluster check > List of check items > Fio disk performance test`
- Source Line Ranges: `5-122`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`, `tidb`, `tikv`, `pd`
- Topic Tags: `precheck`, `environment-validation`, `os-version`, `kernel-parameters`, `time-sync`, `swap`, `thp`, `selinux`, `firewall`, `ports`, `cpu`, `memory`, `disk-performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0496_58f90a6eeb`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-cluster-check.md#tiup-cluster-check`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d67aa77f30b16eae4cde7f65e3c13d0c27b137370ec6643adb37941dd375a0c3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-check#tiup-cluster-check
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-cluster-check.md

## Retrieval Guidance

- Use When: Use this chunk when identifying what environment validation items `tiup cluster check` covers before a TiDB cluster goes live or when interpreting checks related to OS, time, swap, THP, SELinux, firewall, ports, CPU, memory, or disk performance.
- Retrieval Keywords: tiup cluster check, List of check items, Operating system version, CPU EPOLLEXCLUSIVE, numactl, System time, 500 ms, System time zone, Time synchronization service, ntpd, Swap partitioning, Kernel parameters, net.ipv4.tcp_tw_recycle, net.ipv4.tcp_syncookies, net.core.somaxconn, vm.swappiness, vm.overcommit_memory, fs.file-max, Transparent Huge Pages, THP, /etc/security/limits.conf, soft nofile 1000000, hard nofile 1000000, soft stack 10240, SELinux, getenforce, /etc/selinux/config, FirewallD, irqbalance, Disk mount options, nodelalloc, noatime, Port usage, CPU core number, -enable-cpu, Memory size, -enable-mem, Fio disk performance test, data_dir, fio_randread_write_latency, fio_randread_write, fio_randread, -enable-disk
- Follow-up Guidance: The content notes that port usage check assumes the cluster is not started yet, and that CPU core number, memory size, and fio disk performance test are not checked by default unless `-enable-cpu`, `-enable-mem`, or `-enable-disk` is added.
- Classification Note: This is classified as an operation chunk because it lists the runtime environment and host validation checks performed by `tiup cluster check` for cluster preparation and normal operation.

## Official Source Content

# tiup cluster check

For a formal production environment, before the environment goes live, you need to perform a series of checks to ensure the clusters are in their best performance. To simplify the manual check steps, TiUP Cluster provides the `check` command to check whether the hardware and software environments of the target machines of a specified cluster meet the requirements to work normally.
## List of check items
### Operating system version

Check the operating system distribution and version of the deployed machines. For a list of supported versions, see [OS and platform requirements](https://docs.pingcap.com/tidb/stable/hardware-and-software-requirements#os-and-platform-requirements).
### CPU EPOLLEXCLUSIVE

Check whether the CPU of the target machine supports EPOLLEXCLUSIVE.
### numactl

Check whether `numactl` is installed on the target machine. If tied cores are configured on the target machine, you must install `numactl`.
### System time

Check whether the system time of the target machine is synchronized. Compare the system time of the target machine with that of the central control machine, and report an error if the deviation exceeds a certain threshold (500 ms).
### System time zone

Check whether the system time zone of the target machines is synchronized. Compare the time zone configuration of these machines and report an error if the time zone is inconsistent.
### Time synchronization service

Check whether the time synchronization service is configured on the target machine. Namely, check whether ntpd is running.
### Swap partitioning

Check whether swap partitioning is enabled on the target machine. It is recommended to disable swap partitioning.
### Kernel parameters

Check the values of the following kernel parameters:

- `net.ipv4.tcp_tw_recycle`: 0
- `net.ipv4.tcp_syncookies`: 0
- `net.core.somaxconn`: 32768
- `vm.swappiness`: 0
- `vm.overcommit_memory`: 0 or 1
- `fs.file-max`: 1000000
### Transparent Huge Pages (THP)

Check whether THP is enabled on the target machine. It is recommended to disable THP.
### System limits

Check the limit values in the `/etc/security/limits.conf` file:

```
<deploy-user> soft nofile 1000000
<deploy-user> hard nofile 1000000
<deploy-user> soft stack 10240
```

`<deploy-user>` is the user who deploys and runs the TiDB cluster, and the last column is the minimum value required for the system.
### SELinux

SELinux must be disabled or set to permissive mode. To check the current status, use the [getenforce(8)](https://linux.die.net/man/8/getenforce) utility.

If SELinux is not disabled, open the `/etc/selinux/config` file, locate the line starting with `SELINUX=`, and change it to `SELINUX=disabled`. After making this change, you need to reboot the system because switching from `enforcing` or `permissive` to `disabled` does not take effect without a reboot.

On some systems (such as Ubuntu), the `/etc/selinux/config` file might not exist, and the getenforce utility might not be installed. In that case, you can skip this step.
### Firewall

Check whether the FirewallD service is enabled. It is recommended to either disable the FirewallD service or add permission rules for each service in the TiDB cluster.
### irqbalance

Check whether the irqbalance service is enabled. It is recommended to enable the irqbalance service.
### Disk mount options

Check the mount options for ext4 partitions. Make sure the mount options include the nodelalloc option and the noatime option.
### Port usage

Check if the ports defined in the topology (including the auto-completion default ports) are already used by the processes on the target machine.

> **Note:**
>
> The port usage check assumes that a cluster is not started yet. If a cluster is already deployed and started, the port usage check on the cluster fails because the ports must be in use in this case.
### CPU core number

Check the CPU information of the target machine. For a production cluster, it is recommended that the number of the CPU logical core is greater than or equal to 16.

> **Note:**
>
> CPU core number is not checked by default. To enable the check, you need to add the `-enable-cpu` option to the command.
### Memory size

Check the memory size of the target machine. For a production cluster, it is recommended that the total memory capacity is greater than or equal to 32GB.

> **Note:**
>
> Memory size is not checked by default. To enable the check, you need to add the `-enable-mem` option to the command.
### Fio disk performance test

Use flexible I/O tester (fio) to test the performance of the disk where `data_dir` is located, including the following three test items:

- fio_randread_write_latency
- fio_randread_write
- fio_randread

> **Note:**
>
> The fio disk performance test is not performed by default. To perform the test, you need to add the `-enable-disk` option to the command.
