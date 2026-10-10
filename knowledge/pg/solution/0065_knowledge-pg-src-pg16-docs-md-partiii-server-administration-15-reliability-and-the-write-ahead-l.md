# Off-line Enabling of Checksums

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/15_reliability_and_the_write-ahead_log.md`
- Source Title: `Reliability and the Write-Ahead Log`
- Source Heading Path: `Reliability and the Write-Ahead Log > Data Checksums > Off-line Enabling of Checksums`
- Source Line Ranges: `160-186`
- Chunk ID: `pg16_solution_0065_f45b83f091`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e84ddd21785658915c353aad973bc6965701850093af7b7b8893539e2577fa26`

## Retrieval Guidance

- Use When: 需要在已有集群离线启用/验证/禁用数据页 checksum。
- Retrieval Keywords: pg_checksums, offline checksums, enable checksums, verify checksums, disable checksums
- Follow-up Guidance: 停库后执行并在启动前确认 pg_checksums 结果。
- Classification Note: 指出 pg_checksums 可离线启用、禁用或验证 checksum。

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
