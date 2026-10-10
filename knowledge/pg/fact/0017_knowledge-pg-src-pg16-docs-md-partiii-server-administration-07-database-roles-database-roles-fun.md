# Function Security

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/07_database_roles.md`
- Source Title: `Database Roles`
- Source Heading Path: `Database Roles > Function Security`
- Source Line Ranges: `493-513`
- Chunk ID: `pg16_fact_0017_579b482256`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bc1aa4406fae18e7328463ddb2cff29e5d2a62edd5b4d72535d644c452507d0b`

## Retrieval Guidance

- Use When: 需要理解用户可定义代码对后端和其他用户的安全影响。
- Retrieval Keywords: function security, Trojan horse, search_path, untrusted languages, superuser, row-level security
- Follow-up Guidance: 严格控制谁能创建函数/触发器/策略，并移除不可信 schema 的 search_path。
- Classification Note: 解释函数、触发器、RLS 和 untrusted language 的安全风险与 search_path 注意。

## Official Source Content

## Function Security

Functions, triggers and row-level security policies allow users to insert
code into the backend server that other users might execute
unintentionally. Hence, these mechanisms permit users to "Trojan
horse" others with relative ease. The strongest protection is tight
control over who can define objects. Where that is infeasible, write
queries referring only to objects having trusted owners.  Remove
from `search_path` any schemas that permit untrusted users
to create objects.

Functions run inside the backend
server process with the operating system permissions of the
database server daemon.  If the programming language
used for the function allows unchecked memory accesses, it is
possible to change the server's internal data structures.
Hence, among many other things, such functions can circumvent any
system access controls.  Function languages that allow such access
are considered "untrusted", and
PostgreSQL allows only superusers to
create functions written in those languages.
