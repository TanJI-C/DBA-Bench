# TiDB Lightning cleanup and goroutine debugging

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-faq.md`
- Source Title: `TiDB Lightning FAQs`
- Source Heading Path: `TiDB Lightning FAQs > How to completely destroy all intermediate data associated with TiDB Lightning? | TiDB Lightning FAQs > How to get the runtime goroutine information of TiDB Lightning`
- Source Line Ranges: `95-139`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `sql`, `tidb`
- Topic Tags: `checkpoint-cleanup`, `metadata-cleanup`, `intermediate-data`, `goroutine-debugging`, `status-port`, `pprof`, `process-signals`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0456_bfbda10eca`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-faq.md#how-to-completely-destroy-all-intermediate-data-associated-with-tidb-lightning`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b72876a2d546677c8f54ec7b61ba0ea997922258fde852c00551a9971357ab27`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-faq#how-to-completely-destroy-all-intermediate-data-associated-with-tidb-lightning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-faq.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about fully removing TiDB Lightning intermediate state or obtaining runtime goroutine information through status-port and pprof.
- Retrieval Keywords: completely destroy all intermediate data associated with TiDB Lightning, tidb-lightning-ctl --config conf/tidb-lightning.toml --checkpoint-remove=all, /tmp/tidb_lightning_checkpoint.pb, sorted-kv-dir, DROP DATABASE IF EXISTS `lightning_metadata`;, lightning_metadata, checkpoint-remove=all, clean up residual metadata, TiDB Lightning v5.1.x and v5.2.x metadata schema, runtime goroutine information of TiDB Lightning, status-port, kill -USR1 <lightning-pid>, starting HTTP server, start HTTP server, started HTTP server, /debug/pprof/goroutine?debug=2
- Follow-up Guidance: If `status-port` is not configured, the chunk says to send the USR1 signal, check the log for the enabled `status-port`, and then access `http://<lightning-ip>:<status-port>/debug/pprof/goroutine?debug=2`.
- Classification Note: This is classified as operation because the content gives operational cleanup steps, process-signal usage, and runtime debugging endpoints for TiDB Lightning.

## Official Source Content

## How to completely destroy all intermediate data associated with TiDB Lightning?

1. Delete the checkpoint file.

    ```sh
    tidb-lightning-ctl --config conf/tidb-lightning.toml --checkpoint-remove=all
    ```

    If, for some reason, you cannot run this command, try manually deleting the file `/tmp/tidb_lightning_checkpoint.pb`.

2. If you are using Local-backend, delete the `sorted-kv-dir` directory in the configuration.

3. Delete all tables and databases created on the TiDB cluster, if needed.

4. Clean up the residual metadata. You need to clean up the metadata schema manually if either of the following conditions exist.

    - For TiDB Lightning v5.1.x and v5.2.x versions, the `tidb-lightning-ctl` command does not clean up the metadata schema in the target cluster. You need to clean it up manually.
    - If you have deleted the checkpoint files manually, you need to clean up the downstream metadata schema manually; otherwise, the correctness of subsequent imports might be affected.

    Use the following command to clean up the metadata:

    ```sql
    DROP DATABASE IF EXISTS `lightning_metadata`;
    ```
## How to get the runtime goroutine information of TiDB Lightning

1. If [`status-port`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-configuration) has been specified in the configuration file of TiDB Lightning, skip this step. Otherwise, you need to send the USR1 signal to TiDB Lightning to enable `status-port`.

    Get the process ID (PID) of TiDB Lightning using commands like `ps`, and then run the following command:

    ```sh
    kill -USR1 <lightning-pid>
    ```

    Check the log of TiDB Lightning. The log of `starting HTTP server` / `start HTTP server` / `started HTTP server` shows the newly enabled `status-port`.

2. Access `http://<lightning-ip>:<status-port>/debug/pprof/goroutine?debug=2` to get the goroutine information.
