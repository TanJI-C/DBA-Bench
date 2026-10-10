# TiDB v8.1 Online Unsafe Recovery

This is version-bound operational knowledge for a self-managed TiDB/PD/TiKV v8.1 deployment. It
describes product semantics and safety boundaries; it does not identify objects from a particular
run.

## Product boundary

TiDB v8.1 Online Unsafe Recovery is intended for permanently damaged TiKV Stores that make a
Region unreadable or unwritable because most or all replicas are unavailable. It is explicitly a
lossy recovery operation. A successful recovery can restore a readable and writable Region, but
does not prove that every write after the last confirmed commit boundary survived.

The operation is a PD-owned global task. While it runs, PD pauses Region scheduling, including
split and merge, collects metadata from surviving Stores, distributes a recovery plan, and waits
for TiKV execution reports. The scheduling pause is part of the recovery state; it is not a
normal Offline Store drain.

## Request and state

The product control entry point is equivalent to:

```text
pd-ctl unsafe remove-failed-stores <store_id1,store_id2,...> --timeout <seconds>
```

The failed Store list must contain every permanently failed Store and must not contain a healthy
or connected Store. `Success` means that PD registered the task. It does not mean that recovery
finished. Observe the product status command until the terminal output contains
`Unsafe recovery finished`; a terminal `Unsafe recovery failed` is failure.

The status output may contain stages such as `collect report`, `force leader`,
`demote failed voter`, `create empty region`, and `Collecting reports from alive stores`.
Treat this output as raw task evidence. A client must not convert registration or an intermediate
stage into a synthetic finished result.

## Post-recovery boundary

Online Unsafe Recovery can turn failed voters into failed learners. After the task reports
finished, wait for affected Regions to settle and for failed Stores to reach the product terminal
state before accepting service as recovered. Check both record and secondary-index consistency
with `ADMIN CHECK TABLE`, and validate affected table IDs against
`INFORMATION_SCHEMA.TABLES`.

The operation may restore availability while leaving an unconfirmed write interval. That interval
must be reported rather than silently described as lossless recovery.

