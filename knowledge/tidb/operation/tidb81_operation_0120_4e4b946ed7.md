# Audit operations, run host commands, and use dmctl

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/maintain-dm-using-tiup.md`
- Source Title: `Maintain a DM Cluster Using TiUP`
- Source Heading Path: `Maintain a DM Cluster Using TiUP > View the operation log | Maintain a DM Cluster Using TiUP > Run commands on a host in the DM cluster | Maintain a DM Cluster Using TiUP > dmctl`
- Source Line Ranges: `303-386`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`
- Topic Tags: `audit`, `operation-log`, `exec`, `host-commands`, `dmctl`, `cli`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0120_4e4b946ed7`
- Source ID: `tidb-docs-8.1:dm/maintain-dm-using-tiup.md#view-the-operation-log`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1e3d3deb20428954db22a6d419039e0e20509b72dccab33f4bf82c7727cd4f5f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/maintain-dm-using-tiup#view-the-operation-log
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/maintain-dm-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiUP DM commands for viewing operation logs, executing commands on cluster hosts, or invoking the integrated `dmctl` CLI.
- Retrieval Keywords: tiup dm audit, audit-id, tiup dm audit 4D5kQY, View the operation log, tiup dm exec, --command string, --sudo, -N, --node, -R, --role, tiup dm exec prod-cluster --command='ls /tmp', tiup dmctl, tiup dmctl:${version}, --master-addr master1:8261, operate-source create /tmp/source1.yml
- Follow-up Guidance: The source shows that `tiup dm audit` lists executed commands, `tiup dm exec` runs host commands such as `ls /tmp`, and `tiup dmctl --master-addr master1:8261 operate-source create /tmp/source1.yml` is the integrated dmctl form.
- Classification Note: This is classified as an operation because the content covers operational CLI usage for auditing, remote command execution, and DM cluster control through `dmctl`.

## Official Source Content

## View the operation log

To view the operation log, use the `audit` command. The usage of the `audit` command is as follows:

```bash
Usage:
  tiup dm audit [audit-id] [flags]

Flags:
  -h, --help   help for audit
```

If the `[audit-id]` argument is not specified, the command shows a list of commands that have been executed. For example:

```bash
tiup dm audit
```

```
ID      Time                  Command
--      ----                  -------
4D5kQY  2020-08-13T05:38:19Z  tiup dm display test
4D5kNv  2020-08-13T05:36:13Z  tiup dm list
4D5kNr  2020-08-13T05:36:10Z  tiup dm deploy -p prod-cluster ${version} ./examples/dm/minimal.yaml
```

The first column is `audit-id`. To view the execution log of a certain command, pass the `audit-id` argument as follows:

```bash
tiup dm audit 4D5kQY
```
## Run commands on a host in the DM cluster

To run commands on a host in the DM cluster, use the `exec` command. The usage of the `exec` command is as follows:

```bash
Usage:
  tiup dm exec <cluster-name> [flags]

Flags:
      --command string   the command run on cluster host (default "ls")
  -h, --help             help for exec
  -N, --node strings     Only exec on host with specified nodes
  -R, --role strings     Only exec on host with specified roles
      --sudo             use root permissions (default false)
```

For example, to execute `ls /tmp` on all DM nodes, run the following command:

```bash
tiup dm exec prod-cluster --command='ls /tmp'
```
## dmctl

TiUP integrates the DM cluster controller `dmctl`.

Run the following command to use dmctl:

```bash
tiup dmctl [args]
```

Specify the version of dmctl. Modify `${version}` to your needed version before running this command:

```
tiup dmctl:${version} [args]
```

The previous dmctl command to add a source is `dmctl --master-addr master1:8261 operate-source create /tmp/source1.yml`. After dmctl is integrated into TiUP, the command is:

```bash
tiup dmctl --master-addr master1:8261 operate-source create /tmp/source1.yml
```
