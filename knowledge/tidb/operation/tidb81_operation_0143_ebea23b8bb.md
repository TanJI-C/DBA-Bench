# PD management FAQs for bootstrap, startup, encryption, and connections

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/manage-cluster-faq.md`
- Source Title: `TiDB Cluster Management FAQs`
- Source Heading Path: `TiDB Cluster Management FAQs > PD management | TiDB Cluster Management FAQs > PD management > The `TiKV cluster is not bootstrapped` message is displayed when I access PD | TiDB Cluster Management FAQs > PD management > The `etcd cluster ID mismatch` message is displayed when starting PD | TiDB Cluster Management FAQs > PD management > The `[PD:encryption:ErrEncryptionNewMasterKey]fail to get encryption key from file /root/path/file%!(EXTRA string=open /root/path/file: permission denied)` message is displayed when enabling encryption at rest for PD | TiDB Cluster Management FAQs > PD management > What's the maximum tolerance for time synchronization error of PD? | TiDB Cluster Management FAQs > PD management > How does the client connection find PD?`
- Source Line Ranges: `136-159`
- Source Scope: `shared`
- Primary Component: `pd`
- Related Components: `tidb`, `tikv`
- Topic Tags: `bootstrap`, `startup-errors`, `etcd`, `encryption-at-rest`, `master-key`, `time-synchronization`, `leader-discovery`, `client-connection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0143_ebea23b8bb`
- Source ID: `tidb-docs-8.1:faq/manage-cluster-faq.md#pd-management`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `42022c39d8ad9f93ead6db7c711baf5d863f7f2a4ee0139b1f7cc6ec33cd98fb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/manage-cluster-faq#pd-management
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/manage-cluster-faq.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting PD bootstrap access, PD startup errors about etcd cluster ID mismatch, PD encryption-at-rest master key file errors, PD time synchronization tolerance, or how TiDB discovers the PD leader.
- Retrieval Keywords: TiKV cluster is not bootstrapped, etcd cluster ID mismatch, --initial-cluster, [PD:encryption:ErrEncryptionNewMasterKey], fail to get encryption key from file, permission denied, encryption at rest, root directory, time synchronization error of PD, read of historical versions, current leader, TiDB reconnects to the leader PD
- Follow-up Guidance: The source states that if PD shows `TiKV cluster is not bootstrapped`, start the TiKV cluster so that PD becomes accessible after TiKV is initialized.
- Classification Note: This is classified as operation for the PD component because the official content is a PD management FAQ focused on startup, encryption, time synchronization, and client connection behavior with PD.

## Official Source Content

## PD management

This section describes common problems you may encounter during PD management, their causes, and solutions.
### The `TiKV cluster is not bootstrapped` message is displayed when I access PD

Most of the APIs of PD are available only when the TiKV cluster is initialized. This message is displayed if PD is accessed when PD is started while TiKV is not started when a new cluster is deployed. If this message is displayed, start the TiKV cluster. When TiKV is initialized, PD is accessible.
### The `etcd cluster ID mismatch` message is displayed when starting PD

This is because the `--initial-cluster` in the PD startup parameter contains a member that doesn't belong to this cluster. To solve this problem, check the corresponding cluster of each member, remove the wrong member, and then restart PD.
### The `[PD:encryption:ErrEncryptionNewMasterKey]fail to get encryption key from file /root/path/file%!(EXTRA string=open /root/path/file: permission denied)` message is displayed when enabling encryption at rest for PD
 
Encryption at rest does not support storing the key file in the `root` directory or its subdirectories. Even if you grant read permissions, the same error occurs. To resolve this issue, store the key file in a location outside the `root` directory.
### What's the maximum tolerance for time synchronization error of PD?

PD can tolerate any synchronization error, but a larger error value means a larger gap between the timestamp allocated by the PD and the physical time, which will affect functions such as read of historical versions.
### How does the client connection find PD?

The client connection can only access the cluster through TiDB. TiDB connects PD and TiKV. PD and TiKV are transparent to the client. When TiDB connects to any PD, the PD tells TiDB who is the current leader. If this PD is not the leader, TiDB reconnects to the leader PD.
