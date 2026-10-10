# K12 error, assertion scope, and release evidence

## Consistency errors

`ERROR 8141` is an existence assertion failure during transaction execution. `ERROR 8134` is a data inconsistency report from `ADMIN CHECK TABLE` that compares index values with record values. These errors are evidence to correlate with schema and write history, not a reason to disable checks and continue writes.

## Assertion scope

`tidb_txn_assertion_level` has `OFF`, `FAST`, and `STRICT` behavior and has global and session scope. `STRICT` can expose or prevent a new conflicting write, but changing the global value does not repair rows or sessions that already hold the old value. Check every TiDB SQL endpoint and a fresh session.

## Version boundary

A vulnerable release must be separated from a fixed release using the actual cluster component versions. Upgrading one TiDB server is not enough when PD, TiKV, and TiDB are deployed together. After an upgrade, verify every component and run the same ODKU canary through autocommit and explicit-transaction paths.

The K12 local PoC uses TiDB `v6.5.0` as the vulnerable image and `v7.5.0` as the fixed image. The implementation does not infer reproducibility for an untested release.
