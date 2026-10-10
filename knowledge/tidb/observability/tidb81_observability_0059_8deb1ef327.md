# TiKV flow control and scheduler metrics

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/grafana-tikv-dashboard.md`
- Source Title: `Key Monitoring Metrics of TiKV`
- Source Heading Path: `Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Flow Control | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Scheduler | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Scheduler - commit | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Scheduler - pessimistic_rollback | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Scheduler - prewrite | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Scheduler - rollback`
- Source Line Ranges: `187-260`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `dashboard`
- Topic Tags: `grafana`, `metrics`, `flow-control`, `scheduler`, `commit`, `prewrite`, `rollback`, `pessimistic-rollback`, `latency`, `throttling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0059_8deb1ef327`
- Source ID: `tidb-docs-8.1:grafana-tikv-dashboard.md#flow-control`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f89edf74a4d60446fedf250a9dd2ec78b49657f12235b88879fabf150fb19f36`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#flow-control
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/grafana-tikv-dashboard.md

## Retrieval Guidance

- Use When: Use this chunk when locating TiKV-Details dashboard metrics for flow control or scheduler behavior, including commit, prewrite, rollback, and pessimistic_rollback latency, throttling, and scan details.
- Retrieval Keywords: TiKV-Details dashboard, Flow Control, Scheduler flow, Scheduler discard ratio, Throttle duration, Scheduler throttled CF, Flow controller actions, Flush/L0 flow, Flow control factors, Compaction pending bytes, Txn command throttled duration, Non-txn command throttled duration, Scheduler, Scheduler stage total, Scheduler writing bytes, Scheduler priority commands, Scheduler pending commands, Scheduler - commit, Scheduler command duration, Scheduler latch wait duration, Scheduler keys read, Scheduler keys written, Scheduler scan details, Scheduler scan details [lock], Scheduler scan details [write], Scheduler scan details [default], pessimistic_rollback, Scheduler - prewrite, Scheduler - rollback
- Follow-up Guidance: The source also states threshold-oriented interpretations such as flow control existing when Scheduler discard ratio is greater than 0 or Throttle duration has values, and command duration or latch wait duration for commit, pessimistic_rollback, prewrite, and rollback being less than 1s.
- Classification Note: This is classified as observability for TiKV because the content enumerates Grafana TiKV-Details dashboard monitoring metrics and their meanings for scheduler and flow-control behavior.

## Official Source Content

### Flow Control

- Scheduler flow: The scheduler traffic on each TiKV instance in real time.
- Scheduler discard ratio: The rejection ratio of scheduler requests on each TiKV instance. If this ratio is greater than 0, it indicates that flow control exists. When `Compaction pending bytes` exceeds its threshold, TiKV will linearly increase the `Scheduler discard ratio` based on the exceeded portion. The client will retry the rejected requests automatically.
- Throttle duration: The blocked duration for the execution of the scheduler requests when flow control is triggered due to too many L0 files. If this metric has values, it indicates that flow control exists.
- Scheduler throttled CF: The CF that triggers RocksDB throttling when the flow control threshold is reached.
- Flow controller actions: The actions that trigger RocksDB throttling when the flow control threshold is reached.
- Flush/L0 flow: The traffic of flush and L0 compaction for different CFs of RocksDB on each TiKV instance.
- Flow control factors: The factors related to triggering RocksDB throttling.
- Compaction pending bytes: The size of the RocksDB data awaiting compaction in real time on each TiKV instance.
- Txn command throttled duration: The blocked duration for commands related to transactions due to throttling. Under normal circumstances, this metric is 0.
- Non-txn command throttled duration: The blocked duration for other commands due to throttling. Under normal circumstances, this metric is 0.

![TiKV Dashboard - Flow Control metrics](/media/tikv-dashboard-flow-control.png)
### Scheduler

- Scheduler stage total: The number of commands at each stage per second. There should not be a lot of errors in a short time.
- Scheduler writing bytes: The total written bytes by commands processed on each TiKV instance
- Scheduler priority commands: The count of different priority commands per second
- Scheduler pending commands: The count of pending commands per TiKV instance per second

![TiKV Dashboard - Scheduler metrics](/media/tikv-dashboard-scheduler.png)
### Scheduler - commit

- Scheduler stage total: The number of commands at each stage per second when executing the commit command. There should not be a lot of errors in a short time.
- Scheduler command duration: The time consumed when executing the commit command. It should be less than `1s`.
- Scheduler latch wait duration: The waiting time caused by latch when executing the commit command. It should be less than `1s`.
- Scheduler keys read: The count of keys read by a commit command
- Scheduler keys written: The count of keys written by a commit command
- Scheduler scan details: The keys scan details of each CF when executing the commit command.
- Scheduler scan details [lock]: The keys scan details of lock CF when executing the commit command
- Scheduler scan details [write]: The keys scan details of write CF when executing the commit command
- Scheduler scan details [default]: The keys scan details of default CF when executing the commit command

![TiKV Dashboard - Scheduler commit metrics](/media/tikv-dashboard-scheduler-commit.png)
### Scheduler - pessimistic_rollback

- Scheduler stage total: The number of commands at each stage per second when executing the `pessimistic_rollback` command. There should not be a lot of errors in a short time.
- Scheduler command duration: The time consumed when executing the `pessimistic_rollback` command. It should be less than `1s`.
- Scheduler latch wait duration: The waiting time caused by latch when executing the `pessimistic_rollback` command. It should be less than `1s`.
- Scheduler keys read: The count of keys read by a `pessimistic_rollback` command
- Scheduler keys written: The count of keys written by a `pessimistic_rollback` command
- Scheduler scan details: The keys scan details of each CF when executing the `pessimistic_rollback` command.
- Scheduler scan details [lock]: The keys scan details of lock CF when executing the `pessimistic_rollback` command
- Scheduler scan details [write]: The keys scan details of write CF when executing the `pessimistic_rollback` command
- Scheduler scan details [default]: The keys scan details of default CF when executing the `pessimistic_rollback` command
### Scheduler - prewrite

- Scheduler stage total: The number of commands at each stage per second when executing the prewrite command. There should not be a lot of errors in a short time.
- Scheduler command duration: The time consumed when executing the prewrite command. It should be less than `1s`.
- Scheduler latch wait duration: The waiting time caused by latch when executing the prewrite command. It should be less than `1s`.
- Scheduler keys read: The count of keys read by a prewrite command
- Scheduler keys written: The count of keys written by a prewrite command
- Scheduler scan details: The keys scan details of each CF when executing the prewrite command.
- Scheduler scan details [lock]: The keys scan details of lock CF when executing the prewrite command
- Scheduler scan details [write]: The keys scan details of write CF when executing the prewrite command
- Scheduler scan details [default]: The keys scan details of default CF when executing the prewrite command
### Scheduler - rollback

- Scheduler stage total: The number of commands at each stage per second when executing the rollback command. There should not be a lot of errors in a short time.
- Scheduler command duration: The time consumed when executing the rollback command. It should be less than `1s`.
- Scheduler latch wait duration: The waiting time caused by latch when executing the rollback command. It should be less than `1s`.
- Scheduler keys read: The count of keys read by a rollback command
- Scheduler keys written: The count of keys written by a rollback command
- Scheduler scan details: The keys scan details of each CF when executing the rollback command.
- Scheduler scan details [lock]: The keys scan details of lock CF when executing the rollback command
- Scheduler scan details [write]: The keys scan details of write CF when executing the rollback command
- Scheduler scan details [default]: The keys scan details of default CF when executing the rollback command
