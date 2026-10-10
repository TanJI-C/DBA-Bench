# Manage project access and membership

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/manage-user-access.md`
- Source Title: `Identity Access Management`
- Source Heading Path: `Identity Access Management > Manage project access | Identity Access Management > Manage project access > View and switch between projects | Identity Access Management > Manage project access > Create a project | Identity Access Management > Manage project access > Rename a project | Identity Access Management > Manage project access > Invite a project member | Identity Access Management > Manage project access > Modify project roles | Identity Access Management > Manage project access > Remove a project member`
- Source Line Ranges: `215-327`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `identity-access`, `projects`, `project-switching`, `project-creation`, `project-renaming`, `member-invitation`, `role-management`, `member-removal`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0337_277ef98d98`
- Source ID: `tidb-docs-8.1:tidb-cloud/manage-user-access.md#manage-project-access`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8eaa772f3c05647435d2f4b5de57d6824875e4e3e20d08fb5bed11bc379871c2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access#manage-project-access
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/manage-user-access.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Cloud project access operations such as switching projects, creating or renaming a project, inviting members, modifying project roles, or removing a project member.
- Retrieval Keywords: Manage project access, View and switch between projects, Project Settings, Create New Project, Rename, Invite a project member, By Project, Modify project roles, Role column, Remove a project member, Project Owner, Organization Owner, Projects, Users, Resend, verification link will expire in 24 hours, free trial users cannot create a new project
- Follow-up Guidance: The source includes related notes that free trial users cannot create a new project, inviting a user not in your organization automatically adds the user to the organization, and the email verification link expires in 24 hours with a **Resend** option.
- Classification Note: This is classified as an operation because the content is a set of procedural console tasks for project membership, role management, and project administration in TiDB Cloud.

## Official Source Content

## Manage project access
### View and switch between projects

To view and switch between projects, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), click the combo box in the upper-left corner. The list of organizations and projects you belong to is displayed.

    > **Tip:**
    >
    > - If you are currently on the page of a specific cluster, after clicking the combo box in the upper-left corner, you also need to click ← in the combo box to return to the organization and project list.
    > - If you are a member of multiple projects, you can click the target project name in the combo box to switch between projects.

2. To view the detailed information of your project, click the project name, and then click **Project Settings** in the left navigation pane.
### Create a project

> **Note:**
>
> For free trial users, you cannot create a new project.

If you are in the `Organization Owner` role, you can create projects in your organization.

To create a new project, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.

2. In the left navigation pane, click **Projects**.

3. On the **Projects** page, click **Create New Project**.

4. Enter your project name.

5. Click **Confirm**.
### Rename a project

If you are in the `Organization Owner` role, you can rename any projects in your organization. If you are in the `Project Owner` role, you can rename your project.

To rename a project, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.

2. In the left navigation pane, click **Projects**.

3. In the row of your project to be renamed, click **...** > **Rename**.

4. Enter a new project name.

5. Click **Confirm**.
### Invite a project member

If you are in the `Organization Owner` or `Project Owner` role, you can invite members to your projects.

> **Note:**
>
> When a user not in your organization joins your project, the user automatically joins your organization as well.

To invite a member to a project, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.

2. In the left navigation pane, click **Organization Settings** > **Users**.

3. On the **Users** page, click the **By Project** tab, and then choose your project in the drop-down list.

4. Click **Invite**.

5. Enter the email address of the user to be invited, and then select a project role for the user.

    > **Tip:**
    >
    > If you want to invite multiple members at one time, you can enter multiple email addresses.

6. Click **Confirm**. Then the new user is successfully added into the user list. At the same time, an email is sent to the invited email address with a verification link.

7. After receiving this email, the user needs to click the link in the email to verify the identity, and a new page shows.

8. If the invited email address has not been signed up for a TiDB Cloud account, the user is directed to the sign-up page to create an account. If the email address has been signed up for a TiDB Cloud account, the user is directed to the sign-in page. After sign-in, the account joins the project automatically.

> **Note:**
>
> The verification link in the email will expire in 24 hours. If your user doesn't receive the email, click **Resend**.
### Modify project roles

If you are in the `Organization Owner` role, you can modify project roles of all project members in your organization. If you are in the `Project Owner` role, you can modify project roles of all members in your project.

To modify the project role of a member, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.

2. In the left navigation pane, click **Organization Settings** > **Users**.

3. On the **Users** page, click the **By Project** tab, and then choose your project in the drop-down list.

4. In the row of the target member, click the role in the **Role** column, and then choose a new role from the drop-down list.
### Remove a project member

If you are in the `Organization Owner` or `Project Owner` role, you can remove project members.

To remove a member from a project, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.

2. In the left navigation pane, click **Organization Settings** > **Users**.

3. On the **Users** page, click the **By Project** tab, and then choose your project in the drop-down list.

4. In the row of the target member, click **...** > **Delete**.
