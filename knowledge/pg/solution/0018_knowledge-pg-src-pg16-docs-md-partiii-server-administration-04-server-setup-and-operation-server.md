# The PostgreSQL User Account

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/04_server_setup_and_operation.md`
- Source Title: `Server Setup and Operation`
- Source Heading Path: `Server Setup and Operation > The PostgreSQL User Account`
- Source Line Ranges: `16-35`
- Chunk ID: `pg16_solution_0018_5d12c30b1b`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b03db5376e188fe120b45eb7c02dbcbcbce0335f37b30e228fdad0d44a5c222a`

## Retrieval Guidance

- Use When: 初始化 PostgreSQL 主机账户和文件所有权。
- Retrieval Keywords: postgres user, useradd, adduser, server daemon account, not root, not nobody
- Follow-up Guidance: 确保数据目录由该用户拥有，二进制不由该用户拥有更安全。
- Classification Note: 说明为服务器守护进程创建专用 OS 用户并避免 root/nobody 的具体做法。

## Official Source Content

## The PostgreSQL User Account

As with any server daemon that is accessible to the outside world,
it is advisable to run PostgreSQL under a
separate user account. This user account should only own the data
that is managed by the server, and should not be shared with other
daemons. (For example, using the user `nobody` is a bad
idea.) In particular, it is advisable that this user account not own
the PostgreSQL executable files, to ensure
that a compromised server process could not modify those executables.

Pre-packaged versions of PostgreSQL will
typically create a suitable user account automatically during
package installation.

To add a Unix user account to your system, look for a command
`useradd` or `adduser`. The user
name postgres is often used, and is assumed
throughout this book, but you can use another name if you like.
