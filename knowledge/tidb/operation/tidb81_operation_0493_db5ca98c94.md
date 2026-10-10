# TiUP cluster environment checks for target machines

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster.md`
- Source Title: `Deploy and Maintain an Online TiDB Cluster Using TiUP`
- Source Heading Path: `Deploy and Maintain an Online TiDB Cluster Using TiUP > Environment checks for target machines`
- Source Line Ranges: `661-698`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `environment-checks`, `predeployment`, `ssh`, `cpu`, `memory`, `disk`, `fio`, `auto-repair`, `topology`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0493_db5ca98c94`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster.md#environment-checks-for-target-machines`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `18478e276025d074e97c7b149e6a6e14736ba1947705f5b7417e1a6db898f651`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster#environment-checks-for-target-machines
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster.md

## Retrieval Guidance

- Use When: Use this content when looking for how `tiup cluster check` validates target machine environment before deployment or for an existing cluster, including optional CPU, memory, disk `fio`, SSH, and auto-repair flags.
- Retrieval Keywords: tiup cluster check, tiup cluster check topology.yml --user tidb -p, tiup cluster check <cluster-name> --cluster, --apply, --cluster, --enable-cpu, --enable-disk, --enable-mem, --identity_file, --password, --user, environment checks for target machines, CPU thread count check, memory size check, disk IO fio check, fio, automatic repair failed checks
- Follow-up Guidance: The content also states that `--apply` automatically repairs some failed items, while unrepaired items need to be handled manually according to the actual situation.
- Classification Note: This is classified as an operation topic for the TiUP component because it describes running the `check` command and its flags to inspect deployment or existing cluster machine environments.

## Official Source Content

## Environment checks for target machines

You can use the `check` command to perform a series of checks on the environment of the target machine and output the check results. By executing the `check` command, you can find common unreasonable configurations or unsupported situations. The command flag list is as follows:

```bash
Usage:
  tiup cluster check <topology.yml | cluster-name> [flags]
Flags:
      --apply                  Try to fix failed checks
      --cluster                Check existing cluster, the input is a cluster name.
      --enable-cpu             Enable CPU thread count check
      --enable-disk            Enable disk IO (fio) check
      --enable-mem             Enable memory size check
  -h, --help                   help for check
  -i, --identity_file string   The path of the SSH identity file. If specified, public key authentication will be used.
  -p, --password               Use password of target hosts. If specified, password authentication will be used.
      --user string            The user name to login via SSH. The user must has root (or sudo) privilege.
```

By default, this command is used to check the environment before deployment. By specifying the `--cluster` flag to switch the mode, you can also check the target machines of an existing cluster, for example:

```bash
# check deployed servers before deployment
tiup cluster check topology.yml --user tidb -p
# check deployed servers of an existing cluster
tiup cluster check <cluster-name> --cluster
```

The CPU thread count check, memory size check, and disk performance check are disabled by default. For the production environment, it is recommended that you enable the three checks and make sure they pass to obtain the best performance.

- CPU: If the number of threads is greater than or equal to 16, the check is passed.
- Memory: If the total size of physical memory is greater than or equal to 32 GB, the check is passed.
- Disk: Execute `fio` test on the partitions of `data_dir` and record the results.

When running the checks, if the `--apply` flag is specified, the program automatically repairs the failed items. Automatic repair is limited to some items that can be adjusted by modifying the configuration or system parameters. Other unrepaired items need to be handled manually according to the actual situation.

Environment checks are not necessary for deploying a cluster. For the production environment, it is recommended to perform environment checks and pass all check items before deployment. If not all the check items are passed, the cluster might be deployed and run normally, but the best performance might not be obtained.
