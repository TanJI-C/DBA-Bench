# Restore encrypted snapshots with BR

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-snapshot-manual.md`
- Source Title: `TiDB Snapshot Backup and Restore Command Manual`
- Source Heading Path: `TiDB Snapshot Backup and Restore Command Manual > Restore encrypted snapshots`
- Source Line Ranges: `280-294`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: none
- Topic Tags: `snapshot-restore`, `encryption`, `decryption`, `experimental-feature`, `crypter`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0013_c8955b085f`
- Source ID: `tidb-docs-8.1:br/br-snapshot-manual.md#restore-encrypted-snapshots`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `88dd6ca24e9659766852e4fe57ef814142f6c8e4e0f6f77511da0c655732b873`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual#restore-encrypted-snapshots
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-snapshot-manual.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how BR restores encrypted snapshots by supplying decryption parameters such as the crypter method and key.
- Retrieval Keywords: Restore encrypted snapshots, experimental feature, tiup br restore full, --crypter.method, --crypter.key, aes128-ctr, decryption parameters, decryption algorithm, key is incorrect, data cannot be restored
- Follow-up Guidance: The content states that the decryption algorithm and key must be correct or the data cannot be restored.
- Classification Note: The official content is classified as recovery for BR because it covers restoring snapshot data that was encrypted and requires matching decryption settings.

## Official Source Content

## Restore encrypted snapshots

> **Warning:**
>
> This is an experimental feature. It is not recommended that you use it in the production environment.

After encrypting the backup data, you need to pass in the corresponding decryption parameters to restore the data. Ensure that the decryption algorithm and key are correct. If the decryption algorithm or key is incorrect, the data cannot be restored. The following is an example:

```shell
tiup br restore full\
    --pd "${PD_IP}:2379" \
    --storage "s3://${backup_collection_addr}/snapshot-${date}?access-key=${access-key}&secret-access-key=${secret-access-key}" \
    --crypter.method aes128-ctr \
    --crypter.key 0123456789abcdef0123456789abcdef
```
