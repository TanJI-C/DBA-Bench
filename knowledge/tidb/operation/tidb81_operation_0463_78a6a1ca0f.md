# Estimate capacity, manage resource groups, and bind workloads

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-resource-control.md`
- Source Title: `Use Resource Control to Achieve Resource Isolation`
- Source Heading Path: `Use Resource Control to Achieve Resource Isolation > How to use resource control | Use Resource Control to Achieve Resource Isolation > How to use resource control > Estimate cluster capacity | Use Resource Control to Achieve Resource Isolation > How to use resource control > Manage resource groups | Use Resource Control to Achieve Resource Isolation > How to use resource control > Create a resource group | Use Resource Control to Achieve Resource Isolation > How to use resource control > Bind resource groups | Use Resource Control to Achieve Resource Isolation > How to use resource control > Bind resource groups > Bind users to a resource group | Use Resource Control to Achieve Resource Isolation > How to use resource control > Bind resource groups > Bind the current session to a resource group | Use Resource Control to Achieve Resource Isolation > How to use resource control > Bind resource groups > Bind the current statement to a resource group`
- Source Line Ranges: `143-258`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `dashboard`, `sql`
- Topic Tags: `resource-control`, `resource-groups`, `capacity-planning`, `calibrate-resource`, `create-resource-group`, `alter-resource-group`, `drop-resource-group`, `user-binding`, `session-binding`, `statement-binding`, `optimizer-hints`, `ru`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0463_78a6a1ca0f`
- Source ID: `tidb-docs-8.1:tidb-resource-control.md#how-to-use-resource-control`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ae00e9a7261b591bd13ae06700767adc9140f314a0e6f0831b68f82dc086a400`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-resource-control#how-to-use-resource-control
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-resource-control.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to estimate cluster capacity, create or modify resource groups, and bind users, sessions, or statements to a resource group.
- Retrieval Keywords: CALIBRATE RESOURCE, Resource Manager page, CREATE RESOURCE GROUP, ALTER RESOURCE GROUP, DROP RESOURCE GROUP, RU_PER_SEC, BURSTABLE, PRIORITY = HIGH, RESOURCE_GROUP(), SET RESOURCE GROUP, CREATE USER RESOURCE GROUP, ALTER USER RESOURCE GROUP, default resource group, RESOURCE_GROUP_ADMIN, SUPER
- Follow-up Guidance: The chunk includes example SQL for CREATE RESOURCE GROUP, ALTER USER ... RESOURCE GROUP, SET RESOURCE GROUP, and the RESOURCE_GROUP(rg1) optimizer hint, along with notes about new sessions and the default resource group.
- Classification Note: This is operation content because it describes usage procedures, required privileges, SQL statements, and binding methods for managing resource groups and workload allocation.

## Official Source Content

## How to use resource control

This section describes how to use the resource control feature to manage resource groups and control the resource allocation of each resource group.
### Estimate cluster capacity

Before resource planning, you need to know the overall capacity of the cluster. TiDB provides the statement [`CALIBRATE RESOURCE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-calibrate-resource) to estimate the cluster capacity. You can use one of the following methods:

