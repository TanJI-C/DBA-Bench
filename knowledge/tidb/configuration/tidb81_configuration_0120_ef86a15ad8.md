# Optimizer Fix Controls overview and tidb_opt_fix_control usage

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/optimizer-fix-controls.md`
- Source Title: `Optimizer Fix Controls`
- Source Heading Path: `Optimizer Fix Controls | Optimizer Fix Controls > Introduction to `tidb_opt_fix_control``
- Source Line Ranges: `5-26`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `optimizer`, `system-variable`, `fix-controls`, `session-settings`, `plan-behavior`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0120_ef86a15ad8`
- Source ID: `tidb-docs-8.1:optimizer-fix-controls.md#optimizer-fix-controls`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0f3acc1dab4cd4a994996e1edbae1420802606feb6f7bf3f082b14753f93b6c0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/optimizer-fix-controls#optimizer-fix-controls
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/optimizer-fix-controls.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the purpose, syntax, or example usage of the `tidb_opt_fix_control` system variable for fine-grained optimizer behavior control.
- Retrieval Keywords: tidb_opt_fix_control, Optimizer Fix Controls, system variable, SET SESSION tidb_opt_fix_control, 44262:ON,44389:ON, fix number GitHub Issue, optimizer behavior control, comma-separated fixes
- Follow-up Guidance: The chunk also explains that each fix is identified by a number corresponding to a GitHub Issue and that multiple fixes are provided in the format "<#issue1>:<value1>,<#issue2>:<value2>".
- Classification Note: This is classified as configuration because the content introduces the `tidb_opt_fix_control` system variable and shows how to set it in a session.

## Official Source Content

# Optimizer Fix Controls

As the product evolves iteratively, the behavior of the TiDB optimizer changes, which in turn generates more reasonable execution plans. However, in some particular scenarios, the new behavior might lead to unexpected results. For example:

- The effect of some behaviors relies on a specific scenario. Changes that bring improvements to most scenarios might cause regressions to others.
- Sometimes, the relationship between changes in the behavior details and their consequences is very complicated. An improvement in a certain behavior might cause overall regression.

Therefore, TiDB provides the Optimizer Fix Controls feature that allows you to make fine-grained control of TiDB optimizer behaviors by setting values for a group of fixes. This document describes the Optimizer Fix Controls feature and how to use them, and lists all the fixes that TiDB currently supports for Optimizer Fix Controls.
## Introduction to `tidb_opt_fix_control`

Starting from v6.5.3 and v7.1.0, TiDB provides the [`tidb_opt_fix_control`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_fix_control-new-in-v653-and-v710) system variable to control the behavior of the optimizer in a more fine-grained way.

Each fix is a control item used to adjust the behavior in the TiDB optimizer for one particular purpose. It is denoted by a number that corresponds to a GitHub Issue that contains the technical details of the behavior change. For example, for fix `44262`, you can review what it controls in [Issue 44262](https://github.com/pingcap/tidb/issues/44262).

The [`tidb_opt_fix_control`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_fix_control-new-in-v653-and-v710) system variable accepts multiple fixes as one value, separated by commas (`,`). The format is `"<#issue1>:<value1>,<#issue2>:<value2>,...,<#issueN>:<valueN>"`, where `<#issueN>` is the fix number. For example:

```sql
SET SESSION tidb_opt_fix_control = '44262:ON,44389:ON';
```
