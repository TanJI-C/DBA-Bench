# DXF implementation principles and references

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-distributed-execution-framework.md`
- Source Title: `TiDB Distributed eXecution Framework (DXF)`
- Source Heading Path: `TiDB Distributed eXecution Framework (DXF) > Implementation principles | TiDB Distributed eXecution Framework (DXF) > See also`
- Source Line Ranges: `107-131`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `architecture`, `dispatcher`, `scheduler`, `subtask-executor`, `resource-pool`, `references`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0096_1e593a3f7c`
- Source ID: `tidb-docs-8.1:tidb-distributed-execution-framework.md#implementation-principles`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `73eb0b41f0c68bcdac3428a45d02e8d8410d2e8960bd1a508378f00e1d322dc5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework#implementation-principles
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-distributed-execution-framework.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks for the DXF internal architecture, execution modules, or reference links for DDL execution principles.
- Retrieval Keywords: Implementation principles, DXF architecture, Dispatcher, Scheduler, Subtask Executor, Resource pool, distributed execution plan, task status, runtime task information, execution status of subtasks, Execution Principles and Best Practices of DDL Statements
- Follow-up Guidance: The source includes see-also links to Execution Principles and Best Practices of DDL Statements.
- Classification Note: This is classified as architecture because the content explains the internal DXF modules and their responsibilities in task execution.

## Official Source Content

## Implementation principles

The architecture of the DXF is as follows:

![Architecture of the DXF](/media/dist-task/dist-task-architect.jpg)

As shown in the preceding diagram, the execution of tasks in the DXF is mainly handled by the following modules:

- Dispatcher: generates the distributed execution plan for each task, manages the execution process, converts the task status, and collects and feeds back the runtime task information.
- Scheduler: replicates the execution of distributed tasks among TiDB nodes to improve the efficiency of task execution.
- Subtask Executor: the actual executor of distributed subtasks. In addition, the Subtask Executor returns the execution status of subtasks to the Scheduler, and the Scheduler updates the execution status of subtasks in a unified manner.
- Resource pool: provides the basis for quantifying resource usage and management by pooling computing resources of the above modules.
## See also

* [Execution Principles and Best Practices of DDL Statements](https://docs.pingcap.com/tidb/stable/best-practices/ddl-introduction)

* [Execution Principles and Best Practices of DDL Statements](https://docs.pingcap.com/tidb/stable/ddl-introduction)
