# Using PD microservices with Operator, compatibility, and bottleneck checks

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-microservices.md`
- Source Title: `PD Microservices`
- Source Heading Path: `PD Microservices > Usage | PD Microservices > Tool compatibility | PD Microservices > FAQs`
- Source Line Ranges: `41-68`
- Source Scope: `kubernetes`
- Primary Component: `pd`
- Related Components: `operator`, `tidb`
- Topic Tags: `deployment`, `operator`, `restart`, `tso`, `scheduling`, `fallback`, `configuration`, `tool-compatibility`, `monitoring`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0190_cd9dbe553c`
- Source ID: `tidb-docs-8.1:pd-microservices.md#usage`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4e5019aeabb43ded85ec84dca46258173baf5217f078e94768b923503810412e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-microservices#usage
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-microservices.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how PD microservices are used with TiDB Operator, how `scheduling` fallback behaves, or how to identify whether PD is a performance bottleneck.
- Retrieval Keywords: TiDB Operator, Deploy PD microservices, Configure PD microservices, Modify PD microservices, Scale PD microservice components, enable microservices and restart PD, PD stops allocating TSO, deploy the tso microservice, scheduling microservice is deployed, scheduling function is still provided by PD, dynamic switching, enable-scheduling-fallback, defaults to true, pd-ctl config set enable-scheduling-fallback false, binary versions of the scheduling microservice and PD are different, Tool compatibility, data import, export, replication tools, FAQs, PD becomes a performance bottleneck, Grafana PD panel, TiDB - PD server TSO handle time, Heartbeat - TiKV side heartbeat statistics, pending items
- Follow-up Guidance: The chunk points to TiDB Operator documents for deploying, configuring, modifying, and scaling PD microservice components, and it notes the Grafana PD panel metrics used to judge whether PD is a performance bottleneck.
- Classification Note: This is classified as operation because the content describes deployment and runtime behavior with TiDB Operator, fallback configuration, tool compatibility, and monitoring checks.

## Official Source Content

## Usage

Currently, PD microservices can be deployed using TiDB Operator.

For detailed information on using TiDB Operator, see the following documents:

- [Deploy PD microservices](https://docs.pingcap.com/tidb-in-kubernetes/v1.6/configure-a-tidb-cluster#enable-pd-microservices)
- [Configure PD microservices](https://docs.pingcap.com/tidb-in-kubernetes/v1.6/configure-a-tidb-cluster#configure-pd-microservices)
- [Modify PD microservices](https://docs.pingcap.com/tidb-in-kubernetes/v1.6/modify-tidb-configuration#modify-pd-microservice-configuration)
- [Scale PD microservice components](https://docs.pingcap.com/tidb-in-kubernetes/v1.6/scale-a-tidb-cluster#scale-pd-microservice-components)

When deploying and using PD microservices, pay attention to the following:

- After you enable microservices and restart PD for a cluster, PD stops allocating TSO for the cluster. Therefore, you need to deploy the `tso` microservice in the cluster when you enable microservices.
- If the `scheduling` microservice is deployed in a cluster, the scheduling function of the cluster is provided by the `scheduling` microservice. If the `scheduling` microservice is not deployed, the scheduling function of the cluster is still provided by PD.
- The `scheduling` microservice supports dynamic switching, which is enabled by default (`enable-scheduling-fallback` defaults to `true`). If the process of the `scheduling` microservice is terminated, PD continues to provide scheduling services for the cluster by default.

    If the binary versions of the `scheduling` microservice and PD are different, to prevent changes in the scheduling logic, you can disable the dynamic switching function of the `scheduling` microservice by executing `pd-ctl config set enable-scheduling-fallback false`. After this function is disabled, PD will not take over the scheduling service when the process of the `scheduling` microservice is terminated. This means that the scheduling service of the cluster will be unavailable until the `scheduling` microservice is restarted.
## Tool compatibility

Microservices do not affect the normal use of data import, export, and other replication tools.
## FAQs

- How can I determine if PD becomes a performance bottleneck?

  When your cluster is in a normal state, you can check monitoring metrics in the Grafana PD panel. If the `TiDB - PD server TSO handle time` metric shows a notable increase in latency or the `Heartbeat - TiKV side heartbeat statistics` metric shows a significant number of pending items, it indicates that PD becomes a performance bottleneck.
