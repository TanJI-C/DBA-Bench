# ADMIN statement synopsis grammar

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-admin.md`
- Source Title: `ADMIN | TiDB SQL Statement Reference`
- Source Heading Path: `ADMIN > Synopsis`
- Source Line Ranges: `151-201`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `admin`, `syntax`, `grammar`, `ebnf`, `statement-reference`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0518_dd2daa2aab`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-admin.md#synopsis`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `29033d4ca828bffe096d5f8e9faa06dea8593d10628b33b5ac8383b6c5840ba4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin#synopsis
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-admin.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the formal synopsis or grammar of the ADMIN SQL statement and its supported variants.
- Retrieval Keywords: Synopsis, AdminStmt ::=, ADMIN SHOW DDL JOBS, ADMIN SHOW JOB QUERIES, ADMIN SHOW SLOW, ADMIN SHOW BDR ROLE, ADMIN CHECK TABLE, ADMIN CHECK INDEX, ADMIN RECOVER INDEX, ADMIN CLEANUP INDEX, ADMIN CLEANUP TABLE LOCK, ADMIN CHECKSUM TABLE, ADMIN CANCEL DDL JOBS, ADMIN PAUSE DDL JOBS, ADMIN RESUME DDL JOBS, ADMIN RELOAD BINDINGS, ADMIN RELOAD STATS_EXTENDED, ADMIN RELOAD STATISTICS, ADMIN PLUGINS ENABLE, ADMIN PLUGINS DISABLE, ADMIN REPAIR TABLE, ADMIN FLUSH BINDINGS, ADMIN CAPTURE BINDINGS, ADMIN EVOLVE BINDINGS, ADMIN FLUSH SESSION PLAN_CACHE, ADMIN FLUSH INSTANCE PLAN_CACHE, ADMIN SET BDR ROLE PRIMARY, ADMIN SET BDR ROLE SECONDARY, ADMIN UNSET BDR ROLE, NumList, AdminStmtLimitOpt, TableNameList
- Follow-up Guidance: The source provides EBNF-style productions for AdminStmt, NumList, AdminStmtLimitOpt, and TableNameList.
- Classification Note: This is reference content because it presents the formal grammar for ADMIN statement syntax rather than task-oriented procedures.

## Official Source Content

## Synopsis

```ebnf+diagram
AdminStmt ::=
    'ADMIN' ( 
        'SHOW' ( 
            'DDL' ( 
                'JOBS' Int64Num? WhereClauseOptional 
                | 'JOB' 'QUERIES' (NumList | AdminStmtLimitOpt)
            )? 
            | TableName 'NEXT_ROW_ID' 
            | 'SLOW' AdminShowSlow 
            | 'BDR' 'ROLE'
        ) 
        | 'CHECK' ( 
            'TABLE' TableNameList 
            | 'INDEX' TableName Identifier ( HandleRange ( ',' HandleRange )* )? 
        ) 
        | 'RECOVER' 'INDEX' TableName Identifier 
        | 'CLEANUP' ( 
            'INDEX' TableName Identifier 
            | 'TABLE' 'LOCK' TableNameList ) 
        | 'CHECKSUM' 'TABLE' TableNameList | 'CANCEL' 'DDL' 'JOBS' NumList 
        | ( 'CANCEL' | 'PAUSE' | 'RESUME' ) 'DDL' 'JOBS' NumList
        | 'RELOAD' (
            'EXPR_PUSHDOWN_BLACKLIST' 
            | 'OPT_RULE_BLACKLIST' 
            | 'BINDINGS'
            | 'STATS_EXTENDED'
            | 'STATISTICS'
        ) 
        | 'PLUGINS' ( 'ENABLE' | 'DISABLE' ) PluginNameList 
        | 'REPAIR' 'TABLE' TableName CreateTableStmt 
        | ( 'FLUSH' | 'CAPTURE' | 'EVOLVE' ) 'BINDINGS'
        | 'FLUSH' ('SESSION' | 'INSTANCE') 'PLAN_CACHE'
        | 'SET' 'BDR' 'ROLE' ( 'PRIMARY' | 'SECONDARY' )
        | 'UNSET' 'BDR' 'ROLE'
    )

NumList ::=
    Int64Num ( ',' Int64Num )*

AdminStmtLimitOpt ::=
    'LIMIT' LengthNum
|    'LIMIT' LengthNum ',' LengthNum
|    'LIMIT' LengthNum 'OFFSET' LengthNum

TableNameList ::=
    TableName ( ',' TableName )*
```
