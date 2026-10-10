# Host access prerequisites NUMA tool and SELinux settings

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/check-before-deployment.md`
- Source Title: `TiDB Environment and System Configuration Check`
- Source Heading Path: `TiDB Environment and System Configuration Check > Manually configure the SSH mutual trust and sudo without password | TiDB Environment and System Configuration Check > Install the `numactl` tool | TiDB Environment and System Configuration Check > Disable SELinux`
- Source Line Ranges: `790-887`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiup`, `tidb`, `tikv`
- Topic Tags: `ssh`, `sudo`, `mutual-trust`, `numactl`, `numa`, `selinux`, `prerequisites`, `host-preparation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0028_1acb8f076b`
- Source ID: `tidb-docs-8.1:check-before-deployment.md#manually-configure-the-ssh-mutual-trust-and-sudo-without-password`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9d96cde0063a7923a63b6b3651d31df603c0e1a7447f25f5441f6946ff003e88`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/check-before-deployment#manually-configure-the-ssh-mutual-trust-and-sudo-without-password
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/check-before-deployment.md

## Retrieval Guidance

- Use When: Use this chunk when preparing self-managed hosts for TiDB with manual SSH mutual trust, passwordless sudo for the tidb user, numactl installation, and SELinux status requirements.
- Retrieval Keywords: SSH mutual trust and sudo without password, useradd tidb, visudo, tidb ALL=(ALL) NOPASSWD: ALL, ssh-keygen -t rsa, ssh-copy-id -i ~/.ssh/id_rsa.pub 10.0.1.1, ssh 10.0.1.1, sudo -su root, Install the numactl tool, yum -y install numactl, tiup cluster exec tidb-test --sudo --command "yum -y install numactl", tiup cluster exec --help, Disable SELinux, getenforce, /etc/selinux/config, SELINUX=disabled, reboot the system, permissive mode
- Follow-up Guidance: The chunk notes that TiUP deployment automatically configures SSH mutual trust and login without password, and that some systems such as Ubuntu might not have /etc/selinux/config or getenforce so the SELinux step can be skipped there.
- Classification Note: This is classified as operation because the content covers host preparation procedures and prerequisite checks, including access setup, package installation, and SELinux state handling.

## Official Source Content

## Manually configure the SSH mutual trust and sudo without password

This section describes how to manually configure the SSH mutual trust and sudo without password. It is recommended to use TiUP for deployment, which automatically configure SSH mutual trust and login without password. If you deploy TiDB clusters using TiUP, ignore this section.

1. Log in to the target machine respectively using the `root` user account, create the `tidb` user and set the login password.

    ```bash
    useradd tidb && \
    passwd tidb
    ```

2. To configure sudo without password, run the following command, and add `tidb ALL=(ALL) NOPASSWD: ALL` to the end of the file:

    ```bash
    visudo
    ```

    ```
    tidb ALL=(ALL) NOPASSWD: ALL
    ```

3. Use the `tidb` user to log in to the control machine, and run the following command. Replace `10.0.1.1` with the IP of your target machine, and enter the `tidb` user password of the target machine as prompted. After the command is executed, SSH mutual trust is already created. This applies to other machines as well. Newly created `tidb` users do not have the `.ssh` directory. To create such a directory, execute the command that generates the RSA key. To deploy TiDB components on the control machine, configure mutual trust for the control machine and the control machine itself.

    ```bash
    ssh-keygen -t rsa
    ssh-copy-id -i ~/.ssh/id_rsa.pub 10.0.1.1
    ```

4. Log in to the control machine using the `tidb` user account, and log in to the IP of the target machine using `ssh`. If you do not need to enter the password and can successfully log in, then the SSH mutual trust is successfully configured.

    ```bash
    ssh 10.0.1.1
    ```

    ```
    [tidb@10.0.1.1 ~]$
    ```

5. After you log in to the target machine using the `tidb` user, run the following command. If you do not need to enter the password and can switch to the `root` user, then sudo without password of the `tidb` user is successfully configured.

    ```bash
    sudo -su root
    ```

    ```
    [root@10.0.1.1 tidb]#
    ```
## Install the `numactl` tool

This section describes how to install the NUMA tool. In online environments, because the hardware configuration is usually higher than required, to better plan the hardware resources, multiple instances of TiDB or TiKV can be deployed on a single machine. In such scenarios, you can use NUMA tools to prevent the competition for CPU resources which might cause reduced performance.

> **Note:**
>
> - Binding cores using NUMA is a method to isolate CPU resources and is suitable for deploying multiple instances on highly configured physical machines.
> - After completing deployment using `tiup cluster deploy`, you can use the `exec` command to perform cluster level management operations.

To install the NUMA tool, take either of the following two methods:

**Method 1**: Log in to the target node to install NUMA. Take CentOS Linux release 7.7.1908 (Core) as an example.

```bash
sudo yum -y install numactl
```

**Method 2**: Install NUMA on an existing cluster in batches by running the `tiup cluster exec` command.

1. Follow [Deploy a TiDB Cluster Using TiUP](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup) to deploy a cluster `tidb-test`. If you have installed a TiDB cluster, you can skip this step.

    ```bash
    tiup cluster deploy tidb-test v6.1.0 ./topology.yaml --user root [-p] [-i /home/root/.ssh/gcp_rsa]
    ```

2. Run the `tiup cluster exec` command using the `sudo` privilege to install NUMA on all the target machines in the `tidb-test` cluster:

    ```bash
    tiup cluster exec tidb-test --sudo --command "yum -y install numactl"
    ```

    To get help information of the `tiup cluster exec` command, run the `tiup cluster exec --help` command.
## Disable SELinux

SELinux must be disabled or set to permissive mode. To check the current status, use the [getenforce(8)](https://linux.die.net/man/8/getenforce) utility.

If SELinux is not disabled, open the `/etc/selinux/config` file, locate the line starting with `SELINUX=`, and change it to `SELINUX=disabled`. After making this change, you need to reboot the system because switching from `enforcing` or `permissive` to `disabled` does not take effect without a reboot.

On some systems (such as Ubuntu), the `/etc/selinux/config` file might not exist, and the getenforce utility might not be installed. In that case, you can skip this step.
