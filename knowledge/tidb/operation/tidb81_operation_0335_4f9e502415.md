# Manage organization access and membership

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/manage-user-access.md`
- Source Title: `Identity Access Management`
- Source Heading Path: `Identity Access Management > Manage organization access | Identity Access Management > Manage organization access > View and switch between organizations | Identity Access Management > Manage organization access > Set the time zone for your organization | Identity Access Management > Manage organization access > Invite an organization member | Identity Access Management > Manage organization access > Modify organization roles`
- Source Line Ranges: `119-196`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `organization-access`, `organization-settings`, `time-zone`, `member-invite`, `role-management`, `console-navigation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0335_4f9e502415`
- Source ID: `tidb-docs-8.1:tidb-cloud/manage-user-access.md#manage-organization-access`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a2118af703b2b65d944c248ed64611bf1581ad6a1de2a4d6ed0f398aa99762a3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access#manage-organization-access
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/manage-user-access.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB Cloud console steps to switch organizations, view organization details, set the organization time zone, invite an organization member, or modify organization roles.
- Retrieval Keywords: Manage organization access, View and switch between organizations, Organization Settings > General, Organization Settings > Users, By Organization, Time Zone, Invite, Confirm, Resend, organization ID, modify organization roles, invite an organization member, verification link expires in 24 hours, combo box in the upper-left corner
- Follow-up Guidance: The source notes that inviting a user directly to a project also makes the user an organization member, and that the verification link email can be resent if needed.
- Classification Note: This is operation content because it provides step-by-step TiDB Cloud console procedures for organization access, membership, time zone settings, and role changes.

## Official Source Content

## Manage organization access
### View and switch between organizations

To view and switch between organizations, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), click the combo box in the upper-left corner. The list of organizations and projects you belong to is displayed.

    > **Tip:**
    >
    > - If you are currently on the page of a specific cluster, after clicking the combo box in the upper-left corner, you also need to click ← in the combo box to return to the organization and project list.
    > - If you are a member of multiple organizations, you can click the target organization name in the combo box to switch your account between organizations.

2. To view the detailed information of your organization such as the organization ID and time zone, click the organization name, and then click **Organization Settings** > **General** in the left navigation pane.
### Set the time zone for your organization

If you are in the `Organization Owner` role, you can modify the system display time according to your time zone.

To change the local timezone setting, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.

2. In the left navigation pane, click **Organization Settings** > **General**.

3. In the **Time Zone** section, select your time zone from the drop-down list.

4. Click **Update**.
### Invite an organization member

If you are in the `Organization Owner` role, you can invite users to your organization.

> **Note:**
>
> You can also [invite a user to your project](#invite-a-project-member) directly according to your need, which also makes the user your organization member.

To invite a member to an organization, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.

2. In the left navigation pane, click **Organization Settings** > **Users**.

3. On the **Users** page, click the **By Organization** tab.

4. Click **Invite**.

5. Enter the email address of the user to be invited, and then select an organization role for the user.

    > **Tip:**
    >
    > - If you want to invite multiple members at one time, you can enter multiple email addresses.
    > - The invited user does not belong to any projects by default. To invite a user to a project, see [Invite a project member](#invite-a-project-member).

6. Click **Confirm**. Then the new user is successfully added into the user list. At the same time, an email is sent to the invited email address with a verification link.

7. After receiving this email, the user needs to click the link in the email to verify the identity, and a new page shows.

8. If the invited email address has not been signed up for a TiDB Cloud account, the user is directed to the sign-up page to create an account. If the email address has been signed up for a TiDB Cloud account, the user is directed to the sign-in page, and after sign-in, the account joins the organization automatically.

> **Note:**
>
> The verification link in the email expires in 24 hours. If the user you want to invite does not receive the email, click **Resend**.
### Modify organization roles

If you are in the `Organization Owner` role, you can modify organization roles of all members in your organization.

To modify the organization role of a member, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.

2. In the left navigation pane, click **Organization Settings** > **Users**.

3. On the **Users** page, click the **By Organization** tab.

4. Click the role of the target member, and then modify the role.
