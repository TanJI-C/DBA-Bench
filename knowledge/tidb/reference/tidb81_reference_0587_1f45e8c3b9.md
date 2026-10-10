# EXPLAIN ANALYZE RU consumption, common execution info, and references

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-explain-analyze.md`
- Source Title: `EXPLAIN ANALYZE | TiDB SQL Statement Reference`
- Source Heading Path: `EXPLAIN ANALYZE > Execution information of operators > RU (Request Unit) consumption | EXPLAIN ANALYZE > Execution information of operators > Other common execution information | EXPLAIN ANALYZE > MySQL compatibility | EXPLAIN ANALYZE > See also`
- Source Line Ranges: `284-354`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `pd`, `tidb`, `tikv`
- Topic Tags: `explain-analyze`, `request-unit`, `resource-control`, `execution-info`, `coprocessor`, `tikv-task`, `mysql-compatibility`, `query-plan`, `references`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0587_1f45e8c3b9`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-explain-analyze.md#ru-request-unit-consumption`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8464f6d6cce75da110a6ee2a7d45ecd74e6e76b3a0483099f3525d20224ee883`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze#ru-request-unit-consumption
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-explain-analyze.md

## Retrieval Guidance

- Use When: Use this when a user needs to interpret RU consumption or common execution info fields in EXPLAIN ANALYZE output, including differences between cop_task and tikv_task.
- Retrieval Keywords: EXPLAIN ANALYZE RU, Request Unit RU, execution info RU:273.842670, executeInfo, cop_task, tikv_task, total_process_time, total_wait_time, tikv_wall_time, scan_detail, total_process_keys_size, coprocessor cache, MySQL compatibility, Understanding the Query Execution Plan, TRACE, ANALYZE TABLE
- Follow-up Guidance: The source also points to Understanding the Query Execution Plan, EXPLAIN, ANALYZE TABLE, and TRACE as related references.
- Classification Note: This is reference content because it defines RU consumption shown in EXPLAIN ANALYZE, describes common execution information fields, notes MySQL compatibility, and links to related documentation.

## Official Source Content

### RU (Request Unit) consumption

[Request Unit (RU)](https://docs.pingcap.com/tidb/stable/tidb-resource-control#what-is-request-unit-ru) is a unified abstraction unit of system resources, which is defined in TiDB resource control. The `execution info` of the top-level operator shows the overall RU consumption of this particular SQL statement.

```
RU:273.842670
```

> **Note:**
>
> This value shows the actual RUs consumed by this execution. The same SQL statement might consume different amounts of RUs each time it is executed due to the effects of caching (for example, [coprocessor cache](https://docs.pingcap.com/tidb/stable/coprocessor-cache)).

You can calculate the RU from the other values in `EXPLAIN ANALYZE`, specifically the `execution info` column. For example:

```json
'executeInfo':
   time:2.55ms, 
   loops:2, 
   RU:0.329460, 
   Get:{
       num_rpc:1,
       total_time:2.13ms
   }, 
   total_process_time: 231.5µs,
   total_wait_time: 732.9µs, 
   tikv_wall_time: 995.8µs,
   scan_detail: {
      total_process_keys: 1, 
      total_process_keys_size: 150, 
      total_keys: 1, 
      get_snapshot_time: 691.7µs,
      rocksdb: {
          block: {
              cache_hit_count: 2,
              read_count: 1,
              read_byte: 8.19 KB,
              read_time: 10.3µs
          }
      }
  },
```

The base costs are defined in the [`tikv/pd` source code](https://github.com/tikv/pd/blob/aeb259335644d65a97285d7e62b38e7e43c6ddca/client/resource_group/controller/config.go#L58C19-L67) and the calculations are performed in the [`model.go`](https://github.com/tikv/pd/blob/54219d649fb4c8834cd94362a63988f3c074d33e/client/resource_group/controller/model.go#L107) file.

If you are using TiDB v7.1, the calculation is the sum of `BeforeKVRequest()` and `AfterKVRequest()` in `pd/pd-client/model.go`, that is:

```
before key/value request is processed:
      consumption.RRU += float64(kc.ReadBaseCost) -> kv.ReadBaseCost * rpc_nums

after key/value request is processed:
      consumption.RRU += float64(kc.ReadBytesCost) * readBytes -> kc.ReadBytesCost * total_process_keys_size
      consumption.RRU += float64(kc.CPUMsCost) * kvCPUMs -> kc.CPUMsCost * total_process_time
```

For writes and batch gets, the calculation is similar with different base costs.
### Other common execution information

The Coprocessor operators usually contain two parts of execution time information: `cop_task` and `tikv_task`. `cop_task` is the time recorded by TiDB, and it is from the moment that the request is sent to the server to the moment that the response is received. `tikv_task` is the time recorded by TiKV Coprocessor itself. If there is much difference between the two, it might indicate that the time spent waiting for the response is too long, or the time spent on gRPC or network is too long.
## MySQL compatibility

`EXPLAIN ANALYZE` is a feature of MySQL 8.0, but both the output format and the potential execution plans in TiDB differ substantially from MySQL.
## See also

* [Understanding the Query Execution Plan](https://docs.pingcap.com/tidb/stable/explain-overview)
* [EXPLAIN](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain)
* [ANALYZE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table)
* [TRACE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-trace)
