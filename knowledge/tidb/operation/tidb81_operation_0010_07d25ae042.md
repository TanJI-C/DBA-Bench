# Control PD scheduling strategy manually

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/pd-scheduling-best-practices.md`
- Source Title: `PD Scheduling Best Practices`
- Source Heading Path: `PD Scheduling Best Practices > Control scheduling strategy | PD Scheduling Best Practices > Control scheduling strategy > Add/delete scheduler manually | PD Scheduling Best Practices > Control scheduling strategy > Add/delete Operators manually`
- Source Line Ranges: `163-183`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: none
- Topic Tags: `pd-ctl`, `schedulers`, `operators`, `manual-control`, `leader-eviction`, `region-operations`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0010_07d25ae042`
- Source ID: `tidb-docs-8.1:best-practices/pd-scheduling-best-practices.md#control-scheduling-strategy`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `673ee02c795193fc71c2a9606310a481cbcfc60c6c80134e1662a6be9b0c4e3f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/pd-scheduling-best-practices#control-scheduling-strategy
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/pd-scheduling-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks how to manually control PD scheduling strategy with pd-ctl by adding or removing schedulers or operators.
- Retrieval Keywords: scheduler show, scheduler remove balance-leader-scheduler, scheduler add evict-leader-scheduler 1, operator add add-peer 2 5, operator add transfer-leader 2 5, operator add split-region 2, operator remove 2, Add/delete scheduler manually, Add/delete Operators manually, pd-ctl
- Follow-up Guidance: The source refers to PD Control for more details about adjusting the scheduling strategy.
- Classification Note: This chunk is classified as operation because it provides concrete pd-ctl commands for manually changing schedulers and operators in the scheduling system.

## Official Source Content

## Control scheduling strategy

You can use pd-ctl to adjust the scheduling strategy from the following three aspects. Refer to [PD Control](https://docs.pingcap.com/tidb/stable/pd-control) for more details.
### Add/delete scheduler manually

PD supports dynamically adding and removing schedulers directly through pd-ctl. For example:

- `scheduler show`: Shows currently running schedulers in the system
- `scheduler remove balance-leader-scheduler`: Removes (disable) balance-leader-scheduler
- `scheduler add evict-leader-scheduler 1`: Adds a scheduler to remove all leaders in Store 1
### Add/delete Operators manually

PD also supports adding or removing operators directly through pd-ctl. For example:

- `operator add add-peer 2 5`: Adds peers to Region 2 in Store 5
- `operator add transfer-leader 2 5`: Migrates the leader of Region 2 to Store 5
- `operator add split-region 2`: Splits Region 2 into two regions evenly in size
- `operator remove 2`: Removes currently pending operator in Region 2
