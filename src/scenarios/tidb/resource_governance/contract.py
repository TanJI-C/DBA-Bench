from src.database.sql import execute_json_payload


def business_truth_queries(case: object) -> tuple[tuple[str, str], ...]:
    return (
        (
            "accounts",
            (
                "SELECT COUNT(*), COALESCE(SUM(account_id), 0), "
                "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', account_id, region, tier))), 0) "
                f"FROM {case.db}.{case.account_table}"
            ),
        ),
        (
            "orders",
            (
                "SELECT COUNT(*), COALESCE(SUM(order_id), 0), "
                "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', order_id, account_id, order_day, status, amount))), 0) "
                f"FROM {case.db}.{case.order_table}"
            ),
        ),
        (
            "events",
            (
                "SELECT COUNT(*), COALESCE(SUM(event_id), 0), "
                "COALESCE(BIT_XOR(CRC32(CONCAT_WS('#', event_id, order_id, event_type, event_day, source))), 0) "
                f"FROM {case.db}.{case.event_table}"
            ),
        ),
    )


def business_truth(
    env: object,
    case: object,
) -> dict[str, tuple[int, int, int]]:
    truth = {}
    for name, sql in business_truth_queries(case):
        payload = execute_json_payload(
            env.execute_sql,
            sql,
            f"RG09 business truth: table={name}",
        )
        row = payload["result"][0]
        truth[name] = (int(row[0]), int(row[1]), int(row[2]))
    return truth
