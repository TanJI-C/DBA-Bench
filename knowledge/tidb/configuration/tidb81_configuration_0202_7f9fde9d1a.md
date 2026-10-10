# GitHub integration setup and default branching app behaviors

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/branch-github-integration.md`
- Source Title: `Integrate TiDB Cloud Serverless Branching (Beta) with GitHub`
- Source Heading Path: `Integrate TiDB Cloud Serverless Branching (Beta) with GitHub | Integrate TiDB Cloud Serverless Branching (Beta) with GitHub > Before you begin | Integrate TiDB Cloud Serverless Branching (Beta) with GitHub > Integrate TiDB Cloud Serverless branching with your GitHub repository | Integrate TiDB Cloud Serverless Branching (Beta) with GitHub > TiDB Cloud Branching app behaviors`
- Source Line Ranges: `5-65`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `github`, `serverless-branching`, `pull-requests`, `app-authorization`, `repository-connection`, `branch-lifecycle`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0202_7f9fde9d1a`
- Source ID: `tidb-docs-8.1:tidb-cloud/branch-github-integration.md#integrate-tidb-cloud-serverless-branching-beta-with-github`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9a2be1ec77d0b1cd9869d0e8ca95f9e602e3bf26aa2cd7974e015c4dacba0ead`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/branch-github-integration#integrate-tidb-cloud-serverless-branching-beta-with-github
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/branch-github-integration.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to connect a TiDB Cloud Serverless cluster to a GitHub repository or wants the default TiDB Cloud Branching app behavior for pull request lifecycle events.
- Retrieval Keywords: TiDB Cloud Serverless Branching (Beta) with GitHub, TiDB Cloud Branching GitHub App, Connect to GitHub, Branches page, GitHub Account, GitHub Repository, create a pull request, push new commits to a pull request, close or merge a pull request, reopen a pull request, branch.mode reset, branch.mode reserve, ${github_branch_name}_${pr_id}, ${github_branch_name}_${pr_id}_${commit_sha}
- Follow-up Guidance: The source also points to app configuration in tidbcloud.yml and a branching-based CI workflow for testing pull requests with branches.
- Classification Note: This is classified as configuration because it describes prerequisites, console steps to connect a repository, app authorization, and default branch lifecycle behaviors controlled by pull request events.

## Official Source Content

# Integrate TiDB Cloud Serverless Branching (Beta) with GitHub 

> **Note:**
>
> The integration is built upon [TiDB Cloud Serverless branching](https://docs.pingcap.com/tidb/stable/tidb-cloud/branch-overview). Make sure that you are familiar with TiDB Cloud Serverless branching before reading this document.

If you use GitHub for application development, you can integrate TiDB Cloud Serverless branching into your GitHub CI/CD pipeline, which lets you automatically test your pull requests with branches without affecting the production database.

In the integration process, you will be prompted to install the [TiDB Cloud Branching](https://github.com/apps/tidb-cloud-branching) GitHub App. The app can automatically manage TiDB Cloud Serverless branches according to pull requests in your GitHub repository. For example, when you create a pull request, the app will create a corresponding branch for your TiDB Cloud Serverless cluster, in which you can work on new features or bug fixes in isolation without affecting the production database.

This document covers the following topics:

1. How to integrate TiDB Cloud Serverless branching with GitHub
2. How does the TiDB Cloud Branching app work
3. How to build a branching-based CI workflow to test every pull request using branches rather than the production cluster
## Before you begin

Before the integration, make sure that you have the following:

- A GitHub account
- A GitHub repository for your application
- A [TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster-serverless)
## Integrate TiDB Cloud Serverless branching with your GitHub repository

To integrate TiDB Cloud Serverless branching with your GitHub repository, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com/), navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, and then click the name of your target TiDB Cloud Serverless cluster to go to its overview page.

2. Click **Branches** in the left navigation pane.

3. In the upper-right corner of the **Branches** page, click **Connect to GitHub**.

    - If you have not logged into GitHub, you will be asked to log into GitHub first.
    - If it is the first time you use the integration, you will be asked to authorize the **TiDB Cloud Branching** app.

   <img src="https://docs-download.pingcap.com/media/images/docs/tidb-cloud/branch/github-authorize.png" width="80%" />

4. In the **Connect to GitHub** dialog, select a GitHub account in the **GitHub Account** drop-down list.

    If your account does not exist in the list, click **Install Other Account**, and then follow the on-screen instructions to install the account.

5. Select your target repository in the **GitHub Repository** drop-down list. If the list is long, you can search the repository by typing the name.

6. Click **Connect** to connect between your TiDB Cloud Serverless cluster and your GitHub repository.

   <img src="https://docs-download.pingcap.com/media/images/docs/tidb-cloud/branch/github-connect.png" width="40%" />
## TiDB Cloud Branching app behaviors

After you connect your TiDB Cloud Serverless cluster to your GitHub repository, for each pull request in this repository, the [TiDB Cloud Branching](https://github.com/apps/tidb-cloud-branching) GitHub App can automatically manage its corresponding TiDB Cloud Serverless branch. The following lists the default behaviors for pull request changes:

| Pull request changes               | TiDB Cloud Branching app behaviors                                                                                                                                                                                                                                                                                                                                        |
|------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Create a pull request              | When you create a pull request in the repository, the [TiDB Cloud Branching](https://github.com/apps/tidb-cloud-branching) app creates a branch for your TiDB Cloud Serverless cluster. When `branch.mode` is set to `reset`, the branch name follows the `${github_branch_name}_${pr_id}` format. When `branch.mode` is set to `reserve`, the branch name follows the `${github_branch_name}_${pr_id}_${commit_sha}` format. Note that the number of branches has a [limit](https://docs.pingcap.com/tidb/stable/tidb-cloud/branch-overview#limitations-and-quotas). |
| Push new commits to a pull request | When `branch.mode` is set to `reset`, every time you push a new commit to a pull request in the repository, the [TiDB Cloud Branching](https://github.com/apps/tidb-cloud-branching) app resets the TiDB Cloud Serverless branch. When `branch.mode` is set to `reserve`, the app creates a new branch for the latest commit.                                                                                                                            |
| Close or merge a pull request      | When you close or merge a pull request, the [TiDB Cloud Branching](https://github.com/apps/tidb-cloud-branching) app deletes the branch for this pull request.                                                                                                                                                                                                            |
| Reopen a pull request              | When you reopen a pull request, the [TiDB Cloud Branching](https://github.com/apps/tidb-cloud-branching) app creates a branch for the lasted commit of the pull request.                                                                                                                                                                                                  |
