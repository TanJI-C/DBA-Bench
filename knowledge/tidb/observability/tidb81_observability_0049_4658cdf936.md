# PD cluster and operator metrics

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/grafana-pd-dashboard.md`
- Source Title: `Key Monitoring Metrics of PD`
- Source Heading Path: `Key Monitoring Metrics of PD > Cluster | Key Monitoring Metrics of PD > Operator`
- Source Line Ranges: `29-53`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `dashboard`
- Topic Tags: `cluster`, `operator`, `tso`, `id allocation`, `scheduler`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0049_4658cdf936`
- Source ID: `tidb-docs-8.1:grafana-pd-dashboard.md#cluster`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e95f1bb4cf209017ffd56b512fd5fea1be0c7bed93657052a92ac404d30e29c2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/grafana-pd-dashboard#cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/grafana-pd-dashboard.md

## Retrieval Guidance

- Use When: Use this when you need PD cluster settings or operator lifecycle metrics from the PD dashboard.
- Retrieval Keywords: Cluster, Operator, PD scheduler config, Cluster ID, Current TSO, Current ID allocation, Region label isolation level, Label distribution, Store Limit, Schedule operator create, Schedule operator check, Schedule operator finish, Schedule operator timeout, Schedule operator replaced or canceled, Schedule operators count by state, Operator finish duration, Operator step duration
- Follow-up Guidance: This section describes the Cluster and Operator panels and the metrics they expose.
- Classification Note: This chunk is an observability reference for PD cluster configuration values and operator state metrics.

## Official Source Content

## Cluster

- PD scheduler config: The list of PD scheduler configurations
- Cluster ID: The unique identifier of the cluster
- Current TSO: The physical part of current allocated TSO
- Current ID allocation: The maximum allocatable ID for new store/peer
- Region label isolation level: The number of Regions in different label levels
- Label distribution: The distribution status of the labels in the cluster
- Store Limit: The flow control limitation of scheduling on the Store

![PD Dashboard - Cluster metrics](/media/pd-dashboard-cluster-v4.png)
## Operator

- Schedule operator create: The number of newly created operators per type
- Schedule operator check: The number of checked operator per type. It mainly checks whether the current step is finished; if yes, it returns the next step to be executed
- Schedule operator finish: The number of finished operators per type
- Schedule operator timeout: The number of timeout operators per type
- Schedule operator replaced or canceled: The number of replaced or canceled operators per type
- Schedule operators count by state: The number of operators per state
- Operator finish duration: The maximum duration of finished operators
- Operator step duration: The maximum duration of finished operator steps

![PD Dashboard - Operator metrics](/media/pd-dashboard-operator-v4.png)
