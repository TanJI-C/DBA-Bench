# Prepare TiUP no-sudo user, SSH trust, and topology

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster-no-sudo-mode.md`
- Source Title: `Deploy and Maintain an Online TiDB Cluster Using TiUP No-sudo Mode`
- Source Heading Path: `Deploy and Maintain an Online TiDB Cluster Using TiUP No-sudo Mode | Deploy and Maintain an Online TiDB Cluster Using TiUP No-sudo Mode > Prepare the user and configure the SSH mutual trust | Deploy and Maintain an Online TiDB Cluster Using TiUP No-sudo Mode > Prepare the topology file`
- Source Line Ranges: `5-114`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `no-sudo`, `systemd-user`, `xdg_runtime_dir`, `linger`, `ssh`, `ssh-trust`, `topology`, `deploy-dir`, `data-dir`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0396_bbeb0fa7a0`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster-no-sudo-mode.md#deploy-and-maintain-an-online-tidb-cluster-using-tiup-no-sudo-mode`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dddaf292b8643f1f51550515baec3d3d6e32ff344c7a35702ce1795058102124`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-no-sudo-mode#deploy-and-maintain-an-online-tidb-cluster-using-tiup-no-sudo-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster-no-sudo-mode.md

## Retrieval Guidance

- Use When: Use this chunk when preparing a TiUP no-sudo deployment with a non-root user, SSH mutual trust, systemd user mode, and topology.yaml settings for deploy_dir and data_dir.
- Retrieval Keywords: TiUP no-sudo mode, systemd user mode, XDG_RUNTIME_DIR, loginctl enable-linger tidb, systemctl --user, user@.service, ssh-keygen, ssh-copy-id tidb@host, authorized_keys, tiup cluster template > topology.yaml, systemd_mode: "user", deploy_dir, data_dir, topology.yaml, tidb user
- Follow-up Guidance: It also shows that the global section of topology.yaml needs systemd_mode: "user" and paths accessible to the non-root tidb user.
- Classification Note: This is classified as configuration because the content defines required user setup, SSH trust, systemd user configuration, and topology file parameters for TiUP no-sudo mode.

## Official Source Content

# Deploy and Maintain an Online TiDB Cluster Using TiUP No-sudo Mode

This document describes how to use the TiUP no-sudo mode to deploy a cluster.

> **Note:**
>
> For CentOS, only CentOS 8 or later versions are supported.
## Prepare the user and configure the SSH mutual trust

1. Take the `tidb` user as an example. Log in to all the target machines and create a user named `tidb` using the `root` user with the following command. In no-sudo mode, configuring passwordless sudo for the `tidb` user is unnecessary, that is, you do not need to add the `tidb` user to the `sudoers` file.
   
    ```shell
    adduser tidb
    ```
   
2. Start the `systemd user` mode for the `tidb` user on each target machine. This step is required and do not skip it.

    1. Use the `tidb` user to set the `XDG_RUNTIME_DIR` environment variable.
   
        ```shell
        sudo -iu tidb  # Switch to the tidb user
        mkdir -p ~/.bashrc.d
        echo "export XDG_RUNTIME_DIR=/run/user/$(id -u)" > ~/.bashrc.d/systemd
        source ~/.bashrc.d/systemd
        ```
   
    2. Use the `root` user to start the user service.
   
        ```shell
        $ uid=$(id -u tidb) # Get the ID of the tidb user
        $ systemctl start user@${uid}.service
        $ systemctl status user@${uid}.service
        user@1000.service - User Manager for UID 1000
        Loaded: loaded (/usr/lib/systemd/system/user@.service; static; vendor preset>
        Active: active (running) since Mon 2024-01-29 03:30:51 EST; 1min 7s ago
        Main PID: 3328 (systemd)
        Status: "Startup finished in 420ms."
        Tasks: 6
        Memory: 6.1M
        CGroup: /user.slice/user-1000.slice/user@1000.service
                ├─dbus.service
                │ └─3442 /usr/bin/dbus-daemon --session --address=systemd: --nofork >
                ├─init.scope
                │ ├─3328 /usr/lib/systemd/systemd --user
                │ └─3335 (sd-pam)
                └─pulseaudio.service
                  └─3358 /usr/bin/pulseaudio --daemonize=no --log-target=journal
        ```
       
    3. Execute `systemctl --user`. If no errors occur, it indicates that the `systemd user` mode has started successfully.

3. Use the `root` user to execute the following command to enable lingering for the systemd user `tidb`.

    ```shell
    loginctl enable-linger tidb
    loginctl show-user -p Linger tidb # This should show: Linger=yes
    ```

    You can read the systemd documentation for reference, [Automatic start-up of systemd user instances](https://wiki.archlinux.org/title/Systemd/User#Automatic_start-up_of_systemd_user_instances).

4. Generate a key using `ssh-keygen` on the control machine:

    ```shell
    ssh-keygen
    ```

5. Copy the public key to the other machines in the cluster to establish SSH trust.

    - If you have set a password for the `tidb` user, you can use `ssh-copy-id` command to copy the public key to the target machine.

        ```shell
        ssh-copy-id tidb@host
        ```

        You need to replace `host` with the hostname of the target machine and run this command on each of the other machines in the cluster.

    - If you use a different method to copy the public key, make sure to check the permissions of the `/home/tidb/.ssh/authorized_keys` file after the copy.

        ```shell
        chown -R tidb:tidb /home/tidb/.ssh/authorized_keys
        chmod 600 /home/tidb/.ssh/authorized_keys
        ```
## Prepare the topology file

1. Execute the following command to generate the topology file.

    ```shell
    tiup cluster template > topology.yaml
    ```
   
2. Edit the topology file.

    Compared with the regular mode, when using TiUP in no-sudo mode, you need to add a line `systemd_mode: "user"` in the `global` module of the `topology.yaml` file. The `systemd_mode` parameter is used to set whether to use the `systemd user` mode. If this parameter is not set, the default value is `system`, meaning sudo permissions are required.

    Additionally, in no-sudo mode, because the non-root `tidb` user does not have permission to use the `/data` directory as `deploy_dir` or `data_dir`, you must select a path accessible to non-root users. The following example uses relative paths, and the actual paths used are `/home/tidb/data/tidb-deploy` and `/home/tidb/data/tidb-data`. The rest of the topology file remains the same as in the regular mode. Another option is to use the root user to create the directories and then use `chown` to change the ownership to `tidb:tidb`.

    ```yaml
    global:
      user: "tidb"
      systemd_mode: "user"
      ssh_port: 22
      deploy_dir: "data/tidb-deploy"
      data_dir: "data/tidb-data"
      arch: "amd64"
      ...
    ```
