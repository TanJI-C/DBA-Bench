---
language: zh-CN
---

# 快速上手

一份从裸机到完成实验的完整走查指南。[README](../../README.md) 的快速上手涵盖了最顺利的路径；本文档则覆盖所有前置条件、可选的模型下载，以及你最可能遇到的故障情形。

## 0. 前置条件

| 需求 | 版本 / 数量 | 说明 |
|---|---|---|
| Python | 3.10 – 3.12 | `python3 --version` |
| Docker Engine | 20.10+ | 包含 Compose v2（`docker compose version`） |
| Docker 存储文件系统 | xfs + pquota | PG/TiDB 使用容器磁盘配额；ext4 不支持该配置，见第 2 节 |
| 空闲磁盘 | ~10 GB | `postgres:16` 镜像加上每次运行的容器；TiDB Compose 还会拉取 PD/TiKV/TiDB/Prometheus 镜像 |
| 空闲内存 | 4 GB（PG）/ 8 GB（TiDB） | TiDB Compose 运行 PD + TiKV + TiDB + Prometheus |
| （可选）NVIDIA GPU | 24 GB+ 显存 | 仅本地语义诊断裁判（vLLM）需要 |
| （可选）NVIDIA GPU / CPU | 任意 | 知识库向量化默认在 CPU 上运行；若检测到 CUDA 会自动启用 |

## 1. Python 环境

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

可选附加依赖：

```bash
pip install -e '.[knowledge]'   # knowledge-base features (chromadb, llama-index, sentence-transformers)
```

验证导入路径是否可用。场景注册表内嵌了 TPC-DS 工作负载定义，因此需要先取得受版权保护的查询流——如果尚未获取，请按第 7 节操作：

```bash
python -c "from src.benchmark import api; print('ok')"
```

也可以使用 Conda（`conda create -n aiopsbench python=3.11`）——环境名称随意，没有硬编码的环境名。

## 2. Docker

1. 为你的平台安装 Docker Engine：<https://docs.docker.com/engine/install/>（Linux）或 Docker Desktop（macOS/Windows）。
2. 在不使用 sudo 的情况下验证：

   ```bash
   docker run --rm hello-world
   docker compose version   # must be Compose v2
   ```

3. 如果第 2 步报 `docker: unknown command: docker compose`，安装 Compose v2 插件后重新验证：

   ```bash
   sudo apt-get install docker-compose-plugin   # Debian/Ubuntu；Docker Desktop 已包含
   ```

4. 如果在 Linux 上第 2 步报 `permission denied`，请把自己加入 `docker` 组并重新登录：

   ```bash
   sudo usermod -aG docker "$USER"
   ```

运行时使用的镜像：

- PostgreSQL 场景从 Docker Hub 拉取 **`postgres:16`**。
- TiDB 场景使用一个按 digest 固定 **`pingcap/pd`、`pingcap/tikv`、`pingcap/tidb`** 的 Compose 文件，外加 Prometheus 与 cAdvisor。
- 如果在你的网络中 `pingcap/*` 拉取缓慢或被阻断，请在 Docker daemon 中配置注册表镜像（例如 `https://docker.m.daocloud.io`）——Compose 文件中的部分内容已直接引用它。

### Ext4 主机：将 Docker 数据目录迁移到 xfs

```bash
df -T /var/lib/docker
```

如文件系统为 ext4，容器的 `--storage-opt` 磁盘配额会导致启动失败（exit 125）。可执行：

```bash
sudo bash scripts/setup_docker_xfs_dataroot.sh
```

脚本创建稀疏镜像（默认 200G，可用 `SIZE=...` 调整），格式化为 xfs，以 pquota 挂载到
`/srv/docker-xfs`，复制旧数据，更新 `/etc/docker/daemon.json` 的 `data-root`，并验证 1G
容器配额。迁移前运行的容器会重新启动。按脚本输出补齐 fstab 挂载项，否则重启后挂载会消失。
原目录保留为 `/var/lib/docker.ext4.bak`，便于按英文指南回滚。

## 3. 首次运行

```bash
python examples/run_mock_llm_demo.py
```

你应当能看到 mock agent 检查一个 PostgreSQL 容器、提交一次诊断，然后评估器打印各阶段结果。整个过程不涉及任何 LLM 凭据——agent 是脚本化的。接着试试 TiDB demo（首次运行拉取镜像需要几分钟）：

```bash
python examples/run_tidb_demo.py
```

## 4. LLM 凭据

凭据保存在 `config/llm_config.json` 中，以模型名称为键，并且**绝不提交入库**（已被 `.gitignore` 覆盖）：

```bash
cp config/llm_config.example.json config/llm_config.json
# edit: replace every REPLACE_ME with a real key; adjust url / provider / context_window_tokens as needed
```

