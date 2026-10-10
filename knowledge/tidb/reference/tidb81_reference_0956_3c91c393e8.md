# LDB administration and encryption metadata dumping

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-control.md`
- Source Title: `TiKV Control User Guide`
- Source Heading Path: `TiKV Control User Guide > Subcommands, some options and flags > Ldb Command | TiKV Control User Guide > Subcommands, some options and flags > Dump encryption metadata`
- Source Line Ranges: `529-616`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `shared`
- Topic Tags: `ldb`, `rocksdb`, `database-administration`, `data-access`, `encryption-metadata`, `master-key`, `kms`, `plaintext-keys`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0956_3c91c393e8`
- Source ID: `tidb-docs-8.1:tikv-control.md#ldb-command`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `27d9ad743dd2db23e132fa100728bbb2c9280af419e1fc1eabe2908010ad3fc6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-control#ldb-command
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-control.md

## Retrieval Guidance

- Use When: Use this content when searching for tikv-ctl ldb examples for RocksDB inspection or for dumping TiKV encryption metadata for files and data encryption keys.
- Retrieval Keywords: tikv-ctl ldb, dump, manifest_dump, --hex, --db, --path, --column_family, --try_load_options, encryption-meta dump-file, encryption-meta dump-key, conf.toml, storage.data-dir, security.encryption.master-key, kms, --ids, I consent, plaintext
- Follow-up Guidance: The content states that dump-key ignores security.encryption.previous-master-key and does not trigger master key rotation, and warns that the command exposes data encryption keys as plaintext.
- Classification Note: This is classified as reference because the official content provides command syntax, options, configuration examples, prompts, and output examples for ldb administration and encryption metadata dumping.

## Official Source Content

### Ldb Command

The `ldb` command line tool offers multiple data access and database administration commands. Some examples are listed below. For more information, refer to the help message displayed when running `tikv-ctl ldb` or check the documents from RocksDB.

Examples of data access sequence:

To dump an existing RocksDB in HEX:

```shell
tikv-ctl ldb --hex --db=/tmp/db dump
```

To dump the manifest of an existing RocksDB:

```shell
tikv-ctl ldb --hex manifest_dump --path=/tmp/db/MANIFEST-000001
```

You can specify the column family that your query is against using the `--column_family=<string>` command line.

`--try_load_options` loads the database options file to open the database. It is recommended to always keep this option on when the database is running. If you open the database with default options, the LSM-tree might be messed up, which cannot be recovered automatically.
### Dump encryption metadata

Use the `encryption-meta` subcommand to dump encryption metadata. The subcommand can dump two types of metadata: encryption info for data files, and the list of data encryption keys used.

To dump encryption info for data files, use the `encryption-meta dump-file` subcommand. You need to create a TiKV config file to specify `data-dir` for the TiKV deployment:

```
# conf.toml
[storage]
data-dir = "/path/to/tikv/data"
```

The `--path` option can be used to specify an absolute or relative path to the data file of interest. The command might give empty output if the data file is not encrypted. If `--path` is not provided, encryption info for all data files will be printed.

```shell
tikv-ctl --config=./conf.toml encryption-meta dump-file --path=/path/to/tikv/data/db/CURRENT
```

```
/path/to/tikv/data/db/CURRENT: key_id: 9291156302549018620 iv: E3C2FDBF63FC03BFC28F265D7E78283F method: Aes128Ctr
```

To dump data encryption keys, use the `encryption-meta dump-key` subcommand. In additional to `data-dir`, you also need to specify the current master key used in the config file. For how to config master key, refer to [Encryption-At-Rest](https://docs.pingcap.com/tidb/stable/encryption-at-rest). Also with this command, the `security.encryption.previous-master-key` config will be ignored, and the master key rotation will not be triggered.

```
# conf.toml
[storage]
data-dir = "/path/to/tikv/data"

[security.encryption.master-key]
type = "kms"
key-id = "0987dcba-09fe-87dc-65ba-ab0987654321"
region = "us-west-2"
```

Note if the master key is a AWS KMS key, `tikv-ctl` needs to have access to the KMS key. Access to a AWS KMS key can be granted to `tikv-ctl` via environment variable, AWS default config file, or IAM role, whichever is suitable. Refer to AWS document for usage.

The `--ids` option can be used to specified a list of comma-separated data encryption key ids to print. If `--ids` is not provided, all data encryption keys will be printed, along with current key id, which is the id of the latest active data encryption key.

When using the command, you will see a prompt warning that the action will expose sensitive information. Type "I consent" to continue.

```shell
tikv-ctl --config=./conf.toml encryption-meta dump-key
```

```
This action will expose encryption key(s) as plaintext. Do not output the result in file on disk.
Type "I consent" to continue, anything else to exit: I consent
current key id: 9291156302549018620
9291156302549018620: key: 8B6B6B8F83D36BE2467ED55D72AE808B method: Aes128Ctr creation_time: 1592938357
```

```shell
tikv-ctl --config=./conf.toml encryption-meta dump-key --ids=9291156302549018620
```

```
This action will expose encryption key(s) as plaintext. Do not output the result in file on disk.
Type "I consent" to continue, anything else to exit: I consent
9291156302549018620: key: 8B6B6B8F83D36BE2467ED55D72AE808B method: Aes128Ctr creation_time: 1592938357
```

> **Note:**
>
> The command will expose data encryption keys as plaintext. In production, DO NOT redirect the output to a file. Even deleting the output file afterward may not cleanly wipe out the content from disk.
