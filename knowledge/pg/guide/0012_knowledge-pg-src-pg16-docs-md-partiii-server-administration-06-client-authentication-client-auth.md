# Authentication Problems

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/06_client_authentication.md`
- Source Title: `Client Authentication`
- Source Heading Path: `Client Authentication > Authentication Problems`
- Source Line Ranges: `1581-1626`
- Chunk ID: `pg16_guide_0012_cff6ff18b6`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b42081a72e51d4cb800e35d6e680a559df5f0486a2b1a262e44396d451b9074e`

## Retrieval Guidance

- Use When: 客户端认证失败，需要根据错误消息判断 HBA、密码、用户或数据库问题。
- Retrieval Keywords: FATAL no pg_hba.conf entry, password authentication failed, user does not exist, database does not exist, server log authentication failure
- Follow-up Guidance: 客户端消息不足时查 server log 获取更详细原因。
- Classification Note: 列出 no pg_hba entry、password failed、user/database does not exist 等认证失败确认信号。

## Official Source Content

## Authentication Problems

Authentication failures and related problems generally
manifest themselves through error messages like the following:

```
FATAL:  no pg_hba.conf entry for host "123.123.123.123", user "andym", database "testdb"
```

This is what you are most likely to get if you succeed in contacting
the server, but it does not want to talk to you. As the message
suggests, the server refused the connection request because it found
no matching entry in its `pg_hba.conf`
configuration file.

```
FATAL:  password authentication failed for user "andym"
```

Messages like this indicate that you contacted the server, and it is
willing to talk to you, but not until you pass the authorization
method specified in the `pg_hba.conf` file. Check
the password you are providing, or check your Kerberos or ident
software if the complaint mentions one of those authentication
types.

```
FATAL:  user "andym" does not exist
```

The indicated database user name was not found.

```
FATAL:  database "testdb" does not exist
```

The database you are trying to connect to does not exist. Note that
if you do not specify a database name, it defaults to the database
user name.

> **Tip:**

> The server log might contain more information about an
> authentication failure than is reported to the client. If you are
> confused about the reason for a failure, check the server log.
>
