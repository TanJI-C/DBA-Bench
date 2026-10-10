# DM handling of gh-ost online schema change

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/feature-online-ddl.md`
- Source Title: `Migrate from Databases that Use GH-ost/PT-osc`
- Source Heading Path: `Migrate from Databases that Use GH-ost/PT-osc > online-schema-change: gh-ost`
- Source Line Ranges: `16-113`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `sql`
- Topic Tags: `gh-ost`, `online-schema-change`, `ghosttable`, `trashtable`, `rename`, `ddl`, `dml`, `dm_meta`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0108_0b0b7e69e9`
- Source ID: `tidb-docs-8.1:dm/feature-online-ddl.md#online-schema-change-gh-ost`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bb59c988ad47774b235120379fe09818761f48a3cc6d495cce7c83e4b8782b0b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/feature-online-ddl#online-schema-change-gh-ost
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/feature-online-ddl.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks how DM handles gh-ost tables, DDL, DML, rename operations, or dm_meta records during online-schema-change.
- Retrieval Keywords: online-schema-change: gh-ost, ghostTable `_*_gho`, trashTable `_*_ghc` `_*_del`, realTable, dm_meta.{task_name}_onlineddl, DELETE FROM dm_meta.{task_name}_onlineddl, REPLACE INTO dm_meta.{task_name}_onlineddl, Rename /* gh-ost */ table, alter table test.test4 add column cl1 varchar(20) not null, DM does not execute DML statements that are not for realtable
- Follow-up Guidance: This chunk also notes that gh-ost SQL statements vary with execution parameters and only the major SQL statements are listed.
- Classification Note: This chunk is classified as operation because it describes the step-by-step SQL handling and runtime behavior of DM for gh-ost online schema change.

## Official Source Content

## online-schema-change: gh-ost

When gh-ost implements online-schema-change, 3 types of tables are created:

- gho: used to apply DDLs. When the data is fully replicated and the gho table is consistent with the origin table, the origin table is replaced by renaming.
- ghc: used to store information that is related to online-schema-change.
- del: created by renaming the origin table.

In the process of migration, DM divides the above tables into 3 categories:

- ghostTable: `_*_gho`
- trashTable: `_*_ghc`, `_*_del`
- realTable: the origin table that executes online-ddl.

The SQL statements mostly used by gh-ost and the corresponding operation of DM are as follows:

1. Create the `_ghc` table:

    ```sql
    Create /* gh-ost */ table `test`.`_test4_ghc` (
                            id bigint auto_increment,
                            last_update timestamp not null DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                            hint varchar(64) charset ascii not null,
                            value varchar(4096) charset ascii not null,
                            primary key(id),
                            unique key hint_uidx(hint)
                    ) auto_increment=256 ;
    ```

    DM does not create the `_test4_ghc` table.

2. Create the `_gho` table:

    ```sql
    Create /* gh-ost */ table `test`.`_test4_gho` like `test`.`test4` ;
    ```

    DM does not create the `_test4_gho` table. DM deletes the `dm_meta.{task_name}_onlineddl` record in the downstream according to `ghost_schema`, `ghost_table`, and the `server_id` of `dm_worker`, and clears the related information in memory.

    ```
    DELETE FROM dm_meta.{task_name}_onlineddl WHERE id = {server_id} and ghost_schema = {ghost_schema} and ghost_table = {ghost_table};
    ```

3. Apply the DDL that needs to be executed in the `_gho` table:

    ```sql
    Alter /* gh-ost */ table `test`.`_test4_gho` add column cl1 varchar(20) not null ;
    ```

    DM does not perform the DDL operation of `_test4_gho`. It records this DDL in `dm_meta.{task_name}_onlineddl` and memory.

    ```sql
    REPLACE INTO dm_meta.{task_name}_onlineddl (id, ghost_schema , ghost_table , ddls) VALUES (......);
    ```

4. Write data to the `_ghc` table, and replicate the origin table data to the `_gho` table:

    ```sql
    INSERT /* gh-ost */ INTO `test`.`_test4_ghc` VALUES (......);
    INSERT /* gh-ost `test`.`test4` */ ignore INTO `test`.`_test4_gho` (`id`, `date`, `account_id`, `conversion_price`, `ocpc_matched_conversions`, `ad_cost`, `cl2`)
      (SELECT `id`, `date`, `account_id`, `conversion_price`, `ocpc_matched_conversions`, `ad_cost`, `cl2` FROM `test`.`test4` FORCE INDEX (`PRIMARY`)
        WHERE (((`id` > _binary'1') OR ((`id` = _binary'1'))) AND ((`id` < _binary'2') OR ((`id` = _binary'2')))) lock IN share mode
      )   ;
    ```

    DM does not execute DML statements that are not for **realtable**.

5. After the migration is completed, both the origin table and `_gho` table are renamed, and the online DDL operation is completed:

    ```sql
    Rename /* gh-ost */ table `test`.`test4` to `test`.`_test4_del`, `test`.`_test4_gho` to `test`.`test4`;
    ```

    DM performs the following two operations:

    * DM splits the above `rename` operation into two SQL statements.

        ```sql
        rename test.test4 to test._test4_del;
        rename test._test4_gho to test.test4;
        ```

    * DM does not execute `rename to _test4_del`. When executing `rename ghost_table to origin table`, DM takes the following steps:

        - Read the DDL recorded in memory in Step 3
        - Replace `ghost_table` and `ghost_schema` with `origin_table` and its corresponding schema
        - Execute the DDL that has been replaced

        ```sql
        alter table test._test4_gho add column cl1 varchar(20) not null;
        -- Replaced with:
        alter table test.test4 add column cl1 varchar(20) not null;
        ```

> **Note:**
>
> The specific SQL statements of gh-ost vary with the parameters used in the execution. This document only lists the major SQL statements. For more details, refer to the [gh-ost documentation](https://github.com/github/gh-ost#gh-ost).
