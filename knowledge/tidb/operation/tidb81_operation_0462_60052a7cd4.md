# TiDB Lightning server mode web interface and task controls

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-web-interface.md`
- Source Title: `TiDB Lightning Web Interface`
- Source Heading Path: `TiDB Lightning Web Interface | TiDB Lightning Web Interface > Front page | TiDB Lightning Web Interface > Submit task | TiDB Lightning Web Interface > Table progress | TiDB Lightning Web Interface > Task management`
- Source Line Ranges: `5-79`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `shared`
- Topic Tags: `server-mode`, `web-interface`, `task-submission`, `task-queue`, `table-progress`, `task-management`, `status-addr`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0462_60052a7cd4`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-web-interface.md#tidb-lightning-web-interface`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6297974f854d57d96245f0f33f59f8ccd3474ac45e1d70d1749f86a543a01350`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-web-interface#tidb-lightning-web-interface
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-web-interface.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB Lightning server mode web interface access, task submission and queue behavior, table progress pages, or task controls exposed through status-addr.
- Retrieval Keywords: TiDB Lightning Web Interface, server mode, --server-mode, lightning.server-mode, status-addr, :8289, http://127.0.0.1:8289, submit task, task configurations, TOML files, UPLOAD, SUBMIT, queued tasks, pause/resume current execution, table progress, Task management, current and queued tasks, reorder queued tasks, stop a task immediately
- Follow-up Guidance: The source also states that clicking the ⓘ button opens task management, where each task is labeled by submission time and clicking a task shows the configuration formatted as JSON.
- Classification Note: This is classified as an operation chunk because the content describes how to enable server mode and use the web interface to control imports, inspect table progress, and manage current and queued tasks.

## Official Source Content

# TiDB Lightning Web Interface

TiDB Lightning provides a webpage for viewing the import progress and performing some simple task management. This is called the *server mode*.

To enable server mode, either start `tidb-lightning` with the `--server-mode` flag

```sh
tiup tidb-lightning --server-mode --status-addr :8289
```

or set the `lightning.server-mode` setting in the configuration file.

```toml
[lightning]
server-mode = true
status-addr = ':8289'
```

After TiDB Lightning is launched, visit `http://127.0.0.1:8289` to control the program (the actual URL depends on the `status-addr` setting).

In server mode, TiDB Lightning does not start running immediately. Rather, users submit (multiple) *tasks* via the web interface to import data.
## Front page

![Front page of the web interface](/media/lightning-web-frontpage.png)

Functions of the title bar, from left to right:

| Icon | Function |
|:----|:----|
| "TiDB Lightning" | Click to go back to the front page |
| ⚠ | Display any error message from *previous* task |
| ⓘ | List current and queued tasks; a badge may appear here to indicate number of queued tasks |
| + | Submit a task |
| ⏸/▶ | Pause/resume current execution |
| ⟳ | Configure auto-refresh of the web page |

Three panels below the title bar show all tables in different states:

* Active: these tables are currently being imported
* Completed: these tables have been imported successfully or failed
* Pending: these tables are not yet processed

Each panel contains cards describing the status of the table.
## Submit task

Click the **+** button on the title bar to submit a task.

![Submit task dialog](/media/lightning-web-submit.png)

Tasks are TOML files described as [task configurations](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task). One could also open a local TOML file by clicking **UPLOAD**.

Click **SUBMIT** to run the task. If a task is already running, the new task will be queued and executed after the current task succeeds.
## Table progress

Click the **>** button of a table card on the front page to view the detailed progress of a table.

![Table progress](/media/lightning-web-table.png)

The page shows the import progress of every engine and data files associated with the table.

Click **TiDB Lightning** on the title bar to go back to the front page.
## Task management

Click the **ⓘ** button on the title bar to manage the current and queued tasks.

![Task management page](/media/lightning-web-queue.png)

Each task is labeled by the time it was submitted. Clicking the task would show the configuration formatted as JSON.

Manage tasks by clicking the **⋮** button next to a task. You can stop a task immediately, or reorder queued tasks.
