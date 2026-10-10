# OS platforms, build libraries, and Docker CPU architecture requirements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/hardware-and-software-requirements.md`
- Source Title: `Software and Hardware Recommendations`
- Source Heading Path: `Software and Hardware Recommendations | Software and Hardware Recommendations > OS and platform requirements | Software and Hardware Recommendations > OS and platform requirements > Libraries required for compiling and running TiDB | Software and Hardware Recommendations > OS and platform requirements > Docker image dependencies`
- Source Line Ranges: `5-144`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`
- Topic Tags: `operating-systems`, `cpu-architectures`, `support-matrix`, `build-dependencies`, `runtime-libraries`, `docker-images`, `instruction-sets`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0365_59cddc964a`
- Source ID: `tidb-docs-8.1:hardware-and-software-requirements.md#software-and-hardware-recommendations`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `46a6f440f02e53d350e016db0a43a133a773aea19224a2565619068403631621`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/hardware-and-software-requirements#software-and-hardware-recommendations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/hardware-and-software-requirements.md

## Retrieval Guidance

- Use When: Use this chunk when checking TiDB v8.1 LTS OS and CPU architecture support, required build and runtime libraries, or Docker image CPU architecture and instruction set requirements.
- Retrieval Keywords: v8.1 LTS, OS and platform requirements, enterprise-level production quality, Red Hat Enterprise Linux 8.4 or a later 8.x version, Amazon Linux 2, Amazon Linux 2023, Rocky Linux 9.1 or later, Kylin V10 SP1/SP2/SP3, UnionTech OS (UOS) V20, openEuler 22.03 LTS SP1/SP3, macOS 12 (Monterey) or later, Oracle Enterprise Linux 8 or a later, Ubuntu LTS 20.04 or later, CentOS Stream 8, Debian 10 (Buster) or later, Fedora 38 or later, openSUSE Leap later than v15.5, SUSE Linux Enterprise Server 15, x86_64, ARM 64, 32-bit operating system, Golang 1.21 or later, Rust nightly-2023-12-28 or later, GCC 7.x, LLVM 13.0 or later, glibc 2.28-151.el8, Docker image dependencies, x86-64-v2 instruction set, Starting from TiDB v6.6.0
- Follow-up Guidance: The source also notes CentOS 7 and Red Hat Enterprise Linux 7 support ends starting from the 8.4 DMR version and links to upstream lifecycle notices.
- Classification Note: This is reference content because it provides support matrices and exact dependency requirements for operating systems, CPU architectures, libraries, and Docker image instruction sets.

## Official Source Content

# Software and Hardware Recommendations

As an open-source distributed SQL database with high performance, TiDB can be deployed in the Intel architecture server, ARM architecture server, and major virtualization environments and runs well. TiDB supports most of the major hardware networks and Linux operating systems.
## OS and platform requirements

In v8.1 LTS, TiDB ensures multi-level quality standards for various combinations of operating systems and CPU architectures.

