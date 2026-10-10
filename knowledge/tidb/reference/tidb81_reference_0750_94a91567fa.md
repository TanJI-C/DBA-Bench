# Table attributes overview, syntax, and override rules

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/table-attributes.md`
- Source Title: `Table Attributes`
- Source Heading Path: `Table Attributes | Table Attributes > Usage | Table Attributes > Attribute override rules`
- Source Line Ranges: `5-70`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `br`, `ticdc`
- Topic Tags: `table-attributes`, `ddl`, `partitions`, `attribute-override`, `merge-option`, `replication`, `incremental-backup`, `information-schema`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0750_94a91567fa`
- Source ID: `tidb-docs-8.1:table-attributes.md#table-attributes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a530cc0c72b0f92f3dae66d9372f50ccc3e96582e42f1ae84edfd238b4d6a9ee`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/table-attributes#table-attributes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/table-attributes.md

## Retrieval Guidance

- Use When: Use this chunk when you need the general syntax, visibility queries, replication or incremental backup note, or override behavior for TiDB table attributes and partition attributes.
- Retrieval Keywords: Table Attributes, ALTER TABLE t [PARTITION p] ATTRIBUTES, ALTER TABLE t [PARTITION p] ATTRIBUTES DEFAULT, information_schema.attributes, SELECT * FROM information_schema.attributes, SELECT * FROM information_schema.attributes WHERE id='schema/t[/p]', attributes LIKE '%key%', merge_option, attribute override rules, partition attribute overrides table attribute, TiDB Binlog, TiCDC, BR incremental backup
- Follow-up Guidance: It also states that when TiDB Binlog or TiCDC replication or BR incremental backup is used, the DDL statement that sets table attributes is skipped and must be manually executed in the downstream or backup cluster to use table attributes there.
- Classification Note: This is classified as reference because the content defines what table attributes are, shows the SQL syntax and information_schema queries, and explains the table-versus-partition override rule.

## Official Source Content

# Table Attributes

The Table Attributes feature is introduced in TiDB v5.3.0. Using this feature, you can add specific attributes to a table or partition to perform the operations corresponding to the attributes. For example, you can use table attributes to control the Region merge behavior.

Currently, TiDB only supports adding the `merge_option` attribute to a table or partition to control the Region merge behavior. The `merge_option` attribute is only part of how to deal with hotspots. For more information, refer to [Troubleshoot Hotspot Issues](https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues).

Currently, TiDB only supports adding the `merge_option` attribute to a table or partition to control the Region merge behavior. The `merge_option` attribute is only part of how to deal with hotspots.

> **Note:**
>
> - When you use TiDB Binlog or TiCDC to perform replication or use BR to perform incremental backup, the replication or backup operations skip the DDL statement that sets table attributes. To use table attributes in the downstream or in the backup cluster, you need to manually execute the DDL statement in the downstream or in the backup cluster.
## Usage

The table attribute is in the form of `key=value`. Multiple attributes are separated by commas. In the following examples, `t` is the name of the table to be modified, `p` is the name of the partition to be modified. Items in `[]` are optional.

+ Set attributes for a table or partition:

    ```sql
    ALTER TABLE t [PARTITION p] ATTRIBUTES [=] 'key=value[, key1=value1...]';
    ```

+ Reset attributes for a table or partition:

    ```sql
    ALTER TABLE t [PARTITION p] ATTRIBUTES [=] DEFAULT;
    ```

+ See the attributes of all tables and partitions:

    ```sql
    SELECT * FROM information_schema.attributes;
    ```

+ See the attribute configured to a table or partition:

    ```sql
    SELECT * FROM information_schema.attributes WHERE id='schema/t[/p]';
    ```

+ See all tables and partitions that have a specific attribute:

    ```sql
    SELECT * FROM information_schema.attributes WHERE attributes LIKE '%key%';
    ```
## Attribute override rules

The attribute configured to a table takes effect on all partitions of the table. However, there is one exception: If the table and partition are configured with the same attribute but different attribute values, the partition attribute overrides the table attribute. For example, suppose that the table `t` is configured with the `key=value` attribute, and the partition `p` is configured with `key=value1`.

```sql
ALTER TABLE t ATTRIBUTES[=]'key=value';
ALTER TABLE t PARTITION p ATTRIBUTES[=]'key=value1';
```

In this case, `key=value1` is the attribute that actually takes effect on the `p1` partition.
