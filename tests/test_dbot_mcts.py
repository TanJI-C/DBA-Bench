"""Tests for DB-GPT trajectory tree helpers."""

from src.agents.baselines.dbot.mcts import DiagnosisTree, TreeSearchConfig


def test_tree_search_config_matches_db_gpt_defaults():
    config = TreeSearchConfig()
    assert config.simulation_count == 2
    assert config.epsilon_new_node == 0.3
    assert config.vote_candidates == 2
    assert config.single_chain_max_step == 24


def test_diagnosis_tree_stores_thought_action_observation_chain():
    tree = DiagnosisTree(alert="High CPU")
    thought = tree.add_child(tree.root, "Thought", "Check CPU first")
    action = tree.add_child(thought, "Action", "whether_is_abnormal_metric")
    action_input = tree.add_child(
        action,
        "Action Input",
        '{"metric_name":"cpu"}',
        observation="CPU is abnormal",
    )

    trace = tree.get_former_trace(tree.root, action_input)
    assert "Thought: Check CPU first" in trace
    assert "Action: whether_is_abnormal_metric" in trace
    assert "Observation: CPU is abnormal" in trace

    data = tree.to_json_recursive()
    assert data["size"] == 4
    assert data["tree"]["node_type"] == "Action Input"
