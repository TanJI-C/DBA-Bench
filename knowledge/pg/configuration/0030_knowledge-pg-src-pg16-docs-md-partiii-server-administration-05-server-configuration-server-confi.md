# data_directory, config_file, hba_file, ident_file, external_pid_file

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/05_server_configuration.md`
- Source Title: `Server Configuration`
- Source Heading Path: `Server Configuration > File Locations > data_directory, config_file, hba_file, ident_file, external_pid_file`
- Source Line Ranges: `360-428`
- Chunk ID: `pg16_configuration_0030_f1cc6c3ab3`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1cb3775abb36fd832e8b8552ad9a1834c6acfca4d28bd706cf825d44f6594f9f`

## Retrieval Guidance

- Use When: 需要将配置文件和数据目录分离，或指定 HBA/ident/PID 文件位置。
- Retrieval Keywords: data_directory, config_file, hba_file, ident_file, external_pid_file, PGDATA, -D
- Follow-up Guidance: 相对路径按 postgres 启动目录解释；config_file 只能命令行设置。
- Classification Note: 定义数据目录、主配置、HBA、ident map 和额外 PID 文件位置参数。

## Official Source Content

## File Locations

In addition to the `postgresql.conf` file
already mentioned, PostgreSQL uses
two other manually-edited configuration files, which control
client authentication (their use is discussed in [client-authentication](#client-authentication)).  By default, all three
configuration files are stored in the database cluster's data
directory.  The parameters described in this section allow the
configuration files to be placed elsewhere.  (Doing so can ease
administration.  In particular it is often easier to ensure that
the configuration files are properly backed-up when they are
kept separate.)

**`data_directory` (`string`)**
: Specifies the directory to use for data storage.
This parameter can only be set at server start.

**`config_file` (`string`)**
: Specifies the main server configuration file
(customarily called `postgresql.conf`).
This parameter can only be set on the `postgres` command line.

**`hba_file` (`string`)**
: Specifies the configuration file for host-based authentication
(customarily called `pg_hba.conf`).
This parameter can only be set at server start.

**`ident_file` (`string`)**
: Specifies the configuration file for user name mapping
(customarily called `pg_ident.conf`).
This parameter can only be set at server start.
See also [auth-username-maps](#auth-username-maps).

**`external_pid_file` (`string`)**
: Specifies the name of an additional process-ID (PID) file that the
server should create for use by server administration programs.
This parameter can only be set at server start.

In a default installation, none of the above parameters are set
explicitly.  Instead, the
data directory is specified by the `-D` command-line
option or the `PGDATA` environment variable, and the
configuration files are all found within the data directory.

If you wish to keep the configuration files elsewhere than the
data directory, the `postgres` `-D`
command-line option or `PGDATA` environment variable
must point to the directory containing the configuration files,
and the `data_directory` parameter must be set in
`postgresql.conf` (or on the command line) to show
where the data directory is actually located.  Notice that
`data_directory` overrides `-D` and
`PGDATA` for the location
of the data directory, but not for the location of the configuration
files.

If you wish, you can specify the configuration file names and locations
individually using the parameters `config_file`,
`hba_file` and/or `ident_file`.
`config_file` can only be specified on the
`postgres` command line, but the others can be
set within the main configuration file.  If all three parameters plus
`data_directory` are explicitly set, then it is not necessary
to specify `-D` or `PGDATA`.

When setting any of these parameters, a relative path will be interpreted
with respect to the directory in which `postgres`
is started.
