# Explicit Subtransactions; Transaction Management

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partV_server_programming/09_plpython_-_python_procedural_language.md`
- Source Title: `PL/Python — Python Procedural Language`
- Source Heading Path: `PL/Python - Python Procedural Language > Explicit Subtransactions; Transaction Management`
- Source Line Ranges: `816-889, 890-921`
- Chunk ID: `pg16_solution_0087_e0aaeafe4c`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `08f31034e3030b206630bd8cccf9912bdf5cfe78facd629894fc6a1350199abe`

## Retrieval Guidance

- Use When: Isolate a known failing PL/Python statement or manage transaction boundaries in supported PL/Python procedures.
- Retrieval Keywords: plpy.subtransaction, PL/Python subtransaction, commit, rollback, transaction management, recover from error
- Follow-up Guidance: Verify procedure/function context and side effects before applying transaction-control actions.
- Classification Note: These sections document subtransaction context managers and transaction controls used to contain or recover from a confirmed failing operation.

## Official Source Content

## Explicit Subtransactions

Recovering from errors caused by database access as described in
[plpython-trapping](#plpython-trapping) can lead to an undesirable
situation where some operations succeed before one of them fails,
and after recovering from that error the data is left in an
inconsistent state.  PL/Python offers a solution to this problem in
the form of explicit subtransactions.

### Subtransaction Context Managers

Consider a function that implements a transfer between two
accounts:

```
CREATE FUNCTION transfer_funds() RETURNS void AS $$
try:
plpy.execute("UPDATE accounts SET balance = balance - 100 WHERE account_name = 'joe'")
plpy.execute("UPDATE accounts SET balance = balance + 100 WHERE account_name = 'mary'")
except plpy.SPIError as e:
result = "error transferring funds: %s" % e.args
else:
result = "funds transferred correctly"
plan = plpy.prepare("INSERT INTO operations (result) VALUES ($1)", ["text"])
plpy.execute(plan, [result])
$$ LANGUAGE plpython3u;
```

If the second `UPDATE` statement results in an
exception being raised, this function will report the error, but
the result of the first `UPDATE` will
nevertheless be committed.  In other words, the funds will be
withdrawn from Joe's account, but will not be transferred to
Mary's account.

To avoid such issues, you can wrap your
`plpy.execute` calls in an explicit
subtransaction.  The `plpy` module provides a
helper object to manage explicit subtransactions that gets created
with the `plpy.subtransaction()` function.
Objects created by this function implement the
[
context manager interface](https://docs.python.org/library/stdtypes.html#context-manager-types).  Using explicit subtransactions
we can rewrite our function as:

```
CREATE FUNCTION transfer_funds2() RETURNS void AS $$
try:
with plpy.subtransaction():
plpy.execute("UPDATE accounts SET balance = balance - 100 WHERE account_name = 'joe'")
plpy.execute("UPDATE accounts SET balance = balance + 100 WHERE account_name = 'mary'")
except plpy.SPIError as e:
result = "error transferring funds: %s" % e.args
else:
result = "funds transferred correctly"
plan = plpy.prepare("INSERT INTO operations (result) VALUES ($1)", ["text"])
plpy.execute(plan, [result])
$$ LANGUAGE plpython3u;
```

Note that the use of `try`/`except` is still
required.  Otherwise the exception would propagate to the top of
the Python stack and would cause the whole function to abort with
a PostgreSQL error, so that the
`operations` table would not have any row
inserted into it.  The subtransaction context manager does not
trap errors, it only assures that all database operations executed
inside its scope will be atomically committed or rolled back.  A
rollback of the subtransaction block occurs on any kind of
exception exit, not only ones caused by errors originating from
database access.  A regular Python exception raised inside an
explicit subtransaction block would also cause the subtransaction
to be rolled back.

## Transaction Management

In a procedure called from the top level or an anonymous code block
(`DO` command) called from the top level it is possible to
control transactions.  To commit the current transaction, call
`plpy.commit()`.  To roll back the current transaction,
call `plpy.rollback()`.  (Note that it is not possible to
run the SQL commands `COMMIT` or
`ROLLBACK` via `plpy.execute` or
similar.  It has to be done using these functions.)  After a transaction is
ended, a new transaction is automatically started, so there is no separate
function for that.

Here is an example:

```
CREATE PROCEDURE transaction_test1()
LANGUAGE plpython3u
AS $$
for i in range(0, 10):
plpy.execute("INSERT INTO test1 (a) VALUES (%d)" % i)
if i % 2 == 0:
plpy.commit()
else:
plpy.rollback()
$$;

CALL transaction_test1();
```

Transactions cannot be ended when an explicit subtransaction is active.
