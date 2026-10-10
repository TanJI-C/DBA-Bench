# Upgrade Grafana and Alertmanager for a TiDB cluster with TiUP

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/upgrade-monitoring-services.md`
- Source Title: `Upgrade Cluster Monitoring Services`
- Source Heading Path: `Upgrade TiDB Cluster Monitoring Services > Upgrade Grafana | Upgrade TiDB Cluster Monitoring Services > Upgrade Grafana > Step 1. Download a new Grafana installation package from the Grafana website | Upgrade TiDB Cluster Monitoring Services > Upgrade Grafana > Step 2. Download the Grafana installation package provided by TiDB | Upgrade TiDB Cluster Monitoring Services > Upgrade Grafana > Step 3. Create a new Grafana package that TiUP can use | Upgrade TiDB Cluster Monitoring Services > Upgrade Grafana > Step 4. Upgrade Grafana using the newly created Grafana package | Upgrade TiDB Cluster Monitoring Services > Upgrade Alertmanager | Upgrade TiDB Cluster Monitoring Services > Upgrade Alertmanager > Step 1. Download a new Alertmanager installation package from the Prometheus website | Upgrade TiDB Cluster Monitoring Services > Upgrade Alertmanager > Step 2. Upgrade Alertmanager using the downloaded installation package`
- Source Line Ranges: `67-133`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `monitoring`, `grafana`, `alertmanager`, `upgrade`, `package`, `patch`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0529_ba86480b62`
- Source ID: `tidb-docs-8.1:upgrade-monitoring-services.md#upgrade-grafana`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d931923e198cfaae87c18f3a293869459ebc1b353c42cabeac3c539ebf364a1b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/upgrade-monitoring-services#upgrade-grafana
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/upgrade-monitoring-services.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented TiUP steps to upgrade Grafana or Alertmanager for a TiDB cluster, including package preparation for Grafana and direct patching for Alertmanager.
- Retrieval Keywords: Upgrade Grafana, Upgrade Alertmanager, tiup cluster patch <cluster-name> grafana-v{new-version}.tar.gz -R grafana --overwrite, tiup cluster patch <cluster-name> alertmanager-v{new-version}-linux-amd64.tar.gz -R alertmanager --overwrite, grafana-v{version}-linux-amd64.tar.gz, grafana-v{new-version}.tar.gz, Grafana download page, Prometheus download page #alertmanager, http://<Grafana-server-host-name>:3000, http://<Alertmanager-server-host-name>:9093, Status
- Follow-up Guidance: After the upgrade, verify Grafana on `http://<Grafana-server-host-name>:3000` by checking the Grafana version on the page, or verify Alertmanager on `http://<Alertmanager-server-host-name>:9093` by clicking **Status** and checking the Alertmanager version.
- Classification Note: This is classified as an operation chunk because the content provides upgrade commands, package sources, and verification steps for Grafana and Alertmanager with TiUP in a self-managed TiDB cluster.

## Official Source Content

## Upgrade Grafana

For better compatibility with TiDB, it is recommended to use the Grafana installation package provided in the TiDB installation package. The version of Grafana in the TiDB installation package is fixed. If you want to use a newer Grafana version, refer to [Grafana Release Notes](https://grafana.com/docs/grafana/latest/whatsnew/) for new features of each version and choose a suitable version for your production environment. You can also consult with PingCAP technical staff for a recommended version.

In the following upgrade steps, you need to download the Grafana installation package of your desired version from the Grafana website, and then use it to create a Grafana package that TiUP can use.
### Step 1. Download a new Grafana installation package from the Grafana website

1. Download a new installation package from the [Grafana download page](https://grafana.com/grafana/download?pg=get&plcmt=selfmanaged-box1-cta1). You can choose either the `OSS` or `Enterprise` edition according to your needs.
2. Extract the downloaded package. 
### Step 2. Download the Grafana installation package provided by TiDB

1. Download the TiDB server package and extract it. Note that your downloading means you agree to the [Privacy Policy](https://www.pingcap.com/privacy-policy/).

    ```
    https://download.pingcap.com/tidb-community-server-{version}-linux-{arch}.tar.gz
    ```

    > **Tip:**
    >
    > `{version}` in the link indicates the version number of TiDB and `{arch}` indicates the architecture of the system, which can be `amd64` or `arm64`. For example, the download link for `v8.1.2` in the `amd64` architecture is `https://download.pingcap.com/tidb-community-toolkit-v8.1.2-linux-amd64.tar.gz`.

2. In the extracted files, locate `grafana-v{version}-linux-amd64.tar.gz` and extract it.

    ```bash
    tar -xzf grafana-v{version}-linux-amd64.tar.gz
    ```
### Step 3. Create a new Grafana package that TiUP can use

1. Copy the files extracted in [Step 1](#step-1-download-a-new-grafana-installation-package-from-the-grafana-website), and then use the copied files to replace the files in the `./grafana-v{version}-linux-amd64/` directory extracted in [Step 2](#step-2-download-the-grafana-installation-package-provided-by-tidb).
2. Recompress the `./grafana-v{version}-linux-amd64` directory and name the new compressed package as `grafana-v{new-version}.tar.gz`, where `{new-version}` can be specified according to your need.

    ```bash
    cd grafana-v{version}-linux-amd64
    tar -zcvf ../grafana-v{new-version}.tar.gz ./
    ```
### Step 4. Upgrade Grafana using the newly created Grafana package

Execute the following command to upgrade Grafana:

```bash
tiup cluster patch <cluster-name> grafana-v{new-version}.tar.gz -R grafana --overwrite

```

After the upgrade, you can go to the home page of the Grafana server (usually at `http://<Grafana-server-host-name>:3000`), and then check the Grafana version on the page to confirm whether the upgrade is successful.
## Upgrade Alertmanager

The Alertmanager package in the TiDB installation package is directly from the Prometheus website. Therefore, when upgrading Alertmanager, you only need to download and install a new version of Alertmanager from the Prometheus website.
### Step 1. Download a new Alertmanager installation package from the Prometheus website

Download the `alertmanager` installation package from the [Prometheus download page](https://prometheus.io/download/#alertmanager).
### Step 2. Upgrade Alertmanager using the downloaded installation package

Execute the following command to upgrade Alertmanager:

```bash
tiup cluster patch <cluster-name> alertmanager-v{new-version}-linux-amd64.tar.gz -R alertmanager --overwrite
```

After the upgrade, you can go to the home page of the Alertmanager server (usually at `http://<Alertmanager-server-host-name>:9093`), click **Status** in the top navigation menu, and then check the Alertmanager version to confirm whether the upgrade is successful.
