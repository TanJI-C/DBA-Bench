# CREATE TABLE syntax and table options

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-create-table.md`
- Source Title: `CREATE TABLE | TiDB SQL Statement Reference`
- Source Heading Path: `CREATE TABLE | CREATE TABLE > Synopsis`
- Source Line Ranges: `5-187`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `create-table`, `syntax`, `grammar`, `table-options`, `partitioning`, `auto-increment`, `auto-random`, `character-set`, `collation`, `region-splitting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0561_cbc0170893`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-create-table.md#create-table`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `20db1ddf7114ea9a00d031d31cc5c9d333aa771087c462ebadaa20e3a11de394`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table#create-table
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-create-table.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the CREATE TABLE grammar, supported table options, or exact identifiers for column, index, foreign key, partition, TTL, placement policy, and region-splitting syntax.
- Retrieval Keywords: CREATE TABLE, CreateTableStmt, ColumnOption, TableOption, PartitionOpt, DuplicateOpt, IfNotExists, AUTO_INCREMENT, AUTO_RANDOM, AUTO_ID_CACHE, AUTO_RANDOM_BASE, SHARD_ROW_ID_BITS, PRE_SPLIT_REGIONS, CHARACTER SET, COLLATE, COMMENT, TTL, PLACEMENT POLICY, FOREIGN KEY, REFERENCES, INDEX, BTREE, RTREE, HASH, split-table, _tidb_rowid
- Follow-up Guidance: The source also notes that the split-table configuration option is enabled by default and that TiDB creates a separate Region for each newly created table.
- Classification Note: This is reference content because it provides formal CREATE TABLE syntax plus a supported table_options list and notes about parsed but ignored options.

## Official Source Content

# CREATE TABLE

This statement creates a new table in the currently selected database. It behaves similarly to the `CREATE TABLE` statement in MySQL.
## Synopsis

```ebnf+diagram
CreateTableStmt ::=
    'CREATE' OptTemporary 'TABLE' IfNotExists TableName ( TableElementListOpt CreateTableOptionListOpt PartitionOpt DuplicateOpt AsOpt CreateTableSelectOpt | LikeTableWithOrWithoutParen ) OnCommitOpt

OptTemporary ::=
    ( 'TEMPORARY' | ('GLOBAL' 'TEMPORARY') )?

IfNotExists ::=
    ('IF' 'NOT' 'EXISTS')?

TableName ::=
    Identifier ('.' Identifier)?

TableElementListOpt ::=
    ( '(' TableElementList ')' )?

TableElementList ::=
    TableElement ( ',' TableElement )*

TableElement ::=
    ColumnDef
|   Constraint

ColumnDef ::=
    ColumnName ( Type | 'SERIAL' ) ColumnOptionListOpt

ColumnOptionListOpt ::=
    ColumnOption*

ColumnOptionList ::=
    ColumnOption*

ColumnOption ::=
    'NOT'? 'NULL'
|   'AUTO_INCREMENT'
|   PrimaryOpt 'KEY'
|   'UNIQUE' 'KEY'?
|   'DEFAULT' DefaultValueExpr
|   'SERIAL' 'DEFAULT' 'VALUE'
|   'ON' 'UPDATE' NowSymOptionFraction
|   'COMMENT' stringLit
|   ConstraintKeywordOpt 'CHECK' '(' Expression ')' EnforcedOrNotOrNotNullOpt
|   GeneratedAlways 'AS' '(' Expression ')' VirtualOrStored
|   ReferDef
|   'COLLATE' CollationName
|   'COLUMN_FORMAT' ColumnFormat
|   'STORAGE' StorageMedia
|   'AUTO_RANDOM' OptFieldLen

Constraint ::=
    IndexDef
|   ForeignKeyDef

IndexDef ::=
    ( 'INDEX' | 'KEY' ) IndexName? '(' KeyPartList ')' IndexOption?

KeyPartList ::=
    KeyPart ( ',' KeyPart )*

KeyPart ::=
    ColumnName ( '(' Length ')')? ( 'ASC' | 'DESC' )?
|   '(' Expression ')' ( 'ASC' | 'DESC' )?

IndexOption ::=
    'COMMENT' String
|   ( 'VISIBLE' | 'INVISIBLE' )
|   ('USING' | 'TYPE') ('BTREE' | 'RTREE' | 'HASH')

ForeignKeyDef
         ::= ( 'CONSTRAINT' Identifier )? 'FOREIGN' 'KEY'
             Identifier? '(' ColumnName ( ',' ColumnName )* ')'
             'REFERENCES' TableName '(' ColumnName ( ',' ColumnName )* ')'
             ( 'ON' 'DELETE' ReferenceOption )?
             ( 'ON' 'UPDATE' ReferenceOption )?

ReferenceOption
         ::= 'RESTRICT'
           | 'CASCADE'
           | 'SET' 'NULL'
           | 'SET' 'DEFAULT'
           | 'NO' 'ACTION'

CreateTableOptionListOpt ::=
    TableOptionList?

PartitionOpt ::=
    ( 'PARTITION' 'BY' PartitionMethod PartitionNumOpt SubPartitionOpt PartitionDefinitionListOpt )?

DuplicateOpt ::=
    ( 'IGNORE' | 'REPLACE' )?

TableOptionList ::=
    TableOption ( ','? TableOption )*

TableOption ::=
    PartDefOption
|   DefaultKwdOpt ( CharsetKw EqOpt CharsetName | 'COLLATE' EqOpt CollationName )
|   ( 'AUTO_INCREMENT' | 'AUTO_ID_CACHE' | 'AUTO_RANDOM_BASE' | 'AVG_ROW_LENGTH' | 'CHECKSUM' | 'TABLE_CHECKSUM' | 'KEY_BLOCK_SIZE' | 'DELAY_KEY_WRITE' | 'SHARD_ROW_ID_BITS' | 'PRE_SPLIT_REGIONS' ) EqOpt LengthNum
|   ( 'CONNECTION' | 'PASSWORD' | 'COMPRESSION' ) EqOpt stringLit
|   RowFormat
|   ( 'STATS_PERSISTENT' | 'PACK_KEYS' ) EqOpt StatsPersistentVal
|   ( 'STATS_AUTO_RECALC' | 'STATS_SAMPLE_PAGES' ) EqOpt ( LengthNum | 'DEFAULT' )
|   'STORAGE' ( 'MEMORY' | 'DISK' )
|   'SECONDARY_ENGINE' EqOpt ( 'NULL' | StringName )
|   'UNION' EqOpt '(' TableNameListOpt ')'
|   'ENCRYPTION' EqOpt EncryptionOpt
|    'TTL' EqOpt TimeColumnName '+' 'INTERVAL' Expression TimeUnit (TTLEnable EqOpt ( 'ON' | 'OFF' ))? (TTLJobInterval EqOpt stringLit)?
|   PlacementPolicyOption

OnCommitOpt ::=
    ('ON' 'COMMIT' 'DELETE' 'ROWS')?

PlacementPolicyOption ::=
    "PLACEMENT" "POLICY" EqOpt PolicyName
|   "PLACEMENT" "POLICY" (EqOpt | "SET") "DEFAULT"

DefaultValueExpr ::=
    NowSymOptionFractionParentheses
|   SignedLiteral
|   NextValueForSequenceParentheses
|   BuiltinFunction

BuiltinFunction ::=
    '(' BuiltinFunction ')'
|   identifier '(' ')'
|   identifier '(' ExpressionList ')'
|   "REPLACE" '(' ExpressionList ')'

NowSymOptionFractionParentheses ::=
    '(' NowSymOptionFractionParentheses ')'
|   NowSymOptionFraction

NowSymOptionFraction ::=
    NowSym
|   NowSymFunc '(' ')'
|   NowSymFunc '(' NUM ')'
|   CurdateSym '(' ')'
|   "CURRENT_DATE"

NextValueForSequenceParentheses ::=
    '(' NextValueForSequenceParentheses ')'
|   NextValueForSequence

NextValueForSequence ::=
    "NEXT" "VALUE" forKwd TableName
|   "NEXTVAL" '(' TableName ')'
```

