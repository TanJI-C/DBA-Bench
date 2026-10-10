# PD member management and leader commands

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-control.md`
- Source Title: `PD Control User Guide`
- Source Heading Path: `PD Control User Guide > Command > `member [delete | leader_priority | leader [show | resign | transfer <member_name>]]``
- Source Line Ranges: `442-476`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tiup`, `operator`, `shared`
- Topic Tags: `pd-ctl`, `members`, `leader`, `delete`, `transfer`, `resign`, `production-warning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0185_1bdb5ddd4d`
- Source ID: `tidb-docs-8.1:pd-control.md#member-delete-leader-priority-leader-show-resign-transfer-member-name`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c098c2144fbaf1cc3eea9502785042947b8b1971073efca0dcbf2b2a5d6dead1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-control#member-delete-leader-priority-leader-show-resign-transfer-member-name
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-control.md

## Retrieval Guidance

- Use When: Use this chunk when looking for pd-ctl member management commands to show PD members, inspect or change the PD leader, or understand the warning about `member delete`.
- Retrieval Keywords: member, member delete name, member delete id, member leader show, member leader resign, member leader transfer, leader_priority, PD members, etcd_leader, DO NOT use the member delete command in a production environment, remove PD nodes, scale in a TiDB/PD/TiKV cluster
- Follow-up Guidance: The source explicitly says not to use `member delete` to remove PD nodes in a production environment and points to scale-in documentation instead.
- Classification Note: This is classified as operation because the content covers operational pd-ctl member and leader commands, including viewing members, deleting a member, and resigning or transferring leadership.

## Official Source Content

### `member [delete | leader_priority | leader [show | resign | transfer <member_name>]]`

> **Note:**
>
> **DO NOT** use the `member delete` command to remove PD nodes in a production environment. To remove a PD node, see [Scale in a TiDB/PD/TiKV cluster](https://docs.pingcap.com/tidb/stable/scale-tidb-using-tiup#scale-in-a-tidbpdtikv-cluster) and [Manually Scale TiDB on Kubernetes](https://docs.pingcap.com/tidb-in-kubernetes/stable/scale-a-tidb-cluster/).

Use this command to view the PD members, remove a specified member, or configure the priority of leader.

Usage:

```bash
>> member                               // Display the information of all members
{
  "header": {......},
  "members": [......],
  "leader": {......},
  "etcd_leader": {......},
}
>> member delete name pd2               // Delete "pd2"
Success!
>> member delete id 1319539429105371180 // Delete a node using id
Success!
>> member leader show                   // Display the leader information
{
  "name": "pd",
  "member_id": 13155432540099656863,
  "peer_urls": [......],
  "client_urls": [......]
}
>> member leader resign // Move leader away from the current member
......
>> member leader transfer pd3 // Migrate leader to a specified member
......
```
