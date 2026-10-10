# Data backup and migration roadmap items

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-roadmap.md`
- Source Title: `TiDB Cloud Roadmap`
- Source Heading Path: `TiDB Cloud Roadmap > Data backup and migration`
- Source Line Ranges: `135-172`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `br`
- Topic Tags: `backup`, `restore`, `migration`, `replication`, `kafka`, `mysql`, `rds`, `aurora`, `snapshots`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0108_2eb1fb78d8`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-roadmap.md#data-backup-and-migration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `88cdd20a4df2f78bdb91f33a15411ba53252cd23f27b7b0d8a966efe4b10b4a9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-roadmap#data-backup-and-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-roadmap.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Cloud roadmap information about backup, restore, replication, or migration involving TiCDC, BR, Kafka, MySQL, RDS, Aurora, EBS, or persistent disk snapshots.
- Retrieval Keywords: Data backup and migration, TiDB Cloud supports replicating data to Kafka/MySQL, TiCDC-based data replication, Kafka, MySQL compatible databases, Support EBS snapshot-based backup and restore, BR service, AWS EBS, Google Cloud persistent disk snapshots, Online data migration, full data migration from Amazon Relational Database Service (RDS), incremental data migration from RDS, Aurora
- Follow-up Guidance: The source includes roadmap items for replication to Kafka/MySQL, backup and restore based on AWS EBS or Google Cloud persistent disk snapshots, and full or incremental migration from MySQL services such as Amazon RDS and Aurora.
- Classification Note: This is classified as data_pipeline because the official content covers data replication, backup and restore, and online data migration workflows in TiDB Cloud.

## Official Source Content

## Data backup and migration

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
    <td>Data replication to Kafka/MySQL</td>
    <td>✅ TiDB Cloud supports replicating data to Kafka/MySQL.</td>
    <td>TiDB Cloud supports TiCDC-based data replication to Kafka and MySQL compatible databases.</td>
  </tr>
  <tr>
    <td>Backup and Restore</td>
    <td>✅ Support EBS snapshot-based backup and restore.</td>
    <td>BR service on TiDB Cloud uses EBS snapshot-based backup and restore.</td>
  </tr>
  <tr>
    <td>Backup and restore</td>
    <td>Backup and restore service based on AWS EBS or Google Cloud persistent disk snapshots.</td>
    <td>Provide backup and restore service on the cloud based on AWS EBS or Google Cloud persistent disk snapshots.</td>
  </tr>
  <tr>
    <td rowspan="2">Online data migration</td>
    <td>✅ Support full data migration from Amazon Relational Database Service (RDS).</td>
    <td>Full data migration from RDS to TiDB Cloud.</td>
  </tr>
  <tr>
    <td>Support incremental data migration from RDS.</td>
    <td>Full and incremental data migration from MySQL services such as Amazon RDS and Aurora to TiDB Cloud.</td>
  </tr>
</tbody>
</table>
