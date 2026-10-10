# Offline TiUP package preparation, installation, and mirror merge

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/production-deployment-using-tiup.md`
- Source Title: `Deploy a TiDB Cluster Using TiUP`
- Source Heading Path: `Deploy a TiDB Cluster Using TiUP > Step 2. Deploy TiUP on the control machine > Deploy TiUP offline | Deploy a TiDB Cluster Using TiUP > Step 2. Deploy TiUP on the control machine > Deploy TiUP offline > Prepare the TiUP offline component package | Deploy a TiDB Cluster Using TiUP > Step 2. Deploy TiUP on the control machine > Deploy TiUP offline > Deploy the offline TiUP component | Deploy a TiDB Cluster Using TiUP > Step 2. Deploy TiUP on the control machine > Deploy TiUP offline > Merge offline packages`
- Source Line Ranges: `83-228`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `shared`
- Topic Tags: `offline-deployment`, `package-download`, `mirror-clone`, `mirror-merge`, `component-package`, `control-machine`, `local-installation`, `mirror-switching`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0196_9d0844b5c8`
- Source ID: `tidb-docs-8.1:production-deployment-using-tiup.md#deploy-tiup-offline`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `503d06868d47999c0a4d40b217af1e362d41d886c9052b61a84d8382d87710ab`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup#deploy-tiup-offline
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/production-deployment-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when looking for offline TiUP package preparation, local installation on the control machine, or how to merge and switch offline mirrors.
- Retrieval Keywords: Deploy TiUP offline, offline component package, tidb-community-server-{version}-linux-{arch}.tar.gz, tidb-community-toolkit-{version}-linux-{arch}.tar.gz, tiup mirror clone, tiup mirror clone tidb-community-server-${version}-linux-amd64 ${version} --os=linux --arch=amd64, tar czvf tidb-community-server-${version}-linux-amd64.tar.gz, tiup-custom-mirror-v1.12.3, --tiup v1.12.3 --cluster v1.12.3, tiup mirror show, $HOME/.tiup/tiup.toml, ${base_mirror}, cp -r ${base_mirror}/keys $HOME/.tiup/, tiup mirror merge, tiup list, local_install.sh, tiup mirror set tidb-community-server-${version}-linux-amd64, merge offline packages, cp -rp keys ~/.tiup/, tiup mirror set <mirror-dir>, tiup mirror set https://tiup-mirrors.pingcap.com
- Follow-up Guidance: The source also states that to switch the mirror to another directory you can run `tiup mirror set <mirror-dir>`, and to switch the mirror to the online environment you can run `tiup mirror set https://tiup-mirrors.pingcap.com`.
- Classification Note: The official content classifies this as an operation topic for the self-managed TiUP component because it covers offline package download or mirror cloning, offline local installation, mirror merge, and mirror switching procedures.

## Official Source Content

### Deploy TiUP offline

Perform the following steps in this section to deploy a TiDB cluster offline using TiUP:
#### Prepare the TiUP offline component package

