#!/bin/bash
set -e

KIND_IMAGE="${KIND_IMAGE:-kindest/node:v1.27.3}"
OUTPUT_IMAGE="${OUTPUT_IMAGE:-kind-node:tidb-ready}"
TEMP_CLUSTER="temp-build-cluster"

echo "=== 构建 TiDB 离线胖镜像 (使用 docker commit) ==="
echo "基础镜像: ${KIND_IMAGE}"
echo "输出镜像: ${OUTPUT_IMAGE}"
echo ""

cleanup_all() {
    echo "=== 清理资源 ==="
    kind delete cluster --name "${TEMP_CLUSTER}" 2>/dev/null || true
}

build_fat_image() {
    echo "[1/4] 清理旧资源..."
    cleanup_all

    echo ""
    echo "[2/4] 创建临时 kind 集群..."
    kind create cluster --name "${TEMP_CLUSTER}" --image "${KIND_IMAGE}"

    echo ""
    echo "[3/4] 加载 TiDB 镜像到集群..."
    for IMG in pingcap/pd:v8.1.0 pingcap/tikv:v8.1.0 pingcap/tidb:v8.1.0 pingcap/tidb-operator:v1.5.2; do
        echo "   -> 加载: ${IMG}"
        kind load docker-image "${IMG}" --name "${TEMP_CLUSTER}"
    done

    echo ""
    echo "[4/4] 使用 docker commit 创建新镜像..."

    CONTAINER_ID=$(docker ps -q -f name="${TEMP_CLUSTER}-control-plane")
    echo "   -> 容器 ID: ${CONTAINER_ID}"

    echo "   -> 直接 docker commit (保留所有元数据)..."
    docker commit "${CONTAINER_ID}" "${OUTPUT_IMAGE}"

    echo ""
    echo "=== 验证胖镜像 ==="
    docker images "${OUTPUT_IMAGE}"
    echo "镜像大小: $(docker image inspect "${OUTPUT_IMAGE}" --format='{{.Size}}' | numfmt --to=iec)"
}

echo ""
echo "开始构建..."
echo ""

build_fat_image

echo ""
echo "✅ 构建完成！"
echo "👉 物理级预热镜像已生成: ${OUTPUT_IMAGE}"