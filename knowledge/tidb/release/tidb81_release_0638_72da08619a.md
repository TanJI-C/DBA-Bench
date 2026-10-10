# TiDB Cloud release notes for late June to late July 2023

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/release-notes-2023.md`
- Source Title: `TiDB Cloud Release Notes in 2023`
- Source Heading Path: `TiDB Cloud Release Notes in 2023 > July 25, 2023 | TiDB Cloud Release Notes in 2023 > July 18, 2023 | TiDB Cloud Release Notes in 2023 > July 11, 2023 | TiDB Cloud Release Notes in 2023 > July 4, 2023 | TiDB Cloud Release Notes in 2023 > June 27, 2023 | TiDB Cloud Release Notes in 2023 > June 20, 2023`
- Source Line Ranges: `305-406`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`, `tidb`
- Topic Tags: `release-notes`, `serverless`, `dedicated`, `console`, `rbac`, `cmek`, `import`, `branching`, `backup`, `pitr`, `dark-mode`, `support`, `version-upgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0638_72da08619a`
- Source ID: `tidb-docs-8.1:tidb-cloud/release-notes-2023.md#july-25-2023`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `efe22b0646241efb769ed1fd85155f9fbfd6d945474aecc60fc88d50b9c2e74b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/release-notes-2023#july-25-2023
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/release-notes-2023.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks about TiDB Cloud release changes from June 20 to July 25, 2023 for Serverless, Dedicated, or console features such as RBAC, CMEK, Import, branching, backup, PITR, Dark Mode, support access, or default TiDB version upgrades.
- Retrieval Keywords: July 25 2023, July 18 2023, July 11 2023, July 4 2023, June 27 2023, June 20 2023, TiDB Cloud release notes 2023, TiDB Cloud Serverless Generally Available, TiDB Bot beta, branching feature beta, TiDB Cloud Serverless branching, weekly backup, point-in-time recovery, PITR beta, Dark Mode, role-based access control, Organization Owner, Organization Billing Admin, Organization Console Audit Admin, Organization Member, Project Owner, Project Data Access Read-Write, Project Data Access Read-Only, Customer-Managed Encryption Key, CMEK, AWS KMS, Import feature, Amazon S3 import, CSV configuration, target table selection, source files mapping, Support entry, ? icon, default TiDB version, v6.5.2, v6.5.3, v7.1.1, sample dataset removed
- Follow-up Guidance: The release notes link to related documents for User roles, TiDB Cloud Support, branching, backup and restore, and Serverless PITR restore details.
- Classification Note: This chunk is classified as a cloud release note because it lists dated TiDB Cloud changes across Dedicated, Serverless, and console capabilities in late June and July 2023.

## Official Source Content

## July 25, 2023

**General changes**

- Upgrade the default TiDB version of new [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters from [v6.5.3](https://docs.pingcap.com/tidb/v6.5/release-6.5.3) to [v7.1.1](https://docs.pingcap.com/tidb/v7.1/release-7.1.1).

**Console changes**

- Simplify access to PingCAP Support for TiDB Cloud users by optimizing support entries. Improvements include:

    - Add an entrance for **Support** in the <MDSvgIcon name="icon-top-organization" /> in the lower-left corner.
    - Revamp the menus of the **?** icon in the lower-right corner of the [TiDB Cloud console](https://tidbcloud.com/) to make them more intuitive.

  For more information, see [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
## July 18, 2023

**General changes**

- Refine role-based access control at both the organization level and project level, which lets you grant roles with minimum permissions to users for better security, compliance, and productivity.

    - The organization roles include `Organization Owner`, `Organization Billing Admin`, `Organization Console Audit Admin`, and `Organization Member`.
    - The project roles include `Project Owner`, `Project Data Access Read-Write`, and `Project Data Access Read-Only`.
    - To manage clusters in a project (such as cluster creation, modification, and deletion), you need to be in the `Organization Owner` or `Project Owner` role.

  For more information about permissions of different roles, see [User roles](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access#user-roles).

- Support the Customer-Managed Encryption Key (CMEK) feature (beta) for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters hosted on AWS.

    You can create CMEK based on AWS KMS to encrypt data stored in EBS and S3 directly from the TiDB Cloud console. This ensures that customer data is encrypted with a key managed by the customer, which enhances security.

    Note that this feature still has restrictions and is only available upon request. To apply for this feature, contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).

- Optimize the Import feature in TiDB Cloud, aimed at enhancing the data import experience. The following improvements have been made:

    - Unified Import entry for TiDB Cloud Serverless: consolidate the entries for importing data, allowing you to seamlessly switch between importing local files and importing files from Amazon S3.
    - Streamlined configuration: importing data from Amazon S3 now only requires a single step, saving time and effort.
    - Enhanced CSV configuration: the CSV configuration settings are now located under the file type option, making it easier for you to quickly configure the necessary parameters.
    - Enhanced target table selection: support choosing the desired target tables for data import by clicking checkboxes. This improvement eliminates the need for complex expressions and simplifies the target table selection.
    - Refined display information: resolve issues related to inaccurate information displayed during the import process. In addition, the Preview feature has been removed to prevent incomplete data display and avoid misleading information.
    - Improved source files mapping: support defining mapping relationships between source files and target tables. It addresses the challenge of modifying source file names to meet specific naming requirements.
## July 11, 2023

**General changes**

- [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) now is Generally Available.

- Introduce TiDB Bot (beta), an OpenAI-powered chatbot that offers multi-language support, 24/7 real-time response, and integrated documentation access.

    TiDB Bot provides you with the following benefits:

    - Continuous support: always available to assist and answer your questions for an enhanced support experience.
    - Improved efficiency: automated responses reduce latency, improving overall operations.
    - Seamless documentation access: direct access to TiDB Cloud documentation for easy information retrieval and quick issue resolution.

  To use TiDB Bot, click **?** in the lower-right corner of the [TiDB Cloud console](https://tidbcloud.com), and select **Ask TiDB Bot** to start a chat.

- Support [the branching feature (beta)](https://docs.pingcap.com/tidb/stable/tidb-cloud/branch-overview) for [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters.

    TiDB Cloud lets you create branches for TiDB Cloud Serverless clusters. A branch for a cluster is a separate instance that contains a diverged copy of data from the original cluster. It provides an isolated environment, allowing you to connect to it and experiment freely without worrying about affecting the original cluster.

    You can create branches for TiDB Cloud Serverless clusters created after July 5, 2023 by using either [TiDB Cloud console](https://docs.pingcap.com/tidb/stable/tidb-cloud/branch-manage) or [TiDB Cloud CLI](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-branch-create).

    If you use GitHub for application development, you can integrate TiDB Cloud Serverless branching into your GitHub CI/CD pipeline, which lets you automatically test your pull requests with branches without affecting the production database. For more information, see [Integrate TiDB Cloud Serverless Branching (Beta) with GitHub](https://docs.pingcap.com/tidb/stable/tidb-cloud/branch-github-integration).

- Support weekly backup for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters. For more information, see [Back up and restore TiDB Cloud Dedicated data](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore#turn-on-auto-backup).
## July 4, 2023

**General changes**

- Support point-in-time recovery (PITR) (beta) for [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters.

    You can now restore your TiDB Cloud Serverless cluster to any point in time within the last 90 days. This feature enhances the data recovery capability of TiDB Cloud Serverless clusters. For example, you can use PITR when data write errors occur and you want to restore the data to an earlier state.

    For more information, see [Back up and restore TiDB Cloud Serverless data](https://docs.pingcap.com/tidb/stable/tidb-cloud/backup-and-restore-serverless#restore).

**Console changes**

- Enhance the **Usage This Month** panel on the cluster overview page for [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters to provide a clearer view of your current resource usage.

- Enhance the overall navigation experience by making the following changes:

    - Consolidate <MDSvgIcon name="icon-top-organization" /> **Organization** and <MDSvgIcon name="icon-top-account-settings" /> **Account** in the upper-right corner into the left navigation bar.
    - Consolidate <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke-width="1.5" xmlns="http://www.w3.org/2000/svg"><path d="M12 14.5H7.5C6.10444 14.5 5.40665 14.5 4.83886 14.6722C3.56045 15.06 2.56004 16.0605 2.17224 17.3389C2 17.9067 2 18.6044 2 20M14.5 6.5C14.5 8.98528 12.4853 11 10 11C7.51472 11 5.5 8.98528 5.5 6.5C5.5 4.01472 7.51472 2 10 2C12.4853 2 14.5 4.01472 14.5 6.5ZM22 16.516C22 18.7478 19.6576 20.3711 18.8054 20.8878C18.7085 20.9465 18.6601 20.9759 18.5917 20.9911C18.5387 21.003 18.4613 21.003 18.4083 20.9911C18.3399 20.9759 18.2915 20.9465 18.1946 20.8878C17.3424 20.3711 15 18.7478 15 16.516V14.3415C15 13.978 15 13.7962 15.0572 13.6399C15.1077 13.5019 15.1899 13.3788 15.2965 13.2811C15.4172 13.1706 15.5809 13.1068 15.9084 12.9791L18.2542 12C18.3452 11.9646 18.4374 11.8 18.4374 11.8H18.5626C18.5626 11.8 18.6548 11.9646 18.7458 12L21.0916 12.9791C21.4191 13.1068 21.5828 13.1706 21.7035 13.2811C21.8101 13.3788 21.8923 13.5019 21.9428 13.6399C22 13.7962 22 13.978 22 14.3415V16.516Z" stroke="currentColor" stroke-width="inherit" stroke-linecap="round" stroke-linejoin="round"></path></svg> **Admin** in the left navigation bar into <MDSvgIcon name="icon-left-projects" /> **Project** in the left navigation bar, and remove the ☰ hover menu in the upper-left corner. Now you can click <MDSvgIcon name="icon-left-projects" /> to switch between projects and modify project settings.
    - Consolidate all the help and support information for TiDB Cloud into the menu of the **?** icon in the lower-right corner, such as documentation, interactive tutorials, self-paced training, and support entries.

- TiDB Cloud console now supports Dark Mode, which provides a more comfortable, eye-friendly experience. You can switch between light mode and dark mode from the bottom of the left navigation bar.
## June 27, 2023

**General changes**

- Remove the pre-built sample dataset for newly created [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters.
## June 20, 2023

**General changes**

- Upgrade the default TiDB version of new [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters from [v6.5.2](https://docs.pingcap.com/tidb/v6.5/release-6.5.2) to [v6.5.3](https://docs.pingcap.com/tidb/v6.5/release-6.5.3).
