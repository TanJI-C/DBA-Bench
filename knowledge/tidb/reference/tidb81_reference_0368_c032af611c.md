# Network ports, storage sizing, and browser requirements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/hardware-and-software-requirements.md`
- Source Title: `Software and Hardware Recommendations`
- Source Heading Path: `Software and Hardware Recommendations > Network requirements | Software and Hardware Recommendations > Storage requirements | Software and Hardware Recommendations > Web browser requirements`
- Source Line Ranges: `215-300`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tidb`, `tikv`, `tiflash`, `ticdc`, `tiup`, `dashboard`
- Topic Tags: `network-ports`, `storage-sizing`, `disk-usage`, `filesystem`, `browser-support`, `monitoring`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0368_c032af611c`
- Source ID: `tidb-docs-8.1:hardware-and-software-requirements.md#network-requirements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `81c2f9393a7527eef1834fa6f1120be8f2c010586c8c90337d225ad7269879f3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/hardware-and-software-requirements#network-requirements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/hardware-and-software-requirements.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB default network ports, storage sizing and healthy disk usage thresholds, supported file systems, or browser requirements for Grafana-based metrics visualization.
- Retrieval Keywords: TiDB 4000 application and DBA tools, TiDB 10080 status port, TiKV 20160 communication port, TiKV 20180 status port, PD 2379 communication port between TiDB and PD, PD 2380 inter-node communication port, TiFlash 9000 TCP service port, TiFlash 3930 RAFT and Coprocessor service port, TiFlash 20170 Proxy service port, TiFlash 20292 Prometheus pull TiFlash Proxy metrics, TiFlash 8234 Prometheus pull TiFlash metrics, Pump 8250, Drainer 8249, TiCDC 8300, Prometheus 9090, NgMonitoring 12020, Node_exporter 9100, Blackbox_exporter 9115, Grafana 3000, Alertmanager 9093, Alertmanager 9094, storage requirements, healthy disk usage, TiDB at least 30 GB for the log disk, tidb_ddl_enable_fast_reorg, IMPORT INTO, Set a temporary space for a TiDB instance, PD at least 20 GB for the data disk and for the log disk, TiKV at least 100 GB for the data disk and for the log disk, TiFlash at least 100 GB for the data disk and at least 30 GB for the log disk, TiUP control machine no more than 1 GB space, TiUP /tmp temporary space less than 1 MB, Ngmonitoring Conprof, Top SQL 30 x 50 MB x Number of components, XFS and Ext4 file systems, Grafana browser requirements, Microsoft Edge Safari Chrome Firefox Javascript enabled
- Follow-up Guidance: The source also states that starting from v6.5.0, Fast Online DDL controlled by tidb_ddl_enable_fast_reorg is enabled by default, and detailed temporary space configuration is referenced in Set a temporary space for a TiDB instance.
- Classification Note: This is classified as reference content because it provides default ports, disk space requirements, healthy usage limits, supported file systems, and browser support details.

## Official Source Content

## Network requirements

As an open-source distributed SQL database, TiDB requires the following network port configuration to run. Based on the TiDB deployment in actual environments, the administrator can open relevant ports in the network side and host side.

| Component | Default Port | Description |
| :--:| :--: | :-- |
| TiDB |  4000  | the communication port for the application and DBA tools |
| TiDB | 10080  | the communication port to report TiDB status |
| TiKV | 20160 | the TiKV communication port |
| TiKV |  20180 | the communication port to report TiKV status |
| PD | 2379 | the communication port between TiDB and PD |
| PD | 2380 | the inter-node communication port within the PD cluster |
| TiFlash | 9000 | the TiFlash TCP service port |
| TiFlash | 3930 | the TiFlash RAFT and Coprocessor service port |
| TiFlash | 20170 |the TiFlash Proxy service port |
| TiFlash | 20292 | the port for Prometheus to pull TiFlash Proxy metrics |
| TiFlash | 8234 | the port for Prometheus to pull TiFlash metrics |
| Pump | 8250 | the Pump communication port |
| Drainer | 8249 | the Drainer communication port |
| TiCDC | 8300 | the TiCDC communication port |
| Monitoring | 9090 | the communication port for the Prometheus service|
| Monitoring | 12020 | the communication port for the NgMonitoring service|
| Node_exporter | 9100 | the communication port to report the system information of every TiDB cluster node |
| Blackbox_exporter | 9115 | the Blackbox_exporter communication port, used to monitor the ports in the TiDB cluster |
| Grafana | 3000 | the port for the external Web monitoring service and client (Browser) access|
| Alertmanager | 9093 | the port for the alert web service |
| Alertmanager | 9094 | the alert communication port |
## Storage requirements

<table>
<thead>
  <tr>
    <th>Component</th>
    <th>Disk space requirement</th>
    <th>Healthy disk usage</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>TiDB</td>
    <td><ul><li>At least 30 GB for the log disk</li><li>Starting from v6.5.0, Fast Online DDL (controlled by the <a href="https://docs.pingcap.com/tidb/v8.1/system-variables#tidb_ddl_enable_fast_reorg-new-in-v630">tidb_ddl_enable_fast_reorg</a> variable) is enabled by default to accelerate DDL operations, such as adding indexes. If DDL operations involving large objects exist in your application, or you want to use <a href="https://docs.pingcap.com/tidb/v8.1/sql-statement-import-into">IMPORT INTO</a> to import data, it is highly recommended to prepare additional SSD disk space for TiDB (100 GB or more). For detailed configuration instructions, see <a href="https://docs.pingcap.com/tidb/v8.1/check-before-deployment#set-temporary-spaces-for-tidb-instances-recommended">Set a temporary space for a TiDB instance</a></li></ul></td>
    <td>Lower than 90%</td>
  </tr>
  <tr>
    <td>PD</td>
    <td>At least 20 GB for the data disk and for the log disk, respectively</td>
    <td>Lower than 90%</td>
  </tr>
  <tr>
    <td>TiKV</td>
    <td>At least 100 GB for the data disk and for the log disk, respectively</td>
    <td>Lower than 80%</td>
  </tr>
  <tr>
    <td>TiFlash</td>
    <td>At least 100 GB for the data disk and at least 30 GB for the log disk, respectively</td>
    <td>Lower than 80%</td>
  </tr>
  <tr>
    <td>TiUP</td>
    <td><ul><li>Control machine: No more than 1 GB space is required for deploying a TiDB cluster of a single version. The space required increases if TiDB clusters of multiple versions are deployed.</li><li>Deployment servers (machines where the TiDB components run): TiFlash occupies about 700 MB space and other components (such as PD, TiDB, and TiKV) occupy about 200 MB space respectively. During the cluster deployment process, the TiUP cluster requires less than 1 MB of temporary space (<code>/tmp</code> directory) to store temporary files.</li></ul></td>
    <td>N/A</td>
  </tr>
  <tr>
    <td>Ngmonitoring</td>
    <td><ul><li>Conprof: 3 x 1 GB x Number of components (each component occupies about 1 GB per day, 3 days in total) + 20 GB reserved space</li><li>Top SQL: 30 x 50 MB x Number of components (each component occupies about 50 MB per day, 30 days in total)</li><li>Conprof and Top SQL share the reserved space</li></ul></td>
    <td>N/A</td>
  </tr>
</tbody>
</table>

TiDB supports the XFS and Ext4 file systems. Other file systems are not recommended for production environments.  
## Web browser requirements

TiDB relies on [Grafana](https://grafana.com/) to provide visualization of database metrics. A recent version of Microsoft Edge, Safari, Chrome or Firefox with Javascript enabled is sufficient.
