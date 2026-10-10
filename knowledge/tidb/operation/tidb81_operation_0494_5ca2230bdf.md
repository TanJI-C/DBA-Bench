# Native SSH, control machine migration, and TiUP metadata backup

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster.md`
- Source Title: `Deploy and Maintain an Online TiDB Cluster Using TiUP`
- Source Heading Path: `Deploy and Maintain an Online TiDB Cluster Using TiUP > Use the system's native SSH client to connect to cluster | Deploy and Maintain an Online TiDB Cluster Using TiUP > Migrate control machine and back up TiUP data | Deploy and Maintain an Online TiDB Cluster Using TiUP > Back up and restore meta files for cluster deployment and O&M`
- Source Line Ranges: `699-761`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `ssh`, `native-ssh`, `authentication`, `control-machine`, `migration`, `backup`, `metadata`, `restore`, `path`, `sshpass`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0494_5ca2230bdf`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster.md#use-the-system-s-native-ssh-client-to-connect-to-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c2380727f9ee48905a78867cfb56c4e8e9bd9d8513110885478323537475bd8a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster#use-the-system-s-native-ssh-client-to-connect-to-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster.md

## Retrieval Guidance

- Use When: Use this content when looking for TiUP cluster operations with the system native SSH client, control machine migration by copying `.tiup`, or TiUP cluster meta backup and restore commands.
- Retrieval Keywords: --ssh=system, TIUP_NATIVE_SSH, tiup cluster deploy <cluster-name> <version> <topo> --ssh=system, tiup cluster start <cluster-name> --ssh=system, tiup cluster upgrade ... --ssh=system, system native SSH client, sshpass, timeout error, passphrase, Migrate control machine, backup TiUP data, .tiup directory, tar czvf tiup.tar.gz .tiup, export PATH=/home/tidb/.tiup/bin:$PATH, tiup cluster meta backup ${cluster_name}, tiup cluster meta restore ${cluster_name} ${backup_file}, meta files used for operation and maintenance
- Follow-up Guidance: The content notes that `--ssh` has higher priority than `TIUP_NATIVE_SSH`, and that restoring meta files overwrites the current meta files.
- Classification Note: This is classified as an operation topic for the TiUP component because it covers SSH behavior for cluster commands, control machine data migration, and backup or restore of TiUP cluster metadata.

## Official Source Content

## Use the system's native SSH client to connect to cluster

All operations above performed on the cluster machine use the SSH client embedded in TiUP to connect to the cluster and execute commands. However, in some scenarios, you might also need to use the SSH client native to the control machine system to perform such cluster operations. For example:

- To use an SSH plug-in for authentication
- To use a customized SSH client

Then you can use the `--ssh=system` command-line flag to enable the system-native command-line tool:

- Deploy a cluster: `tiup cluster deploy <cluster-name> <version> <topo> --ssh=system`. Fill in the name of your cluster for `<cluster-name>`, the TiDB version to be deployed (such as `v8.1.2`) for `<version>`, and the topology file for `<topo>`.
- Start a cluster: `tiup cluster start <cluster-name> --ssh=system`
- Upgrade a cluster: `tiup cluster upgrade ... --ssh=system`

You can add `--ssh=system` in all cluster operation commands above to use the system's native SSH client.

To avoid adding such a flag in every command, you can use the `TIUP_NATIVE_SSH` system variable to specify whether to use the local SSH client:

```shell
export TIUP_NATIVE_SSH=true
# or
export TIUP_NATIVE_SSH=1
# or
export TIUP_NATIVE_SSH=enable
```

If you specify this environment variable and `--ssh` at the same time, `--ssh` has higher priority.

> **Note:**
>
> During the process of cluster deployment, if you need to use a password for connection (`-p`) or `passphrase` is configured in the key file, you must ensure that `sshpass` is installed on the control machine; otherwise, a timeout error is reported.
## Migrate control machine and back up TiUP data

The TiUP data is stored in the `.tiup` directory in the user's home directory. To migrate the control machine, you can take the following steps to copy the `.tiup` directory to the corresponding target machine:

1. Execute `tar czvf tiup.tar.gz .tiup` in the home directory of the original machine.
2. Copy `tiup.tar.gz` to the home directory of the target machine.
3. Execute `tar xzvf tiup.tar.gz` in the home directory of the target machine.
4. Add the `.tiup` directory to the `PATH` environment variable.

    If you use `bash` and you are a `tidb` user, you can add `export PATH=/home/tidb/.tiup/bin:$PATH` in `~/.bashrc` and execute `source ~/.bashrc`. Then make corresponding adjustments according to the shell and the user you use.

> **Note:**
>
> It is recommended that you back up the `.tiup` directory regularly to avoid the loss of TiUP data caused by abnormal conditions, such as disk damage of the control machine.
## Back up and restore meta files for cluster deployment and O&M

If the meta files used for operation and maintenance (O&M) are lost, managing the cluster using TiUP will fail. It is recommended that you back up the meta files regularly by running the following command:

```bash
tiup cluster meta backup ${cluster_name}
```

If the meta files are lost, you can restore them by running the following command:

```bash
tiup cluster meta restore ${cluster_name} ${backup_file}
```

> **Note:**
>
> The restore operation overwrites the current meta files. Therefore, it is recommended to restore the meta files only when they are lost.
