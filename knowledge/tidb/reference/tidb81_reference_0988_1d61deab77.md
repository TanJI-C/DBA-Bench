# tiup mirror init command usage and outputs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-command-mirror-init.md`
- Source Title: `tiup mirror init`
- Source Heading Path: `tiup mirror init | tiup mirror init > Syntax | tiup mirror init > Options | tiup mirror init > Options > -k, --key-dir | tiup mirror init > Options > Outputs`
- Source Line Ranges: `5-47`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `mirror`, `initialization`, `syntax`, `key-directory`, `output-files`, `errors`, `private-keys`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0988_1d61deab77`
- Source ID: `tidb-docs-8.1:tiup/tiup-command-mirror-init.md#tiup-mirror-init`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `14104279cc986bb655eed35762b6b6e4db4aa15f6a52d58b3d721cf0adac6a66`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror-init#tiup-mirror-init
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-command-mirror-init.md

## Retrieval Guidance

- Use When: Use this when you need the `tiup mirror init` syntax, its generated mirror files, or the errors reported for invalid `<path>` values.
- Retrieval Keywords: tiup mirror init, initialize an empty mirror, <path>, -k, --key-dir, {path}/keys, root.json, 1.index.json, snapshot.json, timestamp.json, Error: the target path '%s' is not an empty directory, Error: fdopendir: not a directory
- Follow-up Guidance: If you need the file formats and detailed meaning of these mirror files, refer to the TiUP Mirror Reference Guide.
- Classification Note: This is a reference command page for `tiup mirror init`, describing initialization syntax, options, generated files, and output errors.

## Official Source Content

# tiup mirror init

The command `tiup mirror init` is used to initialize an empty mirror. The initialized mirror does not contain any components or component owners. The command only generates the following files for the initialized mirror:

```
+ <mirror-dir>                                  # Mirror's root directory
|-- root.json                                   # Mirror's root certificate
|-- 1.index.json                                # Component/user index
|-- snapshot.json                               # Mirror's latest snapshot
|-- timestamp.json                              # Mirror's latest timestamp
|--+ keys                                       # Mirror's private key (can be moved to other locations)
   |-- {hash1..hashN}-root.json                 # Private key of the root certificate
   |-- {hash}-index.json                        # Private key of the indexes
   |-- {hash}-snapshot.json                     # Private key of the snapshots
   |-- {hash}-timestamp.json                    # Private key of the timestamps
```

For the specific usage and content format of the above files, refer to [TiUP Mirror Reference Guide](https://docs.pingcap.com/tidb/stable/tiup/tiup-mirror-reference).
## Syntax

```shell
tiup mirror init <path> [flags]
```

`<path>` is used to specify a local directory where TiUP generates and stores mirror files. The local directory can be a relative path. If the specified directory already exists, it must be empty; if it does not exist, TiUP creates it automatically.
## Options
### -k, --key-dir

- Specifies the directory where TiUP generates private key files. If the specified directory does not exist, TiUP automatically creates it.
- Data type: `STRING`
- If this option is not specified in the command, TiUP generates private key files in `{path}/keys` by default.
### Outputs

- If the command is executed successfully, there is no output.
- If the specified `<path>` is not empty, TiUP reports the error `Error: the target path '%s' is not an empty directory`.
- If the specified `<path>` is not a directory, TiUP reports the error `Error: fdopendir: not a directory`.

[<< Back to the previous page - TiUP Mirror command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror#command-list)
