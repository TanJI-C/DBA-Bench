# Diagnosis and maintenance roadmap items

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-roadmap.md`
- Source Title: `TiDB Cloud Roadmap`
- Source Heading Path: `TiDB Cloud Roadmap > Diagnosis and maintenance`
- Source Line Ranges: `78-134`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dashboard`, `tidb`, `tikv`, `tiflash`
- Topic Tags: `diagnosis`, `reports`, `health-check`, `sql-tuning`, `htap`, `monitoring`, `tracing`, `offline-analysis`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0093_9af52efc5c`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-roadmap.md#diagnosis-and-maintenance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2c2caf508956aad4c944ac6bc1f175750b6a28cd5b1640b0f6aeb9f1f72b1c11`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-roadmap#diagnosis-and-maintenance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-roadmap.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Cloud roadmap items about diagnosis and maintenance, including reports, SQL tuning for HTAP workloads, diagnosis data accessibility, or service tracing.
- Retrieval Keywords: Diagnosis and maintenance, Cluster health report, Cluster status comparison report, Cluster system check report, SQL tuning for HTAP workloads, TiFlash, TiKV, SQL execution overview, applications perspective, Access diagnosis data online in real time, Access diagnosis data offline, data reconstruction, TiDB Cloud service tracing, service availability
- Follow-up Guidance: The source describes reports, data accessibility, and tracing capabilities for diagnosis and maintenance, including assessment on service availability from the perspective of users.
- Classification Note: This is classified as diagnosis because the official content centers on cluster analysis, diagnosis reports, SQL tuning visibility, diagnosis data access, and service tracing.

## Official Source Content

## Diagnosis and maintenance

<table>
<thead>
  <tr>
    <th>Domain</th>
    <th>Feature</th>
    <th>Description</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td rowspan="3">Self-service cluster analysis and diagnosis using reports</td>
    <td>✅ Cluster health report.</td>
    <td>Provide diagnosis and analysis reports for several different usage scenarios.</td>
  </tr>
  <tr>
    <td>✅ Cluster status comparison report.</td>
    <td>Locate cluster failures for some scenarios and provide recommended solutions.</td>
  </tr>
  <tr>
    <td>✅ Cluster system check report.</td>
    <td>Provide cluster key status summary for some scenarios.</td>
  </tr>
  <tr>
    <td rowspan="2">SQL tuning for HTAP workloads</td>
    <td>Provide suggestions on optimizing SQL for TiFlash and TiKV in HTAP workloads.</td>
    <td>Provide a dashboard that displays a SQL execution overview from the perspective of applications in HTAP workloads.</td>
  </tr>
  <tr>
    <td>Provide SQL execution information from the perspective of applications.</td>
    <td>For one or several HTAP scenarios, provide suggestions on SQL optimization.</td>
  </tr>
  <tr>
    <td rowspan="3">Cluster diagnosis data accessibility </td>
    <td>✅ Access diagnosis data online in real time.</td>
    <td>Integrate with various monitoring and diagnosis systems to improve the real-time data access capability.</td>
  </tr>
  <tr>
    <td>✅ Access diagnosis data offline.</td>
    <td>Provide offline data access for large-scale diagnosis, analysis, and tuning.</td>
  </tr>
  <tr>
    <td>Build logic for data reconstruction.</td>
    <td>Improve data stability and build logic for data reconstruction.</td>
  </tr>
  <tr>
    <td>TiDB Cloud service tracing</td>
    <td>Build the monitoring links for each component of TiDB Cloud service.</td>
    <td>
      <ul><li>Build the tracing links for each component of TiDB Cloud service in user scenarios.</li>
      <li>Provide assessment on service availability from the perspective of users.</li></ul>
    </td>
  </tr>
</tbody>
</table>