The following *table_options* are supported. Other options such as `AVG_ROW_LENGTH`, `CHECKSUM`, `COMPRESSION`, `CONNECTION`, `DELAY_KEY_WRITE`, `ENGINE`, `KEY_BLOCK_SIZE`, `MAX_ROWS`, `MIN_ROWS`, `ROW_FORMAT` and `STATS_PERSISTENT` are parsed but ignored.

| Options | Description | Example |
| ---------- | ---------- | ------- |
| `AUTO_INCREMENT` | The initial value of the increment field | `AUTO_INCREMENT` = 5 |
| [`SHARD_ROW_ID_BITS`](https://docs.pingcap.com/tidb/stable/shard-row-id-bits)| To set the number of bits for the implicit `_tidb_rowid` shards |`SHARD_ROW_ID_BITS` = 4|
|`PRE_SPLIT_REGIONS`| To pre-split `2^(PRE_SPLIT_REGIONS)` Regions when creating a table |`PRE_SPLIT_REGIONS` = 4|
|`AUTO_ID_CACHE`| To set the auto ID cache size in a TiDB instance. By default, TiDB automatically changes this size according to allocation speed of auto ID |`AUTO_ID_CACHE` = 200 |
|`AUTO_RANDOM_BASE`| To set the initial incremental part value of auto_random. This option can be considered as a part of the internal interface. Users can ignore this parameter |`AUTO_RANDOM_BASE` = 0|
| `CHARACTER SET` | To specify the [character set](https://docs.pingcap.com/tidb/stable/character-set-and-collation) for the table | `CHARACTER SET` =  'utf8mb4' |
| `COMMENT` | The comment information | `COMMENT` = 'comment info' |

> **Note:**
>
> The `split-table` configuration option is enabled by default. When it is enabled, a separate Region is created for each newly created table. For details, see [TiDB configuration file](https://docs.pingcap.com/tidb/stable/tidb-configuration-file).

> **Note:**
>
> TiDB creates a separate Region for each newly created table.
