# example of preparing and applying a DM hotfix patch

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-component-dm-patch.md`
- Source Title: `Apply Hotfix to DM Clusters Online`
- Source Heading Path: `Apply Hotfix to DM Clusters Online > Example > Prepare the patch package and apply it to the DM cluster`
- Source Line Ranges: `103-204`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`
- Topic Tags: `example`, `hotfix`, `package-preparation`, `binary-replacement`, `cluster-status`, `node-selection`, `role-selection`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0510_7fe6c97b0c`
- Source ID: `tidb-docs-8.1:tiup/tiup-component-dm-patch.md#prepare-the-patch-package-and-apply-it-to-the-dm-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b96e0931e86733a1bfb6af0e402470e04bc5b25a4773e5462b319836ac085c91`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm-patch#prepare-the-patch-package-and-apply-it-to-the-dm-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-component-dm-patch.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants a concrete example of preparing DM hotfix tarballs, applying them to specific nodes or roles with `tiup dm patch`, and verifying the patched result with version output and `tiup dm display`.
- Retrieval Keywords: Prepare the patch package and apply it to the DM cluster, mkdir -p /tmp/package, /root/.tiup/storage/dm/packages/dm-master-v5.3.0-linux-amd64.tar.gz, /root/.tiup/storage/dm/packages/dm-worker-v5.3.0-linux-amd64.tar.gz, dm-master-hotfix-linux-amd64.tar.gz, dm-worker-hotfix-linux-amd64.tar.gz, tiup dm display dm-test, tiup dm patch dm-test dm-master-hotfix-linux-amd64.tar.gz -N 172.16.100.21:8261, tiup dm patch dm-test dm-worker-hotfix-linux-amd64.tar.gz -R dm-worker, intersection will be taken, dm-master (patched), dm-worker (patched), Release Version: v5.3.0-20211230
- Follow-up Guidance: After applying the hotfix, the content verifies the result by running `/home/tidb/dm/deploy/dm-master-8261/bin/dm-master/dm-master -V` and checking that `tiup dm display dm-test` shows roles such as `dm-master (patched)` and `dm-worker (patched)`.
- Classification Note: This is classified as an operation chunk because the official content provides a step-by-step hotfix application workflow, including package preparation, patch execution, node or role targeting, and result verification.

## Official Source Content

### Prepare the patch package and apply it to the DM cluster

1. Prepare the DM software package that matches the current version:

    ```shell
    mkdir -p /tmp/package
    tar -zxvf /root/.tiup/storage/dm/packages/dm-master-v5.3.0-linux-amd64.tar.gz -C /tmp/package/
    tar -zxvf /root/.tiup/storage/dm/packages/dm-worker-v5.3.0-linux-amd64.tar.gz -C /tmp/package/
    ```

2. Replace the binary file with the hotfix package:

    ```shell
    # Decompress the hotfix package and use it to replace the binary file.
    cd /root; tar -zxvf dm-linux-amd64.tar.gz
    cp /root/dm-linux-amd64/bin/dm-master /tmp/package/dm-master/dm-master
    cp /root/dm-linux-amd64/bin/dm-worker /tmp/package/dm-worker/dm-worker
    # Re-package the modified files.
    # Note that the packaging method might be different for other deployment methods.
    cd /tmp/package/ && tar -czvf dm-master-hotfix-linux-amd64.tar.gz dm-master/
    cd /tmp/package/ && tar -czvf dm-worker-hotfix-linux-amd64.tar.gz dm-worker/
    ```

