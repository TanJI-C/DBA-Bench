# BR backup auto-tune limitations and mitigations

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-auto-tune.md`
- Source Title: `Backup Auto-Tune`
- Source Heading Path: `Backup Auto-Tune <span class="version-mark">New in v5.4.0</span> > Limitations`
- Source Line Ranges: `38-57`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tikv`
- Topic Tags: `backup`, `auto-tune`, `limitations`, `write-heavy`, `hotspot`, `traffic-jitter`, `cpu`, `thread-tuning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0069_4df7dcbf62`
- Source ID: `tidb-docs-8.1:br/br-auto-tune.md#limitations`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `654e1e222f1970bd41d94ba17c92104213225ad05b4577297d8c1938485eb1c1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-auto-tune#limitations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-auto-tune.md

## Retrieval Guidance

- Use When: Use this chunk when looking for known limitations of BR backup auto-tune and the documented mitigations for write-heavy clusters, hotspot nodes, or high traffic jitter.
- Retrieval Keywords: Limitations, write-heavy clusters, positive feedback loop, backup.num-threads, clusters with hotspots, disable auto-tune on the hotspot node, high traffic jitter, auto-tune-refresh-interval, Disable auto-tune
- Follow-up Guidance: It explains that backup tasks consume significant CPU because the backup process includes SST decoding, encoding, compression, and decompression, and that the backup thread pool CPU utilization is close to 100% in previous test cases.
- Classification Note: This is classified as performance because the content focuses on cases where auto-tune cannot fully remove backup impact on cluster performance and describes ways to limit or avoid that impact.

## Official Source Content

## Limitations

Auto-tune is a coarse-grained solution for limiting backup speed. It reduces the need for manual tuning. However, because of the lack of fine-grained control, auto-tune might not be able to completely remove the impact of backup on the cluster.

The auto-tune feature has the following issues and corresponding solutions:

- Issue 1: For **write-heavy clusters**, auto-tune might put the workload and backup tasks into a "positive feedback loop": the backup tasks take up too many resources, which causes the cluster to use fewer resources; at this point, auto-tune might mistakenly assume that the cluster is not under heavy workload and thus allowing backup to run faster. In such cases, auto-tune is ineffective.

    - Solution: Manually adjust `backup.num-threads` to a smaller number to limit the number of threads used by backup tasks. The working principle is as follows:

        The backup process includes lots of SST decoding, encoding, compression, and decompression, which consume CPU resources. In addition, previous test cases have shown that during the backup process, the CPU utilization of the thread pool used for backup is close to 100%. This means that the backup tasks take up a lot of CPU resources. By adjusting the number of threads used by the backup tasks, TiKV can limit the CPU cores used by backup tasks, thus reducing the impact of backup tasks on the cluster performance.

- Issue 2: For **clusters with hotspots**, backup tasks on the TiKV node that has hotspots might be excessively limited, which slows down the overall backup process.

    - Solution: Eliminate the hotspot node, or disable auto-tune on the hotspot node (this might reduce the cluster performance).

- Issue 3: For scenarios with **high traffic jitter**, because auto-tune adjusts the speed limit on a fixed interval (1 minute by default), it might not be able to handle high traffic jitter. For details, see [`auto-tune-refresh-interval`](#implementation).

    - Solution: Disable auto-tune.
