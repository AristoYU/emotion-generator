#!/usr/bin/env python3
"""
配置加载器 - 加载 config.yaml
"""

import os
import yaml
from pathlib import Path


def load_config(config_path=None):
    """加载配置文件"""
    if config_path is None:
        script_dir = Path(__file__).parent.parent
        config_path = script_dir / "config.yaml"
    
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# 全局配置缓存
_config_cache = None

def get_config():
    """获取配置（带缓存）"""
    global _config_cache
    if _config_cache is None:
        _config_cache = load_config()
    return _config_cache


if __name__ == "__main__":
    # 测试
    import json
    config = get_config()
    print(json.dumps(config, indent=2, ensure_ascii=False))