3. Apply the hotfix:

    Query the cluster status. The following uses the cluster named `dm-test` as an example:

    ```shell
    tiup dm display dm-test
    ```

    Output:

    ```
    Cluster type:       dm
    Cluster name:       dm-test
    Cluster version:    v5.3.0
    Deploy user:        tidb
    SSH type:           builtin
    ID                  Role                 Host           Ports      OS/Arch       Status     Data Dir                              Deploy Dir
    --                  ----                 ----           -----      -------       ------     --------                              ----------
    172.16.100.21:9093  alertmanager         172.16.100.21  9093/9094  linux/x86_64  Up         /home/tidb/dm/data/alertmanager-9093  /home/tidb/dm/deploy/alertmanager-9093
    172.16.100.21:8261  dm-master            172.16.100.21  8261/8291  linux/x86_64  Healthy|L  /home/tidb/dm/data/dm-master-8261     /home/tidb/dm/deploy/dm-master-8261
    172.16.100.21:8262  dm-worker            172.16.100.21  8262       linux/x86_64  Free       /home/tidb/dm/data/dm-worker-8262     /home/tidb/dm/deploy/dm-worker-8262
    172.16.100.21:3000  grafana              172.16.100.21  3000       linux/x86_64  Up         -                                     /home/tidb/dm/deploy/grafana-3000
    172.16.100.21:9090  prometheus           172.16.100.21  9090       linux/x86_64  Up         /home/tidb/dm/data/prometheus-9090    /home/tidb/dm/deploy/prometheus-9090
    Total nodes: 5
    ```

    Apply the hotfix to the specified node or specified role. If both `-R` and `-N` are specified, the intersection will be taken.

    ```
    # Apply hotfix to a specified node.
    tiup dm patch dm-test dm-master-hotfix-linux-amd64.tar.gz -N 172.16.100.21:8261
    tiup dm patch dm-test dm-worker-hotfix-linux-amd64.tar.gz -N 172.16.100.21:8262
    # Apply hotfix to a specified role.
    tiup dm patch dm-test dm-master-hotfix-linux-amd64.tar.gz -R dm-master
    tiup dm patch dm-test dm-worker-hotfix-linux-amd64.tar.gz -R dm-worker
    ```

4. Query the hotfix application result:

    ```shell
    /home/tidb/dm/deploy/dm-master-8261/bin/dm-master/dm-master -V
    ```

    Output:

    ```
    Release Version: v5.3.0-20211230
    Git Commit Hash: ca7070c45013c24d34bd9c1e936071253451d707
    Git Branch: heads/refs/tags/v5.3.0-20211230
    UTC Build Time: 2022-01-05 14:19:02
    Go Version: go version go1.16.4 linux/amd64
    ```

    The cluster information changes accordingly:

    ```shell
    tiup dm display dm-test
    ```

    Output:

    ```
    Starting component `dm`: /root/.tiup/components/dm/v1.8.1/tiup-dm display dm-test
    Cluster type:       dm
    Cluster name:       dm-test
    Cluster version:    v5.3.0
    Deploy user:        tidb
    SSH type:           builtin
    ID                  Role                 Host           Ports      OS/Arch       Status     Data Dir                              Deploy Dir
    --                  ----                 ----           -----      -------       ------     --------                              ----------
    172.16.100.21:9093  alertmanager         172.16.100.21  9093/9094  linux/x86_64  Up         /home/tidb/dm/data/alertmanager-9093  /home/tidb/dm/deploy/alertmanager-9093
    172.16.100.21:8261  dm-master (patched)  172.16.100.21  8261/8291  linux/x86_64  Healthy|L  /home/tidb/dm/data/dm-master-8261     /home/tidb/dm/deploy/dm-master-8261
    172.16.100.21:8262  dm-worker (patched)  172.16.100.21  8262       linux/x86_64  Free       /home/tidb/dm/data/dm-worker-8262     /home/tidb/dm/deploy/dm-worker-8262
    172.16.100.21:3000  grafana              172.16.100.21  3000       linux/x86_64  Up         -                                     /home/tidb/dm/deploy/grafana-3000
    172.16.100.21:9090  prometheus           172.16.100.21  9090       linux/x86_64  Up         /home/tidb/dm/data/prometheus-9090    /home/tidb/dm/deploy/prometheus-9090
    Total nodes: 5
    ```

[<< Back to the previous page - TiUP DM command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-dm#command-list)
