# Control Region merge behavior with merge_option

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/table-attributes.md`
- Source Title: `Table Attributes`
- Source Heading Path: `Table Attributes > Control the Region merge behavior using table attributes | Table Attributes > Control the Region merge behavior using table attributes > User scenarios | Table Attributes > Control the Region merge behavior using table attributes > User scenarios > Write hotspot on a newly created table or partition | Table Attributes > Control the Region merge behavior using table attributes > User scenarios > Periodic read hotspot in read-only scenarios | Table Attributes > Control the Region merge behavior using table attributes > Usage | Table Attributes > Control the Region merge behavior using table attributes > Attribute override rules`
- Source Line Ranges: `71-148`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`
- Topic Tags: `region-merge`, `merge-option`, `hotspot`, `write-hotspot`, `read-hotspot`, `partitions`, `pd-configuration`, `split-merge-interval`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0242_4bf4005f36`
- Source ID: `tidb-docs-8.1:table-attributes.md#control-the-region-merge-behavior-using-table-attributes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ec3a75b1f0baab65d01edc0fb0c20e1f59395cc79b88cacf1e31b3fd7924956d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/table-attributes#control-the-region-merge-behavior-using-table-attributes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/table-attributes.md

## Retrieval Guidance

- Use When: Use this chunk when you need SQL and behavior details for controlling Region merge with the merge_option table attribute in hotspot-related table or partition scenarios.
- Retrieval Keywords: Control the Region merge behavior using table attributes, merge_option=deny, merge_option=allow, ALTER TABLE t ATTRIBUTES 'merge_option=deny', ALTER TABLE t ATTRIBUTES 'merge_option=allow', ALTER TABLE t PARTITION p ATTRIBUTES 'merge_option=deny', ALTER TABLE t PARTITION p ATTRIBUTES 'merge_option=allow', ALTER TABLE t ATTRIBUTES DEFAULT, information_schema.attributes WHERE attributes LIKE '%merge_option%', write hotspot on a newly created table or partition, periodic read hotspot in read-only scenarios, split and scatter Regions, Region merge behavior, split-merge-interval, partition override merge_option
- Follow-up Guidance: It further notes that PD decides whether Regions can be merged after the interval specified by split-merge-interval according to the merge_option configuration, and for partitioned tables a table-level merge_option=allow still leaves the table split into multiple Regions by default unless the table attribute is reset.
- Classification Note: This is classified as operation because the content focuses on when to use merge_option for hotspot scenarios and provides the specific ALTER TABLE statements and behavior notes for Region merging.

## Official Source Content

## Control the Region merge behavior using table attributes
### User scenarios

If there is a write hotspot or read hotspot, you can use table attributes to control the Region merge behavior. You can first add the `merge_option` attribute to a table or partition and then set its value to `deny`. The two scenarios are as follows.
#### Write hotspot on a newly created table or partition

If a hotspot issue occurs when data is written to a newly created table or partition, you usually need to split and scatter Regions. However, if there is a certain time interval between the split/scatter operation and writes, these operations do not truly avoid the write hotspot. This is because the split operation performed when the table or partition is created produces empty Regions, so if the time interval exists, the split Regions might be merged. To handle this case, you can add the `merge_option` attribute to the table or partition and set the attribute value to `deny`.
#### Periodic read hotspot in read-only scenarios

Suppose that in a read-only scenario, you try to reduce the periodic read hotspot that occurs on a table or partition by manually splitting Regions, and you do not want the manually split Regions to be merged after the hotspot issue is resolved. In this case, you can add the `merge_option` attribute to the table or partition and set its value to `deny`.
### Usage

+ Prevent the Regions of a table from merging:

    ```sql
    ALTER TABLE t ATTRIBUTES 'merge_option=deny';
    ```

+ Allow merging Regions belonging to a table:

    ```sql
    ALTER TABLE t ATTRIBUTES 'merge_option=allow';
    ```

+ Reset attributes of a table:

    ```sql
    ALTER TABLE t ATTRIBUTES DEFAULT;
    ```

+ Prevent the Regions of a partition from merging:

    ```sql
    ALTER TABLE t PARTITION p ATTRIBUTES 'merge_option=deny';
    ```

+ Allow merging Regions belonging to a partition:

    ```sql
    ALTER TABLE t PARTITION p ATTRIBUTES 'merge_option=allow';
    ```

+ See all tables or partitions configured the `merge_option` attribution:

    ```sql
    SELECT * FROM information_schema.attributes WHERE attributes LIKE '%merge_option%';
    ```
### Attribute override rules

```sql
ALTER TABLE t ATTRIBUTES 'merge_option=deny';
ALTER TABLE t PARTITION p ATTRIBUTES 'merge_option=allow';
```

When the above two attributes are configured at the same time, the Regions belonging to the partition `p` can actually be merged. When the attribute of the partition is reset, the partition `p` inherits the attribute from the table `t`, and the Regions cannot be merged.

> **Note:**
>
> - For a table with partitions, if the `merge_option` attribute is configured at the table level only, even if `merge_option=allow`, the table is still split into multiple Regions by default according to the actual number of partitions. To merge all Regions, you need to [reset the attribute of the table](#usage).
> - When using the `merge_option` attribute, you need to pay attention to the PD configuration parameter [`split-merge-interval`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#split-merge-interval). Suppose that the `merge_option` attribute is not configured. In this case, if Regions meet conditions, Regions can be merged after the interval specified by `split-merge-interval`. If the `merge_option` attribute is configured, PD decides whether to merge Regions after the specified interval according to the `merge_option` configuration.

> **Note:**
>
> - For a table with partitions, if the `merge_option` attribute is configured at the table level only, even if `merge_option=allow`, the table is still split into multiple Regions by default according to the actual number of partitions. To merge all Regions, you need to [reset the attribute of the table](#usage).
> - Suppose that the `merge_option` attribute is not configured. In this case, if Regions meet conditions, Regions can be merged after one hour. If the `merge_option` attribute is configured, PD decides whether to merge Regions after one hour according to the `merge_option` configuration.
