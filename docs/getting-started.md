# Getting Started

A complete walkthrough from a bare machine to a finished experiment. The
[README](../README.md) quick start covers the happy path; this document covers
every prerequisite, the optional model downloads, and the failure modes you are
most likely to hit.

## 0. Prerequisites

| Requirement | Version / amount | Notes |
|---|---|---|
| Python | 3.10 – 3.12 | `python3 --version` |
| Docker Engine | 20.10+ | Includes Compose v2 (`docker compose version`) |
| Free disk | ~10 GB | `postgres:16` image plus per-run containers; TiDB Compose adds PD/TiKV/TiDB/Prometheus images |
| Free RAM | 4 GB (PG) / 8 GB (TiDB) | TiDB Compose runs PD + TiKV + TiDB + Prometheus |
| (Optional) NVIDIA GPU | 24 GB+ VRAM | Only for the local semantic-diagnosis judge (vLLM) |
| (Optional) NVIDIA GPU / CPU | any | Knowledge-base embedding runs on CPU by default; CUDA is auto-detected if available |

## 1. Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

Optional extras:

```bash
pip install -e '.[knowledge]'   # knowledge-base features (chromadb, llama-index, sentence-transformers)
```

Verify the import path works. The scenario registry embeds TPC-DS workload
definitions, so this needs the copyrighted query stream first — fetch it per
§7 if you have not yet:

```bash
python -c "from src.benchmark import api; print('ok')"
```

Conda works too (`conda create -n aiopsbench python=3.11`) — any environment name is fine; there is no hardcoded environment name.

## 2. Docker

1. Install Docker Engine for your platform: <https://docs.docker.com/engine/install/> (Linux) or Docker Desktop (macOS/Windows).
2. Verify without sudo:

   ```bash
   docker run --rm hello-world
   docker compose version   # must be Compose v2
   ```

3. If step 2 fails with `permission denied` on Linux, add yourself to the `docker` group and re-login:

   ```bash
   sudo usermod -aG docker "$USER"
   ```

Images used at runtime:

- PostgreSQL scenarios pull **`postgres:16`** from Docker Hub.
- TiDB scenarios use a Compose file that pins **`pingcap/pd`, `pingcap/tikv`, `pingcap/tidb`** by digest, plus Prometheus and cAdvisor.
- If `pingcap/*` pulls are slow or blocked in your network, configure a registry mirror in the Docker daemon
  (for example `https://docker.m.daocloud.io`) — parts of the Compose file already reference it directly.

## 3. First run

```bash
python examples/run_mock_llm_demo.py
```

You should see the mock agent inspect a PostgreSQL container, submit a diagnosis, and the evaluator
print per-phase results. No LLM credentials are involved — the agent is scripted. Then try the TiDB
demo (takes a few minutes on first run while images pull):

```bash
python examples/run_tidb_demo.py
```

## 4. LLM credentials

Credentials live in `config/llm_config.json`, keyed by model name, and are **never committed**
(already covered by `.gitignore`):

```bash
cp config/llm_config.example.json config/llm_config.json
# edit: replace every REPLACE_ME with a real key; adjust url / provider / context_window_tokens as needed
```

The example file shows the three supported shapes:

- OpenAI-compatible cloud API (`url` ends in `/chat/completions`)
- Anthropic-native API (`"provider": "anthropic"`)
- Local OpenAI-compatible endpoint (for example a vLLM server on `127.0.0.1`)

The provider is auto-detected from the URL or the explicit `provider` field.

## 5. Optional: semantic-diagnosis judge (LLM judge)

The DP evaluator supports exact matching out of the box. For semantic diagnosis matching it needs a
local judge served by vLLM (requires an NVIDIA GPU with ~24 GB VRAM):

```bash
pip install vllm
python scripts/start_dp_semantic_model.py
# first start downloads Qwen/Qwen3-4B-Instruct-2507 (~8 GB) from Hugging Face
```

Then switch scenarios to semantic mode:

```bash
export AIOPS_DP_MATCH_MODE=semantic
export AIOPS_DP_SEMANTIC_MODEL='Qwen/Qwen3-4B-Instruct-2507'
export AIOPS_DP_SEMANTIC_CONFIG='config/llm_config.json'
```

Details: [semantic diagnosis matching guide](guides/evaluation/semantic-diagnosis-matching.guide.md).

## 6. Optional: knowledge-base embedding models

Knowledge-base features embed PostgreSQL/TiDB operations documents. The embedding model is
downloaded automatically on first use:

- Default model: **`Qwen/Qwen3-Embedding-4B`** (override with `AIOPS_PG_KB_EMBED_MODEL`)
- Default device: **CPU** (override with `AIOPS_PG_KB_EMBED_DEVICE`, e.g. `cuda:0`, or `AIOPS_PG_KB_EMBED_TARGET_DEVICES` for multi-GPU)
- Downloads default to the `https://hf-mirror.com` endpoint; set `HF_ENDPOINT=https://huggingface.co` to use the official Hub

Requires `pip install -e '.[knowledge]'`.

The knowledge corpus ships with this repository under `knowledge/`: the curated operations
documents and manifests live in `knowledge/tidb/curated/` and `knowledge/pg/`, and the
precomputed unified serving layers (chunks, mappings, provenance) live in
`knowledge/tidb_unified/`. Scenario contracts and knowledge manifests pin the corpus by
sha256, so no external download is needed to run the knowledge-driven scenarios. The local
Chroma index under `data/knowledge_bases/` is generated on demand and is git-ignored.

## 7. TPC-DS query text (required) and data files (demo only)

The TPC-DS query stream `data/workloads/tpcds/queries/query_0.sql` is **required before the
first run**: PostgreSQL scenario definitions embed TPC-DS workload profiles, so the scenario
registry cannot load without it. TPC-DS query text and data are copyrighted by the Transaction
Processing Performance Council and are not redistributable under this repository's license —
obtain them from the official TPC-DS kit (tpc.org) and place the query stream at the path above.

The multi-GB `.dat` data files (each listed with its sha256 in `data/workloads/tpcds/manifest.json`)
are only needed for `examples/run_tpcds_demo.py`, which generates and loads a full TPC-DS dataset.

## 8. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `permission denied ... /var/run/docker.sock` | Docker group membership missing — see step 2 |
| Port already allocated (`15432`, `4000`, `2379`) | A previous run is still up; `docker ps`, then stop/remove the leftover containers |
| `postgres:16` pull times out | Configure a Docker registry mirror for your region |
| TiDB Compose containers restart-loop or OOM | Not enough free RAM — stop other workloads or lower TiKV memory in a local copy of the Compose file |
| Hugging Face download stalls | Keep the default `hf-mirror.com` endpoint (default here), or set `HF_ENDPOINT` explicitly |
| vLLM fails to start | Check CUDA driver and free VRAM; the judge is optional — exact DP matching needs no GPU |
| Tests hang on first run | Scenario tests pull images on first use; watch `docker ps` for progress |
