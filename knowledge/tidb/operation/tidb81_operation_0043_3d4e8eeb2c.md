# Share and use a TiDB Dashboard session

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-session-share.md`
- Source Title: `Share TiDB Dashboard Sessions`
- Source Heading Path: `Share TiDB Dashboard Sessions | Share TiDB Dashboard Sessions > Steps for the inviter | Share TiDB Dashboard Sessions > Steps for the invitee`
- Source Line Ranges: `5-56`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tidb`
- Topic Tags: `session-sharing`, `authorization-code`, `signin`, `read-only`, `expiration`, `security-warning`, `access-control`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0043_3d4e8eeb2c`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-session-share.md#share-tidb-dashboard-sessions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `af444041f58543659d969a32eeb2b946a3c3790ac4d957e02c7c4a98e9541974`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-session-share#share-tidb-dashboard-sessions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-session-share.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about sharing a current TiDB Dashboard session with another user by using an Authorization Code, including read-only access, expiration, and alternative authentication sign-in steps.
- Retrieval Keywords: Share TiDB Dashboard Sessions, Share Current Session, Authorization Code, Use Alternative Authentication, Share as read-only privilege, Expire in, TiDB Dashboard sign-in, shared session cannot be shared again, Steps for the inviter, Steps for the invitee
- Follow-up Guidance: The source also provides the invitee sign-in flow through Use Alternative Authentication, Authorization Code, entering the code, and clicking Sign In.
- Classification Note: This is classified as a dashboard operation topic because the content describes the procedure and controls for sharing and using a TiDB Dashboard session in a self-managed environment.

## Official Source Content

# Share TiDB Dashboard Sessions

You can share the current session of the TiDB Dashboard to other users so that they can access and operate the TiDB Dashboard without entering the user password.
## Steps for the inviter

1. Sign into TiDB Dashboard.

2. Click the username in the left sidebar to access the configuration page.

3. Click **Share Current Session**.

   ![Sample Step](/media/dashboard/dashboard-session-share-settings-1-v650.png)

   > **Note:**
   >
   > For security reasons, the shared session cannot be shared again.

4. Adjust sharing settings in the popup dialog:

   - Expire in: How long the shared session will be effective. Signing out of the current session does not affect the effective time of the shared session.

   - Share as read-only privilege: The shared session only permits read operations but not write operations (such as modifying configurations).

5. Click **Generate Authorization Code**.

   ![Sample Step](/media/dashboard/dashboard-session-share-settings-2-v650.png)

6. Provide the generated **Authorization Code** to the user to whom you want to share the session.

   ![Sample Step](/media/dashboard/dashboard-session-share-settings-3-v650.png)

   > **Warning:**
   >
   > Keep your authorization code secure and do not send it to anyone who is untrusted. Otherwise, they will be able to access and operate TiDB Dashboard without your authorization.
## Steps for the invitee

1. On the sign-in page of TiDB Dashboard, click **Use Alternative Authentication**.

   ![Sample Step](/media/dashboard/dashboard-session-share-signin-1-v650.png)

2. Click **Authorization Code** to use it to sign in.

   ![Sample Step](/media/dashboard/dashboard-session-share-signin-2-v650.png)

3. Enter the authorization code you have received from the inviter.

4. Click **Sign In**.

   ![Sample Step](/media/dashboard/dashboard-session-share-signin-3-v650.png)
