<div align="center">

![DBA-Bench — 面向真实数据库运维的生产级保真 LLM Agent Benchmark](docs/figures/DBA-Bench_title.png)

# DBA-Bench

**生产级保真的数据库运维 LLM Agent Benchmark——PostgreSQL 与 TiDB 的故障诊断与修复评测。**

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Paper](https://img.shields.io/badge/Paper-arXiv%3A2607.22165-B31B1B?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2607.22165)

**113 个 Scenario · 241 个 Case —— 231 个 ScenarioCase + 10 个 Persistent Episode · 2 个数据库系统 · 五阶段故障生命周期 · 4 个内置 baseline**

📄 论文: [arXiv:2607.22165](https://arxiv.org/abs/2607.22165) · [English](README.md) · 简体中文

</div>

## 它是什么

DBA-Bench 让 Agent 在真实数据库环境里完成运维任务，并由数据库系统本身给出判定：

- **五阶段故障生命周期**：故障注入 → 检测 → 诊断 → 修复 → 恢复，trace 记录逐阶段证据。
- **DP/OP/SP 评估合同**：诊断点、操作点、安全点逐 Case 声明，评分是合同而非主观判断；Diagnosis Pass 默认由 `llm_config.json` 选择的本地或外部模型进行语义判分，可显式使用 exact 匹配。详见[语义 DP 指南](docs/zh/guides/evaluation/semantic-diagnosis-matching.guide.zh-CN.md)。
- **难度校准**：Case 提供 Easy/Hard 双难度，附模型实测证据。
- **Persistent 长时程任务**：事件单调到达、多轮告警/巡检会话、检查点、逆向能力清理。
- **业务真值对比**：以业务查询结果快照对真值，不用代理指标。
- **同构工具面**：PostgreSQL 与 TiDB 共用 `query_metrics` / `execute_sql` / `manage_instance` / `read_log`，Agent 跨引擎可移植。

![DBA-Bench 框架图](docs/figures/framework.png)

**场景构建**在 OLTP/OLAP 负载下从故障目录构建"脏环境"PostgreSQL/TiDB 实例；**Agent-环境交互**
让任意 Agent 通过共享工具面在多轮"动作-观察"中修复系统；**多维评估**对每次运行给出
结果（业务真值 Pass/Fail）、诊断准确性、安全性、效率四维得分——即 DP/OP/SP 合同。

## 快速开始

环境要求与完整准备（Python、Docker、镜像源、LLM 凭证、embedding/judge 模型）见
[docs/getting-started.md](docs/getting-started.md)。

> 中文文档：`docs/` 下的文档为英文原版；中文版本位于 [docs/zh/](docs/zh/index.md)
> （子目录结构镜像，文件名带 `.zh-CN.md` 后缀），索引见
> [docs/zh/index.md](docs/zh/index.md)。

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -U pip && pip install -e .

# 零凭证 mock demo：脚本 Agent 修复一个 PostgreSQL 容器（需要 Docker）
python examples/run_mock_llm_demo.py

# TiDB demo（Docker Compose：PD + TiKV + TiDB + Prometheus）
python examples/run_tidb_demo.py
```

正式实验、Agent 接入、内置 baseline（D-Bot / Panda / DBAIOps / Andromeda）、场景分类总览
与扩展指南见 [英文 README](README.md)和[中文文档索引](docs/zh/index.md)。

正式实验可通过 `runtime.agent_language` 选择框架提供给 Agent 的文本语言：`zh`（默认）
或 `en`。英文目前仅支持 PostgreSQL bounded Scenario，也适用于远程 Agent 接收的
提示词和工具说明；完整范围和限制见[正式实验指南](docs/zh/guides/benchmark/run-experiment.guide.zh-CN.md)。

## 接入远程 Agent

独立于 benchmark 进程、使用任意语言编写的 Agent 可以通过 `remote` 模式接入。
外部服务负责模型调用和决策，benchmark 通过 HTTP 获取动作并执行共享工具。
配置、轮数计算、usage 上报和会话结束要求见
[远程 Agent 接入指南](docs/zh/guides/benchmark/connect-remote-agent.guide.zh-CN.md)。

## 引用

使用 DBA-Bench 时请引用配套论文（[arXiv:2607.22165](https://arxiv.org/abs/2607.22165)）：

```bibtex
@misc{chen2026dbabench,
  title         = {DBA-Bench: A Production-Fidelity Benchmark for LLM-Based Database Operations Agents},
  author        = {Junming Chen and Junyang Jiang and Xu Chen and Zibo Liang and Kai Zheng},
  year          = {2026},
  eprint        = {2607.22165},
  archivePrefix = {arXiv},
  primaryClass  = {cs.DB},
  url           = {https://arxiv.org/abs/2607.22165}
}
```

## 许可证

[Apache License 2.0](LICENSE)
