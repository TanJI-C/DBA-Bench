# Branching app configuration and CI workflow creation

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/branch-github-integration.md`
- Source Title: `Integrate TiDB Cloud Serverless Branching (Beta) with GitHub`
- Source Heading Path: `Integrate TiDB Cloud Serverless Branching (Beta) with GitHub > Configure TiDB Cloud Branching app | Integrate TiDB Cloud Serverless Branching (Beta) with GitHub > Configure TiDB Cloud Branching app > branch.blockList | Integrate TiDB Cloud Serverless Branching (Beta) with GitHub > Configure TiDB Cloud Branching app > branch.allowList | Integrate TiDB Cloud Serverless Branching (Beta) with GitHub > Configure TiDB Cloud Branching app > branch.mode | Integrate TiDB Cloud Serverless Branching (Beta) with GitHub > Configure TiDB Cloud Branching app > branch.autoDestroy | Integrate TiDB Cloud Serverless Branching (Beta) with GitHub > Create a branching CI workflow | Integrate TiDB Cloud Serverless Branching (Beta) with GitHub > What's next`
- Source Line Ranges: `66-170`
- Source Scope: `developer`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `tidbcloud-yml`, `allowlist`, `blocklist`, `branch-mode`, `auto-destroy`, `github-actions`, `api-keys`, `ci-workflow`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0203_cd48fa450f`
- Source ID: `tidb-docs-8.1:tidb-cloud/branch-github-integration.md#configure-tidb-cloud-branching-app`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `213a5ef35cf05874bebcccb7b5606c5faef40d959d4931e6bbdd8da8e5921d43`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/branch-github-integration#configure-tidb-cloud-branching-app
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/branch-github-integration.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to configure the TiDB Cloud Branching app with tidbcloud.yml or how to create a GitHub Actions CI workflow that waits for a TiDB Cloud Serverless branch and uses its connection information.
- Retrieval Keywords: tidbcloud.yml, branch.blockList, branch.allowList, branch.mode, branch.autoDestroy, reset, reserve, wait-for-tidbcloud-branch, tidbcloud/wait-for-tidbcloud-branch@v0, GITHUB_TOKEN, TIDB_CLOUD_API_PUBLIC_KEY, TIDB_CLOUD_API_PRIVATE_KEY, public-key, private-key, GitHub Actions, branch connection information, setup-tidbcloud-cli
- Follow-up Guidance: The source also links example repositories including branching-gorm-example, branching-django-example, and branching-rails-example, and mentions setup-tidbcloud-cli for customized CI/CD workflows.
- Classification Note: This is classified as configuration because the content defines supported tidbcloud.yml settings, their defaults and types, and the workflow inputs used in a branching CI setup.

## Official Source Content

## Configure TiDB Cloud Branching app

To configure the behaviors of [TiDB Cloud Branching](https://github.com/apps/tidb-cloud-branching) app, you can add a `tidbcloud.yml` file to the root directory of your repository, and then add the desired configurations to this file according to the following instructions.
### branch.blockList

**Type:** array of string. **Default:** `[]`.

Specify the GitHub branches that forbid the TiDB Cloud Branching app, even if they are in the `allowList`.

```yaml
github:
    branch:
        blockList:
            - ".*_doc"
            - ".*_blackList"
```
### branch.allowList

**type:** array of string. **Default:** `[.*]`.

Specify the GitHub branches that allow the TiDB Cloud Branching app.

```yaml
github:
    branch:
        allowList:
            - ".*_db"
```
### branch.mode

**Type:** string. **Default:** `reset`.

Specify how the TiDB Cloud Branching app handles branch updates:

- If it is set to `reset`, the TiDB Cloud Branching app will update the existing branch with the latest data.
- If it is set to `reserve`, the TiDB Cloud Branching app will create a new branch for your latest commit.

```yaml
github:
    branch:
        mode: reset
```
### branch.autoDestroy

**Type:** boolean. **Default:** `true`.

If it is set to `false`, the TiDB Cloud Branching app will not delete the TiDB Cloud Serverless branch when a pull request is closed or merged.

```yaml
github:
    branch:
        autoDestroy: true
```
## Create a branching CI workflow

One of the best practices for using branches is to create a branching CI workflow. With the workflow, you can test your code using a TiDB Cloud Serverless branch instead of using the production cluster before merging the pull request. You can find a live demo [here](https://github.com/shiyuhang0/tidbcloud-branch-gorm-example).

Here are the main steps to create the workflow:

1. [Integrate TiDB Cloud Serverless branching with your GitHub repository](#integrate-tidb-cloud-serverless-branching-with-your-github-repository).

2. Get the branch connection information.

   You can use the [wait-for-tidbcloud-branch](https://github.com/tidbcloud/wait-for-tidbcloud-branch) action to wait for the readiness of the TiDB Cloud Serverless branch and get the connection information of the branch.

    Example usage:

   ```yaml
   steps:
     - name: Wait for TiDB Cloud Serverless branch to be ready
       uses: tidbcloud/wait-for-tidbcloud-branch@v0
       id: wait-for-branch
       with:
         token: ${{ secrets.GITHUB_TOKEN }}
         public-key: ${{ secrets.TIDB_CLOUD_API_PUBLIC_KEY }}
         private-key: ${{ secrets.TIDB_CLOUD_API_PRIVATE_KEY }}

     - name: Test with TiDB Cloud Serverless branch
        run: |
           echo "The host is ${{ steps.wait-for-branch.outputs.host }}"
           echo "The user is ${{ steps.wait-for-branch.outputs.user }}"
           echo "The password is ${{ steps.wait-for-branch.outputs.password }}"
   ```
   
   - `token`: GitHub will automatically create a [GITHUB_TOKEN](https://docs.github.com/en/actions/security-guides/automatic-token-authentication) secret. You can use it directly.
   - `public-key` and `private-key`: The TiDB Cloud [API key](https://docs.pingcap.com/tidbcloud/api/v1beta#section/Authentication/API-Key-Management).

3. Modify your test code.

   Modify your test code to accept the connection information from GitHub Actions. For example, you can accept the connection information through the environment, as demonstrated in the [live demo](https://github.com/shiyuhang0/tidbcloud-branch-gorm-example).
## What's next

Learn how to use the branching GitHub integration with the following examples:

- [branching-gorm-example](https://github.com/tidbcloud/branching-gorm-example)
- [branching-django-example](https://github.com/tidbcloud/branching-django-example)
- [branching-rails-example](https://github.com/tidbcloud/branching-rails-example)

You can also build your branching CI/CD workflow without the branching GitHub integration. For example, you can use [`setup-tidbcloud-cli`](https://github.com/tidbcloud/setup-tidbcloud-cli) and GitHub Actions to customize your CI/CD workflows.
