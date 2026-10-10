# Lightning checkpoint identity and resume semantics

TiDB Lightning checkpoints are durable task state, not a generic progress marker. A
checkpoint is reusable only when the task identity, target object, source file set, source
content, target schema, import backend, checkpoint driver, and checkpoint storage namespace
still describe the same import. The checkpoint table list and its metadata are part of that
identity; a table existing in the checkpoint database does not prove that another task may
reuse it.

Before resuming, compare an immutable source manifest with the current files, including file
names, byte sizes, format, character set, header contract, row ranges, and content hashes.
Compare the target `SHOW CREATE TABLE` result and index signatures with the saved schema
identity. Inspect the checkpoint storage tables and columns through the configured checkpoint
driver, and bind any partial target rows to the same task identity. A partial target is not
automatically evidence that a fresh import should be started.

Resume the original task only after every identity comparison matches. A source, schema,
target, backend, checkpoint driver, or checkpoint namespace mismatch is a stop condition. Do
not destroy or recreate the checkpoint to make a mismatch disappear, switch the source or
target, or treat a process exit code as proof of successful import. `checkpointed`, admitted,
running, and terminal-success states have different meanings and must be observed separately.
