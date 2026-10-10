# TiKV log error analysis

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-troubleshooting-map.md`
- Source Title: `TiDB Troubleshooting Map`
- Source Heading Path: `TiDB Troubleshooting Map > 7. Common log analysis > 7.2 TiKV`
- Source Line Ranges: `599-631`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`, `pd`
- Topic Tags: `lock conflict`, `write conflict`, `ttl`, `epoch`, `leader`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0116_a53bf9cf37`
- Source ID: `tidb-docs-8.1:tidb-troubleshooting-map.md#7-2-tikv`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `debe1c55d5bca3fe54ec67fefc9523fdf888e5650a8db7cc690aca7c8555212c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-troubleshooting-map#7-2-tikv
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-troubleshooting-map.md

## Retrieval Guidance

- Use When: Use this chunk when TiKV logs contain lock conflict, write conflict, TTL rollback, stale epoch, or leader routing errors and you need the documented interpretation of their business impact.
- Retrieval Keywords: key is locked, write conflict, TxnLockNotFound, PessimisticLockNotFound, Time To Live (TTL), TTL, LockNotFound error, stale_epoch, peer is not leader, switch region peer to next due to send request fail, split/merge operation, replica is migrated
- Follow-up Guidance: The content references Troubleshoot Write Conflicts in Optimistic Transactions, the LockNotFound error documentation, the corresponding TiDB log switch region peer to next due to send request fail, and the section about some TiKV nodes dropping Leader frequently.
- Classification Note: The classification is diagnosis for TiKV in self-managed deployments because the content maps common TiKV log errors to their causes, expected behavior, and related troubleshooting references involving TiDB and PD.

## Official Source Content

### 7.2 TiKV

- 7.2.1 `key is locked`.

    The read and write have conflict. The read request encounters data that has not been committed and needs to wait until the data is committed.

    A small number of this error has no impact on the business, but a large number of this error indicates that the read-write conflict is severe in your business.

- 7.2.2 `write conflict`.

    This is the write-write conflict in optimistic transactions. If multiple transactions modify the same key, only one transaction succeed and other transactions automatically obtain the timestamp again and retry the operation, with no impact on the business.

    If the conflict is severe, it might cause transaction failure after multiple retries. In this case, it is recommended to use the pessimistic lock. For more details about the error and the solution, see [Troubleshoot Write Conflicts in Optimistic Transactions](https://docs.pingcap.com/tidb/stable/troubleshoot-write-conflicts).

- 7.2.3 `TxnLockNotFound`.

    This transaction commit is too slow, causing it to be rolled back by other transactions after Time To Live (TTL). This transaction will automatically retry, so the business is usually not affected. For a transaction with a size of 0.25 MB or smaller, the default TTL is 3 seconds. For more details, see the [`LockNotFound` error](https://docs.pingcap.com/tidb/stable/troubleshoot-lock-conflicts#locknotfound-error).

- 7.2.4 `PessimisticLockNotFound`.

    Similar to `TxnLockNotFound`. The pessimistic transaction commit is too slow and thus rolled back by other transactions.

- 7.2.5 `stale_epoch`.

    The request epoch is outdated, so TiDB re-sends the request after updating the routing. The business is not affected. Epoch changes when Region has a split/merge operation or a replica is migrated.

- 7.2.6 `peer is not leader`.

    The request is sent to a replica that is not Leader. If the error response indicates which replica is the latest Leader, TiDB updates the local routing according the error and sends a new request to the latest Leader. Usually, the business is not affected.

    In v3.0 and later versions, TiDB tries other peers if the request to the previous Leader fails, which might lead to frequent `peer is not leader` in TiKV log. You can check the `switch region peer to next due to send request fail` log of the corresponding Region in TiDB to determine the root cause of the sending failure. For details, refer to [7.1.4](#71-tidb).

    This error might also be returned if a Region has no Leader due to other reasons. For details, see [4.4](#44-some-tikv-nodes-drop-leader-frequently).
