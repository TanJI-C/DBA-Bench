# TiUP FAQ basics: mirrors, components, topology, conflict checks, and SSH deployment issue

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-faq.md`
- Source Title: `TiUP FAQs`
- Source Heading Path: `TiUP FAQs | TiUP FAQs > Can TiUP not use the official mirror source? | TiUP FAQs > How do I put my own component into the TiUP mirrors? | TiUP FAQs > What is the difference between the TiUP playground and TiUP cluster components? | TiUP FAQs > How do I write the topology file for the TiUP cluster component? | TiUP FAQs > Can multiple instances be deployed on the same host? | TiUP FAQs > Are port and directory conflicts detected within the same cluster? | TiUP FAQs > Are port and directory conflicts detected among different clusters? | TiUP FAQs > During cluster deployment, TiUP received an `ssh: handshake failed: read tcp 10.10.10.34:38980 -> 10.10.10.34:3600: read: connection reset by peer` error`
- Source Line Ranges: `5-62`
- Source Scope: `shared`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `faq`, `mirrors`, `offline-mirror`, `component-publishing`, `playground`, `cluster`, `topology`, `multi-instance`, `port-conflict`, `directory-conflict`, `deployment`, `scaling`, `ssh`, `sshd`, `concurrency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1041_d55b61217b`
- Source ID: `tidb-docs-8.1:tiup/tiup-faq.md#tiup-faqs`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8e3b7d53082f156879772620b077da79635666e891027e408b8602a8294e2fb6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-faq#tiup-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-faq.md

## Retrieval Guidance

- Use When: Use this chunk when answering TiUP FAQ questions about mirror configuration, offline mirrors, component publishing support, playground versus cluster, topology templates, same-host multi-instance deployment, port or directory conflict detection, or the SSH handshake failed deployment error.
- Retrieval Keywords: TIUP_MIRRORS, tiup mirror set https://tiup-mirrors.pingcap.com, offline mirror source, official mirror source, local directory, HTTP server address, tiup publish <comp> <version>, TiUP playground, TiUP cluster, topology file, Multi-DC deployment topology, Minimal deployment topology, Complete topology file, multiple instances on the same host, different ports and directories, port and directory conflicts, deployment and scaling, same TiUP control machine, different TiUP control machines, ssh: handshake failed: read tcp 10.10.10.34:38980 -> 10.10.10.34:3600: read: connection reset by peer, MaxSessions 1000, MaxStartups 1000, sshd_config, restart the sshd service
- Follow-up Guidance: The content points to topology templates at the TiUP cluster examples repository and notes changing `MaxSessions` and `MaxStartups` in `/etc/ssh/sshd_config` before restarting `sshd` for the SSH connection reset issue.
- Classification Note: This is a reference FAQ chunk because it lists documented TiUP behaviors, commands, configuration names, and error context for mirrors, topology, deployment conflicts, and SSH limits.

## Official Source Content

# TiUP FAQs

This document collects the frequently asked questions (FAQs) about TiUP.
## Can TiUP not use the official mirror source?

TiUP supports specifying the mirror source through the `TIUP_MIRRORS` environment variable. The address of the mirror source can be a local directory or an HTTP server address. If your environment cannot access the network, you can create your own offline mirror source to use TiUP.

After using an unofficial mirror, if you want the official mirror back and use it, take one of the following measures:

- Set the `TIUP_MIRRORS` variable to the official mirror address: `https://tiup-mirrors.pingcap.com`.
- Make sure that the `TIUP_MIRRORS` variable is not set, and then execute the `tiup mirror set https://tiup-mirrors.pingcap.com` command.
## How do I put my own component into the TiUP mirrors?

TiUP does not support third-party components for the time being, but the TiUP Team has developed the TiUP component development specifications and is developing the tiup-publish component. After everything is ready, a contributor can publish their own components to TiUP's official mirrors by using the `tiup publish <comp> <version>` command.
## What is the difference between the TiUP playground and TiUP cluster components?

The TiUP playground component is mainly used to build a stand-alone development environment on Linux or macOS operating systems. It helps you get started quickly and run a specified version of the TiUP cluster easily. The TiUP cluster component is mainly used to deploy and maintain a production environment cluster, which is usually a large-scale cluster. TiDB clusters deployed by TiUP Playground might lack some features and operational capabilities, and it is not recommended for complete functional and stability testing.
## How do I write the topology file for the TiUP cluster component?

Refer to [these templates](https://github.com/pingcap/tiup/tree/master/embed/examples/cluster) to write the topology file. The templates include:

- Multi-DC deployment topology
- Minimal deployment topology
- Complete topology file

You can edit your topology file based on the templates and your needs.
## Can multiple instances be deployed on the same host?

You can use the TiUP cluster component to deploy multiple instances on the same host, but with different ports and directories configured; otherwise, directory and port conflicts might occur.
## Are port and directory conflicts detected within the same cluster?

Port and directory conflicts in the same cluster are detected during deployment and scaling. If there is any directory or port conflict, the deployment or scaling process is interrupted.
## Are port and directory conflicts detected among different clusters?

If multiple different clusters are deployed by the same TiUP control machine, the port and directory conflicts among these clusters are detected during deployment and scaling. If the clusters are deployed by different TiUP control machines, conflict detection is not supported currently.
## During cluster deployment, TiUP received an `ssh: handshake failed: read tcp 10.10.10.34:38980 -> 10.10.10.34:3600: read: connection reset by peer` error

The error might occur because the default number of concurrent threads of TiUP exceeds the default maximum number of SSH connections. To solve the issue, you can increase the default number of SSH connections, and then restart the sshd service:

```shell
vi /etc/ssh/sshd_config
```

```bash
MaxSessions 1000
MaxStartups 1000
```
