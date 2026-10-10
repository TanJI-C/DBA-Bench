# Built-in changefeed alert conditions and recommended actions

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/monitor-built-in-alerting.md`
- Source Title: `TiDB Cloud Built-in Alerting`
- Source Heading Path: `TiDB Cloud Built-in Alerting > TiDB Cloud built-in alert conditions > Changefeed alerts`
- Source Line Ranges: `88-94`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`
- Topic Tags: `alerts`, `changefeed`, `latency`, `failed-status`, `warning-status`, `recommended-actions`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0093_6d9caf4894`
- Source ID: `tidb-docs-8.1:tidb-cloud/monitor-built-in-alerting.md#changefeed-alerts`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f1d86bd6b7aab5bf3dcef05b398cf664eda7c7f386006cd38b3a3d684e6527dc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-built-in-alerting#changefeed-alerts
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/monitor-built-in-alerting.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB Cloud built-in changefeed alerts, including latency exceeding 600 seconds or a changefeed status of `FAILED` or `WARNING`.
- Retrieval Keywords: Changefeed alerts, The changefeed latency exceeds 600 seconds, The changefeed status is `FAILED`, The changefeed status is `WARNING`, Changefeed page, Changefeed Detail page, TiDB Cloud Support, downstream or network is abnormal, Tables lack indexes if the downstream is RDS, scale up the changefeed
- Follow-up Guidance: The content says to check the changefeed status on the Changefeed page and Changefeed Detail page of the TiDB Cloud console for error messages, and to contact TiDB Cloud Support if the problem cannot be fixed from your side.
- Classification Note: This is classified as observability for the cloud component because the official content lists built-in alert conditions and recommended diagnostic actions for TiDB Cloud changefeeds.

## Official Source Content

### Changefeed alerts

| Condition                                   | Recommended Action                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|:--------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| The changefeed latency exceeds 600 seconds. | Check the changefeed status on the **Changefeed** page and **Changefeed Detail** page of the TiDB Cloud console, where you can find some error messages to help diagnose this issue. <br/> Possible reasons that can trigger this alert include:<ul><li>The overall traffic in the upstream has increased, causing the existing changefeed specification to be insufficient to handle it. If the traffic increase is temporary, the changefeed latency will automatically recover after the traffic returns to normal. If the traffic increase is continuous, you need to scale up the changefeed.</li><li>The downstream or network is abnormal. In this case, resolve this abnormality first.</li><li>Tables lack indexes if the downstream is RDS, which might cause low write performance and high latency. In this case, you need to add the necessary indexes to the upstream or downstream.</li></ul>If the problem cannot be fixed from your side, you can contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for further assistance. |
| The changefeed status is `FAILED`.                 | Check the changefeed status on the **Changefeed** page and **Changefeed Detail** page of the TiDB Cloud console, where you can find some error messages to help diagnose this issue. <br/> If the problem cannot be fixed from your side, you can contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for further assistance.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| The changefeed status is `WARNING`.              | Check the changefeed status on the **Changefeed** page and **Changefeed Detail** page of the TiDB Cloud console, where you can find some error messages to help diagnose this issue. <br/> If the problem cannot be fixed from your side, you can contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for further assistance.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
