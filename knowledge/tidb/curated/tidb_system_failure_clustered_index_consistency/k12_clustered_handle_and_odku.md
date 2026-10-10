# K12 clustered handle and ODKU mechanism

## Clustered primary key

A clustered primary key is the physical row handle in TiDB. When a primary-key column changes, the row key and every secondary index entry that carries the handle must move together. A nonclustered primary-key table is a control, not proof that a clustered table has the same failure.

## ODKU failure

TiDB issue 44565 covers a case where an `ON UPDATE` column changes a primary-key handle but the write path does not mark the handle as changed. Repeated `INSERT ... ON DUPLICATE KEY UPDATE` can then leave a secondary index inconsistent with the clustered record. The fix is PR 44566, `executor: set handle changed when col gets auto-updated`.

The relevant trigger is a mutable `TIMESTAMP` or `DATETIME` column with `ON UPDATE CURRENT_TIMESTAMP` that is part of a clustered primary key and participates in a secondary index. The duplicate-update list can omit that column while the automatic update still changes its value.

## Evidence boundary

The mechanism must be connected to the actual table definition, the duplicate-update statement, the release matrix, and the observed primary and secondary access paths. A generic query-cache explanation and an ordinary nonclustered-primary-key table explain neither the row-handle transition nor the consistency error.