示例文件展示了三种受支持的形态：

- OpenAI 兼容的云端 API（`url` 以 `/chat/completions` 结尾）
- Anthropic 原生 API（`"provider": "anthropic"`）
- 本地 OpenAI 兼容端点（例如 `127.0.0.1` 上的 vLLM 服务）

提供商会根据 URL 或显式的 `provider` 字段自动识别。

## 5. 可选：语义诊断裁判（LLM judge）

DP 评估器开箱即支持精确匹配。若要进行语义诊断匹配，则需要一个由 vLLM 服务的本地裁判（需要约 24 GB 显存的 NVIDIA GPU）：

```bash
pip install vllm
python scripts/start_dp_semantic_model.py
# first start downloads Qwen/Qwen3-4B-Instruct-2507 (~8 GB) from Hugging Face
```

然后将场景切换到语义模式：

```bash
export AIOPS_DP_MATCH_MODE=semantic
export AIOPS_DP_SEMANTIC_MODEL='Qwen/Qwen3-4B-Instruct-2507'
export AIOPS_DP_SEMANTIC_CONFIG='config/llm_config.json'
```

详情：[语义诊断匹配指南](../guides/evaluation/semantic-diagnosis-matching.guide.md)。

## 6. 可选：知识库向量化（embedding）模型

知识库功能会对 PostgreSQL/TiDB 运维文档做向量化。embedding 模型会在首次使用时自动下载：

- 默认模型：**`Qwen/Qwen3-Embedding-4B`**（可用 `AIOPS_PG_KB_EMBED_MODEL` 覆盖）
- 默认设备：**CPU**（可用 `AIOPS_PG_KB_EMBED_DEVICE` 覆盖，例如 `cuda:0`；多 GPU 可用 `AIOPS_PG_KB_EMBED_TARGET_DEVICES`）
- 下载默认走 `https://hf-mirror.com` 端点；设置 `HF_ENDPOINT=https://huggingface.co` 可改用官方 Hub

需要 `pip install -e '.[knowledge]'`。

知识语料随本仓库一起发布，位于 `knowledge/` 下：精选的运维文档与清单位于 `knowledge/tidb/curated/` 和 `knowledge/pg/`，预计算好的统一服务层（分块、映射、溯源）位于 `knowledge/tidb_unified/`。场景契约与知识清单通过 sha256 固定语料，因此运行知识驱动的场景不需要任何外部下载。`data/knowledge_bases/` 下的本地 Chroma 索引按需生成，且已被 git 忽略。

## 7. TPC-DS 查询文本（必需）与数据文件（仅 demo 需要）

TPC-DS 查询流 `data/workloads/tpcds/queries/query_0.sql` 在**首次运行前必须就位**：PostgreSQL 场景定义内嵌了 TPC-DS 工作负载画像，缺少它场景注册表将无法加载。TPC-DS 查询文本和数据的版权归 Transaction Processing Performance Council 所有，无法在本仓库许可证下再分发——请从官方 TPC-DS 工具包（tpc.org）获取，并把查询流放到上述路径。

数 GB 的 `.dat` 数据文件（每个文件都在 `data/workloads/tpcds/manifest.json` 中列有 sha256）只有 `examples/run_tpcds_demo.py` 需要，该脚本会生成并加载完整的 TPC-DS 数据集。

TPC-DS 和 TPC-DSX 准备过程将实际本地数据集的 manifest 写入 Git 忽略的
`data/workloads/<workload>/runtime/manifest.json`。部署使用这个运行时 manifest
校验数据和 schema 的哈希。公开的 `data/workloads/<workload>/manifest.json`
保持不变，因此准备 workload 不会使下一次正式实验的工作区洁净检查失败。

## 8. 故障排查

| 症状 | 原因 / 解决办法 |
|---|---|
| `permission denied ... /var/run/docker.sock` | 缺少 docker 组成员身份——见第 2 步 |
| 端口已被占用（`15432`、`4000`、`2379`） | 上一次运行仍在运行；先 `docker ps`，再停止/移除遗留容器 |
| `postgres:16` 拉取超时 | 为你所在区域配置 Docker 注册表镜像 |
| TiDB Compose 容器反复重启或 OOM | 空闲内存不足——停止其他工作负载，或在 Compose 文件的本地副本中调低 TiKV 内存 |
| Hugging Face 下载停滞 | 保持默认 `hf-mirror.com` 端点（此处默认如此），或显式设置 `HF_ENDPOINT` |
| vLLM 启动失败 | 检查 CUDA 驱动与空闲显存；裁判是可选的——DP 精确匹配不需要 GPU |
| 首次运行时测试挂起 | 场景测试会在首次使用时拉取镜像；用 `docker ps` 观察进度 |
