# upgrade procedure

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/pgupgrade.md`
- Source Title: `pgupgrade`
- Source Heading Path: `Part VI Reference > Applications > pg_upgrade > upgrade procedure`
- Source Line Ranges: `254-325`
- Chunk ID: `pg16_solution_0135_54be904c01`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `df888802e36a4450194c0c4c28138b32e88e9b312c50c0cfc527af4166fc5f2b`

## Retrieval Guidance

- Use When: Use when the confirmed task is upgrading a PostgreSQL cluster to a new major version.
- Retrieval Keywords: pg_upgrade, major version upgrade, link mode, clone mode, post-upgrade processing
- Follow-up Guidance: Take backups, run check mode, preserve logs, run post-upgrade statistics collection, and verify rollback plan.
- Classification Note: The main usage performs a major-version cluster upgrade without dump/restore; it is a planned operational migration action.

## Official Source Content

## Run pg_upgrade

Always run the pg_upgrade binary of the new server, not the old one.
pg_upgrade requires the specification of the old and new cluster's
data and executable (`bin`) directories. You can also specify
user and port values, and whether you want the data files linked or cloned
instead of the default copy behavior.

If you use link mode, the upgrade will be much faster (no file
copying) and use less disk space, but you will not be able to access
your old cluster
once you start the new cluster after the upgrade.  Link mode also
requires that the old and new cluster data directories be in the
same file system.  (Tablespaces and `pg_wal` can be on
different file systems.)
Clone mode provides the same speed and disk space advantages but
does not cause the old cluster to be unusable once the new cluster
is started.  Clone mode also requires that the old and new data
directories be in the same file system.  This mode is only available
on certain operating systems and file systems.

The `--jobs` option allows multiple CPU cores to be used
for copying/linking of files and to dump and restore database schemas
in parallel;  a good place to start is the maximum of the number of
CPU cores and tablespaces.  This option can dramatically reduce the
time to upgrade a multi-database server running on a multiprocessor
machine.

For Windows users, you must be logged into an administrative account, and
then start a shell as the `postgres` user and set the proper path:

```
RUNAS /USER:postgres "CMD.EXE"
SET PATH=%PATH%;C:\Program Files\PostgreSQL\\bin;
```

and then run pg_upgrade with quoted directories, e.g.:

```
pg_upgrade.exe
--old-datadir "C:/Program Files/PostgreSQL/12/data"
--new-datadir "C:/Program Files/PostgreSQL//data"
--old-bindir "C:/Program Files/PostgreSQL/12/bin"
--new-bindir "C:/Program Files/PostgreSQL//bin"
```

Once started, `pg_upgrade` will verify the two clusters are compatible
and then do the upgrade. You can use `pg_upgrade --check`
to perform only the checks, even if the old server is still
running. `pg_upgrade --check` will also outline any
manual adjustments you will need to make after the upgrade.  If you
are going to be using link or clone mode, you should use the option
`--link` or `--clone` with
`--check` to enable mode-specific checks.
`pg_upgrade` requires write permission in the current directory.

Obviously, no one should be accessing the clusters during the
upgrade.  pg_upgrade defaults to running servers
on port 50432 to avoid unintended client connections.
You can use the same port number for both clusters when doing an
upgrade because the old and new clusters will not be running at the
same time.  However, when checking an old running server, the old
and new port numbers must be different.

If an error occurs while restoring the database schema, `pg_upgrade` will
exit and you will have to revert to the old cluster as outlined in [pgupgrade-step-revert](#pgupgrade-step-revert)
below. To try `pg_upgrade` again, you will need to modify the old
cluster so the pg_upgrade schema restore succeeds. If the problem is a
`contrib` module, you might need to uninstall the `contrib` module from
the old cluster and install it in the new cluster after the upgrade,
assuming the module is not being used to store user data.
