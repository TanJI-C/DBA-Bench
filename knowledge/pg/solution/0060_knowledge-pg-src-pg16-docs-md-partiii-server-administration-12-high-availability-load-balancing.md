# Failover

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/12_high_availability,_load_balancing,_and_replication.md`
- Source Title: `High Availability, Load Balancing, and Replication`
- Source Heading Path: `High Availability, Load Balancing, and Replication > Failover`
- Source Line Ranges: `918-977`
- Chunk ID: `pg16_solution_0060_457d30c710`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `54c09e22d75b219b5347dd7b3f1011725f3ad4306ed19de1cc4ca8791e06e9f3`

## Retrieval Guidance

- Use When: 确认 primary 故障后需要提升 standby 或故障后恢复集群正常形态。
- Retrieval Keywords: failover, pg_ctl promote, pg_promote, STONITH, pg_rewind, recreate standby
- Follow-up Guidance: 防止双主，promote 后使用 pg_rewind 或新 base backup 重建 standby。
- Classification Note: 说明 primary/standby 故障后的 promotion、STONITH 和重建 standby 操作。

## Official Source Content

## Failover

If the primary server fails then the standby server should begin
failover procedures.

If the standby server fails then no failover need take place. If the
standby server can be restarted, even some time later, then the recovery
process can also be restarted immediately, taking advantage of
restartable recovery. If the standby server cannot be restarted, then a
full new standby server instance should be created.

If the primary server fails and the standby server becomes the
new primary, and then the old primary restarts, you must have
a mechanism for informing the old primary that it is no longer the primary. This is
sometimes known as STONITH (Shoot The Other Node In The Head), which is
necessary to avoid situations where both systems think they are the
primary, which will lead to confusion and ultimately data loss.

Many failover systems use just two systems, the primary and the standby,
connected by some kind of heartbeat mechanism to continually verify the
connectivity between the two and the viability of the primary. It is
also possible to use a third system (called a witness server) to prevent
some cases of inappropriate failover, but the additional complexity
might not be worthwhile unless it is set up with sufficient care and
rigorous testing.

PostgreSQL does not provide the system
software required to identify a failure on the primary and notify
the standby database server.  Many such tools exist and are well
integrated with the operating system facilities required for
successful failover, such as IP address migration.

Once failover to the standby occurs, there is only a
single server in operation. This is known as a degenerate state.
The former standby is now the primary, but the former primary is down
and might stay down.  To return to normal operation, a standby server
must be recreated,
either on the former primary system when it comes up, or on a third,
possibly new, system. The [app-pgrewind](#app-pgrewind) utility can be
used to speed up this process on large clusters.
Once complete, the primary and standby can be
considered to have switched roles. Some people choose to use a third
server to provide backup for the new primary until the new standby
server is recreated,
though clearly this complicates the system configuration and
operational processes.

So, switching from primary to standby server can be fast but requires
some time to re-prepare the failover cluster. Regular switching from
primary to standby is useful, since it allows regular downtime on
each system for maintenance. This also serves as a test of the
failover mechanism to ensure that it will really work when you need it.
Written administration procedures are advised.

To trigger failover of a log-shipping standby server, run
`pg_ctl promote` or call `pg_promote()`.
If you're setting up reporting servers that are only used to offload
read-only queries from the primary, not for high availability purposes,
you don't need to promote.
