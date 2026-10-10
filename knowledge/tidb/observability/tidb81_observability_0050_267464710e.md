# PD balance and hotspot statistics

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/grafana-pd-dashboard.md`
- Source Title: `Key Monitoring Metrics of PD`
- Source Heading Path: `Key Monitoring Metrics of PD > Statistics - Balance | Key Monitoring Metrics of PD > Statistics - hot write | Key Monitoring Metrics of PD > Statistics - hot read`
- Source Line Ranges: `54-94`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`, `dashboard`
- Topic Tags: `balance`, `hot write`, `hot read`, `store capacity`, `leader distribution`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0050_267464710e`
- Source ID: `tidb-docs-8.1:grafana-pd-dashboard.md#statistics-balance`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ae9098007c61b1ca9ed91fe1bc7b0bd970e4fcb2d14ac0bbb91361851a374006`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/grafana-pd-dashboard#statistics-balance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/grafana-pd-dashboard.md

## Retrieval Guidance

- Use When: Use this when you need balance, hotspot, store capacity, or leader and Region distribution metrics in the PD dashboard.
- Retrieval Keywords: Statistics - Balance, Statistics - hot write, Statistics - hot read, Store capacity, Store available, Store used, Size amplification, Size available ratio, Store leader score, Store Region score, Store leader size, Store Region size, Store leader count, Store Region count, Hot Region's leader distribution, Hot write Region's peer distribution, Hot cache write entry number, Direction of hotspot move leader, Direction of hotspot move peer, Hot Region's peer distribution, Store read rate bytes, Store read rate keys
- Follow-up Guidance: This section groups Balance, hot write, and hot read metrics for TiKV instances.
- Classification Note: This chunk is an observability reference for PD statistics that describe balance and hotspot behavior across TiKV instances.

## Official Source Content

## Statistics - Balance

- Store capacity: The capacity size per TiKV instance
- Store available: The available capacity size per TiKV instance
- Store used: The used capacity size per TiKV instance
- Size amplification: The size amplification ratio per TiKV instance, which is equal to (Store Region size)/(Store used capacity size)
- Size available ratio: The size availability ratio per TiKV instance, which is equal to (Store available capacity size)/(Store capacity size)
- Store leader score: The leader score per TiKV instance
- Store Region score: The Region score per TiKV instance
- Store leader size: The total leader size per TiKV instance
- Store Region size: The total Region size per TiKV instance
- Store leader count: The leader count per TiKV instance
- Store Region count: The Region count per TiKV instance

![PD Dashboard - Balance metrics](/media/pd-dashboard-balance-v4.png)
## Statistics - hot write

- Hot Region's leader distribution: The total number of leader Regions that have become write hotspots on each TiKV instance
- Total written bytes on hot leader Regions: The total written bytes by leader Regions that have become write hotspots on each TiKV instance
- Hot write Region's peer distribution: The total number of peer Regions that have become write hotspots on each TiKV instance
- Total written bytes on hot peer Regions: The written bytes of all peer Regions that have become write hotspots on each TiKV instance
- Store Write rate bytes: The total written bytes on each TiKV instance
- Store Write rate keys: The total written keys on each TiKV instance
- Hot cache write entry number: The number of peers on each TiKV instance that are in the write hotspot statistics module
- Selector events: The event count of Selector in the hotspot scheduling module
- Direction of hotspot move leader: The direction of leader movement in the hotspot scheduling. The positive number means scheduling into the instance. The negative number means scheduling out of the instance
- Direction of hotspot move peer: The direction of peer movement in the hotspot scheduling. The positive number means scheduling into the instance. The negative number means scheduling out of the instance

![PD Dashboard - Hot write metrics](/media/pd-dashboard-hotwrite-v4.png)
## Statistics - hot read

- Hot Region's peer distribution: The total number of peer Regions that have become read hotspots on each TiKV instance
- Total read bytes on hot peer Regions: The total read bytes of peers that have become read hotspots on each TiKV instance
- Store read rate bytes: The total read bytes of each TiKV instance
- Store read rate keys: The total read keys of each TiKV instance
- Hot cache read entry number: The number of peers that are in the read hotspot statistics module on each TiKV instance

![PD Dashboard - Hot read metrics](/media/pd-dashboard-hotread-v4.png)
