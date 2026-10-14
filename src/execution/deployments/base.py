from abc import ABC, abstractmethod


class BaseDeployment(ABC):
    """
    部署层抽象。
    职责：承载底层服务的运行容器或集群，提供标准化的部署/销毁接口。
    """
    @abstractmethod
    def deploy(self):
        """部署服务"""
        pass

    @abstractmethod
    def teardown(self):
        """销毁服务"""
        pass

    @abstractmethod
    def is_ready(self) -> bool:
        """检查服务是否就绪"""
        pass
