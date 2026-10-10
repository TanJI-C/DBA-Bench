# tiup mirror genkey command usage and options

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-command-mirror-genkey.md`
- Source Title: `tiup mirror genkey`
- Source Heading Path: `tiup mirror genkey | tiup mirror genkey > Syntax | tiup mirror genkey > Options | tiup mirror genkey > Options > -n, --name | tiup mirror genkey > Options > -p, --public | tiup mirror genkey > Options > --save | tiup mirror genkey > Outputs`
- Source Line Ranges: `5-56`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `key-generation`, `private-key`, `public-key`, `mirror`, `command-syntax`, `command-options`, `command-output`, `security-warning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0986_a680d0b70e`
- Source ID: `tidb-docs-8.1:tiup/tiup-command-mirror-genkey.md#tiup-mirror-genkey`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2044f59790ca72cc770c3a04e36322d5c1888cd73e5fb10e0249004f3e72355e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror-genkey#tiup-mirror-genkey
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-command-mirror-genkey.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, options, output messages, or key file locations of the `tiup mirror genkey` command for TiUP mirror private and public keys.
- Retrieval Keywords: tiup mirror genkey, tiup mirror genkey [flags], -n --name, -p --public, --save, ${TIUP_HOME}/keys/{name}.json, $HOME/.tiup, {hash-prefix}-public.json, Key already exists, skipped, private key have been write to ${TIUP_HOME}/keys/{name}.json, Error: open ${TIUP_HOME}/keys/{name}.json: no such file or directory, mirror administrators, component owners, normal users, DO NOT transmit private keys over the Internet
- Follow-up Guidance: This chunk also states that `-p/--public` shows the corresponding public key without creating a new private key, and `--save` saves public key information in the current directory as `{hash-prefix}-public.json`.
- Classification Note: The official content is a reference page because it defines the `tiup mirror genkey` command purpose, syntax, flags, file paths, warning, and exact outputs and errors.

## Official Source Content

# tiup mirror genkey

TiUP [mirror](https://docs.pingcap.com/tidb/stable/tiup/tiup-mirror-reference), according its definition, has three roles of users:

- Mirror administrators: They have the permission to modify `root.json`, `index.json`, `snapshot.json`, and `timestamp.json`.
- Component owners: They have the permission to modify the corresponding component.
- Normal users: They can download and use the components.

 Because TiUP requires the signature of the corresponding owner/administrator to modify a file, owners/administrators must have his or her own private key. The command `tiup mirror genkey` is used to generate a private key.

> **Warning:**
>
> **DO NOT** transmit private keys over the Internet.
## Syntax

```shell
tiup mirror genkey [flags]
```
## Options
### -n, --name

- Specifies the name of the key, which also determines the name of the final generated file. The path of the generated private key file is `${TIUP_HOME}/keys/{name}.json`. `TIUP_HOME` refers to the home directory of TiUP, which is `$HOME/.tiup` by default. `name` refers to the private key name that `-n/--name` specifies.
- Data type: `STRING`
- Default: "private"
### -p, --public

- Shows the corresponding public key of the private key specified in the option `-n/--name`.
- TiUP does not create a new private key when `-p/--public` is specified. If the private key specified in `-n/--name` does not exist, TiUP returns an error.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
### --save

- Saves the information of the public key as a file in the current directory. The file name is `{hash-prefix}-public.json`. `hash-prefix` is the first 16 bits of the key ID.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
## Outputs

- If `-p/--public` is not specified:
    - If the private key specified in `-n/--name` exists: TiUP outputs `Key already exists, skipped`.
    - If the private key specified in `-n/--name` does not exist: TiUP outputs `private key have been write to ${TIUP_HOME}/keys/{name}.json`.
- If `-p/--public` is specified:
    - If the private key specified in `-n/--name` does not exist: TiUP reports the error `Error: open ${TIUP_HOME}/keys/{name}.json: no such file or directory`.
    - If the private key specified in `-n/--name` exists: TiUP outputs the content of the corresponding public key.

[<< Back to the previous page - TiUP Mirror command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror#command-list)
