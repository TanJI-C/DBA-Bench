# Disable or re-enable TiDB Dashboard

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-ops-deploy.md`
- Source Title: `Deploy TiDB Dashboard`
- Source Heading Path: `Deploy TiDB Dashboard > Disable TiDB Dashboard | Deploy TiDB Dashboard > Re-enable TiDB Dashboard | Deploy TiDB Dashboard > What's next`
- Source Line Ranges: `95-145`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`, `tiup`
- Topic Tags: `disable`, `re-enable`, `tiup`, `pd-config`, `verification`, `data-loss-warning`, `follow-up`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0038_5b4799d9b4`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-ops-deploy.md#disable-tidb-dashboard`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3a191d03eadc33d9c686978e365044e50696b9005fa8a2c3357b743cb2ebaf91`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-deploy#disable-tidb-dashboard
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-ops-deploy.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiUP PD configuration commands and expected messages for disabling or re-enabling TiDB Dashboard in a running cluster deployed using TiUP.
- Retrieval Keywords: Disable TiDB Dashboard, Re-enable TiDB Dashboard, tiup ctl:v<CLUSTER_VERSION> pd, config set dashboard-address none, config set dashboard-address auto, Error: TiDB Dashboard is disabled, Dashboard is not started., tiup cluster display CLUSTER_NAME --dashboard, PD renegotiate an instance, running cluster deployed using TiUP
- Follow-up Guidance: The source points to Access TiDB Dashboard for login and UI access and Secure TiDB Dashboard for security hardening such as configuring a firewall.
- Classification Note: This is classified as an operation chunk because the content gives operational TiUP procedures to disable, re-enable, verify, and follow up on TiDB Dashboard availability.

## Official Source Content

## Disable TiDB Dashboard

For a running cluster deployed using TiUP, use the `tiup ctl:v<CLUSTER_VERSION> pd` command to disable TiDB Dashboard on all PD instances (replace `127.0.0.1:2379` with the IP and port of any PD instance):

```bash
tiup ctl:v<CLUSTER_VERSION> pd -u http://127.0.0.1:2379 config set dashboard-address none
```

After disabling TiDB Dashboard, checking which PD instance provides the TiDB Dashboard service will fail:

```
Error: TiDB Dashboard is disabled
```

Visiting the TiDB Dashboard address of any PD instance via the browser will also fail:

```
Dashboard is not started.
```
## Re-enable TiDB Dashboard

For a running cluster deployed using TiUP, use the `tiup ctl:v<CLUSTER_VERSION> pd` command to request PD to renegotiate an instance to run TiDB Dashboard (replace `127.0.0.1:2379` with the IP and port of any PD instance):

```bash
tiup ctl:v<CLUSTER_VERSION> pd -u http://127.0.0.1:2379 config set dashboard-address auto
```

After executing the command above, you can use the `tiup cluster display` command to view the TiDB Dashboard instance address automatically negotiated by PD (replace `CLUSTER_NAME` with the cluster name):

```bash
tiup cluster display CLUSTER_NAME --dashboard
```

You can also re-enable TiDB Dashboard by manually specifying the PD instance that serves TiDB Dashboard. See [Switch to another PD instance to serve TiDB Dashboard](#switch-to-another-pd-instance-to-serve-tidb-dashboard).

> **Warning:**
>
> If the newly enabled TiDB Dashboard instance is different with the previous instance that served the TiDB Dashboard, the local data stored in the previous TiDB Dashboard instance will be lost, including Key Visualize history and search history.
## What's next

- To learn how to access and log into the TiDB Dashboard UI, see [Access TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-access).

- To learn how to enhance the security of TiDB Dashboard, such as configuring a firewall, see [Secure TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-security).
