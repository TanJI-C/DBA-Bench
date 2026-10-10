# Upgrade Prometheus for a TiDB cluster with TiUP

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/upgrade-monitoring-services.md`
- Source Title: `Upgrade Cluster Monitoring Services`
- Source Heading Path: `Upgrade TiDB Cluster Monitoring Services | Upgrade TiDB Cluster Monitoring Services > Upgrade Prometheus | Upgrade TiDB Cluster Monitoring Services > Upgrade Prometheus > Step 1. Download a new Prometheus installation package from the Prometheus website | Upgrade TiDB Cluster Monitoring Services > Upgrade Prometheus > Step 2. Download the Prometheus installation package provided by TiDB | Upgrade TiDB Cluster Monitoring Services > Upgrade Prometheus > Step 3. Create a new Prometheus package that TiUP can use | Upgrade TiDB Cluster Monitoring Services > Upgrade Prometheus > Step 4. Upgrade Prometheus using the newly created Prometheus package`
- Source Line Ranges: `5-66`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `monitoring`, `prometheus`, `upgrade`, `package`, `patch`, `verification`, `compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0528_9aad256152`
- Source ID: `tidb-docs-8.1:upgrade-monitoring-services.md#upgrade-tidb-cluster-monitoring-services`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b60c82b763a49e13d4f759d90349550b0f6d3b487b1e84af77099b8cb7b95128`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/upgrade-monitoring-services#upgrade-tidb-cluster-monitoring-services
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/upgrade-monitoring-services.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented TiUP procedure to upgrade Prometheus for a TiDB cluster by creating a custom package from a Prometheus download and the TiDB-provided package.
- Retrieval Keywords: Upgrade Prometheus, TiUP, tiup cluster patch <cluster-name> prometheus-v{new-version}.tar.gz -R prometheus --overwrite, prometheus-v{version}-linux-amd64.tar.gz, prometheus-v{new-version}.tar.gz, Prometheus download page, Runtime & Build Information, http://<Prometheus-server-host-name>:9090, deploy scale-out scale-in reload, TiUP version 1.9.0 and later
- Follow-up Guidance: After the upgrade, open the Prometheus home page at `http://<Prometheus-server-host-name>:9090`, click **Status**, and check **Runtime & Build Information** to confirm the Prometheus version.
- Classification Note: This is classified as an operation chunk because the content gives step-by-step package preparation, patch, and verification commands for upgrading Prometheus with TiUP in a self-managed TiDB cluster.

## Official Source Content

# Upgrade TiDB Cluster Monitoring Services

When deploying a TiDB cluster, TiUP automatically deploys monitoring services (such as Prometheus, Grafana, and Alertmanager) for the cluster. If you scale out this cluster, TiUP also automatically adds monitoring configurations for newly added nodes during the scaling. The monitoring services automatically deployed by TiUP are usually not the latest versions of these third-party monitoring services. To use the latest versions, you can follow this document to upgrade the monitoring services.

When managing a cluster, TiUP uses its own configurations to override the configurations of the monitoring services. If you directly upgrade the monitoring services by replacing their configuration files, any subsequent TiUP operations such as `deploy`, `scale-out`, `scale-in`, and `reload` on the cluster might overwrite your upgrade, leading to errors. To upgrade Prometheus, Grafana, and Alertmanager, follow the steps in this document rather than directly replacing configuration files.

> **Note:**
>
> - If your monitoring services are [deployed manually](https://docs.pingcap.com/tidb/stable/deploy-monitoring-services) instead of using TiUP, you can directly upgrade them without referring to this document.
> - The TiDB compatibility with newer versions of monitoring services has not been tested, so some features might not work as expected after the upgrade. For any issues, create an [issue](https://github.com/pingcap/tidb/issues) on GitHub.
> - The upgrade steps in this document are applicable for TiUP version 1.9.0 and later. Therefore, check your TiUP version before the upgrade.
> - When you use TiUP to upgrade the TiDB cluster, TiUP will redeploy the monitoring services to the default version. You need to redo the upgrade for monitoring services after the TiDB upgrade. 
## Upgrade Prometheus

For better compatibility with TiDB, it is recommended to use the Prometheus installation package provided in the TiDB installation package. The version of Prometheus in the TiDB installation package is fixed. If you want to use a newer Prometheus version, refer to [Prometheus Release Notes](https://github.com/prometheus/prometheus/releases) for new features of each version and choose a suitable version for your production environment. You can also consult with PingCAP technical staff for a recommended version.

In the following upgrade steps, you need to download the Prometheus installation package of your desired version from the Prometheus website, and then use it to create a Prometheus package that TiUP can use.
### Step 1. Download a new Prometheus installation package from the Prometheus website

Download a new installation package from the [Prometheus download page](https://prometheus.io/download/) and extract it.
### Step 2. Download the Prometheus installation package provided by TiDB

1. Download the TiDB server package and extract it. Note that your downloading means you agree to the [Privacy Policy](https://www.pingcap.com/privacy-policy/).

    ```
    https://download.pingcap.com/tidb-community-server-{version}-linux-{arch}.tar.gz
    ```

    > **Tip:**
    >
    > `{version}` in the link indicates the version number of TiDB and `{arch}` indicates the architecture of the system, which can be `amd64` or `arm64`. For example, the download link for `v8.1.2` in the `amd64` architecture is `https://download.pingcap.com/tidb-community-toolkit-v8.1.2-linux-amd64.tar.gz`.

2. In the extracted files, locate `prometheus-v{version}-linux-amd64.tar.gz` and extract it.

    ```bash
    tar -xzf prometheus-v{version}-linux-amd64.tar.gz
    ```
### Step 3. Create a new Prometheus package that TiUP can use

1. Copy the files extracted in [Step 1](#step-1-download-a-new-prometheus-installation-package-from-the-prometheus-website), and then use the copied files to replace the files in the `./prometheus-v{version}-linux-amd64/prometheus` directory extracted in [Step 2](#step-2-download-the-prometheus-installation-package-provided-by-tidb).
2. Recompress the `./prometheus-v{version}-linux-amd64` directory and name the new compressed package as `prometheus-v{new-version}.tar.gz`, where `{new-version}` can be specified according to your need.

    ```bash
    cd prometheus-v{version}-linux-amd64
    tar -zcvf ../prometheus-v{new-version}.tar.gz ./
    ```
### Step 4. Upgrade Prometheus using the newly created Prometheus package

Execute the following command to upgrade Prometheus:

```bash
tiup cluster patch <cluster-name> prometheus-v{new-version}.tar.gz -R prometheus --overwrite
```

After the upgrade, you can go to the home page of the Prometheus server (usually at `http://<Prometheus-server-host-name>:9090`), click **Status** in the top navigation menu, and then open the **Runtime & Build Information** page to check the Prometheus version and confirm whether the upgrade is successful.
