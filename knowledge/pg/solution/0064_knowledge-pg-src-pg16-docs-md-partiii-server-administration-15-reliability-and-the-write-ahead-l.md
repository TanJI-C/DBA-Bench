# Data Checksums

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/15_reliability_and_the_write-ahead_log.md`
- Source Title: `Reliability and the Write-Ahead Log`
- Source Heading Path: `Reliability and the Write-Ahead Log > Data Checksums`
- Source Line Ranges: `160-186`
- Chunk ID: `pg16_solution_0064_8052eeab99`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e84ddd21785658915c353aad973bc6965701850093af7b7b8893539e2577fa26`

## Retrieval Guidance

- Use When: 诊断 checksum failure、确认 checksum 是否启用或损坏恢复需临时读取页面。
- Retrieval Keywords: data checksums, data_checksums, ignore_checksum_failure, page corruption, initdb --data-checksums
- Follow-up Guidance: 绕过 checksum 只应临时使用，恢复后定位硬件/介质问题并重建受损数据。
- Classification Note: 说明 checksum 启用/检查状态和页面损坏恢复时的临时绕过参数。

## Official Source Content

## Data Checksums

By default, data pages are not protected by checksums, but this can
optionally be enabled for a cluster. When enabled, each data page includes
a checksum that is updated when the page is written and verified each time
the page is read. Only data pages are protected by checksums; internal data
structures and temporary files are not.

Checksums can be enabled when the cluster is initialized using [initdb](#app-initdb-data-checksums).
They can also be enabled or disabled at a later time as an offline
operation. Data checksums are enabled or disabled at the full cluster
level, and cannot be specified individually for databases or tables.

The current state of checksums in the cluster can be verified by viewing the
value of the read-only configuration variable [guc-data-checksums](#guc-data-checksums) by issuing the command `SHOW
data_checksums`.

When attempting to recover from page corruptions, it may be necessary to
bypass the checksum protection. To do this, temporarily set the
configuration parameter [guc-ignore-checksum-failure](#guc-ignore-checksum-failure).

### Off-line Enabling of Checksums

The [pg_checksums](#app-pgchecksums)
application can be used to enable or disable data checksums, as well as
verify checksums, on an offline cluster.
