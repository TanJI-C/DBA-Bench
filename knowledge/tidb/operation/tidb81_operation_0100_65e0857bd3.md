# DM migration task precheck overview and usage

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-precheck.md`
- Source Title: `Migration Task Precheck`
- Source Heading Path: `Migration Task Precheck | Migration Task Precheck > Usage scenario | Migration Task Precheck > Descriptions of check items`
- Source Line Ranges: `5-37`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`
- Topic Tags: `precheck`, `task-start`, `manual-check`, `dmctl`, `check-results`, `mandatory-checks`, `warnings`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0100_65e0857bd3`
- Source ID: `tidb-docs-8.1:dm/dm-precheck.md#migration-task-precheck`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4be27042e77bc21fdfc5555c580026986848ed6be66f10cc20c8127c04e59cd1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-precheck#migration-task-precheck
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-precheck.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks what DM migration task precheck does, when it runs, how to trigger it manually, or how DM treats mandatory check failures versus warnings.
- Retrieval Keywords: Migration Task Precheck, precheck automatically at the start of the task, check-task, tiup dmctl check-task ./task.yaml, mandatory check item, warning, DM starts the migration only after the precheck is passed, DM automatically starts a migration task if the check result contains only warnings but no errors
- Follow-up Guidance: If a mandatory check item does not pass, DM returns an error and does not proceed with the migration task; if only non-mandatory items do not pass, DM returns warnings and automatically starts the migration task.
- Classification Note: Classified as an operation chunk because it explains the precheck workflow, the manual `check-task` command, and the meaning of errors and warnings before task start.

## Official Source Content

# Migration Task Precheck

Before using DM to migrate data from upstream to downstream, a precheck helps detect errors in the upstream database configurations and ensures that the migration goes smoothly. This document introduces the DM precheck feature, including its usage scenario, check items, and arguments.
## Usage scenario

To run a data migration task smoothly, DM triggers a precheck automatically at the start of the task and returns the check results. DM starts the migration only after the precheck is passed.

To trigger a precheck manually, run the `check-task` command.

For example:

```bash
tiup dmctl check-task ./task.yaml
```
## Descriptions of check items

After a precheck is triggered for a task, DM checks the corresponding items according to your migration mode configuration.

This section lists all the precheck items.

> **Note:**
>
> In this document, check items that must be passed are labeled "(Mandatory)".

> - If a mandatory check item does not pass, DM returns an error after the check and does not proceed with the migration task. In this case, modify the configurations according to the error message and retry the task after meeting the precheck requirements.
>
> - If a non-mandatory check item does not pass, DM returns a warning after the check. DM automatically starts a migration task if the check result contains only warnings but no errors.
