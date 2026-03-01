#!/usr/bin/env python3
"""
Prompt 生成器 - 构建 ComfyUI 的正面和负面 Prompt
"""

import random
from typing import Optional
from .config_loader import get_config


class PromptGenerator:
    """Prompt 生成器"""
    
    def __init__(self):
        self.config = get_config()
        self.character = self.config.get('character', {})
        self.quality = self.config.get('quality', {})
    
    def select_outfit(self) -> str:
        """
        根据权重随机选择衣服
        
        Returns:
            衣服描述字符串
        """
        outfits = self.config.get('character', {}).get('outfits', [])
        if not outfits:
            return ""
        
        # 提取权重和描述
        weights = []
        descriptions = []
        
        for outfit in outfits:
            if isinstance(outfit, dict):
                weights.append(outfit.get('weight', 1))
                descriptions.append(outfit.get('description', ''))
        
        if not descriptions:
            return ""
        
        # 按权重随机选择
        selected = random.choices(descriptions, weights=weights, k=1)[0]
        return selected
    
    def generate_positive(self, emotion: str, outfit: Optional[str] = None) -> str:
        """
        生成正面 Prompt
        
        Args:
            emotion: 情绪类型 (happy, shy, angry, smug, sad, surprised, love)
            outfit: 指定衣服（可选，默认随机）
        
        Returns:
            完整的正面 prompt
        """
        emotions_config = self.config.get('emotions', {})
        emotion_config = emotions_config.get(emotion, {})
        
        # 随机选择衣服（如果未指定）
        if outfit is None:
            outfit = self.select_outfit()
        
        # 构建 prompt 各部分
        parts = [
            self.quality.get('base_prompt', 'masterpiece, best quality, amazing quality'),
            "1girl",
            f"({self.character.get('name', 'souryuu asuka langley')}:1.5)",
            self.character.get('base_traits', 'blue eyes, long brown hair, hair ornament'),
            "cowboy shot, upper body",
            outfit,
            emotion_config.get('expression', ''),
            emotion_config.get('background', ''),
            "(beautiful detailed eyes:1.6)",
            "(perfect hands, perfect anatomy)"
        ]
        
        # 过滤空值并连接
        parts = [p for p in parts if p]
        return ", ".join(parts)
    
    def generate_negative(self) -> str:
        """
        生成负面 Prompt
        
        Returns:
            负面 prompt
        """
        return self.quality.get(
            'negative_prompt',
            'bad quality, worst quality, worst detail, sketch, censor, patreon, watermark, deformed, ugly'
        )


# 便捷函数
def generate_positive_prompt(emotion: str, outfit: Optional[str] = None) -> str:
    """生成正面 prompt 的便捷函数"""
    generator = PromptGenerator()
    return generator.generate_positive(emotion, outfit)


def generate_negative_prompt() -> str:
    """生成负面 prompt 的便捷函数"""
    generator = PromptGenerator()
    return generator.generate_negative()


if __name__ == "__main__":
    # 测试
    generator = PromptGenerator()
    
    emotions = ['happy', 'shy', 'angry', 'smug', 'sad', 'surprised', 'love']
    
    for emotion in emotions:
        print(f"\n{'='*60}")
        print(f"Emotion: {emotion}")
        print(f"{'='*60}")
        print(f"Positive: {generator.generate_positive(emotion)}")
        print(f"Outfit: {generator.select_outfit()}")
    
    print(f"\n{'='*60}")
    print(f"Negative: {generator.generate_negative()}")
