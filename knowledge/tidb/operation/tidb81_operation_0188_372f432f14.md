# PD store query and deletion commands

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-control.md`
- Source Title: `PD Control User Guide`
- Source Heading Path: `PD Control User Guide > Command > `store [delete | cancel-delete | label | weight | remove-tombstone | limit ] <store_id> [--jq="<query string>"]` | PD Control User Guide > Command > `store [delete | cancel-delete | label | weight | remove-tombstone | limit ] <store_id> [--jq="<query string>"]` > Get a store | PD Control User Guide > Command > `store [delete | cancel-delete | label | weight | remove-tombstone | limit ] <store_id> [--jq="<query string>"]` > Delete a store`
- Source Line Ranges: `1000-1054`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`
- Topic Tags: `pd-ctl`, `store`, `jq`, `offline`, `tombstone`, `cancel-delete`, `remove-tombstone`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0188_372f432f14`
- Source ID: `tidb-docs-8.1:pd-control.md#store-delete-cancel-delete-label-weight-remove-tombstone-limit-store-id-jq-query-string`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `40c6bf3a71442fdb853bf636a6861951e8df0a158b678aa4f7d2480e37564b90`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-control#store-delete-cancel-delete-label-weight-remove-tombstone-limit-store-id-jq-query-string
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-control.md

## Retrieval Guidance

- Use When: Use this chunk when looking for pd-ctl store commands to list store information, query a specific store by ID, delete a store, cancel deletion for an Offline store, or remove all Tombstone stores.
- Retrieval Keywords: store, store 1, store delete 1, store cancel-delete 1, store remove-tombstone, Offline, Up, Tombstone, --jq, jq formatted output, store limit
- Follow-up Guidance: The content notes that if the PD leader changes during store deletion, you need to modify the store limit manually using the store limit command.
- Classification Note: This is classified as an operation chunk because the official content documents pd-ctl store management commands and their state-related behavior for store deletion and cleanup.

## Official Source Content

### `store [delete | cancel-delete | label | weight | remove-tombstone | limit ] <store_id> [--jq="<query string>"]`

For a jq formatted output, see [jq-formatted-json-output-usage](#jq-formatted-json-output-usage).
#### Get a store

To display the information of all stores, run the following command:

```bash
store
```

```
{
  "count": 3,
  "stores": [...]
}
```

To get the store with id of 1, run the following command:

```bash
store 1
```

```
......
```
#### Delete a store

To delete the store with id of 1, run the following command:

```bash
store delete 1
```

To cancel deleting `Offline` state stores which are deleted using `store delete`, run the `store cancel-delete` command. After canceling, the store changes from `Offline` to `Up`. Note that the `store cancel-delete` command cannot change a `Tombstone` state store to the `Up` state.

To cancel deleting the store with id of 1, run the following command:

```bash
store cancel-delete 1
```

To delete all stores in `Tombstone` state, run the following command:

```bash
store remove-tombstone
```

> **Note:**
>
> If the PD leader changes during store deletion, you need to modify the store limit manually using the [`store limit`](#configure-store-scheduling-speed) command.
