"""_normalize_tool_args 的空串归一化合同。

LLM native tools 会把可选 string 字段显式填成空串表达"未提供"；归一化必须
删除该键让签名默认值生效，而不是映射成 None——部分工具的默认值本身就是 ""
（match_diagnose_knowledge.alert_metric、optimize_index_selection 时间窗），
None 会在函数体内炸 TypeError 或改变输出语义。
"""

import pytest

from src.agents.agent import _normalize_tool_args


def test_empty_string_arg_is_dropped_so_signature_default_applies():
    args = {"metric_name": "cpu", "alert_metric": "", "top_k": 5}
    assert _normalize_tool_args(args) == {"metric_name": "cpu", "top_k": 5}


def test_non_string_and_non_empty_values_are_preserved():
    args = {"sql_query": "SELECT 1", "lines": 0, "filters": {}, "flag": False}
    assert _normalize_tool_args(args) == args


def test_match_diagnose_knowledge_default_empty_string_join_does_not_crash():
    """删除键后走默认值 alert_metric=""，与"未传该参数"的默认路径逐字节一致。"""
    args = _normalize_tool_args({"metric_name": "cpu", "alert_metric": ""})
    query = " ".join(["cpu", args.get("alert_metric", ""), "qps"]).strip()
    assert query == " ".join(["cpu", "", "qps"]).strip()


def test_none_and_missing_args_untouched():
    assert _normalize_tool_args(None) == {}
    assert _normalize_tool_args({"target": None}) == {"target": None}


@pytest.mark.parametrize("value", ["", "  ", "x"])
def test_only_exact_empty_string_is_dropped(value):
    args = {"key": value}
    result = _normalize_tool_args(args)
    assert ("key" in result) == (value != "")
