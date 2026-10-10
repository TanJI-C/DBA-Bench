# tiup mirror publish syntax options and outputs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-command-mirror-publish.md`
- Source Title: `tiup mirror publish`
- Source Heading Path: `tiup mirror publish | tiup mirror publish > Syntax | tiup mirror publish > Options | tiup mirror publish > Options > -k, --key | tiup mirror publish > Options > --arch | tiup mirror publish > Options > --os | tiup mirror publish > Options > --desc | tiup mirror publish > Options > --hide | tiup mirror publish > Options > --standalone | tiup mirror publish > Outputs`
- Source Line Ranges: `5-86`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `mirror`, `publish`, `syntax`, `flags`, `signing`, `platform`, `architecture`, `operating-system`, `component-ownership`, `authorization`, `outputs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0991_de9ae02255`
- Source ID: `tidb-docs-8.1:tiup/tiup-command-mirror-publish.md#tiup-mirror-publish`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0161b494fe6433942079ae4e6749d9e05fa069a8c2561115247ad00eb67f7130`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror-publish#tiup-mirror-publish
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-command-mirror-publish.md

## Retrieval Guidance

- Use When: Use this when looking up the command syntax, flags, platform restrictions, signing key option, authorization behavior, or output of `tiup mirror publish` for publishing a component or a new component version.
- Retrieval Keywords: tiup mirror publish, tiup mirror publish <comp-name> <version> <tarball> <entry>, -k, --key, --arch, --os, --desc, --hide, --standalone, private.json, Semantic Versioning, component owner, grant command, Error: The server refused, make sure you have access to this component, Error: the signature is not correct, tiup list -all, tiup list, amd64, arm64, linux, darwin, any
- Follow-up Guidance: If the topic is adding a new component owner, the source points to the usage of the `grant` command.
- Classification Note: This is reference content because it defines `tiup mirror publish` syntax, parameter meanings, option defaults and constraints, and the exact success and error outputs.

## Official Source Content

# tiup mirror publish

The command `tiup mirror publish` is used to publish a new component or a new version of an existing component. Only component owner that has the access to the target component can publish it. To add a new component owner, see the usage of the [`grant` command](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror-grant).
## Syntax

```shell
tiup mirror publish <comp-name> <version> <tarball> <entry> [flags]
```

The meaning of each parameter is as follows:

- `<comp-name>`: The name of the components, such as `tidb`. It is recommended to use a string that matches the regular expression `^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}$`.
- `<version>`: The version of the component to be published. The version number needs to follow the requirements of [Semantic Versioning](https://semver.org/).
- `<tarball>`: The local directory of the `.tar.gz` package. You need to put dependencies and the executable file of the component in this package. TiUP uploads this package to the mirror.
- `<entry>`: The location of the component's executable file in `<tarball>`.
## Options
### -k, --key

- Specifies the component owner's private key. The client uses the private key to sign `{component}.json` files.
- Data type: `STRING`
- Default: "${TIUP_HOME}/keys/private.json"
### --arch

- Specifies the platform on which the binary files in `<tarball>` can run. For a single `<tarball>` package, you can only choose the platform from the following options:

    - `amd64`: Indicates that the files run on AMD64 machines.
    - `arm64`: Indicates that the files run on ARM64 machines.
    - `any`: Indicates that the files, such as scripts, run on both AMD64 and ARM64 machines.

- Data type: `STRING`
- Default: "${GOARCH}"

> **Note:**
>
> If `--arch` is set to `any`, then `--os` must be set to `any` as well.
### --os

- Specifies the operating system on which the binary files in `<tarball>` can run. For a single `<tarball>` package, you can only choose the operating system from the following options:

    - `linux`: Indicates that the files run on the Linux operating system.
    - `darwin`: Indicates that the files run on the Darwin operating system.
    - `any`: Indicates that the files, such as scripts, run on both the Linux and Darwin operating systems.

- Data type: `STRING`
- Default: "${GOOS}"

> **Note:**
>
> If `--os` is set to `any`, then `--arch` must be set to `any` as well.
### --desc

- Specifies the description of the component.
- Data type: `String`
- Default: NULL
### --hide

- Specifies whether the component is hidden. If it is a hidden component, it can be seen in the result list of `tiup list -all`, but not in that of `tiup list`.
- Data type: `STRING`
- Default: NULL
### --standalone

- Controls whether the component can run standalone. This option is currently **NOT available**.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
## Outputs

- If the command is executed successfully, there is no output.
- If the component owner is not authorized to modify the target component:
    - If the mirror is a remote mirror, TiUP reports the error `Error: The server refused, make sure you have access to this component`.
    - If the mirror is a local mirror, TiUP reports the error `Error: the signature is not correct`.

[<< Back to the previous page - TiUP Mirror command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror#command-list)
