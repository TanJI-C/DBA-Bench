# Trust Authentication

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/06_client_authentication.md`
- Source Title: `Client Authentication`
- Source Heading Path: `Client Authentication > Trust Authentication`
- Source Line Ranges: `823-859`
- Chunk ID: `pg16_configuration_0093_d807982a51`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b66551c362854d0766dd14d45e49d9f711104fb77b6c9a3555dd3b52f4c51954`

## Retrieval Guidance

- Use When: 评估是否可对本地连接使用 trust。
- Retrieval Keywords: trust authentication, unix_socket_permissions, unix_socket_group, localhost, multiuser machine
- Follow-up Guidance: 除单用户/受控本地环境外，避免对 TCP/IP 使用 trust。
- Classification Note: 定义 trust 无条件信任行为、适用边界和 socket 文件权限替代约束。

## Official Source Content

## Trust Authentication

When `trust` authentication is specified,
PostgreSQL assumes that anyone who can
connect to the server is authorized to access the database with
whatever database user name they specify (even superuser names).
Of course, restrictions made in the `database` and
`user` columns still apply.
This method should only be used when there is adequate
operating-system-level protection on connections to the server.

`trust` authentication is appropriate and very
convenient for local connections on a single-user workstation.  It
is usually *not* appropriate by itself on a multiuser
machine.  However, you might be able to use `trust` even
on a multiuser machine, if you restrict access to the server's
Unix-domain socket file using file-system permissions.  To do this, set the
`unix_socket_permissions` (and possibly
`unix_socket_group`) configuration parameters as
described in [runtime-config-connection](#runtime-config-connection).  Or you
could set the `unix_socket_directories`
configuration parameter to place the socket file in a suitably
restricted directory.

Setting file-system permissions only helps for Unix-socket connections.
Local TCP/IP connections are not restricted by file-system permissions.
Therefore, if you want to use file-system permissions for local security,
remove the `host ... 127.0.0.1 ...` line from
`pg_hba.conf`, or change it to a
non-`trust` authentication method.

`trust` authentication is only suitable for TCP/IP connections
if you trust every user on every machine that is allowed to connect
to the server by the `pg_hba.conf` lines that specify
`trust`.  It is seldom reasonable to use `trust`
for any TCP/IP connections other than those from localhost (127.0.0.1).
