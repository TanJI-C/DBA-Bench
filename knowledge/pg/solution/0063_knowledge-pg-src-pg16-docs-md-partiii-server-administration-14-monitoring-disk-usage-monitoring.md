# Disk Full Failure

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/14_monitoring_disk_usage.md`
- Source Title: `Monitoring Disk Usage`
- Source Heading Path: `Monitoring Disk Usage > Disk Full Failure`
- Source Line Ranges: `94-115`
- Chunk ID: `pg16_solution_0063_bcb024e87a`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `375ab59abdf625927e299384662babf80f231c3876a4922e767b8c40ddd0808f`

## Retrieval Guidance

- Use When: 确认磁盘满或接近满，需要恢复服务或释放/迁移空间。
- Retrieval Keywords: disk full, WAL disk full, PANIC shutdown, tablespaces, disk quota, free space
- Follow-up Guidance: 优先释放空间或迁移对象到 tablespace，并为 WAL/data 分区建立容量告警。
- Classification Note: 说明数据盘/WAL 盘满的影响和迁移到 tablespaces 的处置方向。

## Official Source Content

## Disk Full Failure

The most important disk monitoring task of a database administrator
is to make sure the disk doesn't become full.  A filled data disk will
not result in data corruption, but it might prevent useful activity
from occurring. If the disk holding the WAL files grows full, database
server panic and consequent shutdown might occur.

If you cannot free up additional space on the disk by deleting
other things, you can move some of the database files to other file
systems by making use of tablespaces. See [manage-ag-tablespaces](#manage-ag-tablespaces) for more information about that.

> **Tip:**

> Some file systems perform badly when they are almost full, so do
> not wait until the disk is completely full to take action.
>

If your system supports per-user disk quotas, then the database
will naturally be subject to whatever quota is placed on the user
the server runs as.  Exceeding the quota will have the same bad
effects as running out of disk space entirely.
