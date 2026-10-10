# Clone, configure, and update a private mirror

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-mirror.md`
- Source Title: `Create a Private Mirror`
- Source Heading Path: `Create a Private Mirror > Clone a mirror | Create a Private Mirror > Clone a mirror > Manage the private repository | Create a Private Mirror > Clone a mirror > Update the private repository`
- Source Line Ranges: `50-127`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `tikv`
- Topic Tags: `mirror-clone`, `repository-sharing`, `mirror-location`, `environment-variables`, `platform-selection`, `version-selection`, `repository-update`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0520_93d03352f7`
- Source ID: `tidb-docs-8.1:tiup/tiup-mirror.md#clone-a-mirror`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5cd3fd2548c7670b752b54e7065113c3d43b8508247835da9809b4f1291d2722`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-mirror#clone-a-mirror
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-mirror.md

## Retrieval Guidance

- Use When: Use this chunk when you need the syntax and flags for `tiup mirror clone`, how to point TiUP to a shared mirror, or what happens when cloning again to update a local repository.
- Retrieval Keywords: tiup mirror clone <target-dir> [global-version] [flags], target-dir, global-version, --prefix, --full, --os, --arch, --tidb, --tikv, v8.1.2, After cloning, signing keys are set up automatically, Manage the private repository, tiup mirror set <location>, tiup mirror set /shared_data/tiup, tiup mirror set https://tiup-mirror.example.com/, tiup mirror set --reset, TIUP_MIRRORS, export TIUP_MIRRORS=/shared_data/tiup, tiup list, Update the private repository, same target-dir, create new manifests, latest versions of components available
- Follow-up Guidance: If `tiup mirror set...` was run on the machine that runs `tiup mirror clone`, reset the mirror with `tiup mirror set --reset` before updating the private mirror.
- Classification Note: This is operation content because it describes how to clone a mirror with platform and version flags, configure repository location sharing, and rerun cloning to update manifests and components.

## Official Source Content

## Clone a mirror

You can run the `tiup mirror clone` command to build a local mirror:

```bash
tiup mirror clone <target-dir> [global-version] [flags]
```

- `target-dir`: used to specify the directory in which cloned data is stored.
- `global-version`: used to quickly set a global version for all components.

The `tiup mirror clone` command provides many optional flags (might provide more in the future). These flags can be divided into the following categories according to their intended usages:

- Determines whether to use prefix matching to match the version when cloning

    If the `--prefix` flag is specified, the version number is matched by prefix for the clone. For example, if you specify `--prefix` as "v5.0.0", then "v5.0.0-rc", and "v5.0.0" are matched.

- Determines whether to use the full clone

    If you specify the `--full` flag, you can clone the official mirror fully.

    > **Note:**
    >
    > If `--full`, `global-version` flags, and the component versions are not specified, only some meta information is cloned.

- Determines whether to clone packages from the specific platform

    If you want to clone packages only for a specific platform, use `-os` and `-arch` to specify the platform. For example:

    - Execute the `tiup mirror clone <target-dir> [global-version] --os=linux` command to clone for linux.
    - Execute the `tiup mirror clone <target-dir> [global-version] --arch=amd64` command to clone for amd64.
    - Execute the `tiup mirror clone <target-dir> [global-version] --os=linux --arch=amd64` command to clone for linux/amd64.

- Determines whether to clone a specific version of a package

    If you want to clone only one version (not all versions) of a component, use `--<component>=<version>` to specify this version. For example:

    - Execute the `tiup mirror clone <target-dir> --tidb v8.1.2` command to clone the v8.1.2 version of the TiDB component.
    - Run the `tiup mirror clone <target-dir> --tidb v8.1.2 --tikv all` command to clone the v8.1.2 version of the TiDB component and all versions of the TiKV component.
    - Run the `tiup mirror clone <target-dir> v8.1.2` command to clone the v8.1.2 version of all components in a cluster.

After cloning, signing keys are set up automatically.
### Manage the private repository

You can share the repository cloned using `tiup mirror clone` among hosts either by sharing files via SCP, NFS, or by making the repository available over the HTTP or HTTPS protocol. Use `tiup mirror set <location>` to specify the location of the repository.

```bash
tiup mirror set /shared_data/tiup
```

```bash
tiup mirror set https://tiup-mirror.example.com/
```

> **Note:**
>
> If you run `tiup mirror set...` on the machine where you run `tiup mirror clone`, the next time you run `tiup mirror clone...`, the machine clones from the local mirror, not the remote one. Therefore, you need to reset the mirror by running `tiup mirror set --reset` before updating the private mirror.

Another way of using a mirror is to use the `TIUP_MIRRORS` environment variable. Here is an example for running `tiup list` with a private repository.

```bash
export TIUP_MIRRORS=/shared_data/tiup
tiup list
```

`TIUP_MIRRORS` setting can permanently change the mirror configuration, for example, `tiup mirror set`. For details, see [tiup issue #651](https://github.com/pingcap/tiup/issues/651).
### Update the private repository

If you run the `tiup mirror clone` command again with the same `target-dir`, the machine will create new manifests and download the latest versions of components available.

> **Note:**
>
> Before recreating the manifest, ensure that all components and versions (including earlier ones downloaded previously) are included.
