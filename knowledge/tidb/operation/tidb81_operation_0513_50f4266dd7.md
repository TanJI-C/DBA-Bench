# tiup dm upgrade command syntax, options, and output

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-dm-upgrade.md`
- Source Title: `tiup dm upgrade`
- Source Heading Path: `tiup dm upgrade | tiup dm upgrade > Syntax | tiup dm upgrade > Options | tiup dm upgrade > Options > --offline | tiup dm upgrade > Options > -h, --help | tiup dm upgrade > Output`
- Source Line Ranges: `5-35`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`
- Topic Tags: `upgrade`, `command-line`, `syntax`, `offline-upgrade`, `help`, `output`, `version-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0513_50f4266dd7`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-dm-upgrade.md#tiup-dm-upgrade`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6613bfa7005e755432373b34524a6fad1ca798e5c1d1dbb0fb9297f19de7d3f7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-upgrade#tiup-dm-upgrade
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-dm-upgrade.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiUP DM command syntax, flags, and constraints for upgrading a specified DM cluster to a target version.
- Retrieval Keywords: tiup dm upgrade, tiup dm upgrade <cluster-name> <version> [flags], --offline, -h, --help, tiup dm list, upgrade to a later version only, downgrade is not allowed, upgrading to a nightly version is not allowed, Log of the service upgrade process
- Follow-up Guidance: If the cluster name is unknown, the content points to the `tiup dm list` command to check it.
- Classification Note: This is classified as an operation chunk because the content defines the `tiup dm upgrade` command usage, options, and output for managing a DM cluster upgrade.

## Official Source Content

# tiup dm upgrade

The `tiup dm upgrade` command is used to upgrade a specified cluster to a specific version.
## Syntax

```shell
tiup dm upgrade <cluster-name> <version> [flags]
```

- `<cluster-name>` is the name of the cluster to be operated on. If you forget the cluster name, you can check it using the [`tiup dm list`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-list) command.
- `<version>` is the target version to be upgraded to, such as `v8.1.2`. Currently, only upgrading to a later version is allowed, and upgrading to an earlier version is not allowed, which means the downgrade is not allowed. Upgrading to a nightly version is not allowed either.
## Options
### --offline

- Declares that the current cluster is offline. When this option is specified, TiUP DM only replaces the binary files of the cluster components in place without restarting the service.
### -h, --help

- Prints the help information.
- Data type: `BOOLEAN`
- This option is disabled by default with the `false` value. To enable this option, add this option to the command, and either pass the `true` value or do not pass any value.
## Output

Log of the service upgrade process.

[<< Back to the previous page - TiUP DM command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm#command-list)
