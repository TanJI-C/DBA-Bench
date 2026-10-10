# Check remediation, cluster operations, and FAQ for TiUP no-sudo mode

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster-no-sudo-mode.md`
- Source Title: `Deploy and Maintain an Online TiDB Cluster Using TiUP No-sudo Mode`
- Source Heading Path: `Deploy and Maintain an Online TiDB Cluster Using TiUP No-sudo Mode > Manually repair failed check items | Deploy and Maintain an Online TiDB Cluster Using TiUP No-sudo Mode > Deploy and manage the cluster | Deploy and Maintain an Online TiDB Cluster Using TiUP No-sudo Mode > FAQ | Deploy and Maintain an Online TiDB Cluster Using TiUP No-sudo Mode > FAQ > The `Trying to run as user instance, but $XDG_RUNTIME_DIR is not set.` error occurs when starting user@.service`
- Source Line Ranges: `115-190`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`, `tidb`, `tikv`, `pd`
- Topic Tags: `cluster-check`, `manual-remediation`, `deploy`, `start`, `scale-out`, `scale-in`, `upgrade`, `pam_systemd`, `troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0488_17e84c90c4`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster-no-sudo-mode.md#manually-repair-failed-check-items`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `40dc860bc3b6d75439c220c80b936a81cb8f28702f5a06d7b4e8157f447e9e46`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-no-sudo-mode#manually-repair-failed-check-items
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster-no-sudo-mode.md

## Retrieval Guidance

- Use When: Use this chunk when checking, manually repairing, deploying, starting, scaling, upgrading, or troubleshooting a TiUP no-sudo cluster after topology preparation.
- Retrieval Keywords: tiup cluster check topology.yaml --user tidb, tiup cluster check --apply --user tidb, Manually repair failed check items, tar package, THP is enabled, service firewalld is running but should be stopped, same partition as data dir, tiup cluster deploy mycluster v8.5.0 topology.yaml --user tidb, tiup cluster start mycluster, tiup cluster scale-out mycluster scale.yaml --user tidb, tiup cluster scale-in mycluster -N 192.168.124.27:20160, tiup cluster upgrade mycluster v8.2.0, Trying to run as user instance, but $XDG_RUNTIME_DIR is not set., pam_systemd.so, /etc/pam.d/system-auth.ued
- Follow-up Guidance: The FAQ says the $XDG_RUNTIME_DIR error when starting user@.service might be caused by missing pam_systemd.so in /etc/pam.d/system-auth.ued and provides a grep command to check or append it.
- Classification Note: This is classified as operation because the content covers cluster check results, manual remediation limits in no-sudo mode, lifecycle commands such as deploy/start/scale/upgrade, and a troubleshooting FAQ.

## Official Source Content

## Manually repair failed check items

> **Note:**
>
> If you use a minimal install, make sure the `tar` package is installed. Otherwise, the `tiup cluster check` command will fail.

Executing `tiup cluster check topology.yaml --user tidb` can generate some failed check items. The following is an example.

```shell
Node            Check         Result  Message
----            -----         ------  -------
192.168.124.27  thp           Fail    THP is enabled, please disable it for best performance
192.168.124.27  command       Pass    numactl: policy: default
192.168.124.27  os-version    Pass    OS is CentOS Stream 8 
192.168.124.27  network       Pass    network speed of ens160 is 10000MB
192.168.124.27  disk          Warn    mount point / does not have 'noatime' option set
192.168.124.27  disk          Fail    multiple components tikv:/home/blackcat/data/tidb-deploy/tikv-20160/data/tidb-data,tikv:/home/blackcat/data/tidb-deploy/tikv-20161/data/tidb-data are using the same partition 192.168.124.27:/ as data dir
192.168.124.27  selinux       Pass    SELinux is disabled
192.168.124.27  cpu-cores     Pass    number of CPU cores / threads: 16
192.168.124.27  cpu-governor  Warn    Unable to determine current CPU frequency governor policy
192.168.124.27  swap          Warn    swap is enabled, please disable it for best performance
192.168.124.27  memory        Pass    memory size is 9681MB
192.168.124.27  service       Fail    service firewalld is running but should be stopped
```

In no-sudo mode, the `tidb` user does not have sudo permissions. As a result, running `tiup cluster check topology.yaml --apply --user tidb` cannot automatically fix the failed check items. You need to manually fix it by using the `root` user on the target machines.

For more information, see [TiDB Environment and System Configuration Check](https://docs.pingcap.com/tidb/stable/check-before-deployment). Note that you need to skip the step [Manually configure the SSH mutual trust and sudo without password](https://docs.pingcap.com/tidb/stable/check-before-deployment#manually-configure-the-ssh-mutual-trust-and-sudo-without-password) in the document.
## Deploy and manage the cluster

To use the `tidb` user created in preceding steps and avoid creating a new one, add `--user tidb` when running the following `deploy` command:

```shell
tiup cluster deploy mycluster v8.5.0 topology.yaml --user tidb
```

> **Note:**
>
> You need to replace `v8.5.0` in the preceding command with the TiDB version that you want to deploy and `mycluster` with the name you want to give to your cluster.

Start the cluster:

```shell
tiup cluster start mycluster
```

Scale out the cluster:

```shell
tiup cluster scale-out mycluster scale.yaml --user tidb
```

Scale in the cluster:

```shell
tiup cluster scale-in mycluster -N 192.168.124.27:20160
```

Upgrade the cluster:

```shell
tiup cluster upgrade mycluster v8.2.0
```
## FAQ
### The `Trying to run as user instance, but $XDG_RUNTIME_DIR is not set.` error occurs when starting user@.service

This issue might be caused by the absence of `pam_systemd.so` in your `/etc/pam.d/system-auth.ued` file.

To resolve this issue, use the following command to check whether the `/etc/pam.d/system-auth.ued` file contains the `pam_systemd.so` module. If not, append `session optional pam_systemd.so` to the end of the file.

```shell
grep 'pam_systemd.so' /etc/pam.d/system-auth.ued || echo 'session     optional      pam_systemd.so' >> /etc/pam.d/system-auth.ued
```
