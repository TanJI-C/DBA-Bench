# Using the Prometheus API for metric queries and reporting

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/grafana-monitor-best-practices.md`
- Source Title: `Best Practices for Monitoring TiDB Using Grafana`
- Source Heading Path: `Best Practices for Monitoring TiDB Using Grafana > Grafana tips > Tip 7: Use the API of Prometheus to obtain the result of query expressions | Best Practices for Monitoring TiDB Using Grafana > Summary`
- Source Line Ranges: `147-205`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dashboard`, `tidb`, `tikv`, `pd`
- Topic Tags: `prometheus-api`, `query-range`, `automation`, `reporting`, `health-checks`, `metrics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0011_0d38ff3de8`
- Source ID: `tidb-docs-8.1:best-practices/grafana-monitor-best-practices.md#tip-7-use-the-api-of-prometheus-to-obtain-the-result-of-query-expressions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b2217dcf4d1b80250f8d342d776f04a1f3a1de1c9c4fa516b9022bd89282d5c9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/grafana-monitor-best-practices#tip-7-use-the-api-of-prometheus-to-obtain-the-result-of-query-expressions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/grafana-monitor-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Prometheus API example that Grafana uses, especially for query_range requests, automated reporting, cluster status collection, or regular health inspection of important metrics.
- Retrieval Keywords: Use the API of Prometheus to obtain the result of query expressions, Grafana obtains data through the API of Prometheus, api/v1/query_range, curl -u user:pass, http://__grafana_ip__:3000/api/datasources/proxy/1/api/v1/query_range, sum(tikv_engine_size_bytes, by (instance), start end step, cluster size and status, total amount of QPS per day, peak value of QPS per day, response time per day, regular health inspection, resultType matrix, status success
- Follow-up Guidance: The chunk includes a `query_range` curl example and states that the API can be used to automatically obtain cluster size and status, generate report data such as daily QPS totals and peaks, and perform regular health inspection on important metrics.
- Classification Note: This chunk is classified as observability because it covers programmatic metric retrieval and reporting through the Prometheus API used by Grafana.

## Official Source Content

### Tip 7: Use the API of Prometheus to obtain the result of query expressions

Grafana obtains data through the API of Prometheus and you can use this API to obtain information as well. In addition, it also has the following usages:

- Automatically obtains information such as the cluster size and status.
- Makes minor changes to the expression to provide information for the report, such as counting the total amount of QPS per day, the peak value of QPS per day, and the response time per day.
- Performs regular health inspection on the important metrics.

The API of Prometheus is shown as follows:

![The API of Prometheus](/media/best-practices/prometheus-api-interface.jpg)

```bash
curl -u user:pass 'http://__grafana_ip__:3000/api/datasources/proxy/1/api/v1/query_range?query=sum(tikv_engine_size_bytes%7Binstancexxxxxxxxx20180%22%7D)%20by%20(instance)&start=1565879269&end=1565882869&step=30' |python -m json.tool
```

```
{
    "data": {
        "result": [
            {
                "metric": {
                    "instance": "xxxxxxxxxx:20180"
                },
                "values": [
                    [
                        1565879269,
                        "1006046235280"
                    ],
                    [
                        1565879299,
                        "1006057877794"
                    ],
                    [
                        1565879329,
                        "1006021550039"
                    ],
                    [
                        1565879359,
                        "1006021550039"
                    ],
                    [
                        1565882869,
                        "1006132630123"
                    ]
                ]
            }
        ],
        "resultType": "matrix"
    },
    "status": "success"
}
```
## Summary

The Grafana + Prometheus monitoring platform is a very powerful tool. Making good use of it can improve efficiency, saving you a lot of time on analyzing the status of the TiDB cluster. More importantly, it can help you diagnose problems. This tool is very useful in the operation and maintenance of TiDB clusters, especially when there is a large amount of data.
