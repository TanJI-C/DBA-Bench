import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.execution.environments.postgres import PGEnv


def test_read_log_default_returns_first_100_lines_with_total():
    output = "\n".join(f"line-{i}" for i in range(1, 121))

    page = PGEnv._slice_log_output(output, lines=100, start_line=None, end_line=None)

    assert page["total_lines"] == 120
    assert page["start_line"] == 1
    assert page["end_line"] == 100
    assert page["content"].splitlines()[0] == "line-1"
    assert page["content"].splitlines()[-1] == "line-100"


def test_read_log_range_is_1_based_and_inclusive():
    output = "\n".join(f"line-{i}" for i in range(1, 11))

    page = PGEnv._slice_log_output(output, lines=100, start_line=4, end_line=6)

    assert page["total_lines"] == 10
    assert page["start_line"] == 4
    assert page["end_line"] == 6
    assert page["content"].splitlines() == ["line-4", "line-5", "line-6"]


def test_read_log_end_line_minus_one_means_last_line():
    output = "\n".join(f"line-{i}" for i in range(1, 11))

    page = PGEnv._slice_log_output(output, lines=100, start_line=8, end_line=-1)

    assert page["total_lines"] == 10
    assert page["start_line"] == 8
    assert page["end_line"] == 10
    assert page["content"].splitlines() == ["line-8", "line-9", "line-10"]


def test_read_log_match_key_returns_previous_line_to_next_two():
    output = "\n".join(f"line-{i}" for i in range(1, 8))

    page = PGEnv._slice_log_output(output, lines=100, start_line=None, end_line=None, match_key="line-4")

    assert page["matched_lines"] == [4]
    assert page["start_line"] == 3
    assert page["end_line"] == 6
    assert page["content"].splitlines() == ["line-3", "line-4", "line-5", "line-6"]


def test_read_log_match_key_is_case_insensitive():
    output = "ERROR: nextval reached maximum for invoice_events_event_id_seq"

    page = PGEnv._slice_log_output(
        output,
        lines=100,
        start_line=None,
        end_line=None,
        match_key="INVOICE_EVENTS_EVENT_ID_SEQ",
    )

    assert page["matched_lines"] == [1]
    assert page["content"] == output
