# Validate recovered data and remove unrecoverable stores

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/online-unsafe-recovery.md`
- Source Title: `Online Unsafe Recovery`
- Source Heading Path: `Online Unsafe Recovery > Usage > Step 3. Check the consistency of data and index (not required for RawKV) | Online Unsafe Recovery > Usage > Step 4: Remove unrecoverable stores (optional)`
- Source Line Ranges: `165-234`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `sql`, `tiup`, `operator`, `tikv`
- Topic Tags: `consistency-check`, `admin-check`, `index-repair`, `store-removal`, `tombstone-cleanup`, `kubernetes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0030_447f2f861b`
- Source ID: `tidb-docs-8.1:online-unsafe-recovery.md#step-3-check-the-consistency-of-data-and-index-not-required-for-rawkv`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fa231ba40e6106f4fa05be8080920cf1be2b12c4536e6979864c0ee394602c07`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/online-unsafe-recovery#step-3-check-the-consistency-of-data-and-index-not-required-for-rawkv
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/online-unsafe-recovery.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the post-recovery validation SQL for affected tables, the documented index repair sequence, or the optional removal steps for unrecoverable stores after online unsafe recovery.
- Retrieval Keywords: ADMIN CHECK TABLE table_name, check the consistency of data and index, not required for RawKV, ALTER TABLE table_name RENAME INDEX index_name TO index_name_lame_duck, ALTER TABLE table_name ADD INDEX index_name (column_name), ALTER TABLE table_name DROP INDEX index_name_lame_duck, Remove unrecoverable stores, tiup cluster scale-in <cluster-name> -N <host> --force, tiup cluster prune <cluster-name>, PersistentVolumeClaim, kubectl delete -n ${namespace} pvc ${pvc_name} --wait=false, kubectl delete -n ${namespace} pod ${pod_name}, Tombstone nodes
- Follow-up Guidance: The source provides separate optional store-removal steps for stores deployed using TiUP and stores deployed using TiDB Operator.
- Classification Note: This chunk is classified as recovery for a shared component scope because it combines SQL consistency checks and index repair with deployment-specific store cleanup steps using TiUP, Kubernetes, and TiKV-related node removal.

## Official Source Content

### Step 3. Check the consistency of data and index (not required for RawKV)

> **Note:**
>
> Although the data can be read and written, it does not mean that there is no data loss.

After the recovery is completed, the data and index might be inconsistent. Use the SQL command [`ADMIN CHECK`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-check-table-index) to check the data and index consistency of the affected tables

```sql
ADMIN CHECK TABLE table_name;
```

If there are inconsistent indexes, you can fix the index inconsistency by renaming the old index, creating a new index, and then dropping the old index.

1. Rename the old index:

    ```sql
    ALTER TABLE table_name RENAME INDEX index_name TO index_name_lame_duck;
    ```

2. Create a new index:

    ```sql
    ALTER TABLE table_name ADD INDEX index_name (column_name);
    ```

3. Drop the old index:

    ```sql
    ALTER TABLE table_name DROP INDEX index_name_lame_duck;
    ```
### Step 4: Remove unrecoverable stores (optional)

<div label="Stores deployed using TiUP">

1. Remove the unrecoverable nodes:

    ```bash
    tiup cluster scale-in <cluster-name> -N <host> --force
    ```

2. Clean up Tombstone nodes:

    ```bash
    tiup cluster prune <cluster-name>
    ```

</div>
<div label="Stores deployed using TiDB Operator">

1. Delete the `PersistentVolumeClaim`.

    ```bash
    kubectl delete -n ${namespace} pvc ${pvc_name} --wait=false
    ```

2. Delete the TiKV Pod and wait for newly created TiKV Pods to join the cluster.

    ```bash
    kubectl delete -n ${namespace} pod ${pod_name}
    ```

</div>
