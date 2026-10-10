# K12 repair and safety contract

## Repair family

Choose repair from trusted evidence. If clustered records are canonical, rebuilding every affected secondary index is valid. If the row handle or base record is not trusted, reconstruct a replacement table from an append-only business ledger and switch it atomically. An assertion setting alone is never historical repair.

## Forensic order

Before upgrade or DDL, preserve an `ADMIN CHECK TABLE` result, primary and secondary path snapshots, and the append-only ledger. Stop the target ODKU writer before repair. Do not mutate the ledger, healthy control tables, or canary contract. Do not delete raw TiKV keys, restart unapproved services, or perform an unbounded rebuild.

## Closed-loop acceptance

Acceptance joins component versions, endpoint assertion scope, `ADMIN CHECK TABLE`, index definitions, forced primary and secondary results, ledger business columns, authorized new canaries, and unchanged healthy neighbors. A successful command or a green endpoint without those invariants is not recovery.

The repair procedure is not required to use a particular temporary table name or DDL ordering. It must leave the live target and business truth in an equivalent, consistent final state and must not alter protected evidence.
