#!/usr/bin/env python3
"""
表情图片管理器 - 管理生成的表情库存
"""

import json
import random
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any


class EmotionManager:
    """表情图片管理器"""
    
    def __init__(self, base_dir: str = None):
        """
        初始化表情管理器
        
        Args:
            base_dir: 基础目录，默认使用 workspace 下的 assets
        """
        if base_dir is None:
            # 默认路径
            self.base_dir = Path(
                os.path.expanduser("~/.openclaw/workspace/assets/asuka-emotions")
            )
        else:
            self.base_dir = Path(os.path.expanduser(base_dir))
        
        # 生成图片目录
        self.generated_dir = self.base_dir / "generated"
        
        # 索引文件
        self.index_file = self.base_dir / "emotion-index.json"
        
        # 确保目录存在
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载索引
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, List[Dict[str, Any]]]:
        """加载表情索引"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading index: {e}")
                return {}
        return {}
    
    def _save_index(self):
        """保存表情索引"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def add_emotion(
        self,
        emotion: str,
        filepath: str,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        添加新表情到索引
        
        Args:
            emotion: 情绪类型
            filepath: 图片文件路径
            metadata: 元数据（可选）
        
        Returns:
            是否成功
        """
        if emotion not in self.index:
            self.index[emotion] = []
        
        entry = {
            "path": str(filepath),
            "created": datetime.now().isoformat(),
            "metadata": metadata or {},
            "usage_count": 0
        }
        
        self.index[emotion].append(entry)
        self._save_index()
        return True
    
    def get_random_emotion(
        self,
        emotion: str,
        prefer_unused: bool = True
    ) -> Optional[str]:
        """
        随机获取一个表情图片路径
        
        Args:
            emotion: 情绪类型
            prefer_unused: 优先选择使用次数少的
        
        Returns:
            图片文件路径，如果没有返回 None
        """
        if emotion not in self.index or not self.index[emotion]:
            return None
        
        images = self.index[emotion]
        
        # 过滤掉不存在的文件
        valid_images = [
            img for img in images
            if Path(img["path"]).exists()
        ]
        
        if not valid_images:
            return None
        
        if prefer_unused:
            # 按使用次数排序，优先选使用少的
            images_sorted = sorted(
                valid_images,
                key=lambda x: x.get("usage_count", 0)
            )
            # 从前50%中随机选
            top_half = images_sorted[:max(1, len(images_sorted) // 2)]
            selected = random.choice(top_half)
        else:
            selected = random.choice(valid_images)
        
        # 增加使用次数
        selected["usage_count"] = selected.get("usage_count", 0) + 1
        self._save_index()
        
        return selected["path"]
    
    def get_stock(self, emotion: str) -> int:
        """
        获取某类表情的库存数量
        
        Args:
            emotion: 情绪类型
        
        Returns:
            库存数量
        """
        if emotion not in self.index:
            return 0
        
        # 只计算存在的文件
        return sum(
            1 for img in self.index[emotion]
            if Path(img["path"]).exists()
        )
    
    def get_stats(self) -> Dict[str, Dict[str, int]]:
        """
        获取表情统计信息
        
        Returns:
            统计信息字典
        """
        stats = {}
        for emotion, images in self.index.items():
            valid_count = sum(
                1 for img in images
                if Path(img["path"]).exists()
            )
            total_usage = sum(
                img.get("usage_count", 0) for img in images
            )
            stats[emotion] = {
                "total": len(images),
                "valid": valid_count,
                "total_usage": total_usage
            }
        return stats
    
    def list_emotions(self) -> List[str]:
        """
        列出所有情绪类型
        
        Returns:
            情绪类型列表
        """
        return list(self.index.keys())
    
    def clean_missing(self) -> int:
        """
        清理不存在的文件记录
        
        Returns:
            清理的数量
        """
        cleaned = 0
        for emotion in list(self.index.keys()):
            original_len = len(self.index[emotion])
            self.index[emotion] = [
                img for img in self.index[emotion]
                if Path(img["path"]).exists()
            ]
            cleaned += original_len - len(self.index[emotion])
            
            # 如果空了，删除这个情绪
            if not self.index[emotion]:
                del self.index[emotion]
        
        if cleaned > 0:
            self._save_index()
        
        return cleaned


# 便捷函数
def get_emotion_image(emotion: str) -> Optional[str]:
    """获取表情图片的便捷函数"""
    manager = EmotionManager()
    return manager.get_random_emotion(emotion)


def add_emotion_image(emotion: str, filepath: str) -> bool:
    """添加表情图片的便捷函数"""
    manager = EmotionManager()
    return manager.add_emotion(emotion, filepath)


if __name__ == "__main__":
    # 测试
    manager = EmotionManager()
    
    print("Emotion Manager Test")
    print("=" * 50)
    
    # 显示统计
    stats = manager.get_stats()
    print(f"\nCurrent stats:")
    for emotion, info in stats.items():
        print(f"  {emotion}: {info['valid']}/{info['total']} images, {info['total_usage']} uses")
    
    # 测试获取
    for emotion in ["happy", "shy", "angry"]:
        path = manager.get_random_emotion(emotion)
        print(f"\nGet {emotion}: {path}")