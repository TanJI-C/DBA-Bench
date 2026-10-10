# Resource control overview, scenarios, limitations, and RU model

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-resource-control.md`
- Source Title: `Use Resource Control to Achieve Resource Isolation`
- Source Heading Path: `Use Resource Control to Achieve Resource Isolation | Use Resource Control to Achieve Resource Isolation > Scenarios for resource control | Use Resource Control to Achieve Resource Isolation > Limitations | Use Resource Control to Achieve Resource Isolation > What is Request Unit (RU)`
- Source Line Ranges: `5-101`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `cloud`
- Topic Tags: `resource-control`, `resource-groups`, `qos`, `flow-control`, `priority-scheduling`, `request-unit`, `ru`, `limitations`, `tiflash`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0944_8dc4883db5`
- Source ID: `tidb-docs-8.1:tidb-resource-control.md#use-resource-control-to-achieve-resource-isolation`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `131ca00ffb01d3c4b6f25626a7260a83dcc4a57cab15e05bfc78b83216b7401a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-resource-control#use-resource-control-to-achieve-resource-isolation
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-resource-control.md

## Retrieval Guidance

- Use When: Use this chunk when you need an overview of TiDB resource control, including resource groups, flow control, priority scheduling, supported scenarios, limitations, and the Request Unit (RU) model.
- Retrieval Keywords: resource control, resource groups, QoS, flow control, priority scheduling, RU, Request Unit, RU_PER_SEC, PRIORITY, BURSTABLE, token bucket algorithm, TiDB flow control, TiKV scheduling, TiFlash flow control, TiFlash scheduling, SQL bindings, less than 5% performance degradation, Scenarios for resource control, What is Request Unit (RU), 2 storage read batches consume 1 RU, 8 storage read requests consume 1 RU, 64 KiB read request payload consumes 1 RU, 1 storage write batch consumes 1 RU, 1 storage write request consumes 1 RU, 1 KiB write request payload consumes 1 RU, 3 ms consumes 1 RU
- Follow-up Guidance: The source also points to Parameters for resource control for details on enabling the TiDB and TiKV resource management capabilities separately or simultaneously.
- Classification Note: This is reference content because it defines the resource control feature, its limitations, scenarios, and exact RU accounting rules and identifiers from the official documentation.

## Official Source Content

# Use Resource Control to Achieve Resource Isolation

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

As a cluster administrator, you can use the resource control feature to create resource groups, set quotas for resource groups, and bind users to those groups.

The TiDB resource control feature provides two layers of resource management capabilities: the flow control capability at the TiDB layer and the priority scheduling capability at the TiKV layer. The two capabilities can be enabled separately or simultaneously. See the [Parameters for resource control](#parameters-for-resource-control) for details. This allows the TiDB layer to control the flow of user read and write requests based on the quotas set for the resource groups, and allows the TiKV layer to schedule the requests based on the priority mapped to the read and write quota. By doing this, you can ensure resource isolation for your applications and meet quality of service (QoS) requirements.

- TiDB flow control: TiDB flow control uses the [token bucket algorithm](https://en.wikipedia.org/wiki/Token_bucket). If there are not enough tokens in a bucket, and the resource group does not specify the `BURSTABLE` option, the requests to the resource group will wait for the token bucket to backfill the tokens and retry. The retry might fail due to timeout.

- TiKV scheduling: You can set the absolute priority [(`PRIORITY`)](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-resource-groups#examples) as needed. Different resources are scheduled according to the `PRIORITY` setting. Tasks with high `PRIORITY` are scheduled first. If you do not set the absolute priority, TiKV uses the value of `RU_PER_SEC` of each resource group to determine the priority of the read and write requests for each resource group. Based on the priorities, the storage layer uses the priority queue to schedule and process requests.

Starting from v7.4.0, the resource control feature supports controlling TiFlash resources. Its principle is similar to that of TiDB flow control and TiKV scheduling:

- TiFlash flow control: With the [TiFlash pipeline execution model](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-pipeline-model), TiFlash can more accurately obtain the CPU consumption of different queries and convert it into [Request Units (RU)](#what-is-request-unit-ru) for deduction. Traffic control is implemented using a token bucket algorithm.
- TiFlash scheduling: When system resources are insufficient, TiFlash schedules pipeline tasks among multiple resource groups based on their priorities. The specific logic is: First, TiFlash assesses the `PRIORITY` of the resource group, then considers the CPU usage and `RU_PER_SEC`. As a result, if `rg1` and `rg2` have the same `PRIORITY` but the `RU_PER_SEC` of `rg2` is twice that of `rg1`, the CPU usage of `rg2` is twice that of `rg1`.

- TiFlash flow control: With the [TiFlash pipeline execution model](http://docs.pingcap.com/tidb/dev/tiflash-pipeline-model), TiFlash can more accurately obtain the CPU consumption of different queries and convert it into [Request Units (RU)](#what-is-request-unit-ru) for deduction. Traffic control is implemented using a token bucket algorithm.
- TiFlash scheduling: When system resources are insufficient, TiFlash schedules pipeline tasks among multiple resource groups based on their priorities. The specific logic is: First, TiFlash assesses the `PRIORITY` of the resource group, then considers the CPU usage and `RU_PER_SEC`. As a result, if `rg1` and `rg2` have the same `PRIORITY` but the `RU_PER_SEC` of `rg2` is twice that of `rg1`, the CPU usage of `rg2` is twice that of `rg1`.
## Scenarios for resource control

The introduction of the resource control feature is a milestone for TiDB. It can divide a distributed database cluster into multiple logical units. Even if an individual unit overuses resources, it does not crowd out the resources needed by other units.

With this feature, you can:

- Combine multiple small and medium-sized applications from different systems into a single TiDB cluster. When the workload of an application grows larger, it does not affect the normal operation of other applications. When the system workload is low, busy applications can still be allocated the required system resources even if they exceed the set quotas, so as to achieve the maximum utilization of resources.
- Choose to combine all test environments into a single TiDB cluster, or group the batch tasks that consume more resources into a single resource group. It can improve hardware utilization and reduce operating costs while ensuring that critical applications can always get the necessary resources.
- When there are mixed workloads in a system, you can put different workloads into separate resource groups. By using the resource control feature, you can ensure that the response time of transactional applications is not affected by data analysis or batch applications.
- When the cluster encounters an unexpected SQL performance issue, you can use SQL bindings along with resource groups to temporarily limit the resource consumption of a SQL statement.

In addition, the rational use of the resource control feature can reduce the number of clusters, ease the difficulty of operation and maintenance, and save management costs.

> **Note:**
>
> - To assess the effectiveness of resource management, it is recommended to deploy the cluster on independent computing and storage nodes. Scheduling and other cluster resource-sensitive features are hardly working properly on the deployment created by `tiup playground`, where the resources are shared across instances. 
## Limitations

Resource control incurs additional scheduling overhead. Therefore, there might be a slight performance degradation (less than 5%) when this feature is enabled.
## What is Request Unit (RU)

Request Unit (RU) is a unified abstraction unit in TiDB for system resources, which currently includes CPU, IOPS, and IO bandwidth metrics. It is used to indicate the amount of resources consumed by a single request to the database. The number of RUs consumed by a request depends on a variety of factors, such as the type of operations, and the amount of data being queried or modified. Currently, the RU contains consumption statistics for the resources in the following table:

<table>
    <thead>
        <tr>
            <th>Resource type</th>
            <th>RU consumption</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan="3">Read</td>
            <td>2 storage read batches consume 1 RU</td>
        </tr>
        <tr>
            <td>8 storage read requests consume 1 RU</td>
        </tr>
        <tr>
            <td>64 KiB read request payload consumes 1 RU</td>
        </tr>
        <tr>
            <td rowspan="3">Write</td>
            <td>1 storage write batch consumes 1 RU</td>
        </tr>
        <tr>
            <td>1 storage write request consumes 1 RU</td>
        </tr>
        <tr>
            <td>1 KiB write request payload consumes 1 RU</td>
        </tr>
        <tr>
            <td>CPU</td>
            <td> 3 ms consumes 1 RU</td>
        </tr>
    </tbody>
</table>

> **Note:**
>
> - Each write operation is eventually replicated to all replicas (by default, TiKV has 3 replicas). Each replication operation is considered a different write operation.
> - The preceding table lists only the resources involved in RU calculation for TiDB Self-Managed clusters, excluding the network and storage consumption. For {{{ .starter }}} RUs, see [{{{ .starter }}} Pricing Details](https://www.pingcap.com/tidb-cloud-starter-pricing-details/).
> - Currently, TiFlash resource control only considers SQL CPU, which is the CPU time consumed by the execution of pipeline tasks for queries, and read request payload.
