# Enable and disable placement rules

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/configure-placement-rules.md`
- Source Title: `Placement Rules`
- Source Heading Path: `Placement Rules > Configure rules | Placement Rules > Configure rules > Enable Placement Rules | Placement Rules > Configure rules > Disable Placement Rules`
- Source Line Ranges: `65-125`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tiup`, `tidb`
- Topic Tags: `placement-rules`, `enablement`, `disablement`, `pd-ctl`, `pd-configuration`, `replica-policy`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0026_4e08a3b841`
- Source ID: `tidb-docs-8.1:configure-placement-rules.md#configure-rules`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2219d57be303b6907b5f497e6edffa9f167ca0e43ff7e1fe5e27406ea6bd087b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/configure-placement-rules#configure-rules
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/configure-placement-rules.md

## Retrieval Guidance

- Use When: Use this content when you need the exact PD configuration or pd-ctl commands for enabling or disabling Placement Rules and the documented default rule behavior.
- Retrieval Keywords: Enable Placement Rules, Disable Placement Rules, pd-ctl config placement-rules enable, pd-ctl config placement-rules disable, [replication], enable-placement-rules = true, max-replicas, location-labels, isolation-level, default rule, group_id pd, id default, switch to the previous scheduling strategy
- Follow-up Guidance: The notes explain that after Placement Rules are enabled, multiple rules make max-replicas, location-labels, and isolation-level no longer take effect, while disabling reuses those original configurations and keeps configured rules in PD for later re-enablement.
- Classification Note: This is configuration content because it covers feature enablement and disablement through PD configuration and pd-ctl, plus the resulting default rule generation behavior.

## Official Source Content

## Configure rules

The operations in this section are based on [pd-ctl](https://docs.pingcap.com/tidb/stable/pd-control), and the commands involved in the operations also support calls via HTTP API.
### Enable Placement Rules

The Placement Rules feature is enabled by default in v5.0 and later versions of TiDB. To disable it, refer to [Disable Placement Rules](#disable-placement-rules). To enable this feature after it has been disabled, you can modify the PD configuration file as follows before initializing the cluster:

```toml
[replication]
enable-placement-rules = true
```

In this way, PD enables this feature after the cluster is successfully bootstrapped and generates corresponding rules according to the [`max-replicas`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#max-replicas), [`location-labels`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#location-labels), and [`isolation-level`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#isolation-level) configurations:

```json
{
  "group_id": "pd",
  "id": "default",
  "start_key": "",
  "end_key": "",
  "role": "voter",
  "count": 3,
  "location_labels": ["zone", "rack", "host"],
  "isolation_level": ""
}
```

For a bootstrapped cluster, you can also enable Placement Rules dynamically through pd-ctl:

```bash
pd-ctl config placement-rules enable
```

PD also generates default rules based on the `max-replicas`, `location-labels`, and `isolation-level` configurations.

> **Note:**
>
> - When Placement Rules are enabled and multiple rules exist, the previously configured `max-replicas`, `location-labels`, and `isolation-level` no longer take effect. To adjust the replica policy, use the interface related to Placement Rules.
> - When Placement Rules are enabled and only one default rule exists, TiDB will automatically update this default rule when `max-replicas`, `location-labels`, or `isolation-level` configurations are changed.
### Disable Placement Rules

You can use pd-ctl to disable the Placement Rules feature and switch to the previous scheduling strategy.

```bash
pd-ctl config placement-rules disable
```

> **Note:**
>
> After disabling Placement Rules, PD uses the original `max-replicas`, `location-labels`, and `isolation-level` configurations. The modification of rules (when Placement Rules is enabled) will not update these three configurations in real time. In addition, all the rules that have been configured remain in PD and will be used the next time you enable Placement Rules.
