#!/usr/bin/env python3
"""
配置加载器 - 加载 config.yaml
"""

import os
import re
from pathlib import Path


def parse_yaml_simple(content):
    """
    简化的 YAML 解析器 - 专门处理我们的 config 格式
    """
    result = {}
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # 跳过空行和注释
        if not stripped or stripped.startswith('#'):
            i += 1
            continue
        
        # 顶级键 (无缩进)
        if not line.startswith(' ') and not line.startswith('\t') and ':' in stripped:
            key = stripped.split(':')[0].strip()
            value = stripped.split(':', 1)[1].strip()
            
            # 检查下一行
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                next_indent = len(next_line) - len(next_line.lstrip())
                
                if next_indent > 0:
                    # 有子项，递归解析
                    j = i + 1
                    sub_lines = []
                    base_indent = next_indent
                    
                    while j < len(lines):
                        sub_line = lines[j]
                        if not sub_line.strip():
                            j += 1
                            continue
                        
                        sub_indent = len(sub_line) - len(sub_line.lstrip())
                        
                        if sub_indent < base_indent and not sub_line.strip().startswith('#'):
                            break
                        
                        if sub_indent >= base_indent:
                            sub_lines.append(sub_line[base_indent:])
                        
                        j += 1
                    
                    sub_content = '\n'.join(sub_lines)
                    result[key] = parse_yaml_simple(sub_content)
                    i = j - 1
                else:
                    # 简单值
                    result[key] = parse_value(value)
            else:
                result[key] = parse_value(value)
        
        i += 1
    
    return result


def parse_value(value):
    """解析单个值"""
    value = value.strip()
    
    if not value:
        return {}
    
    # 布尔值
    if value.lower() == 'true':
        return True
    if value.lower() == 'false':
        return False
    
    # 整数
    if value.isdigit():
        return int(value)
    
    # 数组 [1, 2, 3]
    if value.startswith('[') and value.endswith(']'):
        items = value[1:-1].split(',')
        return [parse_value(item.strip()) for item in items]
    
    # 去掉引号
    return value.strip('"\'')


def load_config(config_path=None):
    """加载配置文件"""
    if config_path is None:
        script_dir = Path(__file__).parent.parent
        config_path = script_dir / "config.yaml"
    
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return parse_yaml_simple(content)


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