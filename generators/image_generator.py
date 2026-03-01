#!/usr/bin/env python3
"""
图片生成主逻辑
"""

import os
import time
from pathlib import Path
from typing import Optional

# 使用绝对导入
import sys
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

from core.config_loader import get_config
from core.prompt_generator import PromptGenerator
from core.workflow_builder import WorkflowBuilder
from generators.comfyui_client import ComfyUIClient


class ImageGenerator:
    """图片生成器"""
    
    def __init__(self, config=None):
        """
        初始化图片生成器
        
        Args:
            config: 配置字典，默认加载配置文件
        """
        self.config = config or get_config()
        
        comfyui_config = self.config.get('comfyui', {})
        self.client = ComfyUIClient(
            host=comfyui_config.get('host', 'localhost'),
            port=comfyui_config.get('port', 7860),
            timeout=180
        )
        
        self.prompt_gen = PromptGenerator()
        
        # 加载基础 workflow 路径
        script_dir = Path(__file__).parent.parent
        base_workflow_path = script_dir / "workflows" / "base-workflow.json"
        self.workflow_builder = WorkflowBuilder(base_workflow_path)
        
        # 输出目录
        self.output_dir = Path(
            os.path.expanduser(
                self.config.get('generation', {}).get(
                    'output_dir',
                    '~/.openclaw/workspace/assets/asuka-emotions/generated'
                )
            )
        )
    
    def generate(
        self,
        emotion: str,
        outfit: Optional[str] = None,
        save_dir: Optional[str] = None
    ) -> Optional[str]:
        """
        生成一张表情图片
        
        Args:
            emotion: 情绪类型 (happy, shy, angry, smug, sad, surprised, love)
            outfit: 指定衣服（可选）
            save_dir: 保存目录（可选，默认按情绪分类）
        
        Returns:
            生成的图片路径，失败返回 None
        """
        # 检查 ComfyUI 连接
        if not self.client.check_connection():
            print("Error: Cannot connect to ComfyUI")
            return None
        
        # 生成 prompt
        positive = self.prompt_gen.generate_positive(emotion, outfit)
        negative = self.prompt_gen.generate_negative()
        
        print(f"Generating {emotion} image...")
        print(f"Positive: {positive[:80]}...")
        
        # 构建 workflow
        workflow = self.workflow_builder.build(positive, negative)
        
        # 提交任务
        try:
            prompt_id = self.client.submit(workflow)
            print(f"Submitted: {prompt_id}")
        except Exception as e:
            print(f"Error submitting workflow: {e}")
            return None
        
        # 等待完成
        outputs = self.client.wait_for_completion(prompt_id)
        
        if not outputs:
            print("Generation failed or timeout")
            return None
        
        # 下载图片
        if "81" not in outputs:
            print("Error: No output node 81 found")
            return None
        
        image_info = outputs["81"]["images"][0]
        filename = image_info["filename"]
        
        # 确定保存路径
        if save_dir is None:
            save_dir = self.output_dir / emotion
        else:
            save_dir = Path(save_dir)
        
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 使用种子作为文件名
        seed = workflow["prompt"]["61"]["inputs"]["seed"]
        save_path = save_dir / f"{emotion}_{seed}.png"
        
        try:
            downloaded = self.client.download_image(
                filename=filename,
                save_path=str(save_path),
                subfolder=image_info.get("subfolder", ""),
                image_type=image_info.get("type", "temp")
            )
            print(f"✓ Saved: {downloaded}")
            return downloaded
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None
    
    def generate_batch(
        self,
        emotion: str,
        count: int = 1,
        outfit: Optional[str] = None
    ) -> list:
        """
        批量生成图片
        
        Args:
            emotion: 情绪类型
            count: 生成数量
            outfit: 指定衣服（可选）
        
        Returns:
            生成的图片路径列表
        """
        results = []
        
        for i in range(count):
            print(f"\n[{i+1}/{count}] Generating {emotion}...")
            path = self.generate(emotion, outfit)
            if path:
                results.append(path)
            time.sleep(1)  # 避免请求过快
        
        return results


# 便捷函数
def generate_emotion_image(emotion: str, outfit: Optional[str] = None) -> Optional[str]:
    """生成表情图片的便捷函数"""
    generator = ImageGenerator()
    return generator.generate(emotion, outfit)


if __name__ == "__main__":
    # 测试
    generator = ImageGenerator()
    
    # 生成一张开心的表情
    result = generator.generate("happy")
    
    if result:
        print(f"\n✓ Success: {result}")
    else:
        print("\n✗ Failed")