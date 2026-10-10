# Use the system native SSH client for DM cluster operations

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/maintain-dm-using-tiup.md`
- Source Title: `Maintain a DM Cluster Using TiUP`
- Source Heading Path: `Maintain a DM Cluster Using TiUP > Use the system's native SSH client to connect to cluster`
- Source Line Ranges: `387-416`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`
- Topic Tags: `native-ssh`, `ssh`, `authentication`, `environment-variables`, `deployment`, `upgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0088_e2b447463f`
- Source ID: `tidb-docs-8.1:dm/maintain-dm-using-tiup.md#use-the-system-s-native-ssh-client-to-connect-to-cluster`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0669bef810c7f9b967682d060ea82a94c19a02ef2ed85b2e55dc6b195be970a4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/maintain-dm-using-tiup#use-the-system-s-native-ssh-client-to-connect-to-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/maintain-dm-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when you need to enable the control machine's native SSH client for TiUP DM cluster operations or set the related environment variable.
- Retrieval Keywords: --native-ssh, TIUP_NATIVE_SSH, Use the system's native SSH client to connect to cluster, tiup dm deploy <cluster-name> <version> <topo> --native-ssh, tiup dm start <cluster-name> --native-ssh, tiup dm upgrade ... --native-ssh, export TIUP_NATIVE_SSH=true, export TIUP_NATIVE_SSH=1, export TIUP_NATIVE_SSH=enable, sshpass, timeout error, SSH plug-in for authentication, customized SSH client
- Follow-up Guidance: The source states that `--native-ssh` can be added to cluster operation commands, `TIUP_NATIVE_SSH` can enable local SSH client usage by environment variable, and `--native-ssh` has higher priority if both are specified.
- Classification Note: This is classified as a configuration topic because the content describes SSH client selection through the `--native-ssh` flag and the `TIUP_NATIVE_SSH` environment variable.

## Official Source Content

## Use the system's native SSH client to connect to cluster

All operations above performed on the cluster machine use the SSH client embedded in TiUP to connect to the cluster and execute commands. However, in some scenarios, you might also need to use the SSH client native to the control machine system to perform such cluster operations. For example:

- To use an SSH plug-in for authentication
- To use a customized SSH client

Then you can use the `--native-ssh` command-line flag to enable the system-native command-line tool:

- Deploy a cluster: `tiup dm deploy <cluster-name> <version> <topo> --native-ssh`. Fill in the name of your cluster for `<cluster-name>`,  the DM version to be deployed (such as `v8.1.2`) for `<version>` , and the topology file name for `<topo>`.
- Start a cluster: `tiup dm start <cluster-name> --native-ssh`.
- Upgrade a cluster: `tiup dm upgrade ... --native-ssh`

You can add `--native-ssh` in all cluster operation commands above to use the system's native SSH client.

To avoid adding such a flag in every command, you can use the `TIUP_NATIVE_SSH` system variable to specify whether to use the local SSH client:

```sh
export TIUP_NATIVE_SSH=true
# or
export TIUP_NATIVE_SSH=1
# or
export TIUP_NATIVE_SSH=enable
```

If you specify this environment variable and `--native-ssh` at the same time, `--native-ssh` has higher priority.

> **Note:**
>
> During the process of cluster deployment, if you need to use a password for connection or `passphrase` is configured in the key file, you must ensure that `sshpass` is installed on the control machine; otherwise, a timeout error is reported.
