# Baseline evolution notes and upgrade checklist

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-plan-management.md`
- Source Title: `SQL Plan Management (SPM)`
- Source Heading Path: `SQL Plan Management (SPM) > Baseline evolution > Notes | SQL Plan Management (SPM) > Upgrade checklist`
- Source Line Ranges: `818-874`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`, `tiflash`
- Topic Tags: `sql-plan-management`, `baseline-evolution`, `bindings`, `optimizer-hints`, `upgrade-checklist`, `compatibility`, `version-upgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0624_d70e5793f2`
- Source ID: `tidb-docs-8.1:sql-plan-management.md#notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `338a60cbf8f0cd35027bbd7fbd2d9852fa0fd588b4d8ee3ab0b2f65a6180d532`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-plan-management#notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-plan-management.md

## Retrieval Guidance

- Use When: Use this chunk when checking SQL Plan Management baseline evolution behavior or preparing an upgrade precheck for bindings and tidb_evolve_plan_baselines compatibility.
- Retrieval Keywords: SQL Plan Management (SPM), baseline evolution, global binding, standardized SQL statements, creating a new binding deletes all previous bindings, memory_quota, use_toja, use_cascades, no_index_merge, read_consistent_replica, max_execution_time, read_from_storage, TiKV, TiFlash, isolation reads, upgrade checklist, tidb_evolve_plan_baselines, SELECT @@global.tidb_evolve_plan_baselines, SET GLOBAL tidb_evolve_plan_baselines = OFF, mysql.bind_info, SELECT bind_sql FROM mysql.bind_info WHERE status = 'using', ERROR 1064 (42000): You have an error in your SQL syntax
- Follow-up Guidance: The content includes checking @@global.tidb_evolve_plan_baselines, disabling it with SET GLOBAL tidb_evolve_plan_baselines = OFF for upgrades from versions earlier than v5.2.0, and verifying bind_sql values from mysql.bind_info in the new version environment for v4.0 upgrades.
- Classification Note: This is classified as a release item because it documents upgrade checklist and compatibility notes for SPM baseline evolution and SQL bindings during cluster upgrades.

## Official Source Content

### Notes

Because the baseline evolution automatically creates a new binding, when the query environment changes, the automatically created binding might have multiple behavior choices. Pay attention to the following notes:

+ Baseline evolution only evolves standardized SQL statements that have at least one global binding.

+ Because creating a new binding deletes all previous bindings (for a standardized SQL statement), the automatically evolved binding will be deleted after manually creating a new binding.

+ All hints related to the calculation process are retained during the evolution. These hints are as follows:

    | Hint | Description            |
    | :-------- | :------------- |
    | `memory_quota` | The maximum memory that can be used for a query. |
    | `use_toja` | Whether the optimizer transforms sub-queries to Join. |
    | `use_cascades` | Whether to use the cascades optimizer. |
    | `no_index_merge` | Whether the optimizer uses Index Merge as an option for reading tables. |
    | `read_consistent_replica` | Whether to forcibly enable Follower Read when reading tables. |
    | `max_execution_time` | The longest duration for a query. |

+ `read_from_storage` is a special hint in that it specifies whether to read data from TiKV or from TiFlash when reading tables. Because TiDB provides isolation reads, when the isolation condition changes, this hint has a great influence on the evolved execution plan. Therefore, when this hint exists in the initially created binding, TiDB ignores all its evolved bindings.
## Upgrade checklist

During cluster upgrade, SQL Plan Management (SPM) might cause compatibility issues and make the upgrade fail. To ensure a successful upgrade, you need to include the following list for upgrade precheck:

* When you upgrade from a version earlier than v5.2.0 (that is, v4.0, v5.0, and v5.1) to the current version, make sure that `tidb_evolve_plan_baselines` is disabled before the upgrade. To disable this variable, perform the following steps.

    ```sql
    -- Check whether `tidb_evolve_plan_baselines` is disabled in the earlier version.

    SELECT @@global.tidb_evolve_plan_baselines;

    -- If `tidb_evolve_plan_baselines` is still enabled, disable it.

    SET GLOBAL tidb_evolve_plan_baselines = OFF;
    ```

* Before you upgrade from v4.0 to the current version, you need to check whether the syntax of all queries corresponding to the available SQL bindings is correct in the new version. If any syntax errors exist, delete the corresponding SQL binding. To do that, perform the following steps.

    ```sql
    -- Check the query corresponding to the available SQL binding in the version to be upgraded.

    SELECT bind_sql FROM mysql.bind_info WHERE status = 'using';

    -- Verify the result from the above SQL query in the test environment of the new version.

    bind_sql_0;
    bind_sql_1;
    ...

    -- In the case of a syntax error (ERROR 1064 (42000): You have an error in your SQL syntax), delete the corresponding binding.
    -- For any other errors (for example, tables are not found), it means that the syntax is compatible. No other operation is needed.
    ```
