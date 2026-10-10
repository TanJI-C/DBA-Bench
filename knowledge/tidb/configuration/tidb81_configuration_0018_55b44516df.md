# Firewall checks and port access configuration for TiDB nodes

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/check-before-deployment.md`
- Source Title: `TiDB Environment and System Configuration Check`
- Source Heading Path: `TiDB Environment and System Configuration Check > Check the firewall service of target machines | TiDB Environment and System Configuration Check > Check the firewall service of target machines > Stop and disable firewalld | TiDB Environment and System Configuration Check > Check the firewall service of target machines > Change the firewall zone | TiDB Environment and System Configuration Check > Check the firewall service of target machines > Configure the firewall`
- Source Line Ranges: `172-299`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `firewall`, `firewalld`, `network-access`, `ports`, `allowlist`, `security-zones`, `service-rules`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0018_55b44516df`
- Source ID: `tidb-docs-8.1:check-before-deployment.md#check-the-firewall-service-of-target-machines`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6dbbdbcc2035ad0dddc1119db5110d4fdcd09bddecfdf6ff40152d8bc3197727`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/check-before-deployment#check-the-firewall-service-of-target-machines
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/check-before-deployment.md

## Retrieval Guidance

- Use When: Use this chunk when checking or configuring firewall access on self-managed TiDB target machines so cluster node ports can communicate.
- Retrieval Keywords: firewalld, firewall-cmd, systemctl stop firewalld.service, systemctl disable firewalld.service, trusted zone, public zone, --set-default-zone trusted, --get-default-zone, --list-all, allowlist, port usage, TiDB 4000/tcp 10080/tcp, TiKV 20160/tcp 20180/tcp, PD 2379/tcp 2380/tcp, Prometheus 12020/tcp, Grafana, --permanent --new-service tidb, --permanent --new-service tikv, --permanent --new-service pd
- Follow-up Guidance: The content provides example `firewall-cmd` commands to stop or disable `firewalld`, switch the default zone to `trusted`, and define services and ports for TiDB, TiKV, PD, Prometheus, and Grafana.
- Classification Note: This is classified as configuration because the official content covers firewall service state, zone selection, and port rule definitions for TiDB cluster components.

## Official Source Content

## Check the firewall service of target machines

In TiDB clusters, the access ports between nodes must be open to ensure the transmission of information such as read and write requests and data heartbeats. In common online scenarios, the data interaction between the database and the application service and between the database nodes are all made within a secure network. Therefore, if there are no special security requirements, it is recommended to stop the firewall of the target machine. Otherwise, refer to [the port usage](https://docs.pingcap.com/tidb/stable/hardware-and-software-requirements#network-requirements) and add the needed port information to the allowlist of the firewall service.
### Stop and disable firewalld

This section describes how to stop and disable the firewall service of a target machine.

1. Check the firewall status. The following example uses CentOS Linux release 7.7.1908 (Core):

    ```shell
    sudo firewall-cmd --state
    sudo systemctl status firewalld.service
    ```

2. Stop the firewall service:

    ```bash
    sudo systemctl stop firewalld.service
    ```

3. Disable automatic startup of the firewall service:

    ```bash
    sudo systemctl disable firewalld.service
    ```

4. Check the firewall status:

    ```bash
    sudo systemctl status firewalld.service
    ```
### Change the firewall zone

Instead of disabling the firewall completely, you can use a less restrictive zone. The default `public` zone allows only specific services and ports, while the `trusted` zone allows all traffic by default.

To set the default zone to `trusted`:

```bash
firewall-cmd --set-default-zone trusted
```

To verify the default zone:

```bash
firewall-cmd --get-default-zone
# trusted
```

To list the policy for a zone:

```bash
firewall-cmd --zone=trusted --list-all
# trusted
#   target: ACCEPT
#   icmp-block-inversion: no
#   interfaces:
#   sources:
#   services:
#   ports:
#   protocols:
#   forward: yes
#   masquerade: no
#   forward-ports:
#   source-ports:
#   icmp-blocks:
#   rich rules:
```
### Configure the firewall

To configure the firewall for TiDB cluster components, use the following commands. These examples are for reference only. Adjust the zone names, ports, and services based on your specific environment.

Configure the firewall for the TiDB component:

```bash
firewall-cmd --permanent --new-service tidb
firewall-cmd --permanent --service tidb --set-description="TiDB Server"
firewall-cmd --permanent --service tidb --set-short="TiDB"
firewall-cmd --permanent --service tidb --add-port=4000/tcp
firewall-cmd --permanent --service tidb --add-port=10080/tcp
firewall-cmd --permanent --zone=public --add-service=tidb
```

Configure the firewall for the TiKV component:

```bash
firewall-cmd --permanent --new-service tikv
firewall-cmd --permanent --service tikv --set-description="TiKV Server"
firewall-cmd --permanent --service tikv --set-short="TiKV"
firewall-cmd --permanent --service tikv --add-port=20160/tcp
firewall-cmd --permanent --service tikv --add-port=20180/tcp
firewall-cmd --permanent --zone=public --add-service=tikv
```

Configure the firewall for the PD component:

```bash
firewall-cmd --permanent --new-service pd
firewall-cmd --permanent --service pd --set-description="PD Server"
firewall-cmd --permanent --service pd --set-short="PD"
firewall-cmd --permanent --service pd --add-port=2379/tcp
firewall-cmd --permanent --service pd --add-port=2380/tcp
firewall-cmd --permanent --zone=public --add-service=pd
```

Configure the firewall for Prometheus:

```bash
firewall-cmd --permanent --zone=public --add-service=prometheus
firewall-cmd --permanent --service=prometheus --add-port=12020/tcp
```

Configure the firewall for Grafana:

```bash
firewall-cmd --permanent --zone=public --add-service=grafana
```
