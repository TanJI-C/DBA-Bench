# DM WebUI access and page usage for managing migration tasks

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-webui-guide.md`
- Source Title: `Use WebUI to Manage DM migration tasks`
- Source Heading Path: `Use WebUI to Manage DM migration tasks | Use WebUI to Manage DM migration tasks > Access method | Use WebUI to Manage DM migration tasks > Migration | Use WebUI to Manage DM migration tasks > Migration > Source | Use WebUI to Manage DM migration tasks > Migration > Task | Use WebUI to Manage DM migration tasks > Migration > Task > View migration task details | Use WebUI to Manage DM migration tasks > Migration > Task > Create migration tasks | Use WebUI to Manage DM migration tasks > Migration > Replication detail | Use WebUI to Manage DM migration tasks > Cluster | Use WebUI to Manage DM migration tasks > Cluster > Members`
- Source Line Ranges: `5-73`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `dashboard`
- Topic Tags: `webui`, `access`, `migration-tasks`, `sources`, `task-details`, `task-creation`, `replication-detail`, `cluster-members`, `warnings`, `openapi`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0106_57081b34a7`
- Source ID: `tidb-docs-8.1:dm/dm-webui-guide.md#use-webui-to-manage-dm-migration-tasks`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `eb897c810fe4ddbc3f4d33f6a7b0ea4611199b98c89507399bc5ba18053567f1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-webui-guide#use-webui-to-manage-dm-migration-tasks
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-webui-guide.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to access DM WebUI or what the Migration, Source, Task, Replication Detail, and Cluster Members pages are used for in managing DM migration tasks.
- Retrieval Keywords: DM WebUI, Use WebUI to Manage DM migration tasks, OpenAPI, 8261, http://{master_ip}:{master_port}/dashboard/, Migration, Source, Task, Replication Detail, Cluster, Members, View migration task details, Create migration tasks, JSON-formatted configuration file, sub-task statuses, full dump, full import, load, incremental replication, sync, query by task, source, and database name, worker nodes and the source, experimental feature, dmctl
- Follow-up Guidance: The content also states that DM WebUI is an experimental feature, its task lifecycle has changed, and it is not recommended to use DM WebUI and dmctl at the same time.
- Classification Note: This is classified as operation content because it explains WebUI access, page usage, task viewing and creation flows, and cluster/member management views for DM.

## Official Source Content

# Use WebUI to Manage DM migration tasks

DM WebUI is a web-based GUI platform for managing TiDB Data Migration (DM) tasks. This platform provides a simple and intuitive way to manage a large number of migration tasks, which frees you from using the dmctl command-line tool.

This document introduces how to access DM WebUI, the prerequisites, the use cases of each page on the interface, and the attention points.

> **Warning:**
>
> - DM WebUI is currently an experimental feature. It is not recommended to use it in the production environment.
> - The lifecycle of `task` in DM WebUI has been changed, and it is not recommended to use DM WebUI and dmctl at the same time.

DM WebUI has the following pages:

- **Migration**
    - **Task**: Provides an entry to task creation, and displays the detailed information of each migration task. This page helps you monitor, create, delete, and configure migration tasks.
    - **Source**: Configures the information of upstream data source for a migration task. On this page, you can manage the upstream configuration in a data migration environment, including creating and deleting upstream configuration, monitoring the task status corresponding to the upstream configuration, and modifying upstream configuration.
    - **Replication Detail**: Displays the detailed status information of migration tasks. On this page, you can view the detailed configuration and status information based on a specified filter, including the configuration information and database names of the upstream and downstream, the relation of source tables and target tables.
- **Cluster**
    - **Members**: Displays the list of all master and worker nodes in the DM cluster, and the binding relationship between worker nodes and the source. On this page, you can view the configuration information of the current DM cluster and the status information of each worker. In addition, basic management is also provided on this page.

The interface is as follows:

![webui](/media/dm/dm-webui-preview-en.png)
## Access method

When [OpenAPI](https://docs.pingcap.com/tidb/stable/dm/dm-open-api#maintain-dm-clusters-using-openapi) is enabled, you can access the DM WebUI from any master node of the DM cluster. The access port is `8261` by default and is the same as that of DM OpenAPI. Here is an example of an access address: `http://{master_ip}:{master_port}/dashboard/`.
## Migration

**Migration** includes **Source**, **Task**, and **Replication Detail** pages.
### Source

Before creating a migration task, you need to create the data source information of the upstream for the replication task. You can create the upstream configuration in the **Source** page. When creating sources, pay attention to the following items:

- If there is an auto failover between primary and secondary instance, enable GTID in the upstream MySQL and set GTID to `True` when creating the upstream configuration; otherwise, the migration task will be interrupted during the failover (except for AWS Aurora).
- If a MySQL instance needs to be temporarily offline, you can disable the instance. However, when the MySQL instance is being disabled, other MySQL instances running migration tasks should not execute DDL operations; otherwise, the disabled instance cannot properly migrate data after it is enabled.
- When multiple migration tasks use the same upstream, it might cause additional stress. Enabling relay log can reduce the impact on the upstream, so it is recommended to enable relay log.
### Task

You can view the migration task details on the **Task** page, and create migration tasks.
#### View migration task details

In the task list, click the task name to view the Details page from the right. The Details page displays more detailed task status information. On this page, you can view the status of each sub-task and the current configuration information of the migration task.

In DM, each sub-task of a migration task might be at different stages, namely full dump -> full import (load) -> incremental replication (sync). Therefore, the current stage of a task is displayed with the statistics of the sub-task statuses, which can help you better understand the running status of the task.
#### Create migration tasks

To create a migration task on this page, click the **Add** button on the top right corner. You can use one of the following methods to create a migration task:

- By following the WebUI instruction. Fill in the required information step by step on the WebUI. This method is suitable for beginners and for daily use.
- By using a configuration file. Paste or write a JSON-formatted configuration file to create a migration task. This method supports adjusting more parameters and is suitable for advanced users.
### Replication detail

You can view the status of the migration rules configured for a migration task on the **Replication Detail** page. This page supports querying by task, source, and database name.

The query result contains the corresponding information of the upstream table and the downstream table, so be careful using `.*` in case that too many query results slow down the page response.
## Cluster
### Members

The **Members** page displays all the master and worker nodes in the DM cluster, and the binding relationship between worker nodes and the source.
