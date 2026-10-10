# Patch DM components with a temporary package

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/maintain-dm-using-tiup.md`
- Source Title: `Maintain a DM Cluster Using TiUP`
- Source Heading Path: `Maintain a DM Cluster Using TiUP > Update component`
- Source Line Ranges: `225-270`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`
- Topic Tags: `patch`, `component-update`, `hotfix`, `restart`, `node-selection`, `role-selection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0118_8021fc4725`
- Source ID: `tidb-docs-8.1:dm/maintain-dm-using-tiup.md#update-component`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1e563f3e940c6203514b4bd32ac867a6c65903c4066caff80e42d031a565add3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/maintain-dm-using-tiup#update-component
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/maintain-dm-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiUP DM command syntax for replacing a running DM component with a temporary package and restarting the service.
- Retrieval Keywords: tiup dm patch, Replace the remote package with a specified package and restart the service, --overwrite, --transfer-timeout, -N, --node, -R, --role, dm-master hotfix package, /tmp/dm-master-hotfix.tar.gz, tiup dm patch prod-cluster /tmp/dm-master-hotfix.tar.gz -R dm-master, tiup dm patch prod-cluster /tmp/dm--hotfix.tar.gz -N 172.16.4.5:8261
- Follow-up Guidance: The source also shows examples for patching all DM-master instances with `-R dm-master` or only one node with `-N 172.16.4.5:8261`.
- Classification Note: This is classified as an operation because the content describes using the `tiup dm patch` command to update running DM components with a temporary package.

## Official Source Content

## Update component

For normal upgrade, you can use the `upgrade` command. But in some scenarios, such as debugging, you might need to replace the currently running component with a temporary package. To achieve this, use the `patch` command:

```bash
tiup dm patch --help
```

```
Replace the remote package with a specified package and restart the service

Usage:
  tiup dm patch <cluster-name> <package-path> [flags]

Flags:
  -h, --help                   help for patch
  -N, --node strings           Specify the nodes
      --overwrite              Use this package in the future scale-out operations
  -R, --role strings           Specify the role
      --transfer-timeout int   Timeout in seconds when transferring dm-master leaders (default 600)

Global Flags:
      --native-ssh         Use the native SSH client installed on local system instead of the build-in one.
      --ssh-timeout int    Timeout in seconds to connect host via SSH, ignored for operations that don't need an SSH connection. (default 5)
      --wait-timeout int   Timeout in seconds to wait for an operation to complete, ignored for operations that don't fit. (default 60)
  -y, --yes                Skip all confirmations and assumes 'yes'
```

If a DM-master hotfix package is in `/tmp/dm-master-hotfix.tar.gz` and you want to replace all the DM-master packages in the cluster, run the following command:

```bash
tiup dm patch prod-cluster /tmp/dm-master-hotfix.tar.gz -R dm-master
```

You can also replace only one DM-master package in the cluster:

```bash
tiup dm patch prod-cluster /tmp/dm--hotfix.tar.gz -N 172.16.4.5:8261
```
