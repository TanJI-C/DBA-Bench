# Encryption Options

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/04_server_setup_and_operation.md`
- Source Title: `Server Setup and Operation`
- Source Heading Path: `Server Setup and Operation > Encryption Options`
- Source Line Ranges: `1470-1559`
- Chunk ID: `pg16_fact_0009_b74828e1d4`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9bdd25bb6e0ece4a94ab72d9fb446cf44b4ada84f6290d5cfc70e5f7f271095c`

## Retrieval Guidance

- Use When: 需要选择 PostgreSQL 数据保护层次或解释各加密方式覆盖面。
- Retrieval Keywords: password encryption, pgcrypto, disk encryption, SSL, GSSAPI encryption, SSH, client-side encryption
- Follow-up Guidance: 按威胁模型选择列级、传输层、磁盘或客户端加密。
- Classification Note: 概述密码哈希、列加密、存储/磁盘加密、网络加密、SSL 主机认证、客户端加密的保护范围。

## Official Source Content

## Encryption Options

PostgreSQL offers encryption at several
levels, and provides flexibility in protecting data from disclosure
due to database server theft, unscrupulous administrators, and
insecure networks. Encryption might also be required to secure
sensitive data such as medical records or financial transactions.

**Password Encryption**
: Database user passwords are stored as hashes (determined by the setting
[guc-password-encryption](#guc-password-encryption)), so the administrator cannot
determine the actual password assigned to the user. If SCRAM or MD5
encryption is used for client authentication, the unencrypted password is
never even temporarily present on the server because the client encrypts
it before being sent across the network. SCRAM is preferred, because it
is an Internet standard and is more secure than the PostgreSQL-specific
MD5 authentication protocol.

**Encryption For Specific Columns**
: The [pgcrypto](#pgcrypto) module allows certain fields to be
stored encrypted.
This is useful if only some of the data is sensitive.
The client supplies the decryption key and the data is decrypted
on the server and then sent to the client.

The decrypted data and the decryption key are present on the
server for a brief time while it is being decrypted and
communicated between the client and server. This presents a brief
moment where the data and keys can be intercepted by someone with
complete access to the database server, such as the system
administrator.

**Data Partition Encryption**
: Storage encryption can be performed at the file system level or the
block level.  Linux file system encryption options include eCryptfs
and EncFS, while FreeBSD uses PEFS.  Block level or full disk
encryption options include dm-crypt + LUKS on Linux and GEOM
modules geli and gbde on FreeBSD.  Many other operating systems
support this functionality, including Windows.

This mechanism prevents unencrypted data from being read from the
drives if the drives or the entire computer is stolen. This does
not protect against attacks while the file system is mounted,
because when mounted, the operating system provides an unencrypted
view of the data. However, to mount the file system, you need some
way for the encryption key to be passed to the operating system,
and sometimes the key is stored somewhere on the host that mounts
the disk.

**Encrypting Data Across A Network**
: SSL connections encrypt all data sent across the network: the
password, the queries, and the data returned. The
`pg_hba.conf` file allows administrators to specify
which hosts can use non-encrypted connections (`host`)
and which require SSL-encrypted connections
(`hostssl`). Also, clients can specify that they
connect to servers only via SSL.

GSSAPI-encrypted connections encrypt all data sent across the network,
including queries and data returned.  (No password is sent across the
network.)  The `pg_hba.conf` file allows
administrators to specify which hosts can use non-encrypted connections
(`host`) and which require GSSAPI-encrypted connections
(`hostgssenc`).  Also, clients can specify that they
connect to servers only on GSSAPI-encrypted connections
(`gssencmode=require`).

Stunnel or
SSH can also be used to encrypt
transmissions.

**SSL Host Authentication**
: It is possible for both the client and server to provide SSL
certificates to each other. It takes some extra configuration
on each side, but this provides stronger verification of identity
than the mere use of passwords. It prevents a computer from
pretending to be the server just long enough to read the password
sent by the client. It also helps prevent "man in the middle"
attacks where a computer between the client and server pretends to
be the server and reads and passes all data between the client and
server.

**Client-Side Encryption**
: If the system administrator for the server's machine cannot be trusted,
it is necessary
for the client to encrypt the data; this way, unencrypted data
never appears on the database server. Data is encrypted on the
client before being sent to the server, and database results have
to be decrypted on the client before being used.
