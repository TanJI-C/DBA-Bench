# Check and install NTP service for clock synchronization

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/check-before-deployment.md`
- Source Title: `TiDB Environment and System Configuration Check`
- Source Heading Path: `TiDB Environment and System Configuration Check > Check and install the NTP service`
- Source Line Ranges: `300-435`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tidb`, `tikv`
- Topic Tags: `time-synchronization`, `ntp`, `chrony`, `clock-sync`, `service-check`, `installation`, `systemd`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0027_280f10ffd6`
- Source ID: `tidb-docs-8.1:check-before-deployment.md#check-and-install-the-ntp-service`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `52503aff9bfaafbc9ba854e8fec1303f9dcba6444e64dcac5fb7803e634fee21`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/check-before-deployment#check-and-install-the-ntp-service
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/check-before-deployment.md

## Retrieval Guidance

- Use When: Use this chunk when checking or installing clock synchronization service before TiDB deployment, including verifying `ntpd.service` or `chronyd.service` status and NTP synchronization health.
- Retrieval Keywords: Check and install the NTP service, clock synchronization, Network Time Protocol, NTP, Chrony, ntpd.service, chronyd.service, sudo systemctl status ntpd.service, sudo systemctl status chronyd.service, ntpstat, chronyc tracking, synchronised to NTP server, unsynchronised, Unable to talk to NTP daemon. Is it running?, Leap status     : Normal, Leap status    : Not synchronised, 506 Cannot talk to daemon, chronyc makestep, ntpdate pool.ntp.org, sudo yum install ntp ntpdate, linear consistency, ACID model, pool.ntp.org
- Follow-up Guidance: The content also includes commands to trigger immediate synchronization with `ntpdate pool.ntp.org`, install `ntp` and `ntpdate` on CentOS 7, and use `chronyc makestep` when the time offset is too high.
- Classification Note: This is classified as a self-managed shared operation topic because it describes system-level NTP or Chrony checks and installation steps required across TiDB, PD, and TiKV nodes.

## Official Source Content

## Check and install the NTP service

TiDB is a distributed database system that requires clock synchronization between nodes to guarantee linear consistency of transactions in the ACID model.

At present, the common solution to clock synchronization is to use the Network Time Protocol (NTP) services. You can use the `pool.ntp.org` timing service on the Internet, or build your own NTP service in an offline environment.

To check whether the NTP service is installed and whether it synchronizes with the NTP server normally, take the following steps:

1. Run the following command. If it returns `running`, then the NTP service is running.

    ```bash
    sudo systemctl status ntpd.service
    ```

    ```
    ntpd.service - Network Time Service
    Loaded: loaded (/usr/lib/systemd/system/ntpd.service; disabled; vendor preset: disabled)
    Active: active (running) since 一 2017-12-18 13:13:19 CST; 3s ago
    ```

    - If it returns `Unit ntpd.service could not be found.`, then try the following command to see whether your system is configured to use `chronyd` instead of `ntpd` to perform clock synchronization with NTP:

        ```bash
        sudo systemctl status chronyd.service
        ```

        ```
        chronyd.service - NTP client/server
        Loaded: loaded (/usr/lib/systemd/system/chronyd.service; enabled; vendor preset: enabled)
        Active: active (running) since Mon 2021-04-05 09:55:29 EDT; 3 days ago
        ```

        If the result shows that neither `chronyd` nor `ntpd` is configured, it means that neither of them is installed in your system. You should first install `chronyd` or `ntpd` and ensure that it can be automatically started. By default, `ntpd` is used.

        If your system is configured to use `chronyd`, proceed to step 3.

2. Run the `ntpstat` command to check whether the NTP service synchronizes with the NTP server.

    > **Note:**
    >
    > For the Ubuntu system, you need to install the `ntpstat` package.

    ```bash
    ntpstat
    ```

    - If it returns `synchronised to NTP server` (synchronizing with the NTP server), then the synchronization process is normal.

        ```
        synchronised to NTP server (85.199.214.101) at stratum 2
        time correct to within 91 ms
        polling server every 1024 s
        ```

    - The following situation indicates the NTP service is not synchronizing normally:

        ```
        unsynchronised
        ```

    - The following situation indicates the NTP service is not running normally:

        ```
        Unable to talk to NTP daemon. Is it running?
        ```

3. Run the `chronyc tracking` command to check whether the Chrony service synchronizes with the NTP server.

    > **Note:**
    >
    > This only applies to systems that use Chrony instead of NTPd.

    ```bash
    chronyc tracking
    ```

    - If the command returns `Leap status     : Normal`, the synchronization process is normal.

        ```
        Reference ID    : 5EC69F0A (ntp1.time.nl)
        Stratum         : 2
        Ref time (UTC)  : Thu May 20 15:19:08 2021
        System time     : 0.000022151 seconds slow of NTP time
        Last offset     : -0.000041040 seconds
        RMS offset      : 0.000053422 seconds
        Frequency       : 2.286 ppm slow
        Residual freq   : -0.000 ppm
        Skew            : 0.012 ppm
        Root delay      : 0.012706812 seconds
        Root dispersion : 0.000430042 seconds
        Update interval : 1029.8 seconds
        Leap status     : Normal
        ```

    - If the command returns the following result, an error occurs in the synchronization:

        ```
        Leap status    : Not synchronised
        ```

    - If the command returns the following result, the `chronyd` service is not running normally:

        ```
        506 Cannot talk to daemon
        ```

    - If the offset appears to be too high, you can run the `chronyc makestep` command to immediately correct the time offset. Otherwise, `chronyd` will gradually correct the time offset.

To make the NTP service start synchronizing as soon as possible, run the following command. Replace `pool.ntp.org` with your NTP server.

```bash
sudo systemctl stop ntpd.service && \
sudo ntpdate pool.ntp.org && \
sudo systemctl start ntpd.service
```

To install the NTP service manually on the CentOS 7 system, run the following command:

```bash
sudo yum install ntp ntpdate && \
sudo systemctl start ntpd.service && \
sudo systemctl enable ntpd.service
```
