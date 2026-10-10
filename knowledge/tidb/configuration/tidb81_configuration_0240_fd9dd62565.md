# Vercel preview deployments with TiDB Cloud Serverless branching

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/integrate-tidbcloud-with-vercel.md`
- Source Title: `Integrate TiDB Cloud with Vercel`
- Source Heading Path: `Integrate TiDB Cloud with Vercel > Connect via the TiDB Cloud Vercel integration > Connect with TiDB Cloud Serverless branching`
- Source Line Ranges: `170-215`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `vercel`, `preview-deployments`, `serverless-branching`, `github`, `environment-variables`, `branch-limits`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0240_fd9dd62565`
- Source ID: `tidb-docs-8.1:tidb-cloud/integrate-tidbcloud-with-vercel.md#connect-with-tidb-cloud-serverless-branching`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `50e3ad4d878c8f5376bececc7586b19c2662179c9ca05b2a53e20ac662db298c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-vercel#connect-with-tidb-cloud-serverless-branching
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/integrate-tidbcloud-with-vercel.md

## Retrieval Guidance

- Use When: Use this when looking for how Vercel Preview Deployments work with TiDB Cloud Serverless Branching, including branch creation, environment variables, GitHub repository support, and branch limits.
- Retrieval Keywords: Vercel Preview Deployments, TiDB Cloud Serverless Branching, TiDB Cloud Vercel integration workflow, Cluster connection type, Enable Branching, Vercel projects associated with GitHub repositories, preview deployment, TiDB Cloud Serverless branch, environment variables, blocking check, rerun the check manually, environment variable cannot be ensured to be set in the deployment, redeploy the deployment, maximum of five TiDB Cloud Serverless branches, Manage TiDB Cloud Serverless branches
- Follow-up Guidance: The content notes that if the environment variable is not set in the deployment due to a Vercel deployment workflow limitation, you need to redeploy the deployment.
- Classification Note: This is classified as configuration because the content explains the required integration settings and workflow behavior for enabling TiDB Cloud Serverless branching in Vercel preview environments.

## Official Source Content

### Connect with TiDB Cloud Serverless branching

Vercel's [Preview Deployments](https://vercel.com/docs/deployments/preview-deployments) feature allows you to preview changes to your app in a live deployment without merging those changes to your Git project's production branch. With [TiDB Cloud Serverless Branching](https://docs.pingcap.com/tidb/stable/tidb-cloud/branch-overview), you can create a new instance for each branch of your Vercel project. This allows you to preview app changes in a live deployment without affecting your production data.

> **Note:**
>
> Currently, TiDB Cloud Serverless branching only supports [Vercel projects associated with GitHub repositories](https://vercel.com/docs/deployments/git/vercel-for-github).

To enable TiDB Cloud Serverless Branching, you need to ensure the following in the [TiDB Cloud Vercel integration workflow](#integration-workflow):

1. Select **Cluster** as your connection type. 
2. Enable **Branching** to create new branches for preview environments.

After you push changes to the Git repository, Vercel will trigger a preview deployment. TiDB Cloud integration will automatically create a TiDB Cloud Serverless branch for the Git branch and set environment variables. The detailed steps are as follows:

1. Create a new branch in your Git repository.

    ```shell
    cd tidb-prisma-vercel-demo1
    git checkout -b new-branch
    ```

2. Add some changes and push the changes to the remote repository.
3. Vercel will trigger a preview deployment for the new branch.

    ![Vercel Preview_Deployment](/media/tidb-cloud/vercel/vercel-preview-deployment.png)

    1. During the deployment, TiDB Cloud integration will automatically create a TiDB Cloud Serverless branch with the same name as the Git branch. If the TiDB Cloud Serverless branch already exists, TiDB Cloud integration will skip this step.

        ![TiDB_Cloud_Branch_Check](/media/tidb-cloud/vercel/tidbcloud-branch-check.png)

    2. After the TiDB Cloud Serverless branch is ready, TiDB Cloud integration will set environment variables in the preview deployment for the Vercel project.

        ![Preview_Envs](/media/tidb-cloud/vercel/preview-envs.png)

    3. TiDB Cloud integration will also register a blocking check to wait for the TiDB Cloud Serverless branch to be ready. You can rerun the check manually.
4. After the check is passed, you can visit the preview deployment to see the changes.

> **Note:**
>
> Due to a limitation of Vercel deployment workflow, the environment variable cannot be ensured to be set in the deployment. In this case, you need to redeploy the deployment.

> **Note:**
>
> For each organization in TiDB Cloud, you can create a maximum of five TiDB Cloud Serverless branches by default. To avoid exceeding the limit, you can delete the TiDB Cloud Serverless branches that are no longer needed. For more information, see [Manage TiDB Cloud Serverless branches](https://docs.pingcap.com/tidb/stable/tidb-cloud/branch-manage).
