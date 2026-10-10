# TiUP reference syntax, global options, commands, and components

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-reference.md`
- Source Title: `TiUP Reference`
- Source Heading Path: `TiUP Reference | TiUP Reference > Syntax | TiUP Reference > Options | TiUP Reference > Options > --binary | TiUP Reference > Options > --binpath | TiUP Reference > Options > -T, --tag | TiUP Reference > Options > -v, --version | TiUP Reference > Options > --help | TiUP Reference > Command list | TiUP Reference > Component list`
- Source Line Ranges: `5-79`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `pd`, `tikv`, `dm`
- Topic Tags: `syntax`, `global-options`, `binary-path`, `binpath`, `tag`, `version`, `help`, `command-list`, `component-list`, `package-manager`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1048_973baf8f0d`
- Source ID: `tidb-docs-8.1:tiup/tiup-reference.md#tiup-reference`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d3c2f9828610a5ab3937e0d1b251742d3d58db1bcbe82f1039b8dffaf26cf5d9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-reference#tiup-reference
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-reference.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiUP command syntax, global flags such as `--binary`, `--binpath`, `-T/--tag`, `-v/--version`, and `--help`, or the top-level TiUP command and component lists.
- Retrieval Keywords: TiUP Reference, tiup [flags] <command> [args...], tiup [flags] <component> [args...], --binary, --binpath, -T, --tag, -v, --version, --help, Command list, Component list, install, list, uninstall, update, status, clean, mirror, telemetry, completion, env, help, cluster, dm, package manager of the TiDB ecosystem
- Follow-up Guidance: The source points to the specific command pages for `install`, `list`, `uninstall`, `update`, `status`, `clean`, `mirror`, `telemetry`, `completion`, `env`, and `help`, and to component pages for `cluster` and `dm`.
- Classification Note: This is reference content because it defines TiUP syntax, describes global option behavior and constraints, and enumerates supported commands and components.

## Official Source Content

# TiUP Reference

TiUP serves as the package manager of the TiDB ecosystem. It manages components in the TiDB ecosystem, such as TiDB, PD, and TiKV.
## Syntax

```shell
tiup [flags] <command> [args...]        # Executes a command
# or
tiup [flags] <component> [args...]      # Runs a component
```

You can use the `--help` command to get the information of a specific command. The summary of each command shows its parameters and their usage. Mandatory parameters are shown in angle brackets, and optional parameters are shown in square brackets.

`<command>` represents the command name. For the list of supported commands, see the [Command list](#command-list) below. `<component>` represents the component name. For the list of supported components, see the [Component list](#component-list) below.
## Options
### --binary

- If you enable this option, the specified binary file path is printed.

    - Executing `tiup --binary <component>` will have the path of the latest stable installed `<component>` component printed. If `<component>` is not installed, an error is returned.
    - Executing `tiup --binary <component>:<version>` will have the path of the installed `<component>` component's `<version>` printed. If this `<version>` is not printed, an error is returned.

- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.

> **Note:**
>
> This option can only be used in commands of the `tiup [flags] <component> [args...]` format.
### --binpath

> **Note:**
>
> This option can only be used in commands of the `tiup [flags] <component> [args...]` format.

- Specifies the path of the component to be executed. When a component is executed, if you do not want to use the binary file in the TiUP mirror, you can add this option to specify using the binary file in a custom path.
- Data type: `STRING`
### -T, --tag

- Specifies a tag for the component to be started. Some components need to use disk storage during the execution, and TiUP allocates a temporary storage directory for this execution. If you want TiUP to allocate a fixed directory, you can use `-T/--tag` to specify the name of the directory, so that the same batch of files can be read and written in multiple executions with the same tag.
- Data type: `STRING`
### -v, --version

Prints the TiUP version.
### --help

Prints the help information.
## Command list

TiUP has multiple commands, and these commands have multiple sub-commands. For the specific commands and their detailed descriptions, click the corresponding links in the list below:

- [install](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-install): Installs a component.
- [list](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-list): Shows the component list.
- [uninstall](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-uninstall): Uninstalls a component.
- [update](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-update): Updates the installed component.
- [status](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-status): Shows the running status of a component.
- [clean](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-clean): Cleans the data directory of a component.
- [mirror](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror): Manages the mirror.
- [telemetry](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-telemetry): Enables or disables the telemetry.
- [completion](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-completion): Completes the TiUP command.
- [env](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-env): Shows the TiUP-related environment variables.
- [help](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-help): Shows the help information of a command or component.
## Component list

- [cluster](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster): Manages the TiDB cluster in a production environment.
- [dm](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm): Manages the TiDB Data Migration (DM) cluster in a production environment.
