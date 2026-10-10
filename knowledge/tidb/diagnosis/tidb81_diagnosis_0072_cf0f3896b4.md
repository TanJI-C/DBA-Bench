# Statement summary troubleshooting query examples

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/statement-summary-tables.md`
- Source Title: `Statement Summary Tables`
- Source Heading Path: `Statement Summary Tables > Troubleshooting examples > Could high SQL latency be caused by the server end? | Statement Summary Tables > Troubleshooting examples > Which categories of SQL statements consume the longest total time?`
- Source Line Ranges: `271-324`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `statement-summary`, `troubleshooting`, `latency`, `qps`, `history-table`, `query-analysis`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0072_cf0f3896b4`
- Source ID: `tidb-docs-8.1:statement-summary-tables.md#could-high-sql-latency-be-caused-by-the-server-end`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `96e7a48c102568481aed7cd8c8e14fccc7e5dd0d40ff9e0b42fdc0c1578e5514`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/statement-summary-tables#could-high-sql-latency-be-caused-by-the-server-end
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/statement-summary-tables.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing whether slow point queries are caused by the TiDB server or when identifying which SQL categories have the highest total time during a specific history window.
- Retrieval Keywords: information_schema.statements_summary, information_schema.statements_summary_history, avg_latency, sum_latency, exec_count, query_sample_text, digest_text LIKE 'select * from employee%', summary_begin_time='2020-01-02 10:00:00', ORDER BY sum_latency DESC LIMIT 3, QPS decrease significantly from 10:00 to 10:30, server end is not the cause, client or the network
- Follow-up Guidance: The content also notes that if avg_latency values such as 1ms and 0.3ms are within the normal range, you can troubleshoot with the client or the network.
- Classification Note: This is classified as diagnosis because it provides troubleshooting query examples using statement summary tables to judge server-side latency and rank SQL categories by total time consumption.

## Official Source Content

### Could high SQL latency be caused by the server end?

In this example, the client shows slow performance with point queries on the `employee` table. You can perform a fuzzy search on SQL texts:

```sql
SELECT avg_latency, exec_count, query_sample_text
    FROM information_schema.statements_summary
    WHERE digest_text LIKE 'select * from employee%';
```

 `1ms` and `0.3ms` are considered within the normal range of `avg_latency`. Therefore, it can be concluded that the server end is not the cause. You can troubleshoot with the client or the network.

```sql
+-------------+------------+------------------------------------------+
| avg_latency | exec_count | query_sample_text                        |
+-------------+------------+------------------------------------------+
|     1042040 |          2 | select * from employee where name='eric' |
|      345053 |          3 | select * from employee where id=3100     |
+-------------+------------+------------------------------------------+
2 rows in set (0.00 sec)
```
### Which categories of SQL statements consume the longest total time?

If the QPS decrease significantly from 10:00 to 10:30, you can find out the three categories of SQL statements with the longest time consumption from the history table:

```sql
SELECT sum_latency, avg_latency, exec_count, query_sample_text
    FROM information_schema.statements_summary_history
    WHERE summary_begin_time='2020-01-02 10:00:00'
    ORDER BY sum_latency DESC LIMIT 3;
```

The result shows that the following three categories of SQL statements consume the longest time in total, which need to be optimized with high priority.

```sql
+-------------+-------------+------------+-----------------------------------------------------------------------+
| sum_latency | avg_latency | exec_count | query_sample_text                                                     |
+-------------+-------------+------------+-----------------------------------------------------------------------+
|     7855660 |     1122237 |          7 | select avg(salary) from employee where company_id=2013                |
|     7241960 |     1448392 |          5 | select * from employee join company on employee.company_id=company.id |
|     2084081 |     1042040 |          2 | select * from employee where name='eric'                              |
+-------------+-------------+------------+-----------------------------------------------------------------------+
3 rows in set (0.00 sec)
```
