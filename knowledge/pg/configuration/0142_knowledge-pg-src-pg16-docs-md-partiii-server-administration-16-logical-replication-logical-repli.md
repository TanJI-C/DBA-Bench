# Security

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/16_logical_replication.md`
- Source Title: `Logical Replication`
- Source Heading Path: `Logical Replication > Security`
- Source Line Ranges: `1418-1485`
- Chunk ID: `pg16_configuration_0142_070475f224`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8cc13a60765ddb4fb6f89f46503f289057cd9739932d3437fcbb879aa042b496`

## Retrieval Guidance

- Use When: 配置逻辑复制权限、诊断权限/RLS 冲突或评估订阅安全风险。
- Retrieval Keywords: logical replication security, REPLICATION attribute, pg_hba.conf, row_security=off, pg_create_subscription, run_as_owner
- Follow-up Guidance: 避免不可信 table owner 与 run_as_owner=true 组合。
- Classification Note: 解释复制连接角色权限、pg_hba、RLS、subscription owner 和 run_as_owner 风险。

## Official Source Content

## Security

The role used for the replication connection must have
the `REPLICATION` attribute (or be a superuser).  If the
role lacks `SUPERUSER` and `BYPASSRLS`,
publisher row security policies can execute.  If the role does not trust
all table owners, include `options=-crow_security=off` in
the connection string; if a table owner then adds a row security policy,
that setting will cause replication to halt rather than execute the policy.
Access for the role must be configured in `pg_hba.conf`
and it must have the `LOGIN` attribute.

In order to be able to copy the initial table data, the role used for the
replication connection must have the `SELECT` privilege on
a published table (or be a superuser).

To create a publication, the user must have the `CREATE`
privilege in the database.

To add tables to a publication, the user must have ownership rights on the
table. To add all tables in schema to a publication, the user must be a
superuser. To create a publication that publishes all tables or all tables in
schema automatically, the user must be a superuser.

There are currently no privileges on publications.  Any subscription (that
is able to connect) can access any publication.  Thus, if you intend to
hide some information from particular subscribers, such as by using row
filters or column lists, or by not adding the whole table to the
publication, be aware that other publications in the same database could
expose the same information.  Publication privileges might be added to
PostgreSQL in the future to allow for
finer-grained access control.

To create a subscription, the user must have the privileges of the
the `pg_create_subscription` role, as well as
`CREATE` privileges on the database.

The subscription apply process will, at a session level, run with the
privileges of the subscription owner. However, when performing an insert,
update, delete, or truncate operation on a particular table, it will switch
roles to the table owner and perform the operation with the table owner's
privileges. This means that the subscription owner needs to be able to
`SET ROLE` to each role that owns a replicated table.

If the subscription has been configured with
`run_as_owner = true`, then no user switching will
occur. Instead, all operations will be performed with the permissions
of the subscription owner. In this case, the subscription owner only
needs privileges to `SELECT`, `INSERT`,
`UPDATE`, and `DELETE` from the
target table, and does not need privileges to `SET ROLE`
to the table owner. However, this also means that any user who owns
a table into which replication is happening can execute arbitrary code with
the privileges of the subscription owner. For example, they could do this
by simply attaching a trigger to one of the tables which they own.
Because it is usually undesirable to allow one role to freely assume
the privileges of another, this option should be avoided unless user
security within the database is of no concern.

On the publisher, privileges are only checked once at the start of a
replication connection and are not re-checked as each change record is read.

On the subscriber, the subscription owner's privileges are re-checked for
each transaction when applied. If a worker is in the process of applying a
transaction when the ownership of the subscription is changed by a
concurrent transaction, the application of the current transaction will
continue under the old owner's privileges.
