# pgbench

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/client_applications/pgbench.md`
- Source Title: `pgbench`
- Source Heading Path: `Part VI Reference > Client Applications > pgbench`
- Source Line Ranges: `587-619`
- Chunk ID: `pg16_guide_0100_f91f8802ac`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `22cd77339224ed76b7be38d1b6684059ba080d54212ed94249e380ffff51c855`

## Retrieval Guidance

- Use When: Use to reproduce/measure workload performance, connection overhead, contention, retries, or benchmark impact.
- Retrieval Keywords: pgbench, benchmark, TPS, latency, per-statement report, deadlock retries, serialization failures
- Follow-up Guidance: Use good-practice guidance: sufficient duration, scale factor, repeatability, and avoid pgbench becoming the bottleneck.
- Classification Note: Runs benchmark workloads and reports TPS, latency, failures, retries, per-statement latency, and logs; performance diagnostic signal.

## Official Source Content

### What Is the "Transaction" Actually Performed in pgbench?

pgbench executes test scripts chosen randomly
from a specified list.
The scripts may include built-in scripts specified with `-b`
and user-provided scripts specified with `-f`.
Each script may be given a relative weight specified after an
`@` so as to change its selection probability.
The default weight is `1`.
Scripts with a weight of `0` are ignored.

The default built-in transaction script (also invoked with `-b tpcb-like`)
issues seven commands per transaction over randomly chosen `aid`,
`tid`, `bid` and `delta`.
The scenario is inspired by the TPC-B benchmark, but is not actually TPC-B,
hence the name.

1. `BEGIN;`
2. `UPDATE pgbench_accounts SET abalance = abalance + :delta WHERE aid = :aid;`
3. `SELECT abalance FROM pgbench_accounts WHERE aid = :aid;`
4. `UPDATE pgbench_tellers SET tbalance = tbalance + :delta WHERE tid = :tid;`
5. `UPDATE pgbench_branches SET bbalance = bbalance + :delta WHERE bid = :bid;`
6. `INSERT INTO pgbench_history (tid, bid, aid, delta, mtime) VALUES (:tid, :bid, :aid, :delta, CURRENT_TIMESTAMP);`
7. `END;`

If you select the `simple-update` built-in (also `-N`),
steps 4 and 5 aren't included in the transaction.
This will avoid update contention on these tables, but
it makes the test case even less like TPC-B.

If you select the `select-only` built-in (also `-S`),
only the `SELECT` is issued.
