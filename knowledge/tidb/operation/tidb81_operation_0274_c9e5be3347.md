# Stop, restart, and wrap up the TiDB Binlog tutorial

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/get-started-with-tidb-binlog.md`
- Source Title: `TiDB Binlog Tutorial`
- Source Heading Path: `TiDB Binlog Tutorial > Cleanup | TiDB Binlog Tutorial > Conclusion`
- Source Line Ranges: `382-419`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`
- Topic Tags: `cleanup`, `shutdown`, `restart`, `startup-order`, `tutorial-summary`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0274_c9e5be3347`
- Source ID: `tidb-docs-8.1:tidb-binlog/get-started-with-tidb-binlog.md#cleanup`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b2a3fcef8b68322e7ef058b2b28268fcbf86e8b26f7fd52a1d9a892e0f787070`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/get-started-with-tidb-binlog#cleanup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/get-started-with-tidb-binlog.md

## Retrieval Guidance

- Use When: Use this chunk when you need the shutdown order, restart command sequence, and tutorial wrap-up for a TiDB Binlog cluster with pd-server, tikv-server, drainer, pump, and tidb-server.
- Retrieval Keywords: Cleanup, Conclusion, pkill -P $$, for p in tidb-server drainer pump tikv-server pd-server; do pkill "$p"; sleep 1; done, shutdown cleanly, restart the cluster, start drainer before pump, pump before tidb-server, ./bin/pd-server --config=pd.toml, ./bin/tikv-server --config=tikv.toml, ./drainer --config=drainer.toml, ./pump --config=pump.toml, ./bin/tidb-server --config=tidb.toml, If any of the components fail to start
- Follow-up Guidance: The chunk concludes by summarizing that the tutorial used a single Pump and single Drainer to replicate from TiDB to downstream MariaDB, and mentions multiple TiDB servers, Pump instances, and additional Drainer instances in more robust deployments.
- Classification Note: This is classified as an operation chunk because it gives the process stop order, restart startup order, and related service commands for the tutorial environment.

## Official Source Content

## Cleanup

To stop the TiDB cluster and TiDB Binlog processes, you can execute `pkill -P $$` in the shell where you started all the processes that form the cluster (pd-server, tikv-server, pump, tidb-server, drainer). To give each component enough time to shut down cleanly, it's helpful to stop them in a particular order:

```bash
for p in tidb-server drainer pump tikv-server pd-server; do pkill "$p"; sleep 1; done
```

Expected output:

```
kolbe@localhost tidb-latest-linux-amd64]$ for p in tidb-server drainer pump tikv-server pd-server; do pkill "$p"; sleep 1; done
[4]-  Done                    ./bin/tidb-server --config=tidb.toml &>tidb.out
[5]+  Done                    ./drainer --config=drainer.toml &>drainer.out
[3]+  Done                    ./pump --config=pump.toml &>pump.out
[2]+  Done                    ./bin/tikv-server --config=tikv.toml &>tikv.out
[1]+  Done                    ./bin/pd-server --config=pd.toml &>pd.out
```

If you wish to restart the cluster after all services exit, use the same commands you ran originally to start the services. As discussed in the [`binlogctl`](#binlogctl) section above, you'll need to start `drainer` before `pump`, and `pump` before `tidb-server`.

```bash
./bin/pd-server --config=pd.toml &>pd.out &
./bin/tikv-server --config=tikv.toml &>tikv.out &
./drainer --config=drainer.toml &>drainer.out &
sleep 3
./pump --config=pump.toml &>pump.out &
sleep 3
./bin/tidb-server --config=tidb.toml &>tidb.out &
```

If any of the components fail to start, try to restart the failed individual component(s).
## Conclusion

In this tutorial, we've set up TiDB Binlog to replicate from a TiDB cluster to a downstream MariaDB server, using a cluster with a single Pump and a single Drainer. As we've seen, TiDB Binlog is a comprehensive platform for capturing and processing changes to a TiDB cluster.

In a more robust development, testing, or production deployment, you'd have multiple TiDB servers for high availability and scaling purposes, and you'd use multiple Pump instances to ensure that application traffic to TiDB server instances is unaffected by problems in the Pump cluster. You may also use additional Drainer instances to push updates to different downstream platforms or to implement incremental backups.
