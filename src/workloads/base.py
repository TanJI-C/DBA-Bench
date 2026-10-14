import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseWorkload(ABC):
    """
    负载层抽象。
    职责：准备数据库初始化所需的数据文件和 SQL。
    """

    def __init__(self, workload_name: str, workload_root: str = None):
        if workload_root is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            workload_root = os.path.join(project_root, "data", "workloads")
        self.workload_root = workload_root
        self.workload_name = workload_name
        self.workload_dir = os.path.join(self.workload_root, workload_name)
        self.data_dir = os.path.join(self.workload_dir, "data")
        self.manifest_path = os.path.join(self.workload_dir, "manifest.json")

    @abstractmethod
    def prepare(self):
        """
        准备工作：
        1. 检查数据文件是否存在，不存在则报错或生成
        2. 生成 init.sql（包含 schema 创建 + 数据导入）
        """
        pass

    def get_init_sql_path(self) -> str:
        """返回 init.sql 路径"""
        return os.path.join(self.workload_dir, "init.sql")

    def ensure_dir(self, path: str):
        """确保目录存在"""
        os.makedirs(path, exist_ok=True)

    def load_manifest(self) -> Optional[Dict[str, Any]]:
        """加载 manifest 配置"""
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        return None

    def save_manifest(self, manifest: Dict[str, Any]):
        """保存 manifest 配置"""
        self.ensure_dir(os.path.dirname(self.manifest_path))
        with open(self.manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
            f.write("\n")
