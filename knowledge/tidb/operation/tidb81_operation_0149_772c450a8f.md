# Online migration and traffic cutover FAQs

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/migration-tidb-faq.md`
- Source Title: `Migration FAQs`
- Source Heading Path: `Migration FAQs > Migrate the data online | Migration FAQs > Migrate the data online > Is there a current solution to replicating data from TiDB to other databases like HBase and Elasticsearch? | Migration FAQs > Migrate the traffic | Migration FAQs > Migrate the traffic > How to migrate the traffic quickly? | Migration FAQs > Migrate the traffic > Is there a limit for the total write and read capacity in TiDB? | Migration FAQs > Migrate the traffic > The error message `transaction too large` is displayed | Migration FAQs > Migrate the traffic > How to import data in batches? | Migration FAQs > Migrate the traffic > Does TiDB release space immediately after deleting data? | Migration FAQs > Migrate the traffic > Can I execute DDL operations on the target table when loading data? | Migration FAQs > Migrate the traffic > Does TiDB support the `replace into` syntax? | Migration FAQs > Migrate the traffic > Why does the query speed getting slow after deleting data? | Migration FAQs > Migrate the traffic > What is the most efficient way of deleting data?`
- Source Line Ranges: `132-181`
- Source Scope: `shared`
- Primary Component: `tidb`
- Related Components: `dm`, `tikv`, `shared`
- Topic Tags: `online-migration`, `replication`, `traffic-cutover`, `load-balancer`, `read-scaling`, `write-scaling`, `transaction-size`, `batch-import`, `space-reclamation`, `ddl-restrictions`, `replace-into`, `delete-performance`, `region-merge`, `garbage-collection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0149_772c450a8f`
- Source ID: `tidb-docs-8.1:faq/migration-tidb-faq.md#migrate-the-data-online`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e5df2a0901414fe15be7ccd5ef67100393750437d5e02d7d9cd82484e2b63003`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/migration-tidb-faq#migrate-the-data-online
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/migration-tidb-faq.md

## Retrieval Guidance

- Use When: Use this chunk when answering questions about online migration, traffic cutover, TiDB read or write scaling, transaction too large limits, batch import sizing, space reclamation after delete or drop, DDL restrictions during loading, REPLACE INTO support, and delete performance after large deletions.
- Retrieval Keywords: Migrate the data online, replicating data from TiDB to other databases like HBase and Elasticsearch, data replication depends on the application itself, How to migrate the traffic quickly, TiDB Data Migration, DM, HAproxy, LVS, F5, DNS, stable network LB, seamless migration, Is there a limit for the total write and read capacity in TiDB, add more TiDB servers, add more TiKV nodes, transaction too large, txn-entry-size-limit, txn-total-size-limit, 6MB, 100MB, 10G, How to import data in batches, within 10,000 for each batch, Does TiDB release space immediately after deleting data, DELETE, TRUNCATE, DROP, TiDB GC, Garbage Collection, COMPACT, Can I execute DDL operations on the target table when loading data, Does TiDB support the replace into syntax, replace into, Why does the query speed getting slow after deleting data, Region Merge, What is the most efficient way of deleting data, Delete from t where xx limit 5000, Affected Rows == 0, strong filter index column, primary key
- Follow-up Guidance: For slower queries after deleting data and for large-delete patterns, the content points to the deleting data section in TiDB Best Practices for more details.
- Classification Note: This chunk is classified as operation because the official content centers on online migration flow, traffic switching, capacity scaling, transaction limits, and operational behavior during loading and deletion.

## Official Source Content

## Migrate the data online
### Is there a current solution to replicating data from TiDB to other databases like HBase and Elasticsearch?

No. Currently, the data replication depends on the application itself.
## Migrate the traffic
### How to migrate the traffic quickly?

It is recommended to migrate application data from MySQL to TiDB using [TiDB Data Migration](https://docs.pingcap.com/tidb/stable/dm/dm-overview) tool. You can migrate the read and write traffic in batches by editing the network configuration as needed. Deploy a stable network LB (such as HAproxy, LVS, F5, and DNS) on the upper layer, in order to implement seamless migration by directly editing the network configuration.
### Is there a limit for the total write and read capacity in TiDB?

The total read capacity has no limit. You can increase the read capacity by adding more TiDB servers. Generally the write capacity has no limit as well. You can increase the write capacity by adding more TiKV nodes.
### The error message `transaction too large` is displayed

Due to the limitation of the underlying storage engine, each key-value entry (one row) in TiDB should be no more than 6MB. You can adjust the [`txn-entry-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-entry-size-limit-new-in-v4010-and-v500) configuration value up to 120MB.

Distributed transactions need two-phase commit and the bottom layer performs the Raft replication. If a transaction is very large, the commit process would be quite slow and the write conflict is more likely to occur. Moreover, the rollback of a failed transaction leads to an unnecessary performance penalty. To avoid these problems, we limit the total size of key-value entries to no more than 100MB in a transaction by default. If you need larger transactions, modify the value of `txn-total-size-limit` in the TiDB configuration file. The maximum value of this configuration item is up to 10G. The actual limitation is also affected by the physical memory of the machine.

There are [similar limits](https://cloud.google.com/spanner/docs/limits) on Google Cloud Spanner.
### How to import data in batches?

When you import data, insert in batches and keep the number of rows within 10,000 for each batch.
### Does TiDB release space immediately after deleting data?

None of the `DELETE`, `TRUNCATE` and `DROP` operations release data immediately. For the `TRUNCATE` and `DROP` operations, after the TiDB GC (Garbage Collection) time (10 minutes by default), the data is deleted and the space is released. For the `DELETE` operation, the data is deleted but the space is not released according to TiDB GC. When subsequent data is written into RocksDB and executes `COMPACT`, the space is reused.
### Can I execute DDL operations on the target table when loading data?

No. None of the DDL operations can be executed on the target table when you load data, otherwise the data fails to be loaded.
### Does TiDB support the `replace into` syntax?

Yes.
### Why does the query speed getting slow after deleting data?

Deleting a large amount of data leaves a lot of useless keys, affecting the query efficiency. The [Region Merge feature](https://docs.pingcap.com/tidb/stable/best-practices/massive-regions-best-practices#method-3-enable-region-merge) can solve this problem. For more details, see the [deleting data section in TiDB Best Practices](https://www.pingcap.com/blog/tidb-best-practice/#write).
### What is the most efficient way of deleting data?

When deleting a large amount of data, it is recommended to use `Delete from t where xx limit 5000;`. It deletes through the loop and uses `Affected Rows == 0` as a condition to end the loop, so as not to exceed the limit of transaction size. With the prerequisite of meeting business filtering logic, it is recommended to add a strong filter index column or directly use the primary key to select the range, such as `id >= 5000*n+m and id < 5000*(n+1)+m`.

If the amount of data that needs to be deleted at a time is very large, this loop method will get slower and slower because each deletion traverses backward. After deleting the previous data, lots of deleted flags remain for a short period (then all will be processed by Garbage Collection) and influence the following Delete statement. If possible, it is recommended to refine the Where condition. See [details in TiDB Best Practices](https://www.pingcap.com/blog/tidb-best-practice/#write).
