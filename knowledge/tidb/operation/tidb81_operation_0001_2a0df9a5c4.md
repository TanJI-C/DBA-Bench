# Add TiDB Docs Dash badges to a GitHub profile README

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/.vaunt/add-tidb-docs-dash-badge.md`
- Source Title: `How to Add TiDB Docs Dash Badges to Your GitHub Profile`
- Source Heading Path: `How to Add TiDB Docs Dash Badges to Your GitHub Profile | How to Add TiDB Docs Dash Badges to Your GitHub Profile > Step 1. Create a repository for your profile README | How to Add TiDB Docs Dash Badges to Your GitHub Profile > Step 2. Edit your profile README | How to Add TiDB Docs Dash Badges to Your GitHub Profile > (Optional) Explore more with Vaunt`
- Source Line Ranges: `1-70`
- Source Scope: `developer`
- Primary Component: `shared`
- Related Components: `ecosystem`
- Topic Tags: `github-profile`, `readme`, `badge`, `vaunt`, `repository-creation`, `html-snippet`, `markdown-snippet`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0001_2a0df9a5c4`
- Source ID: `tidb-docs-8.1:.vaunt/add-tidb-docs-dash-badge.md#how-to-add-tidb-docs-dash-badges-to-your-github-profile`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `eb40ca3739b506146fa136004b1c6ba42b018132e8db99135d1d08f20e743e51`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/.vaunt/add-tidb-docs-dash-badge#how-to-add-tidb-docs-dash-badges-to-your-github-profile
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/.vaunt/add-tidb-docs-dash-badge.md

## Retrieval Guidance

- Use When: Use this chunk when someone wants to add a TiDB Docs Dash 2024 badge to a GitHub profile README or needs the exact README snippet and repository setup steps.
- Retrieval Keywords: TiDB Docs Dash 2024, GitHub profile README, Add TiDB Docs Dash badges to your GitHub profile, repository name matches your GitHub username, Add a README file, Edit README, https://api.vaunt.dev/v1/github/entities/{{github_username}}/achievements?format=svg&limit=3, Vaunt, developer card, https://api.vaunt.dev/v1/github/entities/{{github_username}}/contributions?format=svg, VauntCommunity, https://api.vaunt.dev/v1/github/entities/{{github_username}}/badges/community, community boards
- Follow-up Guidance: The same source also provides optional Vaunt snippets for integrating a developer card and community boards into the GitHub profile README.
- Classification Note: This is classified as an operation for the shared component because the content gives step-by-step GitHub README editing and repository creation instructions, with ecosystem-related Vaunt badge integrations.

## Official Source Content

# How to Add TiDB Docs Dash Badges to Your GitHub Profile

Your [GitHub profile](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/about-your-profile) is more than just a collection of repositories; it is your professional identity in the coding world.

This guide walks you through the steps of adding [TiDB Docs Dash 2024](https://www.pingcap.com/event/tidb-docs-dash/) badges to your GitHub profile.
## Step 1. Create a repository for your profile README

If you have already set up your GitHub profile README, skip the following and go to [Step 2. Edit your profile README](#step-2-edit-your-profile-readme).

1. In the upper-right corner of any GitHub page, click **+**, and then click **New repository**.

    <img src="https://docs.github.com/assets/cb-34248/mw-1440/images/help/repository/repo-create-global-nav-update.webp" width="350" />

2. Type a repository name that matches your GitHub username. For example, if your username is `ilovetidb`, the repository name must be `ilovetidb`.
3. Choose **Public** for the repository visibility.
4. Under **Initialize this repository with:**, select **Add a README file**.
5. Click **Create repository**.
## Step 2. Edit your profile README

1. On the GitHub page of your `<github_username>` repository, click **Edit README** above the right sidebar.
2. Add the following code to your README file, replace `{{github_username}}` with your username, and commit the changes directly.

    ```HTML
    <p>
      <img src="https://api.vaunt.dev/v1/github/entities/{{github_username}}/achievements?format=svg&limit=3" width="350" />
    </p>
    ```

 Your GitHub profile now displays your TiDB Docs Dash badge. For more information about managing your profile README, see [GitHub docs](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/managing-your-profile-readme).
## (Optional) Explore more with Vaunt

TiDB Docs Dash badges are granted via [Vaunt](https://vaunt.dev/), a developer relations platform that aims to empower and grow developer communities.

You can use additional Vaunt features to showcase your contributions to other open source projects as follows:

- Integrate your developer card

    Example card:

    <p>
        <a href="https://vaunt.dev">
            <img src="https://api.vaunt.dev/v1/github/entities/jeff1010322/contributions?format=svg" width="350" />
        </a>
    </p>

    To integrate your developer card, add the following code to your README file and replace `{{github_username}}` with your username.

    ```HTML
    <p>
        <a href="https://vaunt.dev">
            <img src="https://api.vaunt.dev/v1/github/entities/{{github_username}}/contributions?format=svg" width="350" />
        </a>
    </p>
    ```

- Integrate your community boards

    The community boards provide community statistics, repository insights, and a view into repository achievements.

    [![VauntCommunity](https://api.vaunt.dev/v1/github/entities/pingcap/badges/community)](https://community.vaunt.dev/board/pingcap)

    - Explore [your own community boards](https://community.vaunt.dev/).
    - Add the following code to your README file and replace `{{github_username}}` with your username:

    ```Markdown
    [![VauntCommunity](https://api.vaunt.dev/v1/github/entities/{{github_username}}/badges/community)](https://community.vaunt.dev/board/{{github_username}})
    ```
