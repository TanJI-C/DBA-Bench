# Query PD scheduling status with metrics and pd-ctl

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/pd-scheduling-best-practices.md`
- Source Title: `PD Scheduling Best Practices`
- Source Heading Path: `PD Scheduling Best Practices > Query scheduling status | PD Scheduling Best Practices > Query scheduling status > Operator status | PD Scheduling Best Practices > Query scheduling status > Balance status | PD Scheduling Best Practices > Query scheduling status > Hot Region status | PD Scheduling Best Practices > Query scheduling status > Region health`
- Source Line Ranges: `110-162`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `dashboard`
- Topic Tags: `metrics`, `pd-ctl`, `operators`, `balance-status`, `hot-regions`, `region-health`, `grafana`, `monitoring`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0012_805f85cb50`
- Source ID: `tidb-docs-8.1:best-practices/pd-scheduling-best-practices.md#query-scheduling-status`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ca5229c4f3229838a5d9a938664c252ad8875102d529a9126fcffd0e02aa8895`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/pd-scheduling-best-practices#query-scheduling-status
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/pd-scheduling-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks how to inspect PD scheduling status, operator activity, balance metrics, hot regions, or abnormal region health with Grafana or pd-ctl.
- Retrieval Keywords: Grafana PD/Operator, Schedule operator create, Operator finish duration, Operator step duration, operator show, operator show [admin | leader | region], Grafana PD/Statistics - Balance, Store leader/region score, Store leader/region count, Store available, Grafana PD/Statistics - hotspot, hot read, hot write, hot store, region topread [limit], region topwrite [limit], Grafana PD/Cluster/Region health, region check miss-peer, region check extra-peer, region check down-peer, region check pending-peer
- Follow-up Guidance: The source also notes that scheduling status can be checked through logs, and refers to PD Monitoring Metrics and PD Control for more details.
- Classification Note: This chunk is classified as observability because it lists the Grafana panels, metrics, and pd-ctl queries used to observe operator status, balance status, hot region status, and region health.

## Official Source Content

## Query scheduling status

You can check the status of scheduling system through metrics, pd-ctl and logs. This section briefly introduces the methods of metrics and pd-ctl. Refer to [PD Monitoring Metrics](https://docs.pingcap.com/tidb/stable/grafana-pd-dashboard) and [PD Control](https://docs.pingcap.com/tidb/stable/pd-control) for details.
### Operator status

The **Grafana PD/Operator** page shows the metrics about operators, among which:

- Schedule operator create: Operator creating information
- Operator finish duration: Execution time consumed by each operator
- Operator step duration: Execution time consumed by the operator step

You can query operators using pd-ctl with the following commands:

- `operator show`: Queries all operators generated in the current scheduling task
- `operator show [admin | leader | region]`: Queries operators by type
### Balance status

The **Grafana PD/Statistics - Balance** page shows the metrics about load balancing, among which:

- Store leader/region score: Score of each store
- Store leader/region count: The number of leaders/regions in each store
- Store available: Available storage on each store

You can use store commands of pd-ctl to query balance status of each store.
### Hot Region status

The **Grafana PD/Statistics - hotspot** page shows the metrics about hot regions, among which:

- Hot write region's leader/peer distribution: the leader/peer distribution in hot write regions
- Hot read region's leader distribution: the leader distribution in hot read regions

You can also query the status of hot regions using pd-ctl with the following commands:

- `hot read`: Queries hot read regions
- `hot write`: Queries hot write regions
- `hot store`: Queries the distribution of hot regions by store
- `region topread [limit]`: Queries the region with top read traffic
- `region topwrite [limit]`: Queries the region with top write traffic
### Region health

The **Grafana PD/Cluster/Region health** panel shows the metrics about regions in abnormal states.

You can query the list of regions in abnormal states using pd-ctl with region check commands:

- `region check miss-peer`: Queries regions without enough peers
- `region check extra-peer`: Queries regions with extra peers
- `region check down-peer`: Queries regions with down peers
- `region check pending-peer`: Queries regions with pending peers
