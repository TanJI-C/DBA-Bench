# enable/disable modes

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/client_applications/pg_checksums.md`
- Source Title: `pg checksums`
- Source Heading Path: `Part VI Reference > Client Applications > pg_checksums > enable/disable modes`
- Source Line Ranges: `1-105`
- Chunk ID: `pg16_configuration_0227_a9a5e25d7d`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `85bb6449b1b452e02450ee3f50c58fb2043bb2e0067b53c22c588b52db3dd9ee`

## Retrieval Guidance

- Use When: Use when changing cluster checksum policy after planning downtime and replication consistency.
- Retrieval Keywords: pg_checksums --enable, pg_checksums --disable, data checksum configuration, offline cluster
- Follow-up Guidance: Stop all related clusters consistently and recreate standbys if required by checksum-state changes.
- Classification Note: Enable/disable modes change the cluster data-checksum configuration while the server is cleanly shut down.

## Official Source Content

pg_checksums
1
Application

pg_checksums
enable, disable or check data checksums in a PostgreSQL database cluster

`pg_checksums`
`option`

`-D`
`--pgdata`

`datadir`

## Description

pg_checksums checks, enables or disables data
checksums in a PostgreSQL cluster.  The server
must be shut down cleanly before running
pg_checksums. When verifying checksums, the exit
status is zero if there are no checksum errors, and nonzero if at least one
checksum failure is detected. When enabling or disabling checksums, the
exit status is nonzero if the operation failed.

When verifying checksums, every file in the cluster is scanned. When
enabling checksums, each relation file block with a changed checksum is
rewritten in-place.
Disabling checksums only updates the file `pg_control`.

## Options

The following command-line options are available:

**`-D `directory``**
: Specifies the directory where the database cluster is stored.

**`-c`**
: Checks checksums. This is the default mode if nothing else is
specified.

**`-d`**
: Disables checksums.

**`-e`**
: Enables checksums.

**`-f `filenode``**
: Only validate checksums in the relation with filenode
`filenode`.

**`-N`**
: By default, `pg_checksums` will wait for all files
to be written safely to disk.  This option causes
`pg_checksums` to return without waiting, which is
faster, but means that a subsequent operating system crash can leave
the updated data directory corrupt.  Generally, this option is useful
for testing but should not be used on a production installation.
This option has no effect when using `--check`.

**`-P`**
: Enable progress reporting. Turning this on will deliver a progress
report while checking or enabling checksums.

**`-v`**
: Enable verbose output. Lists all checked files.

**`-V`**
: Print the pg_checksums version and exit.

**`-?`**
: Show help about pg_checksums command line
arguments, and exit.

## Environment

**`PGDATA`**
: Specifies the directory where the database cluster is
stored; can be overridden using the `-D` option.

**`PG_COLOR`**
: Specifies whether to use color in diagnostic messages. Possible values
are `always`, `auto` and
`never`.

## Notes

Enabling checksums in a large cluster can potentially take a long time.
During this operation, the cluster or other programs that write to the
data directory must not be started or else data loss may occur.

When using a replication setup with tools which perform direct copies
of relation file blocks (for example [app-pgrewind](#app-pgrewind)),
enabling or disabling checksums can lead to page corruptions in the
shape of incorrect checksums if the operation is not done consistently
across all nodes. When enabling or disabling checksums in a replication
setup, it is thus recommended to stop all the clusters before switching
them all consistently. Destroying all standbys, performing the operation
on the primary and finally recreating the standbys from scratch is also
safe.

If pg_checksums is aborted or killed while
enabling or disabling checksums, the cluster's data checksum configuration
remains unchanged, and pg_checksums can be
re-run to perform the same operation.
