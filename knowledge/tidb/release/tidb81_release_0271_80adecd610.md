# New SQL and security features

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.4.0.md`
- Source Title: `TiDB 5.4 Release Notes`
- Source Heading Path: `TiDB 5.4 Release Notes > New features | TiDB 5.4 Release Notes > New features > SQL | TiDB 5.4 Release Notes > New features > Security`
- Source Line Ranges: `143-170`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tiup`, `ecosystem`
- Topic Tags: `new-features`, `sql`, `gbk`, `character-set`, `collation`, `security`, `authentication`, `authorization`, `initial-password`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0271_80adecd610`
- Source ID: `tidb-docs-8.1:releases/release-5.4.0.md#new-features`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `143bc25118b7a91b386a73055ed0ce9435d911e7561134c39719d095c4fd2ac8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.4.0#new-features
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks what new SQL or security features were introduced in TiDB 5.4.0, especially GBK character set support, TiSpark authentication and authorization, or TiUP initial root password generation.
- Retrieval Keywords: TiDB 5.4 new features SQL security, GBK character set, new_collations_enabled_on_first_bootstrap, gbk_bin, gbk_chinese_ci, Character Set and Collation - GBK, TiSpark user authentication and authorization, database user authentication, read/write authorization at database or table level, TiSpark 2.5.0, TiUP initial password for root user, --init parameter, start a cluster, production deployment using TiUP
- Follow-up Guidance: The chunk links to the GBK character set documentation, the TiSpark security user document, and the TiUP production deployment step for starting a cluster.
- Classification Note: This is a release-note new-features section because the content announces newly supported SQL and security capabilities and names the related options and commands.

## Official Source Content

## New features
### SQL

- **TiDB supports the GBK character set since v5.4.0**

    Before v5.4.0, TiDB supports `ascii`, `binary`, `latin1`, `utf8`, and `utf8mb4` character sets.

    To better support Chinese users, TiDB supports the GBK character set since v5.4.0. After enabling the [`new_collations_enabled_on_first_bootstrap`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#new_collations_enabled_on_first_bootstrap) option in the TiDB configuration file when initializing a TiDB cluster for the first time, the TiDB GBK character set supports both `gbk_bin` and `gbk_chinese_ci` collations.

    When using the GBK character set, you need to pay attention to the compatibility restrictions. For details, see [Character Set and Collation - GBK](https://docs.pingcap.com/tidb/stable/character-set-gbk).
### Security

- **TiSpark supports user authentication and authorization**

    Since TiSpark 2.5.0, TiSpark supports both database user authentication and read/write authorization at a database or table level. After enabling this feature, you can prevent the business from running unauthorized batch tasks such as draws to obtain data, which improves the stability and data security of online clusters.

    This feature is disabled by default. When it is enabled, if a user operating through TiSpark does not have the needed permissions, the user gets an exception from TiSpark.

    [User document](https://docs.pingcap.com/tidb/stable/tispark-overview#security)

- **TiUP supports generating an initial password for the root user**

    An `--init` parameter is introduced to the command for starting a cluster. With this parameter, in a TiDB cluster deployed using TiUP, TiUP generates an initial strong password for the database root user. This avoids security risks in using a root user with an empty password and ensures the security of databases.

    [User document](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup#step-7-start-a-tidb-cluster)
