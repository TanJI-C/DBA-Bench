# Deploy the Netlify example app with TiDB Cloud database settings

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/integrate-tidbcloud-with-netlify.md`
- Source Title: `Integrate TiDB Cloud with Netlify`
- Source Heading Path: `Integrate TiDB Cloud with Netlify > Step 2. Deploy the example app to Netlify`
- Source Line Ranges: `125-226`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`
- Topic Tags: `deployment`, `netlify-cli`, `authentication`, `site-init`, `github-webhook`, `deploy-key`, `environment-variables`, `database-url`, `local-build`, `schema-migration`, `local-preview`, `production-deploy`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0333_9245e319fe`
- Source ID: `tidb-docs-8.1:tidb-cloud/integrate-tidbcloud-with-netlify.md#step-2-deploy-the-example-app-to-netlify`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1743cf6baf5ba7337fabc4355da7300b15e9e6814fe1bed61ab26302efe32b4e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-netlify#step-2-deploy-the-example-app-to-netlify
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/integrate-tidbcloud-with-netlify.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the exact Netlify CLI deployment flow for the TiDB Cloud example app, including authentication, site initialization, environment variables, local build, preview, and production deployment.
- Retrieval Keywords: netlify login, netlify init, Create & configure a new site, deploy key, webhook, GitHub Notification Hooks, DATABASE_URL, netlify env:set DATABASE_URL, netlify env:list, env | grep DATABASE_URL, npm run netlify-build, netlify dev, http://localhost:3000/, netlify deploy --prod --trigger
- Follow-up Guidance: The chunk points to using the Netlify console to check deployment state after `netlify deploy --prod --trigger`.
- Classification Note: This is classified as operation because the content is a step-by-step deployment procedure for running the example app on Netlify with TiDB Cloud database settings.

## Official Source Content

## Step 2. Deploy the example app to Netlify

1. In Netlify CLI, authenticate your Netlify account and obtain an access token.

    ```shell
    netlify login
    ```

2. Start the automatic setup. This step connects your repository for continuous deployment, so Netlify CLI needs access to create a deploy key and a webhook on the repository.

    ```shell
    netlify init
    ```

    When you are prompted, choose **Create & configure a new site**, and grant GitHub access. Use the default values for all other options.

    ```shell
    Adding local .netlify folder to .gitignore file...
    ? What would you like to do? +  Create & configure a new site
    ? Team: your_username’s team
    ? Site name (leave blank for a random name; you can change it later):

    Site Created

    Admin URL: https://app.netlify.com/sites/mellow-crepe-e2ca2b
    URL:       https://mellow-crepe-e2ca2b.netlify.app
    Site ID:   b23d1359-1059-49ed-9d08-ed5dba8e83a2

    Linked to mellow-crepe-e2ca2b


    ? Netlify CLI needs access to your GitHub account to configure Webhooks and Deploy Keys. What would you like to do? Authorize with GitHub through app.netlify.com
    Configuring Next.js runtime...

    ? Your build command (hugo build/yarn run build/etc): npm run netlify-build
    ? Directory to deploy (blank for current dir): .next

    Adding deploy key to repository...
    (node:36812) ExperimentalWarning: The Fetch API is an experimental feature. This feature could change at any time
    (Use `node --trace-warnings ...` to show where the warning was created)
    Deploy key added!

    Creating Netlify GitHub Notification Hooks...
    Netlify Notification Hooks configured!

    Success! Netlify CI/CD Configured!

    This site is now configured to automatically deploy from github branches & pull requests

    Next steps:

    git push       Push to your git repository to trigger new site builds
    netlify open   Open the Netlify admin URL of your site
    ```

3. Set environment variables. To connect to your TiDB Cloud cluster from your own space and the Netlify space, you need to set the `DATABASE_URL` as the connection string obtained from [Step 1](#step-1-get-the-example-project-and-the-connection-string).

    ```shell
    # set the environment variable for your own space
    export DATABASE_URL='mysql://<User>:<Password>@<Endpoint>:<Port>/<Database>?sslaccept=strict'

    # set the environment variable for the Netlify space
    netlify env:set DATABASE_URL 'mysql://<User>:<Password>@<Endpoint>:<Port>/<Database>?sslaccept=strict'
    ```

    Check your environment variables.

    ```shell
    # check the environment variable for your own space
    env | grep DATABASE_URL

    # check the environment variable for the Netlify space
    netlify env:list
    ```

4. Build the app locally and migrate the schema to your TiDB Cloud cluster.

    > **Tips:**
    >
    > If you want to skip the local deployment and directly deploy the app to Netlify, just go to step 6.

    ```shell
    npm install .
    npm run netlify-build
    ```

5. Run the application locally. You can start a local development server to preview your site.

    ```shell
    netlify dev
    ```

    Then, go to `http://localhost:3000/` in your browser to explore its UI.

6. Deploy the app to Netlify. Once you are satisfied with the local preview, you can deploy your site to Netlify using the following command. `--trigger` means deployment without uploading local files. If you made any local changes, make sure that you have committed them to your GitHub repository.

    ```shell
    netlify deploy --prod --trigger
    ```

    Go to your Netlify console to check the deployment state. After the deployment is done, the site for the app will have a public IP address provided by Netlify so that everyone can access it.
