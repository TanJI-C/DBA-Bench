# TiUP mirror overview, creation, update, and layout

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-mirror-reference.md`
- Source Title: `TiUP Mirror Reference Guide`
- Source Heading Path: `TiUP Mirror Reference Guide | TiUP Mirror Reference Guide > Create and update mirror | TiUP Mirror Reference Guide > Mirror structure`
- Source Line Ranges: `5-54`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `mirror`, `repository`, `creation`, `update`, `directory-structure`, `certificates`, `keys`, `rollback`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1042_2915c2432b`
- Source ID: `tidb-docs-8.1:tiup/tiup-mirror-reference.md#tiup-mirror-reference-guide`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `626b79fc74ccb0bae59f62e5d0bc4370bd87c560715cdf89cd1f3b6c7e2a4899`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-mirror-reference#tiup-mirror-reference-guide
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-mirror-reference.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how TiUP mirrors are created or updated and what files and directories exist in a local mirror or remote mirror layout.
- Retrieval Keywords: TiUP Mirror Reference Guide, tiup mirror init, tiup mirror clone, tiup mirror, local mirror, remote mirror, mirror structure, root.json, snapshot.json, timestamp.json, commits directory, keys directory, component binary package, rollback, Component/user index
- Follow-up Guidance: The source also notes that the `commits` directory stores mirror update logs used to roll back the mirror, and that the private keys in the `keys` directory are sensitive and can be kept separately.
- Classification Note: This is reference content because it defines TiUP mirror forms, creation and update commands, and the exact mirror directory structure and file names.

## Official Source Content

# TiUP Mirror Reference Guide

TiUP mirrors are TiUP's component warehouse, which stores components and their metadata. TiUP mirrors take the following two forms:

+ Directory on the local disk: serves the local TiUP client, which is called a local mirror in this document.
+ HTTP mirror started based on the remote disk directory: serves the remote TiUP client, which is called a remote mirror in this document.
## Create and update mirror

You can create a TiUP mirror using one of the following two methods:

+ Execute `tiup mirror init` to create a mirror from scratch.
+ Execute `tiup mirror clone` to clone from an existing mirror.

After the mirror is created, you can add components to or delete components from the mirror using the `tiup mirror` commands. TiUP updates a mirror by adding files and assigning a new version number to it, rather than deleting any files from the mirror.
## Mirror structure

A typical mirror structure is as follows:

```
+ <mirror-dir>                                  # Mirror's root directory
|-- root.json                                   # Mirror's root certificate
|-- {2..N}.root.json                            # Mirror's root certificate
|-- {1..N}.index.json                           # Component/user index
|-- {1..N}.{component}.json                     # Component metadata
|-- {component}-{version}-{os}-{arch}.tar.gz    # Component binary package
|-- snapshot.json                               # Mirror's latest snapshot
|-- timestamp.json                              # Mirror's latest timestamp
|--+ commits                                    # Mirror's update log (deletable)
   |--+ commit-{ts1..tsN}
      |-- {N}.root.json
      |-- {N}.{component}.json
      |-- {N}.index.json
      |-- {component}-{version}-{os}-{arch}.tar.gz
      |-- snapshot.json
      |-- timestamp.json
|--+ keys                                       # Mirror's private key (can be moved to other locations)
   |-- {hash1..hashN}-root.json                 # Private key of the root certificate
   |-- {hash}-index.json                        # Private key of the indexes
   |-- {hash}-snapshot.json                     # Private key of the snapshots
   |-- {hash}-timestamp.json                    # Private key of the timestamps
```

> **Note:**
>
> + The `commits` directory stores the logs generated in the process of mirror update and is used to roll back the mirror. You can delete the old log directories regularly when the disk space is insufficient.
> + The private key stored in the `keys` directory is sensitive. It is recommended to keep it separately.
