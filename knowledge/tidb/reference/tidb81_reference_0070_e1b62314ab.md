# Resource Manager page access and sections

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-resource-manager.md`
- Source Title: `TiDB Dashboard Resource Manager Page`
- Source Heading Path: `TiDB Dashboard Resource Manager Page | TiDB Dashboard Resource Manager Page > Access the page | TiDB Dashboard Resource Manager Page > Resource Manager page`
- Source Line Ranges: `5-34`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`, `tidb`
- Topic Tags: `resource-control`, `resource-groups`, `quotas`, `capacity-estimation`, `metrics`, `dashboard-access`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0070_e1b62314ab`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-resource-manager.md#tidb-dashboard-resource-manager-page`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cc34be79422639655da86a3356ff97f902e112a2250b145d92f79b59f70d5d91`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-resource-manager#tidb-dashboard-resource-manager-page
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-resource-manager.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB Dashboard Resource Manager page entry points and a summary of its Configuration, Estimate Capacity, and Metrics sections for resource control planning.
- Retrieval Keywords: Resource Manager, TiDB Dashboard, http://127.0.0.1:2379/dashboard/#/resource_manager, PD instance address and port, RESOURCE_GROUPS table, Configuration, Estimate Capacity, Metrics, resource groups, quotas, cluster capacity, Resource Control
- Follow-up Guidance: The page shows Configuration data from the `RESOURCE_GROUPS` table, links to estimate capacity based on actual workload or hardware deployment, and metrics panels for overall resource consumption status.
- Classification Note: This is reference content because it describes how to access the Resource Manager page and what information its three sections display.

## Official Source Content

# TiDB Dashboard Resource Manager Page

To implement resource isolation using the [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control) feature, cluster administrators can create resource groups and set quotas for each group. Before resource planning, you need to know the overall capacity of the cluster. This document helps you view the information about resource control, so you can estimate the cluster capacity before resource planning and allocate resources more effectively.
## Access the page

You can use one of the following two methods to access the Resource Manager page:

* After logging in to TiDB Dashboard, click **Resource Manager** in the left navigation menu.

* Visit <http://127.0.0.1:2379/dashboard/#/resource_manager> in your browser. Replace `127.0.0.1:2379` with the actual PD instance address and port.
## Resource Manager page

The following figure shows the Resource Manager details page:

![TiDB Dashboard: Resource Manager](/media/dashboard/dashboard-resource-manager-info.png)

The Resource Manager page contains the following three sections:

- Configuration: This section displays the data obtained from the `RESOURCE_GROUPS` table of TiDB. It contains the information about all resource groups. For more information, see [`RESOURCE_GROUPS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-resource-groups).

- Estimate Capacity: Before resource planning, you need to know the overall capacity of the cluster. You can use one of the following methods:

    - [Estimate capacity based on actual workload](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-calibrate-resource#estimate-capacity-based-on-actual-workload)
    - [Estimate capacity based on hardware deployment](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-calibrate-resource#estimate-capacity-based-on-hardware-deployment)

- Metrics: By observing the metrics on the panels, you can understand the current overall resource consumption status of the cluster.