+ For the following combinations of operating systems and CPU architectures, TiDB **provides enterprise-level production quality**, and the product features have been comprehensively and systematically verified:

    <table>
    <thead>
      <tr>
        <th>Operating systems</th>
        <th>Supported CPU architectures</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Red Hat Enterprise Linux 8.4 or a later 8.x version</td>
        <td><ul><li>x86_64</li><li>ARM 64</li></ul></td>
      </tr>
      <tr>
        <td><ul><li>Red Hat Enterprise Linux 7.3 or a later 7.x version (TiDB ends support for it starting from 8.4 DMR)</li><li>CentOS 7.3 or a later 7.x version (TiDB ends support for it starting from 8.4 DMR)</li></ul></td>
        <td><ul><li>x86_64</li><li>ARM 64</li></ul></td>
      </tr>
      <tr>
        <td>Amazon Linux 2</td>
        <td><ul><li>x86_64</li><li>ARM 64</li></ul></td>
      </tr>
      <tr>
        <td>Amazon Linux 2023</td>
        <td><ul><li>x86_64</li><li>ARM 64</li></ul></td>
      </tr>
      <tr>
        <td>Rocky Linux 9.1 or later</td>
        <td><ul><li>x86_64</li><li>ARM 64</li></ul></td>
      </tr>
      <tr>
        <td>Kylin V10 SP1/SP2/SP3 (SP3 is supported starting from v7.5.5)</td>
        <td><ul><li>x86_64</li><li>ARM 64</li></ul></td>
      </tr>
      <tr>
        <td>UnionTech OS (UOS) V20</td>
        <td><ul><li>x86_64</li><li>ARM 64</li></ul></td>
      </tr>
      <tr>
        <td>openEuler 22.03 LTS SP1/SP3</td>
        <td><ul><li>x86_64</li><li>ARM 64</li></ul></td>
      </tr>
    </tbody>
    </table>

    > **Note:**
    >
    > - According to [CentOS Linux EOL](https://blog.centos.org/2023/04/end-dates-are-coming-for-centos-stream-8-and-centos-linux-7/), the upstream support for CentOS Linux 7 ends on June 30, 2024. TiDB ends the support for CentOS 7 starting from the 8.4 DMR version. It is recommended to use Rocky Linux 9.1 or a later version.
    > - According to [Red Hat Enterprise Linux Life Cycle](https://access.redhat.com/support/policy/updates/errata/#Life_Cycle_Dates), the maintenance support for Red Hat Enterprise Linux 7 ends on June 30, 2024. TiDB ends the support for Red Hat Enterprise Linux 7 starting from the 8.4 DMR version. It is recommended to use Rocky Linux 9.1 or a later version.

+ For the following combinations of operating systems and CPU architectures, you can compile, build, and deploy TiDB. In addition, you can also use the basic features of OLTP, OLAP, and the data tools. However, TiDB **does not guarantee enterprise-level production quality**:

    <table>
    <thead>
      <tr>
        <th>Operating systems</th>
        <th>Supported CPU architectures</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>macOS 12 (Monterey) or later</td>
        <td><ul><li>x86_64</li><li>ARM 64</li></ul></td>
      </tr>
      <tr>
        <td>Oracle Enterprise Linux 8 or a later</td>
        <td>x86_64</td>
      </tr>
      <tr>
        <td>Ubuntu LTS 20.04 or later</td>
        <td>x86_64</td>
      </tr>
      <tr>
        <td>CentOS Stream 8</td>
        <td><ul><li>x86_64</li><li>ARM 64</li></ul></td>
      </tr>
      <tr>
        <td>Debian 10 (Buster) or later</td>
        <td>x86_64</td>
      </tr>
      <tr>
        <td>Fedora 38 or later</td>
        <td>x86_64</td>
      </tr>
      <tr>
        <td>openSUSE Leap later than v15.5 (not including Tumbleweed)</td>
        <td>x86_64</td>
      </tr>
      <tr>
        <td>SUSE Linux Enterprise Server 15</td>
        <td>x86_64</td>
      </tr>
    </tbody>
    </table>

    > **Note:**
    >
    > - For Oracle Enterprise Linux, TiDB supports the Red Hat Compatible Kernel (RHCK) and does not support the Unbreakable Enterprise Kernel provided by Oracle Enterprise Linux.
    > - Support for Ubuntu 16.04 will be removed in future versions of TiDB. Upgrading to Ubuntu 18.04 or later is strongly recommended.
    > - CentOS Stream 8 reaches [End of Builds](https://blog.centos.org/2023/04/end-dates-are-coming-for-centos-stream-8-and-centos-linux-7/) on May 31, 2024.

+ If you are using the 32-bit version of an operating system listed in the preceding two tables, TiDB **is not guaranteed** to be compilable, buildable or deployable on the 32-bit operating system and the corresponding CPU architecture, or TiDB does not actively adapt to the 32-bit operating system.

+ Other operating system versions not mentioned above might work but are not officially supported.
### Libraries required for compiling and running TiDB

|  Libraries required for compiling and running TiDB |  Version   |
|   :---   |   :---   |
|   Golang  |  1.21 or later |
|   Rust    |   nightly-2023-12-28 or later  |
|  GCC      |   7.x      |
|  LLVM     |  13.0 or later  |

Library required for running TiDB: glibc (2.28-151.el8 version)
### Docker image dependencies

The following CPU architectures are supported:

- x86_64. Starting from TiDB v6.6.0, the [x86-64-v2 instruction set](https://developers.redhat.com/blog/2021/01/05/building-red-hat-enterprise-linux-9-for-the-x86-64-v2-microarchitecture-level) is required.
- ARM 64
