import logging
import os
from typing import Optional


class LogManager:
    """
    日志管理器，提供统一的日志记录接口。
    支持同时输出到控制台和文件。
    """
    _instances = {}

    def __init__(self, name: str, log_dir: Optional[str] = None, level: int = logging.INFO):
        self.name = name
        self.log_dir = log_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "logs"
        )
        self.level = level
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """设置logger"""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        logger.handlers = []

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)
        log_file = os.path.join(self.log_dir, f"{self.name}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)

    @classmethod
    def get_logger(cls, name: str, log_dir: Optional[str] = None) -> 'LogManager':
        """
        获取指定名称的logger实例（单例模式）
        """
        if name not in cls._instances:
            cls._instances[name] = cls(name, log_dir)
        return cls._instances[name]

    @classmethod
    def clear_instances(cls):
        """清空所有实例（主要用于测试）"""
        cls._instances = {}


def get_logger(name: str, log_dir: Optional[str] = None) -> LogManager:
    """
    快捷函数：获取logger实例
    """
    return LogManager.get_logger(name, log_dir)
