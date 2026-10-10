# Manage placement rules and rule groups with pd-ctl

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/configure-placement-rules.md`
- Source Title: `Placement Rules`
- Source Heading Path: `Placement Rules > Configure rules > Set rules using pd-ctl | Placement Rules > Configure rules > Use pd-ctl to configure rule groups`
- Source Line Ranges: `126-249`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `shared`
- Topic Tags: `placement-rules`, `pd-ctl`, `rule-management`, `rule-groups`, `json`, `scheduling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0033_c4adc47e54`
- Source ID: `tidb-docs-8.1:configure-placement-rules.md#set-rules-using-pd-ctl`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5f23edd6fd3f96be8ff82a7dab26e46b4735d4ed005accde288fa44cdeb38ea7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/configure-placement-rules#set-rules-using-pd-ctl
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/configure-placement-rules.md

## Retrieval Guidance

- Use When: Use this content when you need pd-ctl commands to view, save, overwrite, delete, or manage placement rules and rule groups in PD.
- Retrieval Keywords: Set rules using pd-ctl, pd-ctl config placement-rules show, pd-ctl config placement-rules show --group=pd, pd-ctl config placement-rules show --group=pd --id=default, pd-ctl config placement-rules show --region=2, pd-ctl config placement-rules save --in=rules.json, GroupID + ID, rule-group show, pd-ctl config placement-rules rule-group show, pd-ctl config placement-rules rule-group set pd 100 true, pd-ctl config placement-rules rule-group delete pd, JSON-format rule
- Follow-up Guidance: The content notes that rule changes affect PD scheduling in real time and that deleting a rule is done by saving a rule with the same GroupID and ID while setting count to 0.
- Classification Note: This is operation content because it provides concrete pd-ctl procedures and JSON examples for inspecting and modifying placement rules and rule group settings.

## Official Source Content

### Set rules using pd-ctl

> **Note:**
>
> The change of rules affects the PD scheduling in real time. Improper rule setting might result in fewer replicas and affect the high availability of the system.

pd-ctl supports using the following methods to view rules in the system, and the output is a JSON-format rule or a rule list.

- To view the list of all rules:

    ```bash
    pd-ctl config placement-rules show
    ```

- To view the list of all rules in a PD Group:

    ```bash
    pd-ctl config placement-rules show --group=pd
    ```

- To view the rule of a specific ID in a Group:

    ```bash
    pd-ctl config placement-rules show --group=pd --id=default
    ```

- To view the rule list that matches a Region:

    ```bash
    pd-ctl config placement-rules show --region=2
    ```

    In the above example, `2` is the Region ID.

Adding rules and editing rules are similar. You need to write the corresponding rules into a file and then use the `save` command to save the rules to PD:

```bash
cat > rules.json <<EOF
[
    {
        "group_id": "pd",
        "id": "rule1",
        "role": "voter",
        "count": 3,
        "location_labels": ["zone", "rack", "host"]
    },
    {
        "group_id": "pd",
        "id": "rule2",
        "role": "voter",
        "count": 2,
        "location_labels": ["zone", "rack", "host"]
    }
]
EOF

» ./pd-ctl -u 127.0.0.1:2379 config placement-rules save --in=rules.json
Success!
```

The above operation writes `rule1` and `rule2` to PD. If a rule with the same `GroupID` + `ID` already exists in the system, this rule is overwritten.

To delete a rule, you only need to set the `count` of the rule to `0`, and the rule with the same `GroupID` + `ID` will be deleted. The following command deletes the `pd / rule2` rule:

```bash
cat > rules.json <<EOF
[
    {
        "group_id": "pd",
        "id": "rule2"
    }
]
EOF

» ./pd-ctl -u 127.0.0.1:2379 config placement-rules save --in=rules.json
Success!
```
### Use pd-ctl to configure rule groups

- To view the list of all rule groups:

    ```bash
    pd-ctl config placement-rules rule-group show
    ```

- To view the rule group of a specific ID:

    ```bash
    pd-ctl config placement-rules rule-group show pd
    ```

- To set the `index` and `override` attributes of the rule group:

    ```bash
    pd-ctl config placement-rules rule-group set pd 100 true
    ```

- To delete the configuration of a rule group (use the default group configuration if there is any rule in the group):

    ```bash
    pd-ctl config placement-rules rule-group delete pd
    ```