- [Estimate capacity based on actual workload](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-calibrate-resource#estimate-capacity-based-on-actual-workload)
- [Estimate capacity based on hardware deployment](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-calibrate-resource#estimate-capacity-based-on-hardware-deployment)

You can view the [Resource Manager page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-resource-manager) in TiDB Dashboard. For more information, see [`CALIBRATE RESOURCE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-calibrate-resource#methods-for-estimating-capacity).

For TiDB Self-Managed, you can use the [`CALIBRATE RESOURCE`](https://docs.pingcap.com/tidb/stable/sql-statement-calibrate-resource) statement to estimate the cluster capacity.

For TiDB Cloud, the [`CALIBRATE RESOURCE`](https://docs.pingcap.com/tidb/stable/sql-statement-calibrate-resource) statement is inapplicable.
### Manage resource groups

To create, modify, or delete a resource group, you need to have the `SUPER` or `RESOURCE_GROUP_ADMIN` privilege.

You can create a resource group for a cluster by using [`CREATE RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-resource-group).

For an existing resource group, you can modify the `RU_PER_SEC` option (the rate of RU backfilling per second) of the resource group by using [`ALTER RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-resource-group). The changes to the resource group take effect immediately.

You can delete a resource group by using [`DROP RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-resource-group).
### Create a resource group

The following is an example of how to create a resource group.

1. Create a resource group `rg1`. The resource limit is 500 RUs per second and allows applications in this resource group to overrun resources.

    ```sql
    CREATE RESOURCE GROUP IF NOT EXISTS rg1 RU_PER_SEC = 500 BURSTABLE;
    ```

2. Create a resource group `rg2`. The RU backfill rate is 600 RUs per second and does not allow applications in this resource group to overrun resources.

    ```sql
    CREATE RESOURCE GROUP IF NOT EXISTS rg2 RU_PER_SEC = 600;
    ```

3. Create a resource group `rg3` with the absolute priority set to `HIGH`. The absolute priority currently supports `LOW|MEDIUM|HIGH`. The default value is `MEDIUM`.

    ```sql
    CREATE RESOURCE GROUP IF NOT EXISTS rg3 RU_PER_SEC = 100 PRIORITY = HIGH;
    ```
### Bind resource groups

TiDB supports three levels of resource group settings as follows.

- User level. Bind a user to a specific resource group via the [`CREATE USER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-user) or [`ALTER USER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-user#modify-the-resource-group-bound-to-the-user) statement. After a user is bound to a resource group, sessions created by the user are automatically bound to the corresponding resource group.
- Session level. Set the resource group for the current session via [`SET RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-resource-group).
- Statement level. Set the resource group for the current statement via [`RESOURCE_GROUP()`](https://docs.pingcap.com/tidb/stable/optimizer-hints#resource_groupresource_group_name) Optimizer Hint.
#### Bind users to a resource group

The following example creates a user `usr1` and binds the user to the resource group `rg1`. `rg1` is the resource group created in the example in [Create Resource Group](#create-a-resource-group).

```sql
CREATE USER 'usr1'@'%' IDENTIFIED BY '123' RESOURCE GROUP rg1;
```

The following example uses `ALTER USER` to bind the user `usr2` to the resource group `rg2`. `rg2` is the resource group created in the example in [Create Resource Group](#create-a-resource-group).

```sql
ALTER USER usr2 RESOURCE GROUP rg2;
```

After you bind users, the resource consumption of newly created sessions will be controlled by the specified quota (Request Unit, RU). If the system workload is relatively high and there is no spare capacity, the resource consumption rate of `usr2` will be strictly controlled not to exceed the quota. Because `usr1` is bound by `rg1` with `BURSTABLE` configured, the consumption rate of `usr1` is allowed to exceed the quota.

If there are too many requests that result in insufficient resources for the resource group, the client's requests will wait. If the wait time is too long, the requests will report an error.

> **Note:**
>
> - When you bind a user to a resource group by using `CREATE USER` or `ALTER USER`, it will not take effect for the user's existing sessions, but only for the user's new sessions.
> - TiDB automatically creates a `default` resource group during cluster initialization. For this resource group, the default value of `RU_PER_SEC` is `UNLIMITED` (equivalent to the maximum value of the `INT` type, that is, `2147483647`) and it is in `BURSTABLE` mode. Statements that are not bound to a resource group are automatically bound to this resource group. This resource group does not support deletion, but you can modify the configuration of its RU.

To unbind users from a resource group, you can simply bind them to the `default` group again as follows:

```sql
ALTER USER 'usr3'@'%' RESOURCE GROUP `default`;
```

For more details, see [`ALTER USER ... RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-user#modify-the-resource-group-bound-to-the-user).
#### Bind the current session to a resource group

By binding a session to a resource group, the resource usage of the corresponding session is limited by the specified usage (RU).

The following example binds the current session to the resource group `rg1`.

```sql
SET RESOURCE GROUP rg1;
```
#### Bind the current statement to a resource group

By adding the [`RESOURCE_GROUP(resource_group_name)`](https://docs.pingcap.com/tidb/stable/optimizer-hints#resource_groupresource_group_name) hint to a SQL statement, you can specify the resource group to which the statement is bound. This hint supports `SELECT`, `INSERT`, `UPDATE`, and `DELETE` statements.

The following example binds the current statement to the resource group `rg1`.

```sql
SELECT /*+ RESOURCE_GROUP(rg1) */ * FROM t limit 10;
```
