# Verify TiKV permissions for backup and restore directories

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/backup-and-restore-faq.md`
- Source Title: `Backup & Restore FAQs`
- Source Heading Path: `Backup & Restore FAQs > Data restore issues > What should I do to handle the `Permission denied` or `No such file or directory` error, even if I have tried to run `br` using root in vain?`
- Source Line Ranges: `167-247`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tikv`, `tiup`
- Topic Tags: `permissions`, `filesystem`, `nfs`, `local-storage`, `backup`, `restore`, `uid`, `directory-access`, `troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0140_4a54dba0c8`
- Source ID: `tidb-docs-8.1:faq/backup-and-restore-faq.md#what-should-i-do-to-handle-the-permission-denied-or-no-such-file-or-directory-error-even-if-i-have-tried-to-run-br-using-root-in-vain`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3effb381425a09d05d2e4194a880fafb85e59fff7a17f27554af7bd09f142577`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/backup-and-restore-faq#what-should-i-do-to-handle-the-permission-denied-or-no-such-file-or-directory-error-even-if-i-have-tried-to-run-br-using-root-in-vain
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/backup-and-restore-faq.md

## Retrieval Guidance

- Use When: You need permission checks for BR backup or restore directories when `Permission denied` or `No such file or directory` appears.
- Retrieval Keywords: Permission denied, No such file or directory, tikv-server, ps aux | grep tikv-server, tiup cluster list, UIDs must be consistent, write permission, read permission, backup directory, NFS, root
- Follow-up Guidance: The steps include checking the TiKV process user, cluster startup information, and the backup directory permissions before restore.
- Classification Note: This chunk is an operation-oriented FAQ about verifying TiKV access to backup and restore directories.

## Official Source Content

### What should I do to handle the `Permission denied` or `No such file or directory` error, even if I have tried to run `br` using root in vain?

You need to confirm whether TiKV has access to the backup directory. To back up data, confirm whether TiKV has the write permission. To restore data, confirm whether it has the read permission.

During the backup operation, if the storage medium is the local disk or a network file system (NFS), make sure that the user to start `br` and the user to start TiKV are consistent (if `br` and TiKV are on different machines, the users' UIDs must be consistent). Otherwise, the `Permission denied` issue might occur.

Running `br` as the `root` user might fail due to the disk permission, because the backup files (SST files) are saved by TiKV.

> **Note:**
>
> You might encounter the same problem during data restore. When the SST files are read for the first time, the read permission is verified. The execution duration of DDL suggests that there might be a long interval between checking the permission and running `br`. You might receive the error message `Permission denied` after waiting for a long time.

Therefore, it is recommended to check the permission before data restore according to the following steps:

1. Run the Linux command for process query:

    ```bash
    ps aux | grep tikv-server
    ```

    The output is as follows:

    ```shell
    tidb_ouo  9235 10.9  3.8 2019248 622776 ?      Ssl  08:28   1:12 bin/tikv-server --addr 0.0.0.0:20162 --advertise-addr 172.16.6.118:20162 --status-addr 0.0.0.0:20188 --advertise-status-addr 172.16.6.118:20188 --pd 172.16.6.118:2379 --data-dir /home/user1/tidb-data/tikv-20162 --config conf/tikv.toml --log-file /home/user1/tidb-deploy/tikv-20162/log/tikv.log
    tidb_ouo  9236  9.8  3.8 2048940 631136 ?      Ssl  08:28   1:05 bin/tikv-server --addr 0.0.0.0:20161 --advertise-addr 172.16.6.118:20161 --status-addr 0.0.0.0:20189 --advertise-status-addr 172.16.6.118:20189 --pd 172.16.6.118:2379 --data-dir /home/user1/tidb-data/tikv-20161 --config conf/tikv.toml --log-file /home/user1/tidb-deploy/tikv-20161/log/tikv.log
    ```

    Or you can run the following command:

    ```bash
    ps aux | grep tikv-server | awk '{print $1}'
    ```

    The output is as follows:

    ```shell
    tidb_ouo
    tidb_ouo
    ```

2. Query the startup information of the cluster using the `tiup` command:

    ```bash
    tiup cluster list
    ```

    The output is as follows:

    ```shell
    [root@Copy-of-VM-EE-CentOS76-v1 br]# tiup cluster list
    Starting component `cluster`: /root/.tiup/components/cluster/v1.5.2/tiup-cluster list
    Name          User      Version  Path                                               PrivateKey
    ----          ----      -------  ----                                               ----------
    tidb_cluster  tidb_ouo  v5.0.2   /root/.tiup/storage/cluster/clusters/tidb_cluster  /root/.tiup/storage/cluster/clusters/tidb_cluster/ssh/id_rsa
    ```

3. Check the permission for the backup directory. For example, `backup` is for backup data storage:

    ```bash
    ls -al backup
    ```

    The output is as follows:

    ```shell
    [root@Copy-of-VM-EE-CentOS76-v1 user1]# ls -al backup
    total 0
    drwxr-xr-x  2 root root   6 Jun 28 17:48 .
    drwxr-xr-x 11 root root 310 Jul  4 10:35 ..
    ```

    From the output of step 2, you can find that the `tikv-server` instance is started by the user `tidb_ouo`. But the user `tidb_ouo` does not have the write permission for `backup`. Therefore, the backup fails.
