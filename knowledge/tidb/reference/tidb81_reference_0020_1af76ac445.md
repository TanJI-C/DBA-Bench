# HAProxy overview, features, and deployment prerequisites

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/haproxy-best-practices.md`
- Source Title: `Best Practices for Using HAProxy in TiDB`
- Source Heading Path: `Best Practices for Using HAProxy in TiDB | Best Practices for Using HAProxy in TiDB > HAProxy overview | Best Practices for Using HAProxy in TiDB > Basic features | Best Practices for Using HAProxy in TiDB > Before you begin | Best Practices for Using HAProxy in TiDB > Before you begin > Hardware requirements | Best Practices for Using HAProxy in TiDB > Before you begin > Software requirements | Best Practices for Using HAProxy in TiDB > Before you begin > Software requirements > Operating systems | Best Practices for Using HAProxy in TiDB > Before you begin > Software requirements > Dependencies`
- Source Line Ranges: `5-76`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`
- Topic Tags: `haproxy`, `load-balancing`, `high-availability`, `health-checks`, `sticky-sessions`, `ssl`, `monitoring`, `hardware-requirements`, `software-requirements`, `operating-systems`, `dependencies`, `installation-prerequisites`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0020_1af76ac445`
- Source ID: `tidb-docs-8.1:best-practices/haproxy-best-practices.md#best-practices-for-using-haproxy-in-tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1ac7b50de3a6ed6765b2afee66c73b4d7a76dc38a0c6b957cbb16dcc4f377f27`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/haproxy-best-practices#best-practices-for-using-haproxy-in-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/haproxy-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when you need an overview of HAProxy in TiDB, its basic features, supported operating systems, dependencies, hardware requirements, or the minimum HAProxy version and `mysql-check` `post-41` note.
- Retrieval Keywords: HAProxy overview, Best Practices for Using HAProxy in TiDB, floating virtual IP address, load balancing for TCP-based applications, High Availability, Load Balancing, Health Check, Sticky Session, SSL, Monitoring and Statistics, minimum version of HAProxy v1.5, mysql-check post-41, HAProxy v2.2 or newer, HAProxy 2.6, hardware requirements, 2 cores 3.5 GHz, 4 GB, 50 GB SATA, 10G Network Card, Sysbench oltp_read_write, maximum QPS about 50K, software requirements, Red Hat Enterprise Linux 7 or 8, CentOS 7 or 8, Oracle Enterprise Linux 7 or 8, Ubuntu LTS 18.04 or later, epel-release, gcc, systemd-devel, yum -y install epel-release gcc systemd-devel
- Follow-up Guidance: The source also provides the dependency installation command `yum -y install epel-release gcc systemd-devel`.
- Classification Note: This chunk is reference material because it summarizes HAProxy capabilities, prerequisites, operating systems, dependencies, and version notes rather than a step-by-step procedure.

## Official Source Content

# Best Practices for Using HAProxy in TiDB

This document describes best practices for configuration and usage of [HAProxy](https://github.com/haproxy/haproxy) in TiDB. HAProxy provides load balancing for TCP-based applications. From TiDB clients, you can manipulate data just by connecting to the floating virtual IP address provided by HAProxy, which helps to achieve load balance in the TiDB server layer.

![HAProxy Best Practices in TiDB](/media/haproxy.jpg)

> **Note:**
>
> The minimum version of HAProxy that works with all versions of TiDB is v1.5. Between v1.5 and v2.1, you need to set the `post-41` option in `mysql-check`. It is recommended to use HAProxy v2.2 or newer.
## HAProxy overview

HAProxy is free, open-source software written in C language that provides a high availability load balancer and proxy server for TCP and HTTP-based applications. Because of its fast and efficient use of CPU and memory, HAProxy is now widely used by many well-known websites such as GitHub, Bitbucket, Stack Overflow, Reddit, Tumblr, Twitter, Tuenti, and AWS (Amazon Web Services).

HAProxy is written in the year 2000 by Willy Tarreau, the core contributor to the Linux kernel, who is still responsible for the maintenance of the project and provides free software updates in the open-source community. In this guide, HAProxy [2.6](https://www.haproxy.com/blog/announcing-haproxy-2-6/) is used. It is recommended to use the latest stable version. See [the released version of HAProxy](http://www.haproxy.org/) for details.
## Basic features

- [High Availability](http://cbonte.github.io/haproxy-dconv/2.6/intro.html#3.3.4): HAProxy provides high availability with support for a graceful shutdown and a seamless switchover;
- [Load Balancing](http://cbonte.github.io/haproxy-dconv/2.6/configuration.html#4.2-balance): Two major proxy modes are supported: TCP, also known as layer 4, and HTTP, also known as layer 7. No less than 9 load balancing algorithms are supported, such as roundrobin, leastconn and random;
- [Health Check](http://cbonte.github.io/haproxy-dconv/2.6/configuration.html#5.2-check): HAProxy periodically checks the status of HTTP or TCP mode of the server;
- [Sticky Session](http://cbonte.github.io/haproxy-dconv/2.6/intro.html#3.3.6): HAProxy can stick a client to a specific server for the duration when the application does not support sticky sessions;
- [SSL](http://cbonte.github.io/haproxy-dconv/2.6/intro.html#3.3.2): HTTPS communication and resolution are supported;
- [Monitoring and Statistics](http://cbonte.github.io/haproxy-dconv/2.6/intro.html#3.3.3): Through the web page, you can monitor the service state and traffic flow in real time.
## Before you begin

Before you deploy HAProxy, make sure that you meet the hardware and software requirements.
### Hardware requirements

According to the [HAProxy documentation](https://www.haproxy.com/documentation/haproxy-enterprise/getting-started/installation/linux/), the minimum hardware configuration for HAProxy is shown in the following table. Under the Sysbench `oltp_read_write` workload, the maximum QPS for this configuration is about 50K. You can increase the server configuration according to your load balancing environment.

| Hardware resource      | Minimum specification |
| :--------------------- | :-------------------- |
| CPU                    | 2 cores, 3.5 GHz      |
| Memory                 | 4 GB                 |
| Storage                | 50 GB (SATA)          |
| Network Interface Card | 10G Network Card      |
### Software requirements

You can use the following operating systems and make sure the required dependencies are installed. If you use yum to install HAProxy, the dependencies are installed along with it and you do not need to separately install them again.
#### Operating systems

| Linux distribution       | Version         |
| :----------------------- | :----------- |
| Red Hat Enterprise Linux | 7 or 8   |
| CentOS                   | 7 or 8   |
| Oracle Enterprise Linux  | 7 or 8   |
| Ubuntu LTS               | 18.04 or later versions |

> **Note:**
>
> - For more information about other supported operating systems, see [HAProxy documentation](https://github.com/haproxy/haproxy/blob/master/INSTALL).
#### Dependencies

- epel-release
- gcc
- systemd-devel

To install the dependencies above, run the following command:

```bash
yum -y install epel-release gcc systemd-devel
```