**Method 1**: Download the offline binary packages (TiUP offline package included) of the target TiDB version using the following links. You need to download both the server and toolkit packages. Note that your downloading means you agree to the [Privacy Policy](https://www.pingcap.com/privacy-policy/).

```
https://download.pingcap.com/tidb-community-server-{version}-linux-{arch}.tar.gz
```

```
https://download.pingcap.com/tidb-community-toolkit-{version}-linux-{arch}.tar.gz
```

> **Tip:**
>
> `{version}` in the link indicates the version number of TiDB and `{arch}` indicates the architecture of the system, which can be `amd64` or `arm64`. For example, the download link for `v8.1.2` in the `amd64` architecture is `https://download.pingcap.com/tidb-community-toolkit-v8.1.2-linux-amd64.tar.gz`.

**Method 2**: Manually pack an offline component package using `tiup mirror clone`. The detailed steps are as follows:

1. Install the TiUP package manager online.

    1. Install the TiUP tool:

        ```shell
        curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh
        ```

    2. Redeclare the global environment variables:

        ```shell
        source .bash_profile
        ```

    3. Confirm whether TiUP is installed:

        ```shell
        which tiup
        ```

2. Pull the mirror using TiUP.

    1. Pull the needed components on a machine that has access to the Internet:

        ```shell
        tiup mirror clone tidb-community-server-${version}-linux-amd64 ${version} --os=linux --arch=amd64
        ```

        The command above creates a directory named `tidb-community-server-${version}-linux-amd64` in the current directory, which contains the component package necessary for starting a cluster.

    2. Pack the component package by using the `tar` command and send the package to the control machine in the isolated environment:

        ```bash
        tar czvf tidb-community-server-${version}-linux-amd64.tar.gz tidb-community-server-${version}-linux-amd64
        ```

        `tidb-community-server-${version}-linux-amd64.tar.gz` is an independent offline environment package.

3. Customize the offline mirror, or adjust the contents of an existing offline mirror.

    If you want to adjust an existing offline mirror (such as adding a new version of a component), take the following steps:

    1. When pulling an offline mirror, you can get an incomplete offline mirror by specifying specific information via parameters, such as the component and version information. For example, you can pull an offline mirror that includes only the offline mirror of TiUP v1.12.3 and TiUP Cluster v1.12.3 by running the following command:

        ```bash
        tiup mirror clone tiup-custom-mirror-v1.12.3 --tiup v1.12.3 --cluster v1.12.3
        ```

        If you only need the components for a particular platform, you can specify them using the `--os` or `--arch` parameters.

    2. Refer to the step 2 of "Pull the mirror using TiUP", and send this incomplete offline mirror to the control machine in the isolated environment.

    3. Check the path of the current offline mirror on the control machine in the isolated environment. If your TiUP tool is of a recent version, you can get the current mirror address by running the following command:

        ```bash
        tiup mirror show
        ```

        If the output of the above command indicates that the `show` command does not exist, you might be using an older version of TiUP. In this case, you can get the current mirror address from `$HOME/.tiup/tiup.toml`. Record this mirror address. In the following steps, `${base_mirror}` is used to refer to this address.

    4. Merge an incomplete offline mirror into an existing offline mirror:

        First, copy the `keys` directory in the current offline mirror to the `$HOME/.tiup` directory:

        ```bash
        cp -r ${base_mirror}/keys $HOME/.tiup/
        ```

        Then use the TiUP command to merge the incomplete offline mirror into the mirror in use:

        ```bash
        tiup mirror merge tiup-custom-mirror-v1.12.3
        ```

    5. When the above steps are completed, check the result by running the `tiup list` command. In this document's example, the outputs of both `tiup list tiup` and `tiup list cluster` show that the corresponding components of `v1.12.3` are available.
#### Deploy the offline TiUP component

After sending the package to the control machine of the target cluster, install the TiUP component by running the following commands:

```bash
tar xzvf tidb-community-server-${version}-linux-amd64.tar.gz && \
sh tidb-community-server-${version}-linux-amd64/local_install.sh && \
source /home/tidb/.bash_profile
```

The `local_install.sh` script automatically runs the `tiup mirror set tidb-community-server-${version}-linux-amd64` command to set the current mirror address to `tidb-community-server-${version}-linux-amd64`.
#### Merge offline packages

If you download the offline packages via download links, you need to merge the server package and the toolkit package into an offline mirror. If you manually package the offline component packages using the `tiup mirror clone` command, you can skip this step.

Run the following commands to merge the offline toolkit package into the server package directory:

```bash
tar xf tidb-community-toolkit-${version}-linux-amd64.tar.gz
ls -ld tidb-community-server-${version}-linux-amd64 tidb-community-toolkit-${version}-linux-amd64
cd tidb-community-server-${version}-linux-amd64/
cp -rp keys ~/.tiup/
tiup mirror merge ../tidb-community-toolkit-${version}-linux-amd64
```

To switch the mirror to another directory, run the `tiup mirror set <mirror-dir>` command. To switch the mirror to the online environment, run the `tiup mirror set https://tiup-mirrors.pingcap.com` command.
