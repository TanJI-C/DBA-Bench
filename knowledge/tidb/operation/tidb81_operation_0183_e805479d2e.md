# Unlock locked account and reset failed-login counters

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/password-management.md`
- Source Title: `TiDB Password Management`
- Source Heading Path: `TiDB Password Management > Failed-login tracking and temporary account locking policy > Unlock the locked account`
- Source Line Ranges: `405-422`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `account-locking`, `failed-login-tracking`, `account-unlock`, `login-attempts`, `password-errors`, `lock-time`, `alter-user`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0183_e805479d2e`
- Source ID: `tidb-docs-8.1:password-management.md#unlock-the-locked-account`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `997742cbde107a36e02b57d230789ebb98bd969ca0ae59bca9fb4daab7e81640`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/password-management#unlock-the-locked-account
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/password-management.md

## Retrieval Guidance

- Use When: Use this content when asking how TiDB resets consecutive password error counts, unlocks a temporarily locked account, or what happens after changing account locking policy settings.
- Retrieval Keywords: ALTER USER ... ACCOUNT UNLOCK, FAILED_LOGIN_ATTEMPTS, PASSWORD_LOCK_TIME, consecutive password errors, locked account, unlock the locked account, successful login, next login attempt, automatic lock flag
- Follow-up Guidance: The content states that changing FAILED_LOGIN_ATTEMPTS or PASSWORD_LOCK_TIME does not immediately change the current lock status, and the new setting takes effect after unlock or at the next login attempt.
- Classification Note: This is classified as an operation topic because the official content describes the conditions and SQL statement used to reset failed-login counters and unlock an account.

## Official Source Content

### Unlock the locked account

In the following scenarios, the count of consecutive password errors can be reset:

- When you execute the `ALTER USER ... ACCOUNT UNLOCK` statement.
- When you log in successfully.

In the following scenarios, the locked account can be unlocked:

- When the lock time ends, the automatic lock flag of the account will be reset at the next login attempt.
- When you execute the `ALTER USER ... ACCOUNT UNLOCK` statement.

> **Note:**
>
> When an account is locked due to consecutive login failures, modifying the account locking policy has the following effects:
>
> - When you modify `FAILED_LOGIN_ATTEMPTS`, the lock status of the account does not change. The modified `FAILED_LOGIN_ATTEMPTS` takes effect after the account is unlocked and attempts to log in again.
> - When you modify `PASSWORD_LOCK_TIME`, the lock status of the account does not change. The modified `PASSWORD_LOCK_TIME` takes effect when the account attempts to log in again. At that time, TiDB checks whether the new lock time has reached. If yes, TiDB will unlock the user.
