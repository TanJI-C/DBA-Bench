# Reset the root password by starting TiDB with skip-grant-table

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/user-account-management.md`
- Source Title: `TiDB User Account Management`
- Source Heading Path: `TiDB User Account Management > Forget the `root` password`
- Source Line Ranges: `183-226`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `root-password`, `password-reset`, `skip-grant-table`, `process-control`, `configuration`, `authentication-recovery`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0069_2b701c9b0f`
- Source ID: `tidb-docs-8.1:user-account-management.md#forget-the-root-password`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `83bc00e45b89460056fea8fb41dceef9d733edf4effdcabb10efefe8e43700df`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/user-account-management#forget-the-root-password
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/user-account-management.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the documented procedure to recover access after forgetting the TiDB `root` password by starting TiDB with `skip-grant-table`.
- Retrieval Keywords: Forget the `root` password, skip-grant-table, [security], tidb.toml, ps aux | grep tidb-server, kill -9 <pid>, run_tidb.sh, mysql -h 127.0.0.1 -P 4000 -u root, root user of the operating system
- Follow-up Guidance: It states that when `skip-grant-table` is set before starting TiDB, only the operating system `root` user can start the TiDB process, and after changing the password you remove the added configuration and wait for tidb-server to start automatically.
- Classification Note: This is classified as recovery because the content is a password-reset procedure for regaining access to the `root` account.

## Official Source Content

## Forget the `root` password

1. Modify the configuration file:

    1. Log in to the machine where one of the tidb-server instances is located.
    2. Enter the `conf` directory under the TiDB node deployment directory, and find the `tidb.toml` configuration file.
    3. Add the configuration item `skip-grant-table` in the `security` section of the configuration file. If there is no `security` section, add the following two lines to the end of the tidb.toml configuration file:

        ```
        [security]
        skip-grant-table = true
        ```

2. Stop the tidb-server process:

    1. View the tidb-server process:

        ```bash
        ps aux | grep tidb-server
        ```

    2. Find the process ID (PID) corresponding to tidb-server and use the `kill` command to stop the process:

        ```bash
        kill -9 <pid>
        ```

3. Start TiDB using the modified configuration:

    > **Note:**
    >
    > If you set `skip-grant-table` before starting the TiDB process, a check on the operating system user will be initiated. Only the `root` user of the operating system can start the TiDB process.

    1. Enter the `scripts` directory under the TiDB node deployment directory.
    2. Switch to the `root` account of the operating system.
    3. Run the `run_tidb.sh` script in the directory in the foreground.
    4. Log in as `root` in a new terminal window and change the password.

        ```bash
        mysql -h 127.0.0.1 -P 4000 -u root
        ```

4. Stop running the `run_tidb.sh` script, remove the content added in the TiDB configuration file in step 1, and wait for tidb-server to start automatically.
